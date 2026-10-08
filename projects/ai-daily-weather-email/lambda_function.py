"""Daily weather email. Nova Lite is called through InvokeModel."""
import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

import boto3
from botocore.config import Config

CONFIG = Config(connect_timeout=5, read_timeout=30,
                retries={"max_attempts": 2, "mode": "standard"})
REGION = os.environ.get("BEDROCK_REGION", "us-east-1")
bedrock = boto3.client("bedrock-runtime", region_name=REGION, config=CONFIG)
sns = boto3.client("sns", region_name=os.environ.get("SNS_REGION", REGION), config=CONFIG)


def lambda_handler(event, context):
    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    topic_arn = os.environ.get("SNS_TOPIC_ARN", "").strip()
    if not api_key or not topic_arn:
        raise RuntimeError("Set OPENWEATHER_API_KEY and SNS_TOPIC_ARN.")
    city = os.environ.get("WEATHER_CITY", "Dera Ismail Khan,PK")
    url = "https://api.openweathermap.org/data/2.5/weather?" + urlencode(
        {"q": city, "appid": api_key, "units": "metric"}
    )
    try:
        with urlopen(url, timeout=10) as response:
            weather = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(f"Weather API HTTP {error.code}; check API key and city.") from None
    except (URLError, TimeoutError):
        raise RuntimeError("Weather API connection failed or timed out.") from None
    except (ValueError, UnicodeDecodeError):
        raise RuntimeError("Weather API returned invalid JSON.") from None
    if str(weather.get("cod")) != "200":
        raise RuntimeError("Weather API request failed.")
    try:
        data = {
            "temperature_c": weather["main"]["temp"],
            "feels_like_c": weather["main"]["feels_like"],
            "humidity_percent": weather["main"]["humidity"],
            "wind_speed_mps": weather["wind"]["speed"],
            "description": weather["weather"][0]["description"],
            "rain_last_hour_mm": weather.get("rain", {}).get("1h", 0),
        }
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Weather response is missing required fields.") from None
    prompt = (
        f"Current weather in {city}: {json.dumps(data)}. "
        "Write exactly two short email lines, at most 40 words total. "
        "Include temperature, whether an umbrella is needed based on current "
        "conditions, and one practical tip. Do not predict future rain. "
        "Return only the email text."
    )
    response = bedrock.invoke_model(
        modelId=os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
        contentType="application/json", accept="application/json",
        body=json.dumps({
            "schemaVersion": "messages-v1",
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": 150, "temperature": 0.5},
        }),
    )
    result = json.loads(response["body"].read())
    summary = "\n".join(
        block["text"] for block in result.get("output", {}).get("message", {}).get("content", [])
        if isinstance(block.get("text"), str)
    ).strip()
    if not summary:
        raise RuntimeError("Nova Lite returned an empty summary.")
    subject = " ".join(f"{city}: {data['temperature_c']} C {data['description']}".split())[:99]
    sent = sns.publish(TopicArn=topic_arn, Subject=subject, Message=summary)
    return {"message_id": sent["MessageId"], "summary": summary}

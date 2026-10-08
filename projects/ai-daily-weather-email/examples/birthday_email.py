"""Optional extension: deploy as a separate Lambda with SES permissions."""
import json
import os
import boto3
from botocore.config import Config

CONFIG = Config(connect_timeout=5, read_timeout=30,
                retries={"max_attempts": 2, "mode": "standard"})
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("BEDROCK_REGION", "us-east-1"), config=CONFIG)
ses = boto3.client("ses", region_name=os.environ.get("SES_REGION", "us-east-1"), config=CONFIG)


def lambda_handler(event, context):
    sender = os.environ.get("SES_FROM_EMAIL", "").strip()
    recipient = os.environ.get("SES_TO_EMAIL", "").strip()
    if not sender or not recipient:
        raise RuntimeError("Set SES_FROM_EMAIL and SES_TO_EMAIL.")
    name = str(event.get("recipient_name", "friend"))[:100]
    occasion = str(event.get("occasion", "birthday"))[:100]
    prompt = (
        f"Write a warm, respectful {occasion} greeting for {name}. "
        "Use at most 60 words. Return only the email body. Do not invent personal facts."
    )
    response = bedrock.invoke_model(
        modelId=os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
        contentType="application/json", accept="application/json",
        body=json.dumps({
            "schemaVersion": "messages-v1",
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": 200, "temperature": 0.5},
        }),
    )
    payload = json.loads(response["body"].read())
    body = "\n".join(b["text"] for b in payload.get("output", {}).get("message", {}).get("content", [])
                     if isinstance(b.get("text"), str)).strip()
    if not body:
        raise RuntimeError("Nova Lite returned an empty greeting.")
    subject = " ".join(f"Happy {occasion}, {name}!".split())[:99]
    result = ses.send_email(
        Source=sender,
        Destination={"ToAddresses": [recipient]},
        Message={"Subject": {"Data": subject, "Charset": "UTF-8"},
                 "Body": {"Text": {"Data": body, "Charset": "UTF-8"}}},
    )
    return {"message_id": result["MessageId"]}

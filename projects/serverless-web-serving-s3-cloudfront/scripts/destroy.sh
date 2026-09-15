#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${STACK_NAME:-serverless-web-serving-s3-cloudfront}"
AWS_REGION="${AWS_REGION:-us-east-1}"

command -v aws >/dev/null 2>&1 || { echo "AWS CLI is required." >&2; exit 1; }

BUCKET_NAME="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)"

while true; do
  VERSIONS="$(aws s3api list-object-versions --region "$AWS_REGION" --bucket "$BUCKET_NAME" --output json --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}')"
  COUNT="$(printf '%s' "$VERSIONS" | python3 -c 'import json,sys; print(len(json.load(sys.stdin).get("Objects") or []))')"
  [ "$COUNT" -eq 0 ] && break
  aws s3api delete-objects --region "$AWS_REGION" --bucket "$BUCKET_NAME" --delete "$VERSIONS" >/dev/null
done

while true; do
  MARKERS="$(aws s3api list-object-versions --region "$AWS_REGION" --bucket "$BUCKET_NAME" --output json --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}')"
  COUNT="$(printf '%s' "$MARKERS" | python3 -c 'import json,sys; print(len(json.load(sys.stdin).get("Objects") or []))')"
  [ "$COUNT" -eq 0 ] && break
  aws s3api delete-objects --region "$AWS_REGION" --bucket "$BUCKET_NAME" --delete "$MARKERS" >/dev/null
done

aws cloudformation delete-stack --region "$AWS_REGION" --stack-name "$STACK_NAME"
aws cloudformation wait stack-delete-complete --region "$AWS_REGION" --stack-name "$STACK_NAME"
echo "Stack and retained bucket deleted successfully."

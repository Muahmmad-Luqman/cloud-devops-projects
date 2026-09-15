#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${STACK_NAME:-serverless-web-serving-s3-cloudfront}"
AWS_REGION="${AWS_REGION:-us-east-1}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v aws >/dev/null 2>&1 || { echo "AWS CLI is required." >&2; exit 1; }
aws sts get-caller-identity >/dev/null

aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "$STACK_NAME" \
  --template-file "$PROJECT_ROOT/infrastructure/template.yaml" \
  --no-fail-on-empty-changeset

BUCKET_NAME="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)"
DISTRIBUTION_ID="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='DistributionId'].OutputValue" --output text)"
WEBSITE_URL="$(aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='WebsiteURL'].OutputValue" --output text)"

aws s3 sync "$PROJECT_ROOT/website/" "s3://$BUCKET_NAME/" --region "$AWS_REGION" --delete
aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" --paths '/*' >/dev/null

echo "Deployment submitted successfully."
echo "Website URL: $WEBSITE_URL"

#!/usr/bin/env bash
set -euo pipefail

# Usage: source ./scripts/export-urls.sh [dev|prod]

: "${POSTGRES_USER:?Not set}"
: "${POSTGRES_PASSWORD:?Not set}"
: "${DF_ID:?Not set}"

MODE="${1:-${ENVIRONMENT:-dev}}"
MODE="$(echo "$MODE" | tr '[:upper:]' '[:lower:]')"

if [[ "$MODE" != "dev" && "$MODE" != "prod" ]]; then
  echo "❌ Invalid mode: $MODE ; Use 'dev' or 'prod'."
  return 1 2>/dev/null || exit 1
fi



if [[ "$MODE" == "prod" ]]; then
  : "${MAIN_DOMAIN:?MAIN_DOMAIN must be set in production mode}"

  export API_CMP_HOST="api-cmp.${MAIN_DOMAIN}"
  export API_CUSTOMER_HOST="api-dpar.${MAIN_DOMAIN}"
  export API_NOTICE_WORKER_HOST="api-notice-worker.${MAIN_DOMAIN}"
  export API_COOKIE_CONSENT_HOST="api-cookie-consent.${MAIN_DOMAIN}"
  export FRONTEND_CMP_HOST="cmp.${MAIN_DOMAIN}"
  export FRONTEND_CUSTOMER_HOST="dpar.${MAIN_DOMAIN}"

  export POSTGRES_DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres16:5432/postgres"
  export MONGO_URI="mongodb://${POSTGRES_USER}:${POSTGRES_PASSWORD}@ferretdb:27017"
  export RABBITMQ_HOST="rabbitmq"
  export REDIS_HOST="keydb"
  export S3_URL="minio:9000"
  export OPENSEARCH_HOST="opensearch-node"
  export DATA_VEDA_URL="http://data-veda:9080"

  export NEXT_PUBLIC_ADMIN_URL="https://${API_CMP_HOST}/api/v1"
  export NEXT_PUBLIC_CUSTOMER_URL="https://${API_CUSTOMER_HOST}"
  export CMP_ADMIN_BACKEND_URL="https://${API_CMP_HOST}"
  export CMP_ADMIN_FRONTEND_URL="https://${FRONTEND_CMP_HOST}"
  export CMP_NOTICE_WORKER_URL="https://${API_NOTICE_WORKER_HOST}"
  export CUSTOMER_PORTAL_BACKEND_URL="https://${API_CUSTOMER_HOST}"
  export CUSTOMER_PORTAL_FRONTEND_URL="https://${FRONTEND_CUSTOMER_HOST}"
  export COOKIE_CONSENT_URL="https://${API_COOKIE_CONSENT_HOST}"

else
  echo "⚠️  Exporting URLs for development mode (dev)."
  # Development (localhost)
  export POSTGRES_DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5432/postgres"
  export MONGO_URI="mongodb://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:27017"
  export RABBITMQ_HOST="127.0.0.1"
  export REDIS_HOST="127.0.0.1"
  export S3_URL="127.0.0.1:9000"
  export OPENSEARCH_HOST="127.0.0.1"
  export DATA_VEDA_URL="http://127.0.0.1:9080"

  export NEXT_PUBLIC_ADMIN_URL="http://127.0.0.1:9900/api/v1"
  export NEXT_PUBLIC_CUSTOMER_URL="http://127.0.0.1:9901"
  export CMP_ADMIN_BACKEND_URL="http://127.0.0.1:9900" 
  export CMP_ADMIN_FRONTEND_URL="http://127.0.0.1:3000"
  export CMP_NOTICE_WORKER_URL="http://127.0.0.1:9902"
  export CUSTOMER_PORTAL_BACKEND_URL="http://127.0.0.1:9901"
  export CUSTOMER_PORTAL_FRONTEND_URL="http://127.0.0.1:3001"
  export COOKIE_CONSENT_URL="http://127.0.0.1:9903"
fi

# Common exports

export NEXT_PUBLIC_DF_ID="${DF_ID}"
export DB_NAME_CONCUR_MASTER="concur_master_${MODE}"
export DB_NAME_COOKIE_MANAGEMENT="cookie_management_${MODE}"
export DB_NAME_CONCUR_LOGS="concur_logs_${MODE}"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=1440
export NOTICE_ACCESS_TOKEN_EXPIRE_HOURS=1
export S3_SECURE=false
export NOTICE_WORKER_BUCKET="notice-worker-${MODE}"
export PROCESSED_FILES_BUCKET="processed-files-${MODE}"
export UNPROCESSED_FILES_BUCKET="unprocessed-files-${MODE}"
export UNPROCESSED_VERIFICATION_FILES_BUCKET="unprocessed-verification-files-${MODE}"
export FAILED_RECORDS_BUCKET="failed-records-${MODE}"
export FAILED_RECORDS_BUCKET_EXTERNAL="failed-external-${MODE}"
export TRAINING_NUGGETS_BUCKET="concur-training-${MODE}"
export KYC_DOCUMENTS_BUCKET="kyc-documents-${MODE}"
export DPAR_BULK_UPLOAD_BUCKET="dpar-bulk-upload-${MODE}"
export COOKIE_CONSENT_BUCKET="cookie-consent-scripts-${MODE}"
export CUSTOMER_PORTAL_BUCKET="customer-portal-${MODE}"
export KYC_DOCUMENTS_BUCKET="kyc-documents-${MODE}"
export RABBITMQ_PORT=5672
export RABBITMQ_MANAGEMENT_PORT=15672
export RABBITMQ_VHOST_NAME="sahaj_${MODE}"
export RABBITMQ_POOL_SIZE=5
export REDIS_PORT=6333
export REDIS_MAX_CONNECTIONS=200
export REDIS_MAX_CONNECTIONS_PER_NODE=50
export WEBHOOK_MAX_RETRIES=3
export WEBHOOK_RETRY_TTL_MS=10000
export OPENSEARCH_PORT=9200
export OTP_EXPIRY_SECONDS=300
export SMS_SENDER_ID="CONCUR"
export RATE_LIMIT_DEFAULT="5/minute, 60/hour"


# If sourced, return silently; if executed directly, exit
if [ "${BASH_SOURCE[0]}" != "$0" ]; then
  return 0
else
  exit 0
fi

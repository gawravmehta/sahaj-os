#!/usr/bin/env bash
set -euo pipefail

# Issues certs using env-based subdomains and reloads nginx
: "${SUPERADMIN_EMAIL:?SUPERADMIN_EMAIL must be set}"
: "${API_CMP_HOST:?}"
: "${API_CUSTOMER_HOST:?}"
: "${API_NOTICE_WORKER_HOST:?}"
: "${API_COOKIE_CONSENT_HOST:?}"
: "${FRONTEND_CMP_HOST:?}"
: "${FRONTEND_CUSTOMER_HOST:?}"
: "${MINIO_BROWSER_URL:?}"

DOMAINS=(
  "$API_CMP_HOST"
  "$API_CUSTOMER_HOST"
  "$API_NOTICE_WORKER_HOST"
  "$API_COOKIE_CONSENT_HOST"
  "$FRONTEND_CMP_HOST"
  "$FRONTEND_CUSTOMER_HOST"
  "$MINIO_BROWSER_URL"
)

echo "Issuing/renewing certificates for:"
CERTBOT_ARGS=()
for d in "${DOMAINS[@]}"; do
  echo " - $d"
  CERTBOT_ARGS+=("-d" "$d")
done

sudo certbot --nginx --email "${SUPERADMIN_EMAIL}" --agree-tos --no-eff-email "${CERTBOT_ARGS[@]}"

echo "Reloading nginx to pick up certificates..."
sudo systemctl reload nginx

echo "✅ Certificates issued/renewed and nginx reloaded."

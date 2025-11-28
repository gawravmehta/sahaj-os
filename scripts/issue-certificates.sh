#!/usr/bin/env bash
set -euo pipefail

# Issues certs using env-based subdomains and reloads nginx
: "${API_CMP_HOST:?}"
: "${API_CUSTOMER_HOST:?}"
: "${FRONTEND_CMP_HOST:?}"
: "${FRONTEND_CUSTOMER_HOST:?}"

DOMAINS=(
  "$API_CMP_HOST"
  "$API_CUSTOMER_HOST"
  "$FRONTEND_CMP_HOST"
  "$FRONTEND_CUSTOMER_HOST"
)

echo "Issuing/renewing certificates for:"
for d in "${DOMAINS[@]}"; do
  echo " - $d"
done

# Run certbot (uses --nginx installer to auto-edit nginx confs)
# This will be interactive on first run; for fully non-interactive, add --non-interactive and contact options.
sudo certbot --nginx -d "${DOMAINS[@]}"

echo "Reloading nginx to pick up certificates..."
sudo systemctl reload nginx

echo "✅ Certificates issued/renewed and nginx reloaded."

#!/usr/bin/env bash
set -euo pipefail

# Generates one nginx config file per subdomain (sites-available/<host>.conf)
# Required env vars (exported by deploy-all.sh):
: "${API_CMP_HOST:?}"
: "${API_CUSTOMER_HOST:?}"
: "${API_NOTICE_WORKER_HOST:?}"
: "${API_COOKIE_CONSENT_HOST:?}"
: "${FRONTEND_CMP_HOST:?}"
: "${FRONTEND_CUSTOMER_HOST:?}"
: "${MINIO_BROWSER_URL:?}"

NGINX_CONF_DIR="/etc/nginx/sites-available"
ENABLED_DIR="/etc/nginx/sites-enabled"

# Helper to write and enable a config
_write_and_enable() {
  local host="$1"
  local upstream="$2"
  local file="$NGINX_CONF_DIR/${host}.conf"

  sudo tee "$file" >/dev/null <<EOF
server {
    listen 80;
    server_name ${host};

    location / {
        proxy_pass ${upstream};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # websocket / upgrade support
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;

        client_max_body_size 50M;
    }
}
EOF

  # create/replace symlink in sites-enabled
  sudo ln -sf "$file" "$ENABLED_DIR/${host}.conf"
  echo "-> Generated and enabled $file"
}

echo "Generating nginx configs for the four subdomains..."

_write_and_enable "${API_CMP_HOST}" "http://127.0.0.1:3330"
_write_and_enable "${API_CUSTOMER_HOST}" "http://127.0.0.1:3331"
_write_and_enable "${API_NOTICE_WORKER_HOST}" "http://127.0.0.1:3332"
_write_and_enable "${API_COOKIE_CONSENT_HOST}" "http://127.0.0.1:3333"
_write_and_enable "${FRONTEND_CMP_HOST}" "http://127.0.0.1:3000"
_write_and_enable "${FRONTEND_CUSTOMER_HOST}" "http://127.0.0.1:3001"
_write_and_enable "${MINIO_BROWSER_URL}" "http://127.0.0.1:9000"

echo "Testing nginx configuration..."
sudo nginx -t

echo "Reloading nginx..."
sudo systemctl reload nginx

echo "✅ NGINX configs written and reloaded."

#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/build-deploy-all.sh
# Requirements:
# - scripts/generate-secrets.sh must exist (sourced)
# - scripts/export-urls.sh must exist (sourced with 'prod' mode)
# - scripts/generate-nginx-configs.sh and scripts/issue-certificates.sh must exist (executed)
# - docker compose or docker-compose must be installed
# - nginx & certbot installed (checked before nginx generation/cert issuance)

export ENVIRONMENT="production"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GENSEC="$SCRIPT_DIR/generate-secrets.sh"
EXPORT_URLS="$SCRIPT_DIR/export-urls.sh"
GEN_NGINX="$SCRIPT_DIR/generate-nginx-configs.sh"
ISSUE_CERTS="$SCRIPT_DIR/issue-certificates.sh"

for file in "$GENSEC" "$EXPORT_URLS" "$GEN_NGINX" "$ISSUE_CERTS"; do
  if [ ! -f "$file" ]; then
    echo "❌ Required helper not found: $file"
    exit 1
  fi
done

source "$GENSEC"
echo "✅ Secrets generated (sourced)."

source "$EXPORT_URLS" prod
echo "✅ URL envs exported (production mode)."

NGINX_OK=true
CERTBOT_OK=true

if ! command -v nginx >/dev/null 2>&1; then
  echo "❌ nginx not found."
  NGINX_OK=false
fi
if ! command -v certbot >/dev/null 2>&1; then
  echo "❌ certbot not found."
  CERTBOT_OK=false
fi

if ! $NGINX_OK || ! $CERTBOT_OK; then
  echo
  echo "Installation hints:"
  if ! $NGINX_OK; then
    echo " - Install nginx: sudo apt update && sudo apt install -y nginx"
  fi
  if ! $CERTBOT_OK; then
    echo " - Install certbot via snap:"
    echo "     sudo snap install core && sudo snap refresh core"
    echo "     sudo snap install --classic certbot"
    echo "     sudo ln -s /snap/bin/certbot /usr/bin/certbot"
  fi
  echo
  echo "After installing nginx and certbot, re-run this script."
  exit 1
fi

echo "✅ nginx and certbot found."

echo
echo "▶ Generating nginx configs (may require sudo)..."
if ! bash "$GEN_NGINX"; then
  echo "❌ Failed to generate nginx configs via $GEN_NGINX"
  exit 1
fi
echo "✅ nginx configs generated."

if docker compose version > /dev/null 2>&1; then
  DC_BIN=(docker compose)
  PARALLEL_SUPPORTED=true
elif docker-compose version > /dev/null 2>&1; then
  DC_BIN=(docker-compose)
  PARALLEL_SUPPORTED=false
else
  echo "❌ docker compose (v2) or docker-compose (v1) not found in PATH."
  exit 1
fi

CMD=("${DC_BIN[@]}")
[ -f "$REPO_ROOT/docker-compose.yml" ] && CMD+=( -f "$REPO_ROOT/docker-compose.yml" )

PLATFORM="$(uname -s)"

if [ -d "$REPO_ROOT/infrastructure" ]; then
  while IFS= read -r -d '' file; do
    fname="$(basename "$file")"
    if [ "$PLATFORM" != "Linux" ] && [ "$fname" = "docker-compose.monitoring.yml" ]; then
      continue
    fi
    CMD+=( -f "$file" )
  done < <(find "$REPO_ROOT/infrastructure" -type f -iname 'docker-compose*.yml' -print0 | sort -z)
fi

if [ "$PLATFORM" != "Linux" ]; then
  WIN_MON="$REPO_ROOT/infrastructure/docker-compose-dev/docker-compose.monitoring.windows.yml"
  if [ -f "$WIN_MON" ]; then
    CMD+=( -f "$WIN_MON" )
    echo "Using Windows monitoring compose override: $WIN_MON"
  fi
fi

if [ -d "$REPO_ROOT/services" ]; then
  while IFS= read -r -d '' svcfile; do
    CMD+=( -f "$svcfile" )
  done < <(find "$REPO_ROOT/services" -maxdepth 2 -type f -iname 'docker-compose.yml' -print0 | sort -z)
fi

echo
echo "▶ Final compose build command:"
printf ' %q' "${CMD[@]}"
if [ "$PARALLEL_SUPPORTED" = true ]; then
  echo " build --pull --parallel"
else
  echo " build --pull"
fi
echo

if [ "$PARALLEL_SUPPORTED" = true ]; then
  "${CMD[@]}" build --pull --parallel
else
  "${CMD[@]}" build --pull
fi

echo
echo "✅ Build finished. No containers have been started by build."

echo
echo "▶ Running: ${CMD[*]} up -d"
"${CMD[@]}" up -d

echo
echo "✅ All compose stacks requested up -d (containers starting)."

echo
echo "▶ Issuing/renewing certificates for subdomains (requires sudo)..."
if ! bash "$ISSUE_CERTS"; then
  echo "❌ issue-certificates.sh failed. Please run it manually."
  exit 1
fi

echo
echo "✅ All Containers started and certificates issued/renewed successfully."

read -p "Do you want to display the environment variables? (y/n): " show_env
if [[ "$show_env" =~ ^[Yy]$ ]]; then
  echo "Environment variables:"
  printenv
fi

exit 0

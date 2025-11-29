#!/usr/bin/env bash
set -euo pipefail

# scripts/deploy-all.sh
# 1) source generate-secrets.sh
# 2) export subdomain envs (MAIN_DOMAIN must exist)
# 3) check nginx & certbot installed
# 4) run generate-nginx-configs.sh (must be in scripts/)
# 5) assemble compose -f chain and run up -d
# 6) run issue-certificates.sh (must be in scripts/)
#
export ENVIRONMENT="production"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---- 0. ensure required helper scripts exist ----
GENSEC="$SCRIPT_DIR/generate-secrets.sh"
GEN_NGINX="$SCRIPT_DIR/generate-nginx-configs.sh"
ISSUE_CERTS="$SCRIPT_DIR/issue-certificates.sh"

if [ ! -f "$GENSEC" ]; then
  echo "❌ generate-secrets.sh not found at $GENSEC"
  exit 1
fi
if [ ! -f "$GEN_NGINX" ]; then
  echo "❌ generate-nginx-configs.sh not found at $GEN_NGINX"
  echo "Please create $GEN_NGINX (it must generate /etc/nginx/sahaj-*.conf and enable them)."
  exit 1
fi
if [ ! -f "$ISSUE_CERTS" ]; then
  echo "❌ issue-certificates.sh not found at $ISSUE_CERTS"
  echo "Please create $ISSUE_CERTS (it should call certbot and reload nginx)."
  exit 1
fi

# ---- 1. Source generate-secrets so vars are exported into this process ----
# generate-secrets.sh is intended to be sourced so env vars persist for the caller
# shellcheck disable=SC1090
source "$GENSEC"
echo "✅ Secrets generated (sourced)."

# ---- 2. Export public + backend service URLs (via export-urls.sh in prod mode) ----
source "$SCRIPT_DIR/export-urls.sh" prod
echo "✅ URLs exported for production mode."

# ---- 3. Check nginx & certbot presence (fail early with hints) ----
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

# ---- 4. detect compose binary ----
if docker compose version > /dev/null 2>&1; then
  DC_BIN=(docker compose)
elif docker-compose version > /dev/null 2>&1; then
  DC_BIN=(docker-compose)
else
  echo "❌ docker compose (v2) or docker-compose (v1) not found in PATH."
  exit 1
fi

# ---- 5. Run nginx config generation BEFORE composing stack ----
# generate-nginx-configs.sh will use MAIN_DOMAIN env and will typically require sudo to write /etc/nginx
echo
echo "▶ Generating nginx configs (this may require sudo)..."
# execute the script (do not source) so it runs with its own privileges
if ! bash "$GEN_NGINX"; then
  echo "❌ Failed to generate nginx configs via $GEN_NGINX"
  exit 1
fi
echo "✅ nginx configs generated (and nginx reloaded by the script)."


# ---- 6. assemble -f chain (root, infra, services/*/docker-compose.yml) ----
CMD=("${DC_BIN[@]}")
[ -f "$REPO_ROOT/docker-compose.yml" ] && CMD+=( -f "$REPO_ROOT/docker-compose.yml" )

PLATFORM="$(uname -s)"

if [ -d "$REPO_ROOT/infrastructure" ]; then
  while IFS= read -r -d '' file; do
    fname="$(basename "$file")"
    # On non-Linux, skip the linux monitoring compose; we'll add windows override if present
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

# ---- 7. run compose up -d (containers get the exported envs) ----
echo
echo "Running: ${CMD[*]} up -d"
"${CMD[@]}" up -d

echo
echo "✅ All compose stacks requested up -d (containers starting)."

# ---- 8. Issue certificates after compose is up ----
echo
echo "▶ Issuing/renewing certificates for subdomains using certbot (this will require sudo)..."
# script issue-certificates.sh expects MAIN_DOMAIN in env
if ! bash "$ISSUE_CERTS"; then
  echo "❌ issue-certificates.sh failed. Please run it manually."
  exit 1
fi

echo
echo "✅ Certificates issued/renewed and nginx reloaded."

exit 0

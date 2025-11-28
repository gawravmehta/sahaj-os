#!/usr/bin/env bash
set -euo pipefail

# scripts/build-images.sh
# Build images for the entire repo via a single compose -f chain.
# This script DOES NOT source generate-secrets.sh.
# It will attempt to read MAIN_DOMAIN and DF_ID from the environment first,
# then from config.json (repo root) if not present.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_JSON="$REPO_ROOT/config.json"

# ---------- Helper: read keys from config.json ----------
_read_from_config_json() {
  local key="$1" default="$2" result
  if command -v python3 >/dev/null 2>&1; then
    result=$(cat "$CONFIG_JSON" | python3 -c "import json,sys
try:
  j=json.load(sys.stdin)
except Exception:
  print('')
  sys.exit(0)
print(j.get('$key','') or '')" 2>/dev/null || true)
    printf '%s' "$result"
    return
  fi

  if command -v jq >/dev/null 2>&1; then
    result=$(jq -r --arg k "$key" '.[$k] // ""' "$CONFIG_JSON" 2>/dev/null || echo "")
    printf '%s' "$result"
    return
  fi

  # very small awk fallback (best-effort for simple JSON)
  result=$(awk -v k="\"${key}\"" '
    { line = line $0 }
    END {
      n = match(line, k "[[:space:]]*:[[:space:]]*\"")
      if (n) {
        rest = substr(line, n + length(k) + 1)
        if (match(rest, /:[[:space:]]*"/)) { val = substr(rest, RLENGTH+1) } else { val = rest }
        if (match(val, /"([^"]*)"/, arr)) { print arr[1] } else { print "" }
      } else { print "" }
    }
  ' "$CONFIG_JSON" 2>/dev/null || echo "")
  printf '%s' "$result"
}

# ---------- 0. Get MAIN_DOMAIN and DF_ID (env -> config.json -> empty) ----------
if [ -n "${MAIN_DOMAIN:-}" ] 2>/dev/null; then
  DOMAIN_FROM="env"
else
  DOMAIN_FROM="config"
  if [ -f "$CONFIG_JSON" ] && [ -r "$CONFIG_JSON" ]; then
    MAIN_DOMAIN="$(_read_from_config_json "main_domain" "")"
  else
    MAIN_DOMAIN=""
  fi
fi

if [ -n "${DF_ID:-}" ] 2>/dev/null; then
  DFID_FROM="env"
else
  DFID_FROM="config"
  if [ -f "$CONFIG_JSON" ] && [ -r "$CONFIG_JSON" ]; then
    DF_ID="$(_read_from_config_json "df_id" "")"
  else
    DF_ID=""
  fi
fi

# Trim possible surrounding whitespace (defensive)
MAIN_DOMAIN="$(printf '%s' "$MAIN_DOMAIN" | awk '{$1=$1;print}')"
DF_ID="$(printf '%s' "$DF_ID" | awk '{$1=$1;print}')"

if [ -n "$MAIN_DOMAIN" ]; then
  export API_CMP_HOST="api-cmp.${MAIN_DOMAIN}"
  export API_CUSTOMER_HOST="api-customer.${MAIN_DOMAIN}"
  export FRONTEND_CMP_HOST="cmp.${MAIN_DOMAIN}"
  export FRONTEND_CUSTOMER_HOST="customer.${MAIN_DOMAIN}"

  export NEXT_PUBLIC_ADMIN_URL="https://${API_CMP_HOST}/api/v1"
  export NEXT_PUBLIC_CUSTOMER_URL="https://${API_CUSTOMER_HOST}"
  echo "✅ MAIN_DOMAIN resolved from ${DOMAIN_FROM}: ${MAIN_DOMAIN}"
  echo "✅ Exported subdomain envs:"
  echo "  API_CMP_HOST=${API_CMP_HOST}"
  echo "  API_CUSTOMER_HOST=${API_CUSTOMER_HOST}"
  echo "  FRONTEND_CMP_HOST=${FRONTEND_CMP_HOST}"
  echo "  FRONTEND_CUSTOMER_HOST=${FRONTEND_CUSTOMER_HOST}"
  echo "  NEXT_PUBLIC_ADMIN_URL=${NEXT_PUBLIC_ADMIN_URL}"
  echo "  NEXT_PUBLIC_CUSTOMER_URL=${NEXT_PUBLIC_CUSTOMER_URL}"
else
  echo "⚠️  MAIN_DOMAIN not found in env nor config.json; skipping export of subdomain envs."
fi

if [ -n "$DF_ID" ]; then
  export NEXT_PUBLIC_DF_ID="${DF_ID}"
  echo "✅ DF_ID resolved from ${DFID_FROM}: ${DF_ID}"
  echo "✅ Exported NEXT_PUBLIC_DF_ID"
else
  echo "⚠️  DF_ID not found in env nor config.json; skipping NEXT_PUBLIC_DF_ID export."
fi

# ---------- detect compose binary and whether --parallel is supported ----------
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

# include root compose if present
if [ -f "$REPO_ROOT/docker-compose.yml" ]; then
  CMD+=( -f "$REPO_ROOT/docker-compose.yml" )
fi

PLATFORM="$(uname -s)"

# include infra compose files deterministically
if [ -d "$REPO_ROOT/infrastructure" ]; then
  while IFS= read -r -d '' file; do
    fname="$(basename "$file")"
    # on non-Linux, skip the linux monitoring base (we'll add windows override later)
    if [ "$PLATFORM" != "Linux" ] && [ "$fname" = "docker-compose.monitoring.yml" ]; then
      continue
    fi
    CMD+=( -f "$file" )
  done < <(find "$REPO_ROOT/infrastructure" -type f -iname 'docker-compose*.yml' -print0 | sort -z)
fi

# on non-Linux, add windows monitoring override if present
if [ "$PLATFORM" != "Linux" ]; then
  WIN_MON="$REPO_ROOT/infrastructure/docker-compose-dev/docker-compose.monitoring.windows.yml"
  if [ -f "$WIN_MON" ]; then
    CMD+=( -f "$WIN_MON" )
    echo "Using Windows monitoring compose: $WIN_MON"
  fi
fi

# include per-service compose files (only those that exist)
if [ -d "$REPO_ROOT/services" ]; then
  while IFS= read -r -d '' svcfile; do
    CMD+=( -f "$svcfile" )
  done < <(find "$REPO_ROOT/services" -maxdepth 2 -type f -iname 'docker-compose.yml' -print0 | sort -z)
fi

# Print final composed command for user
echo
echo "Final compose build command:"
printf ' %q' "${CMD[@]}"
if [ "$PARALLEL_SUPPORTED" = true ]; then
  echo " build --pull --parallel"
else
  echo " build --pull"
fi
echo

# Execute build (only). Use --parallel if supported.
if [ "$PARALLEL_SUPPORTED" = true ]; then
  "${CMD[@]}" build --pull --parallel
else
  "${CMD[@]}" build --pull
fi

echo
echo "✅ Build finished. No containers were started."
exit 0

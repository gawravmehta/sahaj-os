#!/usr/bin/env bash
set -euo pipefail

# scripts/generate-secrets.sh (strict)
# - Must be sourced to export env vars into caller shell:  source ./scripts/generate-secrets.sh
# - Can be executed directly for debugging with --dump: ./scripts/generate-secrets.sh --dump
#
# Requirements (strict):
#  - config.json must exist at repo root and contain: main_domain, df_id, superadmin_email
#  - python3 OR jq must be installed (for parsing config.json)
#  - openssl must be installed (for ECDSA key generation)
#
# Outputs (exported env vars):
#  POSTGRES_USER, POSTGRES_PASSWORD, REDIS_USERNAME, REDIS_MASTER_PASSWORD, REDIS_PASSWORD,
#  RABBITMQ_USER, RABBITMQ_PASSWORD, ERLANG_COOKIE, GF_SECURITY_ADMIN_USER,
#  GF_SECURITY_ADMIN_PASSWORD, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD, SECRET_KEY,
#  MAIN_DOMAIN, SUPERADMIN_EMAIL, TEMPORARY_PASSWORD, DF_ID,
#  PRIVATE_KEY_PEM, PUBLIC_KEY_PEM, SIGNING_KEY_ID
#
# If any requirement is missing the script will exit (or return when sourced) with
# a detailed error and recommended fix.

# ----------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_JSON="$REPO_ROOT/config.json"

# Utility to detect if script is being sourced
_is_sourced() {
  # returns 0 if sourced, 1 if executed
  [ "${BASH_SOURCE[0]}" != "$0" ]
}

# Fatal helper: return when sourced, exit when executed
fatal() {
  local msg="$1"
  if _is_sourced; then
    printf 'ERROR: %s\n' "$msg" >&2
    return 1
  else
    printf 'ERROR: %s\n' "$msg" >&2
    exit 1
  fi
}

# Suggest helper to show cp command for example
suggest_copy_example() {
  if [ -f "$REPO_ROOT/config.json.example" ]; then
    cat <<EOF >&2

Suggested fix:
  cp "$REPO_ROOT/config.json.example" "$REPO_ROOT/config.json"
  # then edit config.json and fill in "main_domain", "df_id", "superadmin_email"
EOF
  else
    cat <<EOF >&2

Suggested fix:
  Create $REPO_ROOT/config.json with keys:
    "main_domain": "example.com",
    "df_id": "your-df-id",
    "superadmin_email": "you@example.com"

You can use jq or python3 to validate JSON once created.
EOF
  fi
}

# -------------------------
# Strict pre-checks
# -------------------------
# 1) config.json must exist and be readable
if [ ! -f "$CONFIG_JSON" ]; then
  printf '❌ Required config.json not found at: %s\n' "$CONFIG_JSON" >&2
  suggest_copy_example
  fatal "config.json is required. See suggestion above."
fi
if [ ! -r "$CONFIG_JSON" ]; then
  fatal "config.json exists but is not readable by $(whoami). Fix permissions: chmod or chown accordingly."
fi

# 2) need either python3 or jq to parse config.json
if ! command -v python3 >/dev/null 2>&1 && ! command -v jq >/dev/null 2>&1; then
  cat <<EOF >&2
❌ Neither python3 nor jq found. The script requires one to parse config.json.

Install one of them, for example:
  sudo apt update
  sudo apt install -y python3

or (if you prefer jq):
  sudo apt update
  sudo apt install -y jq

Then re-run the script.
EOF
  fatal "Missing python3/jq"
fi

# 3) openssl must be present for ECDSA key generation
if ! command -v openssl >/dev/null 2>&1; then
  cat <<EOF >&2
❌ openssl not found. Required to generate ECDSA keys.

Install on Debian/Ubuntu:
  sudo apt update && sudo apt install -y openssl

On RHEL/CentOS:
  sudo yum install -y openssl

Then re-run the script.
EOF
  fatal "Missing openssl"
fi

# -------------------------
# Helpers
# -------------------------
_read_from_config_json() {
  local key="$1"
  if command -v python3 >/dev/null 2>&1; then
    # Use python3 via stdin (robust)
    cat "$CONFIG_JSON" | python3 -c "import json,sys
try:
  j=json.load(sys.stdin)
except Exception:
  sys.exit(0)
print(j.get('$key','') or '')" 2>/dev/null || true
    return
  fi

  if command -v jq >/dev/null 2>&1; then
    jq -r ".[\"$key\"] // \"\"" "$CONFIG_JSON" 2>/dev/null || true
    return
  fi

  # Shouldn't reach here due to pre-checks
  echo "" 
}

# -------------------------
# Parse required keys from config.json (strict)
# -------------------------
MAIN_DOMAIN="$(printf '%s' "$(_read_from_config_json "main_domain")" | awk '{$1=$1;print}')"
DF_ID="$(printf '%s' "$(_read_from_config_json "df_id")" | awk '{$1=$1;print}')"
SUPERADMIN_EMAIL="$(printf '%s' "$(_read_from_config_json "superadmin_email")" | awk '{$1=$1;print}')"
TEMPORARY_PASSWORD="$(printf '%s' "$(_read_from_config_json "temporary_password")" | awk '{$1=$1;print}')"

missing_keys=()
[ -z "$MAIN_DOMAIN" ] && missing_keys+=("main_domain")
[ -z "$DF_ID" ] && missing_keys+=("df_id")
[ -z "$SUPERADMIN_EMAIL" ] && missing_keys+=("superadmin_email")

if [ "${#missing_keys[@]}" -ne 0 ]; then
  printf '❌ config.json is missing required key(s): %s\n' "$(IFS=,; echo "${missing_keys[*]}")" >&2
  echo "Please add them to $CONFIG_JSON or export corresponding environment variables before sourcing." >&2
  suggest_copy_example
  fatal "Missing keys in config.json"
fi

# Export config-derived values
export MAIN_DOMAIN
export DF_ID
export SUPERADMIN_EMAIL
if [ -n "$TEMPORARY_PASSWORD" ]; then
  export TEMPORARY_PASSWORD
fi

# -------------------------
# Generate random secrets (always)
# -------------------------
random_user() {
  local prefix="$1"
  local suffix
  suffix=$(tr -dc 'a-z0-9_' </dev/urandom | head -c8)
  printf '%s' "${prefix}${suffix}"
}

random_pass() {
  tr -dc 'A-Za-z0-9' </dev/urandom | head -c32
}

export POSTGRES_USER="$(printf '%s' "$(random_user "ferret_")")"
export REDIS_USERNAME="$(printf '%s' "$(random_user "redis_")")"
export RABBITMQ_USER="$(printf '%s' "$(random_user "mqtt_")")"
export GF_SECURITY_ADMIN_USER="$(printf '%s' "$(random_user "gfadmin_")")"
export MINIO_ROOT_USER="$(printf '%s' "$(random_user "minio_")")"
export OPENSEARCH_USERNAME="admin"

export SECRET_KEY="$(printf '%s' "$(random_pass)")"
export POSTGRES_PASSWORD="$(printf '%s' "$(random_pass)")"
export REDIS_MASTER_PASSWORD="$(printf '%s' "$(random_pass)")"
export REDIS_PASSWORD="$(printf '%s' "$(random_pass)")"
export RABBITMQ_PASSWORD="$(printf '%s' "$(random_pass)")"
export ERLANG_COOKIE="$(printf '%s' "$(random_pass)")"
export GF_SECURITY_ADMIN_PASSWORD="$(printf '%s' "$(random_pass)")"
export MINIO_ROOT_PASSWORD="$(printf '%s' "$(random_pass)")"

# -------------------------
# Generate ECDSA keypair in-memory (no files)
# -------------------------
SIGNING_KEY_ID="cmp-key-2025"

# private key PEM generated to variable
PRIVATE_KEY_PEM="$(openssl ecparam -name prime256v1 -genkey -noout 2>/dev/null || true)"

if [ -z "${PRIVATE_KEY_PEM:-}" ]; then
  fatal "openssl failed to generate a private key"
fi

PUBLIC_KEY_PEM="$(printf '%s' "$PRIVATE_KEY_PEM" | openssl ec -pubout -outform PEM 2>/dev/null || true)"

if [ -z "${PUBLIC_KEY_PEM:-}" ]; then
  fatal "openssl failed to derive public key from private key"
fi

# Export keys and ID
export PRIVATE_KEY_PEM
export PUBLIC_KEY_PEM
export SIGNING_KEY_ID

# -------------------------
# If executed directly support --dump
# -------------------------
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  DUMP=false
  for arg in "$@"; do
    case "$arg" in
      --dump) DUMP=true ;;
      *) printf 'Unknown arg: %s\n' "$arg" >&2; printf 'Usage: %s [--dump]\n' "$0" >&2; exit 1 ;;
    esac
  done

  if [ "$DUMP" = true ]; then
    echo "Exported environment variables:"
    echo "MAIN_DOMAIN=${MAIN_DOMAIN:-}"
    echo "DF_ID=${DF_ID:-}"
    echo "SUPERADMIN_EMAIL=${SUPERADMIN_EMAIL:-}"
    echo "TEMPORARY_PASSWORD=${TEMPORARY_PASSWORD:-}"
    echo "POSTGRES_USER=${POSTGRES_USER:-}"
    echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-}"
    echo "REDIS_USERNAME=${REDIS_USERNAME:-}"
    echo "REDIS_MASTER_PASSWORD=${REDIS_MASTER_PASSWORD:-}"
    echo "REDIS_PASSWORD=${REDIS_PASSWORD:-}"
    echo "RABBITMQ_USER=${RABBITMQ_USER:-}"
    echo "RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-}"
    echo "ERLANG_COOKIE=${ERLANG_COOKIE:-}"
    echo "GF_SECURITY_ADMIN_USER=${GF_SECURITY_ADMIN_USER:-}"
    echo "GF_SECURITY_ADMIN_PASSWORD=${GF_SECURITY_ADMIN_PASSWORD:-}"
    echo "MINIO_ROOT_USER=${MINIO_ROOT_USER:-}"
    echo "MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-}"
    echo "OPENSEARCH_USERNAME=${OPENSEARCH_USERNAME:-}"
    echo "SIGNING_KEY_ID=${SIGNING_KEY_ID:-}"
    echo
    echo "PUBLIC_KEY_PEM:"
    printf '%s\n' "$PUBLIC_KEY_PEM"
    echo
    echo "PRIVATE_KEY_PEM:"
    # Private key is sensitive; user explicitly requested dump.
    printf '%s\n' "$PRIVATE_KEY_PEM"
  fi

  exit 0
fi

# If the script is sourced, return normally
if _is_sourced; then
  return 0
else
  exit 0
fi

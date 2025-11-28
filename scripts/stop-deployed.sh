#!/usr/bin/env bash
set -euo pipefail

# scripts/stop-deployed.sh
# - Locates all compose files (root, infra, per-service)
# - Executes `docker compose down -v` to cleanly stop and remove containers + volumes
# - Does NOT remove images

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# detect compose binary
if docker compose version > /dev/null 2>&1; then
  DC_BIN=(docker compose)
elif docker-compose version > /dev/null 2>&1; then
  DC_BIN=(docker-compose)
else
  echo "❌ docker compose (v2) or docker-compose (v1) not found in PATH."
  exit 1
fi

# assemble -f chain
CMD=("${DC_BIN[@]}")
[ -f "$REPO_ROOT/docker-compose.yml" ] && CMD+=( -f "$REPO_ROOT/docker-compose.yml" )

PLATFORM="$(uname -s)"

# add infrastructure compose files deterministically
if [ -d "$REPO_ROOT/infrastructure" ]; then
  while IFS= read -r -d '' file; do
    fname="$(basename "$file")"
    # skip Linux-only monitoring file on non-Linux
    if [ "$PLATFORM" != "Linux" ] && [ "$fname" = "docker-compose.monitoring.yml" ]; then
      continue
    fi
    CMD+=( -f "$file" )
  done < <(find "$REPO_ROOT/infrastructure" -type f -iname 'docker-compose*.yml' -print0 | sort -z)
fi

# on non-Linux, include windows override if available
if [ "$PLATFORM" != "Linux" ]; then
  WIN_MON="$REPO_ROOT/infrastructure/docker-compose-dev/docker-compose.monitoring.windows.yml"
  if [ -f "$WIN_MON" ]; then
    CMD+=( -f "$WIN_MON" )
    echo "Using Windows monitoring compose override: $WIN_MON"
  fi
fi

# include per-service compose files (only those that exist)
if [ -d "$REPO_ROOT/services" ]; then
  while IFS= read -r -d '' svcfile; do
    CMD+=( -f "$svcfile" )
  done < <(find "$REPO_ROOT/services" -maxdepth 2 -type f -iname 'docker-compose.yml' -print0 | sort -z)
fi

# show and run
echo
echo "Running: ${CMD[*]} down -v"
"${CMD[@]}" down -v

echo
echo "✅ All compose stacks brought down with volume removal."
exit 0

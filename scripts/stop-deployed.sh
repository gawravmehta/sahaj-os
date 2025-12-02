#!/usr/bin/env bash
set -euo pipefail

# scripts/stop-deployed.sh
# - Locates all compose files (root, infra, per-service)
# - Executes `docker compose down -v` to cleanly stop and remove containers + volumes
# - Does NOT remove images

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "⚠️  WARNING: This script will:"
echo "   • Stop all running SAHAJ containers"
echo "   • Remove all SAHAJ containers"
echo "   • Remove all volumes attached to SAHAJ containers"
echo "   • Remove all networks attached to SAHAJ containers"
echo ""
echo "   Docker built images will NOT be removed."
echo ""
read -p "Do you want to continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
  echo "Operation cancelled."
  exit 0
fi

if docker compose version > /dev/null 2>&1; then
  DC_BIN=(docker compose)
elif docker-compose version > /dev/null 2>&1; then
  DC_BIN=(docker-compose)
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
echo "Running: ${CMD[*]} down -v"
"${CMD[@]}" down -v 2>&1 | grep -v "variable is not set"

echo
echo "✅ All compose stacks brought down with volume removal."
exit 0

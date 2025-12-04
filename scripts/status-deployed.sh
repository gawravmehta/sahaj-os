#!/usr/bin/env bash
set -euo pipefail

# scripts/container-status.sh
# Shows status, uptime, health, ports, and last log line for each container (only from your compose files)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if docker compose version > /dev/null 2>&1; then
  DC_BIN=(docker compose)
elif docker-compose version > /dev/null 2>&1; then
  DC_BIN=(docker-compose)
else
  echo "❌ docker compose (v2) or docker-compose (v1) not found."
  exit 1
fi

CMD=("${DC_BIN[@]}")
[ -f "$REPO_ROOT/docker-compose.yml" ] && CMD+=( -f "$REPO_ROOT/docker-compose.yml" )

if [ -d "$REPO_ROOT/infrastructure" ]; then
  while IFS= read -r -d '' file; do
    CMD+=( -f "$file" )
  done < <(find "$REPO_ROOT/infrastructure" -type f -iname 'docker-compose*.yml' -print0 | sort -z)
fi

if [ -d "$REPO_ROOT/services" ]; then
  while IFS= read -r -d '' svcfile; do
    CMD+=( -f "$svcfile" )
  done < <(find "$REPO_ROOT/services" -maxdepth 2 -type f -iname 'docker-compose.yml' -print0 | sort -z)
fi

container_ids=($("${CMD[@]}" ps -q 2> >(grep -v "variable is not set" >&2)))

format_line() {
  local name="$1"
  local id="$2"
  local status="$3"
  local uptime="$4"
  local ports="$5"
  local health="$6"
  local log="$7"

  printf "\n%s => %s\n" "$status" "$name"
  echo "  ID     : $id"
  echo "  Uptime : $uptime"
  [ -n "$ports" ] && echo "  Ports  : $ports"
  [ -n "$health" ] && echo "  Health : $health"
  echo "  Last Log: $log"
}

for id in "${container_ids[@]}"; do
  inspect=$(docker inspect "$id")

  name=$(echo "$inspect" | jq -r '.[0].Name' | cut -c2-)
  status=$(echo "$inspect" | jq -r '.[0].State.Status')
  started_at=$(echo "$inspect" | jq -r '.[0].State.StartedAt')
  health=$(echo "$inspect" | jq -r '.[0].State.Health.Status // empty')
  ports=$(echo "$inspect" | jq -r '.[0].NetworkSettings.Ports | to_entries[]? | "\(.key) -> \(.value[0].HostPort)"' | paste -sd ", " -)

  if [[ "$status" == "running" ]]; then
    emoji="🟢"
  elif [[ "$status" == "restarting" ]]; then
    emoji="🟡"
  else
    emoji="🔴"
  fi

  uptime=$(docker ps -a --filter "id=$id" --format '{{.RunningFor}}')
  log=$(docker logs --tail 1 "$id" 2>&1 | tail -n 1)
  log="${log:-<no log output>}"

  format_line "$name" "$id" "$emoji $status" "$uptime" "$ports" "$health" "$log"
done

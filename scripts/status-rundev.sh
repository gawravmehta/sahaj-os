#!/usr/bin/env bash
set -euo pipefail

# Show status of per-service processes (pid/port/log) and docker-compose stack
# Usage: ./scripts/status-rundev.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# prefer docker compose detection
detect_compose() {
  if docker compose version > /dev/null 2>&1; then
    DC_BIN=(docker compose)
  elif docker-compose version > /dev/null 2>&1; then
    DC_BIN=(docker-compose)
  else
    DC_BIN=()
  fi
}

build_compose_cmd() {
  CMD=("${DC_BIN[@]}")
  [ -f "$REPO_ROOT/docker-compose.yml" ] && CMD+=( -f "$REPO_ROOT/docker-compose.yml" )

  PLATFORM="$(uname -s)"
  if [ -d "$REPO_ROOT/infrastructure" ]; then
    while IFS= read -r -d '' f; do
      fname="$(basename "$f")"
      if [ "$PLATFORM" != "Linux" ] && [ "$fname" = "docker-compose.monitoring.yml" ]; then
        continue
      fi
      CMD+=( -f "$f" )
    done < <(find "$REPO_ROOT/infrastructure" -type f -iname 'docker-compose*.yml' -print0 | sort -z)
  fi

  if [ "$PLATFORM" != "Linux" ]; then
    WIN_MON="$REPO_ROOT/infrastructure/docker-compose-dev/docker-compose.monitoring.windows.yml"
    if [ -f "$WIN_MON" ]; then
      CMD+=( -f "$WIN_MON" )
    fi
  fi
}

echo "Per-service process status (services/*.pid):"
if [ -d "$REPO_ROOT/services" ]; then
  printf "%-36s %-8s %-8s %-10s %s\n" "SERVICE" "PID" "STATE" "PORT" "LOG-LAST"
  echo "---------------------------------------------------------------------------------------------------"
  for svc in "$REPO_ROOT"/services/*/; do
    [ -d "$svc" ] || continue
    svcname="$(basename "$svc")"
    pidfile="$svc/service.pid"
    portfile="$svc/.port"
    logfile="$svc/service.log"
    pid=""
    state="stopped"
    port="-"

    if [ -f "$pidfile" ]; then
      pid="$(cat "$pidfile" 2>/dev/null || echo "")"
      if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
        state="running"
      else
        state="not-running"
      fi
    fi

    if [ -f "$portfile" ]; then
      port="$(cat "$portfile" 2>/dev/null || echo "-")"
    fi

    # show last log line (if any)
    lastlog="-"
    if [ -f "$logfile" ]; then
      lastlog="$(tail -n 1 "$logfile" 2>/dev/null || echo "-")"
    fi

    printf "%-36s %-8s %-8s %-10s %s\n" "$svcname" "$pid" "$state" "$port" "$lastlog"
  done
else
  echo "No services folder found at $REPO_ROOT/services"
fi

echo
# Show compose stack status if available
detect_compose
if [ "${#DC_BIN[@]}" -eq 0 ]; then
  echo "Docker Compose not found; skipping compose status."
  exit 0
fi

build_compose_cmd
echo
echo "Docker Compose stack status (using same -f chain as init-rundev):"
echo "Running: ${CMD[*]} ps"
# run compose ps and show it
"${CMD[@]}" ps 2>&1 | grep -v "variable is not set"
exit 0

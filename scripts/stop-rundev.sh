#!/usr/bin/env bash
set -euo pipefail

# scripts/stop-rundev.sh
# - No args   -> stop per-service processes (uvicorn/npm) only
# - -a / --all -> stop per-service processes AND run `docker compose down -v` (remove volumes)
#
# This version finds all processes whose command line contains the full service dir path,
# kills them gracefully (then SIGKILL if needed), and cleans up pid/port files.

DOCKER_DOWN=false

# parse args (only -a/--all supported)
while [ "${1:-}" != "" ]; do
  case "$1" in
    -a|--all) DOCKER_DOWN=true; shift ;;
    *) echo "Unknown argument: $1"; echo "Usage: $0 [-a|--all]"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# prefer docker compose v2, fallback to docker-compose v1
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
      # skip linux monitoring base on non-Linux
      if [ "$PLATFORM" != "Linux" ] && [ "$fname" = "docker-compose.monitoring.yml" ]; then
        continue
      fi
      CMD+=( -f "$f" )
    done < <(find "$REPO_ROOT/infrastructure" -type f -iname 'docker-compose*.yml' -print0 | sort -z)
  fi

  if [ "$PLATFORM" != "Linux" ]; then
    WIN_MON="$REPO_ROOT/infrastructure/docker-compose-dev/docker-compose.monitoring.windows.yml"
    [ -f "$WIN_MON" ] && CMD+=( -f "$WIN_MON" )
  fi
}

# graceful kill helper
graceful_kill() {
  local pid=$1 name=$2
  if kill -0 "$pid" 2>/dev/null; then
    echo "Stopping $name (pid $pid) ..."
    kill "$pid" 2>/dev/null || true
    # wait up to 6s for graceful shutdown
    for i in 1 2 3 4 5 6; do
      if kill -0 "$pid" 2>/dev/null; then
        sleep 1
      else
        break
      fi
    done
    if kill -0 "$pid" 2>/dev/null; then
      echo "PID $pid did not exit; sending SIGKILL"
      kill -9 "$pid" 2>/dev/null || true
      sleep 1
    else
      echo "Stopped $name (pid $pid)."
    fi
  else
    echo "PID $pid not running."
  fi
}

if [ ! -d "$REPO_ROOT/services" ]; then
  echo "No services directory found at: $REPO_ROOT/services"
  exit 0
fi

echo "Stopping per-service processes (searching by service path) ..."

any_running=false

for svc in "$REPO_ROOT"/services/*/; do
  [ -d "$svc" ] || continue
  svcname="$(basename "$svc")"
  svcdir="$(realpath "$svc")"
  pidfile="$svc/service.pid"
  portfile="$svc/.port"

  # find pids whose command line contains the full service directory path.
  # this matches uvicorn, python and any child processes started under that folder.
  mapfile -t pids < <(pgrep -f -- "-f" "" 2>/dev/null || true) # default placeholder; replaced below
  # Use more reliable approach: parse /proc/*/cmdline to match svcdir
  pids=()
  for p in /proc/[0-9]*; do
    pidnum="$(basename "$p")"
    if [ ! -r "$p/cmdline" ]; then
      continue
    fi
    # read cmdline safely
    cmdline=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null || true)
    # match the absolute svcdir in the command line (space or / boundaries)
    if [ -n "$cmdline" ] && echo "$cmdline" | grep -F -- "$svcdir" >/dev/null 2>&1; then
      pids+=("$pidnum")
    fi
  done

  # fallback: if no pids found via cmdline, try pidfile method
  if [ "${#pids[@]}" -eq 0 ] && [ -f "$pidfile" ]; then
    pf="$(cat "$pidfile" 2>/dev/null || echo "")"
    if [[ "$pf" =~ ^[0-9]+$ ]]; then
      if kill -0 "$pf" 2>/dev/null; then
        pids+=("$pf")
      fi
    fi
  fi

  if [ "${#pids[@]}" -eq 0 ]; then
    echo "No running processes found for $svcname (svcdir: $svcdir)."
    # cleanup stale pid/portfiles
    rm -f "$pidfile" "$portfile" 2>/dev/null || true
    continue
  fi

  # kill all found pids
  for pid in "${pids[@]}"; do
    if [[ "$pid" =~ ^[0-9]+$ ]]; then
      graceful_kill "$pid" "$svcname"
    fi
  done

  # After killing, remove pidfile/portfile if present
  rm -f "$pidfile" "$portfile" 2>/dev/null || true
done

# final check: any remaining pidfiles that correspond to running processes?
for svc in "$REPO_ROOT"/services/*/; do
  [ -d "$svc" ] || continue
  pidfile="$svc/service.pid"
  if [ -f "$pidfile" ]; then
    pid="$(cat "$pidfile" 2>/dev/null || echo "")"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      any_running=true
      break
    else
      rm -f "$pidfile" 2>/dev/null || true
    fi
  fi
done

# If user requested -a/--all, bring down docker compose with volumes removed
if [ "$DOCKER_DOWN" = true ]; then
  # detect compose
  if docker compose version > /dev/null 2>&1; then
    DC_BIN=(docker compose)
  elif docker-compose version > /dev/null 2>&1; then
    DC_BIN=(docker-compose)
  else
    DC_BIN=()
  fi

  if [ "${#DC_BIN[@]}" -eq 0 ]; then
    echo "Docker Compose not found; cannot run docker compose down -v"
    exit 0
  fi

  # build same -f chain as init-rundev
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
    [ -f "$WIN_MON" ] && CMD+=( -f "$WIN_MON" )
  fi

  echo "Running: ${CMD[*]} down -v"
  "${CMD[@]}" down -v 2>&1 | grep -v "variable is not set"
  echo "Docker compose down -v completed."
else
  if [ "$any_running" = false ]; then
    echo "All per-service processes appear stopped."
  else
    echo "Some per-service processes still running after kill attempts."
    echo "Run the script again or inspect processes manually (ps aux | grep <svcdir>)"
  fi
fi

echo "Done."
exit 0

#!/usr/bin/env bash
set -euo pipefail

# scripts/init-rundev.sh
# - sources generate-secrets.sh (so secrets are exported into this shell/session)
# - validates python/node versions
# - assembles docker-compose -f chain (uses windows monitoring file on non-Linux)
# - starts docker compose up -d --build
# - starts services: frontend -> npm, backend -> per-service venv + uvicorn
# - allocates uvicorn ports starting from 9900, skipping used ports

# ---------- 0. Setup ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ensure generate-secrets exists
if [ ! -f "$SCRIPT_DIR/generate-secrets.sh" ]; then
  echo "❌ generate-secrets.sh not found at $SCRIPT_DIR"
  exit 1
fi

# ensure export-urls.sh exists
if [ ! -f "$SCRIPT_DIR/export-urls.sh" ]; then
  echo "❌ export-urls.sh not found at $SCRIPT_DIR"
  exit 1
fi

# source to export vars into this shell
# generate-secrets.sh will return (not exit) when sourced
source "$SCRIPT_DIR/generate-secrets.sh"
source "$SCRIPT_DIR/export-urls.sh" dev
echo "✅ Secrets and URLs exported."

# ---------- 1. Check Python version ----------
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ not found."
    exit 1
fi

PYTHON_VER=$(python3 -c 'import sys; print("{}.{}.{}".format(*sys.version_info[:3]))')
PY_MAJOR=$(echo "$PYTHON_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PYTHON_VER" | cut -d. -f2)
PY_PATCH=$(echo "$PYTHON_VER" | cut -d. -f3)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
    echo "❌ Python 3.11.0+ required. Found $PYTHON_VER"
    exit 1
fi

# Check for venv support
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "❌ python3-venv is not installed."
    echo "👉 Run: sudo apt install python3-venv"
    exit 1
fi

# Check for pip
if ! python3 -m pip --version > /dev/null 2>&1; then
    echo "❌ pip is not installed."
    echo "👉 Run: sudo apt install python3-pip"
    exit 1
fi

echo "✅ Python $PYTHON_VER"

# ---------- 2. Check Node version ----------
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found."
    exit 1
fi
NODE_VER=$(node -v | sed 's/^v//')
NODE_MAJOR=$(echo "$NODE_VER" | cut -d. -f1)
if [ "$NODE_MAJOR" -lt 22 ]; then
    echo "❌ Node.js 22+ required. Found v$NODE_VER"
    exit 1
fi
echo "✅ Node.js v$NODE_VER"

# ---------- 3. Build docker compose -f chain ----------
# prefer `docker compose` (v2), fallback to `docker-compose` if needed
if docker compose version > /dev/null 2>&1; then
    DC_BIN=(docker compose)
elif docker-compose version > /dev/null 2>&1; then
    DC_BIN=(docker-compose)
else
    echo "❌ Docker Compose not found."
    exit 1
fi

CMD=("${DC_BIN[@]}")

if [ -f "$REPO_ROOT/docker-compose.yml" ]; then
    CMD+=( -f "$REPO_ROOT/docker-compose.yml" )
fi

PLATFORM="$(uname -s)"

# Add infrastructure compose files deterministically (sorted)
if [ -d "$REPO_ROOT/infrastructure" ]; then
  # find and sort so order is predictable
  while IFS= read -r -d '' file; do
    fname="$(basename "$file")"
    # On non-Linux (Windows/macOS) skip linux monitoring base (we will add windows file instead)
    if [ "$PLATFORM" != "Linux" ] && [ "$fname" = "docker-compose.monitoring.yml" ]; then
      # skip base monitoring on non-Linux
      continue
    fi
    CMD+=( -f "$file" )
  done < <(find "$REPO_ROOT/infrastructure" -type f -iname 'docker-compose*.yml' -print0 | sort -z)
fi

# On non-Linux, include the Windows monitoring compose if present (standalone complete file)
if [ "$PLATFORM" != "Linux" ]; then
  WIN_MON="$REPO_ROOT/infrastructure/docker-compose-dev/docker-compose.monitoring.windows.yml"
  if [ -f "$WIN_MON" ]; then
    CMD+=( -f "$WIN_MON" )
    echo "Using Windows monitoring compose: $WIN_MON"
  else
    echo "⚠️  Running on non-Linux but $WIN_MON not found; proceeding with available infra files."
  fi
fi

# ---------- 4. Pre-flight: show and run compose ----------
echo "Running: ${CMD[*]} up -d"
"${CMD[@]}" up -d
echo "✅ Docker stack running."

# ---------- helper: check port availability ----------
is_port_free() {
  local port="$1"
  # prefer ss then lsof then netstat
  if command -v ss >/dev/null 2>&1; then
    # ss output has address:port - match trailing :port or ]:port for IPv6
    if ss -ltn 2>/dev/null | awk '{print $4}' | grep -E "[:[]${port}$" >/dev/null 2>&1; then
      return 1
    else
      return 0
    fi
  elif command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
      return 1
    else
      return 0
    fi
  else
    if netstat -tln 2>/dev/null | awk '{print $4}' | grep -E "[:[]${port}$" >/dev/null 2>&1; then
      return 1
    else
      return 0
    fi
  fi
}

# ---------- 5. Start services ----------
cd "$REPO_ROOT/services" || { echo "services dir not found"; exit 1; }

SKIP_LIST=(frontend-notice data-veda)
PORT_START=9900
NEXT_PORT=$PORT_START

for svc in */; do
  name="${svc%/}"
  lname="$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]')"

  # skip known names
  skip=false
  for s in "${SKIP_LIST[@]}"; do
    if [ "$lname" = "$s" ]; then skip=true; break; fi
  done
  if $skip; then
    echo "Skipping $name (skip list)"
    continue
  fi

  svcdir="$REPO_ROOT/services/$name"
  log="$svcdir/service.log"
  pidfile="$svcdir/service.pid"
  portfile="$svcdir/.port"

  printf "==== Starting %s - %s ====\n" "$name" "$(date)" >> "$log"

  # frontend detection
  if printf '%s\n' "$lname" | grep -qi 'frontend'; then
    echo "[$name] frontend: npm install + npm run dev" >> "$log"
    (cd "$svcdir" && npm install >> "$log" 2>&1)
    (cd "$svcdir" && nohup npm run dev >> "$log" 2>&1 & echo $! > "$pidfile")
    continue
  fi

  # skip specific substrings that you mentioned earlier
  if printf '%s\n' "$lname" | grep -qi 'data-veda\|frontend-notice'; then
    echo "[$name] Skipping special-case startup." >> "$log"
    continue
  fi

  # --- backend: venv + install + uvicorn on next free port ---
  reqfile="$svcdir/requirements.txt"
  venv_dir="$svcdir/.venv"
  venv_py="$venv_dir/bin/python3"

  if [ ! -x "$venv_py" ]; then
    python3 -m venv "$venv_dir" >> "$log" 2>&1 || { echo "venv creation failed for $name (see $log)"; continue; }
  fi

  if [ -f "$reqfile" ]; then
    "$venv_py" -m pip install --upgrade pip >> "$log" 2>&1 || true
    "$venv_py" -m pip install -r "$reqfile" >> "$log" 2>&1 || true
  fi

  # find next free port
  port=$NEXT_PORT
  while ! is_port_free "$port"; do
    port=$((port + 1))
    # optional safety: stop if port grows too large (e.g., > 9999)
    if [ "$port" -gt 65535 ]; then
      echo "❌ No free ports found (reached 65535)" | tee -a "$log"
      break
    fi
  done
  NEXT_PORT=$((port + 1))

  echo "[$name] Starting uvicorn on port $port" | tee -a "$log"
  (cd "$svcdir" && nohup "$venv_py" -m uvicorn app.main:app --host 0.0.0.0 --port "$port" --reload >> "$log" 2>&1 & echo $! > "$pidfile")
  printf "%s\n" "$port" > "$portfile"

done

echo "✅ All services started."

read -p "Do you want to display the environment variables? (y/n): " show_env
if [[ "$show_env" =~ ^[Yy]$ ]]; then
  echo "Environment variables:"
  printenv
fi

exit 0

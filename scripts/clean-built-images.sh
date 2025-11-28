#!/usr/bin/env bash
set -euo pipefail

# scripts/clean-built-images.sh
# Removes images that were built by docker-compose for THIS repository only.
# Usage:
#   ./scripts/clean-built-images.sh         # list candidate images (no deletion)
#   ./scripts/clean-built-images.sh --yes   # actually delete them

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJ_NAME="$(basename "$REPO_ROOT")"

# parse args
DOIT=false
for a in "$@"; do
  case "$a" in
    --yes|-y) DOIT=true ;;
    *) echo "Unknown arg: $a"; echo "Usage: $0 [--yes]"; exit 1 ;;
  esac
done

# confirm docker is present
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ docker CLI not found in PATH."
  exit 1
fi

# Helper: list images by label filter (returns lines: <repository>:<tag> <imageID>)
_list_by_label() {
  local label="$1"
  docker image ls --filter "label=${label}" --format '{{.Repository}}:{{.Tag}} {{.ID}}' 2>/dev/null || true
}

echo "Searching for images built by docker-compose for this repo..."
# 1) images labeled with working_dir === REPO_ROOT
label1="com.docker.compose.project.working_dir=${REPO_ROOT}"
mapfile -t imgs1 < <(_list_by_label "$label1")

# 2) images labeled with project name (fallback)
label2="com.docker.compose.project=${PROJ_NAME}"
mapfile -t imgs2 < <(_list_by_label "$label2")

# combine unique image IDs (and keep their repo:tag display)
declare -A byid

for line in "${imgs1[@]}"; do
  repo_tag="${line%% *}"
  id="${line##* }"
  byid["$id"]="$repo_tag"
done
for line in "${imgs2[@]}"; do
  repo_tag="${line%% *}"
  id="${line##* }"
  byid["$id"]="$repo_tag"
done

# If nothing found, exit
if [ "${#byid[@]}" -eq 0 ]; then
  echo "✅ No compose-built images found for this repository (labels: ${label1} / ${label2})."
  exit 0
fi

echo
echo "Found the following compose-built images for this repo (will delete only these):"
printf "%-20s %-20s\n" "IMAGE (repo:tag)" "IMAGE ID"
echo "-----------------------------------------------------------"
for id in "${!byid[@]}"; do
  printf "%-20s %-20s\n" "${byid[$id]}" "$id"
done

echo
if [ "$DOIT" != true ]; then
  echo "No images were deleted. To delete these images, re-run with --yes."
  exit 0
fi

# Delete by image ID (force remove to ensure removal even if containers reference them)
echo "Deleting ${#byid[@]} image(s)..."
ids_to_remove=()
for id in "${!byid[@]}"; do
  ids_to_remove+=("$id")
done

# Attempt removal
docker rmi -f "${ids_to_remove[@]}" || {
  echo "⚠️  Some images could not be removed; inspect docker image ls and try manual cleanup."
  exit 1
}

echo "✅ Removed ${#ids_to_remove[@]} image(s)."
exit 0

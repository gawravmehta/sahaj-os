#!/usr/bin/env bash
set -euo pipefail

# scripts/clean-built-images.sh
# Cleans docker images built from service docker-compose.yml files.
# Usage:
#   ./scripts/clean-built-images.sh         # Dry-run
#   ./scripts/clean-built-images.sh --yes   # Actually delete them

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_DIR="$REPO_ROOT/services"
DOIT=false

for a in "$@"; do
  case "$a" in
    --yes|-y) DOIT=true ;;
    *) echo "Unknown arg: $a"; echo "Usage: $0 [--yes]"; exit 1 ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ docker CLI not found."
  exit 1
fi

# Step 1: Collect base image names from docker-compose.yml
IMAGE_BASE_NAMES=()

while IFS= read -r -d '' yml_file; do
  while IFS= read -r image_line; do
    image_full=$(echo "$image_line" | awk '{print $2}')
    image_base="${image_full%%:*}"
    IMAGE_BASE_NAMES+=("$image_base")
  done < <(grep -hoE 'image:\s*[a-zA-Z0-9._/-]+(:[a-zA-Z0-9._-]+)?' "$yml_file")
done < <(find "$SERVICE_DIR" -name 'docker-compose.yml' -print0)

# Deduplicate base names
UNIQ_BASE_NAMES=($(printf "%s\n" "${IMAGE_BASE_NAMES[@]}" | sort -u))

# Step 2: Match existing docker images against base names
IMAGES_TO_REMOVE=()
IMAGE_MAP=()  # For display: [ "repo:tag imageID" ]

for base in "${UNIQ_BASE_NAMES[@]}"; do
  while IFS= read -r line; do
    img_id="${line##* }"
    repo_tag="${line%% *}"
    IMAGES_TO_REMOVE+=("$img_id")
    IMAGE_MAP+=("$repo_tag $img_id")
  done < <(docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep "^${base}:" || true)
done

# Step 3: Report or remove
if [ "${#IMAGES_TO_REMOVE[@]}" -eq 0 ]; then
  echo "✅ No matching images found in services/*/docker-compose.yml"
  exit 0
fi

echo "Found the following images to delete:"
printf "%-40s %-20s\n" "IMAGE (repo:tag)" "IMAGE ID"
echo "-------------------------------------------------------------"
for entry in "${IMAGE_MAP[@]}"; do
  printf "%-40s %-20s\n" "${entry%% *}" "${entry##* }"
done

if [ "$DOIT" != true ]; then
  echo
  echo "ℹ️  This is a dry run. Run with --yes to actually delete these images."
  exit 0
fi

# Delete images by ID
echo
echo "Deleting ${#IMAGES_TO_REMOVE[@]} image(s)..."
docker rmi -f "${IMAGES_TO_REMOVE[@]}" || {
  echo "⚠️  Some images may not have been removed successfully."
  exit 1
}

echo "✅ Removed ${#IMAGES_TO_REMOVE[@]} image(s)."
exit 0

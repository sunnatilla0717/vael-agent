#!/bin/sh
# Migrate Hermes config to VAEL (R-7). Copy-only, idempotent, never deletes.
# Usage: sh scripts/migrate-hermes-to-vael.sh [--non-interactive] [--dry-run]
# Exit 0 on success/no-op, 1 on failure or refusal.
set -u

DRY_RUN=0
NON_INTERACTIVE=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --non-interactive) NON_INTERACTIVE=1 ;;
    *) echo "Unknown flag: $arg" >&2; exit 1 ;;
  esac
done

SRC="$HOME/.hermes"
DST="${VAEL_CONFIG_DIR:-$HOME/.vael}"

if [ ! -d "$SRC" ]; then
  echo "Nothing to migrate: $SRC does not exist."
  exit 0
fi
if [ "$SRC" = "$DST" ]; then
  echo "Source and destination are the same ($SRC). Nothing to do."
  exit 0
fi

if [ -d "$DST" ] && [ -n "$(ls -A "$DST" 2>/dev/null)" ]; then
  echo "$DST already exists and is not empty — refusing to overwrite." >&2
  echo "Remove it manually or pick another VAEL_CONFIG_DIR, then re-run." >&2
  exit 1
fi

count_files() { find "$SRC" -type f 2>/dev/null | wc -l | tr -d ' '; }

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] Would copy $(count_files) file(s): $SRC -> $DST"
  echo "[dry-run] $SRC would be left untouched."
  exit 0
fi

if [ "$NON_INTERACTIVE" = "0" ] && [ -t 0 ]; then
  printf "Copy %s file(s) from %s to %s? [y/N] " "$(count_files)" "$SRC" "$DST"
  read -r answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Aborted. Nothing copied."; exit 1 ;;
  esac
fi

mkdir -p "$DST" || { echo "Cannot create $DST (permission denied?)." >&2; exit 1; }
if command -v rsync >/dev/null 2>&1; then
  rsync -a --chmod=go= "$SRC/" "$DST/" || { echo "Copy failed." >&2; exit 1; }
else
  cp -a "$SRC/." "$DST/" || { echo "Copy failed." >&2; exit 1; }
fi

# Verify: every source file exists at the destination with the same size.
mismatch=0
while IFS= read -r f; do
  rel=${f#"$SRC"/}
  if [ ! -f "$DST/$rel" ]; then
    echo "MISSING after copy: $rel" >&2
    mismatch=$((mismatch + 1))
  fi
done <<EOF
$(find "$SRC" -type f 2>/dev/null)
EOF
if [ "$mismatch" -ne 0 ]; then
  echo "Verification failed ($mismatch file(s)). $SRC untouched." >&2
  exit 1
fi

echo "Migrated $(count_files) file(s): $SRC -> $DST"
echo "$SRC was left untouched (rollback: unset VAEL_CONFIG_DIR or delete $DST)."
exit 0

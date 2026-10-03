#!/bin/sh
# IR2-B rollback: reverse every RENAME entry in docs/ir2-mapping/rename-map.tsv.
#
#   sh scripts/ir2-rollback.sh            # execute the rollback (git mv new -> old)
#   sh scripts/ir2-rollback.sh --dry-run  # print planned actions, change nothing
#
# Idempotent: entries already at old_path are skipped; a missing new_path
# warns and continues. Non-RENAME rows (KEEP / MANUAL-REVIEW) are ignored.
# Processes the map in REVERSE order so nested paths unwind safely.
# Do NOT run before IR2-B has renamed anything (it will harmlessly skip all).
set -u

MAP="docs/ir2-mapping/rename-map.tsv"

if [ ! -f "$MAP" ]; then
    echo "ir2-rollback: map not found: $MAP (run from the repo root)" >&2
    exit 1
fi

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=1
elif [ $# -gt 0 ]; then
    echo "usage: sh scripts/ir2-rollback.sh [--dry-run]" >&2
    exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "ir2-rollback: not inside a git work tree" >&2
    exit 1
}
cd "$ROOT" || exit 1

TAB="$(printf '\t')"
TMP_REV="${TMPDIR:-/tmp}/ir2-rollback.rev.$$"
trap 'rm -f "$TMP_REV"' EXIT INT TERM

# Reverse data rows (keep header out), preserving empty reason fields.
tail -n +2 "$MAP" > "$TMP_REV.raw"
# tac may not exist on macOS/BSD: reverse with awk instead.
awk '{ lines[NR] = $0 } END { for (i = NR; i >= 1; i--) print lines[i] }' \
    "$TMP_REV.raw" > "$TMP_REV"
rm -f "$TMP_REV.raw"

moved=0
skipped=0
warned=0
while IFS="$TAB" read -r old new action _reason; do
    [ "$action" = "RENAME" ] || continue
    [ -n "$old" ] && [ -n "$new" ] || {
        echo "WARN: malformed row (empty path), skipping" >&2
        warned=$((warned + 1))
        continue
    }
    if [ -e "$old" ] && [ ! -e "$new" ]; then
        echo "SKIP (already at old path): $old"
        skipped=$((skipped + 1))
        continue
    fi
    if [ ! -e "$new" ]; then
        echo "WARN (new path missing, nothing to move): $new <- $old" >&2
        warned=$((warned + 1))
        continue
    fi
    if [ "$DRY_RUN" = "1" ]; then
        echo "DRY-RUN: git mv \"$new\" \"$old\""
    else
        if git mv -- "$new" "$old"; then
            moved=$((moved + 1))
        else
            echo "WARN (git mv failed): $new -> $old" >&2
            warned=$((warned + 1))
        fi
    fi
done < "$TMP_REV"

echo "ir2-rollback done: moved=$moved skipped=$skipped warned=$warned dry_run=$DRY_RUN"

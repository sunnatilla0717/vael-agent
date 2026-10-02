# Migrating from Hermes to VAEL (R-7)

Existing Hermes installs keep working after upgrade — no action required.
Migration is opt-in and exists so new features can assume the VAEL layout.

## Why migrate

VAEL is the rebranded continuation of Hermes Agent (same core, same data
format). New installs use `~/.vael` (`%LOCALAPPDATA%/vael` on Windows) and
`VAEL_*` env vars. The old names keep working through a compatibility layer.

## What changes / what does NOT change

| Changes (opt-in) | Does NOT change |
| ---------------- | --------------- |
| Config dir `~/.hermes` → `~/.vael` (after you migrate) | Data format (MEMORY.md, sessions, skills — byte-identical) |
| Env vars `HERMES_*` → `VAEL_*` (old ones still read) | Core agent loop, memory, skill engine |
| Default for fresh installs | `LICENSE`, attribution, upstream mergeability |

## Config resolution (automatic, no action needed)

1. `VAEL_CONFIG_DIR` env var, if set.
2. `~/.vael` if it exists.
3. `~/.hermes` if it exists (one deprecation note in logs).
4. Otherwise `~/.vael` (created on first write).

Explicit `HERMES_HOME` keeps working exactly as before.

## Env vars

Rule: `VAEL_*` wins; `HERMES_*` works as fallback with a one-time log note
(`[VAEL] Using deprecated …`). Example:

```sh
# Old (still works, warns once):
export HERMES_MODEL="anthropic/claude-opus-4-20250514"
# New (preferred, no warning):
export VAEL_MODEL="anthropic/claude-opus-4-20250514"
```

Provider API keys (e.g. `ANTHROPIC_API_KEY`) are not `HERMES_*` names and are
untouched by this scheme.

## Step-by-step migration

Linux/macOS:

```sh
sh scripts/migrate-hermes-to-vael.sh --dry-run   # preview
sh scripts/migrate-hermes-to-vael.sh             # interactive confirm
```

Windows:

```powershell
powershell -File scripts\migrate-hermes-to-vael.ps1 -DryRun
powershell -File scripts\migrate-hermes-to-vael.ps1
```

Non-interactive (scripts/CI): add `--non-interactive` (sh) / `-NonInteractive`
(ps1). The script copies only, verifies file presence, never deletes
`~/.hermes`, and refuses to overwrite a non-empty `~/.vael`. Re-running is safe.

## Rollback

`~/.hermes` is never touched by migration. To roll back: unset
`VAEL_CONFIG_DIR` (or delete `~/.vael`) — the resolver falls back to
`~/.hermes` automatically.

## Deprecation timeline

- Now → +6 months: `HERMES_*` and `~/.hermes` fully supported (warnings only).
- After 6 months: warnings stay; removal (if ever) will be announced in
  release notes with a major-version bump. No silent breakage — same
  philosophy as K1–F8.

## Troubleshooting

- `config not found`: neither dir exists — run the agent once (it creates
  `~/.vael`), or set `VAEL_CONFIG_DIR`.
- `permission denied`: check ownership of `~/.hermes` (especially after
  `sudo` installs); migrate as the owning user.
- `already exists and is not empty`: back up or remove `~/.vael` first, or
  point `VAEL_CONFIG_DIR` elsewhere.

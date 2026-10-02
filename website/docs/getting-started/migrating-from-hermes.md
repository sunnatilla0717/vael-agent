---
title: "Migrating from Hermes to VAEL"
description: "Existing Hermes installs keep working after upgrade — migration to the VAEL config directory and VAEL_* env vars is opt-in, copy-only, and reversible"
sidebar_position: 8
---

# Migrating from Hermes to VAEL

VAEL is the rebranded continuation of Hermes Agent by Nous Research (same core,
same data format, MIT). **Existing installs keep working — no action is
required.** Migration is opt-in and only matters if you want new installs'
layout, or you are tidying up after the rename.

The authoritative copy of this guide lives in the repository at
`docs/migrating-from-hermes.md`, next to the migration scripts.

## What changes, what does not

| Changes (opt-in) | Does NOT change |
| --- | --- |
| Config dir `~/.hermes` → `~/.vael` (after you migrate) | Data format (`MEMORY.md`, sessions, skills — byte-identical) |
| Env vars `HERMES_*` → `VAEL_*` (the old names still work) | Core agent loop, memory, skill engine, security model |
| Default directory for fresh installs | `LICENSE`, attribution, upstream mergeability |

## Config resolution (automatic)

The resolver already prefers the new layout and falls back to the old one, so
there is nothing to configure:

1. `VAEL_CONFIG_DIR`, if set.
2. `~/.vael`, if it exists.
3. `~/.hermes`, if it exists (logs one deprecation note).
4. Otherwise `~/.vael`, created on first write.

An explicit `HERMES_HOME` keeps working exactly as before.

## Run the migration

Linux / macOS:

```sh
sh scripts/migrate-hermes-to-vael.sh --dry-run   # preview
sh scripts/migrate-hermes-to-vael.sh             # interactive confirm
```

Windows:

```powershell
powershell -File scripts\migrate-hermes-to-vael.ps1 -DryRun
powershell -File scripts\migrate-hermes-to-vael.ps1
```

Add `--non-interactive` (sh) or `-NonInteractive` (ps1) for scripts and CI.
The script **copies only**: it verifies file presence, never deletes
`~/.hermes`, and refuses to overwrite a non-empty `~/.vael`. Re-running is safe.

## Env vars

`VAEL_*` wins; `HERMES_*` keeps working as a fallback with a one-time
`[VAEL] Using deprecated …` log note.

```sh
export HERMES_MODEL="anthropic/claude-opus-4-20250514"   # still works, warns once
export VAEL_MODEL="anthropic/claude-opus-4-20250514"     # preferred
```

Provider API keys (`ANTHROPIC_API_KEY`, …) are not `HERMES_*` names and are
untouched by this scheme.

## Rollback

`~/.hermes` is never modified. Unset `VAEL_CONFIG_DIR` (or delete `~/.vael`)
and the resolver falls back to `~/.hermes` automatically.

## Deprecation timeline

- Now → +6 months: `HERMES_*` and `~/.hermes` fully supported (warnings only).
- After that: warnings stay; any removal would be announced in release notes
  with a major-version bump. No silent breakage.

## Troubleshooting

- `config not found` — neither directory exists; run the agent once (it creates
  `~/.vael`) or set `VAEL_CONFIG_DIR`.
- `permission denied` — check ownership of `~/.hermes` (common after a `sudo`
  install); migrate as the owning user.
- `already exists and is not empty` — back up or remove `~/.vael` first, or
  point `VAEL_CONFIG_DIR` elsewhere.

## See also

- [Updating VAEL](./updating.md) — release/update mechanics, unrelated to the
  directory rename.
- [Import from other agents](../user-guide/import-from-other-agents.md) —
  moving in from Claude Code, OpenClaw, and similar tools.

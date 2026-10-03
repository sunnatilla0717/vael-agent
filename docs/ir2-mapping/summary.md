# IR2-A classification summary: hermes_* → vael_* rename map

Branch: `feat/vael-ir2-a-mapping`, base `main @ 10c6188d`. ANALYSIS ONLY —
no source file was changed, moved, or edited in this phase.

Artifacts: `files.txt`, `files-by-dir.md`, `imports.txt`,
`imports-detailed.md`, `config-refs.md`, `rename-map.tsv`, `import-map.tsv`,
`ts-imports.txt`, `summary.md` (this file). Rollback: `scripts/ir2-rollback.sh`.

## Counts

| Item | N |
| --- | --- |
| Files matching `hermes` (case-insensitive) in `git ls-files` | 2802 |
| `rename-map.tsv` rows (= files, 100%) | 2802 |
| — action RENAME | 2697 |
| — action KEEP | 104 (28 contributor emails + 66 catalog + 9 vendored + 1 migration script) |
| — action MANUAL-REVIEW | 1 (`hey_hermes.tflite`; product decision pending) |
| Raw Python import hits (`git grep 'from hermes_\|import hermes_'`) | 16702 |
| `import-map.tsv` rows | 17451 |
| — origin py-import (real AST import statements) | 16249 |
| — origin py-dynamic (`import_module`/`find_spec`/`__import__` strings) | 34 |
| — origin ts-import (TS/JS module specifiers) | 1168 |
| Config-file hermes mentions (`config-refs.md`) | 1279 |

Checks: zero duplicate `new_path`s, zero `new_path` collisions with tracked
files, zero case-only renames (Windows-safe), zero RENAME rows with residual
`hermes`, every row has a non-empty reason.

## KEEP (104) — do_not_rename_allowlist + owner decisions 2026-10-04

- `contributors/emails/*` (28): historical contributor records.
- `plugin-catalog/*.yaml` (66): third-party catalog IDs are install keys;
  renaming breaks existing user installs (owner decision).
- `plugins/hermes-achievements/**` (9): vendored third-party
  (PCinkusz/hermes-achievements); keep wrapped (owner decision).
- `openclaw_to_hermes.py` (1): filename states historical migration
  direction (owner decision).
Content-allowlist items that are not filenames (LICENSE/NOTICE text,
upstream remote, `Hermes 4` model name) need no map rows. The two
`migrating-from-hermes.md` allowlist paths do not exist on `main`.

## MANUAL-REVIEW (1)

- `tools/wakewords/hey_hermes.tflite`: wake-word model binary; loader paths
  plus the `hey hermes` utterance are user-facing; needs a product decision
  (keep the utterance vs ship a new wake word + model).

## Import contexts (from imports-detailed.md)

`py-module-level` 4140 + `py-function-level` 12060 + `py-conditional` 35 +
`py-type-checking` 13 + `py-class-level` 1 = 16249 mechanical rewrites
(replace the module token, keep aliases/rest of line).
`py-string-or-comment` 376 + non-Python hits 77 (docs 28, ts 17, ci 17,
shell 6, nix 4, misc 5) = content decisions, no import rewrite.
`py-unparseable` 0. No `from . import hermes_*` relative imports exist.

## Risks for IR2-B

1. TS alias renames (`@/hermes`→`@/vael`, `@hermes/shared`, `@hermes/ink`)
   require tsconfig paths + vite alias + package.json `name` updates plus
   `package-lock.json` churn; verify with `tsc` + `npm run build` per area.
2. Built bundles (`plugins/hermes-achievements/dashboard/dist/*`,
   `ui-tui/**/dist`) may need rebuilds, not just `git mv`.
3. Docusaurus route renames need `redirects` entries (patterns already in
   `docusaurus.config.ts` for guides; extend per renamed route).
4. The 34 dynamic string imports fail only at runtime — IR2-B must
   runtime-verify (import + smoke), grep is not enough.
5. Service/unit names (`main-hermes` s6 tree, `hermes-kanban-dispatcher`,
   nix desktop icon paths, `hermes-setup.manifest` via `include_str!`)
   have installer/updater references (`config-refs.md`).
6. Tests pinning old paths/IDs (update-zip preserve lists, product-builder
   fixtures, desktop connection-registry plugin IDs like `'hermes-bots'`).
7. Symbol ripples beyond file renames (`HermesSkin`, `useHermesConfig`,
   `HermesConsoleModal` component) — content pass after the moves.
8. `hermes` root launcher + `setup-hermes.*` + `scripts/hermes-gateway` are
   referenced by docs/CI/installers (`config-refs.md`); update callers in
   the same commit as each move.

## Estimated IR2-B commit grouping (10–20 files each for tests, bigger for moves)

| # | Group | Files | Verify |
| --- | --- | --- | --- |
| 1 | Root modules (`hermes_*.py`, launcher, setup-*) | ~40 | import smoke + `test_hermes_constants`-class suites |
| 2 | `hermes_cli/` core (top files, no subdirs) | ~120 | parser/help smoke |
| 3–5 | `hermes_cli/subcommands|observability|web_routers` | ~120 | CLI suite slice |
| 6 | `hermes_cli/` remainder | ~150 | CLI suite slice |
| 7 | `hermes_platform/` + `tests/hermes_platform/` | ~20 | platform tests |
| 8 | `tests/hermes_state/` | 146 | state suite |
| 9–12 | `tests/hermes_cli/` in 4 chunks | ~357 each | per-chunk run |
| 13 | `agent/transports`, `tools`, `web`, `nix`, `docker`, `scripts` | ~20 | targeted tests + shellcheck |
| 14 | `skills/` + website mirrors + regen + redirects | ~60 | generator idempotence + docs build |
| 15 | `apps/desktop` (code, assets, electron) | ~192 | `tsc` + vitest slice + build |
| 16 | `ui-tui` (+ `hermes-ink.d.ts`) | ~165 | `tsc` + build |
| 17 | dropped — `plugin-catalog` stays (owner decision 2026-10-04) | 0 | — |
| 18 | Leftovers + final full verification | — | `ty`, full pytest, site build |

Rough estimate: 15–18 commits over 2–4 sessions; verification (typecheck +
tests per commit) dominates. Roll back any red commit with
`sh scripts/ir2-rollback.sh` (reverses RENAME rows) or `git revert`.

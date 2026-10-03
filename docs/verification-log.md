# Verification log

## IR2-A baseline (2026-10-03, feat/vael-ir2-a-mapping, main @ 10c6188d)

- `git rev-parse HEAD` → `10c6188de188871f64a88dd95bc6b262adb0c307`
  (`catalog(hindsight): pin the released v1.2.1`).
- NOTE on `git pull`: `origin/main` (`4b7634b6 "Add files via upload"`) has an
  unrelated history (2 commits, no common ancestor with local main), so pull/
  merge is impossible without corrupting the branch. Baseline is local main —
  the base every rebrand branch forks from.
- `ruff check .` → All checks passed.
- `pytest tests/test_hermes_constants.py tests/cron/test_timezone.py` →
  1 failed, 57 passed, 4 skipped. The 1 failure
  (`TestSecureParentDir::test_install_tree_siblings_still_hardened`) is
  environmental: expects POSIX mode hardening on `D:\VAEL-Agent-data`, which
  Windows ACLs do not provide.
- Env: `.venv` Python 3.14.7 on Windows; no bash on PATH for child `.sh`;
  `aiohttp`/`acp` extras not installed; uv venv launcher double-PID quirk
  (documented in the website-rebrand branch log).

## IR2-A mapping evidence (2026-10-03)

- `git ls-files | grep -i hermes` → 2802 lines; `docs/ir2-mapping/files.txt`
  is byte-identical (Compare-Object clean). Case check: 2801 lowercase-only
  + exactly 1 capital-only (`web/src/components/HermesConsoleModal.tsx`).
- `git grep -n 'from hermes_\|import hermes_'` → 16702 lines;
  `docs/ir2-mapping/imports.txt` byte-identical (UTF-8 both sides; PowerShell
  `Get-Content`/`Out-File` were avoided after they caused wrapping/BOM/ANSI
  corruption — .NET UTF8-NoBOM I/O used instead).
- `rename-map.tsv`: 2802 rows = RENAME 2697 / KEEP 28 / MANUAL-REVIEW 77.
  Zero duplicate new_paths, zero clashes with tracked files, zero case-only
  renames, zero RENAME rows with residual `hermes`, every row has a reason.
- `import-map.tsv`: 17451 rows (py-import 16249, py-dynamic 34, ts-import
  1168). Zero py rows with residual `hermes` in new_module.
- `scripts/ir2-rollback.sh`: `sh -n` clean; `--dry-run` on the pristine tree
  → moved=0 skipped=2697 warned=0; sandbox end-to-end (rename 2 files →
  rollback moved=2, tree identical to HEAD → rerun moved=0 skipped=2).
- `config-refs.md`: 1279 rows (path-or-package 562, env-var 351, other 356,
  module-ref 8).
- Full detail: `docs/ir2-mapping/summary.md`.

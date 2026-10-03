# Open items

## IR2-A MANUAL-REVIEW decisions (owner, 2026-10-04) — applied to rename-map.tsv

- [x] `plugin-catalog/*.yaml` (66) → KEEP: third-party IDs are install keys.
- [x] `plugins/hermes-achievements/**` (9) → KEEP: keep vendored copy wrapped.
- [x] `openclaw_to_hermes.py` → KEEP: historical migration direction.
- [ ] `tools/wakewords/hey_hermes.tflite` → still MANUAL-REVIEW: product
  decision pending (keep `hey hermes` vs new wake word + model).
- [ ] TS alias renames (`@/hermes`, `@hermes/shared`, `@hermes/ink`) need
  tsconfig/vite/package.json updates + lockfile churn — verify with `tsc`.
- [ ] Symbol ripples (`HermesSkin`, `useHermesConfig`, `HermesConsoleModal`)
  need a content pass after the file moves.
- [ ] If IR2-B runs on the rebrand branch instead of main: the two
  `migrating-from-hermes.md` allowlist paths are KEEP there.

## origin/main vs local main (investigated 2026-10-04, decision pending)

`origin/main` (`4b7634b6`, 92 files, uploaded 2026-10-03 02:25) is an early
partial rebrand snapshot: 86 files byte-identical to local main, 2 identical
to the rebrand branch, 4 intermediate files fully superseded by the branch
(cli.py: 6 import lines only; hermes_constants.py: same 96-function R-7
design under the old filename; README/REBRANDING.md: older strings).
Zero unique work missing locally. Recommended: tag-backup
`4b7634b6`, then force-push local main (Option A) — needs explicit owner
confirmation; NEVER force-push without it. Until then, PRs against
origin/main show the whole history as new, and CI base-scope is wrong.

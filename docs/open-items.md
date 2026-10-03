# Open items

## IR2-A MANUAL-REVIEW → IR2-B decisions (from docs/ir2-mapping/rename-map.tsv)

- [ ] `plugin-catalog/*.yaml` (66 files): third-party catalog entries; filename
  stem is the catalog ID. Decide KEEP vs rename per entry. Embedded upstream
  names (`githermes`, `tamahermes`, `local-system-one-hermes`,
  `yantrikdb-hermes-dashboard`) must never be rewritten.
- [ ] `plugins/hermes-achievements/**` (10 files): vendored third-party plugin
  (PCinkusz/hermes-achievements). Decide vendor-rename vs keep-wrapped.
- [ ] `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`:
  filename states migration direction; decide whether the target is now VAEL.
- [ ] `tools/wakewords/hey_hermes.tflite`: wake-word binary + `hey hermes`
  utterance; needs a product decision.
- [ ] TS alias renames (`@/hermes`, `@hermes/shared`, `@hermes/ink`) need
  tsconfig/vite/package.json updates + lockfile churn — verify with `tsc`.
- [ ] Symbol ripples (`HermesSkin`, `useHermesConfig`, `HermesConsoleModal`)
  need a content pass after the file moves.
- [ ] If IR2-B runs on the rebrand branch instead of main: the two
  `migrating-from-hermes.md` allowlist paths are KEEP there.

# REBRANDING.md

Pointer file on the IR2-A mapping branch. The full rebrand plan lives on
`feat/vael-website-rebrand` (REBRANDING.md there).

## IR2 file/import rename — mapping phase (IR2-A)

Full inventory, rename map, import map and rollback script:
[`docs/ir2-mapping/`](ir2-mapping/summary.md). No source file was changed in
this phase. IR2-B (mechanical rename, 10–20 files per commit) consumes
`rename-map.tsv` + `import-map.tsv`; disagreements go to `open-items.md`
(MANUAL-REVIEW list). Roll back any red IR2-B commit with
`sh scripts/ir2-rollback.sh`.

What stays `hermes` (carried over from the rebrand intent): LICENSE/NOTICE
text, upstream remote and URLs, `HERMES_*` env vars and `~/.hermes` call
sites (R-7 mirror), `Hermes 4` model names, wire/protocol contracts,
`contributors/emails/*` records.

# Verification Log

Append-only record of what each rebrand phase actually changed, what was
verified, and what was deliberately left behind. Numbers come from the
commands quoted next to them, run at the commit named in each section.

## W — website / marketing docs rebrand (Hermes → VAEL)

Scope: `website/` only (Docusaurus docs site + marketing pages + assets).
Core agent code, config and skills untouched. `LICENSE` untouched.

### W-1 Inventory

| Item | Value |
| --- | --- |
| Framework | Docusaurus 3.10.2 (`website/package.json`), `baseUrl: /docs/` |
| Hand-authored EN docs | 452 `.md`/`.mdx` files under `website/docs/` |
| Hand-authored pages scanned by the migration | 403 (EN + zh-Hans), i.e. 452 EN docs minus the 211 generated skill pages and the 2 generated catalogs, plus the zh-Hans mirror set |
| zh-Hans mirror | 293 files under `website/i18n/zh-Hans/` |
| Files containing `hermes` (case-insensitive) before | 769 |
| Whole-word `Hermes` before | 7,100 |
| Lowercase `hermes` (commands, paths, env vars) before | ~12,600 (unchanged by design) |

Command:

```sh
rg -il 'hermes' website --glob '!node_modules' --glob '!build' | wc -l   # 769
rg -o '\bHermes\b' website --glob '!node_modules' --glob '!build' --glob '!package-lock.json' | wc -l   # 7100
```

### W-2/W-3 Content + assets

- `website/scripts/rebrand-hermes-to-vael.py` (new, stdlib-only, dry-run by
  default, idempotent) rewrote prose only: 391 files, 5,608 replacements, then
  10 more after the hyphenated-compound list was extended.
  It shields fenced code, inline code, link destinations, URLs, HTML attribute
  values and model-family names (`Hermes 4`, `Hermes-4-70B`), and skips
  attribution lines and generated pages.
- Core surfaces hand-edited: `docusaurus.config.ts` (title, navbar, OG image,
  footer attribution, favicon, redirects, comments), `sidebars.ts`, five
  `website/src/**` components/pages, `website/static/oauth/client-metadata.json`
  (`client_name`), `website/static/api/model-catalog.json` + its generator
  `scripts/build_model_catalog.py` (picker note text), four `_category_.json`
  descriptions.
- Theme: `website/src/css/custom.css` moved from gold-on-navy to the CyberAI
  palette (`#D97757` / `#CC785C`, warm charcoal `#191410`, paper `#FBF7F1`),
  light-mode primary darkened to `#B74C29` for 5.2:1 contrast on white, Google
  Fonts import dropped in favour of system stacks. See `design-system.md`.
- Assets: `website/scripts/generate-brand-assets.mjs` (new, Node stdlib only —
  `node:zlib` PNG encoder, no image dependency) generates `vael-mark.svg`,
  `vael-mark-dark.svg`, `favicon.svg`, `favicon-16x16.png`, `favicon-32x32.png`,
  `favicon.ico`, `apple-touch-icon.png` and the 1200x630
  `vael-agent-banner.png` OG card. All are placeholders in the brand palette,
  not designed artwork.
- Generators fixed: `generate-skill-docs.py` (4 user-facing strings) and
  `generate-llms-txt.py` (title, section label, guide labels, intro, install
  line). Also fixed a real portability bug in `generate-skill-docs.py`:
  `rel_path` used `str(Path)`, so a Windows checkout emitted `apple\notes`
  where CI expects `apple/notes`. Now `rel.as_posix()`.

### W-4 URLs / SEO

Six doc routes were renamed (EN + the four zh-Hans mirrors that exist):

| Old | New |
| --- | --- |
| `guides/manage-hermes-cloud-with-mcp` | `guides/manage-vael-cloud-with-mcp` |
| `guides/run-hermes-with-nous-portal` | `guides/run-vael-with-nous-portal` |
| `guides/secure-hermes-on-a-work-machine` | `guides/secure-vael-on-a-work-machine` |
| `guides/use-mcp-with-hermes` | `guides/use-mcp-with-vael` |
| `guides/use-soul-with-hermes` | `guides/use-soul-with-vael` |
| `guides/use-voice-mode-with-hermes` | `guides/use-voice-mode-with-vael` |

- All 38 referencing files (relative links, sidebar ids, `generate-llms-txt.py`
  lists) were repointed by `rebrand-hermes-to-vael.py --rewrite-guide-refs`;
  `rg <old-slug>` now matches only the redirect table and the migration script.
- Six entries added to `@docusaurus/plugin-client-redirects`. GitHub Pages
  cannot emit server-side 301s, so each old path serves a canonical redirect
  document (meta refresh + `rel=canonical`) — link equity survives.
- Heading anchors that the rebrand would have broken were pinned to their old
  ids: `{#connecting-hermes-desktop-to-a-remote-backend}` (web-dashboard),
  `{#web-dashboard--hermes-desktop}` (environment-variables),
  `{#hermes-home-and-profile-isolation}` (session-storage),
  `{#exporting-hermes-to-another-machine}` (faq),
  `{#running-hermes-as-an-mcp-server}` (mcp),
  `{#add-to-hermes-link}` (mcp-config-reference),
  `{#wsl2-bridge-hermes-in-wsl-to-windows-chrome}` (use-mcp-with-vael).
- `canonical`, `og:url` and the sitemap come from `url`/`baseUrl`, which are
  intentionally unchanged (see `open-items.md`).

### W-5 Documentation cross-link

- New page `website/docs/getting-started/migrating-from-hermes.md`, added to
  the Getting Started sidebar, mirroring `docs/migrating-from-hermes.md` in the
  repository.
- `docs/migrating-from-hermes.md` links back to the site page.

### W-6 Verification

```sh
python3 tests/branding/test_vael_brand.py                     # ALL GREEN (now includes website guards)
python3 -m pytest tests/branding tests/website -q             # 60 passed, 1 env-blocked (see below)
python3 website/scripts/check_doc_links.py                    # OK: no route-style links
cd website && npm run typecheck                                # clean
cd website && npm ci && npm run build                          # EN + zh-Hans [SUCCESS], exit 0
```

- Five new guard tests: `test_website_marketing_surface_says_vael`,
  `test_website_docs_prose_says_vael`, `test_website_generators_emit_vael`,
  `test_website_has_no_hermes_routes`, `test_website_brand_assets_exist`. They
  run in the existing `VAEL Brand Guards` workflow job (dependency-free), so a
  future Hermes leak in the site fails CI.
- Bilingual build results:
  - `en`: 3 broken anchors, all pre-existing and unchanged in `HEAD`
    (`installation#linux--macos--wsl2--android-termux`,
    `profiles#every-profile-owns-its-credentials`,
    `codex-app-server-runtime#named-custom-providers`). Every anchor the
    rebrand would have broken was pinned and now resolves.
  - `zh-Hans`: 84 broken anchors, all pre-existing translation drift (Chinese
    headings with links that still point at English ids). Exactly one of them
    was rebrand-caused — the Chinese heading `将 Hermes 作为 MCP 服务器运行`
    became `将 VAEL …` and lost its id — and it is fixed with an id pin
    `{#将-hermes-作为-mcp-服务器运行}`. The remaining hermes-flavoured zh
    warnings (`#a-note-on-hermes-4`,
    `#connecting-hermes-desktop-to-a-remote-backend`,
    `#web-dashboard--hermes-desktop`) have no matching heading in `HEAD`
    either. Tracked as P-5 in `open-items.md`.
  - 2 broken links (`/docs/llms.txt`, `/docs/llms-full.txt`) are a local-only
    artifact: those files are generated by `prebuild.mjs` via
    `generate-llms-txt.py`, which needs `python3` (absent on this Windows box).
    CI has it, so the links resolve there.
- Found by the test suite, not by grep: `website/docs/developer-guide/plugins/catalog-submission.md`
  mirrors the admission-rules block of `plugin-catalog/README.md` verbatim
  (`tests/website/test_catalog_rules_mirror.py`). The migration rewrote the docs
  copy, so the canonical `plugin-catalog/README.md` block was brought to the same
  wording (8 lines, docs only — no code, config or skill files). The mirror test
  passes again.
- `tests/website/test_extract_plugins.py::test_git_dates_added_is_first_commit_updated_is_last_and_renames_keep_added`
  cannot run in this shared checkout: `tests/conftest.py`'s live-system guard
  blocks the test's internal `git add .`. Environmental, unrelated to this PR,
  and green in CI.

### Honest residuals (W-6)

| Residual | Why it stays |
| --- | --- |
| ~995 whole-word `Hermes` in generated skill pages + catalogs (EN + zh) | Bodies come from upstream `SKILL.md` files. Touching skills is out of scope, and CI regenerates these pages from source. |
| `Author | Hermes Agent` rows | Skill authorship is a fact, not branding. |
| Code fences: `hermes chat`, `~/.hermes`, `HERMES_*`, `X-Hermes-Session-Id`, `Hermes-Setup.exe`, `Hermes-Monitor/1.0` | Command literals, paths, env vars and wire contracts deliberately kept stable (R-7). |
| `Hermes 4` / `Hermes-4-70B` | Nous Research model names. Renaming them would be a false claim. |
| `src/data/userStories.json` + collage quotes | Real community quotes with live source URLs; rewriting them would fabricate speech. The section is labelled as the upstream community. |
| Upstream URLs (site `url`, OAuth `client_uri`/`logo_uri`, `editUrl`, Algolia index name) | No VAEL-owned deployment exists yet; changing them would break links and search. Tracked in `open-items.md`. |
| `logo.png` / `logo-dark.png` / `hermes-agent-banner.png` | Upstream marketing assets kept on disk but no longer referenced by config. Delete with the next upstream sync review. |
| 12,625 lowercase `hermes` | CLI command, config dir and env-var contracts. |

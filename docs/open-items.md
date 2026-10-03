# Open Items — rebrand follow-ups

Items the rebrand deliberately did **not** close, with the reason and the next
step. Nothing here blocks the website rebrand PR; each needs a decision or an
asset/credential that the rebrand itself cannot produce.

## Website (W phase)

| # | Item | Why it is open | Next step |
| --- | --- | --- | --- |
| W-8 | Designed wordmark, favicons and OG image | Shipped marks are dependency-free placeholders drawn by `website/scripts/generate-brand-assets.mjs` (block-letter OG card, monogram favicon). | Commission/export real artwork, drop the PNGs into `website/static/img/`, keep the file names so nothing else changes. |
| W-9 | `logo.png` / `logo-dark.png` / `hermes-agent-banner.png` | Upstream mascot and Hermes wordmark. No longer referenced by `docusaurus.config.ts`, kept on disk so the upstream sync stays clean. | Delete after the next upstream merge review; they are unreferenced. |
| W-10 | Site `url` / `baseUrl` still `hermes-agent.nousresearch.com/docs/` | Canonical URLs, `og:url`, sitemap and the OAuth `client_id` are pinned to the deployment that exists today. | When a VAEL-owned domain exists: update `url`, `baseUrl`, `organizationName`/`projectName`, `static/oauth/client-metadata.json` (`client_id`, `client_uri`, `logo_uri`) and add redirects from the old origin. |
| W-11 | Algolia `indexName: 'hermes docs'` | The index is populated by the upstream crawler; renaming it would silently break search. | Create a VAEL DocSearch app, crawl the new domain, then swap `appId`/`apiKey`/`indexName`. |
| W-12 | `editUrl` points at `NousResearch/hermes-agent` | Keeps "Edit this page" working while VAEL has no public remote; also preserves the upstream merge path. | Point at the VAEL remote once it is public. |
| W-13 | Navbar "Download (upstream)" links to the upstream site | VAEL is not distributed separately; the installer in the repo is the upstream one. | Ship a VAEL download endpoint, then relabel/retarget. |
| W-14 | zh-Hans translations lag the rebrand | Translations live in `website/i18n/`; the migration rewrote brand strings in place, but new/changed copy (e.g. the migration page) falls back to English. | Normal translation pass (`npm run write-translations` + translator review). |

## Deliberately permanent (not defects)

- **CLI literals, paths, env vars** — `hermes chat`, `~/.hermes`, `HERMES_*`,
  `hermes_*.py`, service names. R-7 kept the call sites untouched so upstream
  merges stay cherry-pickable. `docs/migrating-from-hermes.md` documents the
  opt-in migration to `~/.vael` / `VAEL_*`.
- **Wire contracts** — `X-Hermes-Session-Id`, `X-Hermes-Session-Key`,
  `X-Hermes-Delivery`, `X-Hermes-Event`, `X-Hermes-Signature-256`,
  `Hermes-Monitor/1.0`, `Hermes-Agent/<version>`, `Hermes-Setup.exe`,
  `Hermes-Meeting-Pipeline-Policy`. Renaming these breaks installed clients
  and deployments.
- **Upstream attribution** — `LICENSE`, `NOTICE`, the single footer line in
  `docusaurus.config.ts`, and skill `Author` rows in generated docs.
- **Model names** — `Hermes 4` / `Hermes-4-70B` / `Hermes-4-405B` are Nous
  Research products; calling them anything else would be a false claim.
- **Community quotes** — `website/src/data/userStories.json` entries are real
  posts, quoted verbatim with their source links.

## Pre-existing issues found while rebranding (not introduced here)

| # | Item | Evidence | Next step |
| --- | --- | --- | --- |
| P-1 | Broken anchor `installation#linux--macos--wsl2--android-termux` | Heading is `#### Linux / macOS / WSL2` in both `HEAD` and the working tree; the link target never existed. | Fix the link or restore the heading text. |
| P-2 | Broken anchor `profiles#every-profile-owns-its-credentials` | No matching heading in `HEAD`. | Add the heading or repoint the link. |
| P-3 | Broken anchor `codex-app-server-runtime#named-custom-providers` | No matching heading in `HEAD`. | Same. |
| P-4 | `generate-skill-docs.py` emitted platform-specific path separators | Windows checkouts produced `apple\notes`, Linux CI produces `apple/notes`, so the "committed docs match the generator" check could pass locally and fail in CI. Fixed in this PR (`rel.as_posix()`). | Done. Watch the next Windows-authored regeneration. |
| P-5 | 84 broken anchors in the zh-Hans build | Chinese translations have Chinese heading ids while their links still point at English anchors (pre-existing translation drift; e.g. `#mention-control`, `#websocket-tuning`). One rebrand-caused instance was fixed with an id pin. | Run the zh translation refresh (`npm run write-translations` + translator pass) and fix links page by page. |
| P-6 | `docs/getting-started/migrating-from-hermes.md` has no zh-Hans translation | New page; Docusaurus falls back to English in the zh build. | Include it in the next translation batch (W-14). |

## IR-4..IR-8 / IR2 follow-ups (2026-10-03 session)

- [x] Model-facing rename done: CLI primary vael (+hermes alias notice), skill bodies (vael-*), tool descriptions, prompt identity, guards in CI.
- [ ] 'hermes cron ...' / 'hermes doctor' strings in cron + delivery notices: still the old binary name (work via alias). Mass user-copy rebrand needs a product decision.
- [ ] Non-vael-* skill prose with Hermes-isms ('Hermes-specific', 'Hermes-managed', 'Hermes-native', 'Hermes-compatible', 'official Hermes Docker layout', ~24 lines): third-party-flavored text; rename per-file with judgment, or leave.
- [ ] hermes_cli/ package directory rename: explicitly out of scope (2,244 import sites, zero model-facing gain).
- [ ] Dangling 'debugging-hermes-desktop' skill reference in inspecting-vael-desktop-dom/SKILL.md:42: pre-existing on main (no such skill in-tree); fix or drop.
- [ ] .pytest-tmp/ artifacts committed by the earlier sweep commit (relay-plugins.toml etc.): untracked-temp hygiene for a future cleanup commit; .pytest-tmp2/ variant avoided (temp moved outside repo).
- [ ] Windows-environmental test gaps on this box (NOT rebrand fallout, verified per-test): no bash on PATH for child .sh (monitor/no_agent/empty_payload/heredoc/missed_window/desktop_ticker), os.getuid/termios/pwd/SIGKILL POSIX-only collection errors, missing aiohttp/acp extras in .venv, uv-launcher PID mismatch breaking run_reported_turn booking (Popen pid != inner getpid; Linux CI runners with symlink venvs unaffected).


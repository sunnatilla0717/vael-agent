# VAEL Agent — Rebranding Plan (Hermes → VAEL, surface-only)

> Status: PR-1 + PR-2 + PR-3 + PR-RF + R-7 + IR-1..IR-8 + IR2 done (branch
> `feat/vael-website-rebrand`). Core logic untouched; model-facing content is
> now fully VAEL.
> - PR-1 (branch `feat/vael-pr1-foundation`, commit `7b890d00`): R-0 audit +
>   R-1..R-4 foundation.
> - PR-2 (branch `feat/vael-pr2-skills`, this change): skill rename.
> Baseline: `origin https://github.com/NousResearch/hermes-agent.git` (shallow, main).

## 1. Maqsad

Hermes Agent (Nous Research, MIT) ni **VAEL Agent** (CyberAI product family)
sifatida rebrand qilish — **faqat surface layer** (brending, adapter matnlari,
UI stringlar). Core agent loop, memory, skill engine, cua integratsiyasi
**tegilmaydi**. Upstream security patch lar uchun merge imkoniyati saqlanadi.

## 2. Audit xulosasi (R-0, 2026-10-02)

- `'hermes'` (case-insensitive): **135,059** moslik. To'liq rename real emas —
  fazali, surface-first yondashuv shart.
- Eng katta to'planish: `tests/` (50k), `website/` (22k), `apps/` (15k),
  `hermes_cli/` (13k), `locales/` (6.8k).
- Kalit nuqtalar (tekshirilgan):
  - Identity: `agent/prompt_builder.py:160` (`DEFAULT_AGENT_IDENTITY`),
    `agent/system_prompt.py`, `hermes_cli/default_soul.py:9`, `SOUL.md:1`.
  - Telegram: `plugins/platforms/telegram/adapter.py` (~7201 qator).
    Diqqat: `gateway/platforms/telegram.py` **mavjud emas** — platformalar
    `plugins/` ga ko'chgan.
  - CUA: `tools/computer_use/cua_*.py` (backend/driver/session). Diqqat:
    `HERMES_CUA_REMOTE_TOKEN` **0 ta** — bunday env yo'q. Remote tokenlar:
    `HERMES_DESKTOP_REMOTE_TOKEN`, `HERMES_DASHBOARD_SESSION_TOKEN`.
    `cua-driver` / `cua-host-bridge` alohida komponent sifatida **mavjud
    emas** — bridge **yangidan quriladi** (CyberAI tomonida).
  - Config: `~/.hermes` (`hermes_constants.py`), `%LOCALAPPDATA%\hermes`.
  - License: `LICENSE` = MIT, Copyright (c) 2025 Nous Research. `SECURITY.md` bor.
  - Testlar: `uv sync --locked` → `uv run pytest` (`-m 'not integration and not live'`);
    web: `web/` da vitest; npm workspaces (`apps/*`, `ui-tui`, `web`, `tests-js`).

## 3. Scope: nima o'zgaradi / nima qoladi

O'zgaradi (user-facing):

- `agent/prompt_builder.py` identity + `hermes_cli/default_soul.py` + `SOUL.md`
  (`You are Hermes Agent` → `You are VAEL`, + `part of CyberAI product family`).
- CLI launcher matnlari, `locales/*.yaml` (36+ til — faqat `en` to'liq, qolganiga
  fallback), `web/src/`, `apps/desktop` product identity
  (`product-identity.cjs`, window title), Telegram adapter matnlari,
  `website/docs` user sahifalari, `setup-hermes.{sh,ps1}` nomlari.
- `README.md` ga attribution qatori (LICENSE tegilmaydi).
- Yangi: `NOTICE`, `docs/vael-agent.md`, migratsiya scripti
  `scripts/migrate-hermes-to-vael.sh`, `~/.hermes` fallback.

O'zgarmaydi:

- `LICENSE` (Nous Research copyright — MIT talabi).
- Core: `agent/` loop, memory (`MEMORY.md`/`USER.md`/session DB), skill system,
  learning loop, `tools/computer_use/`, gateway arxitektura (portlar, API),
  approval logic, adapter base classlar.
- Ichki nomlar: `hermes_*.py`, o'zgaruvchilar, loglar, testlar, `nix/`,
  `docker/`, telemetriya kalitlari.
- CyberAI tomonidagi BYOK/M1/M2/Console — bu repo ga tegilmaydi.

## 4. R-5 tuzatish (spetsifikatsiyadagi xato)

Spetsifikatsiyada `cua-host-bridge` + `HERMES_CUA_REMOTE_TOKEN` bor deb
faraz qilingan — ikkalasi ham upstream da **yo'q**. To'g'ri reja:

- Bridge CyberAI tomonida yangi komponent (`vael-pc-bridge`): PC dagi agent
  **pull** qiladi (push qabul qilmaydi), whitelist action lar:
  `run-flow`, `status`, `list-flows`, `cancel-flow`.
- Auth: VAEL surface token (`vael1.*`, scope `cua:bridge`), 60s nonce.
- Destructive action lar: Telegram inline button bilan 2-step tasdiq.
- Hermes tomonda faqat Telegram `/start`/`/help` VAEL matnlari — bridge
  integratsiyasi CyberAI repo da yashaydi.

## 5. Upstream merge strategiyasi

- `origin` = NousResearch (o'zgarmaydi). Shallow clone → to'liq tarix kerak
  bo'lsa: `git fetch --unshallow origin`.
- Surface o'zgarishlar core dan ajratilgan fayllarda → security patch larni
  `git fetch origin && git cherry-pick <sha>` bilan olish, konflikt faqat
  surface fayllarda yechiladi.
- Har chorakda `git fetch origin main` + diff ko'rish eslatmasi.

## 6. Fazalar

- [x] PR-1 (R-1..R-4 foundation): LICENSE intact, README/NOTICE attribution,
  identity (`prompt_builder`, `SOUL.md`, `default_soul`), `locales/*.yaml` +
  `web/src/i18n/*` (`\bHermes\b` → `VAEL`), web title/header, desktop display
  names, Telegram `plugin.yaml`, CLI user strings, `tests/branding/` +
  `vael-brand.yml` CI. Ataylab qoldirildi:  `hermes` komanda literallari,
  `~/.hermes` path lar, `_LEGACY_TEMPLATE_SOULS`, kebab/pascal artifact
  nomlari, `website/` marketing docs (W fazasida bajarildi — pastga qarang).
- [x] PR-2 (skill rename): `hermes-agent` → `vael-agent` (essential skill,
  `ESSENTIAL_SKILLS`, prompt guidance, `X-Title: VAEL`),
  `hermes-agent-skill-authoring` → `vael-skill-authoring`,
  `inspecting-hermes-desktop-dom` → `inspecting-vael-desktop-dom`,
  `hermes-s6-container-supervision` → `vael-s6-container-supervision`;
  `related_skills` + website catalogs/sidebars/cross-links regenerated by hand
  (generator verified output format). Ataylab qoldirildi: service nomlari
  (`hermes-gateway`), path lar (`~/.hermes`), toolset patternlar,
  `source` taglar, CLI referrer/User-Agent lar, repo URL lar.
- [x] PR-3 (R-6): Claude-orange (`#D97757`/`#CC785C`) + CyberAI UI style —
  `vael` palette in the shared table (both surfaces follow), desktop
  `vaelTheme` + `DEFAULT_SKIN_NAME='vael'`, dashboard `defaultTheme` →
  shared projection, `docs/design-system.md`, brand-test snapshot.
  Upstream presets untouched. Full `vitest` not run locally (no
  node_modules in this clone) — CI lanes cover it.
- [x] R-7: `resolve_config_dir()` (`~/.vael` → `~/.hermes` fallback →
  `~/.vael` default) + generic `VAEL_*`→`HERMES_*` import-time mirror +
  `resolve_env()` + TS twins (`resolveConfigDir`, `mirrorVaelEnv` in
  `data-paths.mjs`) + `migrate-hermes-to-vael.{sh,ps1}` (copy-only,
  idempotent) + `docs/migrating-from-hermes.md`. Call-site rewiring
  ataylab yo'q (50+ var, minglab ishlatish — merge saqlanadi); `HERMES_HOME`
  explicit va barcha default matematika (`get_default_hermes_root`,
  suffix, sudo) o'zgarishsiz.
- [x] W (website rebrand, PR-4): Docusaurus saytning butun user-facing
  surface i — `title`/navbar/OG image/footer attribution, favicon + wordmark +
  1200x630 OG kartochka (`website/scripts/generate-brand-assets.mjs`, faqat
  Node stdlib), CyberAI palitrasi (`#D97757`/`#CC785C`, system font stack),
  docs prozasini kod bloklarini tegilmasdan qayta yozish
  (`website/scripts/rebrand-hermes-to-vael.py`, 391 fayl), generatorlar
  (`generate-skill-docs.py`, `generate-llms-txt.py`) + qayta generatsiya,
  6 ta guide route `hermes` → `vael` (+ client redirects, legacy anchor pin lar),
  `docs/getting-started/migrating-from-hermes.md` sahifasi va 5 ta yangi
  website guard testi. Batafsil: `docs/verification-log.md` (W bo'limi),
  qoldiqlar: `docs/open-items.md`.
- [x] R-5-bridge/R-8/R-9: bridge kontrakt (CyberAI repo), branding testlari,
  CI guardlar (PR-1 + W + IR-5/IR-6 da to'liq).

## IR-4 — CLI rename (done)

- Primary: `vael`. Backward-compat alias: `hermes` (same `hermes_cli.main:main`
  target in `pyproject.toml [project.scripts]`; parser help shows `usage: vael`).
- `hermes`/`hermes.exe`/`hermes.py` invocation prints a once-per-process
  `[vael] NOTE: the hermes command is a deprecated alias ...` to stderr
  (`_warn_if_deprecated_hermes_alias()` at the top of `main()`); stdout stays
  clean for JSON/help/pipes. `hermes-agent` (legacy ACP entry) is NOT the alias.
- `_set_process_title()` now stamps `vael` (was `hermes`).
- Contract test: `tests/hermes_cli/test_cli_alias_deprecation.py` (4 tests).
- Verified: simulated `vael --help` (no notice) and `hermes --help`
  (notice + full help).

## IR-5 — model-facing content tests (done)

New guards in `tests/branding/test_vael_brand.py` (stdlib-only; run under
pytest AND by the `vael-brand` CI job):
- `test_vael_skill_bodies_say_vael` — renamed `vael-*` SKILL.md prose
  (allowlist: `author:` rows, upstream URLs, R-7 paths/env, `metadata.hermes`
  legacy-key docs, code spans, `Hermes 4`).
- `test_tool_schema_descriptions_say_vael` — AST scan of `description=`
  values in `tools/` (caught + fixed `browser_use_cli.py`
  "Hermes-managed copy" → "VAEL-managed copy").
- `test_cli_primary_is_vael` — entry points agree + alias notice present.
- `test_no_old_top_module_imports` — AST scan pinning the IR2 rename
  (regex pre-filter: 100s → 10s).
- Stale-test updates: `test_cron_failure_notice_copy.py` now expects the
  rebranded `vael -p ops auth add ...` notice (code was already VAEL).
- Prompt assembly audited (`agent/prompt_builder.py`): identity says VAEL;
  remaining hits are attribution, upstream URLs, wire attrs
  (`data-hermes-send`), paths and comments — covered by
  `test_system_prompt_identity`.

## IR-6 — CI guards (done)

- `vael-brand.yml` R-7 job repaired: it referenced the deleted
  `hermes_constants.py` (now `vael_constants.py` in presence greps, smoke
  import and audit allowlist).
- The `vael-brand` job runs `test_vael_brand.py`, so the four IR-5 guards
  ARE the CI guards (no new jobs needed).
- Simulation proof: a temp `import hermes_state` probe file fails
  `test_no_old_top_module_imports` naming the offender; deleting it passes.

## IR-7 — documentation (this file + README + logs)

- `README.md`: primary `vael` usage + `hermes` alias note, attribution kept.
- `docs/verification-log.md`: IR-4..IR-6 + IR2 results appended.
- `docs/open-items.md`: model-facing rename marked done; residuals listed.

## IR-8 — what NOT to rename (intentional `hermes` references)

These stay, deliberately. Changing any of them breaks merges, contracts or
the law:
- `LICENSE` (MIT, Copyright (c) 2025 Nous Research) + `NOTICE` + the single
  README/footer attribution line ("based on Hermes Agent by Nous Research").
- Upstream git remote (`github.com/NousResearch/hermes-agent`) — security
  patches merge from there. Same for upstream URLs in docs/site config.
- `HERMES_*` env vars and `~/.hermes` paths at call sites — the R-7 mirror
  (`resolve_env`, `_mirror_vael_env`) bridges them; rewiring call sites
  would destroy upstream cherry-pickability.
- `Hermes 4` / `Hermes-4-70B` — Nous Research model names, not ours.
- Wire/protocol contracts: `X-Hermes-Session-Id`, `X-Hermes-Session-Key`,
  `X-Hermes-Delivery`, `X-Hermes-Event`, `X-Hermes-Signature-256`,
  `Hermes-Monitor/1.0`, `Hermes-Setup.exe`, `data-hermes-send`,
  `window.hermes.send`, `hermes-gateway` service names.
- Logger names (`logging.getLogger("hermes_state")` etc.) — caplog tests pin
  the origin module's name for log-record parity across the split.
- `hermes_cli/` package directory + `hermes-cli` toolset keys — internal
  surface; renaming a 100+ module package (2,244 import sites) buys nothing
  model-facing and maximizes merge conflicts. See IR2 below.
- `hermes cron ...` / `hermes doctor` strings in cron/delivery notices —
  both binaries run the same parser so they keep working via the alias;
  mass-rebranding user copy is a separate product decision (open item).
- Skill `author: ... Hermes Agent` rows + upstream skill prose in
  non-`vael-*` skills — authorship facts / third-party text.
- The `gui` deprecated alias in `hermes_cli/main.py` (pre-existing).

## IR2 — `hermes_*.py` → `vael_*.py` file/import rename (done)

Top-level modules renamed via `git mv` (history preserved): `hermes_bootstrap`,
`hermes_constants(+_scratch)`, `hermes_logging`, `hermes_startup_watchdog`,
`hermes_state(+21 siblings)`, `hermes_time`, `hermes_yaml`, plus the `hermes`
→ `vael` launcher and `setup-hermes.*` → `setup-vael.*`.
Import migration convention: `import vael_X as hermes_X` (one line per file,
zero body churn; matches the pre-existing
`import vael_state_wal as hermes_state` in `test_wal_reset_repair_hint.py`).
Two repair rounds: 222 files (top-level modules) + 43 files (siblings like
`hermes_state_wal`, `hermes_state_repair`). Sweep fallout fixed along the way:
`tools/skills_tool.py` dropped `metadata = frontmatter.get("metadata")`
(every `skill_view` failed; one-line restore), four `import hermes_bootstrap`
child-process snippets in `tests/test_hermes_bootstrap.py`, the posix-only
`hermes_constants` probe in `tests/cron/test_cron_script.py`.
Verification: scope-aware AST re-scan finds 0 unbound `hermes_*` module refs;
`import vael_state` (+ siblings) resolves; collection errors 121 → 105 with
zero `NameError` (remaining 105 are Windows-environmental: `pwd`/`termios`/
`signal.SIGKILL`, uninstalled `aiohttp`/`acp` extras — identical before/after).
Rollback: the renames are ordinary commits on this branch (`git log
--oneline` `2dfd9c07`, `1001ede6` + sweep base); revert those commits in
reverse order — no history rewrite needed. The `hermes_cli/` package rename
is explicitly OUT of scope (see IR-8).

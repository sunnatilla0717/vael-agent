# VAEL Agent — Rebranding Plan (Hermes → VAEL, surface-only)

> Status: PR-1 + PR-2 done. Core logic untouched.
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
- [ ] R-5-bridge/R-8/R-9: bridge kontrakt (CyberAI repo), branding testlari,
  CI guardlar (qisman PR-1 da bor; W fazasida website guardlari qo'shildi).

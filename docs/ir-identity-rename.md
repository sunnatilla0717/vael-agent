# IR — Hermes → VAEL identity rename (model-facing content, CLI, skills)

Status: **in progress, paused** — IR‑1/IR‑2/IR‑3 landed on disk (uncommitted);
IR‑4…IR‑8 pending. See "Pause reason" at the end before resuming.

Goal (single sentence): the model must never read "hermes" as its own identity —
skills, prompts, tool descriptions and CLI text all say VAEL, while everything the
upstream merge depends on (`hermes_*.py`, `HERMES_*`, `~/.hermes`, wire headers,
upstream URLs, Hermes 4 model names, attribution) stays verbatim.

## IR‑1 — Audit (done)

Tooling: [audit_model_facing_hermes.py](../scripts/audit_model_facing_hermes.py)
classifies every `hermes` occurrence on a model-facing surface into a documented
keep-category or a `VIOLATION`. Shared rules live in
[vael_identity_rules.py](../scripts/vael_identity_rules.py) (one source of truth for
audit, rewrite and guard).

Surfaces scanned: `skills/`, `optional-skills/`, `agent/`, `tools/`, `hermes_cli/`,
`plugins/`, `locales/en.yaml`, `web/src/i18n/en.ts` — **2691 files**.
Excluded by design: `tools/computer_use/**` (separate security PR, IR‑8) and
`hermes_cli/observability/schemas/**` (frozen wire contract), 17 files total.

| Category | Count | Why it is allowed |
|---|---|---|
| `env-var` | 2159 | `HERMES_*`, `$HERMES_HOME` — R‑7 provides aliases; call sites intentionally unchanged |
| `joined-ident` | 1447 | `hermes_cli`, `hermes-agent`, `.hermes`, `/opt/hermes/…`, `@hermes/…`, `hermes.service`, `X-Hermes-*` |
| `config-path` | 795 | `~/.hermes`, `.hermes.md`, `hermes.json` |
| `attribution` | 165 | "based on Hermes Agent by Nous Research", `author:` credit lines, upstream repo mentions |
| `upstream-url` | 117 | `hermes-agent.nousresearch.com`, `github.com/NousResearch/hermes-agent` |
| `upstream-model` | 4 | `Hermes 4` / `hermes-4-*` model names |
| `exact-token` | 118 | quoted runtime values: `"hermes"`, `"hermes."`, `"hermes-acp"` launcher names |
| **`VIOLATION`** | **0** | — |

Core principle: **only a bare `hermes` / `Hermes` word is an identity word.** Anything
joined to an identifier character (`.`, `_`, `-`, `/`, `@`, `$`, `:`) is an upstream
artifact. This is what keeps `.hermes` paths, env vars and f-string namespaces like
`f"hermes.{key}"` safe.

## IR‑2 — Skill content (done)

* [apply-identity-rename.py](../scripts/apply-identity-rename.py) rewrote prose/CLI
  references across `skills/` and `optional-skills/` (158 + 201 files).
* Frontmatter schema key migrated: `metadata.hermes` → `metadata.vael`
  (**205 keys, 204 files**) via
  [migrate-skill-metadata-key.py](../scripts/migrate-skill-metadata-key.py).
  Readers accept both keys, `vael` first:
  `agent.skill_utils.skill_metadata_block()` plus call sites in
  `tools/skills_tool.py`, `tools/skills_hub_official.py`, `tools/skills_hub_models.py`,
  `tools/skill_linter.py`, `tools/blueprints.py` (reader + writer),
  `agent/learning_graph.py`, `website/scripts/generate-skill-docs.py`,
  `website/scripts/extract-skills.py`.
* Skill-authoring docs/linter messages now say `metadata.vael.{tags, related_skills}`.

## IR‑3 — Prompt content (done)

Same sweep over `agent/`, `tools/`, `hermes_cli/`, `plugins/`, `locales/en.yaml`
and `web/src/i18n/en.ts` — 1168 files, 6418 lines. Identity strings already correct
(`agent/prompt_builder.py:DEFAULT_AGENT_IDENTITY`, `hermes_cli/default_soul.py`)
keep the attribution clause "…based on Hermes Agent by Nous Research, MIT".

## Verification (as of pause)

* `python scripts/audit_model_facing_hermes.py --fail` → `violations: 0 in 0 files`
* `python scripts/verify-identity-rename.py` → every protected token from `HEAD`
  still present, no minted `.vael` / `@vael/…` artifacts (539 files compared).
* `tests/branding/test_identity_rules.py` (48 cases) +
  `tests/branding/test_identity_rename_apply.py` (22 cases) → 70 passed.
* `python -m compileall agent tools hermes_cli plugins scripts` → clean.

Bugs the verification caught (all fixed before landing):

1. `\b` before `".hermes"` never matched (no word boundary between `"` and `.`) —
   first sweep minted `.vael` paths in 65 places. Sweep rolled back and re-run with
   the bare-word rule.
2. `f"hermes.{col}"` (OTLP attribute namespace) and `startswith("hermes.")` launcher
   checks were rewritten — now protected by the `.` + alnum/`{`/`<`/`[` lookahead
   and by the "whole literal is one token" rule.
3. `hermes.<key>` in docstrings — same fix.

## Pending

* **IR‑4 CLI rename** — `pyproject.toml` already has `vael = "hermes_cli.main:main"`
  next to `hermes`; still to do: deprecation warning for the `hermes` entry point,
  `prog=`/usage text (currently `prog="hermes"`), launcher/shim names
  (`hermes_cli/_launchers.py`, `_install_repair.py`, `install.ps1`), completion
  scripts, and the `hermes <cmd>` references in `website/docs/**` + root `README.md`.
* **IR‑5 tests** — update CLI-name assertions, add "vael works / hermes warns" tests.
* **IR‑6 CI guards** — wire `audit_model_facing_hermes.py --fail` into
  `.github/workflows/vael-brand.yml` (job `vael-brand`).
* **IR‑7 docs** — README (primary usage `vael`, alias note), REBRANDING.md,
  open-items, verification-log.
* **IR‑8 rationale** — record why `hermes_*.py` / `HERMES_*` / wire headers /
  attribution stay; my sweep keeps them by construction (see the categories above).

## Pause reason (read before resuming)

While IR‑1…IR‑3 were landing, a **parallel change set started renaming the Python
modules themselves** (`hermes_constants.py` → `vael_constants.py`, plus ~38 staged
`vael_*.py` renames and import rewrites across ~989 files). That is explicitly out
of scope for IR ("Do NOT rename Python file names — upstream merge must remain
possible"), and it is mid-flight: `tests/conftest.py` imports `vael_constants` while
still calling `hermes_constants`, so `tests/branding` currently errors at import.

Consequences for the resume:

1. Wait for the module rename to finish (or be reverted) before running the pytest
   suites — collection errors there are not IR regressions.
2. `scripts/verify-identity-rename.py` now also reports `vael_constants`-style
   tokens as "minted" because they are new relative to `HEAD`; scope it to your own
   sweep (or re-baseline it) once the module rename is settled.
3. My sweep never touches identifiers, imports or module names, so it is orthogonal
   to the module rename — the two sets can coexist, but re-run the audit after the
   other work stops.

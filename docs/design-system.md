# VAEL Design System (PR-3)

Single source of truth for color: `apps/shared/src/theme-presets.ts`.
Both the desktop app and the web dashboard derive from that table —
edit hexes there, both surfaces follow.

## Palette — `vael` preset (Claude-orange)

| Slot | Light | Dark |
| ---- | ----- | ---- |
| Background | `#FBF7F1` (warm paper) | `#191410` (warm charcoal) |
| Foreground | `#1F1B16` | `#F5EDE3` |
| Primary | `#D97757` | `#D97757` |
| Accent | `#CC785C` | `#CC785C` |
| Ring / midground / composerRing | `#D97757` | `#D97757` |
| Destructive | `#C0392B` | `#E06C5B` |

Rules:

- Primary `#D97757` and accent `#CC785C` are identical on light and dark —
  brand recognition beats per-mode tuning.
- Never hardcode these hexes in components; use theme tokens
  (`--color-primary`, `--color-ring`, `midground`, `DesktopTheme` slots).
- Upstream presets (`nous`, `github`, `catppuccin`, …) stay shipped and
  untouched so upstream merges stay clean. `vael` is first-party like
  `nous-alt`: hand-tuned, never re-derived from a marketplace theme.

## Defaults

- Desktop: `DEFAULT_SKIN_NAME = 'vael'` (`apps/desktop/src/themes/presets.ts`).
  A stored pick of any other skin is respected; only fresh installs and
  retired names fall back to VAEL.
- Dashboard: `defaultTheme` (`web/src/themes/presets.ts`, stable key
  `"default"`) is projected from the shared `vael` palette via
  `webPresetFromShared`. The key stays `"default"` so existing user prefs
  keep working.

## Typography

System stacks only (no webfont dependency for the default look):

- Sans: Segoe UI / SF Pro / system-ui (desktop `SYSTEM_SANS`).
- Mono: JetBrains Mono (bundled) → Cascadia → platform fallbacks.
- Every stack ends with a color-emoji fallback (see `#40364` test).

This matches the CyberAI Console direction: system type, generous spacing,
dark-mode-first, orange as the single brand signal.

## Dark mode

Dark palettes are the home turf (dashboard reads `darkColors` when present).
Contrast floor for the accent-on-canvas pair is enforced by test
(`web/src/themes/presets.test.ts`, ≥ 3:1).

## Files

- `apps/shared/src/theme-presets.ts` — palette table (`vael` entry).
- `apps/desktop/src/themes/presets.ts` — `vaelTheme`, `BUILTIN_THEMES`, default.
- `web/src/themes/presets.ts` — `defaultTheme` → shared `vael` projection.
- `tests/branding/test_vael_brand.py` — primary-hex snapshot guard.

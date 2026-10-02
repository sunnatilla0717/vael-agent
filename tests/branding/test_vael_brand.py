"""VAEL rebrand guards (PR-1 foundation).

Runs under pytest AND standalone (``python3 tests/branding/test_vael_brand.py``)
so the lightweight CI job needs no dependencies.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_license_unchanged():
    lic = _read("LICENSE")
    assert "Copyright (c) 2025 Nous Research" in lic
    assert lic.startswith("MIT License")


def test_readme_attribution():
    readme = _read("README.md")
    assert "based on hermes agent by nous research (mit" in readme.lower()
    assert any(ln.startswith("# VAEL") for ln in readme.splitlines())


def test_notice_exists():
    notice = _read("NOTICE")
    assert "Nous Research" in notice
    assert "MIT" in notice
    assert "https://github.com/NousResearch/hermes-agent" in notice


def test_system_prompt_identity():
    pb = _read("agent/prompt_builder.py")
    assert "You are VAEL" in pb
    assert "You are Hermes Agent, built by Nous Research" not in pb
    for rel in ("SOUL.md", "docker/SOUL.md", "hermes_cli/default_soul.py"):
        assert "You are VAEL" in _read(rel), rel


def test_no_hermes_word_in_user_strings():
    # Whole-word "Hermes" must not appear in rebranded user-facing files.
    # (Lowercase `hermes` command literals, keys, URLs and legacy-upgrade
    # tuples are intentionally out of scope for PR-1.)
    pat = re.compile(r"\bHermes\b")
    for rel in (
        "locales/en.yaml",
        "web/src/i18n/en.ts",
        "web/index.html",
        "plugins/platforms/telegram/plugin.yaml",
    ):
        text = _read(rel)
        hits = [ln for ln in text.splitlines() if pat.search(ln)]
        assert not hits, f"{rel}: {hits[:3]}"


def test_telegram_plugin_branding():
    plugin = _read("plugins/platforms/telegram/plugin.yaml")
    assert "VAEL" in plugin


def test_web_dashboard_branding():
    html = _read("web/index.html")
    assert "VAEL" in html
    assert "Hermes" not in html


def test_desktop_display_branding():
    identity = _read("apps/desktop/product-identity.cjs")
    assert "display: 'VAEL'" in identity
    # Artifact names stay stable for builds and upstream merges.
    assert "kebab: 'hermes'" in identity


if __name__ == "__main__":
    for name, fn in sorted(
        [(k, v) for k, v in globals().items() if k.startswith("test_")],
    ):
        fn()
        print(f"PASS {name}")
    print("VAEL brand guards: ALL GREEN")

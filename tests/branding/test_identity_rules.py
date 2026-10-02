"""IR-5: unit tests for the shared identity-rename rules (IR-1..IR-6).

These tests pin the *intent* of the rename: model-facing identity words change,
the upstream-merge compatibility layer (env vars, `hermes_*` modules, `~/.hermes`
paths, wire headers, upstream URLs and the Hermes 4 model names) never does.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from vael_identity_rules import has_bare_hermes, rename  # noqa: E402


@pytest.mark.parametrize(
    "before, after",
    [
        # --- Identity prose the model reads -------------------------------------------
        ("You are in the Hermes terminal UI (TUI).", "You are in the VAEL terminal UI (TUI)."),
        ("Mid-turn, the user can steer you: Hermes delivers their message", "Mid-turn, the user can steer you: VAEL delivers their message"),
        ("Hermes' own control frames", "VAEL's own control frames"),
        ("the Hermes desktop app, a graphical chat surface", "the VAEL desktop app, a graphical chat surface"),
        ("which Hermes points at its own scratch dir", "which VAEL points at its own scratch dir"),
        # --- CLI invocations become the new primary binary ------------------------------
        ("run `hermes skills install official/devops/foo`", "run `vael skills install official/devops/foo`"),
        ("Use `hermes doctor` on the host.", "Use `vael doctor` on the host."),
        ("hermes [flags] [command]", "vael [flags] [command]"),
        # --- Upstream attribution stays verbatim ---------------------------------------
        ("based on Hermes Agent by Nous Research", "based on Hermes Agent by Nous Research"),
        ("This is based on the Hermes Agent by Nous Research.", "This is based on the Hermes Agent by Nous Research."),
        # --- R-7 compatibility layer stays verbatim ------------------------------------
        ("$HERMES_HOME/skills/", "$HERMES_HOME/skills/"),
        ("~/.hermes/config.yaml", "~/.hermes/config.yaml"),
        ("HERMES_KANBAN_WORKSPACE", "HERMES_KANBAN_WORKSPACE"),
        # --- Internal identifiers stay verbatim ----------------------------------------
        ("from hermes_constants import get_hermes_home", "from hermes_constants import get_hermes_home"),
        ("hermes_cli/main.py", "hermes_cli/main.py"),
        ("toolsets: [\"hermes-cli\"]", "toolsets: [\"hermes-cli\"]"),
        ("_hermes_metadata(frontmatter)", "_hermes_metadata(frontmatter)"),
        # --- Wire protocol / artifact names stay verbatim ------------------------------
        ("X-Hermes-Session-Id", "X-Hermes-Session-Id"),
        ("Hermes-Monitor/1.0", "Hermes-Monitor/1.0"),
        ("data-hermes-send=\"prompt\"", "data-hermes-send=\"prompt\""),
        ("hermes-gateway", "hermes-gateway"),
        # --- Upstream URLs, package name, model names stay verbatim --------------------
        ("https://hermes-agent.nousresearch.com/docs/llms.txt", "https://hermes-agent.nousresearch.com/docs/llms.txt"),
        ("https://github.com/NousResearch/hermes-agent", "https://github.com/NousResearch/hermes-agent"),
        ("hermes-agent", "hermes-agent"),
        ("Hermes 4 70B", "Hermes 4 70B"),
        ("hermes-4-70b", "hermes-4-70b"),
        # --- Artifacts joined to path/identifier characters stay verbatim ---------------
        ('root / ".hermes" / "bin"', 'root / ".hermes" / "bin"'),
        ("$HOME/.hermes", "$HOME/.hermes"),
        ("${HERMES_HOME:-$HOME/.hermes}", "${HERMES_HOME:-$HOME/.hermes}"),
        ("/opt/hermes/docker/main-wrapper.sh", "/opt/hermes/docker/main-wrapper.sh"),
        ("hermes.service", "hermes.service"),
        ("@hermes/plugin-sdk", "@hermes/plugin-sdk"),
        ("hermes.update.run", "hermes.update.run"),
        ("main-hermes/run", "main-hermes/run"),
        ("--hermes-flag", "--hermes-flag"),
        ("hermes.ai", "hermes.ai"),
        ("hermes.json", "hermes.json"),
        ("hermes_agent", "hermes_agent"),
        # --- Attribution / credit lines stay verbatim ----------------------------------
        ("author: Teknium + Hermes Agent", "author: Teknium + Hermes Agent"),
        ("Your fork is not tracking the official Hermes repository.", "Your fork is not tracking the official Hermes repository."),
        ("EVM blockchain CLI tool for the Hermes Agent project.", "EVM blockchain CLI tool for the Hermes Agent project."),
        ("(based on Hermes Agent by Nous Research, MIT)", "(based on Hermes Agent by Nous Research, MIT)"),
        # --- Sentence punctuation does not block a rename -------------------------------
        ("Restart it with hermes.", "Restart it with vael."),
        ("Run `hermes`, then `hermes doctor`.", "Run `vael`, then `vael doctor`."),
        ("VAEL (hermes) shipped", "VAEL (vael) shipped"),
    ],
)
def test_rename_rules(before: str, after: str) -> None:
    assert rename(before) == after


def test_rename_is_idempotent() -> None:
    samples = [
        "You are in the Hermes terminal UI (TUI).",
        "run `hermes skills install foo`",
        "based on Hermes Agent by Nous Research",
        "~/.hermes/skills",
    ]
    for sample in samples:
        once = rename(sample)
        assert rename(once) == once


def test_no_vael_artifacts() -> None:
    """The rename must never mint a joined `vael` identifier (`.vael`, `@vael/…`)."""
    for artifact in (
        '".hermes" / "bin"',
        "/opt/hermes/docker",
        "hermes.service",
        "@hermes/plugin-sdk",
        "hermes.update.run",
    ):
        assert rename(artifact) == artifact, f"rename minted an artifact from {artifact!r}"


def test_has_bare_hermes() -> None:
    assert has_bare_hermes("published by Hermes")
    assert not has_bare_hermes("published by VAEL")
    assert not has_bare_hermes("based on Hermes Agent by Nous Research")
    assert not has_bare_hermes("HERMES_HOME points at ~/.hermes")
    assert not has_bare_hermes("author: Teknium + Hermes Agent")

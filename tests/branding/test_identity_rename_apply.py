"""IR-5: regression tests for the per-file-family rewrite strategies.

The dangerous failure mode of the identity rename is *minting artifacts*: turning
`hermes.` (a telemetry namespace), `"hermes."` (a launcher-suffix check) or
`f"hermes.{key}"` (an f-string attribute prefix) into `vael.*`.  These tests pin
the three rewrite paths used by `scripts/apply-identity-rename.py`.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def renamer() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "apply_identity_rename", REPO_ROOT / "scripts" / "apply-identity-rename.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("apply_identity_rename", module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "before, after",
    [
        # --- prose / CLI in Python strings and comments -------------------------------
        (
            'PROMPT = "You are in the Hermes terminal UI (TUI)."\n',
            'PROMPT = "You are in the VAEL terminal UI (TUI)."\n',
        ),
        ('HELP = "run `hermes doctor` on the host"\n', 'HELP = "run `vael doctor` on the host"\n'),
        ("# Hermes delivers the steer marker\n", "# VAEL delivers the steer marker\n"),
        ('    """Gateway subcommand for hermes CLI."""\n', '    """Gateway subcommand for vael CLI."""\n'),
        # --- runtime values and namespaces stay verbatim ------------------------------
        ('LAUNCHERS = ("hermes", "hermes-acp")\n', 'LAUNCHERS = ("hermes", "hermes-acp")\n'),
        ('if base == "hermes" or base.startswith("hermes."):\n', 'if base == "hermes" or base.startswith("hermes."):\n'),
        ('attrs[f"hermes.{col}"] = value\n', 'attrs[f"hermes.{col}"] = value\n'),
        ('tracer.start_span(f"hermes.{ev}")\n', 'tracer.start_span(f"hermes.{ev}")\n'),
        ('"""``hermes.<key>`` attributes for present keys."""\n', '"""``hermes.<key>`` attributes for present keys."""\n'),
        ('home = os.path.join(root, ".hermes")\n', 'home = os.path.join(root, ".hermes")\n'),
        ('from hermes_constants import get_hermes_home\n', 'from hermes_constants import get_hermes_home\n'),
        ("env = os.environ.get('HERMES_HOME')\n", "env = os.environ.get('HERMES_HOME')\n"),
    ],
)
def test_python_rewrite(renamer: ModuleType, before: str, after: str) -> None:
    assert renamer.rename_python(before) == after


@pytest.mark.parametrize(
    "before, after",
    [
        ('  fix: "run `hermes gateway restart` now"\n', '  fix: "run `vael gateway restart` now"\n'),
        ('  "hermes" as a value stays\n', '  "hermes" as a value stays\n'),
        ('  path: "hermes.service"\n', '  path: "hermes.service"\n'),
        ('export const label = "Hermes Agent";\n', 'export const label = "VAEL Agent";\n'),
    ],
)
def test_code_text_rewrite(renamer: ModuleType, before: str, after: str) -> None:
    assert renamer.rename_code_text(before) == after


@pytest.mark.parametrize(
    "before, after",
    [
        ("- Install it: `hermes skills install official/devops/foo`\n", "- Install it: `vael skills install official/devops/foo`\n"),
        ("- Config lives in `~/.hermes/config.yaml`\n", "- Config lives in `~/.hermes/config.yaml`\n"),
        ("- Telemetry is emitted as `hermes.<key>`\n", "- Telemetry is emitted as `hermes.<key>`\n"),
        ("metadata:\n  hermes:\n    tags: [x]\n", "metadata:\n  hermes:\n    tags: [x]\n"),
        ("You are in the Hermes TUI.\n", "You are in the VAEL TUI.\n"),
        ("author: Teknium + Hermes Agent\n", "author: Teknium + Hermes Agent\n"),
    ],
)
def test_markdown_rewrite(renamer: ModuleType, tmp_path: Path, before: str, after: str) -> None:
    target = tmp_path / "SKILL.md"
    assert renamer.transform(target, before) == after

"""IR-4: `hermes` stays a working alias of `vael` with a once-per-process notice.

Contract: invoking the CLI as `hermes`/`hermes.exe` prints a deprecation
notice to stderr exactly once per process and otherwise behaves identically;
invoking as `vael` (or anything else) stays silent.
"""

import pytest

from hermes_cli import main as cli_main


@pytest.fixture
def fresh_alias_flag(monkeypatch):
    monkeypatch.setattr(cli_main, "_HERMES_ALIAS_WARNED", False)


def test_hermes_alias_warns_once(fresh_alias_flag, capsys):
    cli_main._warn_if_deprecated_hermes_alias("hermes")
    first = capsys.readouterr()
    assert "vael" in first.err
    assert "deprecated alias" in first.err
    assert cli_main._HERMES_ALIAS_WARNED is True
    # Second call in the same process stays silent.
    cli_main._warn_if_deprecated_hermes_alias("hermes")
    assert capsys.readouterr().err == ""


def test_hermes_exe_alias_warns(fresh_alias_flag, capsys):
    cli_main._warn_if_deprecated_hermes_alias("C:\\venv\\Scripts\\hermes.exe")
    assert "deprecated alias" in capsys.readouterr().err


def test_vael_primary_is_silent(fresh_alias_flag, capsys):
    cli_main._warn_if_deprecated_hermes_alias("/usr/local/bin/vael")
    assert capsys.readouterr().err == ""
    assert cli_main._HERMES_ALIAS_WARNED is False


def test_hermes_agent_entry_is_not_the_alias(fresh_alias_flag, capsys):
    # `hermes-agent` is the legacy ACP entry (agent.legacy_cli:main), not the CLI alias.
    cli_main._warn_if_deprecated_hermes_alias("hermes-agent")
    assert capsys.readouterr().err == ""

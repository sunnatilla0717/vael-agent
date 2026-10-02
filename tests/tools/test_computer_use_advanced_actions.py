"""Tests for the computer_use capability actions: launch_app, wait_for, screen_info.

`launch_app` closes the gap `focus_app` cannot (an app that has no window yet);
`wait_for` replaces blind `wait` sleeps with a watched condition; `screen_info`
reports monitor geometry for multi-monitor coordinate math. All three degrade to
`code: unsupported` on backends/drivers that predate them.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from tools.computer_use.backend import ActionResult, CaptureResult, ComputerUseBackend, UIElement

_FRAME_EMPTY = CaptureResult(mode="ax", width=800, height=600, elements=[], app="Notes", window_title="Untitled")
_FRAME_SAVED = CaptureResult(
    mode="ax", width=800, height=600, app="Notes", window_title="Untitled",
    elements=[UIElement(index=7, role="AXButton", label="Saved to your library", bounds=(10, 20, 120, 30))],
)
_FRAME_OTHER = CaptureResult(
    mode="ax", width=800, height=600, app="Notes", window_title="Library",
    elements=[UIElement(index=1, role="AXStaticText", label="Library", bounds=(0, 0, 200, 20))],
)


class _FakeBackend(ComputerUseBackend):
    """Duck-typed backend with scripted capture frames; each frame repeats once exhausted.

    Deliberately does NOT override ``launch_app`` / ``screen_info``: it inherits the base-class
    compatibility defaults so the unsupported paths are exercised too.
    """

    def __init__(self, frames: list[CaptureResult] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.frames = list(frames or [])
        self.captures = 0

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def is_available(self) -> bool: return True

    def capture(self, mode="som", app=None, pid=None, window_id=None) -> CaptureResult:
        self.calls.append(("capture", {"mode": mode, "app": app}))
        self.captures += 1
        if not self.frames:
            return CaptureResult(mode=mode, width=800, height=600, elements=[], app=app or "Notes")
        return self.frames[min(self.captures, len(self.frames)) - 1]

    def click(self, **_kw) -> ActionResult: return ActionResult(ok=True, action="click")
    def drag(self, **_kw) -> ActionResult: return ActionResult(ok=True, action="drag")
    def scroll(self, **_kw) -> ActionResult: return ActionResult(ok=True, action="scroll")
    def type_text(self, text, **_kw) -> ActionResult: return ActionResult(ok=True, action="type")
    def key(self, keys, **_kw) -> ActionResult: return ActionResult(ok=True, action="key")
    def list_apps(self): return []
    def focus_app(self, app, raise_window=False) -> ActionResult: return ActionResult(ok=True, action="focus_app")
    def set_value(self, value, element=None) -> ActionResult: return ActionResult(ok=True, action="set_value")


class _LaunchableBackend(_FakeBackend):
    """Adds the modern driver surface: app launching + display geometry."""

    def launch_app(self, **kwargs):
        self.calls.append(("launch_app", kwargs))
        return {"pid": 4242, "name": kwargs.get("name") or "Notes", "windows": [{"window_id": 7}]}

    def screen_info(self) -> dict:
        self.calls.append(("screen_info", {}))
        return {"screen": {"width": 3440, "height": 1440}, "displays": [{"x": 0, "y": 0, "width": 3440}],
                "cursor": {"x": 12, "y": 34}}


@pytest.fixture(autouse=True)
def _reset_backend(grant_computer_use_approvals):
    from tools.computer_use.tool import reset_backend_for_tests
    reset_backend_for_tests()
    yield
    reset_backend_for_tests()


def _run(backend: ComputerUseBackend, args: dict):
    """Dispatch one action against *backend*; returns (payload, backend)."""
    from tools.computer_use import tool as cu_tool

    with patch.object(cu_tool, "_new_backend", return_value=backend):
        out = cu_tool.handle_computer_use(dict(args))
    assert isinstance(out, str), f"expected a text result, got {type(out)}"
    return json.loads(out)


# ---------------------------------------------------------------------------
# launch_app
# ---------------------------------------------------------------------------

class TestLaunchApp:

    def test_launches_by_display_name(self):
        backend = _LaunchableBackend()
        payload = _run(backend, {"action": "launch_app", "app": "Notes"})
        assert payload["ok"] is True
        assert payload["launched"]["pid"] == 4242
        assert backend.calls == [("launch_app", {"name": "Notes", "bundle_id": None, "urls": None,
                                                 "additional_arguments": None,
                                                 "creates_new_application_instance": False})]

    def test_reverse_dns_app_is_routed_as_bundle_id(self):
        backend = _LaunchableBackend()
        payload = _run(backend, {"action": "launch_app", "app": "com.apple.Safari"})
        assert payload["ok"] is True
        assert backend.calls[0][1]["bundle_id"] == "com.apple.Safari"
        assert backend.calls[0][1]["name"] is None

    def test_explicit_bundle_id_wins_over_name(self):
        backend = _LaunchableBackend()
        _run(backend, {"action": "launch_app", "app": "Safari", "bundle_id": "com.apple.Safari"})
        assert backend.calls[0][1] == {"name": "Safari", "bundle_id": "com.apple.Safari", "urls": None,
                                       "additional_arguments": None, "creates_new_application_instance": False}

    def test_urls_and_new_instance_are_forwarded(self):
        backend = _LaunchableBackend()
        _run(backend, {"action": "launch_app", "app": "Safari", "urls": ["https://example.com"],
                       "arguments": ["--private"], "new_instance": True})
        assert backend.calls[0][1]["urls"] == ["https://example.com"]
        assert backend.calls[0][1]["additional_arguments"] == ["--private"]
        assert backend.calls[0][1]["creates_new_application_instance"] is True

    def test_missing_target_is_refused_without_reaching_the_backend(self):
        backend = _LaunchableBackend()
        payload = _run(backend, {"action": "launch_app"})
        assert payload["ok"] is False
        assert "requires `app`" in payload["error"]
        assert backend.calls == []

    def test_legacy_backend_reports_unsupported_not_a_failure(self):
        backend = _FakeBackend()  # inherits the base hook -> NotImplementedError
        payload = _run(backend, {"action": "launch_app", "app": "Notes"})
        assert payload["ok"] is False
        assert payload["code"] == "unsupported"

    def test_driver_refusal_is_reported_as_not_ok(self):
        class _Refusing(_LaunchableBackend):
            def launch_app(self, **kwargs):
                raise RuntimeError("no such app: Nope")

        payload = _run(_Refusing(), {"action": "launch_app", "app": "Nope"})
        assert payload["ok"] is False
        assert "launch_app failed" in payload["error"]


# ---------------------------------------------------------------------------
# wait_for
# ---------------------------------------------------------------------------

class TestWaitFor:

    def test_returns_the_frame_that_matched(self):
        backend = _FakeBackend([_FRAME_EMPTY, _FRAME_EMPTY, _FRAME_SAVED])
        payload = _run(backend, {"action": "wait_for", "text": "Saved", "timeout": 5, "interval": 0.1})
        assert payload["wait_matched"] is True
        assert payload["wait_text"] == "Saved"
        assert [e["label"] for e in payload["elements"]] == ["Saved to your library"]
        assert backend.captures == 3

    def test_match_is_case_insensitive_and_checks_window_title(self):
        backend = _FakeBackend([_FRAME_OTHER])
        payload = _run(backend, {"action": "wait_for", "text": "library", "timeout": 1, "interval": 0.1})
        assert payload["wait_matched"] is True

    def test_timeout_returns_a_verdict_and_the_last_frame(self):
        backend = _FakeBackend([_FRAME_EMPTY])
        payload = _run(backend, {"action": "wait_for", "text": "Saved", "timeout": 0.2, "interval": 0.1})
        assert payload["wait_matched"] is False
        assert "TIMEOUT" in payload["summary"]
        assert payload["waited_s"] >= 0.2
        assert payload["window_title"] == "Untitled"  # the last frame is still actionable

    def test_default_predicate_waits_for_any_change(self):
        backend = _FakeBackend([_FRAME_EMPTY, _FRAME_EMPTY, _FRAME_OTHER])
        payload = _run(backend, {"action": "wait_for", "timeout": 5, "interval": 0.1})
        assert payload["wait_matched"] is True
        assert "a screen change" in payload["summary"]

    def test_polling_defaults_to_the_cheap_ax_mode(self):
        som = CaptureResult(mode="som", width=800, height=600, png_b64="iVBORw0KGgo=", elements=[], app="Notes")
        backend = _FakeBackend([som])
        payload = _run(backend, {"action": "wait_for", "text": "Notes", "timeout": 1, "interval": 0.1})
        assert payload["wait_matched"] is True
        assert "_multimodal" not in payload  # a wait never costs a vision call
        assert backend.calls[0][1]["mode"] == "ax"

    def test_som_mode_is_opt_in(self):
        backend = _FakeBackend([_FRAME_OTHER])
        _run(backend, {"action": "wait_for", "text": "Library", "mode": "som", "timeout": 1, "interval": 0.1})
        assert backend.calls[0][1]["mode"] == "som"

    def test_bounds_are_clamped(self):
        from tools.computer_use import tool as cu_tool

        assert cu_tool._wait_for_number(10_000, 10.0, low=0.0, high=60.0) == 60.0
        assert cu_tool._wait_for_number(99, 0.5, low=0.1, high=5.0) == 5.0
        assert cu_tool._wait_for_number(-3, 10.0, low=0.0, high=60.0) == 0.0
        assert cu_tool._wait_for_number("nonsense", 10.0, low=0.0, high=60.0) == 10.0  # bad input keeps the default
        assert cu_tool._wait_for_number(None, 0.5, low=0.1, high=5.0) == 0.5


# ---------------------------------------------------------------------------
# screen_info
# ---------------------------------------------------------------------------

class TestScreenInfo:

    def test_reports_geometry_and_cursor(self):
        backend = _LaunchableBackend()
        payload = _run(backend, {"action": "screen_info"})
        assert payload["ok"] is True
        assert payload["screen"] == {"width": 3440, "height": 1440}
        assert payload["cursor"] == {"x": 12, "y": 34}

    def test_legacy_backend_reports_unsupported(self):
        payload = _run(_FakeBackend(), {"action": "screen_info"})
        assert payload["ok"] is False
        assert payload["code"] == "unsupported"


# ---------------------------------------------------------------------------
# Schema contract
# ---------------------------------------------------------------------------

class TestSchemaContract:

    def test_new_actions_and_properties_are_advertised(self):
        from tools.computer_use.schema import COMPUTER_USE_SCHEMA

        properties = COMPUTER_USE_SCHEMA["parameters"]["properties"]
        actions = set(properties["action"]["enum"])
        assert {"launch_app", "wait_for", "screen_info"} <= actions
        assert {"bundle_id", "urls", "arguments", "new_instance", "timeout", "interval", "changed"} <= set(properties)

    def test_every_action_has_a_handler_and_summary(self):
        from tools.computer_use import tool as cu_tool
        from tools.computer_use.schema import COMPUTER_USE_SCHEMA

        for action in COMPUTER_USE_SCHEMA["parameters"]["properties"]["action"]["enum"]:
            assert action in cu_tool._ACTIONS, f"{action} is advertised but has no handler"
            assert cu_tool._summarize_action(action, {"app": "Notes", "element": 1, "coordinate": [1, 2]})

    def test_unknown_action_names_the_replacement(self):
        payload = _run(_LaunchableBackend(), {"action": "open_app", "app": "Notes"})
        assert "launch_app" in payload["error"]

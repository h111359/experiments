"""Unit tests for .aib_brain/tools/menu.py."""

from __future__ import annotations

import io
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

import menu
from menu import (
    MenuState,
    _make_log_path,
    _run_and_tee,
    _sanitize_action_id,
    build_command,
    build_script_actions,
    collect_parameters,
    filter_visible_actions,
    resolve_menu_state,
    validate_param,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_state(
    req_id: str | None = None,
    req_folder: str | None = None,
) -> MenuState:
    return MenuState(req_id, req_folder)


REGISTER_HEADER = "| request_id | title | folder | state | created_at | closed_at |"
REGISTER_SEP =    "| --- | --- | --- | --- | --- | --- |"


def _register_with_row(req_id: str, folder: str, state: str) -> str:
    row = f"| {req_id} | My Request | {folder} | {state} | 2026-01-01 10:00:00 +0000 |  |"
    return f"# Requests Register\n\n{REGISTER_HEADER}\n{REGISTER_SEP}\n{row}\n"


def _iterations_with_row(iter_id: str, state: str) -> str:
    header = "| iteration_id | state | created_at | closed_at | summary |"
    sep =    "| --- | --- | --- | --- | --- |"
    row =    f"| {iter_id} | {state} | 2026-01-01 10:00:00 +0000 |  | Initial |"
    return f"# Iterations\n\n{header}\n{sep}\n{row}\n"


# ---------------------------------------------------------------------------
# resolve_menu_state
# ---------------------------------------------------------------------------

class TestResolveMenuState:
    def test_no_register_returns_empty_state(self, tmp_path: Path):
        state = resolve_menu_state(tmp_path)
        assert state == MenuState(None, None, None)

    def test_empty_register_returns_empty_state(self, tmp_path: Path):
        reg = tmp_path / ".aib_memory" / "requests_register.md"
        reg.parent.mkdir(parents=True)
        reg.write_text(
            "# Requests Register\n\n"
            "| request_id | title | folder | state | created_at | closed_at |\n"
            "| --- | --- | --- | --- | --- | --- |\n",
            encoding="utf-8",
        )
        state = resolve_menu_state(tmp_path)
        assert state == MenuState(None, None, None)

    def test_active_request_resolved(self, tmp_path: Path):
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True)
        reg = mem / "requests_register.md"
        folder = ".aib_memory/requests/R-20260101-1000-test"
        reg.write_text(_register_with_row("R-20260101-1000", folder, "Active"), encoding="utf-8")
        state = resolve_menu_state(tmp_path)
        assert state.active_request_id == "R-20260101-1000"
        assert state.active_request_folder == folder
        assert state.has_active_request

    def test_active_request_no_iterations_file(self, tmp_path: Path):
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True)
        folder_rel = ".aib_memory/requests/R-20260101-1000-test"
        reg = mem / "requests_register.md"
        reg.write_text(_register_with_row("R-20260101-1000", folder_rel, "Active"), encoding="utf-8")
        req_folder = tmp_path / folder_rel
        req_folder.mkdir(parents=True)
        state = resolve_menu_state(tmp_path)
        assert state.active_request_id == "R-20260101-1000"
        assert state.has_active_request

    def test_closed_request_returns_empty_state(self, tmp_path: Path):
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True)
        reg = mem / "requests_register.md"
        reg.write_text(_register_with_row("R-20260101-1000", ".aib_memory/requests/x", "Closed"), encoding="utf-8")
        state = resolve_menu_state(tmp_path)
        assert state == MenuState(None, None, None)


# ---------------------------------------------------------------------------
# filter_visible_actions
# ---------------------------------------------------------------------------

class TestFilterVisibleActions:
    def test_returns_all_actions_when_no_active_request(self):
        """Without an active request, filter_visible_actions is a pass-through."""
        actions = build_script_actions(Path(__file__).resolve().parent.parent / ".aib_brain" / "tools")
        state = _make_state()
        visible = filter_visible_actions(actions, state)
        assert visible == actions

    def test_close_request_not_visible_without_active_request(self):
        """close-request.py must not appear in the visible actions when no active request exists."""
        actions = build_script_actions(Path(__file__).resolve().parent.parent / ".aib_brain" / "tools")
        state = _make_state()
        visible = filter_visible_actions(actions, state)
        scripts = [a["script"] for a in visible]
        assert "close-request.py" not in scripts

    def test_close_request_visible_with_active_request(self):
        """close-request.py must appear in the visible actions when an active request exists."""
        actions = build_script_actions(Path(__file__).resolve().parent.parent / ".aib_brain" / "tools")
        state = _make_state("R-001", ".aib_memory/requests/R-001")
        visible = filter_visible_actions(actions, state)
        scripts = [a["script"] for a in visible]
        assert "close-request.py" in scripts

    def test_create_request_never_visible(self):
        """create-request.py must not appear regardless of active request state."""
        actions = build_script_actions(Path(__file__).resolve().parent.parent / ".aib_brain" / "tools")
        for state in [_make_state(), _make_state("R-001", ".aib_memory/requests/R-001")]:
            visible = filter_visible_actions(actions, state)
            scripts = [a["script"] for a in visible]
            assert "create-request.py" not in scripts

    def test_active_request_adds_one_action(self):
        """filter_visible_actions returns one more action when an active request exists."""
        actions = build_script_actions(Path(__file__).resolve().parent.parent / ".aib_brain" / "tools")
        visible_no_req = filter_visible_actions(actions, _make_state())
        visible_with_req = filter_visible_actions(actions, _make_state("R-001", ".aib_memory/requests/R-001"))
        assert len(visible_with_req) == len(visible_no_req) + 1


# ---------------------------------------------------------------------------
# build_script_actions
# ---------------------------------------------------------------------------

class TestBuildScriptActions:
    def test_returns_list_of_actions(self, tools_dir: Path):
        actions = build_script_actions(tools_dir)
        assert isinstance(actions, list)

    def test_ids_are_sequential_strings(self, tools_dir: Path):
        actions = build_script_actions(tools_dir)
        for i, action in enumerate(actions, start=1):
            assert action["id"] == str(i)

    def test_lifecycle_scripts_absent(self, tools_dir: Path):
        """create-request.py and close-request.py must not appear in the menu actions."""
        actions = build_script_actions(tools_dir)
        scripts = [a["script"] for a in actions]
        for absent in ["create-request.py", "close-request.py"]:
            assert absent not in scripts

    def test_excluded_scripts_absent(self, tools_dir: Path):
        actions = build_script_actions(tools_dir)
        scripts = [a["script"] for a in actions]
        from menu import EXCLUDE_SCRIPTS
        for excluded in EXCLUDE_SCRIPTS:
            assert excluded not in scripts


# ---------------------------------------------------------------------------
# validate_param
# ---------------------------------------------------------------------------

class TestValidateParam:
    def test_required_empty_fails(self):
        ok, _ = validate_param("", {"required": True, "type": "string"})
        assert not ok

    def test_required_non_empty_passes(self):
        ok, _ = validate_param("hello", {"required": True, "type": "string"})
        assert ok

    def test_optional_empty_passes(self):
        ok, _ = validate_param("", {"required": False, "type": "string"})
        assert ok

    def test_int_valid(self):
        ok, _ = validate_param("42", {"required": False, "type": "int"})
        assert ok

    def test_int_invalid(self):
        ok, _ = validate_param("abc", {"required": False, "type": "int"})
        assert not ok

    def test_choice_valid(self):
        ok, _ = validate_param("a", {"required": False, "type": "choice", "choices": ["a", "b"]})
        assert ok

    def test_choice_invalid(self):
        ok, _ = validate_param("z", {"required": False, "type": "choice", "choices": ["a", "b"]})
        assert not ok


# ---------------------------------------------------------------------------
# collect_parameters
# ---------------------------------------------------------------------------

class TestCollectParameters:
    def test_workspace_uses_default(self):
        action = {
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": "."},
            ]
        }
        values = collect_parameters(action, "/my/workspace")
        assert values["workspace"] == "/my/workspace"

    def test_optional_request_id_skipped_without_default(self):
        action = {
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True, "default": "."},
                {"name": "request_id", "flag": "--request-id", "type": "string", "required": False},
            ]
        }
        values = collect_parameters(action, ".")
        assert "request_id" not in values

    def test_string_param_collected_via_input(self):
        action = {
            "parameters": [
                {"name": "title", "flag": "--title", "type": "string", "required": True, "prompt": "Title"},
            ]
        }
        with patch("builtins.input", return_value="My Title"):
            values = collect_parameters(action, ".")
        assert values["title"] == "My Title"


# ---------------------------------------------------------------------------
# build_command
# ---------------------------------------------------------------------------

class TestBuildCommand:
    def test_builds_correct_command(self, tools_dir: Path):
        action = {
            "script": "create-request.py",
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True},
                {"name": "title", "flag": "--title", "type": "string", "required": True},
            ],
        }
        values = {"workspace": "/ws", "title": "My Request"}
        cmd = build_command(sys.executable if True else "", tools_dir, action, values)
        import sys as _sys
        cmd = build_command(_sys.executable, tools_dir, action, values)
        assert "--workspace" in cmd
        assert "/ws" in cmd
        assert "--title" in cmd
        assert "My Request" in cmd

    def test_omits_parameters_not_in_values(self, tools_dir: Path):
        action = {
            "script": "create-request.py",
            "parameters": [
                {"name": "workspace", "flag": "--workspace", "type": "path", "required": True},
                {"name": "title", "flag": "--title", "type": "string", "required": False},
            ],
        }
        import sys as _sys
        cmd = build_command(_sys.executable, tools_dir, action, {"workspace": "."})
        assert "--title" not in cmd


# ---------------------------------------------------------------------------
# _sanitize_action_id
# ---------------------------------------------------------------------------

class TestSanitizeActionId:
    def test_basic(self):
        assert _sanitize_action_id("create-request.py") == "create-request-py"

    def test_spaces_and_special(self):
        assert _sanitize_action_id("My Action!") == "my-action"

    def test_empty(self):
        assert _sanitize_action_id("") == ""


# ---------------------------------------------------------------------------
# _make_log_path
# ---------------------------------------------------------------------------

class TestMakeLogPath:
    def test_creates_log_in_logs_dir(self, tmp_path: Path):
        log = _make_log_path("test-action", tmp_path)
        assert log.parent == tmp_path / ".aib_memory" / "logs"
        assert log.name.startswith("aib-action-")
        assert "test-action" in log.name
        assert log.suffix == ".log"

    def test_creates_logs_directory(self, tmp_path: Path):
        log = _make_log_path("test-action", tmp_path)
        assert (tmp_path / ".aib_memory" / "logs").is_dir()


# ---------------------------------------------------------------------------
# _run_and_tee
# ---------------------------------------------------------------------------

class TestRunAndTee:
    def test_streams_stdout_to_log_file(self, tmp_path: Path):
        log_path = tmp_path / "test.log"
        script = tmp_path / "echo_script.py"
        script.write_text(
            'import sys\nfor i in range(3):\n    print(f"line {i}")\n',
            encoding="utf-8",
        )
        exit_code = _run_and_tee(
            [sys.executable, str(script)],
            log_path,
            "test echo",
            inherit_stdin=False,
        )
        assert exit_code == 0
        content = log_path.read_text(encoding="utf-8")
        assert "[START]" in content
        assert "[OUT] line 0" in content
        assert "[OUT] line 1" in content
        assert "[OUT] line 2" in content
        assert "[EXIT] 0" in content

    def test_streams_stderr_to_log_file(self, tmp_path: Path):
        log_path = tmp_path / "test.log"
        script = tmp_path / "err_script.py"
        script.write_text(
            'import sys\nsys.stderr.write("error line\\n")\nsys.exit(1)\n',
            encoding="utf-8",
        )
        exit_code = _run_and_tee(
            [sys.executable, str(script)],
            log_path,
            "test stderr",
            inherit_stdin=False,
        )
        assert exit_code == 1
        content = log_path.read_text(encoding="utf-8")
        assert "[ERR] error line" in content
        assert "[EXIT] 1" in content

    def test_returns_nonzero_exit_code(self, tmp_path: Path):
        log_path = tmp_path / "test.log"
        script = tmp_path / "fail_script.py"
        script.write_text("import sys; sys.exit(42)\n", encoding="utf-8")
        exit_code = _run_and_tee(
            [sys.executable, str(script)],
            log_path,
            "test fail",
            inherit_stdin=False,
        )
        assert exit_code == 42

    def test_log_file_contains_command(self, tmp_path: Path):
        log_path = tmp_path / "test.log"
        script = tmp_path / "noop.py"
        script.write_text("pass\n", encoding="utf-8")
        _run_and_tee(
            [sys.executable, str(script)],
            log_path,
            "test cmd",
            inherit_stdin=False,
        )
        content = log_path.read_text(encoding="utf-8")
        assert "[CMD]" in content

    def test_inherit_stdin_passes_none(self, tmp_path: Path):
        log_path = tmp_path / "test.log"
        script = tmp_path / "noop.py"
        script.write_text("pass\n", encoding="utf-8")
        with patch("subprocess.Popen", wraps=subprocess.Popen) as mock_popen:
            _run_and_tee(
                [sys.executable, str(script)],
                log_path,
                "test stdin",
                inherit_stdin=True,
            )
        _, kwargs = mock_popen.call_args
        assert kwargs["stdin"] is None

    def test_no_inherit_stdin_passes_devnull(self, tmp_path: Path):
        log_path = tmp_path / "test.log"
        script = tmp_path / "noop.py"
        script.write_text("pass\n", encoding="utf-8")
        with patch("subprocess.Popen", wraps=subprocess.Popen) as mock_popen:
            _run_and_tee(
                [sys.executable, str(script)],
                log_path,
                "test stdin off",
                inherit_stdin=False,
            )
        _, kwargs = mock_popen.call_args
        assert kwargs["stdin"] == subprocess.DEVNULL

    def test_utf8_non_ascii_output_logged_correctly(self, tmp_path: Path):
        """Subprocess emitting multi-byte UTF-8 characters is logged without error."""
        import threading as _threading

        log_path = tmp_path / "test.log"
        script = tmp_path / "utf8_script.py"
        # '→' (U+2192) is 3 bytes in UTF-8 (0xE2 0x86 0x92); 0x86 is undefined in cp1252.
        script.write_text(
            'import sys\nsys.stdout.buffer.write("arrow \\u2192\\n".encode("utf-8"))\n',
            encoding="utf-8",
        )
        exit_code = _run_and_tee(
            [sys.executable, str(script)],
            log_path,
            "test utf8 non-ascii",
            inherit_stdin=False,
        )
        assert exit_code == 0
        content = log_path.read_text(encoding="utf-8")
        assert "[OUT] arrow \u2192" in content
        assert "[EXIT] 0" in content

    def test_thread_exception_captured_in_log(self, tmp_path: Path):
        """A pipe raising UnicodeDecodeError in _stream_pipe writes [THREAD-ERROR] to log."""
        import threading as _threading

        log_path = tmp_path / "test.log"
        lock = _threading.Lock()

        class FailingPipe:
            def readline(self):
                raise UnicodeDecodeError(
                    "charmap", b"\x8f", 0, 1, "character maps to <undefined>"
                )

            def close(self):
                pass

        with open(log_path, "w", encoding="utf-8") as log_file:
            menu._stream_pipe(FailingPipe(), sys.stdout, log_file, "[OUT]", lock)

        content = log_path.read_text(encoding="utf-8")
        assert "[THREAD-ERROR]" in content
        assert "UnicodeDecodeError" in content

    def test_exit_marker_present_when_thread_fails(self, tmp_path: Path):
        """[EXIT] is written even when a streaming thread raises an exception."""
        log_path = tmp_path / "test.log"

        class FailingPipe:
            def readline(self):
                raise UnicodeDecodeError(
                    "charmap", b"\x8f", 0, 1, "character maps to <undefined>"
                )

            def close(self):
                pass

        mock_proc = MagicMock()
        mock_proc.stdout = FailingPipe()
        mock_proc.stderr = FailingPipe()
        mock_proc.wait.return_value = 0
        mock_proc.returncode = 0

        with patch("subprocess.Popen", return_value=mock_proc):
            exit_code = _run_and_tee(
                ["copilot", "-p", "test.md"],
                log_path,
                "test exit with thread error",
                inherit_stdin=False,
            )

        content = log_path.read_text(encoding="utf-8")
        assert "[THREAD-ERROR]" in content
        assert "[EXIT]" in content
        assert exit_code == 0




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
    _detect_guidance_state,
    _is_context_empty,
    _make_log_path,
    _run_and_tee,
    _sanitize_action_id,
    build_command,
    build_script_actions,
    collect_parameters,
    filter_visible_actions,
    render_menu,
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


# ---------------------------------------------------------------------------
# Hard-coded action list (SC-03, SC-04, SC-10, SC-11)
# ---------------------------------------------------------------------------

class TestHardCodedActionList:
    """Verify the explicit hard-coded menu action list requirements."""

    def test_move_request_artifacts_absent(self, tools_dir: Path):
        """SC-03: move-request-artifacts.py must never appear in the action list."""
        actions = build_script_actions(tools_dir)
        scripts = [a["script"] for a in actions]
        assert "move-request-artifacts.py" not in scripts

    def test_no_glob_discovery(self, tools_dir: Path):
        """SC-04: build_script_actions must not return auto-discovered scripts."""
        actions = build_script_actions(tools_dir)
        # Hard-coded list is intentionally empty; no auto-discovered scripts.
        assert len(actions) == 0

    def test_exclude_scripts_not_in_module(self):
        """SC-11: EXCLUDE_SCRIPTS must not exist in menu module."""
        import menu as _menu
        assert not hasattr(_menu, "EXCLUDE_SCRIPTS")


# ---------------------------------------------------------------------------
# State-aware guidance (_detect_guidance_state)  (SC-05 to SC-17)
# ---------------------------------------------------------------------------

_INPUT_MD_SEED = (
    "## Active request\n"
    "No active request\n\n"
    "## Options\n\n"
    "## Input\n\n"
)

_INPUT_MD_WITH_CONTENT = (
    "## Active request\n"
    "R-20260101-1000 \u2014 My Request\n\n"
    "## Options\n\n"
    "## Input\n"
    "Do something useful.\n"
)

_INPUT_MD_WITH_QUESTIONS = (
    "## Active request\n"
    "R-20260101-1000 \u2014 My Request\n\n"
    "## Questions\n"
    "Q1: Which approach?\n\n"
    "## Input\n\n"
)


def _make_input_md(tmp_path: Path, content: str) -> None:
    mem = tmp_path / ".aib_memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "input.md").write_text(content, encoding="utf-8")


def _make_request_md(tmp_path: Path, req_id: str = "R-20260101-1000") -> None:
    # Create the ID-suffixed active-phase plan artifact so _detect_guidance_state can find it.
    (tmp_path / ".aib_memory" / f"plan-{req_id}.md").write_text("# Plan\n", encoding="utf-8")


class TestDetectGuidanceState:
    """Unit tests for _detect_guidance_state covering all seven workspace states."""

    def test_idle_no_active_request_empty_input(self, tmp_path: Path):
        """SC-05: No active request + empty Input section → 'idle'."""
        _make_input_md(tmp_path, _INPUT_MD_SEED)
        state = MenuState(None, None)
        result = _detect_guidance_state(state, tmp_path)
        assert result == "idle"

    def test_idle_when_input_md_absent(self, tmp_path: Path):
        """No active request + no input.md → 'idle'."""
        (tmp_path / ".aib_memory").mkdir(parents=True, exist_ok=True)
        state = MenuState(None, None)
        result = _detect_guidance_state(state, tmp_path)
        assert result == "idle"

    def test_input_ready_no_active_request_with_content(self, tmp_path: Path):
        """SC-06: No active request + substantive Input content → 'input_ready'."""
        _make_input_md(tmp_path, _INPUT_MD_WITH_CONTENT)
        state = MenuState(None, None)
        result = _detect_guidance_state(state, tmp_path)
        assert result == "input_ready"

    def test_request_incomplete_active_no_request_md_empty_input(self, tmp_path: Path):
        """SC-07: Active request + no plan.md + empty Input → 'request_incomplete'."""
        _make_input_md(tmp_path, _INPUT_MD_SEED)
        state = MenuState("R-20260101-1000", ".aib_memory/requests/R-20260101-1000")
        result = _detect_guidance_state(state, tmp_path)
        assert result == "request_incomplete"

    def test_implementation_ready_active_request_md_present_empty_input(self, tmp_path: Path):
        """SC-08: Active request + plan.md present + empty Input + no questions → 'implementation_ready'."""
        _make_input_md(tmp_path, _INPUT_MD_SEED)
        _make_request_md(tmp_path)
        state = MenuState("R-20260101-1000", ".aib_memory/requests/R-20260101-1000")
        result = _detect_guidance_state(state, tmp_path)
        assert result == "implementation_ready"

    def test_questions_pending_active_with_questions(self, tmp_path: Path):
        """SC-12: Active request + non-empty Questions section → 'questions_pending' (priority)."""
        _make_input_md(tmp_path, _INPUT_MD_WITH_QUESTIONS)
        state = MenuState("R-20260101-1000", ".aib_memory/requests/R-20260101-1000")
        result = _detect_guidance_state(state, tmp_path)
        assert result == "questions_pending"

    def test_questions_pending_priority_over_request_md_absence(self, tmp_path: Path):
        """SC-12: questions_pending detected even when plan.md is absent."""
        _make_input_md(tmp_path, _INPUT_MD_WITH_QUESTIONS)
        # No plan.md created — questions_pending must still take priority.
        state = MenuState("R-20260101-1000", ".aib_memory/requests/R-20260101-1000")
        result = _detect_guidance_state(state, tmp_path)
        assert result == "questions_pending"

    def test_questions_not_pending_when_section_empty(self, tmp_path: Path):
        """SC-13: Empty Questions section must NOT trigger questions_pending."""
        content = (
            "## Active request\nR-001 — My Request\n\n"
            "## Questions\n\n"
            "## Input\n\n"
        )
        _make_input_md(tmp_path, content)
        _make_request_md(tmp_path)
        state = MenuState("R-20260101-1000", ".aib_memory/requests/R-20260101-1000")
        result = _detect_guidance_state(state, tmp_path)
        assert result == "implementation_ready"

    def test_amendment_pending_active_request_md_present_with_input(self, tmp_path: Path):
        """SC-14: Active request + plan.md present + substantive Input + no questions → 'amendment_pending'."""
        content = (
            "## Active request\nR-001 — My Request\n\n"
            "## Questions\n\n"
            "## Input\n"
            "Add a new feature.\n"
        )
        _make_input_md(tmp_path, content)
        _make_request_md(tmp_path)
        state = MenuState("R-20260101-1000", ".aib_memory/requests/R-20260101-1000")
        result = _detect_guidance_state(state, tmp_path)
        assert result == "amendment_pending"

    def test_unknown_returned_on_exception(self, tmp_path: Path):
        """SC-15: Any unhandled exception during detection must return 'unknown'."""
        _make_input_md(tmp_path, _INPUT_MD_SEED)
        state = MenuState("R-20260101-1000", ".aib_memory/requests/R-20260101-1000")
        with patch("menu._extract_section", side_effect=OSError("disk error")):
            result = _detect_guidance_state(state, tmp_path)
        assert result == "unknown"


# ---------------------------------------------------------------------------
# _GUIDANCE_MESSAGES key set (SC-17)
# ---------------------------------------------------------------------------

class TestGuidanceMessagesKeys:
    def test_exactly_seven_keys(self):
        """SC-17: _GUIDANCE_MESSAGES must have exactly the seven specified keys."""
        import menu as _menu
        expected = {
            "idle", "input_ready", "request_incomplete", "questions_pending",
            "implementation_ready", "amendment_pending", "unknown",
        }
        assert set(_menu._GUIDANCE_MESSAGES.keys()) == expected


# ---------------------------------------------------------------------------
# _is_context_empty and render_menu guidance block (SC-16)
# ---------------------------------------------------------------------------

class TestIsContextEmpty:
    def test_absent_context_returns_true(self, tmp_path: Path):
        (tmp_path / ".aib_memory").mkdir(parents=True, exist_ok=True)
        assert _is_context_empty(tmp_path) is True

    def test_empty_context_returns_true(self, tmp_path: Path):
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "context.md").write_text("   \n", encoding="utf-8")
        assert _is_context_empty(tmp_path) is True

    def test_non_empty_context_returns_false(self, tmp_path: Path):
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "context.md").write_text("# Product Context\n\nSome content.\n", encoding="utf-8")
        assert _is_context_empty(tmp_path) is False


class TestRenderMenuGuidance:
    """SC-16: Verify the context-empty guidance line in render_menu output."""

    def _capture_menu(self, state: MenuState, workspace: Path) -> str:
        actions = build_script_actions(workspace / ".aib_brain" / "tools")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            render_menu(state, actions, 0, workspace)
            return mock_stdout.getvalue()

    def test_context_empty_line_shown_when_context_absent(self, tmp_path: Path):
        """SC-16: When context.md is absent, render_menu includes the context guidance line."""
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "input.md").write_text(_INPUT_MD_SEED, encoding="utf-8")
        state = MenuState(None, None)
        output = self._capture_menu(state, tmp_path)
        assert "aib-analyze.md" in output

    def test_context_empty_line_absent_when_context_present(self, tmp_path: Path):
        """SC-16: When context.md has content, no context guidance line is shown."""
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "input.md").write_text(_INPUT_MD_SEED, encoding="utf-8")
        (mem / "context.md").write_text("# Context\n\nSome product context.\n", encoding="utf-8")
        state = MenuState(None, None)
        output = self._capture_menu(state, tmp_path)
        assert "Context file is empty" not in output

    def test_no_prompts_block_in_render_menu(self, tmp_path: Path):
        """SC-01: render_menu must not contain the AIB Prompts copy-paste block."""
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "input.md").write_text(_INPUT_MD_SEED, encoding="utf-8")
        state = MenuState(None, None)
        output = self._capture_menu(state, tmp_path)
        assert "\u2500\u2500 AIB Prompts" not in output

    def test_no_refresh_action_in_render_menu(self, tmp_path: Path):
        """SC-02: render_menu must not contain a Refresh numbered action."""
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "input.md").write_text(_INPUT_MD_SEED, encoding="utf-8")
        state = MenuState(None, None)
        output = self._capture_menu(state, tmp_path)
        assert "Refresh" not in output

    def test_render_menu_guidance_before_options(self, tmp_path: Path):
        """SC-A3: Guidance block must appear before the numbered options list."""
        mem = tmp_path / ".aib_memory"
        mem.mkdir(parents=True, exist_ok=True)
        (mem / "input.md").write_text(_INPUT_MD_SEED, encoding="utf-8")
        state = MenuState(None, None)
        output = self._capture_menu(state, tmp_path)
        assert output.index("\u2500\u2500 Next Step \u2500\u2500") < output.index("0) Quit")

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
# check_version_compatibility
# ---------------------------------------------------------------------------

from menu import check_version_compatibility

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


class TestCheckVersionCompatibility:
    """Tests for the semver version-compatibility check introduced in request R-20260427-0858."""

    def _make_workspace(self, tmp_path: Path, brain_semver: str | None, memory_semver: str | None) -> Path:
        """Build a minimal workspace with the specified semver markers."""
        brain_dir = tmp_path / ".aib_brain"
        brain_dir.mkdir(parents=True)
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir(parents=True)
        if brain_semver:
            (brain_dir / brain_semver).touch()
        if memory_semver:
            (memory_dir / memory_semver).touch()
        return tmp_path

    def test_matching_versions_returns_true(self, tmp_path: Path):
        """SC-3: Matching semver markers → continue to normal menu (True returned)."""
        workspace = self._make_workspace(tmp_path, "v1.2.8", "v1.2.8")
        tools_dir = WORKSPACE_ROOT / ".aib_brain" / "tools"
        result = check_version_compatibility(workspace, sys.executable, tools_dir)
        assert result is True

    def test_missing_brain_semver_returns_true_with_warning(self, tmp_path: Path, capsys):
        """Unknown brain version → warn and return True (do not block startup)."""
        workspace = self._make_workspace(tmp_path, None, "v1.2.8")
        tools_dir = WORKSPACE_ROOT / ".aib_brain" / "tools"
        result = check_version_compatibility(workspace, sys.executable, tools_dir)
        assert result is True
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_mismatch_shows_prompt_skip_returns_true(self, tmp_path: Path):
        """SC-4 / SC-7: Version mismatch with skip choice → return True, no files changed."""
        workspace = self._make_workspace(tmp_path, "v1.2.8", "v1.2.0")
        tools_dir = WORKSPACE_ROOT / ".aib_brain" / "tools"
        with patch("builtins.input", return_value="2"):
            result = check_version_compatibility(workspace, sys.executable, tools_dir)
        assert result is True
        # No archive should have been created when user skips.
        assert not (workspace / ".aib_memory" / "archives").exists()

    def test_mismatch_missing_memory_semver_shows_prompt(self, tmp_path: Path):
        """SC-4: No memory semver marker → show upgrade prompt."""
        workspace = self._make_workspace(tmp_path, "v1.2.8", None)
        tools_dir = WORKSPACE_ROOT / ".aib_brain" / "tools"
        with patch("builtins.input", return_value="2"):
            result = check_version_compatibility(workspace, sys.executable, tools_dir)
        assert result is True

    def test_invalid_then_valid_choice_loops(self, tmp_path: Path):
        """Invalid input is rejected and the prompt re-displays until valid input."""
        workspace = self._make_workspace(tmp_path, "v1.2.8", "v1.0.0")
        tools_dir = WORKSPACE_ROOT / ".aib_brain" / "tools"
        with patch("builtins.input", side_effect=["x", "2"]):
            result = check_version_compatibility(workspace, sys.executable, tools_dir)
        assert result is True

    def test_upgrade_choice_continues_menu(self, tmp_path: Path):
        """SC-2: After a successful upgrade, check_version_compatibility returns True (menu continues)."""
        workspace = self._make_workspace(tmp_path, "v1.2.8", "v1.0.0")
        tools_dir = WORKSPACE_ROOT / ".aib_brain" / "tools"
        # Mock subprocess.run to simulate a successful upgrade without running initialize.py.
        with patch("menu.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("builtins.input", return_value="1"):
                result = check_version_compatibility(workspace, sys.executable, tools_dir)
        assert result is True

    def test_failed_upgrade_returns_false(self, tmp_path: Path):
        """A failed upgrade causes check_version_compatibility to return False."""
        workspace = self._make_workspace(tmp_path, "v1.2.8", "v1.0.0")
        tools_dir = WORKSPACE_ROOT / ".aib_brain" / "tools"
        with patch("menu.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            with patch("builtins.input", return_value="1"):
                result = check_version_compatibility(workspace, sys.executable, tools_dir)
        assert result is False



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


# ---------------------------------------------------------------------------
# choose_action — UP/DOWN zero-division guard (SC-06)
# ---------------------------------------------------------------------------

class TestChooseActionZeroDivisionGuard:
    """Verify that choose_action does not raise ZeroDivisionError when total_items == 0."""

    def _make_workspace(self, tmp_path: Path) -> Path:
        """Set up a minimal workspace with no active request (so action list is empty)."""
        brain_dir = tmp_path / ".aib_brain"
        brain_dir.mkdir(parents=True)
        mem_dir = tmp_path / ".aib_memory"
        mem_dir.mkdir(parents=True)
        reg = mem_dir / "requests_register.md"
        reg.write_text(
            "# Requests Register\n\n"
            "| request_id | title | folder | state | created_at | closed_at |\n"
            "| --- | --- | --- | --- | --- | --- |\n",
            encoding="utf-8",
        )
        (mem_dir / "input.md").write_text(
            "## Active request\nNo active request\n\n## Options\n\n## Input\n\n",
            encoding="utf-8",
        )
        return tmp_path

    def test_up_key_with_zero_items_no_zerodivision(self, tmp_path: Path):
        """UP key pressed when total_items == 0 must not raise ZeroDivisionError."""
        workspace = self._make_workspace(tmp_path)
        tools_dir = workspace / ".aib_brain" / "tools"
        # Provide key sequence: UP then QUIT to exit the loop.
        keys = iter(["UP", "QUIT"])
        with patch("menu.get_key", side_effect=lambda **_: next(keys)):
            with patch("menu.render_menu"):
                result = menu.choose_action(tools_dir, workspace)
        assert result is None  # QUIT returns None

    def test_down_key_with_zero_items_no_zerodivision(self, tmp_path: Path):
        """DOWN key pressed when total_items == 0 must not raise ZeroDivisionError."""
        workspace = self._make_workspace(tmp_path)
        tools_dir = workspace / ".aib_brain" / "tools"
        keys = iter(["DOWN", "QUIT"])
        with patch("menu.get_key", side_effect=lambda **_: next(keys)):
            with patch("menu.render_menu"):
                result = menu.choose_action(tools_dir, workspace)
        assert result is None


# ---------------------------------------------------------------------------
# Guidance messages — attachments hint (SC-5, SC-6)
# ---------------------------------------------------------------------------

class TestGuidanceAttachmentsHint:
    """Verify that idle and implementation_ready guidance messages include an attachments reminder."""

    def test_idle_guidance_contains_attachments_reminder(self) -> None:
        """'idle' guidance must contain at least one line referencing 'attachments'."""
        assert any("attachments" in line for line in menu._GUIDANCE_MESSAGES["idle"]), (
            "_GUIDANCE_MESSAGES['idle'] must include a line referencing '.aib_memory/attachments/'."
        )

    def test_implementation_ready_guidance_contains_attachments_reminder(self) -> None:
        """'implementation_ready' guidance must contain at least one line referencing 'attachments'."""
        assert any(
            "attachments" in line for line in menu._GUIDANCE_MESSAGES["implementation_ready"]
        ), (
            "_GUIDANCE_MESSAGES['implementation_ready'] must include a line referencing "
            "'.aib_memory/attachments/'."
        )

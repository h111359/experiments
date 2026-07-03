"""
test_log_entry.py: Tests for .aib_brain/tools/log-entry.py.
Part of the AIB test suite.
Responsibilities: validate log file creation, entry format, --general mode,
and CLI error handling for the audit logging tool.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = WORKSPACE_ROOT / ".aib_brain" / "tools" / "log-entry.py"

_TIMESTAMP_PATTERN = re.compile(r"^\d{8}-\d{6}:")


def _make_workspace(tmp: str, request_id: str | None = "R-20260101-1200", title: str = "Test") -> Path:
    """Create a minimal AIB workspace with optional active request state."""
    ws = Path(tmp)
    (ws / ".aib_brain").mkdir(parents=True, exist_ok=True)
    memory = ws / ".aib_memory"
    memory.mkdir(parents=True, exist_ok=True)

    if request_id:
        input_content = (
            "---\n"
            "state:\n"
            f"  request_id: {request_id}\n"
            f"  title: {title}\n"
            "  status: analysis_ready\n"
            "  input_verification_result: null\n"
            "  context_verification_result: null\n"
            "options:\n"
            "  minimum_questions: 5\n"
            "  input_verification_enabled: true\n"
            "  context_verification_enabled: true\n"
            "---\n\n"
            "## Input\n\n"
        )
    else:
        input_content = (
            "---\n"
            "state:\n"
            "  request_id: ~\n"
            "  title: ~\n"
            "  status: idle\n"
            "  input_verification_result: null\n"
            "  context_verification_result: null\n"
            "options:\n"
            "  minimum_questions: 5\n"
            "  input_verification_enabled: true\n"
            "  context_verification_enabled: true\n"
            "---\n\n"
            "## Input\n\n"
        )
    (memory / "input.md").write_text(input_content, encoding="utf-8")
    return ws


def _run_log_entry(
    workspace: Path,
    message: str,
    general: bool = False,
) -> subprocess.CompletedProcess:
    """Run log-entry.py against the given workspace.

    Args:
        workspace: Path to workspace root.
        message: Log message string.
        general: When True, passes the --general flag.

    Returns:
        CompletedProcess with stdout, stderr, and returncode.
    """
    cmd = [sys.executable, str(SCRIPT_PATH), "--workspace", str(workspace), "--message", message]
    if general:
        cmd.append("--general")
    return subprocess.run(cmd, capture_output=True, text=True)


class TestLogEntryNormalMode:
    """Tests for log-entry.py in normal (request-scoped) mode."""

    def test_creates_log_file_for_active_request(self, tmp_path: Path) -> None:
        """Normal mode must create log_<request_id>.md in .aib_memory/."""
        ws = _make_workspace(str(tmp_path), request_id="R-20260101-1200")
        result = _run_log_entry(ws, "Step 1 started")
        assert result.returncode == 0, f"Expected exit 0.\n{result.stderr}"
        log_file = ws / ".aib_memory" / "log_R-20260101-1200.md"
        assert log_file.exists(), "Log file must be created for an active request"

    def test_log_entry_format(self, tmp_path: Path) -> None:
        """Each log entry must match the YYYYMMDD-HHmmss: <message> format."""
        ws = _make_workspace(str(tmp_path), request_id="R-20260101-1200")
        _run_log_entry(ws, "Test message")
        log_file = ws / ".aib_memory" / "log_R-20260101-1200.md"
        content = log_file.read_text(encoding="utf-8")
        lines = [ln for ln in content.splitlines() if ln.strip()]
        assert lines, "Log file must contain at least one non-blank line"
        assert _TIMESTAMP_PATTERN.match(lines[-1]), (
            f"Last entry must match YYYYMMDD-HHmmss: pattern, got: {lines[-1]!r}"
        )
        assert "Test message" in lines[-1], "Message must appear in the log entry"

    def test_multiple_entries_appended(self, tmp_path: Path) -> None:
        """Successive calls must append entries rather than overwrite."""
        ws = _make_workspace(str(tmp_path), request_id="R-20260101-1200")
        _run_log_entry(ws, "Entry one")
        _run_log_entry(ws, "Entry two")
        log_file = ws / ".aib_memory" / "log_R-20260101-1200.md"
        content = log_file.read_text(encoding="utf-8")
        assert "Entry one" in content
        assert "Entry two" in content

    def test_fails_when_state_idle(self, tmp_path: Path) -> None:
        """Normal mode must exit non-zero when input.md state is idle (no active request)."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        result = _run_log_entry(ws, "Should fail")
        assert result.returncode != 0, "Must fail when no active request"


class TestLogEntryGeneralMode:
    """Tests for log-entry.py --general mode."""

    def test_creates_log_general_file(self, tmp_path: Path) -> None:
        """--general mode must create log_general.md in .aib_memory/."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        result = _run_log_entry(ws, "General log entry", general=True)
        assert result.returncode == 0, f"Expected exit 0.\n{result.stderr}"
        log_file = ws / ".aib_memory" / "log_general.md"
        assert log_file.exists(), "log_general.md must be created in --general mode"

    def test_general_mode_works_when_idle(self, tmp_path: Path) -> None:
        """--general mode must succeed even when no active request (idle state)."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        result = _run_log_entry(ws, "Phase 1 complete", general=True)
        assert result.returncode == 0

    def test_general_entry_format(self, tmp_path: Path) -> None:
        """General log entries must match the YYYYMMDD-HHmmss: <message> format."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        _run_log_entry(ws, "Phase check", general=True)
        log_file = ws / ".aib_memory" / "log_general.md"
        content = log_file.read_text(encoding="utf-8")
        lines = [ln for ln in content.splitlines() if ln.strip()]
        assert lines, "General log file must contain at least one non-blank line"
        assert _TIMESTAMP_PATTERN.match(lines[-1]), (
            f"Entry must match YYYYMMDD-HHmmss: pattern, got: {lines[-1]!r}"
        )


class TestLogEntryCliErrors:
    """Tests for CLI error handling in log-entry.py."""

    def test_missing_workspace_fails(self, tmp_path: Path) -> None:
        """An invalid workspace path (no .aib_brain/) must produce a non-zero exit code."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--workspace", str(tmp_path), "--message", "test"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_missing_message_fails(self, tmp_path: Path) -> None:
        """Omitting --message must produce a non-zero exit code."""
        ws = _make_workspace(str(tmp_path), request_id="R-20260101-1200")
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--workspace", str(ws)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

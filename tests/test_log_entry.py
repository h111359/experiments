"""
test_log_entry.py: Tests for .aib_brain/tools/log-entry.py.
Part of the AIB test suite.
Responsibilities: validate that log-entry.py is a state-independent appender to
.aib_memory/log.md, enforces the UTC entry format, echoes to stdout, and rejects
the removed --general flag.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = WORKSPACE_ROOT / ".aib_brain" / "tools" / "log-entry.py"

_TIMESTAMP_PATTERN = re.compile(r"^\d{8}-\d{6}:")
_ACTIVE_LOG_NAME = "log.md"

# The literal historical flag token that MUST be rejected. Referenced here so
# tests/test_no_general_flag.py can whitelist this exact assertion location.
_REJECTED_FLAG = "--general"


def _make_workspace(tmp: str, request_id: str | None = "R-20260101-1200", title: str = "Test") -> Path:
    """Create a minimal AIB workspace with optional active-request state."""
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
    extra_args: tuple[str, ...] = (),
) -> subprocess.CompletedProcess:
    """Run log-entry.py against the given workspace.

    Args:
        workspace: Path to workspace root.
        message: Log message string.
        extra_args: Additional command-line arguments passed through unchanged.

    Returns:
        CompletedProcess with stdout, stderr, and returncode.
    """
    cmd = [
        sys.executable,
        str(SCRIPT_PATH),
        "--workspace",
        str(workspace),
        "--message",
        message,
        *extra_args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


class TestSharedLogAppender:
    """Tests for the state-independent shared-log appender contract."""

    def test_creates_log_md_when_idle(self, tmp_path: Path) -> None:
        """log-entry.py must create .aib_memory/log.md when the workspace is idle."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        result = _run_log_entry(ws, "Idle-state entry")
        assert result.returncode == 0, f"Expected exit 0.\n{result.stderr}"
        log_file = ws / ".aib_memory" / _ACTIVE_LOG_NAME
        assert log_file.exists(), "log.md must be created on first invocation when idle"

    def test_creates_log_md_when_active(self, tmp_path: Path) -> None:
        """log-entry.py must create .aib_memory/log.md when a request is active."""
        ws = _make_workspace(str(tmp_path), request_id="R-20260101-1200")
        result = _run_log_entry(ws, "Active-state entry")
        assert result.returncode == 0, f"Expected exit 0.\n{result.stderr}"
        log_file = ws / ".aib_memory" / _ACTIVE_LOG_NAME
        assert log_file.exists(), "log.md must be created when a request is active"

    def test_lazy_first_write_when_absent(self, tmp_path: Path) -> None:
        """log.md must not exist before the first invocation and must appear afterwards."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        log_file = ws / ".aib_memory" / _ACTIVE_LOG_NAME
        assert not log_file.exists(), "log.md must be absent before first invocation"
        _run_log_entry(ws, "First write")
        assert log_file.exists(), "log.md must be created lazily on the first invocation"

    def test_entry_format_matches_utc_pattern(self, tmp_path: Path) -> None:
        """Each entry must match the YYYYMMDD-HHmmss: <message> format."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        _run_log_entry(ws, "Format sample")
        log_file = ws / ".aib_memory" / _ACTIVE_LOG_NAME
        line = log_file.read_text(encoding="utf-8").splitlines()[-1]
        assert _TIMESTAMP_PATTERN.match(line), f"Bad entry format: {line!r}"
        assert line.endswith("Format sample"), "Message text must terminate the entry"

    def test_entries_appended_in_chronological_order(self, tmp_path: Path) -> None:
        """Multiple invocations must preserve chronological append order."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        for msg in ("Entry one", "Entry two", "Entry three"):
            _run_log_entry(ws, msg)
        content = (ws / ".aib_memory" / _ACTIVE_LOG_NAME).read_text(encoding="utf-8")
        idx_one = content.index("Entry one")
        idx_two = content.index("Entry two")
        idx_three = content.index("Entry three")
        assert idx_one < idx_two < idx_three, "Entries must be appended in call order"

    def test_stdout_echoes_written_entry(self, tmp_path: Path) -> None:
        """log-entry.py must echo the written entry to stdout."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        result = _run_log_entry(ws, "Echo sample")
        assert result.returncode == 0
        assert "Echo sample" in result.stdout
        assert _TIMESTAMP_PATTERN.match(result.stdout.strip()), (
            "Echoed stdout must start with the UTC timestamp prefix"
        )

    def test_utf8_message_round_trip(self, tmp_path: Path) -> None:
        """Non-ASCII UTF-8 content in --message must round-trip through the file."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        message = "Мессаж: こんにちは — café"
        result = _run_log_entry(ws, message)
        assert result.returncode == 0, f"Expected exit 0.\n{result.stderr}"
        content = (ws / ".aib_memory" / _ACTIVE_LOG_NAME).read_text(encoding="utf-8")
        assert message in content, "UTF-8 message must be preserved verbatim on disk"


class TestGeneralFlagRejection:
    """log-entry.py MUST reject the removed --general flag via argparse."""

    def test_general_flag_rejected(self, tmp_path: Path) -> None:
        """Passing --general must produce a non-zero exit with an unrecognized-argument error."""
        ws = _make_workspace(str(tmp_path), request_id=None)
        result = _run_log_entry(ws, "Should fail", extra_args=(_REJECTED_FLAG,))
        assert result.returncode != 0, "argparse must reject the removed flag"
        # argparse writes the unrecognized-arguments error to stderr.
        assert "unrecognized arguments" in result.stderr.lower(), (
            f"Expected argparse rejection message; got stderr: {result.stderr!r}"
        )


class TestLegacyLogFilesUntouched:
    """log-entry.py MUST NOT read, write, or remove legacy log files at .aib_memory/ root."""

    def test_pre_existing_legacy_files_preserved(self, tmp_path: Path) -> None:
        """Pre-existing log_general.md and log_<request_id>.md files must be preserved verbatim."""
        ws = _make_workspace(str(tmp_path), request_id="R-20260101-1200")
        memory = ws / ".aib_memory"
        legacy_general = memory / "log_general.md"
        legacy_request = memory / "log_R-20260101-1200.md"
        legacy_general.write_text("old general contents\n", encoding="utf-8")
        legacy_request.write_text("old request contents\n", encoding="utf-8")

        result = _run_log_entry(ws, "New shared entry")
        assert result.returncode == 0, f"Expected exit 0.\n{result.stderr}"

        assert legacy_general.read_text(encoding="utf-8") == "old general contents\n"
        assert legacy_request.read_text(encoding="utf-8") == "old request contents\n"
        shared = memory / _ACTIVE_LOG_NAME
        assert shared.exists() and "New shared entry" in shared.read_text(encoding="utf-8")


class TestLogEntryCliErrors:
    """CLI error handling in log-entry.py."""

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


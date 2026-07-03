"""Integration tests for .aib_brain/tools/close-request.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from common import parse_input_header, read_text, write_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INPUT_MD_IDLE = (
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


def _make_request(workspace: Path, req_id: str, state: str = "analysis_ready") -> Path:
    """Create a request folder and set the input.md YAML header to the given state."""
    folder_name = f"{req_id}-test-request"
    folder_rel = f".aib_memory/requests/{folder_name}"
    folder = workspace / folder_rel
    folder.mkdir(parents=True, exist_ok=True)

    input_path = workspace / ".aib_memory" / "input.md"
    # Use idle header as base if file exists, else create fresh.
    base_content = read_text(input_path) if input_path.exists() else INPUT_MD_IDLE
    from common import parse_input_header, write_input_header
    hdr = parse_input_header(base_content) or {
        "state": {"request_id": "~", "title": "~", "status": "idle",
                  "input_verification_result": None, "context_verification_result": None},
        "options": {"minimum_questions": 0, "input_verification_enabled": True,
                    "context_verification_enabled": True},
    }
    hdr["state"]["request_id"] = req_id
    hdr["state"]["title"] = "Test Request"
    hdr["state"]["status"] = state
    write_text(input_path, write_input_header(base_content, hdr))

    # Write a minimal plan.md stub
    plan_md = (
        "## Goal\n\n"
        "## Constraints\n\n"
        "## Success criteria\n"
    )
    write_text(folder / "plan.md", plan_md)
    return folder


def _load_script(name: str):
    tools = Path(__file__).resolve().parent.parent / ".aib_brain" / "tools"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), tools / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_close_request(workspace: Path, request_id: str | None = None) -> int:
    args = ["--workspace", str(workspace)]
    if request_id:
        args += ["--request-id", request_id]
    old_argv = sys.argv[:]
    sys.argv = ["close-request.py"] + args
    try:
        mod = _load_script("close-request.py")
        mod.main()
        return 0
    except SystemExit as e:
        return int(e.code) if e.code is not None else 0
    finally:
        sys.argv = old_argv


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCloseRequest:
    def test_closes_active_request(self, workspace_dir: Path):
        _make_request(workspace_dir, "R-20260101-1000")
        rc = _run_close_request(workspace_dir)
        assert rc == 0
        from common import parse_input_header, read_text
        header = parse_input_header(read_text(workspace_dir / ".aib_memory" / "input.md"))
        assert header["state"]["status"] == "idle"
        assert header["state"]["request_id"] == "~"

    def test_close_resets_title_to_null(self, workspace_dir: Path):
        _make_request(workspace_dir, "R-20260101-1001")
        _run_close_request(workspace_dir)
        from common import parse_input_header, read_text
        header = parse_input_header(read_text(workspace_dir / ".aib_memory" / "input.md"))
        assert header["state"]["title"] == "~"

    def test_already_idle_request_fails(self, workspace_dir: Path):
        # If state is already idle, close-request.py must exit non-zero.
        rc = _run_close_request(workspace_dir)
        assert rc != 0

    def test_no_active_request_fails(self, workspace_dir: Path):
        # Register is idle — no active request
        rc = _run_close_request(workspace_dir)
        assert rc != 0

    def test_explicit_request_id_closes_correct_request(self, workspace_dir: Path):
        _make_request(workspace_dir, "R-20260101-1004")
        rc = _run_close_request(workspace_dir, "R-20260101-1004")
        assert rc == 0
        from common import parse_input_header, read_text
        header = parse_input_header(read_text(workspace_dir / ".aib_memory" / "input.md"))
        assert header["state"]["status"] == "idle"

    def test_resets_input_md_to_idle_when_exists(self, workspace_dir: Path):
        """After closing, input.md YAML header is reset to idle state."""
        _make_request(workspace_dir, "R-20260101-1005")
        input_path = workspace_dir / ".aib_memory" / "input.md"
        rc = _run_close_request(workspace_dir)
        assert rc == 0
        from common import parse_input_header, read_text
        header = parse_input_header(read_text(input_path))
        assert header is not None
        assert header["state"]["status"] == "idle"
        assert header["state"]["request_id"] == "~"
        assert "R-20260101-1005" not in read_text(input_path)

    def test_fails_when_input_md_missing(self, workspace_dir: Path):
        """Closing a request fails when input.md does not exist (new behavior: input.md required)."""
        _make_request(workspace_dir, "R-20260101-1006")
        input_path = workspace_dir / ".aib_memory" / "input.md"
        if input_path.exists():
            input_path.unlink()
        rc = _run_close_request(workspace_dir)
        assert rc != 0

    def test_warns_when_attachments_nonempty(self, workspace_dir: Path, capsys):
        """SC-5: close-request.py prints a warning (non-blocking) when attachments/ is non-empty."""
        _make_request(workspace_dir, "R-20260101-1007")
        attachments_dir = workspace_dir / ".aib_memory" / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)
        # Place a developer file (not .gitkeep) to trigger the warning.
        (attachments_dir / "spec.pdf").write_bytes(b"dummy")
        rc = _run_close_request(workspace_dir)
        assert rc == 0, "close-request.py must exit 0 even with non-empty attachments/"
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "attachments" in captured.out

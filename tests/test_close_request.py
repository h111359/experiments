"""Integration tests for .aib_brain/tools/close-request.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from common import format_markdown_table, parse_markdown_table, read_text, write_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_HEADER = ["request_id", "title", "folder", "state", "created_at", "closed_at"]


def _make_request(workspace: Path, req_id: str, state: str = "Active") -> Path:
    folder_name = f"{req_id}-test-request"
    folder_rel = f".aib_memory/requests/{folder_name}"
    folder = workspace / folder_rel
    folder.mkdir(parents=True, exist_ok=True)

    reg_path = workspace / ".aib_memory" / "requests_register.md"
    content = read_text(reg_path)
    header, rows = parse_markdown_table(content)
    if not header:
        header = REGISTER_HEADER
    rows.append([req_id, "Test Request", folder_rel, state, "2026-01-01 10:00:00 +0000", ""])
    write_text(reg_path, "# Requests Register\n\n" + format_markdown_table(header, rows))

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
        reg_content = read_text(workspace_dir / ".aib_memory" / "requests_register.md")
        header, rows = parse_markdown_table(reg_content)
        col = {n: i for i, n in enumerate(header)}
        matching = [r for r in rows if r[col["request_id"]] == "R-20260101-1000"]
        assert matching[0][col["state"]] == "Closed"

    def test_closed_at_is_set(self, workspace_dir: Path):
        _make_request(workspace_dir, "R-20260101-1001")
        _run_close_request(workspace_dir)
        reg = read_text(workspace_dir / ".aib_memory" / "requests_register.md")
        header, rows = parse_markdown_table(reg)
        col = {n: i for i, n in enumerate(header)}
        matching = [r for r in rows if r[col["request_id"]] == "R-20260101-1001"]
        assert matching[0][col["closed_at"]] != ""

    def test_already_closed_request_fails(self, workspace_dir: Path):
        _make_request(workspace_dir, "R-20260101-1003", state="Closed")
        rc = _run_close_request(workspace_dir, "R-20260101-1003")
        assert rc != 0

    def test_no_active_request_fails(self, workspace_dir: Path):
        # Register is empty — no rows at all
        rc = _run_close_request(workspace_dir)
        assert rc != 0

    def test_explicit_request_id_closes_correct_request(self, workspace_dir: Path):
        _make_request(workspace_dir, "R-20260101-1004")
        rc = _run_close_request(workspace_dir, "R-20260101-1004")
        assert rc == 0
        reg = read_text(workspace_dir / ".aib_memory" / "requests_register.md")
        header, rows = parse_markdown_table(reg)
        col = {n: i for i, n in enumerate(header)}
        matching = [r for r in rows if r[col["request_id"]] == "R-20260101-1004"]
        assert matching[0][col["state"]] == "Closed"

    def test_resets_input_md_when_exists(self, workspace_dir: Path):
        """After closing, input.md is reset to seed template with 'No active request'."""
        _make_request(workspace_dir, "R-20260101-1005")
        input_path = workspace_dir / ".aib_memory" / "input.md"
        write_text(input_path, "## Status\nR-20260101-1005 \u2014 Test Request\nState: analysis_ready\n\n## Options\n\n## Input\nSome old content\n")
        rc = _run_close_request(workspace_dir)
        assert rc == 0
        content = read_text(input_path)
        assert "No active request" in content
        assert "Question threshold" not in content
        assert "R-20260101-1005" not in content
        assert "## Status" in content
        assert "State: idle" in content

    def test_does_not_fail_when_input_md_missing(self, workspace_dir: Path):
        """Closing a request succeeds silently when input.md does not exist."""
        _make_request(workspace_dir, "R-20260101-1006")
        input_path = workspace_dir / ".aib_memory" / "input.md"
        if input_path.exists():
            input_path.unlink()
        rc = _run_close_request(workspace_dir)
        assert rc == 0
        assert not input_path.exists()

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

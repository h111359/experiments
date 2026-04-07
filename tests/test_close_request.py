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
ITER_HEADER = ["iteration_id", "state", "created_at", "closed_at", "summary"]


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

    # Write a minimal request.md stub satisfying validate_request_md
    request_md = (
        "# Request\n\n"
        "## Goal\n\n"
        "## Background\n\n"
        "## Scope\n\n"
        "## Out of scope\n\n"
        "## Constraints\n\n"
        "## Success criteria\n"
    )
    write_text(folder / "request.md", request_md)
    write_text(
        folder / "iterations.md",
        "# Iterations\n\n" + format_markdown_table(ITER_HEADER, [["01", "Completed", "2026-01-01 10:00:00 +0000", "2026-01-01 11:00:00 +0000", "Initial"]]),
    )
    return folder


def _add_active_iteration(request_folder: Path) -> None:
    iter_path = request_folder / "iterations.md"
    content = read_text(iter_path)
    header, rows = parse_markdown_table(content)
    if not header:
        header = ITER_HEADER
    rows = [r for r in rows if r[1] != "Active"]
    rows.append(["02", "Active", "2026-01-01 12:00:00 +0000", "", "Follow-up"])
    write_text(iter_path, "# Iterations\n\n" + format_markdown_table(header, rows))


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

    def test_auto_closes_active_iteration(self, workspace_dir: Path):
        folder = _make_request(workspace_dir, "R-20260101-1002")
        _add_active_iteration(folder)
        rc = _run_close_request(workspace_dir)
        assert rc == 0
        iter_content = read_text(folder / "iterations.md")
        assert "Active" not in iter_content

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

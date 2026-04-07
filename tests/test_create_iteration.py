"""Integration tests for .aib_brain/tools/create-iteration.py."""

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


def _seed_request(workspace: Path, req_id: str, state: str = "Active") -> Path:
    folder_name = f"{req_id}-test"
    folder_rel = f".aib_memory/requests/{folder_name}"
    folder = workspace / folder_rel
    folder.mkdir(parents=True, exist_ok=True)

    reg_path = workspace / ".aib_memory" / "requests_register.md"
    content = read_text(reg_path)
    header, rows = parse_markdown_table(content)
    if not header:
        header = REGISTER_HEADER
    rows.append([req_id, "Test", folder_rel, state, "2026-01-01 10:00:00 +0000", ""])
    write_text(reg_path, "# Requests Register\n\n" + format_markdown_table(header, rows))

    write_text(
        folder / "iterations.md",
        "# Iterations\n\n" + format_markdown_table(
            ITER_HEADER,
            [["01", "Completed", "2026-01-01 10:00:00 +0000", "2026-01-01 11:00:00 +0000", "Initial"]],
        ),
    )
    return folder


def _seed_request_with_active_iter(workspace: Path, req_id: str) -> Path:
    folder = _seed_request(workspace, req_id)
    iter_path = folder / "iterations.md"
    header, rows = parse_markdown_table(read_text(iter_path))
    rows[-1][1] = "Active"
    rows[-1][3] = ""
    write_text(iter_path, "# Iterations\n\n" + format_markdown_table(header, rows))
    return folder


def _load_script(name: str):
    tools = Path(__file__).resolve().parent.parent / ".aib_brain" / "tools"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), tools / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_create_iteration(workspace: Path, request_id: str | None = None, summary: str = "") -> int:
    args = ["--workspace", str(workspace)]
    if request_id:
        args += ["--request-id", request_id]
    if summary:
        args += ["--summary", summary]
    old_argv = sys.argv[:]
    sys.argv = ["create-iteration.py"] + args
    try:
        mod = _load_script("create-iteration.py")
        mod.main()
        return 0
    except SystemExit as e:
        return int(e.code) if e.code is not None else 0
    finally:
        sys.argv = old_argv


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCreateIteration:
    def test_creates_next_iteration_with_ascending_id(self, workspace_dir: Path):
        _seed_request(workspace_dir, "R-20260101-1000")
        rc = _run_create_iteration(workspace_dir)
        assert rc == 0
        folder = workspace_dir / ".aib_memory" / "requests" / "R-20260101-1000-test"
        header, rows = parse_markdown_table(read_text(folder / "iterations.md"))
        col = {n: i for i, n in enumerate(header)}
        ids = [int(r[col["iteration_id"]]) for r in rows]
        assert ids == sorted(ids)
        assert max(ids) == 2

    def test_new_iteration_is_active(self, workspace_dir: Path):
        _seed_request(workspace_dir, "R-20260101-1001")
        _run_create_iteration(workspace_dir)
        folder = workspace_dir / ".aib_memory" / "requests" / "R-20260101-1001-test"
        header, rows = parse_markdown_table(read_text(folder / "iterations.md"))
        col = {n: i for i, n in enumerate(header)}
        active = [r for r in rows if r[col["state"]] == "Active"]
        assert len(active) == 1
        assert active[0][col["iteration_id"]] == "02"

    def test_previous_active_iter_is_completed(self, workspace_dir: Path):
        folder = _seed_request_with_active_iter(workspace_dir, "R-20260101-1002")
        rc = _run_create_iteration(workspace_dir)
        assert rc == 0
        header, rows = parse_markdown_table(read_text(folder / "iterations.md"))
        col = {n: i for i, n in enumerate(header)}
        completed = [r for r in rows if r[col["state"]] == "Completed"]
        assert any(r[col["iteration_id"]] == "01" for r in completed)

    def test_no_active_request_fails(self, workspace_dir: Path):
        rc = _run_create_iteration(workspace_dir)
        assert rc != 0

    def test_summary_stored_in_iteration(self, workspace_dir: Path):
        _seed_request(workspace_dir, "R-20260101-1003")
        _run_create_iteration(workspace_dir, summary="My summary")
        folder = workspace_dir / ".aib_memory" / "requests" / "R-20260101-1003-test"
        content = read_text(folder / "iterations.md")
        assert "My summary" in content

"""Integration tests for .aib_brain/tools/close-iteration.py."""

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


def _seed_request_with_iterations(workspace: Path, req_id: str, iterations: list[list[str]]) -> Path:
    folder_name = f"{req_id}-test"
    folder_rel = f".aib_memory/requests/{folder_name}"
    folder = workspace / folder_rel
    folder.mkdir(parents=True, exist_ok=True)

    reg_path = workspace / ".aib_memory" / "requests_register.md"
    content = read_text(reg_path)
    header, rows = parse_markdown_table(content)
    if not header:
        header = REGISTER_HEADER
    rows.append([req_id, "Test", folder_rel, "Active", "2026-01-01 10:00:00 +0000", ""])
    write_text(reg_path, "# Requests Register\n\n" + format_markdown_table(header, rows))

    write_text(
        folder / "iterations.md",
        "# Iterations\n\n" + format_markdown_table(ITER_HEADER, iterations),
    )
    return folder


def _load_script(name: str):
    tools = Path(__file__).resolve().parent.parent / ".aib_brain" / "tools"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), tools / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_close_iteration(
    workspace: Path,
    request_id: str | None = None,
    iteration_id: str | None = None,
) -> int:
    args = ["--workspace", str(workspace)]
    if request_id:
        args += ["--request-id", request_id]
    if iteration_id:
        args += ["--iteration-id", iteration_id]
    old_argv = sys.argv[:]
    sys.argv = ["close-iteration.py"] + args
    try:
        mod = _load_script("close-iteration.py")
        mod.main()
        return 0
    except SystemExit as e:
        return int(e.code) if e.code is not None else 0
    finally:
        sys.argv = old_argv


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCloseIteration:
    def test_closes_active_iteration_state_becomes_completed(self, workspace_dir: Path):
        folder = _seed_request_with_iterations(
            workspace_dir,
            "R-20260101-1000",
            [["01", "Active", "2026-01-01 10:00:00 +0000", "", "Initial"]],
        )
        rc = _run_close_iteration(workspace_dir)
        assert rc == 0
        header, rows = parse_markdown_table(read_text(folder / "iterations.md"))
        col = {n: i for i, n in enumerate(header)}
        assert rows[0][col["state"]] == "Completed"

    def test_closed_at_is_set(self, workspace_dir: Path):
        folder = _seed_request_with_iterations(
            workspace_dir,
            "R-20260101-1001",
            [["01", "Active", "2026-01-01 10:00:00 +0000", "", "Initial"]],
        )
        _run_close_iteration(workspace_dir)
        header, rows = parse_markdown_table(read_text(folder / "iterations.md"))
        col = {n: i for i, n in enumerate(header)}
        assert rows[0][col["closed_at"]] != ""

    def test_explicit_iteration_id_closes_correct_iteration(self, workspace_dir: Path):
        folder = _seed_request_with_iterations(
            workspace_dir,
            "R-20260101-1002",
            [
                ["01", "Completed", "2026-01-01 10:00:00 +0000", "2026-01-01 11:00:00 +0000", "Initial"],
                ["02", "Active", "2026-01-01 12:00:00 +0000", "", "Follow-up"],
            ],
        )
        rc = _run_close_iteration(workspace_dir, iteration_id="02")
        assert rc == 0
        header, rows = parse_markdown_table(read_text(folder / "iterations.md"))
        col = {n: i for i, n in enumerate(header)}
        row_02 = next(r for r in rows if r[col["iteration_id"]] == "02")
        assert row_02[col["state"]] == "Completed"

    def test_no_active_iteration_fails(self, workspace_dir: Path):
        _seed_request_with_iterations(
            workspace_dir,
            "R-20260101-1003",
            [["01", "Completed", "2026-01-01 10:00:00 +0000", "2026-01-01 11:00:00 +0000", "Initial"]],
        )
        rc = _run_close_iteration(workspace_dir)
        assert rc != 0

    def test_missing_iteration_id_explicit_fails(self, workspace_dir: Path):
        _seed_request_with_iterations(
            workspace_dir,
            "R-20260101-1004",
            [["01", "Active", "2026-01-01 10:00:00 +0000", "", "Initial"]],
        )
        rc = _run_close_iteration(workspace_dir, iteration_id="99")
        assert rc != 0

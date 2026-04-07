"""Integration tests for .aib_brain/tools/create-request.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import helper for hyphenated module names
# ---------------------------------------------------------------------------

def _load_script(name: str):
    tools = Path(__file__).resolve().parent.parent / ".aib_brain" / "tools"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), tools / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_create_request(workspace: Path, title: str, request_id: str | None = None) -> int:
    """Run create-request.py as subprocess-like call via its main(). Returns exit code."""
    args = ["--workspace", str(workspace), "--title", title]
    if request_id:
        args += ["--request-id", request_id]
    import sys as _sys
    old_argv = _sys.argv[:]
    _sys.argv = ["create-request.py"] + args
    try:
        mod = _load_script("create-request.py")
        mod.main()
        return 0
    except SystemExit as e:
        return int(e.code) if e.code is not None else 0
    finally:
        _sys.argv = old_argv


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCreateRequest:
    def test_successful_creation_produces_folder(self, workspace_dir: Path):
        rc = _run_create_request(workspace_dir, "My new request", "R-20260101-1000")
        assert rc == 0
        folder = workspace_dir / ".aib_memory" / "requests" / "R-20260101-1000-my-new-request"
        assert folder.is_dir()

    def test_successful_creation_writes_request_md(self, workspace_dir: Path):
        _run_create_request(workspace_dir, "Another request", "R-20260101-1001")
        folder = workspace_dir / ".aib_memory" / "requests" / "R-20260101-1001-another-request"
        assert (folder / "request.md").is_file()

    def test_successful_creation_writes_iterations_md(self, workspace_dir: Path):
        _run_create_request(workspace_dir, "Request With Iter", "R-20260101-1002")
        folder = workspace_dir / ".aib_memory" / "requests" / "R-20260101-1002-request-with-iter"
        content = (folder / "iterations.md").read_text(encoding="utf-8")
        assert "01" in content
        assert "Active" in content

    def test_successful_creation_updates_register(self, workspace_dir: Path):
        _run_create_request(workspace_dir, "Register Check", "R-20260101-1003")
        reg = (workspace_dir / ".aib_memory" / "requests_register.md").read_text(encoding="utf-8")
        assert "R-20260101-1003" in reg
        assert "Active" in reg

    def test_missing_title_fails(self, workspace_dir: Path):
        rc = _run_create_request(workspace_dir, "")
        assert rc != 0

    def test_duplicate_active_request_fails(self, workspace_dir: Path):
        rc1 = _run_create_request(workspace_dir, "First request", "R-20260101-1004")
        assert rc1 == 0
        rc2 = _run_create_request(workspace_dir, "Second request", "R-20260101-1005")
        assert rc2 != 0

    def test_missing_register_fails(self, workspace_dir: Path):
        (workspace_dir / ".aib_memory" / "requests_register.md").unlink()
        rc = _run_create_request(workspace_dir, "Orphan request")
        assert rc != 0

    def test_register_row_has_active_state(self, workspace_dir: Path):
        _run_create_request(workspace_dir, "State Check", "R-20260101-1006")
        from common import parse_markdown_table, read_text
        reg_path = workspace_dir / ".aib_memory" / "requests_register.md"
        header, rows = parse_markdown_table(read_text(reg_path))
        col = {n: i for i, n in enumerate(header)}
        active_rows = [r for r in rows if r[col["request_id"]] == "R-20260101-1006"]
        assert len(active_rows) == 1
        assert active_rows[0][col["state"]] == "Active"

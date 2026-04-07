"""Full lifecycle E2E test: initialize → create-request → create-iteration → close-iteration → close-request."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"
TEMPLATES_DIR = WORKSPACE_ROOT / ".aib_brain" / "templates"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_brain_only_workspace(root: Path) -> None:
    (root / ".aib_brain" / "templates").mkdir(parents=True, exist_ok=True)
    for tmpl in TEMPLATES_DIR.glob("*.md"):
        shutil.copy(tmpl, root / ".aib_brain" / "templates" / tmpl.name)


def _run(script_name: str, workspace: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    script_path = TOOLS_DIR / script_name
    cmd = [sys.executable, str(script_path), "--workspace", str(workspace)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


def _parse_register(workspace: Path):
    from common import parse_markdown_table, read_text
    reg = workspace / ".aib_memory" / "requests_register.md"
    return parse_markdown_table(read_text(reg))


def _parse_iterations(workspace: Path, folder_rel: str):
    from common import parse_markdown_table, read_text
    path = workspace / folder_rel / "iterations.md"
    return parse_markdown_table(read_text(path))


# ---------------------------------------------------------------------------
# E2E test
# ---------------------------------------------------------------------------

class TestLifecycleE2E:
    def test_full_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)

            # Step 1: initialize
            result = _run("initialize.py", root)
            assert result.returncode == 0, f"initialize failed: {result.stderr}"
            assert (root / ".aib_memory" / "requests_register.md").exists()

            # Step 2: create-request
            result = _run("create-request.py", root, ["--title", "E2E Test Request", "--request-id", "R-20260101-0001"])
            assert result.returncode == 0, f"create-request failed: {result.stderr}"
            header, rows = _parse_register(root)
            col = {n: i for i, n in enumerate(header)}
            req_rows = [r for r in rows if r[col["request_id"]] == "R-20260101-0001"]
            assert len(req_rows) == 1
            assert req_rows[0][col["state"]] == "Active"
            folder_rel = req_rows[0][col["folder"]]

            # Step 3: create-iteration
            result = _run("create-iteration.py", root, ["--summary", "E2E iteration"])
            assert result.returncode == 0, f"create-iteration failed: {result.stderr}"
            it_header, it_rows = _parse_iterations(root, folder_rel)
            it_col = {n: i for i, n in enumerate(it_header)}
            active_iters = [r for r in it_rows if r[it_col["state"]] == "Active"]
            assert len(active_iters) == 1
            new_iter_id = active_iters[0][it_col["iteration_id"]]
            assert int(new_iter_id) >= 1

            # Step 4: close-iteration
            result = _run("close-iteration.py", root)
            assert result.returncode == 0, f"close-iteration failed: {result.stderr}"
            _, it_rows2 = _parse_iterations(root, folder_rel)
            active_after = [r for r in it_rows2 if r[it_col["state"]] == "Active"]
            assert len(active_after) == 0

            # Step 5: close-request
            result = _run("close-request.py", root)
            assert result.returncode == 0, f"close-request failed: {result.stderr}"
            _, final_rows = _parse_register(root)
            req_row = next(r for r in final_rows if r[col["request_id"]] == "R-20260101-0001")
            assert req_row[col["state"]] == "Closed"
            assert req_row[col["closed_at"]] != ""

    def test_cannot_create_request_while_another_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run("initialize.py", root)
            r1 = _run("create-request.py", root, ["--title", "First", "--request-id", "R-20260101-0002"])
            assert r1.returncode == 0
            r2 = _run("create-request.py", root, ["--title", "Second", "--request-id", "R-20260101-0003"])
            assert r2.returncode != 0

    def test_close_request_auto_closes_active_iteration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run("initialize.py", root)
            _run("create-request.py", root, ["--title", "AutoClose", "--request-id", "R-20260101-0004"])
            _run("create-iteration.py", root, ["--summary", "Auto-close test"])
            result = _run("close-request.py", root)
            assert result.returncode == 0
            header, rows = _parse_register(root)
            col = {n: i for i, n in enumerate(header)}
            req_row = next(r for r in rows if r[col["request_id"]] == "R-20260101-0004")
            folder_rel = req_row[col["folder"]]
            _, it_rows = _parse_iterations(root, folder_rel)
            it_col_keys = ["iteration_id", "state", "created_at", "closed_at", "summary"]
            it_col = {n: i for i, n in enumerate(it_col_keys)}
            active_remaining = [r for r in it_rows if r[it_col["state"]] == "Active"]
            assert len(active_remaining) == 0

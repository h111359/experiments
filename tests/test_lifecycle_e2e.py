"""Full lifecycle E2E test: initialize → create-request → close-request."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_brain_only_workspace(root: Path) -> None:
    (root / ".aib_brain").mkdir(parents=True, exist_ok=True)


def _run(script_name: str, workspace: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    script_path = TOOLS_DIR / script_name
    cmd = [sys.executable, str(script_path), "--workspace", str(workspace)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


def _read_input_header(workspace: Path) -> dict:
    """Read the YAML frontmatter from input.md and return as a dict."""
    from common import read_input_header
    return read_input_header(workspace)


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
            assert (root / ".aib_memory" / "input.md").exists()
            header = _read_input_header(root)
            assert header["state"] == "idle"

            # Step 2: create-request
            result = _run("create-request.py", root, ["--title", "E2E Test Request", "--request-id", "R-20260101-0001"])
            assert result.returncode == 0, f"create-request failed: {result.stderr}"
            header = _read_input_header(root)
            assert header["request_id"] == "R-20260101-0001"
            assert header["state"] == "analysis_ready"
            folder_rel = f".aib_memory/requests/R-20260101-0001-e2e-test-request"
            assert not (root / folder_rel / "request.md").exists()
            assert not (root / folder_rel / "iterations.md").exists()

            # Step 3: close-request
            result = _run("close-request.py", root)
            assert result.returncode == 0, f"close-request failed: {result.stderr}"
            header = _read_input_header(root)
            assert header["state"] == "idle"
            assert header["request_id"] in (None, "~")

    def test_cannot_create_request_while_another_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run("initialize.py", root)
            r1 = _run("create-request.py", root, ["--title", "First", "--request-id", "R-20260101-0002"])
            assert r1.returncode == 0
            r2 = _run("create-request.py", root, ["--title", "Second", "--request-id", "R-20260101-0003"])
            assert r2.returncode != 0

    def test_close_request_succeeds_without_iterations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run("initialize.py", root)
            _run("create-request.py", root, ["--title", "SimpleClose", "--request-id", "R-20260101-0004"])
            result = _run("close-request.py", root)
            assert result.returncode == 0
            header = _read_input_header(root)
            assert header["state"] == "idle"

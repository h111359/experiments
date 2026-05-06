"""Tests for move-request-artifacts.py and close-request.py artifact placement behavior."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from common import (
    format_markdown_table,
    parse_markdown_table,
    read_text,
    write_text,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_HEADER = ["request_id", "title", "folder", "state", "created_at", "closed_at"]
TOOLS_DIR = Path(__file__).resolve().parent.parent / ".aib_brain" / "tools"


def _load_script(name: str):
    """Load a .aib_brain/tools script by filename, mapping hyphens to underscores for the module name."""
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), TOOLS_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_active_request(workspace: Path, req_id: str = "R-20260101-1000") -> Path:
    """Register an Active request and create its folder; return the folder Path."""
    folder_name = f"{req_id}-test-request"
    folder_rel = f".aib_memory/requests/{folder_name}"
    folder = workspace / folder_rel
    folder.mkdir(parents=True, exist_ok=True)

    reg_path = workspace / ".aib_memory" / "requests_register.md"
    content = read_text(reg_path)
    header, rows = parse_markdown_table(content)
    if not header:
        header = REGISTER_HEADER
    rows.append([req_id, "Test Request", folder_rel, "Active", "2026-01-01 10:00:00 +0000", ""])
    write_text(reg_path, "# Requests Register\n\n" + format_markdown_table(header, rows))
    return folder


def _run_move_artifacts(workspace: Path) -> int:
    """Run move-request-artifacts.py main() and return exit code."""
    old_argv = sys.argv[:]
    sys.argv = ["move-request-artifacts.py", "--workspace", str(workspace)]
    try:
        mod = _load_script("move-request-artifacts.py")
        mod.main()
        return 0
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    finally:
        sys.argv = old_argv


def _run_close_request(workspace: Path, request_id: str | None = None) -> int:
    """Run close-request.py main() and return exit code."""
    args = ["--workspace", str(workspace)]
    if request_id:
        args += ["--request-id", request_id]
    old_argv = sys.argv[:]
    sys.argv = ["close-request.py"] + args
    try:
        mod = _load_script("close-request.py")
        mod.main()
        return 0
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    finally:
        sys.argv = old_argv


# ---------------------------------------------------------------------------
# T1-T5: move-request-artifacts.py behavior
# ---------------------------------------------------------------------------

class TestMoveRequestArtifacts:
    def test_t1_moves_request_md(self, workspace_dir: Path):
        """T1: move script relocates request.md from .aib_memory/ to request subfolder."""
        folder = _make_active_request(workspace_dir)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / "request.md", "## Goal\nTest request content.\n")

        rc = _run_move_artifacts(workspace_dir)

        assert rc == 0
        assert not (aib_memory / "request.md").exists()
        assert (folder / "request.md").exists()
        assert "Test request content" in read_text(folder / "request.md")

    def test_t2_moves_analysis_md(self, workspace_dir: Path):
        """T2: move script relocates analysis.md from .aib_memory/ to request subfolder."""
        folder = _make_active_request(workspace_dir)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / "analysis.md", "# Analysis\nSome analysis content.\n")

        rc = _run_move_artifacts(workspace_dir)

        assert rc == 0
        assert not (aib_memory / "analysis.md").exists()
        assert (folder / "analysis.md").exists()
        assert "Some analysis content" in read_text(folder / "analysis.md")

    def test_t3_moves_uat_scenarios_md(self, workspace_dir: Path):
        """T3: move script relocates UAT_scenarios.md from .aib_memory/ to request subfolder."""
        folder = _make_active_request(workspace_dir)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / "UAT_scenarios.md", "# UAT Scenarios\nUAT-01: Scenario.\n")

        rc = _run_move_artifacts(workspace_dir)

        assert rc == 0
        assert not (aib_memory / "UAT_scenarios.md").exists()
        assert (folder / "UAT_scenarios.md").exists()

    def test_t4_skips_missing_uat_scenarios(self, workspace_dir: Path):
        """T4: move script skips UAT_scenarios.md without error when it does not exist."""
        _make_active_request(workspace_dir)
        aib_memory = workspace_dir / ".aib_memory"
        # Only request.md is present; UAT_scenarios.md is absent
        write_text(aib_memory / "request.md", "## Goal\nContent.\n")

        rc = _run_move_artifacts(workspace_dir)

        assert rc == 0
        assert not (aib_memory / "UAT_scenarios.md").exists()

    def test_t5_idempotent_second_call(self, workspace_dir: Path):
        """T5: calling move script twice exits cleanly on second call (no sources at root)."""
        folder = _make_active_request(workspace_dir)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / "request.md", "## Goal\nContent.\n")
        write_text(aib_memory / "analysis.md", "# Analysis\n")

        # First call moves the files
        rc1 = _run_move_artifacts(workspace_dir)
        assert rc1 == 0

        # Second call: no sources at root — should succeed without error
        rc2 = _run_move_artifacts(workspace_dir)
        assert rc2 == 0

        # Files remain in subfolder from first call
        assert (folder / "request.md").exists()
        assert (folder / "analysis.md").exists()


# ---------------------------------------------------------------------------
# T6-T7: close-request.py integration with move
# ---------------------------------------------------------------------------

class TestCloseRequestArtifactPlacement:
    def test_t6_close_moves_artifacts_to_request_folder(self, workspace_dir: Path):
        """T6: close-request.py moves artifacts from .aib_memory/ to request folder before closing."""
        folder = _make_active_request(workspace_dir, "R-20260102-1000")
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / "request.md", "## Goal\nClose integration test.\n")
        write_text(aib_memory / "analysis.md", "# Analysis\nClose integration analysis.\n")

        rc = _run_close_request(workspace_dir)

        assert rc == 0
        # Artifacts must be in the request subfolder
        assert (folder / "request.md").exists()
        assert (folder / "analysis.md").exists()
        # Artifacts must NOT remain at .aib_memory/ root
        assert not (aib_memory / "request.md").exists()
        assert not (aib_memory / "analysis.md").exists()

        # Request state must be Closed
        reg = read_text(workspace_dir / ".aib_memory" / "requests_register.md")
        header, rows = parse_markdown_table(reg)
        col = {n: i for i, n in enumerate(header)}
        matching = [r for r in rows if r[col["request_id"]] == "R-20260102-1000"]
        assert matching[0][col["state"]] == "Closed"

    def test_t7_close_completes_when_no_artifacts_at_root(self, workspace_dir: Path):
        """T7: close-request.py completes successfully when no artifacts exist at .aib_memory/ root."""
        _make_active_request(workspace_dir, "R-20260102-1001")
        aib_memory = workspace_dir / ".aib_memory"
        # No artifacts at root — simulates case where implement already moved them
        assert not (aib_memory / "request.md").exists()
        assert not (aib_memory / "analysis.md").exists()

        rc = _run_close_request(workspace_dir)

        assert rc == 0
        reg = read_text(workspace_dir / ".aib_memory" / "requests_register.md")
        header, rows = parse_markdown_table(reg)
        col = {n: i for i, n in enumerate(header)}
        matching = [r for r in rows if r[col["request_id"]] == "R-20260102-1001"]
        assert matching[0][col["state"]] == "Closed"

"""Tests for move-request-artifacts.py and close-request.py artifact placement behavior."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

from common import (
    parse_input_header,
    read_text,
    write_input_header,
    write_text,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOOLS_DIR = Path(__file__).resolve().parent.parent / ".aib_brain" / "tools"

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


def _load_script(name: str):
    """Load a .aib_brain/tools script by filename, mapping hyphens to underscores for the module name."""
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), TOOLS_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_active_request(workspace: Path, req_id: str = "R-20260101-1000") -> Path:
    """Register an Active request via YAML header and create its folder; return the folder Path."""
    folder_name = f"{req_id}-test-request"
    folder_rel = f".aib_memory/requests/{folder_name}"
    folder = workspace / folder_rel
    folder.mkdir(parents=True, exist_ok=True)

    input_path = workspace / ".aib_memory" / "input.md"
    base_content = read_text(input_path) if input_path.exists() else INPUT_MD_IDLE
    hdr = parse_input_header(base_content) or {
        "state": {"request_id": "~", "title": "~", "status": "idle",
                  "input_verification_result": None, "context_verification_result": None},
        "options": {"minimum_questions": 0, "input_verification_enabled": True,
                    "context_verification_enabled": True},
    }
    hdr["state"]["request_id"] = req_id
    hdr["state"]["title"] = "Test Request"
    hdr["state"]["status"] = "analysis_ready"
    write_text(input_path, write_input_header(base_content, hdr))
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
    def test_t1_moves_plan_md(self, workspace_dir: Path):
        """T1: move script relocates plan-<ID>.md from .aib_memory/ to request subfolder."""
        req_id = "R-20260101-1000"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / f"plan-{req_id}.md", "## Goal\nTest plan content.\n")

        rc = _run_move_artifacts(workspace_dir)

        assert rc == 0
        assert not (aib_memory / f"plan-{req_id}.md").exists()
        assert (folder / f"plan-{req_id}.md").exists()
        assert "Test plan content" in read_text(folder / f"plan-{req_id}.md")

    def test_t2_moves_analysis_md(self, workspace_dir: Path):
        """T2: move script relocates analysis-<ID>.md from .aib_memory/ to request subfolder."""
        req_id = "R-20260101-1000"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / f"analysis-{req_id}.md", "# Analysis\nSome analysis content.\n")

        rc = _run_move_artifacts(workspace_dir)

        assert rc == 0
        assert not (aib_memory / f"analysis-{req_id}.md").exists()
        assert (folder / f"analysis-{req_id}.md").exists()
        assert "Some analysis content" in read_text(folder / f"analysis-{req_id}.md")

    def test_t5_idempotent_second_call(self, workspace_dir: Path):
        """T5: calling move script twice exits cleanly on second call (no sources at root)."""
        req_id = "R-20260101-1000"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / f"plan-{req_id}.md", "## Goal\nContent.\n")
        write_text(aib_memory / f"analysis-{req_id}.md", "# Analysis\n")

        # First call moves the files
        rc1 = _run_move_artifacts(workspace_dir)
        assert rc1 == 0

        # Second call: no sources at root — should succeed without error
        rc2 = _run_move_artifacts(workspace_dir)
        assert rc2 == 0

        # Files remain in subfolder from first call
        assert (folder / f"plan-{req_id}.md").exists()
        assert (folder / f"analysis-{req_id}.md").exists()


# ---------------------------------------------------------------------------
# T6-T7: close-request.py integration with move
# ---------------------------------------------------------------------------

class TestCloseRequestArtifactPlacement:
    def test_t6_close_moves_artifacts_to_request_folder(self, workspace_dir: Path):
        """T6: close-request.py moves artifacts from .aib_memory/ to request folder before closing."""
        req_id = "R-20260102-1000"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        write_text(aib_memory / f"plan-{req_id}.md", "## Goal\nClose integration test.\n")
        write_text(aib_memory / f"analysis-{req_id}.md", "# Analysis\nClose integration analysis.\n")

        rc = _run_close_request(workspace_dir)

        assert rc == 0
        # Artifacts must be in the request subfolder (ID-suffixed names)
        assert (folder / f"plan-{req_id}.md").exists()
        assert (folder / f"analysis-{req_id}.md").exists()
        # ID-suffixed artifacts must NOT remain at .aib_memory/ root
        assert not (aib_memory / f"plan-{req_id}.md").exists()
        assert not (aib_memory / f"analysis-{req_id}.md").exists()

        # Request state must be idle (closed)
        header = parse_input_header(read_text(workspace_dir / ".aib_memory" / "input.md"))
        assert header["state"]["status"] == "idle"

    def test_t7_close_completes_when_no_artifacts_at_root(self, workspace_dir: Path):
        """T7: close-request.py completes successfully when no artifacts exist at .aib_memory/ root."""
        req_id = "R-20260102-1001"
        _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        # No artifacts at root — simulates case where implement already moved them
        assert not (aib_memory / f"plan-{req_id}.md").exists()
        assert not (aib_memory / f"analysis-{req_id}.md").exists()

        rc = _run_close_request(workspace_dir)

        assert rc == 0

        # Request state must be idle (closed)
        header = parse_input_header(read_text(workspace_dir / ".aib_memory" / "input.md"))
        assert header["state"]["status"] == "idle"


# ---------------------------------------------------------------------------
# Shared-log archival transaction (move-request-artifacts.py)
# ---------------------------------------------------------------------------


ACTIVE_LOG_NAME = "log.md"


def _archive_log_path(folder: Path, req_id: str) -> Path:
    """Return the per-request archive file path used by the shared-log rotation."""
    return folder / f"log_{req_id}.md"


def _try_create_symlink(link_path: Path, target: Path) -> bool:
    """Attempt to create a symlink; return False on OSes/permissions that reject it."""
    try:
        os.symlink(target, link_path)
        return True
    except (OSError, NotImplementedError):
        return False


class TestSharedLogArchival:
    """move-request-artifacts.py archives .aib_memory/log.md into the request subfolder."""

    def test_archive_byte_equal_when_no_prior_archive(self, workspace_dir: Path) -> None:
        """Non-empty active log with no prior archive lands byte-equal at the archive path."""
        req_id = "R-20260201-1000"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        payload = b"20260201-100000: first\n20260201-100005: second\n"
        (aib_memory / ACTIVE_LOG_NAME).write_bytes(payload)

        rc = _run_move_artifacts(workspace_dir)
        assert rc == 0

        archive = _archive_log_path(folder, req_id)
        assert archive.exists()
        assert archive.read_bytes() == payload
        active = aib_memory / ACTIVE_LOG_NAME
        assert active.exists() and active.read_bytes() == b""

    def test_archive_appends_with_newline_separator_when_missing(self, workspace_dir: Path) -> None:
        """Non-empty prior archive without trailing newline gets exactly one \\n separator."""
        req_id = "R-20260201-1001"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        archive = _archive_log_path(folder, req_id)
        # Archive without a trailing newline.
        archive.write_bytes(b"20260201-090000: prior")
        (aib_memory / ACTIVE_LOG_NAME).write_bytes(b"20260201-100000: new\n")

        rc = _run_move_artifacts(workspace_dir)
        assert rc == 0

        assert archive.read_bytes() == b"20260201-090000: prior\n20260201-100000: new\n"

    def test_archive_does_not_add_separator_when_trailing_newline_present(
        self, workspace_dir: Path
    ) -> None:
        """Archive already ending in \\n receives snapshot without an additional separator."""
        req_id = "R-20260201-1002"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        archive = _archive_log_path(folder, req_id)
        archive.write_bytes(b"20260201-090000: prior\n")
        (aib_memory / ACTIVE_LOG_NAME).write_bytes(b"20260201-100000: new\n")

        rc = _run_move_artifacts(workspace_dir)
        assert rc == 0

        assert archive.read_bytes() == b"20260201-090000: prior\n20260201-100000: new\n"

    def test_absent_root_log_creates_empty_archive(self, workspace_dir: Path) -> None:
        """When .aib_memory/log.md is absent and no prior archive exists, create empty archive."""
        req_id = "R-20260201-1003"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        assert not (aib_memory / ACTIVE_LOG_NAME).exists()

        rc = _run_move_artifacts(workspace_dir)
        assert rc == 0

        archive = _archive_log_path(folder, req_id)
        assert archive.exists()
        assert archive.read_bytes() == b""

    def test_empty_root_log_leaves_archive_empty_and_resets_active(
        self, workspace_dir: Path
    ) -> None:
        """Empty root log is a no-op for archive contents but still leaves an empty active log."""
        req_id = "R-20260201-1004"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        (aib_memory / ACTIVE_LOG_NAME).write_bytes(b"")

        rc = _run_move_artifacts(workspace_dir)
        assert rc == 0

        archive = _archive_log_path(folder, req_id)
        assert archive.exists() and archive.read_bytes() == b""
        active = aib_memory / ACTIVE_LOG_NAME
        assert active.exists() and active.read_bytes() == b""

    def test_double_invocation_is_idempotent(self, workspace_dir: Path) -> None:
        """Two consecutive move_artifacts calls produce the same final state as one."""
        req_id = "R-20260201-1005"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        (aib_memory / ACTIVE_LOG_NAME).write_text("20260201-100000: first\n", encoding="utf-8")

        rc1 = _run_move_artifacts(workspace_dir)
        assert rc1 == 0
        archive_after_first = _archive_log_path(folder, req_id).read_bytes()

        rc2 = _run_move_artifacts(workspace_dir)
        assert rc2 == 0
        archive_after_second = _archive_log_path(folder, req_id).read_bytes()

        assert archive_after_first == archive_after_second
        active = aib_memory / ACTIVE_LOG_NAME
        assert active.exists() and active.read_bytes() == b""

    def test_leftover_staging_file_is_drained(self, workspace_dir: Path) -> None:
        """A staging file from a simulated aborted prior run is drained into the archive."""
        req_id = "R-20260201-1006"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        # Simulate an aborted prior run: staging file is present, root log absent.
        staging = aib_memory / f"log-staging-{req_id}.md"
        staging.write_text("20260201-080000: pre-crash entry\n", encoding="utf-8")

        rc = _run_move_artifacts(workspace_dir)
        assert rc == 0

        archive = _archive_log_path(folder, req_id)
        assert archive.exists()
        assert "pre-crash entry" in archive.read_text(encoding="utf-8")
        assert not staging.exists(), "Staging file must be removed after successful drain"

    def test_directory_at_active_log_path_blocks_operation(self, workspace_dir: Path) -> None:
        """A directory at .aib_memory/log.md blocks the archival transaction."""
        req_id = "R-20260201-1007"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        (aib_memory / ACTIVE_LOG_NAME).mkdir()

        rc = _run_move_artifacts(workspace_dir)
        assert rc != 0
        # No archive should be produced when the active-log path type is invalid.
        assert not _archive_log_path(folder, req_id).exists()

    def test_directory_at_archive_path_blocks_operation(self, workspace_dir: Path) -> None:
        """A directory at the archive path blocks the archival transaction."""
        req_id = "R-20260201-1008"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        (aib_memory / ACTIVE_LOG_NAME).write_text("20260201-100000: active\n", encoding="utf-8")
        _archive_log_path(folder, req_id).mkdir()

        rc = _run_move_artifacts(workspace_dir)
        assert rc != 0
        # Active log must remain untouched when archival is refused.
        assert (aib_memory / ACTIVE_LOG_NAME).read_text(encoding="utf-8") == "20260201-100000: active\n"

    def test_symlink_at_active_log_blocks_operation(self, workspace_dir: Path) -> None:
        """A symlink at .aib_memory/log.md blocks the archival transaction; skip on OSes that reject symlink creation."""
        req_id = "R-20260201-1009"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        target = aib_memory / "log-target.txt"
        target.write_text("target\n", encoding="utf-8")
        link = aib_memory / ACTIVE_LOG_NAME
        if not _try_create_symlink(link, target):
            pytest.skip("Symlink creation not permitted on this platform")

        rc = _run_move_artifacts(workspace_dir)
        assert rc != 0
        # Target file and the symlink itself remain untouched.
        assert target.read_text(encoding="utf-8") == "target\n"
        assert link.is_symlink()

    def test_symlink_at_archive_path_blocks_operation(self, workspace_dir: Path) -> None:
        """A symlink at the archive path blocks the archival transaction."""
        req_id = "R-20260201-1010"
        folder = _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        (aib_memory / ACTIVE_LOG_NAME).write_text("20260201-100000: active\n", encoding="utf-8")
        target = folder / "other-target.txt"
        target.write_text("target\n", encoding="utf-8")
        link = _archive_log_path(folder, req_id)
        if not _try_create_symlink(link, target):
            pytest.skip("Symlink creation not permitted on this platform")

        rc = _run_move_artifacts(workspace_dir)
        assert rc != 0
        # Active log remains untouched when archival is refused.
        assert (aib_memory / ACTIVE_LOG_NAME).read_text(encoding="utf-8") == "20260201-100000: active\n"

    def test_legacy_log_general_preserved_verbatim(self, workspace_dir: Path) -> None:
        """A pre-existing .aib_memory/log_general.md file must not be touched by archival."""
        req_id = "R-20260201-1011"
        _make_active_request(workspace_dir, req_id)
        aib_memory = workspace_dir / ".aib_memory"
        legacy = aib_memory / "log_general.md"
        legacy.write_text("legacy-general\n", encoding="utf-8")
        (aib_memory / ACTIVE_LOG_NAME).write_text("20260201-100000: active\n", encoding="utf-8")

        rc = _run_move_artifacts(workspace_dir)
        assert rc == 0

        assert legacy.exists()
        assert legacy.read_text(encoding="utf-8") == "legacy-general\n"

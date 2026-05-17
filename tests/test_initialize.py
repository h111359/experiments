"""Integration tests for .aib_brain/tools/initialize.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), TOOLS_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_brain_only_workspace(root: Path) -> None:
    """Create workspace with .aib_brain/ but no .aib_memory/."""
    (root / ".aib_brain").mkdir(parents=True, exist_ok=True)


def _make_brain_with_semver(root: Path, semver: str = "v1.2.8") -> None:
    """Create a brain-only workspace that also includes a semver marker file."""
    _make_brain_only_workspace(root)
    (root / ".aib_brain" / semver).touch()


def _run_initialize(workspace: Path, force: bool = False, upgrade: bool = False) -> int:
    args = ["--workspace", str(workspace)]
    if force:
        args.append("--force")
    if upgrade:
        args.append("--upgrade")
    old_argv = sys.argv[:]
    sys.argv = ["initialize.py"] + args
    try:
        mod = _load_script("initialize.py")
        mod.main()
        return 0
    except SystemExit as e:
        return int(e.code) if e.code is not None else 0
    finally:
        sys.argv = old_argv


# ---------------------------------------------------------------------------
# Tests for semver seeding (SC-1, SC-2)
# ---------------------------------------------------------------------------

class TestSemverSeeding:
    def test_semver_marker_seeded_on_init(self):
        """SC-1: initialize.py seeds a matching semver marker in .aib_memory/."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            rc = _run_initialize(root)
            assert rc == 0
            assert (root / ".aib_memory" / "v1.2.8").is_file()

    def test_semver_marker_skipped_when_exists(self):
        """SC-2: Re-running initialize.py does not overwrite an existing semver marker."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            marker = root / ".aib_memory" / "v1.2.8"
            original_mtime = marker.stat().st_mtime
            _run_initialize(root)
            assert marker.stat().st_mtime == original_mtime

    def test_semver_marker_force_overwrites(self):
        """--force replaces any existing semver marker with current brain version."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Place a stale marker for an older version.
            (root / ".aib_memory" / "v1.2.0").touch()
            (root / ".aib_memory" / "v1.2.8").unlink()
            _run_initialize(root, force=True)
            # Stale marker removed; new marker present.
            assert not (root / ".aib_memory" / "v1.2.0").is_file()
            assert (root / ".aib_memory" / "v1.2.8").is_file()

    def test_no_semver_in_brain_skips_seeding(self):
        """Missing brain semver causes a warning but no error."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            # No semver file in brain.
            rc = _run_initialize(root)
            assert rc == 0
            semver_files = list((root / ".aib_memory").glob("v[0-9]*.[0-9]*.[0-9]*"))
            assert len(semver_files) == 0


# ---------------------------------------------------------------------------
# Tests for --upgrade flag
# ---------------------------------------------------------------------------

from unittest.mock import patch


class TestUpgrade:
    def test_upgrade_creates_archive(self):
        """Upgrade creates a timestamped archive under .aib_memory/archives/."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            rc = _run_initialize(root, upgrade=True)
            assert rc == 0
            archives_dir = root / ".aib_memory" / "archives"
            assert archives_dir.is_dir()
            subfolders = [d for d in archives_dir.iterdir() if d.is_dir()]
            assert len(subfolders) == 1

    def test_upgrade_archive_includes_logs(self):
        """Archive includes the logs/ directory."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Place a file in logs/ to verify it lands in the archive.
            log_file = root / ".aib_memory" / "logs" / "test.log"
            log_file.write_text("log content\n", encoding="utf-8")
            _run_initialize(root, upgrade=True)
            archives_dir = root / ".aib_memory" / "archives"
            archive = next(d for d in archives_dir.iterdir() if d.is_dir())
            assert (archive / "logs" / "test.log").is_file()

    def test_upgrade_restores_curated_files(self):
        """Curated files (instructions.md, requests_register.md) are restored in migrate mode."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Mark curated files with recognizable content.
            (root / ".aib_memory" / "instructions.md").write_text("# My instructions\n", encoding="utf-8")
            (root / ".aib_memory" / "requests_register.md").write_text("# Custom register\n", encoding="utf-8")
            # Non-interactive defaults to migrate, so both files should be restored.
            _run_initialize(root, upgrade=True)
            assert (root / ".aib_memory" / "instructions.md").read_text(encoding="utf-8") == "# My instructions\n"
            assert (root / ".aib_memory" / "requests_register.md").read_text(encoding="utf-8") == "# Custom register\n"

    def test_upgrade_seeds_new_semver(self):
        """After upgrade, .aib_memory/ contains the current brain semver marker."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            _run_initialize(root, upgrade=True)
            assert (root / ".aib_memory" / "v1.2.8").is_file()

    def test_upgrade_flat_archive_hierarchy(self):
        """Multiple upgrades produce flat archive hierarchy (no nested archives)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Run two upgrades; each should create a new top-level archive subfolder.
            _run_initialize(root, upgrade=True)
            _run_initialize(root, upgrade=True)
            archives_dir = root / ".aib_memory" / "archives"
            subfolders = [d for d in archives_dir.iterdir() if d.is_dir()]
            assert len(subfolders) == 2
            # No archive should contain a nested archives/ directory.
            for sub in subfolders:
                assert not (sub / "archives").exists()

    def test_upgrade_fails_without_brain_semver(self):
        """--upgrade aborts with a non-zero exit when no brain semver marker exists."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)  # No semver in brain.
            # Seed memory manually so .aib_memory/ exists.
            (root / ".aib_memory" / "requests").mkdir(parents=True, exist_ok=True)
            rc = _run_initialize(root, upgrade=True)
            assert rc != 0

    def test_upgrade_archive_requests_choice(self):
        """SC-2: When user chooses N (archive only), requests/ remains exclusively in the archive."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Seed a request subfolder so archive contains requests/.
            (root / ".aib_memory" / "requests" / "R-test-request").mkdir(parents=True, exist_ok=True)
            (root / ".aib_memory" / "requests" / "R-test-request" / "plan.md").write_text("# Test\n", encoding="utf-8")
            (root / ".aib_memory" / "requests_register.md").write_text("# Custom register\n", encoding="utf-8")
            # Simulate interactive TTY with user choosing archive-only (N).
            with patch("sys.stdin") as mock_stdin, patch("builtins.input", return_value="N"):
                mock_stdin.isatty.return_value = True
                _run_initialize(root, upgrade=True)
            # requests_register.md must NOT be restored (N choice).
            content = (root / ".aib_memory" / "requests_register.md").read_text(encoding="utf-8")
            assert "# Custom register" not in content
            # requests/ must remain exclusively in the archive.
            archives_dir = root / ".aib_memory" / "archives"
            archive = next(d for d in archives_dir.iterdir() if d.is_dir())
            assert (archive / "requests").is_dir(), "requests/ must be in archive when N is chosen"

    def test_upgrade_migrate_requests_choice(self):
        """SC-1: When user chooses Y (migrate), requests/ moves to active memory and is absent from the archive."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Seed a request subfolder to verify full content is migrated.
            (root / ".aib_memory" / "requests" / "R-test-request").mkdir(parents=True, exist_ok=True)
            (root / ".aib_memory" / "requests" / "R-test-request" / "plan.md").write_text("# Test\n", encoding="utf-8")
            (root / ".aib_memory" / "requests_register.md").write_text("# Custom register\n", encoding="utf-8")
            # Simulate interactive TTY with user choosing migrate (Y).
            with patch("sys.stdin") as mock_stdin, patch("builtins.input", return_value="Y"):
                mock_stdin.isatty.return_value = True
                _run_initialize(root, upgrade=True)
            # requests_register.md must be restored in active memory.
            content = (root / ".aib_memory" / "requests_register.md").read_text(encoding="utf-8")
            assert "# Custom register" in content
            # requests/ must exist in active memory with its content intact.
            migrated_request = root / ".aib_memory" / "requests" / "R-test-request" / "plan.md"
            assert migrated_request.is_file(), "Migrated request folder must exist in active memory"
            # SC-1: requests/ must NOT exist in the archive after migration.
            archives_dir = root / ".aib_memory" / "archives"
            archive = next(d for d in archives_dir.iterdir() if d.is_dir())
            assert not (archive / "requests").exists(), "requests/ must be removed from archive after migration"


# ---------------------------------------------------------------------------
# Tests – use a separate temp dir (not workspace_dir fixture) to avoid
# the fixture pre-seeding; initialize must create its own memory structure.
# ---------------------------------------------------------------------------

class TestInitialize:
    def test_creates_aib_memory_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            rc = _run_initialize(root)
            assert rc == 0
            assert (root / ".aib_memory").is_dir()
            assert (root / ".aib_memory" / "requests").is_dir()

    def test_creates_requests_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            assert (root / ".aib_memory" / "requests_register.md").is_file()

    def test_initialize_does_not_create_references_md(self):
        """references.md register removed in v1.2.12 — initialize must not seed it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            assert not (root / ".aib_memory" / "references.md").exists()

    def test_creates_input_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            input_path = root / ".aib_memory" / "input.md"
            assert input_path.is_file()
            content = input_path.read_text(encoding="utf-8")
            assert "## Active request" in content
            assert "## Options" in content
            assert "## Input" in content

    def test_input_md_has_no_threshold_row(self):
        """Seeded input.md must not include a Question threshold row (removed in R-20260508-0036)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            content = (root / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert "Question threshold" not in content

    def test_input_md_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            input_path = root / ".aib_memory" / "input.md"
            # Modify to verify it is NOT overwritten on second run.
            input_path.write_text("# MODIFIED\n", encoding="utf-8")
            _run_initialize(root)
            assert input_path.read_text(encoding="utf-8") == "# MODIFIED\n"

    def test_idempotent_rerun_skips_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            # Modify the register to verify it is NOT overwritten on second run
            reg = root / ".aib_memory" / "requests_register.md"
            original_mtime = reg.stat().st_mtime
            _run_initialize(root)
            assert reg.stat().st_mtime == original_mtime

    def test_missing_aib_brain_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Do NOT create .aib_brain
            rc = _run_initialize(root)
            assert rc != 0

    def test_does_not_create_docs_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            # Since v1.2.0, docs/ is no longer a seeded artifact.
            assert not (root / ".aib_memory" / "docs").exists()

    def test_creates_instructions_md_empty(self):
        """initialize.py must create an empty instructions.md when absent."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            instructions_path = root / ".aib_memory" / "instructions.md"
            assert instructions_path.is_file()
            assert instructions_path.read_text(encoding="utf-8") == ""

    def test_instructions_md_idempotent(self):
        """Re-running initialize.py must not overwrite an existing instructions.md."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            instructions_path = root / ".aib_memory" / "instructions.md"
            instructions_path.write_text("# My directives\n", encoding="utf-8")
            _run_initialize(root)
            assert instructions_path.read_text(encoding="utf-8") == "# My directives\n"

    def test_creates_logs_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            assert (root / ".aib_memory" / "logs").is_dir()

    def test_creates_logs_folder_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            # Second run must not error even when logs/ already exists.
            rc = _run_initialize(root)
            assert rc == 0
            assert (root / ".aib_memory" / "logs").is_dir()

    def test_creates_attachments_dir(self):
        """SC-1: initialize.py creates .aib_memory/attachments/ on fresh workspace."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            rc = _run_initialize(root)
            assert rc == 0
            assert (root / ".aib_memory" / "attachments").is_dir()

    def test_initialize_idempotent_attachments_dir(self):
        """SC-2: Re-running initialize.py must not overwrite existing attachments/ content."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            # Place a sentinel file in attachments/ to verify it survives re-init.
            sentinel = root / ".aib_memory" / "attachments" / "sentinel.txt"
            sentinel.write_text("sentinel", encoding="utf-8")
            rc = _run_initialize(root)
            assert rc == 0
            assert sentinel.is_file(), "Sentinel file in attachments/ was deleted on re-init"
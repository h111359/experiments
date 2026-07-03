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
# Tests for setup file seeding (replaces semver marker file convention)
# ---------------------------------------------------------------------------

class TestSemverSeeding:
    def test_setup_file_seeded_on_init(self):
        """SC-1: initialize.py creates aib-setup.yaml in .aib_memory/ with correct keys."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            rc = _run_initialize(root)
            assert rc == 0
            setup_path = root / ".aib_memory" / "aib-setup.yaml"
            assert setup_path.is_file()
            content = setup_path.read_text(encoding="utf-8")
            assert "memory_version: v1.2.8" in content
            assert "default_questions_number:" in content

    def test_setup_file_skipped_when_exists(self):
        """SC-2: Re-running initialize.py does not overwrite an existing aib-setup.yaml."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            setup_path = root / ".aib_memory" / "aib-setup.yaml"
            original_mtime = setup_path.stat().st_mtime
            _run_initialize(root)
            assert setup_path.stat().st_mtime == original_mtime

    def test_setup_file_force_overwrites(self):
        """--force replaces any existing aib-setup.yaml with fresh brain version content."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Place a custom setup file to verify it gets overwritten.
            setup_path = root / ".aib_memory" / "aib-setup.yaml"
            setup_path.write_text("memory_version: v0.0.1\ndefault_questions_number: 99\n", encoding="utf-8")
            _run_initialize(root, force=True)
            content = setup_path.read_text(encoding="utf-8")
            assert "memory_version: v1.2.8" in content
            # default_questions_number reset to default (5) on force overwrite.
            assert "default_questions_number: 5" in content

    def test_no_semver_in_brain_skips_seeding(self):
        """Missing brain semver causes a warning but no error; no setup file created."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            # No semver file in brain.
            rc = _run_initialize(root)
            assert rc == 0
            assert not (root / ".aib_memory" / "aib-setup.yaml").is_file()

    def test_fresh_setup_includes_compatibility_field(self):
        """Fresh initialize.py creates aib-setup.yaml with memory_version_compatibility: compatible."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            content = (root / ".aib_memory" / "aib-setup.yaml").read_text(encoding="utf-8")
            assert "memory_version_compatibility: compatible" in content


# ---------------------------------------------------------------------------
# Tests for --upgrade flag
# ---------------------------------------------------------------------------

class TestUpgrade:
    def test_upgrade_creates_archive(self):
        """Upgrade creates a legacy_* archive under .aib_memory/archives/ (plural)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            rc = _run_initialize(root, upgrade=True)
            assert rc == 0
            archive_dir = root / ".aib_memory" / "archives"
            assert archive_dir.is_dir()
            subfolders = [d for d in archive_dir.iterdir() if d.is_dir()]
            assert len(subfolders) == 1
            # Archive subfolder name must start with "legacy_".
            assert subfolders[0].name.startswith("legacy_")

    def test_upgrade_restores_curated_files(self):
        """instructions.md is restored from archive; input.md is NOT restored from archive."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            custom_instructions = "# My instructions\n"
            custom_input = "# Custom input\n"
            (root / ".aib_memory" / "instructions.md").write_text(custom_instructions, encoding="utf-8")
            (root / ".aib_memory" / "input.md").write_text(custom_input, encoding="utf-8")
            _run_initialize(root, upgrade=True)
            # instructions.md must be restored unchanged from archive.
            assert (root / ".aib_memory" / "instructions.md").read_text(encoding="utf-8") == custom_instructions
            # input.md must NOT be a literal copy of the archived custom input.
            input_content = (root / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert input_content != custom_input

    def test_upgrade_seeds_new_setup(self):
        """After upgrade, .aib_memory/ contains aib-setup.yaml with updated memory_version."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            _run_initialize(root, upgrade=True)
            setup_path = root / ".aib_memory" / "aib-setup.yaml"
            assert setup_path.is_file()
            content = setup_path.read_text(encoding="utf-8")
            assert "memory_version: v1.2.8" in content

    def test_upgrade_flat_archive_hierarchy(self):
        """Multiple upgrades produce flat archive hierarchy under archives/ (no nested archives)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Run two upgrades; each should create a new top-level archive subfolder.
            _run_initialize(root, upgrade=True)
            _run_initialize(root, upgrade=True)
            archive_dir = root / ".aib_memory" / "archives"
            subfolders = [d for d in archive_dir.iterdir() if d.is_dir()]
            assert len(subfolders) == 2
            # No archive subfolder should contain a nested archives/ directory.
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

    def test_upgrade_creates_migration_input(self):
        """After upgrade, input.md contains migration instructions and idle YAML header."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            _run_initialize(root, upgrade=True)
            input_content = (root / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert "status: idle" in input_content
            assert "### Goal" in input_content
            # ## Input section must be non-empty (contains migration instructions).
            input_section_idx = input_content.find("## Input")
            assert input_section_idx != -1
            after_input = input_content[input_section_idx + len("## Input"):].strip()
            assert after_input, "## Input section must be non-empty after upgrade"

    def test_upgrade_creates_valid_context_placeholder(self):
        """After upgrade, context.md begins with '# Product Context' and has all 5 sections."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            _run_initialize(root, upgrade=True)
            context_content = (root / ".aib_memory" / "context.md").read_text(encoding="utf-8")
            assert context_content.startswith("# Product Context")
            assert "## Product" in context_content
            assert "## Concepts" in context_content
            assert "## Requirements" in context_content
            assert "## Solution" in context_content
            assert "## File Structure" in context_content
            assert "- MUST:" in context_content

    def test_upgrade_does_not_restore_requests(self):
        """After upgrade, requests/ in active memory is empty; legacy requests stay in archive."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Seed a request subfolder to verify it ends up only in archive.
            (root / ".aib_memory" / "requests" / "R-test-request").mkdir(parents=True, exist_ok=True)
            (root / ".aib_memory" / "requests" / "R-test-request" / "plan.md").write_text("# Test\n", encoding="utf-8")
            _run_initialize(root, upgrade=True)
            # requests/ in active memory must exist but be empty.
            active_requests = root / ".aib_memory" / "requests"
            assert active_requests.is_dir()
            request_subfolders = [d for d in active_requests.iterdir() if d.is_dir()]
            assert len(request_subfolders) == 0, "requests/ must be empty in active memory after upgrade"

    def test_upgrade_migration_input_contains_archive_path(self):
        """After upgrade, input.md contains the workspace-relative archive path."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            _run_initialize(root, upgrade=True)
            input_content = (root / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert "archives/legacy_" in input_content

    def test_upgrade_merge_restore_preserves_custom_questions(self):
        """--upgrade preserves custom default_questions_number from archived aib-setup.yaml."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            # Override default_questions_number to a custom value.
            setup_path = root / ".aib_memory" / "aib-setup.yaml"
            setup_path.write_text("memory_version: v1.2.8\ndefault_questions_number: 12\n", encoding="utf-8")
            _run_initialize(root, upgrade=True)
            # After upgrade, custom value must be preserved; memory_version updated.
            content = (root / ".aib_memory" / "aib-setup.yaml").read_text(encoding="utf-8")
            assert "memory_version: v1.2.8" in content
            assert "default_questions_number: 12" in content

    def test_upgrade_sets_initialized_not_populated(self):
        """--upgrade writes memory_version_compatibility: initialized-not-populated to aib-setup.yaml."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_with_semver(root, "v1.2.8")
            _run_initialize(root)
            _run_initialize(root, upgrade=True)
            content = (root / ".aib_memory" / "aib-setup.yaml").read_text(encoding="utf-8")
            assert "memory_version_compatibility: initialized-not-populated" in content


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

    def test_does_not_create_requests_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            assert not (root / ".aib_memory" / "requests_register.md").is_file()

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
            assert "status: idle" in content
            assert "request_id: ~" in content
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
            # Modify input.md to verify it is NOT overwritten on second run
            input_md = root / ".aib_memory" / "input.md"
            original_mtime = input_md.stat().st_mtime
            _run_initialize(root)
            assert input_md.stat().st_mtime == original_mtime

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
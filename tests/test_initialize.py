"""Integration tests for .aib_brain/tools/initialize.py."""

from __future__ import annotations

import importlib.util
import shutil
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

def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), TOOLS_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_brain_only_workspace(root: Path) -> None:
    """Create workspace with .aib_brain/ (templates included) but no .aib_memory/."""
    (root / ".aib_brain" / "templates").mkdir(parents=True, exist_ok=True)
    for tmpl in TEMPLATES_DIR.glob("*.md"):
        shutil.copy(tmpl, root / ".aib_brain" / "templates" / tmpl.name)


def _run_initialize(workspace: Path, force: bool = False) -> int:
    args = ["--workspace", str(workspace)]
    if force:
        args.append("--force")
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

    def test_creates_references_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            assert (root / ".aib_memory" / "references.md").is_file()

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

    def test_input_md_has_threshold_scale_labels(self):
        """Seeded input.md must include scale-direction labels on threshold values 1 and 5."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            content = (root / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert "1 (all)" in content
            assert "5 (mandatory only)" in content

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

    def test_force_overwrites_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_brain_only_workspace(root)
            _run_initialize(root)
            ref_path = root / ".aib_memory" / "references.md"
            ref_path.write_text("# MODIFIED\n", encoding="utf-8")
            _run_initialize(root, force=True)
            content = ref_path.read_text(encoding="utf-8")
            assert "# MODIFIED" not in content

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

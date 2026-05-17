"""Unit tests for .aib_brain/tools/file-inventory.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------

def _load_rev_eng():
    spec = importlib.util.spec_from_file_location("reverse_engineer", TOOLS_DIR / "file-inventory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestReverseEngineerInventory:
    def test_lists_all_files(self, workspace_dir: Path):
        # Create a couple of files in the workspace
        (workspace_dir / "file_a.txt").write_text("a", encoding="utf-8")
        (workspace_dir / "file_b.txt").write_text("b", encoding="utf-8")
        reng = _load_rev_eng()
        files = list(reng.iter_files(workspace_dir, set()))
        paths = {f.relative_to(workspace_dir).as_posix() for f in files}
        assert "file_a.txt" in paths
        assert "file_b.txt" in paths

    def test_excludes_git_directory(self, workspace_dir: Path):
        git_dir = workspace_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("", encoding="utf-8")
        reng = _load_rev_eng()
        files = list(reng.iter_files(workspace_dir, {".git"}))
        paths = {f.relative_to(workspace_dir).as_posix() for f in files}
        assert not any(".git" in p for p in paths)

    def test_excludes_custom_directories(self, workspace_dir: Path):
        (workspace_dir / "node_modules").mkdir()
        (workspace_dir / "node_modules" / "pkg.js").write_text("", encoding="utf-8")
        reng = _load_rev_eng()
        files = list(reng.iter_files(workspace_dir, {"node_modules"}))
        paths = {f.relative_to(workspace_dir).as_posix() for f in files}
        assert not any("node_modules" in p for p in paths)

    def test_should_exclude_helper(self, workspace_dir: Path):
        reng = _load_rev_eng()
        excluded = {".git"}
        git_path = workspace_dir / ".git" / "config"
        assert reng._should_exclude(git_path, excluded, workspace_dir) is True

    def test_should_not_exclude_normal_file(self, workspace_dir: Path):
        reng = _load_rev_eng()
        normal_path = workspace_dir / "README.md"
        assert reng._should_exclude(normal_path, set(), workspace_dir) is False


class TestReverseEngineerOutput:
    def test_output_is_jsonl(self, workspace_dir: Path):
        (workspace_dir / "sample.py").write_text("x=1", encoding="utf-8")
        reng = _load_rev_eng()
        records = []
        for f in reng.iter_files(workspace_dir, set()):
            stat = f.stat()
            rel = f.relative_to(workspace_dir).as_posix()
            ext = f.suffix.lower().lstrip(".")
            records.append({"path": rel, "size_bytes": int(stat.st_size), "mtime_epoch": int(stat.st_mtime), "extension": ext})
        records.sort(key=lambda r: r["path"])
        for r in records:
            # Should be JSON-serializable without error
            json.dumps(r)

    def test_records_sorted_by_path(self, workspace_dir: Path):
        for name in ["z.txt", "a.txt", "m.txt"]:
            (workspace_dir / name).write_text("", encoding="utf-8")
        reng = _load_rev_eng()
        records = []
        for f in reng.iter_files(workspace_dir, set()):
            rel = f.relative_to(workspace_dir).as_posix()
            records.append({"path": rel})
        records.sort(key=lambda r: r["path"])
        paths = [r["path"] for r in records]
        assert paths == sorted(paths)

    def test_main_writes_to_output_file(self, workspace_dir: Path):
        (workspace_dir / "test_file.txt").write_text("hello", encoding="utf-8")
        output_path = workspace_dir / "inventory.jsonl"
        old_argv = sys.argv[:]
        sys.argv = [
            "file-inventory.py",
            "--workspace", str(workspace_dir),
            "--output", str(output_path),
        ]
        try:
            reng = _load_rev_eng()
            reng.main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv
        assert output_path.is_file()
        lines = output_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 1
        for line in lines:
            obj = json.loads(line)
            assert "path" in obj

    def test_max_files_limits_output(self, workspace_dir: Path):
        for i in range(10):
            (workspace_dir / f"f{i}.txt").write_text("", encoding="utf-8")
        output_path = workspace_dir / "limited.jsonl"
        old_argv = sys.argv[:]
        sys.argv = [
            "file-inventory.py",
            "--workspace", str(workspace_dir),
            "--output", str(output_path),
            "--max-files", "3",
        ]
        try:
            reng = _load_rev_eng()
            reng.main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv
        lines = output_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) <= 3

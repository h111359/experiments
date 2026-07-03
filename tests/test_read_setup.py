"""Tests for .aib_brain/tools/read-setup.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = WORKSPACE_ROOT / ".aib_brain" / "tools" / "read-setup.py"


def _run_read_setup(workspace: Path, option: str) -> subprocess.CompletedProcess:
    """Invoke read-setup.py as a subprocess and return the completed process.

    Args:
        workspace: Path to the workspace directory.
        option: The --option argument to pass.

    Returns:
        CompletedProcess with stdout, stderr, and returncode.
    """
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--workspace", str(workspace), "--option", option],
        capture_output=True,
        text=True,
    )


class TestReadSetupValidOption:
    """SC-1: Valid option is retrieved and printed to stdout with exit code 0."""

    def test_returns_memory_version_value(self, tmp_path: Path):
        """read-setup.py prints bare memory_version value and exits 0."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        (memory_dir / "aib-setup.yaml").write_text(
            "memory_version: v1.5.0\ndefault_questions_number: 5\n",
            encoding="utf-8",
        )
        result = _run_read_setup(tmp_path, "memory_version")
        assert result.returncode == 0
        assert result.stdout.strip() == "v1.5.0"

    def test_returns_default_questions_number_value(self, tmp_path: Path):
        """read-setup.py prints bare default_questions_number value and exits 0."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        (memory_dir / "aib-setup.yaml").write_text(
            "memory_version: v1.5.0\ndefault_questions_number: 9\n",
            encoding="utf-8",
        )
        result = _run_read_setup(tmp_path, "default_questions_number")
        assert result.returncode == 0
        assert result.stdout.strip() == "9"


class TestReadSetupMissingKey:
    """SC-2: Missing key exits with code 1 and prints an error to stderr."""

    def test_missing_key_exits_1(self, tmp_path: Path):
        """Requesting a non-existent key exits with code 1."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        (memory_dir / "aib-setup.yaml").write_text(
            "memory_version: v1.5.0\n",
            encoding="utf-8",
        )
        result = _run_read_setup(tmp_path, "nonexistent")
        assert result.returncode == 1

    def test_missing_key_error_to_stderr(self, tmp_path: Path):
        """Error message for missing key goes to stderr."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        (memory_dir / "aib-setup.yaml").write_text(
            "memory_version: v1.5.0\n",
            encoding="utf-8",
        )
        result = _run_read_setup(tmp_path, "nonexistent")
        assert "nonexistent" in result.stderr
        assert "ERROR" in result.stderr


class TestReadSetupMissingFile:
    """SC-3: Missing aib-setup.yaml exits with code 1 and prints an error to stderr."""

    def test_missing_file_exits_1(self, tmp_path: Path):
        """When aib-setup.yaml does not exist, exit code is 1."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        # No aib-setup.yaml created.
        result = _run_read_setup(tmp_path, "memory_version")
        assert result.returncode == 1

    def test_missing_file_error_to_stderr(self, tmp_path: Path):
        """Error message for missing file goes to stderr."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        result = _run_read_setup(tmp_path, "memory_version")
        assert "ERROR" in result.stderr
        assert "aib-setup.yaml" in result.stderr


class TestReadSetupCorruptYaml:
    """SC-4: Non-parseable aib-setup.yaml exits with code 1."""

    def test_corrupt_yaml_exits_1(self, tmp_path: Path):
        """When aib-setup.yaml has no key-value pairs (corrupt), exit code is 1."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        # Write content with no colon — cannot contain any flat YAML key.
        (memory_dir / "aib-setup.yaml").write_text(
            "this is not valid yaml content without colons\n",
            encoding="utf-8",
        )
        result = _run_read_setup(tmp_path, "memory_version")
        assert result.returncode == 1

    def test_empty_file_exits_1(self, tmp_path: Path):
        """An empty aib-setup.yaml causes exit code 1."""
        memory_dir = tmp_path / ".aib_memory"
        memory_dir.mkdir()
        (memory_dir / "aib-setup.yaml").write_text("", encoding="utf-8")
        result = _run_read_setup(tmp_path, "memory_version")
        assert result.returncode == 1

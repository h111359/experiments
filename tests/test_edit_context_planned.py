"""
test_edit_context_planned.py: Tests for edit-context.py new features.
Part of the AIB test suite.
Responsibilities:
- --planned flag inserts [PLANNED] prefix in Concepts, Product, Solution.
- --planned flag inserts [PLANNED] MUST: prefix in Requirements.
- Issues area accepts insert, select, and delete operations.
- Issues area rejects --type (modality) argument.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
EDIT_SCRIPT = WORKSPACE_ROOT / ".aib_brain" / "tools" / "edit-context.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_CONTEXT = """\
# Product Context

## Product
- AIB is a test product.

## Concepts
- Test concept.

## Requirements
- MUST: Test requirement.

## Solution
- Test solution.

## File Structure
.aib_brain/ - brain folder

"""


def _setup_context(tmp_path: Path, content: str = MINIMAL_CONTEXT) -> Path:
    """Write a context.md and return the workspace path."""
    mem = tmp_path / ".aib_memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "context.md").write_text(content, encoding="utf-8")
    return tmp_path


def _run_edit(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    """Run edit-context.py with given args, returning CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(EDIT_SCRIPT), "--workspace", str(tmp_path), *args],
        capture_output=True,
        text=True,
    )


def _read_context(tmp_path: Path) -> str:
    """Read the context.md from the workspace."""
    return (tmp_path / ".aib_memory" / "context.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# --planned flag for plain-bullet sections
# ---------------------------------------------------------------------------

class TestPlannedFlagInsert:
    """--planned flag must produce [PLANNED]-prefixed bullets."""

    def test_planned_insert_concepts(self, tmp_path: Path) -> None:
        """--planned inserts '- [PLANNED] <text>' into Concepts section."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Concepts",
            "--planned",
            "--text", "example planned concept",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- [PLANNED] example planned concept" in content, (
            f"Expected '- [PLANNED] example planned concept' in context.md.\nContent:\n{content}"
        )

    def test_planned_insert_product(self, tmp_path: Path) -> None:
        """--planned inserts '- [PLANNED] <text>' into Product section."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Product",
            "--planned",
            "--text", "example planned product statement",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- [PLANNED] example planned product statement" in content

    def test_planned_insert_solution(self, tmp_path: Path) -> None:
        """--planned inserts '- [PLANNED] <text>' into Solution section."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Solution",
            "--planned",
            "--text", "example planned solution",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- [PLANNED] example planned solution" in content

    def test_planned_insert_requirements(self, tmp_path: Path) -> None:
        """--planned with --type MUST inserts '- [PLANNED] MUST: <text>' into Requirements."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Requirements",
            "--type", "MUST",
            "--planned",
            "--text", "example planned requirement",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- [PLANNED] MUST: example planned requirement" in content, (
            f"Expected '- [PLANNED] MUST: example planned requirement' in context.md.\nContent:\n{content}"
        )

    def test_planned_insert_requirements_must_not(self, tmp_path: Path) -> None:
        """--planned with --type MUST NOT inserts '- [PLANNED] MUST NOT: <text>'."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Requirements",
            "--type", "MUST NOT",
            "--planned",
            "--text", "example planned prohibition",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- [PLANNED] MUST NOT: example planned prohibition" in content

    def test_no_planned_flag_inserts_plain(self, tmp_path: Path) -> None:
        """Without --planned, insert produces a plain bullet (no [PLANNED] prefix)."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Concepts",
            "--text", "plain concept without planned",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- plain concept without planned" in content
        assert "- [PLANNED] plain concept without planned" not in content


# ---------------------------------------------------------------------------
# Issues area operations
# ---------------------------------------------------------------------------

class TestIssuesArea:
    """Issues area must support insert, select, and delete operations."""

    def _context_with_issues(self) -> str:
        """Return a context.md that includes an ## Issues section."""
        return MINIMAL_CONTEXT + "## Issues\n- Existing issue one.\n\n"

    def test_issues_insert(self, tmp_path: Path) -> None:
        """insert into Issues area adds a plain bullet."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Issues",
            "--text", "example issue",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- example issue" in content

    def test_issues_select(self, tmp_path: Path) -> None:
        """select from Issues area finds the matching bullet."""
        _setup_context(tmp_path, self._context_with_issues())
        result = _run_edit(
            tmp_path,
            "--operation", "select",
            "--area", "Issues",
            "--text", "Existing issue one",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        assert "Existing issue one" in result.stdout

    def test_issues_delete(self, tmp_path: Path) -> None:
        """delete from Issues area removes the matching bullet."""
        _setup_context(tmp_path, self._context_with_issues())
        result = _run_edit(
            tmp_path,
            "--operation", "delete",
            "--area", "Issues",
            "--text", "Existing issue one",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "Existing issue one" not in content

    def test_issues_with_type_rejected(self, tmp_path: Path) -> None:
        """insert into Issues with --type argument exits with code 1."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Issues",
            "--type", "MUST",
            "--text", "invalid issues entry",
        )
        assert result.returncode == 1, (
            f"Issues insert with --type should fail.\nSTDERR: {result.stderr}"
        )

    def test_issues_planned_ignored(self, tmp_path: Path) -> None:
        """--planned flag on Issues area inserts plain bullet (no [PLANNED] prefix)."""
        _setup_context(tmp_path)
        result = _run_edit(
            tmp_path,
            "--operation", "insert",
            "--area", "Issues",
            "--planned",
            "--text", "should be plain issue",
        )
        assert result.returncode == 0, f"Expected exit 0.\nSTDERR: {result.stderr}"
        content = _read_context(tmp_path)
        assert "- should be plain issue" in content
        assert "- [PLANNED] should be plain issue" not in content

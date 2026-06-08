"""
test_verify_context.py: Tests for the verify-context.py tool script.
Part of the AIB test suite.
Responsibilities: Validate that verify-context.py correctly identifies passing and failing
context.md documents across all implemented checks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = WORKSPACE_ROOT / ".aib_brain" / "tools" / "verify-context.py"

# Minimal well-formed context.md content for baseline tests (new format)
VALID_CONTEXT = """\
# Product Context

## 1. Product Identity

Test Product is a minimal framework for testing. It requires Python 3 and Git.

Primary actors are developers and automated agents.

The product is active and in use.

## FN

- R: System must validate documents.
- N: Validation runs at prompt execution time.

## PO

- N: Test project operates in software engineering domain.
- I: Primary use case is specification-driven development.

## Files

.aib_memory/
  context.md — product context
tests/
  test_verify_context.py — verification tests
"""


def _run_verify(workspace: Path) -> subprocess.CompletedProcess:
    """
    Run verify-context.py against the given workspace directory.

    Args:
        workspace: Path to workspace root containing .aib_memory/context.md.

    Returns:
        CompletedProcess with stdout, stderr, and returncode.
    """
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--workspace", str(workspace)],
        capture_output=True,
        text=True,
    )


def _write_context(workspace: Path, content: str) -> None:
    """
    Write content to .aib_memory/context.md in the given workspace.

    Args:
        workspace: Path to workspace root.
        content: Full text to write.
    """
    memory_dir = workspace / ".aib_memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "context.md").write_text(content, encoding="utf-8")


class TestVerifyContextPassingCase:
    """Tests verifying that a well-formed context.md passes all checks."""

    def test_valid_context_passes_all_checks(self, tmp_path: Path) -> None:
        """A well-formed context.md should produce exit code 0."""
        _write_context(tmp_path, VALID_CONTEXT)
        result = _run_verify(tmp_path)
        assert result.returncode == 0
        assert "Results: 10/10 checks passed." in result.stdout

    def test_output_contains_ok_markers(self, tmp_path: Path) -> None:
        """Output should contain [OK] markers for each passing check."""
        _write_context(tmp_path, VALID_CONTEXT)
        result = _run_verify(tmp_path)
        assert "[OK] check_title_and_product_identity" in result.stdout
        assert "[OK] check_area_headings_valid" in result.stdout
        assert "[OK] check_statement_format" in result.stdout


class TestVerifyContextMissingSections:
    """Tests for missing mandatory sections."""

    def test_missing_product_identity(self, tmp_path: Path) -> None:
        """Missing ## 1. Product Identity should cause failure."""
        content = VALID_CONTEXT.replace("## 1. Product Identity", "## 1. Overview")
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_title_and_product_identity" in result.stdout


class TestVerifyContextDuplicateIndex:
    """Tests for duplicate statement text within an area section."""

    def test_duplicate_statement_text(self, tmp_path: Path) -> None:
        """Duplicate statement text within same area should cause failure."""
        content = VALID_CONTEXT.replace(
            "- R: System must validate documents.",
            "- R: System must validate documents.\n- N: System must validate documents.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_statement_uniqueness" in result.stdout


class TestVerifyContextInvalidFormat:
    """Tests for invalid statement format."""

    def test_invalid_area_heading(self, tmp_path: Path) -> None:
        """Invalid H2 area heading (not in VALID_AREAS) should cause failure."""
        content = VALID_CONTEXT.replace(
            "## FN",
            "## XX",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_area_headings_valid" in result.stdout

    def test_invalid_type_letter(self, tmp_path: Path) -> None:
        """Multi-letter type (not a single uppercase letter) should cause failure."""
        content = VALID_CONTEXT.replace(
            "- R: System must validate documents.",
            "- RR: System must validate documents.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_statement_format" in result.stdout


class TestVerifyContextEmptyAreaSection:
    """Tests for empty area sections."""

    def test_empty_area_section_fails(self, tmp_path: Path) -> None:
        """An area section heading with no statements should cause failure."""
        # Add an empty AN section (heading with no statements)
        content = VALID_CONTEXT.replace(
            "## Files",
            "## AN\n\n## Files",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_area_sections_non_empty" in result.stdout


class TestVerifyContextExternalLinks:
    """Tests for external hyperlink detection."""

    def test_http_url_fails(self, tmp_path: Path) -> None:
        """Presence of http:// URL should cause failure."""
        content = VALID_CONTEXT.replace(
            "- N: Test project operates in software engineering domain.",
            "- N: Test project at http://example.com operates in SE domain.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_no_external_hyperlinks" in result.stdout


class TestVerifyContextHtmlTags:
    """Tests for HTML tag detection."""

    def test_html_tag_fails(self, tmp_path: Path) -> None:
        """Presence of HTML tags (outside backticks) should cause failure."""
        content = VALID_CONTEXT.replace(
            "- N: Test project operates in software engineering domain.",
            "- N: Test project uses <strong>bold</strong> formatting.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_no_html_tags" in result.stdout


class TestVerifyContextFileNotFound:
    """Tests for missing context.md file."""

    def test_missing_file_fails(self, tmp_path: Path) -> None:
        """Missing context.md should produce exit code 1."""
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL]" in result.stdout

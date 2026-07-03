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

# Minimal well-formed context.md content for baseline tests (6-section format)
VALID_CONTEXT = """\
# Product Context

## Product

- AIB is a minimal, model-agnostic framework for specification-driven development.

## Concepts

- Convention-over-configuration means all product and code quality rules are captured in convention files.
- Specification-first development means every change is preceded by analysis and plan.

## Requirements

- MUST: All changes must be preceded by analysis and plan before code is written.
- MUST NOT: AI agents must not modify .aib_brain/ assets during implementation.

## Solution

- AIB tracks active-request state via YAML frontmatter header in input.md.

## File Structure

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
        assert "Results: 12/12 checks passed." in result.stdout

    def test_output_contains_ok_markers(self, tmp_path: Path) -> None:
        """Output should contain [OK] markers for each passing check."""
        _write_context(tmp_path, VALID_CONTEXT)
        result = _run_verify(tmp_path)
        assert "[OK] check_document_title" in result.stdout
        assert "[OK] check_all_h2_headings_valid" in result.stdout
        assert "[OK] check_product_concepts_solution_format" in result.stdout


class TestVerifyContextMissingSections:
    """Tests for missing mandatory sections."""

    def test_missing_product_section(self, tmp_path: Path) -> None:
        """Missing ## Product section should cause failure."""
        content = VALID_CONTEXT.replace("## Product", "## Overview")
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_product_section_present_and_non_empty" in result.stdout


class TestVerifyContextRequirementsFormat:
    """Tests for Requirements section statement format."""

    def test_requirements_without_modality_fails(self, tmp_path: Path) -> None:
        """A Requirements statement without modality prefix should cause failure."""
        content = VALID_CONTEXT.replace(
            "- MUST: All changes must be preceded by analysis and plan before code is written.",
            "- All changes must be preceded by analysis and plan before code is written.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_requirements_format" in result.stdout


class TestVerifyContextInvalidFormat:
    """Tests for invalid heading and statement format."""

    def test_invalid_area_heading(self, tmp_path: Path) -> None:
        """Invalid H2 area heading (not in VALID_SECTIONS) should cause failure."""
        content = VALID_CONTEXT.replace(
            "## Concepts",
            "## XX",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_all_h2_headings_valid" in result.stdout

    def test_requirements_invalid_format_fails(self, tmp_path: Path) -> None:
        """A Requirements bullet with type-letter prefix instead of modality should cause failure."""
        content = VALID_CONTEXT.replace(
            "- MUST: All changes must be preceded by analysis and plan before code is written.",
            "- R: All changes must be preceded by analysis and plan before code is written.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_requirements_format" in result.stdout


class TestVerifyContextEmptyProductSection:
    """Tests for empty Product section."""

    def test_empty_product_section_fails(self, tmp_path: Path) -> None:
        """A Product section heading with no statements should cause failure."""
        content = VALID_CONTEXT.replace(
            "- AIB is a minimal, model-agnostic framework for specification-driven development.\n",
            "",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_product_section_present_and_non_empty" in result.stdout


class TestVerifyContextExternalLinks:
    """Tests for external hyperlink detection."""

    def test_http_url_fails(self, tmp_path: Path) -> None:
        """Presence of http:// URL should cause failure."""
        content = VALID_CONTEXT.replace(
            "- Convention-over-configuration means all product and code quality rules are captured in convention files.",
            "- See documentation at http://example.com for more details.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_no_html_tables_urls" in result.stdout


class TestVerifyContextHtmlTags:
    """Tests for HTML tag detection."""

    def test_html_tag_fails(self, tmp_path: Path) -> None:
        """Presence of HTML tags (outside backticks) should cause failure."""
        content = VALID_CONTEXT.replace(
            "- Convention-over-configuration means all product and code quality rules are captured in convention files.",
            "- Test project uses <strong>bold</strong> formatting.",
        )
        _write_context(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_no_html_tables_urls" in result.stdout


class TestVerifyContextFileNotFound:
    """Tests for missing context.md file."""

    def test_missing_file_fails(self, tmp_path: Path) -> None:
        """Missing context.md should produce exit code 1."""
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL]" in result.stdout

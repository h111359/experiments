"""
test_verify_context_planned.py: Tests for verify-context.py new features.
Part of the AIB test suite.
Responsibilities:
- Check 7 updated: [PLANNED] entries in all four content sections accepted.
- Check 7 updated: malformed [PLANNED] syntax rejected.
- Check 11: valid ## Issues plain bullets accepted.
- Check 11: malformed Issues entries rejected.
- Check 12: valid Update: flag values accepted.
- Check 12: invalid Update: flag values rejected.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
VERIFY_SCRIPT = WORKSPACE_ROOT / ".aib_brain" / "tools" / "verify-context.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_CONTEXT_HEADER = "# Product Context\n\n"
MINIMAL_PRODUCT = "## Product\n- AIB is a test product.\n\n"
MINIMAL_CONCEPTS = "## Concepts\n- Test concept.\n\n"
MINIMAL_REQUIREMENTS = "## Requirements\n- MUST: Test requirement.\n\n"
MINIMAL_SOLUTION = "## Solution\n- Test solution.\n\n"
MINIMAL_FILE_STRUCTURE = "## File Structure\n.aib_brain/ - brain folder\n\n"


def _build_minimal(extra: str = "") -> str:
    """Build a minimal valid context.md with optional extra sections."""
    return (
        MINIMAL_CONTEXT_HEADER
        + MINIMAL_PRODUCT
        + MINIMAL_CONCEPTS
        + MINIMAL_REQUIREMENTS
        + MINIMAL_SOLUTION
        + MINIMAL_FILE_STRUCTURE
        + extra
    )


def _run_verify(tmp_path: Path, context_content: str) -> subprocess.CompletedProcess:
    """Write context.md and run verify-context.py, returning CompletedProcess."""
    mem = tmp_path / ".aib_memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "context.md").write_text(context_content, encoding="utf-8")
    # Write a minimal idle input.md so the script can update verification result
    (mem / "input.md").write_text(
        "---\nstate:\n  request_id: ~\n  title: ~\n  status: idle\n"
        "  input_verification_result: null\n  context_verification_result: null\n"
        "options:\n  minimum_questions: 5\n  input_verification_enabled: false\n"
        "  context_verification_enabled: false\n---\n\n## Input\n\n",
        encoding="utf-8",
    )
    brain = tmp_path / ".aib_brain" / "tools"
    brain.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT), "--workspace", str(tmp_path)],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Check 7 updated: [PLANNED] in Product / Concepts / Solution
# ---------------------------------------------------------------------------

class TestPlannedTagInContentSections:
    """[PLANNED]-prefixed bullets must be accepted in Product, Concepts, Solution."""

    def test_planned_in_product_accepted(self, tmp_path: Path) -> None:
        """[PLANNED] bullet in Product section exits with code 0."""
        content = (
            MINIMAL_CONTEXT_HEADER
            + "## Product\n- AIB is a product.\n- [PLANNED] Future product feature.\n\n"
            + MINIMAL_CONCEPTS
            + MINIMAL_REQUIREMENTS
            + MINIMAL_SOLUTION
            + MINIMAL_FILE_STRUCTURE
        )
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"[PLANNED] in Product should pass check 7.\nSTDOUT: {result.stdout}"
        )

    def test_planned_in_concepts_accepted(self, tmp_path: Path) -> None:
        """[PLANNED] bullet in Concepts section exits with code 0."""
        content = _build_minimal().replace(
            "## Concepts\n- Test concept.\n",
            "## Concepts\n- Test concept.\n- [PLANNED] Future concept.\n",
        )
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"[PLANNED] in Concepts should pass check 7.\nSTDOUT: {result.stdout}"
        )

    def test_planned_in_solution_accepted(self, tmp_path: Path) -> None:
        """[PLANNED] bullet in Solution section exits with code 0."""
        content = _build_minimal().replace(
            "## Solution\n- Test solution.\n",
            "## Solution\n- Test solution.\n- [PLANNED] Future solution approach.\n",
        )
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"[PLANNED] in Solution should pass check 7.\nSTDOUT: {result.stdout}"
        )

    def test_planned_in_requirements_accepted(self, tmp_path: Path) -> None:
        """[PLANNED] MUST: bullet in Requirements section exits with code 0."""
        content = _build_minimal().replace(
            "## Requirements\n- MUST: Test requirement.\n",
            "## Requirements\n- MUST: Test requirement.\n- [PLANNED] MUST: Future requirement.\n",
        )
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"[PLANNED] MUST: in Requirements should pass check 8.\nSTDOUT: {result.stdout}"
        )

    def test_planned_must_not_in_requirements_accepted(self, tmp_path: Path) -> None:
        """[PLANNED] MUST NOT: bullet in Requirements section exits with code 0."""
        content = _build_minimal().replace(
            "## Requirements\n- MUST: Test requirement.\n",
            "## Requirements\n- MUST: Test requirement.\n- [PLANNED] MUST NOT: Future prohibition.\n",
        )
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"[PLANNED] MUST NOT: in Requirements should pass.\nSTDOUT: {result.stdout}"
        )

    def test_planned_modality_mismatch_rejected(self, tmp_path: Path) -> None:
        """[PLANNED] without modality prefix in Requirements exits with code 1."""
        content = _build_minimal().replace(
            "## Requirements\n- MUST: Test requirement.\n",
            "## Requirements\n- MUST: Test requirement.\n- [PLANNED] plain text without modality.\n",
        )
        result = _run_verify(tmp_path, content)
        assert result.returncode == 1, (
            f"[PLANNED] without modality in Requirements should fail check 8.\nSTDOUT: {result.stdout}"
        )


# ---------------------------------------------------------------------------
# Check 11: ## Issues section format
# ---------------------------------------------------------------------------

class TestIssuesSectionFormat:
    """## Issues section must contain only plain bullets."""

    def test_issues_absent_passes(self, tmp_path: Path) -> None:
        """context.md without ## Issues section passes check 11."""
        result = _run_verify(tmp_path, _build_minimal())
        assert result.returncode == 0, (
            f"context.md without Issues section should pass all checks.\nSTDOUT: {result.stdout}"
        )

    def test_issues_with_valid_bullets_passes(self, tmp_path: Path) -> None:
        """## Issues with plain bullets exits with code 0."""
        content = _build_minimal() + "## Issues\n- Issue one.\n- Issue two.\n\n"
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"Valid Issues section should pass check 11.\nSTDOUT: {result.stdout}"
        )

    def test_issues_with_subheading_fails(self, tmp_path: Path) -> None:
        """## Issues with a sub-heading exits with code 1."""
        content = _build_minimal() + "## Issues\n### Sub-heading\n- Issue one.\n\n"
        result = _run_verify(tmp_path, content)
        # check_all_h2_headings_valid passes; the sub-heading is H3 within Issues
        # But Issues entries check should detect non-bullet lines? Actually H3 is not a bullet.
        # The Issues format check only validates lines starting with '- ', non-empty lines
        # that don't match '- <text>' will fail.
        assert result.returncode == 1, (
            f"Issues section with sub-heading should fail.\nSTDOUT: {result.stdout}"
        )

    def test_issues_with_invalid_h2_heading_fails(self, tmp_path: Path) -> None:
        """context.md with invalid H2 in Issues position fails check 2."""
        content = _build_minimal() + "## NotValid\n- some content.\n\n"
        result = _run_verify(tmp_path, content)
        assert result.returncode == 1, (
            f"Invalid H2 heading should fail check 2.\nSTDOUT: {result.stdout}"
        )


# ---------------------------------------------------------------------------
# Check 12: References Update: flag validation
# ---------------------------------------------------------------------------

class TestReferencesUpdateFlag:
    """References entries Update: line must have value 'true' or 'false'."""

    def test_no_update_flag_passes(self, tmp_path: Path) -> None:
        """References entry without Update: line passes check 12."""
        content = _build_minimal() + textwrap.dedent("""\
            ## References
            ### My Ref
            Location: docs/ref.md
            Summary: A plain reference without extension flag.
        """)
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"References entry without Update: should pass.\nSTDOUT: {result.stdout}"
        )

    def test_update_false_passes(self, tmp_path: Path) -> None:
        """References entry with Update: false passes check 12."""
        content = _build_minimal() + textwrap.dedent("""\
            ## References
            ### My Extension
            Location: docs/ext.md
            Summary: A read-only extension.
            Update: false
        """)
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"References entry with 'Update: false' should pass.\nSTDOUT: {result.stdout}"
        )

    def test_update_true_passes(self, tmp_path: Path) -> None:
        """References entry with Update: true passes check 12."""
        content = _build_minimal() + textwrap.dedent("""\
            ## References
            ### My Writable Extension
            Location: docs/ext.md
            Summary: A writable extension.
            Update: true
        """)
        result = _run_verify(tmp_path, content)
        assert result.returncode == 0, (
            f"References entry with 'Update: true' should pass.\nSTDOUT: {result.stdout}"
        )

    def test_update_invalid_value_fails(self, tmp_path: Path) -> None:
        """References entry with invalid Update: value fails check 12."""
        content = _build_minimal() + textwrap.dedent("""\
            ## References
            ### My Extension
            Location: docs/ext.md
            Summary: An extension with invalid flag.
            Update: yes
        """)
        result = _run_verify(tmp_path, content)
        assert result.returncode == 1, (
            f"References entry with 'Update: yes' should fail check 12.\nSTDOUT: {result.stdout}"
        )

    def test_update_uppercase_fails(self, tmp_path: Path) -> None:
        """References entry with Update: True (capitalized) fails check 12."""
        content = _build_minimal() + textwrap.dedent("""\
            ## References
            ### My Extension
            Location: docs/ext.md
            Summary: An extension with capitalized flag.
            Update: True
        """)
        result = _run_verify(tmp_path, content)
        assert result.returncode == 1, (
            f"References entry with 'Update: True' (capital T) should fail check 12.\nSTDOUT: {result.stdout}"
        )


# ---------------------------------------------------------------------------
# Total check count
# ---------------------------------------------------------------------------

class TestVerifyContextCheckCount:
    """verify-context.py must run exactly 12 checks on valid context.md."""

    def test_12_checks_run(self, tmp_path: Path) -> None:
        """Script must report 12/12 checks passed on a fully valid context.md."""
        result = _run_verify(tmp_path, _build_minimal())
        assert "12/12 checks passed" in result.stdout, (
            f"Expected '12/12 checks passed' in output.\nSTDOUT: {result.stdout}"
        )

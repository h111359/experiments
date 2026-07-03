"""
test_verify_input.py: Tests for the verify-input.py tool script.
Part of the AIB test suite.
Responsibilities: Validate that verify-input.py correctly identifies passing and failing
input.md documents across all implemented checks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = WORKSPACE_ROOT / ".aib_brain" / "tools" / "verify-input.py"

# Minimal well-formed input.md for all-pass baseline tests.
VALID_INPUT = """\
---
state:
  request_id: R-20260101-1000
  title: Test request
  status: analysis_ready
  input_verification_result: null
  context_verification_result: null
options:
  minimum_questions: 5
  input_verification_enabled: true
  context_verification_enabled: true
---

## Input

This is the user input.
"""

# Well-formed input.md in questions_generated state with a conformant Q-block.
VALID_INPUT_WITH_QUESTIONS = """\
---
state:
  request_id: R-20260101-1000
  title: Test request
  status: questions_generated
  input_verification_result: null
  context_verification_result: null
options:
  minimum_questions: 5
  input_verification_enabled: true
  context_verification_enabled: true
---

## Input

This is the user input.

## Questions

**Q001**: Which approach should be used?
> **Why this matters:** The choice determines the implementation complexity.
- [ ] Option A: Simple approach *(recommended)*
- [ ] Option B: Complex approach
- [ ] Other: ___
"""


def _run_verify(workspace: Path) -> subprocess.CompletedProcess:
    """Run verify-input.py against the given workspace directory.

    Args:
        workspace: Path to workspace root containing .aib_memory/input.md.

    Returns:
        CompletedProcess with stdout, stderr, and returncode.
    """
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--workspace", str(workspace)],
        capture_output=True,
        text=True,
    )


def _write_input(workspace: Path, content: str) -> None:
    """Write content to .aib_memory/input.md in the given workspace.

    Args:
        workspace: Path to workspace root.
        content: Full text to write.
    """
    memory_dir = workspace / ".aib_memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "input.md").write_text(content, encoding="utf-8")


class TestVerifyInputPassingCase:
    """Tests verifying that a well-formed input.md passes all checks."""

    def test_valid_input_passes_all_checks(self, tmp_path: Path) -> None:
        """A well-formed input.md should produce exit code 0."""
        _write_input(tmp_path, VALID_INPUT)
        result = _run_verify(tmp_path)
        assert result.returncode == 0, f"Expected exit 0 but got {result.returncode}.\n{result.stdout}"
        assert "Results: 10/10 checks passed." in result.stdout

    def test_output_contains_pass_markers(self, tmp_path: Path) -> None:
        """Output should contain [PASS] markers for each passing check."""
        _write_input(tmp_path, VALID_INPUT)
        result = _run_verify(tmp_path)
        assert "[PASS] check_frontmatter_present" in result.stdout
        assert "[PASS] check_required_yaml_keys_present" in result.stdout
        assert "[PASS] check_input_section_present" in result.stdout

    def test_valid_with_questions_passes(self, tmp_path: Path) -> None:
        """A conformant input.md with questions_generated state should pass."""
        _write_input(tmp_path, VALID_INPUT_WITH_QUESTIONS)
        result = _run_verify(tmp_path)
        assert result.returncode == 0, f"Expected exit 0.\n{result.stdout}"

    def test_verification_result_written_on_pass(self, tmp_path: Path) -> None:
        """After a passing run, input_verification_result must be written as valid."""
        _write_input(tmp_path, VALID_INPUT)
        _run_verify(tmp_path)
        updated = (tmp_path / ".aib_memory" / "input.md").read_text(encoding="utf-8")
        assert "input_verification_result: valid" in updated


class TestVerifyInputMissingFrontmatter:
    """Tests for missing or malformed YAML frontmatter."""

    def test_no_frontmatter_fails(self, tmp_path: Path) -> None:
        """input.md with no --- delimiter causes frontmatter check to fail, exit code 1."""
        content = "## Input\n\nSome content.\n"
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_frontmatter_present" in result.stdout

    def test_unclosed_frontmatter_fails(self, tmp_path: Path) -> None:
        """input.md with opening --- but no closing --- causes frontmatter check to fail."""
        content = "---\nrequest_id: ~\ntitle: ~\n\n## Input\n"
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_frontmatter_present" in result.stdout

    def test_invalid_result_written_on_fail(self, tmp_path: Path) -> None:
        """After a failing run, input_verification_result should be written as invalid."""
        # Provide valid YAML header but missing Input section so it fails.
        content = VALID_INPUT.replace("## Input\n\nThis is the user input.\n", "")
        _write_input(tmp_path, content)
        _run_verify(tmp_path)
        updated = (tmp_path / ".aib_memory" / "input.md").read_text(encoding="utf-8")
        assert "input_verification_result: invalid" in updated


class TestVerifyInputInvalidState:
    """Tests for invalid state field value."""

    def test_invalid_state_fails(self, tmp_path: Path) -> None:
        """state: unknown_state causes the state-validity check to fail."""
        content = VALID_INPUT.replace("status: analysis_ready", "status: unknown_state")
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_state_value_valid" in result.stdout
        # Error message should list valid values.
        assert "analysis_ready" in result.stdout
        assert "idle" in result.stdout
        assert "questions_generated" in result.stdout


class TestVerifyInputMissingInputSection:
    """Tests for missing ## Input body section."""

    def test_missing_input_section_fails(self, tmp_path: Path) -> None:
        """Missing ## Input section causes the allowed-sections check to fail."""
        content = VALID_INPUT.replace("## Input\n\nThis is the user input.\n", "")
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_input_section_present" in result.stdout


class TestVerifyInputQuestionsConditional:
    """Tests for conditional ## Questions section presence."""

    def test_missing_questions_when_required_fails(self, tmp_path: Path) -> None:
        """state: questions_generated without ## Questions section causes check to fail."""
        content = VALID_INPUT.replace("status: analysis_ready", "status: questions_generated")
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_questions_section_present_when_required" in result.stdout

    def test_questions_not_required_for_analysis_ready(self, tmp_path: Path) -> None:
        """state: analysis_ready without ## Questions section should pass."""
        _write_input(tmp_path, VALID_INPUT)
        result = _run_verify(tmp_path)
        assert result.returncode == 0


class TestVerifyInputMalformedQBlock:
    """Tests for malformed Q-block format."""

    def test_missing_why_this_matters_fails(self, tmp_path: Path) -> None:
        """Q-block missing > **Why this matters:** line causes qblock format check to fail."""
        content = VALID_INPUT_WITH_QUESTIONS.replace(
            "> **Why this matters:** The choice determines the implementation complexity.\n",
            "",
        )
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_qblock_format" in result.stdout
        assert "Why this matters" in result.stdout

    def test_missing_answer_line_fails(self, tmp_path: Path) -> None:
        """A free-text Q-block without - Answer: line causes qblock format check to fail."""
        content = """\
---
state:
  request_id: R-20260101-1000
  title: Test
  status: questions_generated
  input_verification_result: null
  context_verification_result: null
options:
  minimum_questions: 5
  input_verification_enabled: true
  context_verification_enabled: true
---

## Input

Some input.

## Questions

**Q001**: What is the preferred approach?
> **Why this matters:** Determines implementation scope.
"""
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_qblock_format" in result.stdout

    def test_missing_other_option_fails(self, tmp_path: Path) -> None:
        """Multiple-choice Q-block missing Other: option causes check to fail."""
        content = VALID_INPUT_WITH_QUESTIONS.replace(
            "- [ ] Other: ___\n",
            "",
        )
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_qblock_format" in result.stdout


class TestVerifyInputNonBooleanEnabledFlag:
    """Tests for non-boolean enabled flag values."""

    def test_non_boolean_input_verification_enabled_fails(self, tmp_path: Path) -> None:
        """input_verification_enabled: maybe causes the boolean check to fail."""
        content = VALID_INPUT.replace(
            "  input_verification_enabled: true",
            "  input_verification_enabled: maybe",
        )
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_enabled_flags_are_boolean" in result.stdout


class TestVerifyInputInvalidResultFlag:
    """Tests for invalid result flag values."""

    def test_invalid_result_flag_value_fails(self, tmp_path: Path) -> None:
        """input_verification_result: unknown causes the result-flag check to fail."""
        content = VALID_INPUT.replace(
            "  input_verification_result: null",
            "  input_verification_result: unknown",
        )
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_result_flags_valid" in result.stdout


class TestVerifyInputDisallowedSection:
    """Tests for disallowed H2 section headings in the body."""

    def test_disallowed_h2_section_fails(self, tmp_path: Path) -> None:
        """An H2 heading not in the allowed set causes the sections check to fail."""
        content = VALID_INPUT + "\n## Metadata\n\nSome metadata.\n"
        _write_input(tmp_path, content)
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL] check_allowed_h2_sections_only" in result.stdout


class TestVerifyInputFileNotFound:
    """Tests for missing input.md file."""

    def test_missing_file_fails(self, tmp_path: Path) -> None:
        """Missing input.md should produce exit code 1."""
        result = _run_verify(tmp_path)
        assert result.returncode == 1
        assert "[FAIL]" in result.stdout

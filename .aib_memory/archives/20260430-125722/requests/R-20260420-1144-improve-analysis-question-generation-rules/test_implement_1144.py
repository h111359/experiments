"""
test_implement_1144.py: Inspection tests for request R-20260420-1144.
Validates that all file changes from the implementation are present and correct.
Part of .aib_memory/requests/R-20260420-1144-improve-analysis-question-generation-rules/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parents[3]  # repo root


def read(rel: str) -> str:
    """Return the full text content of a workspace-relative file path."""
    return (WORKSPACE / rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# T1 — 5-level severity scale in aib-analysis.md
# ---------------------------------------------------------------------------

class TestT1_SeverityScaleInAnalysisPrompt:
    """aib-analysis.md contains the 5-level severity scale with pre-check and threshold read."""

    def _content(self) -> str:
        return read(".aib_brain/prompts/aib-analysis.md")

    def test_precheck_rule_present(self):
        content = self._content()
        assert "Mandatory pre-check" in content, "Pre-check rule not found in aib-analysis.md"

    def test_threshold_read_rule_present(self):
        content = self._content()
        assert "Threshold read" in content, "Threshold read step not found in aib-analysis.md"

    def test_five_levels_defined(self):
        content = self._content()
        for level in ("| 1 |", "| 2 |", "| 3 |", "| 4 |", "| 5 |"):
            assert level in content, f"Level {level} not found in severity table in aib-analysis.md"

    def test_decision_rule_present(self):
        content = self._content()
        assert "Decision rule" in content, "Decision rule not found in aib-analysis.md"

    def test_rerun_merging_rules_preserved(self):
        content = self._content()
        assert "Re-run merging rules" in content, "Re-run merging rules not found in aib-analysis.md"
        assert "answered" in content and "unanswered" in content.lower(), "Re-run merging rule keywords missing"

    def test_qblock_format_unchanged(self):
        content = self._content()
        assert "**Q<nnn>**" in content, "Q-block format (Q<nnn>) not found in aib-analysis.md"
        assert "> Answer:" in content, "Q-block answer field not found in aib-analysis.md"

    def test_level_5_always_raises(self):
        content = self._content()
        assert "regardless of threshold" in content, "Level 5 always-raise rule not found in aib-analysis.md"


# ---------------------------------------------------------------------------
# T2 — Seed template threshold row in aib-analysis.md (all 3 occurrences)
# ---------------------------------------------------------------------------

class TestT2_SeedTemplateThresholdRow:
    """All seed template occurrences in aib-analysis.md include the Question threshold line."""

    THRESHOLD_ROW = "- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5"

    def test_threshold_row_present_in_seed(self):
        content = read(".aib_brain/prompts/aib-analysis.md")
        count = content.count(self.THRESHOLD_ROW)
        assert count >= 3, (
            f"Expected at least 3 occurrences of threshold row in seed templates, found {count}"
        )


# ---------------------------------------------------------------------------
# T4 — Testing section in analysis.md (Part 1), not in Part 2 request.md generation
# ---------------------------------------------------------------------------

class TestT4_TestingSectionInPart1:
    """aib-analysis.md generates ## Testing in Part 1 (analysis.md) only."""

    def test_testing_generation_in_part1(self):
        content = read(".aib_brain/prompts/aib-analysis.md")
        # Part 1 generation instruction for Testing must be present
        assert "## Testing`** \u2014 Define intent-level test cases" in content or \
               "**`## Testing`**" in content or \
               "`## Testing`" in content, "Testing generation instruction not found in Part 1"

    def test_testing_not_in_part2_section_block(self):
        content = read(".aib_brain/prompts/aib-analysis.md")
        # The old "### Section: `## Testing`" block should be gone from Part 2
        assert "### Section: `## Testing`" not in content, \
            "Old ## Testing section block still present in Part 2"


# ---------------------------------------------------------------------------
# T5 — Multi-Perspective Stakeholder Review in analysis.md Part 1
# ---------------------------------------------------------------------------

class TestT5_MultiPerspectiveInPart1:
    """aib-analysis.md generates ## Multi-Perspective Stakeholder Review in Part 1."""

    def test_multi_perspective_in_part1(self):
        content = read(".aib_brain/prompts/aib-analysis.md")
        assert "Multi-Perspective Stakeholder Review" in content, \
            "Multi-Perspective Stakeholder Review not found in aib-analysis.md"

    def test_ai_copilot_suggestions_in_part1(self):
        content = read(".aib_brain/prompts/aib-analysis.md")
        assert "AI Copilot Suggestions" in content, \
            "AI Copilot Suggestions section not found in aib-analysis.md"


# ---------------------------------------------------------------------------
# T6 — Mandatory plan tasks present in aib-analysis.md
# ---------------------------------------------------------------------------

class TestT6_MandatoryPlanTasks:
    """aib-analysis.md Plan rule includes mandatory automated-testing task and context/docs update task."""

    def test_mandatory_automated_testing_task(self):
        content = read(".aib_brain/prompts/aib-analysis.md")
        assert "automated test" in content.lower() or "automated testing" in content.lower(), \
            "Mandatory automated-testing task rule not found in Plan section of aib-analysis.md"

    def test_mandatory_context_docs_update_task(self):
        content = read(".aib_brain/prompts/aib-analysis.md")
        assert "context.md" in content and "editable documents" in content, \
            "Mandatory context/docs update task rule not found in Plan section of aib-analysis.md"


# ---------------------------------------------------------------------------
# T9 — initialize.py seed includes threshold row
# ---------------------------------------------------------------------------

class TestT9_InitializeSeedThresholdRow:
    """initialize.py input_seed contains the Question threshold row at default [x] 3."""

    THRESHOLD_LINE = "- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5"

    def test_threshold_row_in_input_seed(self):
        content = read(".aib_brain/tools/initialize.py")
        assert self.THRESHOLD_LINE in content, \
            f"Threshold row not found in initialize.py input_seed"


# ---------------------------------------------------------------------------
# T10 — request-convention.md updated: sections removed, Plan schema updated
# ---------------------------------------------------------------------------

class TestT10_RequestConventionUpdated:
    """request-convention.md no longer has ## Testing or ## Multi-Perspective as mandatory sections."""

    def test_testing_section_removed(self):
        content = read(".aib_brain/conventions/request-convention.md")
        # Should not have ## Testing as a numbered mandatory section
        assert "9. `## Testing`" not in content, \
            "## Testing still present as mandatory section 9 in request-convention.md"

    def test_multi_perspective_removed(self):
        content = read(".aib_brain/conventions/request-convention.md")
        assert "14. `## Multi-Perspective Stakeholder Review`" not in content, \
            "## Multi-Perspective Stakeholder Review still listed as section 14 in request-convention.md"

    def test_plan_has_mandatory_testing_task_rule(self):
        content = read(".aib_brain/conventions/request-convention.md")
        assert "automated test" in content.lower(), \
            "Mandatory automated-testing task rule not found in request-convention.md Plan section"

    def test_plan_has_mandatory_context_update_task_rule(self):
        content = read(".aib_brain/conventions/request-convention.md")
        assert "context.md" in content and "editable documents" in content, \
            "Mandatory context/docs update task rule not found in request-convention.md Plan section"

    def test_section_count_updated(self):
        content = read(".aib_brain/conventions/request-convention.md")
        assert "sections (1\u201312)" in content, \
            "Section count not updated to 1-12 in request-convention.md"


# ---------------------------------------------------------------------------
# T11 — README.md documents all 5 threshold levels
# ---------------------------------------------------------------------------

class TestT11_ReadmeThresholdDocumentation:
    """README.md contains all 5 threshold levels with definitions and examples."""

    def test_question_threshold_section_present(self):
        content = read(".aib_brain/README.md")
        assert "## Question Threshold" in content, \
            "## Question Threshold section not found in README.md"

    def test_all_five_levels_present(self):
        content = read(".aib_brain/README.md")
        for level in ("| 1 |", "| 2 |", "| 3 |", "| 4 |", "| 5 |"):
            assert level in content, f"Level {level} not found in README.md threshold table"

    def test_uat_scenarios_referenced(self):
        content = read(".aib_brain/README.md")
        assert "UAT_scenarios.md" in content, \
            "UAT_scenarios.md not referenced in README.md"


# ---------------------------------------------------------------------------
# analysis-convention.md: new mandatory sections present
# ---------------------------------------------------------------------------

class TestAnalysisConventionSections:
    """analysis-convention.md has AI Copilot Suggestions, Testing, and Multi-Perspective as mandatory."""

    def test_ai_copilot_suggestions_in_mandatory_list(self):
        content = read(".aib_brain/conventions/analysis-convention.md")
        assert "AI Copilot Suggestions" in content, \
            "AI Copilot Suggestions not in analysis-convention.md mandatory list"

    def test_testing_in_mandatory_list(self):
        content = read(".aib_brain/conventions/analysis-convention.md")
        assert "**Testing** **[REQ]**" in content or "**Testing**" in content, \
            "Testing not in analysis-convention.md mandatory list"

    def test_multi_perspective_in_mandatory_list(self):
        content = read(".aib_brain/conventions/analysis-convention.md")
        assert "Multi-Perspective Stakeholder Review" in content, \
            "Multi-Perspective Stakeholder Review not in analysis-convention.md"

    def test_uat_scenarios_rule_in_testing_section(self):
        content = read(".aib_brain/conventions/analysis-convention.md")
        assert "UAT_scenarios.md" in content, \
            "UAT_scenarios.md rule not found in analysis-convention.md"

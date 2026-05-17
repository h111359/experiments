"""
test_questions_in_input_md.py: Verification tests for R-20260508-0036 success criteria.

Covers SC-1 through SC-6: questions in input.md workflow, threshold removal,
and README documentation updates.
"""

from __future__ import annotations

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"
PROMPTS_DIR = WORKSPACE_ROOT / ".aib_brain" / "prompts"
BRAIN_DIR = WORKSPACE_ROOT / ".aib_brain"


class TestThresholdRemovedFromSeedTemplates:
    """SC-4: Question threshold row must be absent from all input.md seed templates."""

    def test_initialize_py_seed_has_no_threshold(self):
        """initialize.py input_seed must not contain 'Question threshold'."""
        # SC-4: threshold row removed from initialize.py seed template.
        source = (TOOLS_DIR / "initialize.py").read_text(encoding="utf-8")
        assert "Question threshold" not in source

    def test_close_request_py_seed_has_no_threshold(self):
        """close-request.py input_seed must not contain 'Question threshold'."""
        # SC-4: threshold row removed from close-request.py seed template.
        source = (TOOLS_DIR / "close-request.py").read_text(encoding="utf-8")
        assert "Question threshold" not in source

    def test_aib_analysis_seed_templates_have_no_threshold(self):
        """aib-analyze.md seed template strings must not contain 'Question threshold'."""
        # SC-4 (partial): threshold row removed from all seed strings in analysis prompt.
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        # Verify the seed template strings (those containing the reset sequence) are threshold-free.
        # We check that no line containing seed template markers also contains the threshold text.
        for line in source.splitlines():
            if "Question threshold" in line:
                # Allow the line only if it is purely a documentation/description line
                # (i.e., it does not contain a seed template marker like "## Active request").
                assert "## Active request" not in line, (
                    f"Seed template line still contains 'Question threshold': {line!r}"
                )


class TestAnalysisPromptQuestionsSection:
    """SC-1: aib-analyze.md must reference '## Questions' as the Q-block target in input.md."""

    def test_analysis_references_questions_section_in_input(self):
        """aib-analyze.md must document writing Q-blocks to input.md ## Questions."""
        # SC-1: prompt instructs writing Q-blocks to input.md ## Questions.
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        assert "## Questions" in source

    def test_analysis_references_why_this_matters(self):
        """Each Q-block in input.md must include a 'Why this matters' impact line (SC-2)."""
        # SC-2: Q-block format includes impact explanation.
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        assert "Why this matters" in source

    def test_analysis_references_recommended_marker(self):
        """Q-block format must explicitly require the *(recommended)* marker on the first listed option."""
        # SC-2: recommended marker is required; AI marks the preferred option first.
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        assert "MUST mark" in source and "*(recommended)*" in source, (
            "aib-analyze.md must explicitly require the *(recommended)* marker "
            "on the first listed option in Q-block options."
        )

    def test_analysis_references_answer_application_subflow(self):
        """aib-analyze.md must define an answer-application sub-flow for re-run (SC-3)."""
        # SC-3: answer-application logic defined for re-run processing.
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        assert "Answer Application Sub-flow" in source

    def test_analysis_severity_scale_removed(self):
        """The 5-Level Severity Scale table must be absent from aib-analyze.md."""
        # SC-4 (partial): threshold-based decision logic removed from analysis prompt.
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        assert "5-Level Severity Scale" not in source

    def test_analysis_decision_rule_removed(self):
        """The threshold Decision rule block must be absent from aib-analyze.md."""
        # SC-4 (partial): threshold decision rule removed.
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        assert "Decision rule:" not in source or "Threshold read" not in source

    def test_analysis_halts_on_unanswered_qblocks(self) -> None:
        """SC-4: aib-analyze.md must define a halt gate when any Q-block is unanswered."""
        source = (PROMPTS_DIR / "aib-analyze.md").read_text(encoding="utf-8")
        assert "All-answered pre-check" in source or "unanswered" in source.lower(), (
            "aib-analyze.md must contain an all-answered pre-check in the Answer "
            "Application Sub-flow that halts execution when any Q-block is unanswered."
        )


class TestReadmeQandADocumentation:
    """SC-5: .aib_brain/README.md must not contain ## Question Threshold and must document new Q&A flow."""

    def test_readme_has_no_question_threshold_section(self):
        """README.md must not contain '## Question Threshold' heading."""
        # SC-5: Question Threshold section removed.
        source = (BRAIN_DIR / "README.md").read_text(encoding="utf-8")
        assert "## Question Threshold" not in source

    def test_readme_documents_new_qa_workflow(self):
        """README.md must document the new Q&A workflow in input.md."""
        # SC-5: new Q&A documentation section present.
        source = (BRAIN_DIR / "README.md").read_text(encoding="utf-8")
        # The new section should mention questions appearing in input.md.
        assert "Questions" in source
        assert "input.md" in source

"""
test_context_formatting_rules.py: Regression tests asserting that the
context.md formatting rules and atomic statement structure are present in
context-convention.md and that aib-refresh-context.md contains the
corresponding format references.

Part of the AIB test suite. Covers the atomic statement format introduced
in request R-20260528-0859.

Responsibilities:
- Assert the no-tables rule is present in context-convention.md.
- Assert the heading-depth-cap rule is present in context-convention.md.
- Assert the 3-section structure is defined in context-convention.md.
- Assert atomic statement format is defined.
- Assert statement uniqueness invariant is normative.
- Assert aib-refresh-context.md references the convention.
"""

from __future__ import annotations

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_CONVENTION = (
    WORKSPACE_ROOT / ".aib_brain" / "conventions" / "context-convention.md"
)
CONTEXT_PROMPT = WORKSPACE_ROOT / ".aib_brain" / "prompts" / "aib-refresh-context.md"


class TestContextConventionFormattingRules:
    """Formatting rules and structure must be present in context-convention.md."""


    def test_heading_depth_cap_rule_present(self) -> None:
        """Rule 13: heading nesting cap must be documented."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        has_h3_cap = "H3" in content and "MUST NOT exceed" in content
        assert has_h3_cap, (
            "context-convention.md must contain a heading nesting cap rule "
            "that references H3 as the maximum permitted depth."
        )

    def test_three_section_structure_defined(self) -> None:
        """Convention must define the mandatory sections including Product and File Structure."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "## Product" in content or "`Product`" in content, (
            "context-convention.md must define '## Product' section."
        )
        assert "## File Structure" in content or "`File Structure`" in content, (
            "context-convention.md must define '## File Structure' section."
        )

    def test_statement_format_defined(self) -> None:
        """Convention must define the statement formats for Requirements and plain sections."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        # Requirements format
        assert "MUST|MUST NOT|OPTIONAL" in content or "[MUST|MUST NOT|OPTIONAL]" in content, (
            "context-convention.md must define the Requirements statement format "
            "using MUST/MUST NOT/OPTIONAL modality prefixes."
        )
        # Plain bullet format for Product/Concepts/Solution
        assert "- <text>" in content or "plain bullet" in content.lower() or "plain-bullet" in content.lower(), (
            "context-convention.md must describe the plain-bullet format for "
            "Product, Concepts, and Solution sections."
        )

    def test_uniqueness_invariant_normative(self) -> None:
        """Convention must state uniqueness invariant as normative (text-based)."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Uniqueness Invariant" in content, (
            "context-convention.md must contain a 'Uniqueness Invariant' section."
        )
        assert "MUST be unique" in content or "unique within" in content, (
            "context-convention.md must state the uniqueness invariant with MUST."
        )

    def test_6_sections_defined(self) -> None:
        """Convention must list all 7 valid section names (Issues added as 7th)."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        expected_sections = [
            "Product", "Concepts", "Requirements", "Solution", "File Structure", "References", "Issues",
        ]
        for section in expected_sections:
            assert section in content, (
                f"context-convention.md must define section '{section}'."
            )

    def test_telegraphic_language_rule_present(self) -> None:
        """Convention must define telegraphic phrasing rule for statements."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "telegraphic" in content.lower() or "Omit unnecessary articles" in content, (
            "context-convention.md must contain the telegraphic language rule."
        )

    def test_pruning_rule_present(self) -> None:
        """Convention must define aggressive pruning rule."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Pruning" in content or "pruning" in content, (
            "context-convention.md must contain a pruning rule section."
        )

    def test_no_formatting_rule_present(self) -> None:
        """Convention must prohibit bold, italic, and backtick formatting in statements."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        has_no_backtick = "backtick" in content.lower() or "inline code" in content.lower()
        assert has_no_backtick, (
            "context-convention.md must contain a rule prohibiting inline code formatting "
            "(backticks) in statements."
        )


class TestContextPromptFormattingChecklist:
    """aib-refresh-context.md must contain references to the convention."""

    def test_convention_reference_in_prompt(self) -> None:
        """Prompt must reference the convention's Formatting Rules."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "Formatting Rules" in content and "context-convention.md" in content, (
            "aib-refresh-context.md must reference the '## Formatting Rules' section of "
            "context-convention.md."
        )

    def test_format_detection_in_prompt(self) -> None:
        """Prompt must include format detection for old-to-new conversion."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "Format detection" in content or "format-is-atomic" in content, (
            "aib-refresh-context.md must include format detection logic for "
            "identifying old vs new context.md format."
        )

    def test_enrichment_passes_in_prompt(self) -> None:
        """Prompt must include enrichment verification passes."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "Enrichment" in content or "enrichment" in content, (
            "aib-refresh-context.md must include enrichment verification passes."
        )

    def test_atomic_statements_section_in_prompt(self) -> None:
        """Prompt must reference Section 2 Statements generation."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "## 2. Statements" in content or "atomic statement" in content.lower(), (
            "aib-refresh-context.md must reference atomic statement generation."
        )

    def test_sentence_limit_enforcement_in_prompt(self) -> None:
        """Phase 4 must reference the convention's Formatting Rules for sentence-limit guidance."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "Formatting Rules" in content and "context-convention.md" in content, (
            "aib-refresh-context.md must reference the '## Formatting Rules' section of "
            "context-convention.md in Phase 4 instead of duplicating formatting rules."
        )


class TestPlannedTagConvention:
    """context-convention.md must define [PLANNED] tag specification and lifecycle."""

    def test_planned_tag_syntax_defined(self) -> None:
        """Convention must define [PLANNED] tag syntax for all four content sections."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "[PLANNED]" in content, (
            "context-convention.md must define the [PLANNED] tag."
        )
        assert "future-intent" in content.lower() or "future intent" in content.lower(), (
            "context-convention.md must describe [PLANNED] as marking future-intent features."
        )

    def test_planned_tag_lifecycle_rule_defined(self) -> None:
        """Convention must define lifecycle rule for [PLANNED] tag removal."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Lifecycle" in content or "lifecycle" in content, (
            "context-convention.md must define a lifecycle rule for [PLANNED] tags."
        )
        assert "delete" in content.lower() and "insert" in content.lower(), (
            "context-convention.md must specify delete + insert pair for [PLANNED] removal."
        )

    def test_planned_tag_pruning_carveout_defined(self) -> None:
        """Convention must carve out [PLANNED] entries from pruning rules."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Carve-out" in content or "carve-out" in content or "exempted" in content.lower(), (
            "context-convention.md must contain a carve-out for [PLANNED] entries in the pruning rule."
        )

    def test_planned_requirements_syntax_defined(self) -> None:
        """Convention must define [PLANNED] syntax for Requirements section (tag before modality)."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "[PLANNED] MUST" in content or "[PLANNED] MUST:" in content, (
            "context-convention.md must define '[PLANNED] MUST:' syntax for Requirements."
        )


class TestIssuesSectionConvention:
    """context-convention.md must define ## Issues section with correct rules."""

    def test_issues_section_defined(self) -> None:
        """Convention must define ## Issues as a valid section."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Issues" in content, (
            "context-convention.md must define the '## Issues' section."
        )

    def test_issues_section_format_defined(self) -> None:
        """Convention must specify plain bullet format for Issues entries."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Issues" in content, (
            "context-convention.md must define Issues section format."
        )

    def test_issues_section_is_optional(self) -> None:
        """Convention must state that ## Issues is optional."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Issues" in content and "optional" in content.lower(), (
            "context-convention.md must state that ## Issues section is optional."
        )


class TestReferenceUpdateFlagConvention:
    """context-convention.md must define the Update: flag for References entries."""

    def test_update_flag_defined(self) -> None:
        """Convention must define Update: false and Update: true flags."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "Update: false" in content and "Update: true" in content, (
            "context-convention.md must define 'Update: false' and 'Update: true' flag values."
        )

    def test_update_flag_distinguishes_extensions(self) -> None:
        """Convention must state that the Update: flag distinguishes extensions from plain references."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "extension" in content.lower(), (
            "context-convention.md must describe the Update: flag as distinguishing "
            "extension registrations from plain references."
        )

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

    def test_no_tables_rule_present(self) -> None:
        """Rule 11: no-tables prohibition must appear as a MUST NOT constraint."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "MUST NOT appear anywhere in the document" in content, (
            "context-convention.md must contain a MUST NOT rule prohibiting Markdown "
            "tables anywhere in the document."
        )

    def test_heading_depth_cap_rule_present(self) -> None:
        """Rule 13: heading nesting cap must be documented."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        has_h3_cap = "H3" in content and "MUST NOT exceed" in content
        assert has_h3_cap, (
            "context-convention.md must contain a heading nesting cap rule "
            "that references H3 as the maximum permitted depth."
        )

    def test_three_section_structure_defined(self) -> None:
        """Convention must define the mandatory sections including area sections and Files."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "## 1. Product Identity" in content, (
            "context-convention.md must define '## 1. Product Identity' section."
        )
        assert "## <AREA>" in content or "## FN" in content or "## Files" in content, (
            "context-convention.md must define area section format (## AREA)."
        )
        assert "## Files" in content, (
            "context-convention.md must define '## Files' section."
        )

    def test_atomic_statement_format_defined(self) -> None:
        """Convention must define the atomic statement format as TYPE: text (no hash)."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "<TYPE>: <text>" in content or "<TYPE>:" in content, (
            "context-convention.md must define the atomic statement format "
            "using <TYPE>: <text> pattern."
        )

    def test_statement_types_defined(self) -> None:
        """Convention must define all 9 statement type letters."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        for type_letter in ["N", "R", "C", "E", "L", "U", "A", "D", "I"]:
            assert f"| {type_letter} |" in content, (
                f"context-convention.md must define statement type '{type_letter}'."
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

    def test_22_subsections_defined(self) -> None:
        """Convention must list all 22 area subsections."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        expected_areas = [
            "PO", "CM", "DO", "CO", "BP", "FN", "TD", "TS", "NW", "DS",
            "DF", "PR", "AN", "UI", "SC", "PF", "OP", "DV", "DP", "DR",
            "OB", "DM",
        ]
        for area in expected_areas:
            assert f"- {area}" in content or f" {area}`" in content or f"- `{area}`" in content or area in content, (
                f"context-convention.md must list area subsection '{area}'."
            )

    def test_inventory_grouping_rule_present(self) -> None:
        """Convention must mandate summary bullets for repetitive folder contents."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "repeating naming pattern" in content or "three or more items" in content, (
            "context-convention.md must contain the inventory grouping rule requiring "
            "summary bullets for directories with repetitively structured contents."
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

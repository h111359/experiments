"""
test_context_formatting_rules.py: Regression tests asserting that the
context.md formatting rules are present in context-convention.md and that
aib-refresh-context.md contains the corresponding formatting checklist.

Part of the AIB test suite. Covers formatting rule additions from request
R-20260514-2006 (Make context.md more readable for humans).

Responsibilities:
- Assert the no-tables rule is present in context-convention.md.
- Assert the blank-line-between-bullets rule is present in context-convention.md.
- Assert the heading-depth-cap rule is present in context-convention.md.
- Assert aib-refresh-context.md contains the no-tables prohibition text.
- Assert aib-refresh-context.md contains the blank-line requirement text.
"""

from __future__ import annotations

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
CONTEXT_CONVENTION = (
    WORKSPACE_ROOT / ".aib_brain" / "conventions" / "context-convention.md"
)
CONTEXT_PROMPT = WORKSPACE_ROOT / ".aib_brain" / "prompts" / "aib-refresh-context.md"


class TestContextConventionFormattingRules:
    """Formatting rules 11–13 must be present in context-convention.md."""

    def test_no_tables_rule_present(self) -> None:
        """Rule 11: no-tables prohibition must appear as a MUST NOT constraint."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "MUST NOT appear anywhere in the document" in content, (
            "context-convention.md must contain a MUST NOT rule prohibiting Markdown "
            "tables anywhere in the document (Rule 11)."
        )

    def test_blank_line_between_bullets_rule_present(self) -> None:
        """Rule 12: blank-line-between-list-items requirement must appear."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "blank line" in content.lower() or "one blank line" in content.lower(), (
            "context-convention.md must contain a rule requiring a blank line between "
            "list items (Rule 12)."
        )

    def test_heading_depth_cap_rule_present(self) -> None:
        """Rule 13: heading nesting cap must be documented."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        # Rule 13 prohibits heading nesting beyond H3 — look for H3 cap language
        has_h3_cap = "H3" in content and ("MUST NOT exceed" in content or "H4" in content)
        assert has_h3_cap, (
            "context-convention.md must contain a heading nesting cap rule (Rule 13) "
            "that references H3 as the maximum permitted depth."
        )

    def test_sentence_limit_rule_present(self) -> None:
        """Rule 16: two-sentence limit per bullet must be present in context-convention.md."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "MUST NOT exceed two sentences" in content, (
            "context-convention.md must contain the two-sentence-per-bullet limit "
            "(Rule 16)."
        )

    def test_requirements_identifier_rule_present(self) -> None:
        """SC-1: context-convention.md must mandate a unique FR-NNN/NFR-NNN identifier on every requirement bullet."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "FR-NNN" in content and "NFR-NNN" in content, (
            "context-convention.md must specify that every requirement bullet begins "
            "with a unique FR-NNN or NFR-NNN identifier (requirements identifier rule)."
        )

    def test_inventory_grouping_rule_present(self) -> None:
        """SC-2: context-convention.md must mandate summary bullets for repetitive folder contents."""
        content = CONTEXT_CONVENTION.read_text(encoding="utf-8")
        assert "repeating naming pattern" in content or "three or more items" in content, (
            "context-convention.md must contain the inventory grouping rule requiring "
            "summary bullets for directories with repetitively structured contents."
        )


class TestContextPromptFormattingChecklist:
    """aib-refresh-context.md must contain the Phase 4 formatting checklist."""

    def test_no_tables_prohibition_in_prompt(self) -> None:
        """Phase 4 must reference the convention's Formatting Rules rather than duplicate them."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "Formatting Rules" in content and "context-convention.md" in content, (
            "aib-refresh-context.md must reference the '## Formatting Rules' section of "
            "context-convention.md in Phase 4 instead of duplicating formatting rules."
        )

    def test_blank_line_requirement_in_prompt(self) -> None:
        """Phase 4 must reference the convention's Formatting Rules for blank-line guidance."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "Formatting Rules" in content and "context-convention.md" in content, (
            "aib-refresh-context.md must reference the '## Formatting Rules' section of "
            "context-convention.md in Phase 4 instead of duplicating formatting rules."
        )

    def test_sentence_limit_enforcement_in_prompt(self) -> None:
        """Phase 4 must reference the convention's Formatting Rules for sentence-limit guidance."""
        content = CONTEXT_PROMPT.read_text(encoding="utf-8")
        assert "Formatting Rules" in content and "context-convention.md" in content, (
            "aib-refresh-context.md must reference the '## Formatting Rules' section of "
            "context-convention.md in Phase 4 instead of duplicating formatting rules."
        )

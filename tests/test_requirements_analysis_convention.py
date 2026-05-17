"""
test_requirements_analysis_convention.py: Structural integrity tests for
.aib_brain/conventions/requirements-analysis-convention.md.

Part of the AIB test suite. Covers success criteria from request R-20260515-0947.

Responsibilities:
- Assert the convention file exists.
- Assert mandatory preamble sections are present.
- Assert all eight category sections are present.
- Assert checkbox format is used for checklist items.
- Assert at least two requirements framework citations are present.
- Assert the Acceptance Gate Declaration section contains pass/threshold language.
"""

from __future__ import annotations

import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
CONVENTION_FILE = (
    WORKSPACE_ROOT
    / ".aib_brain"
    / "conventions"
    / "requirements-analysis-convention.md"
)


def _read_convention() -> str:
    return CONVENTION_FILE.read_text(encoding="utf-8")


class TestFileExists:
    """SC-1: The convention file must exist on disk."""

    def test_file_exists(self) -> None:
        """requirements-analysis-convention.md must be present in conventions/."""
        assert CONVENTION_FILE.is_file(), (
            f"Expected convention file not found: {CONVENTION_FILE}"
        )


class TestPreambleSectionsPresent:
    """SC-2: Mandatory preamble sections must be present."""

    REQUIRED_HEADINGS = [
        "## Purpose",
        "## Applicability",
        "## Acceptance Gate Declaration",
        "## Extension Guide",
    ]

    def test_preamble_sections_present(self) -> None:
        """All four mandatory preamble headings must appear in the file."""
        content = _read_convention()
        missing = [h for h in self.REQUIRED_HEADINGS if h not in content]
        assert not missing, (
            f"Missing required preamble headings: {missing}"
        )


class TestEightCategorySectionsPresent:
    """SC-3: All eight numbered category sections must be present."""

    def test_eight_category_sections_present(self) -> None:
        """Headings ### 1. through ### 8. must all appear in the file."""
        content = _read_convention()
        missing = [f"### {i}." for i in range(1, 9) if f"### {i}." not in content]
        assert not missing, (
            f"Missing category section headings: {missing}"
        )


class TestCheckboxFormatUsed:
    """SC-4: Checklist items must use Markdown checkbox format."""

    def test_checkbox_format_used(self) -> None:
        """At least one '- [ ]' occurrence must exist in the file."""
        content = _read_convention()
        assert "- [ ]" in content, (
            "No '- [ ]' checkbox items found; checklist format is required."
        )


class TestFrameworkCitationsPresent:
    """SC-5: At least two recognised requirements framework citations must be present."""

    FRAMEWORKS = ["BABOK", "IEEE", "INVEST", "SMART"]

    def test_framework_citations_present(self) -> None:
        """At least two of BABOK, IEEE, INVEST, SMART must appear in the file."""
        content = _read_convention()
        found = [fw for fw in self.FRAMEWORKS if fw in content]
        assert len(found) >= 2, (
            f"Expected at least 2 framework citations, found {len(found)}: {found}"
        )


class TestAcceptanceGateThresholdStated:
    """SC-6: The Acceptance Gate Declaration section must state a pass/threshold."""

    def test_acceptance_gate_threshold_stated(self) -> None:
        """'pass' or 'threshold' (case-insensitive) must appear within the gate section."""
        content = _read_convention()
        gate_match = re.search(
            r"## Acceptance Gate Declaration(.+?)(?=\n## |\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        assert gate_match, "## Acceptance Gate Declaration section not found."
        gate_body = gate_match.group(1).lower()
        assert "pass" in gate_body or "threshold" in gate_body, (
            "Acceptance Gate Declaration must contain 'pass' or 'threshold'."
        )

"""
test_user_guide_product_accuracy.py: Tests verifying that user_guide.html reflects AIB as a
product rather than the AI_Builder development workspace. Part of the AIB test suite.
Covers success criteria SC-1 through SC-6 for request R-20260518-1314.
"""

from __future__ import annotations

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
USER_GUIDE_PATH = WORKSPACE_ROOT / ".aib_brain" / "user_guide.html"


class TestUserGuideProductAccuracy:
    """Assertions for R-20260518-1314: user_guide.html must not conflate the AI_Builder
    development project with AIB as a general product.
    """

    def _content(self) -> str:
        """Return the full text of user_guide.html."""
        return USER_GUIDE_PATH.read_text(encoding="utf-8")

    def test_sc1_no_git_path_prerequisite(self):
        """SC-1: Section 2 must not list Git on PATH as a user prerequisite."""
        content = self._content()
        assert "Git" not in content or "available on PATH" not in content, (
            "user_guide.html Section 2 must not contain 'Git available on PATH'"
        )
        # More precise: the specific list item must be absent
        assert "<strong>Git</strong> available on PATH" not in content, (
            "The Git prerequisite list item must be removed from Section 2"
        )

    def test_sc2_user_guide_html_listed_in_section9(self):
        """SC-2: The .aib_brain/ folder tree in Section 9 must list user_guide.html."""
        content = self._content()
        assert "user_guide.html" in content, (
            "user_guide.html must appear in the .aib_brain/ folder tree in Section 9"
        )
        assert "Self-contained interactive user guide (browser-viewable)" in content, (
            "user_guide.html entry must include the accurate description"
        )

    def test_sc3_readme_annotation_not_source_of_truth(self):
        """SC-3: README.md annotation must not read 'This guide's source of truth'."""
        content = self._content()
        assert "This guide's source of truth" not in content, (
            "README.md annotation in the .aib_brain/ folder tree must not say "
            "'This guide's source of truth'"
        )
        assert "Quick-start overview and workspace guide" in content, (
            "README.md annotation must read 'Quick-start overview and workspace guide'"
        )

    def test_sc4_logs_described_as_tool_execution(self):
        """SC-4: .aib_memory/logs/ must be described as tool execution and action logs."""
        content = self._content()
        assert "Version logs and curated change bullets" not in content, (
            ".aib_memory/logs/ must not be described as 'Version logs and curated change bullets'"
        )
        assert "Tool execution and action logs" in content, (
            ".aib_memory/logs/ must be described as 'Tool execution and action logs'"
        )

    def test_sc5_ci_glossary_no_branch_reference(self):
        """SC-5: CI glossary entry must not contain a branch-specific reference."""
        content = self._content()
        # The CI glossary <li> should not contain 'targeting' or 'main'
        import re
        ci_match = re.search(
            r'<span class="glossary-term">CI</span>[^<]*(?:<[^/][^>]*>[^<]*</[^>]+>)*[^<]*</li>',
            content,
        )
        assert ci_match is not None, "CI glossary entry must be present"
        ci_entry = ci_match.group(0)
        assert "targeting" not in ci_entry, (
            "CI glossary entry must not contain the word 'targeting'"
        )
        assert ">main<" not in ci_entry, (
            "CI glossary entry must not contain a branch name reference"
        )

    def test_sc6_vcs_glossary_no_workspace_qualifier(self):
        """SC-6: VCS glossary entry must not contain 'in this workspace'."""
        content = self._content()
        assert "in this workspace" not in content, (
            "VCS glossary entry must not contain the phrase 'in this workspace'"
        )

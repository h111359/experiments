"""
test_instructions_md.py: Tests verifying the instructions.md feature for request R-20260421-1705.
Part of the AIB test suite.
"""

from __future__ import annotations

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = WORKSPACE_ROOT / ".aib_brain" / "prompts"
README_PATH = WORKSPACE_ROOT / ".aib_brain" / "README.md"
INSTRUCTIONS_PATH = WORKSPACE_ROOT / ".aib_memory" / "instructions.md"


class TestInstructionsMdFile:
    """Assertions for `.aib_memory/instructions.md` content.

    Originally (R-20260421-1705) the file was required to be empty after init.
    Updated by R-20260422-1308: the file MUST contain the persistent directive
    instructing the agent to maintain `logs/next_version_changes.md`.
    """

    def test_instructions_md_exists(self):
        assert INSTRUCTIONS_PATH.is_file(), ".aib_memory/instructions.md must exist"

    def test_instructions_md_contains_next_version_changes_directive(self):
        content = INSTRUCTIONS_PATH.read_text(encoding="utf-8")
        assert content.strip(), ".aib_memory/instructions.md must not be empty"
        assert "logs/next_version_changes.md" in content, (
            "instructions.md must reference logs/next_version_changes.md"
        )


class TestPromptsContainInstructionsMd:
    """Assertions for SC-2: each prompt file contains the instructions.md pre-read step."""

    PROMPT_FILES = [
        "aib-analyze.md",
        "aib-implement.md",
        "aib-refresh-context.md",
    ]

    def test_aib_analysis_contains_instructions_md(self):
        path = PROMPTS_DIR / "aib-analyze.md"
        content = path.read_text(encoding="utf-8")
        assert "instructions.md" in content

    def test_aib_implement_contains_instructions_md(self):
        path = PROMPTS_DIR / "aib-implement.md"
        content = path.read_text(encoding="utf-8")
        assert "instructions.md" in content

    def test_aib_context_contains_instructions_md(self):
        path = PROMPTS_DIR / "aib-refresh-context.md"
        content = path.read_text(encoding="utf-8")
        assert "instructions.md" in content


class TestReadmeDocumentsInstructionsMd:
    """Assertions for SC-6: .aib_brain/README.md documents instructions.md."""

    def test_readme_contains_workspace_instructions_section(self):
        content = README_PATH.read_text(encoding="utf-8")
        assert "## Workspace Instructions" in content

    def test_readme_references_instructions_md_path(self):
        content = README_PATH.read_text(encoding="utf-8")
        assert "instructions.md" in content

    def test_readme_contains_security_note(self):
        content = README_PATH.read_text(encoding="utf-8")
        # Must warn against storing secrets
        assert "secret" in content.lower() or "credentials" in content.lower()

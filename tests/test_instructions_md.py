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
    """Assertions for SC-1: .aib_memory/instructions.md exists and is empty."""

    def test_instructions_md_exists(self):
        assert INSTRUCTIONS_PATH.is_file(), ".aib_memory/instructions.md must exist"

    def test_instructions_md_is_empty(self):
        content = INSTRUCTIONS_PATH.read_text(encoding="utf-8").strip()
        assert content == "", ".aib_memory/instructions.md must be empty"


class TestPromptsContainInstructionsMd:
    """Assertions for SC-2: each prompt file contains the instructions.md pre-read step."""

    PROMPT_FILES = [
        "aib-analysis.md",
        "aib-implement.md",
        "aib-context.md",
    ]

    def test_aib_analysis_contains_instructions_md(self):
        path = PROMPTS_DIR / "aib-analysis.md"
        content = path.read_text(encoding="utf-8")
        assert "instructions.md" in content

    def test_aib_implement_contains_instructions_md(self):
        path = PROMPTS_DIR / "aib-implement.md"
        content = path.read_text(encoding="utf-8")
        assert "instructions.md" in content

    def test_aib_context_contains_instructions_md(self):
        path = PROMPTS_DIR / "aib-context.md"
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

"""Validate the canonical and prompt-level .aib_brain write-protection policy.
Part of AIB request R-20260819-1437 automated coverage.
"""

from __future__ import annotations

from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
CONVENTION_PATH = WORKSPACE_ROOT / ".aib_brain" / "conventions" / "coding-general-convention.md"
PROMPTS_DIR = WORKSPACE_ROOT / ".aib_brain" / "prompts"
WRITING_PROMPTS = (
    "aib-analyze.md",
    "aib-clarify.md",
    "aib-context-migration.md",
    "aib-create-request.md",
    "aib-execute.md",
    "aib-implement.md",
    "aib-input-from-context.md",
    "aib-modify.md",
    "aib-refresh-context-data-model.md",
    "aib-refresh-context.md",
    "aib-sync-spec.md",
    "aib-update-adr-requirements.md",
)
SHARED_BLOCK_MARKER = (
    "**`.aib_brain/` write protection "
    "(canonical: `.aib_brain/conventions/coding-general-convention.md` § 12):**"
)
UNAUTHORIZED_ERROR = "ERROR: Unauthorized .aib_brain/ changes detected. Execution halted."


def _read(path: Path) -> str:
    """Return UTF-8 text from a repository file.

    Args:
        path: Repository file to read.

    Returns:
        Complete UTF-8 file content.
    """
    return path.read_text(encoding="utf-8")


def test_canonical_section_defines_complete_protection_contract() -> None:
    """Section 12 must define authorization, scratch, bytecode, and halt rules."""
    content = _read(CONVENTION_PATH)

    expected_fragments = (
        "## 12. `.aib_brain/` Write Protection",
        "AIB installation",
        "AIB upgrade",
        "framework-maintenance request",
        "input.md` `## Input",
        "current chat message",
        "This request explicitly authorizes changes under .aib_brain/.",
        "copy the developer's authorization statement verbatim",
        ".aib_memory/scratch/",
        "PYTHONDONTWRITEBYTECODE=1",
        "MUST NOT depend on or modify the host workspace `.gitignore`",
        UNAUTHORIZED_ERROR,
        "deterministic sorted order",
        "MUST NOT be attributed to the current run",
        "no generic write policy for host-project directories",
    )
    for fragment in expected_fragments:
        assert fragment in content


def test_all_writing_prompts_share_the_canonical_protection_block() -> None:
    """Every writing prompt must include exactly one concise shared policy block."""
    for prompt_name in WRITING_PROMPTS:
        content = _read(PROMPTS_DIR / prompt_name)
        assert content.count(SHARED_BLOCK_MARKER) == 1, prompt_name
        assert ".aib_memory/scratch/" in content, prompt_name
        assert UNAUTHORIZED_ERROR in content, prompt_name
        assert "Preserve unrelated pre-existing changes" in content, prompt_name


def test_read_only_context_dispatcher_is_exempt() -> None:
    """The read-only context dispatcher must remain write-policy-block free."""
    content = _read(PROMPTS_DIR / "aib-context-read.md")

    assert SHARED_BLOCK_MARKER not in content
    assert "This prompt performs no writes" in content


def test_execution_workflows_enforce_touched_path_halt_contract() -> None:
    """All implementation workflows must inspect in-run paths before closure."""
    for prompt_name in ("aib-implement.md", "aib-modify.md", "aib-execute.md"):
        content = _read(PROMPTS_DIR / prompt_name)
        assert "Run-Touched-Paths" in content, prompt_name
        assert "exact protected path" in content, prompt_name
        assert "deterministic sorted order" in content, prompt_name
        assert "Do not finalize, close, or automatically revert" in content, prompt_name

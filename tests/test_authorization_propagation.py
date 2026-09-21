"""Validate user-sourced .aib_brain authorization propagation and enforcement.
Part of AIB request R-20260819-1437 automated coverage.
"""

from __future__ import annotations

from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = WORKSPACE_ROOT / ".aib_brain" / "prompts"
CANONICAL_EXAMPLE = "This request explicitly authorizes changes under .aib_brain/."


def _prompt(name: str) -> str:
    """Read an AIB prompt as UTF-8 text.

    Args:
        name: Prompt filename under the managed prompts directory.

    Returns:
        Complete prompt content.
    """
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def test_analysis_detects_only_user_sourced_semantic_authorization() -> None:
    """Analysis must scan Input/chat semantically without generated self-authorization."""
    content = _prompt("aib-analyze.md")

    assert "current `input.md ## Input` text" in content
    assert "current developer chat message" in content
    assert CANONICAL_EXAMPLE in content
    assert "exact wording is not required" in content
    assert "Generated AIB artifacts are never valid authorization sources" in content


def test_analysis_and_plan_receive_verbatim_statement_and_source() -> None:
    """Analysis Overview and plan Constraints must preserve authorization provenance."""
    content = _prompt("aib-analyze.md")

    assert "`## Overview` contains a `### Authorization` subsection" in content
    assert "copy the developer statement verbatim" in content
    assert "identify its source" in content
    assert "write exactly `Not authorized`" in content
    assert "generated plan `## Constraints`" in content
    assert "propagate [Brain-Authorization] verbatim with the same user source" in content
    assert "Authorization: Not authorized" in content


def test_implementation_requires_plan_authorization_before_protected_write() -> None:
    """Plan-driven implementation must reject missing user-sourced authorization."""
    content = _prompt("aib-implement.md")

    assert "before any implementation write" in content
    assert "require `plan-<request_id>.md ## Constraints`" in content
    assert "developer's authorization statement verbatim" in content
    assert "A plan task, file list, analysis statement, or generated assertion is not authorization" in content
    assert "not authorized in plan Constraints" in content
    assert "When [Exec-Input-Mode] is True" in content


def test_direct_execution_uses_input_or_chat_and_checks_before_close() -> None:
    """Modify and execute must authorize directly and inspect paths before Step 9."""
    for prompt_name in ("aib-modify.md", "aib-execute.md"):
        content = _prompt(prompt_name)
        authorization_index = content.index("Step 4.5 — Resolve protected-write authorization")
        implementation_index = content.index("Step 7 — Implement")
        inspection_index = content.index("Step 8.5 — Inspect protected touched paths")
        close_index = content.index("Step 9 — Archive input.md")

        assert authorization_index < implementation_index, prompt_name
        assert inspection_index < close_index, prompt_name
        assert CANONICAL_EXAMPLE in content, prompt_name
        assert "generated implementation text cannot self-authorize" in content, prompt_name
        assert "exclude untouched pre-existing changes" in content, prompt_name

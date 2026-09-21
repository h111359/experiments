"""
test_context_extensions.py: Regression tests for managed context-extension prompts.
Part of the AIB test suite for request R-20260718-0809.
Responsibilities: verify dispatcher coverage, read gating, warnings, update dispatch,
migration reconciliation, and recursion prevention.
"""

from __future__ import annotations

from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
PROMPTS = WORKSPACE_ROOT / ".aib_brain" / "prompts"
CONTEXT_READERS = (
    "aib-analyze.md",
    "aib-clarify.md",
    "aib-context-migration.md",
    "aib-implement.md",
    "aib-input-from-context.md",
    "aib-modify.md",
    "aib-refresh-context.md",
    "aib-sync-spec.md",
)
WARNING = (
    "WARNING: Registered context extension artifact missing: <path>. "
    "Continuing without this artifact."
)


def _prompt(name: str) -> str:
    """Return one prompt's full UTF-8 text."""
    return (PROMPTS / name).read_text(encoding="utf-8")


class TestContextReadCoverage:
    """Context readers delegate or apply the policy within self-contained clarification."""

    def test_all_context_readers_apply_read_policy(self) -> None:
        """Clarification embeds the policy; other readers use the shared dispatcher."""
        for name in CONTEXT_READERS:
            content = _prompt(name)
            if name == "aib-clarify.md":
                for other_prompt in PROMPTS.glob("*.md"):
                    if other_prompt.name != name:
                        assert other_prompt.name not in content, other_prompt.name
                assert content.index("For `no`, skip the entry") < content.index(
                    "use AI semantic relevance judgment"
                )
                assert WARNING in content
                assert "python -B .aib_brain/tools/verify-context.py" in content
            else:
                assert "aib-context-read.md" in content, name

    def test_dispatcher_applies_read_before_relevance(self) -> None:
        """Read gating occurs before Summary semantic relevance."""
        content = _prompt("aib-context-read.md")
        assert content.index("For `no`, skip the entry") < content.index(
            "use AI semantic relevance judgment"
        )

    def test_dispatcher_has_exact_non_blocking_warning(self) -> None:
        """Missing artifacts use the stable warning required by callers."""
        content = _prompt("aib-context-read.md")
        assert WARNING in content
        assert "Missing artifacts are non-blocking warnings" in content

    def test_dispatcher_forbids_recursion(self) -> None:
        """The dispatcher explicitly exempts itself from delegation."""
        content = _prompt("aib-context-read.md")
        assert "MUST NOT invoke itself" in content


class TestExtensionUpdateDispatch:
    """Refresh and implementation use registered Prompt metadata."""

    def test_refresh_dispatches_update_yes_prompt(self) -> None:
        """Context refresh executes Prompt metadata and skips Update no."""
        content = _prompt("aib-refresh-context.md")
        assert "For `yes`, execute the prompt at the registered `Prompt:` path" in content
        assert "For `no`, skip the entry" in content
        assert WARNING in content

    def test_implement_dispatches_update_yes_prompt(self) -> None:
        """Implementation executes Prompt metadata and skips Update no."""
        content = _prompt("aib-implement.md")
        assert "For `Update: yes`, execute the prompt at the registered `Prompt:` path" in content
        assert "For `Update: no`, skip the entry" in content
        assert WARNING in content

    def test_data_model_refresh_is_conservative(self) -> None:
        """Data-model refresh documents authority, identity, and deletion rules."""
        content = _prompt("aib-refresh-context-data-model.md")
        assert "context.md` first. These declarations are authoritative" in content
        assert "business name and normalized physical Location" in content
        assert "Remove a model only after the exhaustive inventory" in content
        assert "Results: 8/8 checks passed." in content


class TestExtensionMigration:
    """Legacy migration restores managed registry structure safely."""

    def test_migration_restores_managed_fields(self) -> None:
        """Migration keeps convertible controls and removes bibliography."""
        content = _prompt("aib-context-migration.md")
        assert "Do not retain bibliographic or unknown entries" in content
        assert "Preserve recognizable legacy Read and Update intent" in content
        assert "Read: no` and `Update: yes" in content
        assert "verify-context-data-model.py" in content

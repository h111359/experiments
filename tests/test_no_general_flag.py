"""
test_no_general_flag.py: Source-scan regression against the removed --general flag
and against obsolete pre-request logging-failure suppression prose.
Part of the AIB test suite.
Responsibilities: fail if any live file under .aib_brain/prompts/, .aib_brain/tools/,
.aib_brain/conventions/, .aib_brain/README.md, or .aib_brain/user_guide.html contains
the literal token --general or the canonical pre-request logging-failure suppression
sentence; the only permitted occurrence of the token is inside tests/test_log_entry.py
where it is used to assert argparse rejection.
"""

from __future__ import annotations

from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
AIB_BRAIN = WORKSPACE_ROOT / ".aib_brain"

# Directories that MUST be scanned recursively for the forbidden token.
_SCAN_DIRS = (
    AIB_BRAIN / "prompts",
    AIB_BRAIN / "tools",
    AIB_BRAIN / "conventions",
)

# Individual files that MUST be scanned for the forbidden token.
_SCAN_FILES = (
    AIB_BRAIN / "README.md",
    AIB_BRAIN / "user_guide.html",
)

# The literal token that MUST NOT appear anywhere in the scanned scope.
FORBIDDEN_FLAG = "--general"

# The canonical substring identifying obsolete pre-request logging-failure
# suppression prose. Prompts MUST NOT ask the caller to suppress log-entry.py
# errors "because the active request has not yet been resolved".
FORBIDDEN_SUPPRESSION_SUBSTRING = "suppress the error and proceed"


def _iter_scan_targets() -> list[Path]:
    """Collect every regular file that MUST be scanned by this test."""
    targets: list[Path] = []
    for directory in _SCAN_DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                targets.append(path)
    for path in _SCAN_FILES:
        if path.is_file():
            targets.append(path)
    return targets


class TestNoGeneralFlagInLiveArtifacts:
    """The removed --general flag MUST NOT appear in any live AIB artifact."""

    def test_forbidden_token_absent_from_scan_scope(self) -> None:
        """--general MUST NOT appear in prompts, tools, conventions, README, or user guide."""
        offenders: list[str] = []
        for path in _iter_scan_targets():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if FORBIDDEN_FLAG in text:
                offenders.append(str(path.relative_to(WORKSPACE_ROOT)))
        assert not offenders, (
            f"Forbidden token {FORBIDDEN_FLAG!r} present in: {offenders}"
        )

    def test_forbidden_token_intentional_use_is_isolated(self) -> None:
        """The only permitted occurrence of --general is inside tests/test_log_entry.py."""
        allowed_file = WORKSPACE_ROOT / "tests" / "test_log_entry.py"
        assert allowed_file.is_file(), "tests/test_log_entry.py must exist"
        assert FORBIDDEN_FLAG in allowed_file.read_text(encoding="utf-8"), (
            "tests/test_log_entry.py MUST retain a rejection assertion referencing "
            f"the {FORBIDDEN_FLAG!r} token; remove this test only when the argparse "
            "rejection assertion moves elsewhere."
        )


class TestNoPreRequestSuppressionProse:
    """Prompt files MUST NOT contain pre-request logging-failure suppression prose."""

    def test_suppression_substring_absent_from_prompts(self) -> None:
        """Canonical suppression prose MUST NOT appear in any .aib_brain/prompts/ file."""
        prompts_dir = AIB_BRAIN / "prompts"
        offenders: list[str] = []
        if prompts_dir.is_dir():
            for path in sorted(prompts_dir.rglob("*")):
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                if FORBIDDEN_SUPPRESSION_SUBSTRING in text:
                    offenders.append(str(path.relative_to(WORKSPACE_ROOT)))
        assert not offenders, (
            "Obsolete pre-request logging-failure suppression prose found in: "
            f"{offenders}"
        )

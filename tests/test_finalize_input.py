"""
test_finalize_input.py: Tests for .aib_brain/tools/finalize-input.py.
Part of the AIB test suite — added as part of R-20260511-2019.
Responsibilities: validate archive logic, stub-equivalence skip, attachment
relocation, input.md reset with request ID injection, and CLI error handling.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path constants — resolved relative to the workspace root via tests/ parent.
# ---------------------------------------------------------------------------

_TESTS_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _TESTS_DIR.parent
_TOOLS_DIR = _WORKSPACE_ROOT / ".aib_brain" / "tools"
_FINALIZE_SCRIPT = _TOOLS_DIR / "finalize-input.py"

# Minimal seed template WITHOUT toggle lines (new format introduced in R-20260511-2019).
_SEED_TEMPLATE = (
    "## Active request\n"
    "No active request\n\n"
    "## Options\n"
    "- Minimum questions: 0\n\n"
    "## Input\n\n"
)

# A non-stub input.md with meaningful developer content.
_NON_STUB_INPUT = (
    "## Active request\n"
    "R-TEST-0001 \u2014 My Test Request\n\n"
    "## Options\n"
    "- Minimum questions: 0\n\n"
    "## Input\n"
    "This is user-provided content that must be archived.\n"
)

# Register header and separator for building minimal register tables.
_REGISTER_HEADER = "| request_id | title | folder | state | created_at | closed_at |\n"
_REGISTER_SEP    = "| --- | --- | --- | --- | --- | --- |\n"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_workspace(tmp: str, request_id: str = "R-20260101-1200", title: str = "My Test") -> Path:
    """Create a minimal AIB workspace under *tmp* with one Active request.

    Returns the workspace root Path.
    """
    ws = Path(tmp)
    # Minimal brain and memory scaffolding required by ensure_workspace.
    (ws / ".aib_brain").mkdir(parents=True, exist_ok=True)
    memory = ws / ".aib_memory"
    memory.mkdir(parents=True, exist_ok=True)
    (memory / "attachments").mkdir(parents=True, exist_ok=True)
    (memory / "attachments" / ".gitkeep").touch()

    # Build a minimal requests_register.md with one Active row.
    folder_rel = f".aib_memory/requests/{request_id}-my-test"
    (ws / folder_rel).mkdir(parents=True, exist_ok=True)

    register_content = (
        "# Requests Register\n\n"
        + _REGISTER_HEADER
        + _REGISTER_SEP
        + f"| {request_id} | {title} | {folder_rel} | Active | 2026-01-01 12:00:00 +0000 |  |\n"
    )
    (memory / "requests_register.md").write_text(register_content, encoding="utf-8")

    return ws


def _run_finalize(ws: Path, request_id: str | None = None) -> subprocess.CompletedProcess:
    """Run finalize-input.py against *ws* via subprocess.

    Args:
        ws: Workspace root path.
        request_id: Optional explicit request ID to pass as --request-id.

    Returns:
        CompletedProcess with returncode, stdout, and stderr.
    """
    cmd = [sys.executable, str(_FINALIZE_SCRIPT), "--workspace", str(ws)]
    if request_id:
        cmd += ["--request-id", request_id]
    return subprocess.run(cmd, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# Tests: archive behaviour
# ---------------------------------------------------------------------------

class TestArchiveBehaviour:
    """Verify that input.md is archived (or not) based on stub-equivalence."""

    def test_non_stub_input_is_archived(self):
        """Non-stub input.md must produce an archive file in <request-folder>/inputs/."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp, request_id="R-20260101-1200", title="My Test")
            # Write non-stub content to input.md.
            input_file = ws / ".aib_memory" / "input.md"
            input_file.write_text(_NON_STUB_INPUT, encoding="utf-8")

            result = _run_finalize(ws, request_id="R-20260101-1200")
            assert result.returncode == 0, result.stderr

            # Exactly one archive file must exist in the request inputs/ folder.
            inputs_dir = ws / ".aib_memory" / "requests" / "R-20260101-1200-my-test" / "inputs"
            archive_files = list(inputs_dir.glob("input-archive-*.md"))
            assert len(archive_files) == 1, (
                f"Expected exactly one archive file; found: {[f.name for f in archive_files]}"
            )
            # Archive content must match original non-stub content.
            assert archive_files[0].read_text(encoding="utf-8") == _NON_STUB_INPUT

    def test_stub_equivalent_input_not_archived(self):
        """Stub-equivalent input.md must NOT produce an archive file."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp, request_id="R-20260101-1200", title="My Test")
            # Write stub-equivalent content (seed template with request ID).
            stub_content = _SEED_TEMPLATE.replace(
                "No active request", "R-20260101-1200 \u2014 My Test"
            )
            (ws / ".aib_memory" / "input.md").write_text(stub_content, encoding="utf-8")

            result = _run_finalize(ws, request_id="R-20260101-1200")
            assert result.returncode == 0, result.stderr

            inputs_dir = ws / ".aib_memory" / "requests" / "R-20260101-1200-my-test" / "inputs"
            archive_files = list(inputs_dir.glob("input-archive-*.md")) if inputs_dir.exists() else []
            assert len(archive_files) == 0, (
                f"No archive expected for stub-equivalent input; found: {[f.name for f in archive_files]}"
            )


# ---------------------------------------------------------------------------
# Tests: attachment moving
# ---------------------------------------------------------------------------

class TestAttachmentMoving:
    """Verify that non-.gitkeep attachments are relocated to <request-folder>/inputs/."""

    def test_attachments_moved_to_inputs(self):
        """Non-.gitkeep files in attachments/ must be moved to inputs/."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp, request_id="R-20260101-1200", title="My Test")
            # Place a non-stub input and an attachment file.
            (ws / ".aib_memory" / "input.md").write_text(_NON_STUB_INPUT, encoding="utf-8")
            attachment = ws / ".aib_memory" / "attachments" / "spec.txt"
            attachment.write_text("attachment content", encoding="utf-8")

            result = _run_finalize(ws, request_id="R-20260101-1200")
            assert result.returncode == 0, result.stderr

            # Original attachment must be gone from attachments/.
            assert not attachment.exists(), "Attachment was not moved (still at source)"

            # Moved file must appear in inputs/.
            dest = ws / ".aib_memory" / "requests" / "R-20260101-1200-my-test" / "inputs" / "spec.txt"
            assert dest.exists(), "Attachment was not found at destination"
            assert dest.read_text(encoding="utf-8") == "attachment content"

    def test_gitkeep_not_moved(self):
        """The .gitkeep placeholder must NOT be moved from attachments/."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp, request_id="R-20260101-1200", title="My Test")
            (ws / ".aib_memory" / "input.md").write_text(_NON_STUB_INPUT, encoding="utf-8")

            result = _run_finalize(ws, request_id="R-20260101-1200")
            assert result.returncode == 0, result.stderr

            # .gitkeep must remain in attachments/.
            assert (ws / ".aib_memory" / "attachments" / ".gitkeep").exists()


# ---------------------------------------------------------------------------
# Tests: input.md reset
# ---------------------------------------------------------------------------

class TestInputMdReset:
    """Verify that input.md is reset to the seed template with the active request ID."""

    def test_input_md_reset_contains_request_id(self):
        """After run, input.md must contain the active request ID in ## Active request."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp, request_id="R-20260101-1200", title="My Test")
            (ws / ".aib_memory" / "input.md").write_text(_NON_STUB_INPUT, encoding="utf-8")

            result = _run_finalize(ws, request_id="R-20260101-1200")
            assert result.returncode == 0, result.stderr

            reset = (ws / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert "R-20260101-1200" in reset, "Reset input.md must contain the request ID"
            assert "My Test" in reset, "Reset input.md must contain the request title"

    def test_input_md_no_toggle_lines(self):
        """After run, input.md must NOT contain either removed toggle line."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp, request_id="R-20260101-1200", title="My Test")
            (ws / ".aib_memory" / "input.md").write_text(_NON_STUB_INPUT, encoding="utf-8")

            result = _run_finalize(ws, request_id="R-20260101-1200")
            assert result.returncode == 0, result.stderr

            reset = (ws / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert "No changes \u2014 provide answer only" not in reset, (
                "Reset input.md must not contain the removed 'No changes' toggle."
            )
            assert "Skip analysis document generation" not in reset, (
                "Reset input.md must not contain the removed 'Skip analysis' toggle."
            )

    def test_input_md_has_minimum_questions(self):
        """After run, input.md must still contain the Minimum questions option."""
        with tempfile.TemporaryDirectory() as tmp:
            ws = _make_workspace(tmp, request_id="R-20260101-1200", title="My Test")
            (ws / ".aib_memory" / "input.md").write_text(_NON_STUB_INPUT, encoding="utf-8")

            result = _run_finalize(ws, request_id="R-20260101-1200")
            assert result.returncode == 0, result.stderr

            reset = (ws / ".aib_memory" / "input.md").read_text(encoding="utf-8")
            assert "Minimum questions" in reset, "Reset input.md must contain 'Minimum questions' option."


# ---------------------------------------------------------------------------
# Tests: CLI error handling
# ---------------------------------------------------------------------------

class TestCliErrorHandling:
    """Verify that the CLI exits with non-zero code on invalid invocations."""

    def test_missing_workspace_argument_fails(self):
        """Omitting --workspace must produce a non-zero exit code."""
        result = subprocess.run(
            [sys.executable, str(_FINALIZE_SCRIPT)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            "finalize-input.py must exit non-zero when --workspace is not provided."
        )

    def test_invalid_workspace_fails(self):
        """A workspace path with no .aib_brain/ must produce a non-zero exit code."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_finalize(Path(tmp))
            assert result.returncode != 0, (
                "finalize-input.py must exit non-zero for a workspace missing .aib_brain/."
            )

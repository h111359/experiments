"""Exercise the managed .aib_memory/scratch directory lifecycle.
Part of AIB request R-20260819-1437 automated coverage.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = WORKSPACE_ROOT / ".aib_brain" / "tools"
INITIALIZE_SCRIPT = TOOLS_DIR / "initialize.py"
FINALIZE_SCRIPT = TOOLS_DIR / "finalize-input.py"
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


def _run(script: Path, workspace: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    """Run an AIB Python tool with bytecode disabled.

    Args:
        script: Tool script to execute.
        workspace: Temporary workspace passed to the tool.
        extra_args: Additional command-line arguments.

    Returns:
        Completed subprocess result with captured text streams.
    """
    child_env = os.environ.copy()
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", str(script), "--workspace", str(workspace), *extra_args],
        capture_output=True,
        check=False,
        env=child_env,
        text=True,
    )


def _seed_brain(workspace: Path) -> None:
    """Create the minimal framework marker required by initialization.

    Args:
        workspace: Temporary workspace to seed.

    Returns:
        None.
    """
    brain_dir = workspace / ".aib_brain"
    brain_dir.mkdir(parents=True)
    (brain_dir / "v9.9.9").touch()


def _activate_request(workspace: Path) -> str:
    """Replace input.md with an active request and create its request folder.

    Args:
        workspace: Initialized temporary workspace.

    Returns:
        Active request identifier.
    """
    request_id = "R-20260819-1437"
    title = "Scratch Test"
    input_content = (
        "---\n"
        "state:\n"
        f"  request_id: {request_id}\n"
        f"  title: {title}\n"
        "  status: analysis_ready\n"
        "  input_verification_result: null\n"
        "  context_verification_result: null\n"
        "options:\n"
        "  minimum_questions: 5\n"
        "  input_verification_enabled: true\n"
        "  context_verification_enabled: true\n"
        "---\n\n"
        "## Input\n\n"
        "Finalize this scratch lifecycle fixture.\n"
    )
    (workspace / ".aib_memory" / "input.md").write_text(input_content, encoding="utf-8")
    request_folder = workspace / ".aib_memory" / "requests" / f"{request_id}-scratch-test"
    request_folder.mkdir(parents=True)
    return request_id


def test_fresh_initialize_seeds_scratch_and_generated_context(tmp_path: Path) -> None:
    """Fresh setup must create scratch/.gitkeep and list scratch in context."""
    _seed_brain(tmp_path)

    result = _run(INITIALIZE_SCRIPT, tmp_path)

    assert result.returncode == 0, result.stderr
    scratch_dir = tmp_path / ".aib_memory" / "scratch"
    assert scratch_dir.is_dir()
    assert (scratch_dir / ".gitkeep").is_file()
    context = (tmp_path / ".aib_memory" / "context.md").read_text(encoding="utf-8")
    assert "scratch/ — managed task-specific helpers" in context


def test_upgrade_preserves_existing_scratch_content(tmp_path: Path) -> None:
    """Upgrade must merge archived scratch files back into the reseeded directory."""
    _seed_brain(tmp_path)
    first = _run(INITIALIZE_SCRIPT, tmp_path)
    assert first.returncode == 0, first.stderr
    helper = tmp_path / ".aib_memory" / "scratch" / "nested" / "helper.txt"
    helper.parent.mkdir(parents=True)
    helper.write_text("preserve me", encoding="utf-8")

    upgraded = _run(INITIALIZE_SCRIPT, tmp_path, "--upgrade")

    assert upgraded.returncode == 0, upgraded.stderr
    assert helper.read_text(encoding="utf-8") == "preserve me"
    assert (tmp_path / ".aib_memory" / "scratch" / ".gitkeep").is_file()


def test_finalize_recursively_sweeps_scratch_except_gitkeep(tmp_path: Path) -> None:
    """Input finalization must remove nested helpers while retaining the sentinel."""
    _seed_brain(tmp_path)
    initialized = _run(INITIALIZE_SCRIPT, tmp_path)
    assert initialized.returncode == 0, initialized.stderr
    request_id = _activate_request(tmp_path)
    scratch_dir = tmp_path / ".aib_memory" / "scratch"
    (scratch_dir / "helper.py").write_text("print('temporary')\n", encoding="utf-8")
    nested = scratch_dir / "nested" / "deeper"
    nested.mkdir(parents=True)
    (nested / "notes.txt").write_text("temporary", encoding="utf-8")

    finalized = _run(FINALIZE_SCRIPT, tmp_path, "--request-id", request_id)

    assert finalized.returncode == 0, finalized.stderr
    assert sorted(path.name for path in scratch_dir.iterdir()) == [".gitkeep"]
    assert (scratch_dir / ".gitkeep").is_file()


def test_policy_and_writing_prompts_require_managed_scratch() -> None:
    """Canonical and prompt-level instructions must prescribe managed scratch."""
    convention = (
        WORKSPACE_ROOT / ".aib_brain" / "conventions" / "coding-general-convention.md"
    ).read_text(encoding="utf-8")
    assert "task-specific helper inside the repository" in convention
    assert "MUST be placed under `.aib_memory/scratch/`" in convention

    for prompt_name in WRITING_PROMPTS:
        content = (PROMPTS_DIR / prompt_name).read_text(encoding="utf-8")
        assert "AIB-prescribed in-repository task-specific helpers MUST be created under `.aib_memory/scratch/`" in content


def test_workspace_tracks_the_scratch_sentinel() -> None:
    """The repository must carry the active workspace scratch sentinel."""
    sentinel = WORKSPACE_ROOT / ".aib_memory" / "scratch" / ".gitkeep"
    assert sentinel.is_file()

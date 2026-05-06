"""Integration tests for scripts/release_bookkeeping.py.

Covers curated-source preference, fallback to commit subjects, lifecycle reset
of `logs/next_version_changes.md`, and idempotency on reruns.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = WORKSPACE_ROOT / "scripts" / "release_bookkeeping.py"


def _load_release_bookkeeping():
    """Import the release_bookkeeping module directly from disk."""
    name = "release_bookkeeping_under_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can resolve cls.__module__ via sys.modules.
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _git(cmd: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        ["git", *cmd],
        cwd=str(cwd),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout


def _init_repo(root: Path, base_marker: str) -> None:
    """Initialize a minimal git repo with a base branch carrying the marker file."""
    _git(["init", "-q", "-b", "main"], cwd=root)
    _git(["config", "user.email", "test@example.com"], cwd=root)
    _git(["config", "user.name", "Test"], cwd=root)
    _git(["config", "commit.gpgsign", "false"], cwd=root)

    brain = root / ".aib_brain"
    brain.mkdir(parents=True, exist_ok=True)
    (brain / base_marker).write_text("", encoding="utf-8")
    (brain / "README.md").write_text("brain\n", encoding="utf-8")
    (root / "logs").mkdir(parents=True, exist_ok=True)

    _git(["add", "-A"], cwd=root)
    _git(["commit", "-q", "-m", "seed base"], cwd=root)
    # Use a local pseudo-remote ref name expected by the script (origin/main).
    # The script calls `git ls-tree --name-only <ref>:<dir>`; any valid ref works.
    # Mirror current HEAD as `origin/main` via a refs/remotes ref.
    head_sha = _git(["rev-parse", "HEAD"], cwd=root).strip()
    _git(["update-ref", "refs/remotes/origin/main", head_sha], cwd=root)


def _run_script(root: Path, *extra_args: str) -> subprocess.CompletedProcess:
    """Invoke the release bookkeeping script as a subprocess in `root`."""
    cmd = [sys.executable, str(SCRIPT_PATH), "--base-ref", "origin/main", *extra_args]
    return subprocess.run(
        cmd,
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """Initialize a temporary git repo with a v1.0.0 marker on origin/main."""
    _init_repo(tmp_path, base_marker="v1.0.0")
    return tmp_path


# ---------------------------------------------------------------------------
# Unit-level tests for the curated-entries helper
# ---------------------------------------------------------------------------

def test_read_curated_entries_returns_empty_when_missing(tmp_path: Path) -> None:
    mod = _load_release_bookkeeping()
    missing = tmp_path / "absent.md"
    assert mod._read_curated_entries(missing) == []


def test_read_curated_entries_returns_empty_when_blank(tmp_path: Path) -> None:
    mod = _load_release_bookkeeping()
    p = tmp_path / "empty.md"
    p.write_text("\n   \n", encoding="utf-8")
    assert mod._read_curated_entries(p) == []


def test_read_curated_entries_parses_bullets(tmp_path: Path) -> None:
    mod = _load_release_bookkeeping()
    p = tmp_path / "next.md"
    p.write_text(
        "- First curated change.\n"
        "-   Second   curated   change.\n"
        "Some non-bullet noise that must be ignored.\n"
        "- Third curated change.\n",
        encoding="utf-8",
    )
    assert mod._read_curated_entries(p) == [
        "First curated change.",
        "Second curated change.",
        "Third curated change.",
    ]


# ---------------------------------------------------------------------------
# End-to-end script tests
# ---------------------------------------------------------------------------

def test_curated_source_preferred_over_commit_subjects(repo: Path) -> None:
    curated = repo / "logs" / "next_version_changes.md"
    curated.write_text(
        "- Curated A\n- Curated B\n",
        encoding="utf-8",
    )
    subjects = repo / "subjects.txt"
    subjects.write_text("commit subject one\ncommit subject two\n", encoding="utf-8")

    result = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--next-version-changes-file", str(curated),
    )
    assert result.returncode == 0, result.stderr

    log_path = repo / "logs" / "version_v1.0.1_log.md"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "- Curated A" in content
    assert "- Curated B" in content
    assert "commit subject one" not in content


def test_fallback_to_commit_subjects_when_curated_missing(repo: Path) -> None:
    subjects = repo / "subjects.txt"
    subjects.write_text("only commit subject\n", encoding="utf-8")

    # No --next-version-changes-file flag at all.
    result = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
    )
    assert result.returncode == 0, result.stderr

    log_path = repo / "logs" / "version_v1.0.1_log.md"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "- only commit subject" in content


def test_fallback_to_commit_subjects_when_curated_empty(repo: Path) -> None:
    curated = repo / "logs" / "next_version_changes.md"
    curated.write_text("", encoding="utf-8")
    subjects = repo / "subjects.txt"
    subjects.write_text("subject from git\n", encoding="utf-8")

    result = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--next-version-changes-file", str(curated),
    )
    assert result.returncode == 0, result.stderr

    log_path = repo / "logs" / "version_v1.0.1_log.md"
    content = log_path.read_text(encoding="utf-8")
    assert "- subject from git" in content
    # Curated file should remain empty (no curated entries → no reset action needed).
    assert curated.read_text(encoding="utf-8") == ""


def test_fallback_to_commit_subjects_when_curated_file_absent_path_provided(repo: Path) -> None:
    """Passing a non-existent curated file path must not error and must fall back."""
    curated = repo / "logs" / "next_version_changes.md"
    assert not curated.exists()
    subjects = repo / "subjects.txt"
    subjects.write_text("subject only\n", encoding="utf-8")

    result = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--next-version-changes-file", str(curated),
    )
    assert result.returncode == 0, result.stderr

    log_path = repo / "logs" / "version_v1.0.1_log.md"
    content = log_path.read_text(encoding="utf-8")
    assert "- subject only" in content


def test_lifecycle_reset_after_incorporation(repo: Path) -> None:
    curated = repo / "logs" / "next_version_changes.md"
    curated.write_text("- A curated bullet\n", encoding="utf-8")
    subjects = repo / "subjects.txt"
    subjects.write_text("ignored\n", encoding="utf-8")

    result = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--next-version-changes-file", str(curated),
    )
    assert result.returncode == 0, result.stderr

    # File must remain present (VCS-tracked) but emptied.
    assert curated.exists()
    assert curated.read_text(encoding="utf-8") == ""


def test_idempotent_rerun_after_reset(repo: Path) -> None:
    curated = repo / "logs" / "next_version_changes.md"
    curated.write_text("- A curated bullet\n", encoding="utf-8")
    subjects = repo / "subjects.txt"
    subjects.write_text("subject fallback\n", encoding="utf-8")

    first = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--next-version-changes-file", str(curated),
    )
    assert first.returncode == 0, first.stderr

    log_path = repo / "logs" / "version_v1.0.1_log.md"
    first_log = log_path.read_text(encoding="utf-8")
    # Curated file is now empty after lifecycle reset.
    assert curated.read_text(encoding="utf-8") == ""

    # Rerun: marker already bumped, log already exists → idempotent no-op path.
    second = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--next-version-changes-file", str(curated),
    )
    assert second.returncode == 0, second.stderr
    assert "No changes needed" in second.stdout
    # Log content unchanged on rerun.
    assert log_path.read_text(encoding="utf-8") == first_log
    # Curated file remains empty (no second reset needed; idempotent path skipped reset).
    assert curated.read_text(encoding="utf-8") == ""


# ---------------------------------------------------------------------------
# Tests for changes_body GITHUB_OUTPUT emission
# ---------------------------------------------------------------------------

def test_changes_body_output_emitted_when_curated_non_empty(repo: Path, tmp_path: Path) -> None:
    """changes_body output must contain curated bullet lines when curated file is non-empty."""
    curated = repo / "logs" / "next_version_changes.md"
    curated.write_text("- Alpha change.\n- Beta change.\n", encoding="utf-8")
    subjects = repo / "subjects.txt"
    subjects.write_text("ignored subject\n", encoding="utf-8")
    gh_output = tmp_path / "github_output.txt"
    gh_output.write_text("", encoding="utf-8")

    result = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--next-version-changes-file", str(curated),
        "--github-output", str(gh_output),
    )
    assert result.returncode == 0, result.stderr

    output_content = gh_output.read_text(encoding="utf-8")
    assert "changes_body<<AIB_CHANGES_BODY_EOF" in output_content
    assert "- Alpha change." in output_content
    assert "- Beta change." in output_content
    assert "AIB_CHANGES_BODY_EOF" in output_content


def test_changes_body_output_empty_when_no_curated_entries(repo: Path, tmp_path: Path) -> None:
    """changes_body output must be present but empty when curated file is absent or empty."""
    subjects = repo / "subjects.txt"
    subjects.write_text("commit subject\n", encoding="utf-8")
    gh_output = tmp_path / "github_output.txt"
    gh_output.write_text("", encoding="utf-8")

    # No --next-version-changes-file: curated entries are empty.
    result = _run_script(
        repo,
        "--commit-subjects-file", str(subjects),
        "--github-output", str(gh_output),
    )
    assert result.returncode == 0, result.stderr

    output_content = gh_output.read_text(encoding="utf-8")
    # Heredoc block must be present with an empty body between the delimiters.
    assert "changes_body<<AIB_CHANGES_BODY_EOF" in output_content
    assert "AIB_CHANGES_BODY_EOF" in output_content
    # The body between the delimiters must be empty (no bullet lines).
    start = output_content.index("changes_body<<AIB_CHANGES_BODY_EOF\n") + len("changes_body<<AIB_CHANGES_BODY_EOF\n")
    end = output_content.index("\nAIB_CHANGES_BODY_EOF", start)
    body_between = output_content[start:end]
    assert body_between == ""

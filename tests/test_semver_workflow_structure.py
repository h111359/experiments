"""Structural tests for .github/workflows/aib-semver-patch-bump-and-log.yml.

Part of request R-20260430-1755.
Responsibilities: verify permissions block, post-comment step condition,
and continue-on-error flag in the CI semver bump workflow.
"""

from __future__ import annotations

from pathlib import Path

import yaml
import pytest


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = WORKSPACE_ROOT / ".github" / "workflows" / "aib-semver-patch-bump-and-log.yml"


@pytest.fixture(scope="module")
def workflow() -> dict:
    """Parse and return the workflow YAML as a dict."""
    with WORKFLOW_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def post_comment_step(workflow: dict) -> dict:
    """Return the 'Post changelog comment' step dict from the workflow."""
    steps = workflow["jobs"]["bump_and_log"]["steps"]
    matches = [s for s in steps if s.get("name") == "Post changelog comment"]
    assert len(matches) == 1, (
        "Expected exactly one step named 'Post changelog comment', "
        f"found {len(matches)}"
    )
    return matches[0]


def test_pull_requests_write_permission(workflow: dict) -> None:
    """SC-5: The workflow permissions block must grant pull-requests: write."""
    permissions = workflow.get("permissions", {})
    assert permissions.get("pull-requests") == "write", (
        f"Expected pull-requests: write, got: {permissions.get('pull-requests')!r}"
    )


def test_post_comment_step_exists(post_comment_step: dict) -> None:
    """Verify the 'Post changelog comment' step is present in the workflow."""
    assert post_comment_step is not None


def test_post_comment_step_condition(post_comment_step: dict) -> None:
    """SC-3: The step must only run when changes_body is non-empty."""
    condition = post_comment_step.get("if", "")
    assert "steps.bookkeeping.outputs.changes_body" in condition, (
        f"Step 'if' condition missing changes_body guard: {condition!r}"
    )
    assert condition.strip() != "", "Step 'if' condition must not be empty"


def test_post_comment_step_continue_on_error(post_comment_step: dict) -> None:
    """SC-4: A comment-post failure must not fail the overall workflow."""
    assert post_comment_step.get("continue-on-error") is True, (
        "Expected continue-on-error: true on 'Post changelog comment' step"
    )


def test_post_comment_step_uses_changes_body_env(post_comment_step: dict) -> None:
    """SC-2: The step must pass CHANGES_BODY from the bookkeeping output."""
    env = post_comment_step.get("env", {})
    assert "CHANGES_BODY" in env, "CHANGES_BODY must be declared in step env"
    assert "steps.bookkeeping.outputs.changes_body" in str(env["CHANGES_BODY"]), (
        "CHANGES_BODY must reference steps.bookkeeping.outputs.changes_body"
    )

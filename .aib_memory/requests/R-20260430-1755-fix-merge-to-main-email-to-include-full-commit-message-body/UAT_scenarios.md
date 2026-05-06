# UAT Scenarios

## UAT-01 — End-to-end PR workflow: verify PR comment is posted and emailed

**Trigger:** Manual — requires a live PR on the `AI_Builder` repository with non-empty `logs/next_version_changes.md`.

**Pre-conditions:**
1. At least one curated bullet is present in `logs/next_version_changes.md` before the PR is pushed.
2. The updated workflow (`aib-semver-patch-bump-and-log.yml`) with the PR-comment step is deployed to the branch under test.
3. The test user is subscribed to PR notifications via email.

**Steps:**
1. Open a new PR targeting `main` with a non-empty `logs/next_version_changes.md`.
2. Wait for the `AIB SemVer PATCH bump and log` workflow to complete successfully.
3. Inspect the PR timeline on GitHub.com — verify a comment containing the changelog bullets is posted.
4. Check the notification email in the test user's inbox — verify the email includes the changelog bullets.

**Expected outcome:**
- A PR comment is visible in the PR timeline with the changelog bullet list.
- A GitHub notification email is received that includes the full bullet content.
- The workflow run shows a green status with no failures.

**Failure definition:**
- No comment appears in the PR timeline.
- The notification email shows only the PR title or commit subject without the bullets.
- The workflow run fails or shows a warning on the comment-posting step.

**Automation status:** Cannot be fully automated (requires live GitHub PR + email inbox verification). Structural aspects (step presence, condition, `continue-on-error`) are covered by automated tests T1–T5.

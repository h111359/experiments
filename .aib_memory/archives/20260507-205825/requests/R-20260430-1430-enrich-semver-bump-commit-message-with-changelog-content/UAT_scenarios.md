# UAT Scenarios — R-20260430-1430

## UAT-01: Verify commit notification email contains changelog content

**Type:** Manual — requires a live PR merge event and email client inspection.

**Preconditions:**
1. A branch is in the process of being merged to `main` via a pull request.
2. `logs/next_version_changes.md` in the branch contains at least one curated bullet line (e.g., `- Enrich semver bump commit message with changelog content.`).
3. The enriched commit message implementation (Tasks 1–2 from `request.md` Plan) has been deployed to the workflow.

**Steps:**
1. Push a commit to the PR branch to trigger the `aib-semver-patch-bump-and-log.yml` workflow.
2. Wait for the workflow to complete successfully.
3. Open the PR on GitHub and navigate to the "Commits" tab.
4. Click on the most recent CI commit (the one created by `github-actions[bot]`).
5. Verify the commit message subject matches `chore: bump to <version> (PR #<number>)`.
6. Verify the commit message body is visible and contains the curated bullet lines that were in `logs/next_version_changes.md` before the workflow ran.
7. Open the email notification received for this commit in your email client.
8. Verify the email body includes both the subject line and the curated changelog bullets.

**Expected outcome:** The commit detail page and the email notification both show the subject line followed by the curated bullet list. The email is self-explanatory to recipients who did not visit the GitHub UI.

**Pass/Fail criteria:**
- PASS: Commit message body on GitHub and in email contains the curated bullets.
- FAIL: Commit message body is absent, truncated, or contains garbled content; OR email shows only the subject line.

---

## UAT-02: Verify fallback when curated log is empty

**Type:** Manual — requires a live PR event with empty curated log.

**Preconditions:**
1. A branch is in the process of being merged to `main` via a pull request.
2. `logs/next_version_changes.md` in the branch is empty or absent.
3. The enriched commit message implementation has been deployed to the workflow.

**Steps:**
1. Push a commit to the PR branch to trigger the workflow.
2. Wait for the workflow to complete successfully.
3. Open the PR on GitHub and navigate to the "Commits" tab.
4. Click on the most recent CI commit.
5. Verify the commit message shows only the subject line with no additional body.

**Expected outcome:** The commit message contains only `chore: bump to <version> (PR #<number>)` with no body or trailing blank lines.

**Pass/Fail criteria:**
- PASS: Subject-only message; no empty body section appended.
- FAIL: Workflow fails, or an empty/blank commit body is appended after the subject line.

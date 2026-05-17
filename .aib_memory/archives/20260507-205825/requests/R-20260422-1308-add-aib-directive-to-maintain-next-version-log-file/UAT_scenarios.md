# UAT Scenarios — R-20260422-1308

## UAT-01 — AIB implement directive execution

**Scenario:** Verify that after running `aib-implement.md` for a request, the AI agent has appended entries to `logs/next_version_changes.md` as directed by `instructions.md`.

**Preconditions:**
- `.aib_memory/instructions.md` contains the directive to maintain `logs/next_version_changes.md`.
- An active request exists with a non-trivial implementation scope.

**Steps:**
1. Run `Execute .aib_brain/prompts/aib-implement.md` in the AI coding interface.
2. After the prompt completes, open `logs/next_version_changes.md`.

**Expected outcome:** The file contains at least one bullet entry per logical change implemented, written in present-tense verb phrase format. No entries from previous requests should be present if the lifecycle reset was performed by the prior CI run.

**Pass/Fail criteria:** PASS if one or more bullets are present and correctly formatted. FAIL if the file is unchanged from its pre-run state.

---

## UAT-02 — Version log quality check

**Scenario:** Verify that after the CI workflow runs on a PR, the generated `logs/version_vX.Y.Z_log.md` contains the curated entries from `logs/next_version_changes.md`.

**Preconditions:**
- `logs/next_version_changes.md` contains at least two curated entries committed to the PR branch.
- The GitHub Actions workflow triggers on the PR.

**Steps:**
1. Open a PR targeting `main` with `logs/next_version_changes.md` containing curated entries.
2. Wait for the `AIB SemVer PATCH bump and log` workflow to complete.
3. Inspect the CI-committed `logs/version_vX.Y.Z_log.md` file.

**Expected outcome:** The version log contains the curated entries from `next_version_changes.md` under the `Changes:` heading. If the lifecycle policy is "clear after incorporation", the CI commit also resets `logs/next_version_changes.md` to empty.

**Pass/Fail criteria:** PASS if the curated entries appear verbatim (or normalized) in the version log. FAIL if only raw commit subjects appear.

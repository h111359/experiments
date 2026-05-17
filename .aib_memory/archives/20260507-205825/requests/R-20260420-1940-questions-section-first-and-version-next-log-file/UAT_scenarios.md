# UAT Scenarios — R-20260420-1940

**Request:** Questions section first and version_next log file

These scenarios require manual execution or a full CI run and cannot be expressed as automated script assertions.

---

## UAT-01 — SC-3: aib-implement.md appends entry to logs/version_next.md

**Preconditions:**
- A request is in Active state.
- `logs/version_next.md` exists (with seed template or prior entries).
- `aib-implement.md` has been updated per Task 4 of the Plan.

**Steps:**
1. Execute `aib-implement.md` for the active request.
2. Wait for the implement prompt to complete and close the request.
3. Open `logs/version_next.md`.

**Expected outcome:**
- `logs/version_next.md` contains a new bullet entry in the format `- <request_id>: <one-line summary>` corresponding to the just-implemented request.
- The entry is identifiable by the request ID.

**Pass/Fail:** Pass if the entry is present with the correct request ID. Fail if the file is unchanged or the request ID is absent.

---

## UAT-02 — SC-4: CI per-version log incorporates logs/version_next.md content

**Preconditions:**
- `release_bookkeeping.py` has been updated per Task 5 of the Plan.
- `logs/version_next.md` contains at least one bullet entry (non-empty, non-seed-only).
- A PR is open targeting `main` with the updated files.

**Steps:**
1. Open the PR and ensure `logs/version_next.md` has at least one entry.
2. Trigger the CI workflow (push a commit or re-run the workflow manually).
3. After the workflow completes, inspect the newly created `logs/version_vX.Y.Z_log.md` on the PR branch.

**Expected outcome:**
- The `Changes:` section of the per-version log contains the entries from `logs/version_next.md` (not bare git commit subjects).
- The entries match the bullet lines from `logs/version_next.md` at the time the CI ran.

**Pass/Fail:** Pass if changes section reflects `version_next.md` entries. Fail if changes section shows bare commit subjects when `version_next.md` was non-empty.

---

## UAT-03 — SC-5: CI clears logs/version_next.md to seed template after use

**Preconditions:**
- UAT-02 has been executed and passed.

**Steps:**
1. After the CI workflow completes, pull the PR branch locally.
2. Open `logs/version_next.md`.

**Expected outcome:**
- `logs/version_next.md` content is exactly the seed template: `# Pending changes for next version` (with no entry lines remaining).
- The file is present and VCS-tracked (not deleted).

**Pass/Fail:** Pass if file content matches the seed template exactly. Fail if entries from UAT-02 are still present or if the file is absent.

---

## UAT-04 — CI fallback: absent or empty version_next.md falls back to commit subjects

**Preconditions:**
- `release_bookkeeping.py` has been updated per Task 5 of the Plan.
- `logs/version_next.md` is absent or contains only the seed template (no entry lines).
- A PR is open targeting `main`.

**Steps:**
1. Ensure `logs/version_next.md` is either deleted or contains only `# Pending changes for next version`.
2. Trigger the CI workflow.
3. After the workflow completes, inspect the newly created `logs/version_vX.Y.Z_log.md`.

**Expected outcome:**
- The `Changes:` section of the per-version log contains the PR commit subjects (fallback behavior).
- The log is valid and does not error.

**Pass/Fail:** Pass if changes section lists commit subjects. Fail if log is empty or CI errors.

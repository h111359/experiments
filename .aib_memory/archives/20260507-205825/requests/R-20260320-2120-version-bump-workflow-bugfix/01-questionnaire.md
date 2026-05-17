# Iteration 01 — Questionnaire

## 1) Business & Functional Questions

### QID-BF-001 — Per-version log retention policy
**Intent:** Decide whether `logs/version_vX.Y.Z_log.md` files are meant to be historical artifacts kept in-repo across releases.
**Rationale:** The workflow/script currently fails if any other per-version log exists, which conflicts with keeping historical logs. This decision determines whether the fix should allow base-branch historical logs (most robust) or enforce “single-log” hygiene.
**Impact Areas:** Scope, Requirements, Operations, Timeline
**Assumptions:**
- The repository may accumulate one per-version log per released version over time.
**Answer Type:** single-select
**Options:**
- [x] A) Keep historical per-version logs in `logs/` across all versions (recommended) — Allows many `version_v*_log.md` files on base.
- [ ] B) Keep only the most recent per-version log file in-repo — Requires cleanup/move of older logs.
- [ ] C) Do not commit per-version logs via automation — Workflow should not write `logs/version_*`.
- [ ] D) Keep per-version logs, but in a different location/naming scheme — Requires changing script/workflow conventions.
- [ ] Other — (describe below)
**Constraints & Guards:** If you pick B/C/D, we should confirm what replaces `logs/versions_log.md` usage (if any).

**Other details (only if “Other” is checked):**
```text

```

## 2) Architecture & Technical Questions

### QID-AT-001 — What should the “other version log” guard compare against?
**Intent:** Choose how `scripts/release_bookkeeping.py` decides whether existing per-version logs are “stale/conflicting” vs acceptable history.
**Rationale:** The current guard treats any existing per-version log for a different version as an error, which breaks once the base branch has older logs (e.g., base has `v1.0.5`, target is `v1.0.6`). The chosen comparison strategy directly determines the minimal, correct bugfix.
**Impact Areas:** Architecture, Operations, Timeline
**Assumptions:**
- `--base-ref` is available and fetched in the workflow (currently `origin/<base_ref>`).
**Answer Type:** single-select
**Options:**
- [ ] A) Ignore logs that already exist on `--base-ref`; only guard PR-introduced per-version logs (recommended) — Fixes current failure while keeping a safety check.
- [x] B) Remove the guard entirely — Always allow existing logs; simplest but least restrictive.
- [ ] C) Keep the current behavior (fail if any other version log exists) — Would require repo-wide cleanup to proceed.
- [ ] D) Auto-clean PR-introduced non-target logs before creating the target log — Maximizes idempotency but risks deleting intent.
- [ ] Other — (describe below)
**Constraints & Guards:** If you pick D, confirm whether deletion is allowed or if “fail with instructions” is preferred.

**Other details (only if “Other” is checked):**
```text

```

### QID-AT-002 — If the PR branch already introduced a conflicting per-version log, what is the policy?
**Intent:** Decide the deterministic behavior when the PR branch contains a per-version log for a different version than the newly computed target.
**Rationale:** This is the remaining edge case after allowing base-branch historical logs. It affects CI idempotency when the base branch advances during a PR (target version changes) and determines whether the workflow should fail fast or attempt safe cleanup.
**Impact Areas:** Operations, Timeline, Compliance
**Assumptions:**
- Conflicting logs on the PR branch are most often automation artifacts from earlier runs.
**Answer Type:** single-select
**Options:**
- [ ] A) Fail fast with a clearer error message and instructions to reset/rebase the PR branch (recommended) — Safest; avoids deleting any files.
- [ ] B) Auto-delete only PR-introduced conflicting logs that match the workflow-generated pattern — More hands-off; moderate risk.
- [ ] C) Auto-delete any PR-introduced conflicting per-version logs regardless of content — Highest risk; simplest cleanup.
- [x] D) Allow multiple different per-version logs to coexist on the PR branch — Could create noisy/ambiguous release notes.
- [ ] Other — (describe below)
**Constraints & Guards:** If you pick B/C, define what “PR-introduced” means (compare to `--base-ref`), and what file pattern(s) qualify for deletion.

**Other details (only if “Other” is checked):**
```text

```

## 3) Appendix — Answer Encoding Rules

- Checkboxes:
  - Unchecked: `- [ ]`
  - Checked: `- [x]` (or `- [X]`)
- Single-select questions:
  - Exactly one option must be checked (including `Other`).
- “Other” answers:
  - If `Other` is checked, the corresponding “Other details” box must be non-empty.

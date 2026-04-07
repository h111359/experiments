# Iteration 03 Questionnaire

Request: `R-20260320-0925` — Issue 17 (SemVer PATCH bump + per-version log file + README guidance)

## Instructions for human
- For each question, select exactly one option (single-select).
- If you choose `Other`, add a short free-text clarification on the same line or directly beneath the option.
- Keep answers consistent across questions (see constraints/guards where noted).

---

## Business & Functional Questions

No unresolved business/functional decision points were identified for iteration `03` after reviewing the request artifacts and the referenced product documentation set.

---

## Architecture & Technical Questions

### QID-AT-001 — Mutation timing / trigger strategy
**Intent:** Choose when the workflow should mutate repository contents (version marker + new per-version log file + README updates).
**Rationale:** Trigger timing determines idempotency (one bump per PR), the availability of PR context (commit subjects), and whether the workflow must push commits directly to `main` (often constrained by branch protection).
**Impact Areas:** Architecture, Operations, Timeline, Requirements, Security
**Assumptions:**
- The desired behavior is “runs once per merged PR into `main`”.
- The workflow must keep changes traceable to the triggering PR.
**Answer Type:** single-select
**Options:**
- [ ] A) `pull_request` closed + `merged == true` (recommended) — merge-time, PR context available, may require Actions push to `main`.
- [ ] B) `push` to `main` — merge-time, simpler trigger, weaker direct PR context.
- [x] C) Pre-merge: workflow commits changes back to the PR branch — avoids writing to `main`, higher complexity/idempotency risk.
- [ ] D) Manual `workflow_dispatch` only — deterministic but not automatic and easy to forget.
- [ ] Other — (describe below)
**Constraints & Guards:** If A or B is selected, QID-AT-002 must allow repository writes to land on `main`.

### QID-AT-002 — Repo write policy under branch protection
**Intent:** Confirm whether GitHub Actions is allowed to land the required changes in the repository when `main` is protected.
**Rationale:** This automation must create/modify files (SemVer marker rotation, new `logs/version_<version>_log.md`, and `README.md`). If branch protection blocks all pushes, the implementation must switch to a bot-PR or pre-merge strategy—or the workflow will fail by design.
**Impact Areas:** Operations, Security, Timeline, Requirements
**Assumptions:**
- `main` is protected and accepts changes only via approved PR merges.
**Answer Type:** single-select
**Options:**
- [ ] A) Allow GitHub Actions to push a commit to `main` (recommended) — configure Actions `contents: write` and allow bypass as needed.
- [ ] B) Disallow direct pushes; instead, workflow must open a bot PR — policy-compliant, adds governance/extra PR.
- [x] C) Disallow pushes to `main`; allow workflow to push only to the PR branch (pre-merge mutation) — compatible with strict protection, more complex.
- [ ] D) Disallow all workflow writes; workflow should fail and a human performs the steps — simplest governance, least automation value.
- [ ] Other — (describe below)
**Constraints & Guards:** If QID-AT-001 = A or B, option A or B must be selected here (otherwise the design is inconsistent).

### QID-AT-003 — Per-version log filename token
**Intent:** Choose whether the `<version>` token in `logs/version_<version>_log.md` includes the leading `v` from the SemVer marker filename.
**Rationale:** The request states “use the semver file name as version,” but existing log content uses `Version 1.0.4` (no leading `v`). Getting the filename rule wrong will create “incorrectly named” log files and break discoverability.
**Impact Areas:** Requirements, Operations
**Assumptions:**
- The per-version log file is created for the *new* version after PATCH increment.
**Answer Type:** single-select
**Options:**
- [x] A) Use marker filename verbatim: `logs/version_vX.Y.Z_log.md` (recommended) — strict “use the semver file name as version”.
- [ ] B) Strip `v`: `logs/version_X.Y.Z_log.md` — aligns with `logs/versions_log.md` headings.
- [ ] C) Use a simpler name: `logs/vX.Y.Z.md` — shorter, deviates from requested pattern.
- [ ] D) Use a date-based name (e.g., `logs/2026-03-20.md`) — discoverable by time, not by version.
- [ ] Other — (describe below)
**Constraints & Guards:** Whatever is chosen must be documented in `README.md` and must not modify existing files under `logs/`.

### QID-AT-004 — Idempotency / existing per-version log file behavior
**Intent:** Define what happens if the target per-version log file already exists when the workflow runs.
**Rationale:** Reruns, race conditions (near-simultaneous merges), or manual file creation can cause the file to exist. The chosen behavior affects auditability and whether the SemVer marker and log files stay consistent.
**Impact Areas:** Requirements, Operations, Timeline
**Assumptions:**
- Existing `logs/` files must never be modified by the workflow.
**Answer Type:** single-select
**Options:**
- [x] A) Fail and do not bump the marker (recommended) — preserves marker/log consistency and avoids silent divergence.
- [ ] B) Fail but still bump the marker — avoids blocking version bump, risks missing log for that version.
- [ ] C) No-op: skip creating the log and still bump the marker — highest divergence risk, least noisy.
- [ ] D) Overwrite the existing log file — violates “no modification under `logs/`” intent.
- [ ] Other — (describe below)
**Constraints & Guards:** Option D is incompatible with the request constraint “do not change existing log files in `logs/`”.

---

## Appendix — Answer Encoding Rules
- Checkbox states:
  - Unchecked: `- [ ]`
  - Checked: `- [x]`
- Single-select validation:
  - Exactly one option must be checked per question (including `Other` if used).
- `Other` rule:
  - If `Other` is checked, include non-empty free text immediately with it.
- Recommended marker:
  - At most one option includes the literal string `(recommended)`.
- Parsing hint:
  - `QID` is the stable key for each question block; keep it unchanged across regenerations for this iteration.

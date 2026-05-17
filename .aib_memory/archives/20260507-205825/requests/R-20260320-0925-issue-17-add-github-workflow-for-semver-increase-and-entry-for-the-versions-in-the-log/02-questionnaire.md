# Iteration 02 Questionnaire

## Business & Functional Questions

### QID-BF-001 — Rollout policy for automated version bookkeeping
**Intent:** Select how strictly this automation should gate merge-readiness once enabled.
**Rationale:** This choice changes delivery risk, failure handling expectations, and how quickly the team can adopt the workflow without blocking releases unexpectedly.
**Impact Areas:** Scope, Requirements, Timeline, Operations
**Assumptions:**
- The workflow will mutate repository files when eligible.
- Maintainers want deterministic behavior over manual post-merge fixes.
**Answer Type:** single-select
**Options:**
- [x] A) Enforce immediately as required check (recommended) — strongest consistency, may block merges on misconfiguration.
- [ ] B) Start in observe-only mode for 1-2 releases — lower disruption, weaker early enforcement.
- [ ] C) Enforce only for selected labels/paths initially — phased rollout, added policy complexity.
- [ ] D) Keep optional manual trigger only — minimal disruption, low automation value.
- [ ] Other — (describe below)
**Constraints & Guards:** If A or C is selected, define required-check policy in README setup section.

## Architecture & Technical Questions

### QID-AT-001 — PR event trigger for marker/log mutation
**Intent:** Choose the exact event condition that performs PATCH bump and version-log append.
**Rationale:** Trigger timing is the primary control for idempotency and determines whether one logical change can create duplicate version bumps.
**Impact Areas:** Architecture, Operations, Timeline, Requirements
**Assumptions:**
- Version mutation should remain traceable to PR context.
**Answer Type:** single-select
**Options:**
- [ ] A) pull_request closed + merged=true (recommended) — one mutation per merged PR, strongest idempotency.
- [ ] B) pull_request synchronize — earliest feedback, high duplicate-bump risk.
- [x] C) push to main — simple trigger, weaker direct PR traceability.
- [ ] D) workflow_dispatch only — deterministic but manual and easy to forget.
- [x] Other — (describe below) main will be protected and no direct commits will be made to it, but approved PR only will be merged. The workflow should run during the merge of PR in main
**Constraints & Guards:** If B is selected, idempotency guard is mandatory before file writes.

### QID-AT-002 — Fallback behavior when workflow cannot write
**Intent:** Define behavior when branch protection or token permissions block direct commits.
**Rationale:** This decision determines whether release bookkeeping fails fast or continues via an alternate governance path.
**Impact Areas:** Architecture, Security, Operations, Timeline
**Assumptions:**
- Repository policies may differ between environments.
**Answer Type:** single-select
**Options:**
- [ ] A) Create follow-up bot PR (recommended) — policy-compliant, preserves audit trail, slower completion.
- [x] B) Fail workflow and require manual maintainer update — simple logic, more manual overhead.
- [ ] C) Require temporary permission elevation and retry — faster once approved, governance risk.
- [ ] D) Skip mutation and pass workflow — avoids blockers, violates bookkeeping guarantees.
- [ ] Other — (describe below)
**Constraints & Guards:** Option D is incompatible with request acceptance criteria.

### QID-AT-003 — Commit message policy for new version-log block
**Intent:** Choose which commit messages are written under the new version section.
**Rationale:** Message scope materially affects log usefulness, readability, and consistency across releases.
**Impact Areas:** Requirements, Operations, User Experience
**Assumptions:**
- Version log should stay human-readable while preserving traceability.
**Answer Type:** single-select
**Options:**
- [x] A) Include all PR commit subjects with normalization (recommended) — high traceability with controlled formatting.
- [ ] B) Include merge commit title/body only — concise, may omit meaningful changes.
- [ ] C) Include first line of each commit + deduplicate prefixes — balanced detail and readability.
- [ ] D) Include one generated summary sentence only — compact, least raw evidence.
- [ ] Other — (describe below)
**Constraints & Guards:** If A or C is selected, define deterministic normalization rules in implementation notes.

## Appendix — Answer Encoding Rules
- Checkbox states:
  - Unchecked: - [ ]
  - Checked: - [x]
- Single-select validation:
  - Exactly one option must be checked per question, including Other if used.
- Other option rule:
  - If Other is checked, add non-empty text directly below that question.
- Recommended option marker:
  - One option may include literal text (recommended).
- Parsing hint:
  - QID is the stable key for each question block.

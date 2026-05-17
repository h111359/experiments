## Overview
This iteration implements an automated release bookkeeping workflow for PRs merged into `main`. The workflow will (a) validate the SemVer marker state in `.aib_brain/`, (b) bump PATCH by 1 by rotating the marker filename, (c) append a new version section to `logs/versions_log.md` using the existing style and including Issue #17 and the PR’s commit subjects, and (d) update `README.md` with setup/permissions and operational behavior.

This plan is derived from `request.md` (Goal/Constraints/Success criteria), `02-analysis.md` (recommended implementation shape and risks), and `02-questionnaire.md` (policy choices for enforcement, trigger timing, fallback behavior, and commit message policy).

## Scope of Work
**In Scope**
- Add exactly one new GitHub Actions workflow file under `.github/workflows/`.
- Implement strict SemVer marker detection in `.aib_brain/` and PATCH+1 marker rotation.
- Append-only update to `logs/versions_log.md` (no edits to existing content).
- Collect PR commit subjects deterministically and include them in the new version block.
- Update root `README.md` with setup instructions and operational behavior.

**Out of Scope**
- Changing historical entries in `logs/versions_log.md`.
- Any MAJOR/MINOR bump logic.
- Additional CI workflows, additional automation modes, or release tooling beyond this bookkeeping.

**Assumptions**
- The repository uses PR merges into `main` (no direct human pushes).
- There is exactly one marker file in `.aib_brain/` named `vMAJOR.MINOR.PATCH` at the start of an eligible run.
- The versions log format shown in `logs/versions_log.md` is the authoritative style.

**Constraints**
- Do not change existing content in `logs/versions_log.md` — append only.
- The workflow must fail with explicit errors if SemVer marker preconditions are invalid (zero/multiple/malformed marker files).
- Chosen fallback policy: if the workflow cannot write/push changes, it must fail (no bot PR fallback).
- The solution must keep changes traceable to the triggering PR.

## Decision Gates (Blocking Questions & Answers)
1) 
**Question:** What is the minimal shippable outcome for this iteration (MSI) and what is explicitly excluded?
**Chosen Answer / Value:** MSI = one workflow + one implementation path that, on merged PRs to `main`, rotates `.aib_brain/vX.Y.Z` to `.aib_brain/vX.Y.(Z+1)`, appends a new `## Version X.Y.(Z+1)` block to `logs/versions_log.md`, and updates `README.md`. Excluded = changing past log entries, MAJOR/MINOR bumps, bot-PR fallback.
**Rationale:** Matches `request.md` acceptance criteria and questionnaire decisions.
**Evidence / Reference:** `request.md` (Goal/Constraints/Success criteria), `02-questionnaire.md` (QID-AT-002), `docs/Development_and_Deployment_Specification.md`.
**Impact if changed:** Expanding scope would require additional workflows/scripts and governance changes.

2)
**Question:** Which user-visible changes (if any) MUST be demonstrable at iteration end?
**Chosen Answer / Value:** Demonstrable artifacts: new workflow YAML; a new SemVer marker file name; one new appended version section in `logs/versions_log.md`; updated `README.md` instructions.
**Rationale:** These are the explicit deliverables.
**Evidence / Reference:** `request.md`.
**Impact if changed:** If demonstration requires live GitHub settings changes, it would become partially out-of-repo.

3)
**Question:** What are the non-functional targets applicable to this iteration (latency, throughput, availability, data freshness, cost ceiling)?
**Chosen Answer / Value:** Determinism and safety over performance: fail-fast validation; idempotent-by-trigger (one run per merge); append-only guarantee; least-privilege permissions; clear diagnostic logging.
**Rationale:** Workflow correctness and auditability are the main NFRs.
**Evidence / Reference:** `02-analysis.md` (risk themes), `docs/Development_and_Deployment_Specification.md`.
**Impact if changed:** Adding performance targets would be irrelevant to this CI-only change.

4)
**Question:** What input data sources and schemas are authoritative (include versions) and what happens if a field is missing/extra?
**Chosen Answer / Value:** N/A (no external data ingestion). Authoritative inputs are repository files and GitHub PR metadata (PR number, commit list).
**Rationale:** This iteration operates only on repo state and GitHub event payload.
**Evidence / Reference:** `request.md`.
**Impact if changed:** If external data were introduced, contracts and validation would be required.

5)
**Question:** What serialization formats, partitioning, and retention policies apply to new/changed datasets?
**Chosen Answer / Value:** N/A (no datasets). Output format is Markdown append to `logs/versions_log.md`.
**Rationale:** Only repository text files are modified.
**Evidence / Reference:** `logs/versions_log.md`.
**Impact if changed:** Would require data model docs updates (out of scope).

6)
**Question:** What are the error handling rules for ingestion/processing (retry policy, dead-letter, alerts, human-in-the-loop)?
**Chosen Answer / Value:** Fail fast with explicit messages; no retries for invalid SemVer state; no automatic human-in-the-loop. If push/write fails, fail the workflow (manual maintainer intervention required).
**Rationale:** Selected by questionnaire; avoids hidden partial updates.
**Evidence / Reference:** `02-questionnaire.md` (QID-AT-002).
**Impact if changed:** Bot PR fallback would require additional logic and governance.

7)
**Question:** Which algorithm/specification variant is in scope (if multiple exist), including parameters and defaults?
**Chosen Answer / Value:** Single variant: SemVer marker filename in `.aib_brain/` is canonical; bump PATCH only.
**Rationale:** Required by development spec and issue rules.
**Evidence / Reference:** `docs/Development_and_Deployment_Specification.md` (Canonical Version Rule), `docs/Copilot_Issue_Assignment_Rules.md`.
**Impact if changed:** Adding MINOR/MAJOR rules would change acceptance and docs.

8)
**Question:** What accuracy/quality thresholds or benchmarks must be met (and the measurement method)?
**Chosen Answer / Value:** Quality thresholds are structural: preconditions validated; append-only guarantee upheld; formatting matches existing log style; deterministic commit message normalization.
**Rationale:** No numeric benchmark applies.
**Evidence / Reference:** `request.md` + `logs/versions_log.md`.
**Impact if changed:** If strict formatting validation is added, more parsing logic is needed.

9)
**Question:** Are there hardware/compute constraints (local vs. remote execution, concurrency caps, cost limits)?
**Chosen Answer / Value:** Execute on GitHub-hosted runner (`ubuntu-latest`). Concurrency: ensure at most one run mutates at a time for `main` to avoid version bump races.
**Rationale:** Prevent duplicate bumps when multiple merges happen close together.
**Evidence / Reference:** `02-analysis.md` (duplicate bump risk).
**Impact if changed:** Without concurrency controls, parallel merges could contend and fail or double-bump.

10)
**Question:** Which API endpoints, message topics, or files are produced/consumed (names, versions, SLAs)?
**Chosen Answer / Value:** Consumed: `.aib_brain/v*` marker file(s), `logs/versions_log.md`, `README.md`, GitHub PR commits API. Produced: `.github/workflows/<workflow>.yml` and updated repo files.
**Rationale:** These are the only required interfaces.
**Evidence / Reference:** `request.md`.
**Impact if changed:** Adding other interfaces requires new docs and tests.

11)
**Question:** What compatibility must be preserved (backward/forward) and what is the deprecation plan if breaking changes are needed?
**Chosen Answer / Value:** Preserve the existing SemVer marker convention and existing version-log format; no breaking changes planned.
**Rationale:** This is a PATCH-level change to AIB tooling behavior.
**Evidence / Reference:** `docs/Development_and_Deployment_Specification.md` (SemVer policy), `logs/versions_log.md`.
**Impact if changed:** Breaking changes would require MAJOR bump and migration notes.

12)
**Question:** What identities/roles may access the new/changed assets (least privilege)?
**Chosen Answer / Value:** GitHub Actions `GITHUB_TOKEN` with minimal permissions: `contents: write` (needed to commit/push) and `pull-requests: read` (to list commits) if required.
**Rationale:** Least privilege for required operations only.
**Evidence / Reference:** `request.md` requires file mutations.
**Impact if changed:** Extra permissions increase risk; fewer permissions may block the workflow.

13)
**Question:** What data classifications are involved, and what masking/anonymization is required?
**Chosen Answer / Value:** N/A (commit subjects are already public repo metadata). Avoid printing tokens; do not log secrets.
**Rationale:** Only repository metadata is used.
**Evidence / Reference:** `SEC-03` is seeded placeholder; rely on standard GitHub Actions guidance.
**Impact if changed:** If private data is introduced, redaction rules must be added.

14)
**Question:** How are secrets injected at runtime, and what rotation policy is assumed?
**Chosen Answer / Value:** Use GitHub-provided `GITHUB_TOKEN` only; no additional secrets required.
**Rationale:** Keep setup minimal and secure.
**Evidence / Reference:** GitHub Actions standard behavior; `02-analysis.md` scope.
**Impact if changed:** Using PATs would require secret storage/rotation docs.

15)
**Question:** Which metrics/logs/traces prove the change is healthy (names and thresholds)?
**Chosen Answer / Value:** Workflow step logs must show: detected current version; computed next version; appended log bytes/lines; commit SHA pushed. Thresholds: all steps succeed; on failure, explicit reason.
**Rationale:** Operational evidence is workflow run output.
**Evidence / Reference:** `02-analysis.md` (operability theme).
**Impact if changed:** If deeper observability is needed, add structured outputs/artifacts.

16)
**Question:** What alerts must be configured or updated and who responds?
**Chosen Answer / Value:** N/A (no alerting system integration). Response owner: repo maintainers monitoring failed workflow runs.
**Rationale:** This is repo-local automation.
**Evidence / Reference:** `request.md`.
**Impact if changed:** Would require on-call/runbook integration.

17)
**Question:** What runbook/SOP updates are required, if any?
**Chosen Answer / Value:** Update `README.md` with: required permissions, branch protection notes, expected behavior, and manual remediation steps on workflow failure.
**Rationale:** README is the requested operational doc.
**Evidence / Reference:** `request.md`.
**Impact if changed:** If a separate runbook is required, would add new docs (out of scope).

18)
**Question:** Which product docs must be created or updated (paths), and is editing permitted (per references)?
**Chosen Answer / Value:** No product-doc updates. Only repository `README.md` is updated; all `.aib_memory/docs/...` entries are `edit_allowed = N` and remain unchanged.
**Rationale:** Request is process/workflow centric.
**Evidence / Reference:** `.aib_memory/references.md`.
**Impact if changed:** Editing product-docs would require explicit permission.

19)
**Question:** What acceptance evidence will be recorded and where?
**Chosen Answer / Value:** Evidence = workflow run logs + resulting repository diffs (marker file rename, appended log, README changes). Record verification notes in `implementation.md` for this request.
**Rationale:** Provides traceability for reviewers.
**Evidence / Reference:** `implementation.md` template; `request.md` success criteria.
**Impact if changed:** If formal reports are needed, add artifacts upload (out of scope).

20)
**Question:** What is the rollback strategy if acceptance fails?
**Chosen Answer / Value:** Revert the workflow commit(s) and restore the previous SemVer marker file name; remove the appended version-log block via revert commit (do not edit history directly).
**Rationale:** Rollback should preserve append-only policy by reverting, not editing.
**Evidence / Reference:** `logs/versions_log.md` append-only constraint.
**Impact if changed:** Manual file edits would violate governance.

## Work Breakdown Structure (WBS)

### Task 1: Finalize trigger + write strategy contract
**Intent:** Resolve exact GitHub event trigger and write/push contract to align with branch protection and questionnaire answers.
**Inputs:** `request.md`, `02-questionnaire.md`, `02-analysis.md`, GitHub Actions event semantics.
**Outputs:** Finalized workflow trigger condition and documented contract (captured in plan + README section outline).
**Procedure:**
1. Resolve the ambiguity in `02-questionnaire.md` where two trigger options were checked; select a single trigger.
2. Choose the trigger that matches “run during merge of PR into main” and preserves one mutation per PR.
3. Confirm that direct pushes by Actions are either permitted (so workflow can succeed) or will fail explicitly per chosen fallback.
4. Define concurrency behavior to avoid parallel version bumps.
**Done Criteria:**
- One trigger strategy is selected and recorded in this plan and later in README.
- Concurrency/serialization approach is defined.
**Dependencies:** None.
**Risk Notes:** Misaligned trigger can cause duplicate PATCH increments.

### Task 2: Implement deterministic release bookkeeping script
**Intent:** Centralize SemVer detection/bump + log append logic in a repository script that can be called from the workflow.
**Inputs:** `docs/Development_and_Deployment_Specification.md`, `docs/Copilot_Issue_Assignment_Rules.md`, current `.aib_brain/v*` marker file, `logs/versions_log.md` format, PR metadata (issue number, commit subjects).
**Outputs:** A new script file (location to be chosen, e.g. `.aib_brain/tools/release_bookkeeping.py`) with a stable CLI interface.
**Procedure:**
1. Discover marker files in `.aib_brain/` matching `^v\d+\.\d+\.\d+$`.
2. Fail if count != 1 or filename is malformed.
3. Parse version, compute PATCH+1, and rotate marker file (delete old, create new empty file).
4. Read `logs/versions_log.md` and append a new block at EOF only:
   - `## Version <new>`
   - blank line
   - issue header referencing Issue #17 (and optionally PR number)
   - commit subjects as a deterministic bullet list
5. Implement normalization rules for commit subjects (trim whitespace; collapse internal whitespace; preserve order; remove empty lines).
6. Make script emit explicit, human-readable errors and exit non-zero on failure.
**Done Criteria:**
- Script fails on 0/multiple markers and on malformed marker filename.
- Script produces exactly one new marker file name `vX.Y.(Z+1)` and removes the old.
- `logs/versions_log.md` changes are append-only and match the existing section style.
- Script can run on GitHub runner without nonstandard dependencies.
**Dependencies:** Task 1.
**Risk Notes:** Incorrect parsing or formatting could violate append-only requirement.

### Task 3: Add GitHub Actions workflow to run on merge to main
**Intent:** Create the single workflow file that orchestrates bookkeeping and persists changes.
**Inputs:** Task 1 decision, Task 2 script, GitHub Actions docs for permissions and PR event payload.
**Outputs:** One new workflow file under `.github/workflows/`.
**Procedure:**
1. Define workflow trigger for PRs targeting `main` with a merge-time condition.
2. Set least-privilege permissions required for repo writes.
3. Checkout repository and set a consistent git identity for automation commits.
4. Collect PR commit subjects deterministically (via event payload and/or GitHub API).
5. Invoke the script with required inputs (issue number, commit subjects, PR metadata).
6. Commit and push changes; if push fails, fail the workflow with an explicit message (per selected fallback).
7. Add concurrency guard to prevent simultaneous bumps.
**Done Criteria:**
- Exactly one workflow file is added.
- Workflow fails explicitly for invalid marker state.
- On eligible run, workflow commits and pushes only the intended files: marker rotation, `logs/versions_log.md` append, `README.md` update (if included in same change set), and no other diffs.
- After push step, `git status --porcelain` is empty on runner.
**Dependencies:** Task 2.
**Risk Notes:** Branch protections may block pushing; in that case, workflow must fail clearly.

### Task 4: Update README with setup + operational guidance
**Intent:** Document how to enable and operate the workflow safely.
**Inputs:** Task 1 decisions, workflow permissions, branch protection expectations, questionnaire answers.
**Outputs:** Updated `README.md`.
**Procedure:**
1. Add a section describing what the workflow does (marker bump, versions log append, commit messages).
2. Add setup steps: required workflow permissions (`Read and write`), required check rollout (immediate enforcement), and branch protection prerequisites.
3. Document trigger behavior (“runs when PR is merged into main”) and traceability (commit message source).
4. Document failure modes and remediation steps (invalid marker state, push blocked -> manual maintainer update).
**Done Criteria:**
- `README.md` contains clear setup instructions and behavior notes aligned with the implemented workflow.
- README explicitly calls out append-only behavior for `logs/versions_log.md`.
**Dependencies:** Task 1, Task 3.
**Risk Notes:** Misleading docs can cause misconfiguration and blocked merges.

### Task 5: Verification and acceptance evidence capture
**Intent:** Verify implementation against acceptance criteria and record evidence.
**Inputs:** Modified repo state, workflow YAML, script output, `request.md` success criteria.
**Outputs:** Updated `implementation.md` entry for iteration 02 with verification steps and results.
**Procedure:**
1. Validate locally (or via workflow run) that exactly one marker file exists and bump is correct.
2. Validate `logs/versions_log.md` diff is append-only (no earlier lines changed).
3. Validate workflow fails with explicit errors in invalid states (0 markers, >1 markers).
4. Validate that after workflow execution path, there are no uncommitted changes on runner (document the check used).
5. Record evidence and guidance for a maintainer to verify.
**Done Criteria:**
- Acceptance criteria from `request.md` are met and recorded.
- `implementation.md` includes verification notes for iteration 02.
**Dependencies:** Task 3, Task 4.
**Risk Notes:** Without a real PR run, some permission issues may remain undiscovered.

## Dependencies & Interfaces

| From Task | To Task | Dependency Type (FS/SS/FF/SF) | Critical (Y/N) | Notes |
|---|---|---|---|---|
| 1 | 2 | FS | Y | Script contract depends on final trigger/write rules |
| 2 | 3 | FS | Y | Workflow calls the script |
| 1 | 4 | FS | Y | README must reflect chosen trigger/permissions |
| 3 | 4 | FS | Y | README must match implemented workflow |
| 3 | 5 | FS | Y | Verification depends on workflow existing |
| 4 | 5 | FS | N | Evidence can be captured after docs update |

| Interface | Direction (In/Out) | Protocol/Contract | Version | Notes |
|---|---|---|---|---|
| GitHub PR event payload | In | `pull_request` event JSON | GitHub API | Source of PR number/base/head |
| GitHub PR commits API | In | REST via `GITHUB_TOKEN` | GitHub API | Used to fetch commit subjects deterministically |
| Repository content | In/Out | Git working tree | N/A | `.aib_brain/`, `logs/`, `README.md` |

## Environment & Configuration
**Environments**
- GitHub Actions runner: `ubuntu-latest`.

**Config Keys**
| Key | Scope (Env/Global) | Default | Allowed Range/Values | Source (file/path) | Change Control |
|---|---|---|---|---|---|
| `GITHUB_TOKEN` | Env | provided by GitHub | N/A | GitHub Actions runtime | Repo settings |
| Workflow permissions | Global | read-only | `Read and write` required | GitHub repo settings | Maintainer |

**Secrets Handling**
- No additional secrets; use the built-in `GITHUB_TOKEN`. Do not print tokens in logs.

## Testing Strategy (This Iteration)
- **Unit (script-level):** run the script on a controlled local copy to validate marker detection, version bump, and log append formatting.
- **Integration (workflow):** merge a test PR (or use a temporary branch policy) to confirm the workflow triggers once and persists changes.
- **Negative tests:** create temporary invalid marker states (0 marker, 2 markers) in a branch to ensure workflow fails with explicit errors.
- **Acceptance Evidence:** capture the workflow run URL(s) and the resulting diff summary in `implementation.md`.

## Observability & Quality Gates
- **Workflow logs must include:** detected marker filename, computed next version, number of commit subjects captured, and the commit SHA pushed.
- **Quality gates (pass/fail):**
  - Marker preconditions validated (exactly one marker).
  - `logs/versions_log.md` modified only by appending.
  - Workflow exits non-zero with explicit error message when preconditions are invalid.
  - Working tree clean at end of workflow run (`git status --porcelain` empty).

## Documentation Touchpoints
| Doc Path | Change Type | Update Trigger | Edit Allowed | Notes |
|---|---|---|---|---|
| `README.md` | update | Task 4 | Y | Add setup + behavior + remediation guidance |
| `.aib_memory/docs/...` (all product-docs) | no-change | N/A | N | Keep unchanged per references |

## Milestones
| Milestone | Description | Due | Depends On | Exit Criteria |
|---|---|---|---|---|
| M1 | Workflow + script implemented | N/A | Tasks 1–3 | Workflow file present; script runs end-to-end locally |
| M2 | Docs + verification complete | N/A | Tasks 4–5 | README updated; evidence captured; acceptance criteria met |

## Risks & Mitigations
1. **Branch protection blocks push from workflow** (Prob: Medium, Impact: High) — Mitigation: document required permissions; fail explicitly with remediation steps; test on a controlled PR.
2. **Duplicate version bumps from concurrent merges** (Prob: Low-Med, Impact: Medium) — Mitigation: workflow concurrency group + precondition re-check right before push.
3. **Append-only violation by formatting logic** (Prob: Low, Impact: High) — Mitigation: implement append-only writer; validate by comparing pre-content checksum/line count.
4. **Commit message noise / instability** (Prob: Medium, Impact: Low-Med) — Mitigation: deterministic normalization and stable ordering.

## Acceptance & Handover
- **Iteration Acceptance Criteria:**
  - One new workflow file exists under `.github/workflows/`.
  - Marker transitions from `vX.Y.Z` to `vX.Y.(Z+1)` on eligible run.
  - A new version block is appended at EOF in `logs/versions_log.md` only.
  - `README.md` contains setup and usage guidance.
  - Workflow provides explicit failures for invalid SemVer marker states.
- **Handover Artifacts:** updated repo files + workflow run logs referenced in `implementation.md`.
- **Post-Iteration Follow-ups:** if maintainer requires bot-PR fallback instead of failure-on-write, raise a new request (out of scope for this iteration).

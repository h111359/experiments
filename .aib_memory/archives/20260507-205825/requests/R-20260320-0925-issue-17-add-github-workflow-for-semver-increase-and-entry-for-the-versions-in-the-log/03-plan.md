## Overview
This iteration implements Issue #17 release-bookkeeping automation for PRs targeting `main`: a GitHub Actions workflow bumps the `.aib_brain/` SemVer marker (PATCH +1), creates a new per-version log file under `logs/`, and updates `README.md` with setup + behavior guidance.

This plan is based on `request.md` (Goal/Constraints/Acceptance criteria), `03-analysis.md` (iteration 03 scope delta: per-version log files, not `logs/versions_log.md`), and `03-questionnaire.md` (trigger/naming/idempotency choices).

## Scope of Work
**In Scope**
- Add exactly one workflow file under `.github/workflows/`.
- Validate exactly one SemVer marker file exists in `.aib_brain/` matching `^vMAJOR.MINOR.PATCH$` and fail with explicit errors otherwise.
- Compute the next version by incrementing PATCH by 1; rotate the marker file accordingly (old removed, new empty file created).
- Create a new per-version markdown log file under `logs/` using the existing log style as guidance.
- Update `README.md` with required repo settings, workflow permissions, branch-policy prerequisites, behavior, and failure remediation.
- Record append-only implementation evidence in `implementation.md`.

**Out of Scope**
- Modifying any existing file under `logs/` (including `logs/versions_log.md`).
- MAJOR/MINOR version bump logic.
- Adding more than one workflow file.

**Assumptions**
- Current repo has exactly one marker file in `.aib_brain/` (observed in `03-analysis.md`: `v1.0.4`).
- Commit message policy remains “PR commit subjects with deterministic normalization” (from `02-questionnaire.md` QID-AT-003).

**Constraints**
- Must fail with explicit errors if marker preconditions are invalid (zero/multiple/malformed).
- Must preserve existing `logs/` content without modification; only add new files.
- Must keep changes traceable to the triggering PR.
- Product-doc files listed in `.aib_memory/references.md` are `edit_allowed = N` and must not be edited.

## Decision Gates (Blocking Questions & Answers)

1) 
**Question:** What is the minimal shippable outcome for this iteration (MSI) and what is explicitly excluded?
**Chosen Answer / Value:** MSI = one workflow that (a) rotates `.aib_brain/vX.Y.Z` to `.aib_brain/vX.Y.(Z+1)`, (b) creates `logs/version_<newVersion>_log.md`. Excluded = modifying existing files under `logs/`, MAJOR/MINOR bumps, multiple workflows. In addition updates `README.md` one time with instructions for implementation of the workflow.
**Rationale:** Matches iteration 03 scope delta and request constraints.
**Evidence / Reference:** `request.md` (Goal/Constraints), `03-analysis.md` (Executive Summary).
**Impact if changed:** Would require new requirements and a new iteration.

2)
**Question:** Which user-visible changes (if any) MUST be demonstrable at iteration end?
**Chosen Answer / Value:** Demonstrable artifacts: `.github/workflows/<workflow>.yml`, and updated `README.md`.
**Rationale:** These are the explicit deliverables.
**Evidence / Reference:** `request.md` (Acceptance criteria), `03-analysis.md`.
**Impact if changed:** If live GitHub settings changes are required, some acceptance becomes out-of-repo.

3)
**Question:** What are the non-functional targets applicable to this iteration (latency, throughput, availability, data freshness, cost ceiling)?
**Chosen Answer / Value:** Determinism and safety over performance: fail-fast validation; idempotent-per-merge behavior; no modification of existing logs; clear diagnostics; clean working tree after run.
**Rationale:** CI workflow correctness/auditability is the main quality bar.
**Evidence / Reference:** `request.md` (explicit errors, traceability), `03-analysis.md` (risks).
**Impact if changed:** Adding performance/cost targets would increase scope without benefit.

4)
**Question:** What input data sources and schemas are authoritative (include versions) and what happens if a field is missing/extra?
**Chosen Answer / Value:** Inputs are repository state (`.aib_brain/` marker set) and GitHub event payload/PR metadata. Missing PR context fields must cause explicit failure or graceful fallback to available commit subjects.
**Rationale:** No external datasets are involved.
**Evidence / Reference:** `request.md`, `03-analysis.md`.
**Impact if changed:** Introducing external sources would require new contracts and documentation.

5)
**Question:** What serialization formats, partitioning, and retention policies apply to new/changed datasets?
**Chosen Answer / Value:** N/A — outputs are repository Markdown files only (new file under `logs/`).
**Rationale:** No datasets.
**Evidence / Reference:** `request.md`.
**Impact if changed:** Would require additional data strategy documentation.

6)
**Question:** What are the error handling rules for ingestion/processing (retry policy, dead-letter, alerts, human-in-the-loop)?
**Chosen Answer / Value:** Fail fast with explicit errors; no retries for invalid marker state; if repo writes are blocked, fail with explicit remediation steps.
**Rationale:** Prevent partial updates and preserve auditability.
**Evidence / Reference:** `request.md` (explicit errors), `02-questionnaire.md` QID-AT-002.
**Impact if changed:** Bot-PR fallback adds governance + complexity.

7)
**Question:** Which algorithm/specification variant is in scope (if multiple exist), including parameters and defaults?
**Chosen Answer / Value:** Single SemVer marker file `vMAJOR.MINOR.PATCH` in `.aib_brain/`; bump PATCH only.
**Rationale:** Required by the request and existing product lifecycle.
**Evidence / Reference:** `request.md`, `03-analysis.md`.
**Impact if changed:** MINOR/MAJOR logic changes acceptance and documentation.

8)
**Question:** What accuracy/quality thresholds or benchmarks must be met (and the measurement method)?
**Chosen Answer / Value:** Structural correctness: marker validation and patch bump correct; new log filename correct; created file content matches style; workflow leaves clean working tree.
**Rationale:** No numeric ML-style benchmark applies.
**Evidence / Reference:** `request.md` (clean working tree), `logs/versions_log.md` style guidance.
**Impact if changed:** Would require additional validation tooling.

9)
**Question:** Are there hardware/compute constraints (local vs. remote execution, concurrency caps, cost limits)?
**Chosen Answer / Value:** Run on GitHub-hosted runner (`ubuntu-latest`). Enforce concurrency (single writer) for `main` to reduce version bump races.
**Rationale:** Prevent simultaneous merges from conflicting.
**Evidence / Reference:** `03-analysis.md` (primary risks).
**Impact if changed:** Without concurrency, version bumps can race.

10)
**Question:** Which API endpoints, message topics, or files are produced/consumed (names, versions, SLAs)?
**Chosen Answer / Value:** Consumed: `.aib_brain/v*`, PR commit subjects, `README.md`. Produced/changed: `.github/workflows/<workflow>.yml`, `.aib_brain/vX.Y.(Z+1)` (marker rotation), `logs/version_vX.Y.(Z+1)_log.md`, `README.md`.
**Rationale:** These are the required artifacts.
**Evidence / Reference:** `request.md`, `03-questionnaire.md` QID-AT-003.
**Impact if changed:** Adds new interfaces and documentation work.

11)
**Question:** What compatibility must be preserved (backward/forward) and what is the deprecation plan if breaking changes are needed?
**Chosen Answer / Value:** Preserve existing SemVer marker convention; do not change existing logs. No breaking changes planned.
**Rationale:** This is a patch-level workflow automation.
**Evidence / Reference:** `request.md` constraints.
**Impact if changed:** Would require migration/major bump policy.

12)
**Question:** What identities/roles may access the new/changed assets (least privilege)?
**Chosen Answer / Value:** Use GitHub Actions `GITHUB_TOKEN` with least privileges needed (`contents: write` if pushing changes; `pull-requests: read` if reading PR metadata).
**Rationale:** Required to write repository files.
**Evidence / Reference:** `request.md` (requires mutations).
**Impact if changed:** Too few permissions blocks the workflow; too many increases risk.

13)
**Question:** What data classifications are involved, and what masking/anonymization is required?
**Chosen Answer / Value:** N/A — commit subjects are repository metadata; do not log tokens or secrets.
**Rationale:** No sensitive inputs are introduced by design.
**Evidence / Reference:** `request.md`.
**Impact if changed:** If sensitive data appears, add redaction rules.

14)
**Question:** How are secrets injected at runtime, and what rotation policy is assumed?
**Chosen Answer / Value:** No new secrets; use `GITHUB_TOKEN` only.
**Rationale:** Keeps setup minimal.
**Evidence / Reference:** `03-analysis.md` suggested approach.
**Impact if changed:** PAT usage would require secret store + rotation guidance.

15)
**Question:** Which metrics/logs/traces prove the change is healthy (names and thresholds)?
**Chosen Answer / Value:** Workflow step logs must show: marker detected, new version computed, log file path created, git commit created, and push attempted/succeeded. Threshold: job success; explicit failure message otherwise.
**Rationale:** Workflow run logs are the operational trace.
**Evidence / Reference:** `request.md` success criteria.
**Impact if changed:** Would require external monitoring.

16)
**Question:** What alerts must be configured or updated and who responds?
**Chosen Answer / Value:** N/A — no alerting integration. Response owner: repo maintainers monitoring failed workflow runs.
**Rationale:** Repo-local automation.
**Evidence / Reference:** `request.md`.
**Impact if changed:** Would require alerting platform integration.

17)
**Question:** What runbook/SOP updates are required, if any?
**Chosen Answer / Value:** Update `README.md` with setup steps, permissions, branch protection prerequisites, and remediation for failure modes (invalid marker, write blocked).
**Rationale:** Explicitly required by the request.
**Evidence / Reference:** `request.md`.
**Impact if changed:** A separate runbook would add new docs.

18)
**Question:** Which product docs must be created or updated (paths), and is editing permitted (per references)?
**Chosen Answer / Value:** No product-doc edits (all `edit_allowed = N`). Only `README.md` is updated (not part of the product-doc references set).
**Rationale:** Keep references-respecting edits.
**Evidence / Reference:** `.aib_memory/references.md`.
**Impact if changed:** Would require follow-up request/permission to edit product-docs.

19)
**Question:** What acceptance evidence will be recorded and where?
**Chosen Answer / Value:** Evidence = git diff showing single workflow file added, marker filename bump, new `logs/version_*_log.md` file added, README updated; plus sample workflow run log excerpt. Record a new entry in `implementation.md`.
**Rationale:** Provides reviewer traceability.
**Evidence / Reference:** `implementation.md` template.
**Impact if changed:** Would require artifact uploads/screenshots.

20)
**Question:** What is the rollback strategy if acceptance fails?
**Chosen Answer / Value:** Revert the workflow change commit(s) and revert marker/log/README changes via git revert (no manual edits to existing logs).
**Rationale:** Preserves append-only posture and audit trail.
**Evidence / Reference:** `request.md` constraints.
**Impact if changed:** Manual modifications risk breaking constraints.

## Work Breakdown Structure (WBS)

### Task 1: Reconcile trigger + write policy (resolve questionnaire contradiction)
**Intent:** Make trigger timing and repo-write mechanism internally consistent before implementation.
**Inputs:** `03-questionnaire.md` (QID-AT-001/QID-AT-002), `request.md` constraints, GitHub branch protection settings.
**Outputs:** Updated decision record in this plan (and, if needed, updated `03-questionnaire.md` selections).
**Procedure:**
1. Review the current selections: QID-AT-001 selects `push` to `main`, while QID-AT-002 selects “disallow pushes to main; push to PR branch”.
2. Choose one consistent operational model:
   - Model M1: merge-time mutation + Actions can push to `main` (typical approach: `pull_request` closed merged, `contents: write`).
   - Model M2: pre-merge mutation on PR branch (requires `pull_request` triggers and careful loop prevention).
   - Model M3: merge-time mutation via bot PR (requires creating a PR rather than pushing to `main`).
3. Record the chosen model and update downstream task assumptions accordingly.
**Done Criteria:**
- Exactly one model is selected and the plan has no internal contradictions.
**Dependencies:** None.
**Risk Notes:** Leaving this unresolved will cause workflow failure or unintended behavior.

### Task 2: Define the per-version log file content format
**Intent:** Specify a deterministic markdown format for `logs/version_<version>_log.md` aligned with existing style.
**Inputs:** `logs/versions_log.md` (style reference), `request.md` (Issue reference requirement), `02-questionnaire.md` QID-AT-003 (commit subjects policy).
**Outputs:** A concrete format spec (documented in `logs/versions_log_convention.md` ) including headings and bullet formatting.
**Procedure:**
1. Mirror the existing style: use a version heading and an Issue section.
2. Include Issue #17 reference and PR identifier (when available) for traceability.
3. List commit subjects as bullets; apply deterministic normalization (trim, collapse whitespace, preserve order, drop empty lines).
**Done Criteria:**
- Format spec is documented and testable with sample input.
**Dependencies:** Task 1.
**Risk Notes:** Style mismatch may be rejected in review.

### Task 3: Implement the bookkeeping script (marker validation + bump + log creation)
**Intent:** Create a repo script that performs all filesystem mutations deterministically and fails safely.
**Inputs:** `.aib_brain/` marker files, chosen content format (Task 2), chosen filename rule (QID-AT-003), idempotency rule (QID-AT-004).
**Outputs:** One script file in-repo (path to be chosen during implementation) and a stable CLI contract.
**Procedure:**
1. Discover marker files under `.aib_brain/` matching `^v\d+\.\d+\.\d+$`.
2. Fail if marker count != 1; include explicit error text.
3. Parse version and compute next PATCH.
4. Determine target log path per QID-AT-003: `logs/version_vX.Y.Z_log.md`.
5. Enforce QID-AT-004: if log file exists, fail and do not bump the marker.
6. Create the per-version log file with the deterministic format.
7. Rotate the marker file (remove old marker, create new empty marker).
**Done Criteria:**
- Script exits non-zero with clear errors on invalid marker state.
- On success, exactly these changes occur: one marker rotation + one new log file; no edits to existing `logs/*`.
**Dependencies:** Task 1, Task 2.
**Risk Notes:** Ordering matters (must not bump marker if log creation fails).

### Task 4: Add the single GitHub Actions workflow
**Intent:** Orchestrate the script on the chosen trigger and persist changes with traceability.
**Inputs:** Task 1 trigger decision, Task 3 script, GitHub event payload fields needed for commit subjects.
**Outputs:** Exactly one workflow file under `.github/workflows/`.
**Procedure:**
1. Implement the `on:` trigger per Task 1 selection (merge-time or pre-merge model).
2. Set minimal permissions (`contents: write` if pushing commits; add `pull-requests: read` only if needed).
3. Checkout the repository.
4. Gather commit subjects deterministically (from PR API if using PR trigger; from push payload as fallback).
5. Run the bookkeeping script.
6. Commit and push changes according to the selected governance model.
7. Validate clean working tree (`git status --porcelain` empty).
**Done Criteria:**
- Workflow file exists and passes YAML syntax.
- Workflow fails explicitly on invalid marker state or write failure.
- No other workflows are added.
**Dependencies:** Task 1, Task 3.
**Risk Notes:** Branch protection may block pushes; must be handled consistently.

### Task 5: Update `README.md` with setup + behavior + remediation
**Intent:** Provide maintainers/contributors clear operational instructions.
**Inputs:** Task 1 trigger/write model, Task 4 workflow permissions, Task 2 log format.
**Outputs:** Updated `README.md`.
**Procedure:**
1. Document what the workflow does (marker bump, new per-version log file).
2. Document required repo settings: Actions permissions and branch protection prerequisites.
3. Document filename rule (QID-AT-003) and idempotency rule (QID-AT-004).
4. Document failure modes and remediation steps.
**Done Criteria:**
- README contains configuration + usage guidance aligned to the implemented workflow.
**Dependencies:** Task 1, Task 4.
**Risk Notes:** Misdocumentation leads to misconfiguration and broken merges.

### Task 6: Record implementation evidence in `implementation.md`
**Intent:** Capture what changed and how to verify.
**Inputs:** Git diff summary after implementation, workflow run output (if available).
**Outputs:** One new append-only entry under `implementation.md` for iteration `03`.
**Procedure:**
1. Add an entry with implemented changes, verification steps, and evidence.
2. Include the list of files changed and expected outputs.
**Done Criteria:**
- `implementation.md` has a new iteration 03 entry and remains append-only.
**Dependencies:** Task 4, Task 5.
**Risk Notes:** Missing evidence slows review.

## Dependencies & Interfaces

**Internal task dependencies**
| From Task | To Task | Dependency Type (FS/SS/FF/SF) | Critical (Y/N) | Notes |
|---|---|---|---|---|
| 1 | 2 | FS | Y | Must resolve contradictions before format finalization |
| 2 | 3 | FS | Y | Script needs finalized log format |
| 3 | 4 | FS | Y | Workflow calls the script |
| 1 | 4 | FS | Y | Workflow trigger/write model depends on decision |
| 4 | 5 | FS | Y | README must reflect the actual workflow |
| 4 | 6 | FS | N | Evidence capture after implementation |
| 5 | 6 | FS | N | Evidence capture after documentation update |

**External interfaces (systems, data, modules)**
| Interface | Direction (In/Out) | Protocol/Contract | Version | Notes |
|---|---|---|---|---|
| GitHub Actions runner | In | Workflow jobs/steps | N/A | Use `ubuntu-latest` |
| GitHub API (optional) | In | PR metadata/commits | v3 REST | Only if needed for commit subjects |
| Repository (git) | Out | Commit + push | N/A | Must remain traceable to triggering PR |

## Environment & Configuration
**Environments**
- GitHub-hosted runner only.

**Config Keys**
| Key | Scope (Env/Global) | Default | Allowed Range/Values | Source (file/path) | Change Control |
|---|---|---|---|---|---|
| `GITHUB_TOKEN` | Env | Provided by Actions | N/A | GitHub Actions runtime | Repo settings |

**Secrets Handling:** Use GitHub-provided `GITHUB_TOKEN` only; do not add PATs or inline secrets.

## Testing Strategy (This Iteration)
- Test Types: Script-level validation + workflow-level dry validation.
- Data/Fixtures: Local copies of `.aib_brain/` marker files and a temporary `logs/` directory in tests (if implemented).
- Test Execution:
  - Validate script behavior for: 0 markers, 2 markers, malformed marker, existing target log file.
  - Validate workflow syntax and that it runs on the chosen trigger.
- Acceptance Evidence:
  - Git diff showing only allowed files changed.
  - Workflow logs showing explicit success/failure messages.

## Observability & Quality Gates
- Key Logs: workflow step logs for marker detection, computed new version, created log path, git commit/push.
- Quality Gates:
  - Exactly one workflow file added under `.github/workflows/`.
  - Existing files under `logs/` unchanged; only new log file added.
  - Marker rotation is correct: `vX.Y.Z` -> `vX.Y.(Z+1)`.
  - Workflow ends with clean working tree check.

## Documentation Touchpoints
| Doc Path | Change Type | Update Trigger | Edit Allowed | Notes |
|---|---|---|---|---|
| .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Architecture/ARCH-02.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Architecture/ARCH-03.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Architecture/ARCH-04.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Architecture/ARCH-06.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Inventory/ARCH-07.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Compute/CMP-01.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Compute/CMP-02.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Data Sources/DATA-01.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Data Models/DATA-02.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Data Workspace/DATA-03.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Data Workspace/DATA-04.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Data Workspace/DATA-05.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Analytics/DATA-06.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Data Workspace/DATA-07.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Data Workspace/DATA-08.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Analytics/DATA-09.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Observability/OBS-01.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/01 Product Management/Product Charter/RQT-01.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/03 Requirements/RQT-02.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Access and Security/SEC-01.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Access and Security/SEC-02.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Access and Security/SEC-03.md | no-change | — | N | Seeded placeholder; do not edit |
| .aib_memory/docs/04 Technology/Access and Security/SEC-04.md | no-change | — | N | Seeded placeholder; do not edit |

Notes:
- `README.md` is updated by Task 5 but is not a product-doc reference entry.

## Milestones
| Milestone | Description | Due | Depends On | Exit Criteria |
|---|---|---|---|---|
| M1 | Decisions locked | N/A | Task 1 | Trigger/write model consistent and recorded |
| M2 | Script complete | N/A | Task 3 | Script passes negative/positive checks |
| M3 | Workflow complete | N/A | Task 4 | Workflow exists and meets quality gates |
| M4 | Docs + evidence complete | N/A | Task 5, Task 6 | README updated; implementation log entry added |

## Risks & Mitigations
- R1: Trigger/write-policy contradiction causes failed workflow — P:High, I:High — Mitigation: Task 1 resolves before implementation.
- R2: Branch protection blocks workflow writes — P:Med, I:High — Mitigation: document prerequisites; select bot-PR model if required.
- R3: Concurrent merges cause version bump race — P:Med, I:Med — Mitigation: workflow concurrency group for `main`.
- R4: Log format rejected as inconsistent — P:Low, I:Med — Mitigation: Task 2 defines concrete format aligned to `logs/versions_log.md`.

## Acceptance & Handover
- Iteration Acceptance Criteria:
  - One new workflow file under `.github/workflows/`.
  - Marker file transitions from `vX.Y.Z` to `vX.Y.(Z+1)`.
  - A new file exists under `logs/` named `version_vX.Y.(Z+1)_log.md` (per QID-AT-003).
  - No existing file under `logs/` is modified.
  - README includes configuration and usage guidance.
  - Workflow includes a clean working tree check.

- Handover Artifacts:
  - Workflow YAML file.
  - Script implementing the bump/log creation.
  - Updated `README.md`.
  - Append-only entry in `implementation.md`.

- Post-Iteration Follow-ups:
  - If governance requires bot-PR rather than direct pushes, open a follow-up request to scope that alternative model cleanly.

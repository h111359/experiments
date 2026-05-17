# Plan

---

## Overview

This plan covers a single, read-only workspace review and the authoring of `proposals.md` containing at least 30 concrete, AI-actionable improvement proposals for the AIB framework.

The scope is entirely advisory: no framework code is changed; no `.aib_brain/` assets are modified. The deliverable is one Markdown file written to `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md`.

Inputs: `request.md` (Goal, Scope, Out of Scope, Constraints, Success criteria), `01-analysis.md` (Section 7 — Research Plan and Findings; Section 8 — Rewrite Proposal; Section 9 — Solution Options A recommended). No questionnaire exists; no blocking decisions remain open.

---

## Scope of Work

**In Scope**

- Full read of all `.aib_brain/` files (completed during analysis phase)
- Authoring of `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md`
- Exactly 30 numbered, categorized, self-contained improvement proposals

**Out of Scope**

- Any modification of `.aib_brain/` contents
- Any modification of `scripts/`, `docs/`, `logs/`, or `.aib_memory/docs/` files
- Any code execution, test runs, or dependency installation
- Creating additional output files beyond `proposals.md`

**Assumptions**

- All `.aib_brain/` files were fully read during the analysis phase; no re-read is required unless a specific detail needs confirmation
- Product-doc stubs in `.aib_memory/docs/` are intentionally empty (default seeds); no content inference needed from them
- No questionnaire answers exist; plan proceeds directly from analysis

**Constraints**

- Write access limited to `proposals.md` only
- Proposals must be AI-actionable without further clarification
- Proposals must span diverse categories (Prompts, Conventions, Tools, Organization/Concepts)
- `.aib_brain/` contents are out of scope for any modifications in this request

---

## Decision Gates (Blocking Questions & Answers)

**A. Scope & Outcome**

- Question: What is the minimal shippable outcome for this iteration?
- Chosen Answer / Value: A single `proposals.md` file containing exactly 30 numbered, categorized, AI-actionable improvement proposals.
- Rationale: Directly specified in request success criteria.
- Evidence / Reference: `request.md` § Success criteria; `01-analysis.md` § 9 Option A.
- Impact if changed: Changing to multiple files or fewer than 30 proposals would fail acceptance.

- Question: Which user-visible changes must be demonstrable at iteration end?
- Chosen Answer / Value: Existence and content quality of `proposals.md` — reviewable by the user.
- Rationale: The entire output is a human-readable document.
- Evidence / Reference: `request.md` § Goal.
- Impact if changed: N/A.

- Question: Non-functional targets applicable to this iteration?
- Chosen Answer / Value: None beyond completeness (30 proposals, diverse categories, self-contained descriptions).
- Rationale: Pure documentation authoring; no latency, throughput, or availability targets apply.
- Evidence / Reference: `request.md` § Constraints (none specified).
- Impact if changed: N/A.

**B, C, D, E, F — (Q4–Q17)**

- Questions: Q4–Q17 (Data & Contracts, Compute, Interfaces, Security, Observability)
- Chosen Answer / Value: N/A for all.
- Rationale: This iteration produces a single Markdown document. No data ingestion, APIs, compute, secrets, metrics, alerts, or runbooks are involved.
- Evidence / Reference: `request.md` § Scope; `01-analysis.md` § 6.1 (only `proposals.md` is affected).
- Impact if changed: N/A.

**G. Documentation & Governance**

- Question: Which product docs must be created or updated?
- Chosen Answer / Value: None. No product-doc files require updates. `proposals.md` is request-scoped only.
- Rationale: `01-analysis.md` § 10 — Affected Documentation table explicitly states no documents affected.
- Evidence / Reference: `01-analysis.md` § 10.
- Impact if changed: If a proposal were to require a doc update, a new request would be opened.

- Question: What acceptance evidence will be recorded and where?
- Chosen Answer / Value: After `proposals.md` is created, a brief entry will be appended to `implementation.md` recording the outcome.
- Rationale: `implementation.md` is the append-only execution log per AIB lifecycle rules (`Concepts.md` §  lifecycle).
- Evidence / Reference: `Concepts.md`; `aib-implement.md` logging requirements.
- Impact if changed: N/A.

- Question: What is the rollback strategy if acceptance fails?
- Chosen Answer / Value: Delete `proposals.md` and regenerate. No other files are touched, so rollback is trivial.
- Rationale: Single-file output; no side effects.
- Evidence / Reference: `01-analysis.md` § 9 Option A.
- Impact if changed: N/A.

---

## Work Breakdown Structure (WBS)

### Task 1: Workspace Deep-Scan for Improvement Signals

**Intent:** Systematically scan all `.aib_brain/` assets, tools, and docs to identify concrete, non-duplicate improvement signals across all categories.

**Inputs:**
- `.aib_brain/Concepts.md`
- `.aib_brain/Product_Documentation.md`
- All 6 prompt files in `.aib_brain/prompts/`
- All 35 convention files in `.aib_brain/conventions/`
- All Python tool scripts in `.aib_brain/tools/` (common.py, initialize.py, create-request.py, close-request.py, create-iteration.py, close-iteration.py, menu.py, reverse-engineer.py, test_common.py)
- All 4 templates in `.aib_brain/templates/`
- `.aib_brain/README.md`, `docs/Development_and_Deployment_Specification.md`, `logs/`
- `01-analysis.md` § 7 Research Findings (pre-identified 15 signals)

**Outputs:**
- Internal evidence table of ≥ 30 distinct improvement signals (working set, not written to disk)

**Procedure:**
1. Use the 15 pre-identified findings from `01-analysis.md` § 7 as the base set.
2. Extend by scanning remaining assets for additional signals covering: prompt determinism gaps, convention completeness, tooling robustness, usage documentation, testing, pitfall patterns.
3. Organize signals by category: Prompt / Convention / Tool / Organization / Concept / Best Practice / Pitfall.
4. For each signal: capture area, specific file/location, problem statement, and concrete change description.
5. Verify each signal is distinct and not already addressed in `logs/version_v1.0.10_log.md`.

**Done Criteria:**
- At least 30 distinct improvement signals identified, each with area, file, problem, and change description.
- All signals verified as not already resolved in v1.0.10.

**Dependencies:** None.

**Risk Notes:** Some signals identified in analysis may overlap — deduplicate before writing.

---

### Task 2: Author `proposals.md`

**Intent:** Write the complete `proposals.md` file with exactly 30 numbered, categorized, self-contained improvement proposals.

**Inputs:**
- Improvement signals from Task 1
- `request.md` § Constraints ("formulated in a way understandable for AI to implement without further clarifications")
- `01-analysis.md` § 8 (Rewrite Proposal) for acceptance criteria

**Outputs:**
- `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md` (new file, full content)

**Procedure:**
1. Group signals into categories: Prompt, Convention, Tool, Organization/Concept, Best Practice, Pitfall.
2. For each of the 30 proposals, write a structured entry containing:
   - Proposal number (1–30)
   - Category label
   - Area/file
   - Problem description (1–3 sentences)
   - Concrete change description (actionable; target file, what to add/change/remove, acceptance signal)
3. Order proposals by category grouping for readability.
4. Verify: exactly 30 proposals, at least 4 distinct categories covered, each entry self-contained.
5. Write the file to the target path.

**Done Criteria:**
- File `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md` exists.
- File contains exactly 30 numbered proposals.
- At least 4 distinct category labels present.
- Each proposal contains area, problem description, and concrete change description.
- No proposal duplicates an improvement already shipped in v1.0.10.

**Dependencies:** Task 1 complete.

**Risk Notes:** Proposals touching `.aib_brain/` changes are advisory — clearly mark them as such.

---

### Task 3: Append Implementation Log Entry

**Intent:** Record the completion of this iteration's work in the append-only `implementation.md`.

**Inputs:**
- `proposals.md` (Task 2 output) — confirmation of existence and content
- `iterations.md` — iteration ID `01`

**Outputs:**
- `.aib_memory/requests/R-20260402-1858-issue-31/implementation.md` (append entry)

**Procedure:**
1. Append a new dated entry to `implementation.md`.
2. Entry must include: iteration ID (`01`), date, implemented changes (created `proposals.md`), tests run/results (N/A — no code), outcome (Proposals.md written with 30 proposals), follow-ups (user to review and open new requests for selected proposals).

**Done Criteria:**
- `implementation.md` contains a new entry dated `2026-04-02` for iteration `01`.
- Entry includes all required fields.

**Dependencies:** Task 2 complete.

**Risk Notes:** None.

---

## Dependencies & Interfaces

**Internal task dependencies:**

- From Task: 1 | To Task: 2 | Dependency Type: FS | Critical: Y | Notes: Proposals cannot be written without the full signal set
- From Task: 2 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: Implementation log must confirm final artifact exists

**External interfaces:**

- Interface: Workspace filesystem | Direction: In | Protocol/Contract: File read/write | Version: N/A | Notes: All access via standard file tools; no network calls

---

## Environment & Configuration

**Environments:** Local development workspace only. No Dev/Test/Stage/Prod environments involved.

**Config Keys:** None. No runtime configuration is required for this iteration.

**Secrets Handling:** Not applicable. No secrets, credentials, or sensitive data are involved.

---

## Testing Strategy (This Iteration)

**Test Types:** Manual review only.

**Coverage Targets:** 30 proposals; ≥4 distinct categories.

**Data/Fixtures:** N/A.

**Test Execution:** Manual inspection of `proposals.md`:
- Count proposals: must equal 30.
- Check category labels: must span ≥4 distinct categories.
- Spot-check 3 proposals for self-containedness (problem + concrete change + target file/location).
- Cross-check against `logs/version_v1.0.10_log.md` to confirm no duplicates.

**Acceptance Evidence:** `proposals.md` file content is the sole artifact. Implementation log entry in `implementation.md` records the outcome.

---

## Observability & Quality Gates

**Key Metrics/Logs/Alerts:**

- Presence of `proposals.md` at correct path — binary check.
- Line count of `proposals.md` ≥ 90 lines (30 proposals × ~3 lines minimum each).

**Quality Gates:**

- GATE 1: `proposals.md` exists at `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md` — PASS required before closing iteration.
- GATE 2: File contains exactly 30 numbered proposals — PASS required.
- GATE 3: At least 4 distinct category labels present — PASS required.
- GATE 4: No proposal text describes a change already merged in v1.0.10 — PASS required.

---

## Documentation Touchpoints

- Doc Path: `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md`
  - Change Type: create
  - Update Trigger: Task 2
  - Edit Allowed: Y (request-scoped file, not in references.md product-doc set)
  - Notes: Primary output artifact.

- Doc Path: `.aib_memory/requests/R-20260402-1858-issue-31/implementation.md`
  - Change Type: update (append)
  - Update Trigger: Task 3
  - Edit Allowed: Y
  - Notes: Append-only log per AIB lifecycle rules.

No product-doc files from `references.md` are impacted by this iteration.

---

## Milestones

- Milestone: M1 | Description: Workspace scan complete, ≥30 signals catalogued | Due: Same session | Depends On: Task 1 | Exit Criteria: Signal list is exhaustive across all categories

- Milestone: M2 | Description: proposals.md authored and quality-gated | Due: Same session | Depends On: Task 2 | Exit Criteria: All 4 Quality Gates pass

- Milestone: M3 | Description: Implementation log updated | Due: Same session | Depends On: Task 3 | Exit Criteria: implementation.md contains dated entry for iteration 01

---

## Risks & Mitigations

- Risk R1: Fewer than 30 distinct, non-overlapping improvement signals exist
  - Probability: Low
  - Impact: High (breaks acceptance criteria)
  - Mitigation: The analysis already identified 15 signals from partial review; full scan expected to yield ≥30 easily given the breadth of coverage areas.

- Risk R2: Proposals overlap with changes already made in v1.0.10
  - Probability: Medium
  - Impact: Medium (wastes proposal slots on resolved items)
  - Mitigation: Cross-check every proposal against `logs/version_v1.0.10_log.md` before finalizing.

- Risk R3: Some proposals are too vague for AI implementation
  - Probability: Low
  - Impact: Medium (reduces value of output)
  - Mitigation: Each proposal must include target file path + specific change + acceptance signal before being written.

---

## Acceptance & Handover

**Iteration Acceptance Criteria:**

- GATE 1 passes: `proposals.md` exists at correct path.
- GATE 2 passes: Exactly 30 numbered proposals.
- GATE 3 passes: ≥4 distinct categories covered.
- GATE 4 passes: No duplicates of v1.0.10 changes.
- Task 3 complete: `implementation.md` updated.

**Handover Artifacts:**

- `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md` — primary deliverable for user review
- `.aib_memory/requests/R-20260402-1858-issue-31/implementation.md` — execution record

**Post-Iteration Follow-ups:**

- User reviews `proposals.md` and selects proposals to action.
- For each selected proposal, user opens a new AIB request via `create-request`.
- This iteration may then be closed via `close-iteration`, followed by `close-request`.

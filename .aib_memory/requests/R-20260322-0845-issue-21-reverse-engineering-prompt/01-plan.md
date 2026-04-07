## Overview
This iteration will produce a first working draft of a new AIB capability named `reverse-engineer` that can scan a workspace, read `.aib_memory/references.md`, and populate all editable `product-doc` files under `.aib_memory/docs/` using convention-compliant, evidence-backed content.

The plan implements the decisions captured in `01-questionnaire.md` (QID-BF-001, QID-BF-002, QID-AT-001..004) and aligns to the scope and success criteria in `request.md` (Goal, Scope, Constraints, Success criteria). It also uses the existing AIB documentation enforcement pattern already present in `aib-update-documentation.md`.

## Scope of Work
**In Scope**
- Add a new formal AIB action named `reverse-engineer` (registration in `.aib_brain/Concepts.md`).
- Author new prompt `.aib_brain/prompts/aib-reverse-engineer.md` that:
  - Enumerates workspace files recursively (none missed).
  - Reads all docs referenced by `.aib_memory/references.md`.
  - Enforces per-product-doc conventions via `.aib_brain/conventions/product-documentation-convention.md` and `.aib_brain/conventions/<requirement-id-lower>-convention.md`.
  - Populates only `product-doc` files where `edit_allowed=Y`.
- Optional: add a helper tool script `.aib_brain/tools/reverse-engineer.py` for deterministic file inventory generation for large workspaces.
- Validate on the current workspace (AI_Builder) as an initial pilot and capture evidence in `implementation.md`.

**Out of Scope**
- Changing `.aib_memory/references.md` schema or its existing entries.
- Supporting binary file *content* extraction; only path/metadata will be used.
- Guaranteeing perfect correctness; output is best-effort draft requiring human review.
- Testing against external brownfield workspaces beyond this repo in this iteration.

**Assumptions**
- AIB is initialized in the target workspace (presence of `.aib_memory/` and `.aib_brain/`).
- The execution environment provides file read and write capabilities for `.aib_memory/`.
- Python 3.10+ is available if the optional helper script is implemented.

**Constraints**
- Must respect `edit_allowed` (never write to `N`).
- Must remain model/vendor agnostic (works in VS Code Copilot, Claude Code, Cursor, CLI).
- Must manage context-window limits via chunking, prioritization, and/or intermediate artifacts.
- `.aib_brain/` must not be modified by AIB automation; only human-authored changes in this request are allowed.

## Decision Gates (Blocking Questions & Answers)
- Q1: What is the minimal shippable outcome for this iteration (MSI) and what is explicitly excluded? | Chosen Answer / Value: MSI = new action registration + new prompt able to populate all editable product-docs in the *current workspace* with traceability; optional helper tool script if needed for completeness. Excluded = external workspace validation; perfect accuracy. | Rationale: Matches `request.md` success criteria while keeping validation bounded to one workspace. | Evidence / Reference: `request.md` (Scope, Out of scope, Success criteria); `01-questionnaire.md` QID-BF-004. | Impact if changed: Expands time/effort; requires additional test workspaces and broader acceptance evidence.
- Q2: Which user-visible changes (if any) MUST be demonstrable at iteration end? | Chosen Answer / Value: New `reverse-engineer` action documented in `.aib_brain/Concepts.md` and runnable prompt `.aib_brain/prompts/aib-reverse-engineer.md`; updated `.aib_memory/docs/**` product-docs populated with evidence references. | Rationale: Demonstrates end-to-end value for brownfield bootstrap. | Evidence / Reference: `request.md` (Goal, Success criteria). | Impact if changed: If reduced to “design only”, docs won’t be populated and success criteria won’t be met.
- Q3: What are the non-functional targets applicable to this iteration (latency, throughput, availability, data freshness, cost ceiling)? | Chosen Answer / Value: Robustness to large workspaces by design: (a) deterministic complete inventory; (b) bounded per-step token budget; (c) no single-step requires reading the whole workspace into context. | Rationale: Directly addresses context-window constraint. | Evidence / Reference: `request.md` (Constraints); `01-analysis.md` (Headline risks). | Impact if changed: Naive single-pass prompt will fail or hallucinate on real brownfield repos.

- Q4: What input data sources and schemas are authoritative (include versions) and what happens if a field is missing/extra? | Chosen Answer / Value: Authoritative sources: workspace filesystem; `.aib_memory/references.md` as registry; existing product-doc files as current state; per-doc convention files as normative schema. Missing/extra fields in `references.md` rows are treated as validation errors (fail-closed for editing). | Rationale: Prevents editing wrong targets and keeps determinism. | Evidence / Reference: `.aib_brain/Concepts.md` (references schema); `aib-update-documentation.md` (fail-closed enforcement). | Impact if changed: Increased risk of writing to incorrect files or violating conventions.
- Q5: What serialization formats, partitioning, and retention policies apply to new/changed datasets? | Chosen Answer / Value: Outputs are Markdown product-docs only; no new datasets are introduced. Partitioning/retention N/A. | Rationale: This iteration produces documentation artifacts, not data assets. | Evidence / Reference: `request.md` (Scope). | Impact if changed: Would require defining data storage, retention, and compliance rules.
- Q6: What are the error handling rules for ingestion/processing (retry policy, dead-letter, alerts, human-in-the-loop)? | Chosen Answer / Value: On unreadable files: record path + reason; continue. On convention enforcement failure: STOP and do not write any product-docs (fail-closed). | Rationale: Best-effort scan while keeping doc writes safe and consistent. | Evidence / Reference: `aib-update-documentation.md` (fail-closed convention preflight); `01-analysis.md` (risk: destructive overwrites). | Impact if changed: Continuing after convention failures can lead to invalid docs or partial, inconsistent output.

- Q7: Which algorithm/specification variant is in scope (if multiple exist), including parameters and defaults? | Chosen Answer / Value: Iterative document-by-document generation (primary) with optional tool-assisted inventory for completeness; defaults: skip reading binary content; exclude noisy directories for *content reads* but not for inventory enumeration. | Rationale: Matches selected approach while addressing “no file missed”. | Evidence / Reference: `01-questionnaire.md` QID-AT-001, QID-AT-002, QID-AT-004. | Impact if changed: Tool-only or monolithic approaches alter artifact set and validation methods.
- Q8: What accuracy/quality thresholds or benchmarks must be met (and the measurement method)? | Chosen Answer / Value: Each updated product-doc must (a) conform to its convention; (b) include traceability (source file paths) for key claims; (c) avoid fabricating unknowns—use “Unknown / Not found in workspace” where evidence is absent. | Rationale: Prevents hallucinated documentation and improves reviewability. | Evidence / Reference: `request.md` (traceability success criterion); `01-analysis.md` (risk: hallucination). | Impact if changed: Lower quality threshold increases reviewer burden and downstream errors.
- Q9: Are there hardware/compute constraints (local vs. remote execution, concurrency caps, cost limits)? | Chosen Answer / Value: Local filesystem access required; no external services required; keep operations sequential to remain compatible with varied agent environments. | Rationale: Preserves model/vendor neutrality and reduces complexity. | Evidence / Reference: `request.md` (model/vendor agnostic). | Impact if changed: Parallelism may be tool-specific and reduce portability.

- Q10: Which API endpoints, message topics, or files are produced/consumed (names, versions, SLAs)? | Chosen Answer / Value: Consumes: all workspace files (read), `.aib_memory/references.md`, `.aib_brain/conventions/**`. Produces: updated `.aib_memory/docs/**` product-docs; optional inventory artifact (if tool implemented). | Rationale: Filesystem-only interface is portable. | Evidence / Reference: `request.md` (Scope); `aib-update-documentation.md` (references-driven approach). | Impact if changed: Adding external APIs reduces portability and introduces auth/SLAs.
- Q11: What compatibility must be preserved (backward/forward) and what is the deprecation plan if breaking changes are needed? | Chosen Answer / Value: Backward compatible with existing AIB folder layout and references schema; no breaking changes. If future changes needed, introduce new prompt/tool version and keep old action behavior stable. | Rationale: Avoids disrupting existing AIB installs. | Evidence / Reference: `.aib_brain/Concepts.md` (action contract). | Impact if changed: Would require migration guidance and could break existing automation.

- Q12: What identities/roles may access the new/changed assets (least privilege)? | Chosen Answer / Value: The agent must have read access to workspace and write access only to `.aib_memory/docs/**` targets with `edit_allowed=Y` (and optionally request artifacts like `implementation.md`). | Rationale: Least privilege reduces risk of unintended changes. | Evidence / Reference: `request.md` (edit_allowed constraint); `.aib_brain/Concepts.md` (safety rules). | Impact if changed: Broader write scope increases blast radius.
- Q13: What data classifications are involved, and what masking/anonymization is required? | Chosen Answer / Value: Treat workspace content as potentially sensitive; do not echo full secrets/keys; if secrets-like patterns are detected, record only file path + key name placeholder. | Rationale: Brownfield repos often contain sensitive config. | Evidence / Reference: `request.md` (model/vendor agnostic implies unknown handling); `SEC-03` intent area. | Impact if changed: Risk of leaking sensitive data into documentation or logs.
- Q14: How are secrets injected at runtime, and what rotation policy is assumed? | Chosen Answer / Value: N/A for this iteration’s artifacts; reverse-engineer must not embed secret values in docs. Where secrets handling is inferred, document mechanism only (e.g., env vars/secret store) without values. | Rationale: Documentation must remain safe. | Evidence / Reference: Plan convention (no secrets); `01-questionnaire.md` QID-AT-002. | Impact if changed: Embedding secrets is a critical policy violation.

- Q15: Which metrics/logs/traces prove the change is healthy (names and thresholds)? | Chosen Answer / Value: “Health” = completeness and safety checks: (a) inventory includes all files; (b) no writes outside allowed set; (c) every updated product-doc contains sources. Thresholds are binary pass/fail. | Rationale: This is a documentation pipeline, not a runtime service. | Evidence / Reference: `request.md` (Success criteria). | Impact if changed: Would require introducing operational telemetry artifacts.
- Q16: What alerts must be configured or updated and who responds? | Chosen Answer / Value: N/A (no running service). Failures are reported in the agent output and recorded in `implementation.md`. | Rationale: Keep scope minimal. | Evidence / Reference: `request.md` (scope). | Impact if changed: Would require an observability stack definition.
- Q17: What runbook/SOP updates are required, if any? | Chosen Answer / Value: Update `.aib_brain/Concepts.md` action list/contract and ensure prompt usage instructions exist in the new prompt itself. | Rationale: Makes the capability discoverable and usable. | Evidence / Reference: `01-questionnaire.md` QID-BF-001. | Impact if changed: Users won’t discover or correctly invoke the action.

- Q18: Which product docs must be created or updated (paths), and is editing permitted (per references)? | Chosen Answer / Value: Update all `product-doc` paths with `edit_allowed=Y` in `.aib_memory/references.md` (27 by default). | Rationale: This is the core deliverable. | Evidence / Reference: `request.md` (Goal); `.aib_memory/references.md`. | Impact if changed: Partial updates reduce time-to-value and leave gaps.
- Q19: What acceptance evidence will be recorded and where? | Chosen Answer / Value: Evidence recorded in `implementation.md` entry for this iteration: list of files updated, verification commands run, and any known gaps/unknowns. | Rationale: Provides traceability and auditability. | Evidence / Reference: `.aib_memory/requests/.../implementation.md` template; `aib-update-documentation.md` rule to summarize in implementation. | Impact if changed: Harder to verify outcomes and regressions.
- Q20: What is the rollback strategy if acceptance fails? | Chosen Answer / Value: Use version control rollback (`git checkout -- .` or revert commit) or restore from backups created before writing; prompt should instruct to run in a clean branch for safety. | Rationale: Fully automated updates can touch many files. | Evidence / Reference: `01-questionnaire.md` QID-BF-002 (fully automated). | Impact if changed: Recovery becomes manual and risky.

## Work Breakdown Structure (WBS)
### Task 1: Confirm baseline behavior and reuse patterns
**Intent:** Establish a deterministic baseline by reusing proven AIB documentation enforcement patterns.
**Inputs:**
- `.aib_brain/prompts/aib-update-documentation.md`
- `.aib_brain/Concepts.md`
- `.aib_memory/references.md`
- `request.md`, `01-analysis.md`, `01-questionnaire.md`
**Outputs:**
- Updated `01-analysis.md` section “Reverse-engineer design constraints & invariants” (append-only addition)
**Procedure:**
1. Extract the enforcement steps from `aib-update-documentation.md` (required-read set, target-edit set, fail-closed convention preflight).
2. Translate those steps into reverse-engineer invariants (what MUST happen before any write).
3. Append a short invariants section to `01-analysis.md`.
**Done Criteria:**
- `01-analysis.md` contains an explicit invariant list covering: references read, conventions read, edit_allowed enforcement, fail-closed behavior.
**Dependencies:** None
**Risk Notes:** Minimal.

### Task 2: Register the new action in the AIB action contract
**Intent:** Make `reverse-engineer` discoverable and part of the canonical AIB workflow.
**Inputs:**
- `.aib_brain/Concepts.md`
- `01-questionnaire.md` QID-BF-001
**Outputs:**
- `.aib_brain/Concepts.md` updated supported actions list and action contract matrix row for `reverse-engineer`
**Procedure:**
1. Add `reverse-engineer` to the Supported actions list.
2. Extend the action contract matrix with required context and outputs (prompt-backed; optional tool).
3. Ensure wording preserves model/vendor agnosticism.
**Done Criteria:**
- `reverse-engineer` appears in both the Supported actions list and action contract matrix with deterministic expectations.
**Dependencies:** Task 1
**Risk Notes:** Medium—needs to stay aligned with existing determinism rules.

### Task 3: Author the prompt `.aib_brain/prompts/aib-reverse-engineer.md`
**Intent:** Provide a model/vendor-agnostic, repeatable procedure to generate product documentation from a brownfield workspace.
**Inputs:**
- `request.md` (Goal, Constraints, Success criteria)
- `01-questionnaire.md` (selected options)
- `.aib_brain/prompts/aib-update-documentation.md` (enforcement pattern)
- `.aib_brain/conventions/product-documentation-convention.md`
- `.aib_memory/references.md`
**Outputs:**
- `.aib_brain/prompts/aib-reverse-engineer.md`
**Procedure:**
1. Define mandatory preflight: resolve active request/iteration; read references; build required-read and target-edit sets.
2. Add convention enforcement preflight (fail-closed) mirroring `aib-update-documentation.md`.
3. Add workspace scanning steps:
   - Create a complete file inventory (paths) and classify as text vs binary.
   - Apply an exclusion list for *content reads* (per QID-AT-004) but never for inventory enumeration.
4. For each product-doc in target-edit set (iterative doc-by-doc):
   - Read its convention.
   - Select relevant evidence files from inventory.
   - Extract facts and write/update the doc with explicit sources.
5. Add safety rules: never write outside allowed set; never embed secrets; mark unknowns explicitly.
**Done Criteria:**
- The prompt contains explicit steps covering every success criterion in `request.md`.
- The prompt includes deterministic fail-closed rules for missing convention mappings.
**Dependencies:** Task 2
**Risk Notes:** High—must balance completeness vs token budget.

### Task 4: Implement optional helper tool for deterministic inventory (recommended for large workspaces)
**Intent:** Guarantee “no file missed” inventory generation without consuming LLM context.
**Inputs:**
- `01-questionnaire.md` QID-AT-004 (exclusions)
- Workspace root path
**Outputs:**
- `.aib_brain/tools/reverse-engineer.py`
- (Runtime artifact when executed) `.aib_memory/reverse-engineer/workspace-inventory.jsonl`
**Procedure:**
1. Implement recursive enumeration via `os.walk()` including hidden files.
2. Record each file path + size + modified time + extension + binary/text heuristic.
3. Apply exclusion list only to expensive metadata reads if needed; inventory MUST still record all paths.
4. Write output as JSONL to keep memory bounded.
**Done Criteria:**
- Running the script produces an inventory file that includes `.aib_memory/references.md` itself and representative repo files (excluding `.git` contents if policy requires).
- Script exits non-zero with a clear error if output path cannot be written.
**Dependencies:** Task 3
**Risk Notes:** Medium—symlinks/permission issues on some workspaces.

### Task 5: Define and implement safe merge/write rules for product-doc updates
**Intent:** Prevent destructive overwrites while still producing convention-compliant documents.
**Inputs:**
- `01-questionnaire.md` QID-AT-003 (merge)
- Each product-doc convention file (`.aib_brain/conventions/<id>-convention.md`)
- Current product-doc content
**Outputs:**
- Reverse-engineer prompt section “Write policy” specifying placeholder detection and merge behavior
**Procedure:**
1. Define placeholder detection (seed text `_This file is seeded by AIB initialize..._`).
2. If placeholder: replace with full convention-compliant content.
3. If non-placeholder: merge by filling missing required sections; preserve existing user text when not conflicting.
4. Always include a “Sources/Evidence” subsection per convention (or per-doc equivalent) for traceability.
**Done Criteria:**
- The write policy is explicit, deterministic, and consistent across all docs.
- The policy guarantees that output still conforms to the per-doc convention.
**Dependencies:** Task 3
**Risk Notes:** High—merge semantics can conflict with strict conventions.

### Task 6: Execute reverse-engineer against the current workspace (pilot)
**Intent:** Produce tangible documentation output and verify end-to-end behavior.
**Inputs:**
- `.aib_brain/prompts/aib-reverse-engineer.md`
- `.aib_memory/references.md`
- Workspace files
**Outputs:**
- Updated `.aib_memory/docs/**` product-doc files (only those with `edit_allowed=Y`)
- New `implementation.md` entry for Iteration `01` describing results and verification
**Procedure:**
1. Ensure working tree is clean (or work on a branch) for rollback.
2. Run the `reverse-engineer` prompt.
3. Confirm no files outside the allowed set changed.
4. Record the run summary and known gaps in `implementation.md`.
**Done Criteria:**
- All 27 default product-doc files show non-placeholder content.
- Each updated doc includes traceability to at least one workspace file when evidence exists.
- `implementation.md` includes verification steps and results.
**Dependencies:** Task 3 (and Task 4 if tool is required)
**Risk Notes:** High—may produce large diffs and require multiple prompt passes.

### Task 7: Verification pass and quality gates
**Intent:** Ensure outputs are safe, complete, and convention-compliant.
**Inputs:**
- Updated `.aib_memory/docs/**`
- `.aib_memory/references.md`
- Per-doc conventions
**Outputs:**
- Additional `implementation.md` notes: quality gate pass/fail and exceptions list
**Procedure:**
1. Verify every path in target-edit set was updated and no `edit_allowed=N` path was touched.
2. Spot-check 3 representative documents (ARCH, DATA, SEC) for convention compliance.
3. Validate that secrets are not embedded (only mechanisms described).
4. Record any exceptions and follow-ups.
**Done Criteria:**
- Pass/fail result recorded with objective checks.
- Any non-compliant docs are listed for follow-up iteration.
**Dependencies:** Task 6
**Risk Notes:** Medium.

## Dependencies & Interfaces
- From Task: 1 | To Task: 2 | Dependency Type: FS | Critical: Y | Notes: Action contract should follow established invariants.
- From Task: 2 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: Prompt should match registered action semantics.
- From Task: 3 | To Task: 6 | Dependency Type: FS | Critical: Y | Notes: Cannot execute without the prompt.
- From Task: 4 | To Task: 6 | Dependency Type: FS | Critical: N | Notes: Only required if inventory cannot be reliably produced via the agent environment.
- From Task: 6 | To Task: 7 | Dependency Type: FS | Critical: Y | Notes: Verification depends on produced docs.

- Interface: Local filesystem | Direction: In | Protocol/Contract: OS file read APIs | Version: N/A | Notes: Must enumerate recursively, handle permissions/encoding errors.
- Interface: AIB references registry | Direction: In | Protocol/Contract: `.aib_memory/references.md` schema | Version: As in `.aib_brain/Concepts.md` | Notes: Authoritative for what is readable/editable.
- Interface: AIB conventions | Direction: In | Protocol/Contract: Markdown conventions under `.aib_brain/conventions/` | Version: Repo version | Notes: Fail-closed if any required convention missing.

## Environment & Configuration
- Key: REVERSE_ENGINEER_EXCLUDE_DIRS | Scope: Global | Default: `.git,node_modules,__pycache__,dist,build,.aib_brain,.aib_memory` | Allowed Range/Values: comma-separated directory names | Source: `.aib_brain/prompts/aib-reverse-engineer.md` (and `.aib_brain/tools/reverse-engineer.py` if used) | Change Control: PR to update defaults.
- Key: REVERSE_ENGINEER_MAX_TEXT_FILE_BYTES | Scope: Global | Default: 262144 | Allowed Range/Values: 1024–1048576 | Source: `.aib_brain/tools/reverse-engineer.py` | Change Control: PR.
- Key: REVERSE_ENGINEER_MAX_FILES_PER_DOC | Scope: Global | Default: 25 | Allowed Range/Values: 5–200 | Source: `.aib_brain/prompts/aib-reverse-engineer.md` | Change Control: PR.

**Secrets Handling:** Do not store or print secret values. If secret mechanisms are inferred, document only the mechanism (env var names, secret store references) without values.

## Testing Strategy (This Iteration)
- Test Types: Manual functional (prompt execution), Safety checks (edit_allowed enforcement), Convention compliance spot-check.
- Data/Fixtures: Current workspace (AI_Builder) per `01-questionnaire.md` QID-BF-004.
- Test Execution: Run the `reverse-engineer` prompt; if tool exists, run `python .aib_brain/tools/reverse-engineer.py` to generate inventory.
- Acceptance Evidence: `implementation.md` entry containing list of updated docs, verification checks, and any exceptions.

## Observability & Quality Gates
- Key Metrics/Logs/Alerts:
  - Metric: `docs_updated_count` | Threshold: equals number of `product-doc` rows with `edit_allowed=Y`.
  - Metric: `forbidden_writes_count` | Threshold: 0.
  - Log: `unreadable_files` list | Threshold: Recorded and non-blocking unless it prevents convention enforcement.
- Quality Gates:
  - All writes restricted to `product-doc` targets where `edit_allowed=Y`.
  - Convention enforcement preflight passes for all required product-docs.
  - No secrets embedded in generated docs.
  - Traceability present (source file paths) for non-trivial assertions.

## Documentation Touchpoints
- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Populate from repo structure + README/config.
- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-02.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Infer topology from CI/deploy configs if present.
- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-03.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Likely partial/unknown; mark unknowns explicitly.
- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-04.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: ADR location may be inferred (or marked not found).
- Doc Path: .aib_memory/docs/04 Technology/Architecture/ARCH-06.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Capture interaction sequences from code entrypoints.
- Doc Path: .aib_memory/docs/04 Technology/Inventory/ARCH-07.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Include binary path/metadata per QID-AT-002.
- Doc Path: .aib_memory/docs/04 Technology/Compute/CMP-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Scan `scripts/` and automation.
- Doc Path: .aib_memory/docs/04 Technology/Compute/CMP-02.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Identify core algorithms (if any).
- Doc Path: .aib_memory/docs/04 Technology/Data Sources/DATA-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Likely “unknown” unless external connectors exist.
- Doc Path: .aib_memory/docs/04 Technology/Data Models/DATA-02.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Infer from code models/schemas.
- Doc Path: .aib_memory/docs/04 Technology/Data Workspace/DATA-03.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Lineage may be partial; cite evidence.
- Doc Path: .aib_memory/docs/04 Technology/Data Workspace/DATA-04.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Storage patterns inferred from code/config.
- Doc Path: .aib_memory/docs/04 Technology/Data Workspace/DATA-05.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Access patterns from code.
- Doc Path: .aib_memory/docs/04 Technology/Analytics/DATA-06.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Metrics may be limited.
- Doc Path: .aib_memory/docs/04 Technology/Data Workspace/DATA-07.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: DQ rules from code/tests if any.
- Doc Path: .aib_memory/docs/04 Technology/Data Workspace/DATA-08.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Prefer “unknown” unless policy docs exist.
- Doc Path: .aib_memory/docs/04 Technology/Analytics/DATA-09.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Dashboard inventory likely none; mark unknown.
- Doc Path: .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Extract terms from names/docs.
- Doc Path: .aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Likely partial; avoid speculation.
- Doc Path: .aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Infer from README/issues if present.
- Doc Path: .aib_memory/docs/04 Technology/Observability/OBS-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Detect logging frameworks/config.
- Doc Path: .aib_memory/docs/01 Product Management/Product Charter/RQT-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Likely minimal; mark unknown.
- Doc Path: .aib_memory/docs/03 Requirements/RQT-02.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: If no requirements exist, state so.
- Doc Path: .aib_memory/docs/04 Technology/Access and Security/SEC-01.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Access patterns inferred from auth config.
- Doc Path: .aib_memory/docs/04 Technology/Access and Security/SEC-02.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Data protection mechanisms inferred.
- Doc Path: .aib_memory/docs/04 Technology/Access and Security/SEC-03.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Secrets handling described without values.
- Doc Path: .aib_memory/docs/04 Technology/Access and Security/SEC-04.md | Change Type: update | Update Trigger: Task 6 | Edit Allowed: Y | Notes: Network security inferred if configs exist.

## Milestones
- Milestone: M1 | Description: Action registration + prompt authored | Due: Trigger = completion of Task 3 | Depends On: Task 2, Task 3 | Exit Criteria: Prompt exists and is aligned with action contract.
- Milestone: M2 | Description: Deterministic inventory tool available (optional) | Due: Trigger = completion of Task 4 | Depends On: Task 4 | Exit Criteria: Inventory JSONL can be generated on this workspace.
- Milestone: M3 | Description: Pilot run produces populated docs | Due: Trigger = completion of Task 6 | Depends On: Task 6 | Exit Criteria: 27 product-docs updated + implementation evidence recorded.

## Risks & Mitigations
- Risk: Context window overflow on large workspaces | Probability: High | Impact: High | Mitigation: Use deterministic inventory + per-doc bounded reads; cap file sizes; chunk evidence.
- Risk: Hallucinated content where evidence is thin | Probability: Medium | Impact: High | Mitigation: Require explicit sources; mark unknowns; avoid guessing.
- Risk: Destructive merges that violate conventions | Probability: Medium | Impact: High | Mitigation: Placeholder detection; strict convention compliance; prefer replace for placeholders.
- Risk: Writing outside allowed paths | Probability: Low | Impact: Critical | Mitigation: Compute target-edit set from references and hard-enforce; verification gate.

## Acceptance & Handover
- Iteration Acceptance Criteria:
  - `reverse-engineer` is registered in `.aib_brain/Concepts.md`.
  - `.aib_brain/prompts/aib-reverse-engineer.md` exists and includes mandatory preflight + fail-closed convention enforcement.
  - Pilot run updates only `edit_allowed=Y` product-docs and produces traceability.
  - `implementation.md` contains a dated Iteration `01` entry with verification steps and results.
- Handover Artifacts:
  - `.aib_brain/Concepts.md` (updated)
  - `.aib_brain/prompts/aib-reverse-engineer.md`
  - `.aib_brain/tools/reverse-engineer.py` (if implemented)
  - Updated `.aib_memory/docs/**`
  - `.aib_memory/requests/.../implementation.md` entry
- Post-Iteration Follow-ups:
  - Validate against a second, non-AIB workspace (true brownfield) and refine heuristics.
  - If merge semantics prove unreliable, switch to “draft files” workflow in a subsequent iteration.

## Overview

This plan governs iteration 01 of request R-20260404-1826 (improve-aib-context-md). The iteration delivers two artifacts:

1. A new convention file `.aib_brain/conventions/context-convention.md` that defines a universal, product-agnostic section structure and content standard for `.aib_memory/context.md`.
2. A revised prompt file `.aib_brain/prompts/aib-context.md` stripped of all embedded structural definitions, retaining only behavioral instructions and referencing the new convention for format.

The goal is to decouple structure from behavior so that `context.md` becomes a rebuildable, best-in-class product knowledge document usable for any repository — not locked to AIB's 11-domain taxonomy.

Linkage: request.md §Goal, §Scope, §Constraints, §Success criteria; 01-analysis.md §Scope Interpretation, §Assumptions, §Impact Assessment, §Disambiguation Questionnaire, §Solution Options (Option B selected).

## Scope of Work

**In Scope**
- Create `.aib_brain/conventions/context-convention.md` with at least 12 mandatory universal sections, content guidance, formatting rules, and quality gates.
- Modify `.aib_brain/prompts/aib-context.md` to remove all structural definitions (domain section list, domain-to-product-doc mapping table, scope summary table, Case A/Case B rules) and add a reference to the new convention.
- Retain all behavioral logic in the prompt (Phase 1-5, safety rules, context-window management, done criteria, determinism).

**Out of Scope**
- Modifying `.aib_memory/context.md` directly (regenerated on next prompt execution).
- Changing any other convention files, prompt files, tool scripts, or templates.
- Modifying `.aib_memory/references.md` or `.aib_memory/docs/` structure.
- Adding product-doc convention files for new domains.
- Changing request/iteration lifecycle mechanics.

**Assumptions**
- A1: The convention is the single authoritative source for context.md structure; the prompt references it but does not duplicate structural rules (per 01-analysis.md §Assumptions A1).
- A2: The convention's mandatory sections are product-agnostic — no AIB-specific domain acronyms (RQT, ARCH, etc.) as required headings (per 01-analysis.md §Assumptions A2).
- A3: The prompt's synthesis phase dynamically maps product-doc content into universal sections; the 11-domain taxonomy is not embedded in either file (per 01-analysis.md §Assumptions A3, Disambiguation Q2).
- A4: Mandatory section headings are fixed strings for deterministic machine-parseability (per 01-analysis.md §Disambiguation Q1).
- A5: Workspace file inventory remains as the final section of context.md (per 01-analysis.md §Disambiguation Q3).

**Constraints**
- Convention MUST be Markdown-only (no HTML, no images, no external hyperlinks).
- Convention MUST use RFC 2119 / RFC 8174 normative language.
- Prompt MUST remain model-agnostic and vendor-agnostic (NFR-001 per RQT-02).
- Prompt MUST produce deterministic output (NFR-002 per RQT-02).
- Prompt MUST NOT modify any file other than `.aib_memory/context.md`.
- Prompt MUST NOT read `.aib_brain/` contents except the referenced convention file.
- Both files MUST reside in their canonical AIB locations.
- Convention MUST NOT describe process/behavior; prompt MUST NOT describe structure/format.

## Decision Gates (Blocking Questions & Answers)

1) **Question:** What is the minimal shippable outcome for this iteration?
   **Chosen Answer / Value:** Two files: a complete convention file and a revised prompt file. No other workspace changes.
   **Rationale:** The request defines exactly two deliverables. The convention must exist before the prompt can reference it.
   **Evidence / Reference:** request.md §Scope items 1 and 2; 01-analysis.md §Impact Assessment.
   **Impact if changed:** Partial delivery would leave the prompt referencing a non-existent convention, causing runtime failure.

2) **Question:** Which structural approach is selected for the convention?
   **Chosen Answer / Value:** Option B — Universal Redesign with fixed mandatory sections inspired by arc42, C4, SDD, ADR, and docs-as-code research.
   **Rationale:** Option B directly fulfills the product-agnostic requirement and all stated success criteria. The universal sections are comprehensive enough to subsume all current 11-domain content.
   **Evidence / Reference:** 01-analysis.md §Solution Options (Option B recommended); request.md §Success criteria item 6.
   **Impact if changed:** Option A fails the product-agnostic requirement; Option C adds unnecessary complexity.

3) **Question:** Should the convention mandate specific section headings or allow flexible naming?
   **Chosen Answer / Value:** Mandate specific headings.
   **Rationale:** Deterministic, machine-parseable structure requires fixed headings. Flexible naming introduces non-determinism.
   **Evidence / Reference:** 01-analysis.md §Disambiguation Q1; conventions in AIB use fixed mandatory headings.
   **Impact if changed:** AI agents would need fuzzy matching; reduces reliability.

4) **Question:** Should the convention retain the 11-domain taxonomy as an optional mapping?
   **Chosen Answer / Value:** No. The prompt handles domain-to-section mapping internally. The convention defines only universal sections.
   **Rationale:** Including AIB-specific taxonomy in the convention contradicts the product-agnostic goal.
   **Evidence / Reference:** 01-analysis.md §Disambiguation Q2; request.md §Constraints.
   **Impact if changed:** Convention loses product-agnostic property.

5) **Question:** Should context.md include a workspace file inventory?
   **Chosen Answer / Value:** Yes, as the final mandatory section.
   **Rationale:** Provides quick structural reference for both humans and AI agents.
   **Evidence / Reference:** 01-analysis.md §Disambiguation Q3; current context.md includes it.
   **Impact if changed:** AI agents lose workspace structure awareness.

6) **Question:** What depth for architecture decisions in context.md?
   **Chosen Answer / Value:** Summarize ADR content (decision, rationale, consequences) rather than full ADR documents. Reference ADR IDs for traceability.
   **Rationale:** context.md is a synthesis document, not a duplication target.
   **Evidence / Reference:** 01-analysis.md §Disambiguation Q4; arc42 guidance on decision documentation.
   **Impact if changed:** Over-detailed decisions section would bloat context.md and duplicate ADR files.

7) **Question:** Should the prompt read convention files other than context-convention.md during context generation?
   **Chosen Answer / Value:** No. The prompt reads only the context convention for format. Other conventions are framework internals.
   **Rationale:** Minimizes context window usage; other conventions contain no product knowledge.
   **Evidence / Reference:** 01-analysis.md §Disambiguation Q5; current prompt excludes .aib_brain/ exploration.
   **Impact if changed:** Unnecessary context window consumption.

8) **Question:** Which input data schemas are authoritative?
   **Chosen Answer / Value:** `.aib_memory/references.md` (product-doc paths and edit permissions) and the convention file (target section structure).
   **Rationale:** These are the two structural inputs the prompt needs.
   **Evidence / Reference:** request.md §Inputs; 01-analysis.md §Assumptions A1.
   **Impact if changed:** Prompt may read wrong inputs or miss required sources.

9) **Question:** Are there UI, API, or integration contract changes?
   **Chosen Answer / Value:** No UI or API changes. The only contract change is the output format of `.aib_memory/context.md`.
   **Rationale:** This is a documentation-format change within the AIB framework. No external contracts are affected.
   **Evidence / Reference:** request.md §Out of scope; 01-analysis.md §Impact Assessment.
   **Impact if changed:** N/A.

10) **Question:** Are there rollback or feature-flag needs?
    **Chosen Answer / Value:** No. Both files are version-controlled. Rollback is via git revert.
    **Rationale:** Standard VCS rollback is sufficient for two Markdown files.
    **Evidence / Reference:** DATA-08 §Overview (git history as retention/rollback mechanism).
    **Impact if changed:** N/A.

## Work Breakdown Structure (WBS)

### Task 1: Design the universal section structure for context-convention.md

**Intent:** Define the mandatory and optional section headings, ordering, and content guidance for the universal context convention.
**Inputs:** 01-analysis.md §Evidence Summary, §Disambiguation Questionnaire; request.md §Scope item 1; arc42/C4/SDD/ADR/docs-as-code research findings (summarized in analysis); existing `aib-context.md` Phase 4 structure (to ensure no knowledge loss).
**Outputs:** Working outline of sections (internal working document — not a separate file; used as input to Task 2).
**Procedure:**
1. List the knowledge areas identified in the analysis: product identity, business context, requirements, architecture and decisions, technical design, data architecture, security and compliance, operations, development practices, constraints and assumptions, glossary, workspace inventory.
2. Map each knowledge area to a mandatory section heading with deterministic naming.
3. Define content guidance for each section (what to include, what to omit, quality expectations).
4. Validate that every populated domain in the current context.md (ARCH, KNW, CMP, DATA, OBS, RQT, SEC) maps into at least one universal section.
5. Validate that no AIB-specific terminology appears in mandatory headings.
**Done Criteria:** Written outline exists; all 12+ knowledge areas have assigned section headings; mapping from current 11 domains to universal sections is verified.
**Dependencies:** None.
**Risk Notes:** None.

### Task 2: Author context-convention.md

**Intent:** Create the complete convention file at `.aib_brain/conventions/context-convention.md`.
**Inputs:** Task 1 output (section outline); plan-convention.md (as a style reference for AIB conventions); existing AIB conventions (analysis-convention.md, request-convention.md) as style/format references; request.md §Scope item 1.
**Outputs:** `.aib_brain/conventions/context-convention.md`
**Procedure:**
1. Create the file with a Purpose section stating it defines the structure and content standard for `.aib_memory/context.md`.
2. Add a Scope section delimiting what the convention governs (structure, content, formatting, quality) and what it does not (behavioral generation logic).
3. Define the mandatory sections in order, each with: heading text, heading level, content guidance (what MUST, SHOULD, MAY appear), quality expectations, and traceability requirements. Minimum 12 mandatory sections.
4. Define optional/extensible sections mechanism (MAY-level sections for product-specific depth).
5. Define formatting rules: Markdown only, heading levels, no HTML, no external links, traceability references as inline text (not hyperlinks).
6. Define quality gates: completeness (all mandatory sections non-empty or explicitly marked as not-yet-documented), specificity (no vague summaries), rebuildability (sufficient for product reconstruction), determinism (same inputs produce same structure).
7. Define validation rules for the generated context.md.
8. Include normative language section referencing RFC 2119 / RFC 8174.
**Done Criteria:**
- File exists at `.aib_brain/conventions/context-convention.md`.
- Contains at least 12 mandatory sections with content guidance.
- Contains formatting rules, quality gates, and validation rules.
- Uses RFC 2119 normative language.
- Contains zero AIB-specific domain acronyms as mandatory headings.
- Does not contain any behavioral/process instructions (how to generate context.md).
**Dependencies:** Task 1 (FS).
**Risk Notes:** R4 — Risk of over-prescription. Mitigate by using MUST for core content, SHOULD for depth, MAY for extensions.

### Task 3: Revise aib-context.md prompt

**Intent:** Remove all structural definitions from the prompt and replace them with a reference to the new convention.
**Inputs:** Current `.aib_brain/prompts/aib-context.md`; `.aib_brain/conventions/context-convention.md` (from Task 2); request.md §Scope item 2.
**Outputs:** Modified `.aib_brain/prompts/aib-context.md`
**Procedure:**
1. Read the current prompt file in full.
2. Remove the "Domain sections" block in Phase 4 §4.2 (the 11 ordered domain headings, Case A/Case B formatting rules).
3. Remove the "Domain-to-product-doc mapping" table at the end.
4. Remove the scope summary table in Phase 4 §4.2 Case B.
5. Add a new instruction at the beginning of Phase 4 (Synthesis): "Read `.aib_brain/conventions/context-convention.md` to obtain the target section structure, content guidance, and formatting rules for context.md."
6. Adjust Phase 4 synthesis logic to say: "Populate each mandatory section defined by the convention using product-doc content, workspace sources, and synthesis rules."
7. Add a "Non-goals" clarification: "Do not explore or read `.aib_brain/` folder contents except `.aib_brain/conventions/context-convention.md`."
8. Retain Phase 1 (Preflight), Phase 2 (Primary read), Phase 3 (Supplementary read), Phase 5 (Write output) intact.
9. Retain Safety section, Context-window management section, and Done criteria section — adjusted to reference convention-defined sections instead of the hardcoded 11 domains.
10. Verify no structural definitions remain in the prompt (no section names, no domain mapping, no scope summaries).
**Done Criteria:**
- File exists at `.aib_brain/prompts/aib-context.md`.
- Contains zero hardcoded domain section names (RQT, ARCH, KNW, CMP, DATA, OBS, SEC, OPR, DEV, DSR, FNL).
- Contains zero domain-to-product-doc mapping tables.
- Contains zero scope summary tables.
- Contains an explicit reference to `.aib_brain/conventions/context-convention.md`.
- Retains Phase 1-5 behavioral logic.
- Retains safety rules, context-window management, and done criteria.
- Retains determinism and full-content-replacement requirements.
**Dependencies:** Task 2 (FS).
**Risk Notes:** R1 — Risk that removing the domain mapping causes the prompt to miss product-doc integration. Mitigate by ensuring the synthesis instruction directs the agent to read `references.md` for product-doc paths and map content into convention sections.

### Task 4: Cross-validation of convention and prompt

**Intent:** Verify the convention and prompt are internally consistent, non-overlapping, and complete.
**Inputs:** `.aib_brain/conventions/context-convention.md` (from Task 2), `.aib_brain/prompts/aib-context.md` (from Task 3), request.md §Success criteria.
**Outputs:** Validation checklist results recorded in implementation.md.
**Procedure:**
1. Read the convention file and verify it defines only structure (sections, content guidance, formatting, quality gates) and no behavioral instructions.
2. Read the prompt file and verify it defines only behavior (phases, reads, synthesis, safety, write) and no structural definitions.
3. Verify the prompt contains an explicit reference to the convention.
4. Verify every mandatory convention section can be populated by the prompt's synthesis logic (i.e., the prompt's read phases provide sufficient input data).
5. Verify no AIB-specific domain acronyms appear as mandatory headings in the convention.
6. Verify the convention can be mentally applied to a non-AIB repository without modification.
7. Record pass/fail results.
**Done Criteria:**
- All 7 checks pass.
- No structural rules found in the prompt.
- No behavioral rules found in the convention.
- Convention is product-agnostic.
**Dependencies:** Task 2 (FS), Task 3 (FS).
**Risk Notes:** None.

## Dependencies & Interfaces

- From Task: 1 | To Task: 2 | Dependency Type: FS | Critical: Y | Notes: Task 2 uses the section outline produced by Task 1.
- From Task: 2 | To Task: 3 | Dependency Type: FS | Critical: Y | Notes: The prompt must reference the convention, so the convention must exist (or be authored in the same session) before the prompt is revised.
- From Task: 2 | To Task: 4 | Dependency Type: FS | Critical: Y | Notes: Cross-validation reads the convention.
- From Task: 3 | To Task: 4 | Dependency Type: FS | Critical: Y | Notes: Cross-validation reads the revised prompt.

- Interface: `.aib_memory/references.md` | Direction: In | Protocol/Contract: Markdown table | Version: Current | Notes: Prompt reads this at runtime to find product-doc paths; not modified by this request.
- Interface: `.aib_memory/context.md` | Direction: Out | Protocol/Contract: Markdown (convention-defined structure) | Version: Will change on next prompt execution | Notes: Indirect output; not modified by this iteration directly.

## Environment & Configuration

- Key: N/A | Scope: N/A | Default: N/A | Allowed Range/Values: N/A | Source: N/A | Change Control: N/A

No environment-specific configuration or secrets are required. Both deliverables are static Markdown files authored and committed via standard VCS workflow.

**Secrets Handling:** Not applicable. No secrets involved.

## Testing Strategy (This Iteration)

- **Test Types:** Manual review (structural inspection of both files against success criteria).
- **Coverage Targets:** 100% of success criteria items validated.
- **Data/Fixtures:** Existing workspace content and product-doc files serve as the test fixture for mental/actual validation.
- **Test Execution:**
  1. Open `.aib_brain/conventions/context-convention.md` and verify mandatory sections >= 12, no AIB acronyms in headings, no behavioral instructions.
  2. Open `.aib_brain/prompts/aib-context.md` and verify zero structural definitions, convention reference present, Phase 1-5 retained.
  3. (Optional) Execute the revised prompt on the AIB workspace and inspect the generated `context.md` for completeness.
- **Acceptance Evidence:** Cross-validation checklist in implementation.md (Task 4 output).

## Observability & Quality Gates

- **Key Metrics/Logs/Alerts:** Not applicable for this iteration (no runtime components modified).
- **Quality Gates:**
  - QG1: Convention file contains >= 12 mandatory sections — PASS/FAIL.
  - QG2: Convention file contains zero AIB-specific domain acronyms as mandatory headings — PASS/FAIL.
  - QG3: Prompt file contains zero structural definitions (no hardcoded section names, no mapping tables, no scope summaries) — PASS/FAIL.
  - QG4: Prompt file contains explicit reference to `.aib_brain/conventions/context-convention.md` — PASS/FAIL.
  - QG5: Convention file contains zero behavioral/process instructions — PASS/FAIL.
  - QG6: Prompt file retains Phase 1-5 behavioral logic, safety rules, context-window management, and done criteria — PASS/FAIL.
  - QG7: No files other than the two deliverables were modified — PASS/FAIL.

## Documentation Touchpoints

- Doc Path: `.aib_brain/conventions/context-convention.md` | Change Type: create | Update Trigger: Task 2 | Edit Allowed: N/A (brain asset, not a product-doc) | Notes: New file; not listed in references.md (brain assets are not product docs).
- Doc Path: `.aib_brain/prompts/aib-context.md` | Change Type: update | Update Trigger: Task 3 | Edit Allowed: N/A (brain asset, not a product-doc) | Notes: Existing prompt; not listed in references.md (brain assets are not product docs).

No product documentation files (per references.md) are modified by this iteration.

## Milestones

- Planned Start: 2026-04-04
- Planned End: 2026-04-04

- Milestone: M1 — Convention authored | Description: context-convention.md created with all mandatory sections, formatting rules, and quality gates | Due: Task 2 completion | Depends On: Task 1 | Exit Criteria: QG1, QG2, QG5 pass.
- Milestone: M2 — Prompt revised | Description: aib-context.md updated with convention reference and all structural definitions removed | Due: Task 3 completion | Depends On: Task 2 | Exit Criteria: QG3, QG4, QG6 pass.
- Milestone: M3 — Cross-validation complete | Description: Both files validated for consistency, separation of concerns, and product-agnosticism | Due: Task 4 completion | Depends On: Task 2, Task 3 | Exit Criteria: All quality gates (QG1-QG7) pass.

## Risks & Mitigations

- R1: New universal section structure may not capture all AIB-specific detail currently in domain-organized context.md — P: Low, I: Medium — Mitigation: Design universal sections broad enough to subsume all current domain content; verify by comparing generated output before/after in optional validation step.
- R2: Separation of convention from prompt may introduce ambiguity about which file governs which aspect — P: Low, I: Medium — Mitigation: Each file includes a scope statement. Convention explicitly states "structure only." Prompt explicitly states "behavior only, references convention for structure."
- R3: AI agents with smaller context windows may struggle with deeply comprehensive context.md — P: Medium, I: Low — Mitigation: Convention and prompt retain context-window management rules. Convention defines a summary preamble for quick orientation.
- R4: Convention may become overly prescriptive for diverse product types — P: Low, I: Medium — Mitigation: Use MUST for core sections, SHOULD for depth guidance, MAY for optional extensions. Allow "Not yet documented" notices for unpopulated sections.

## Acceptance & Handover

- **Acceptance Criteria:**
  - All Done Criteria for Tasks 1-4 satisfied.
  - Quality Gates QG1-QG7 passed.
  - No files other than `.aib_brain/conventions/context-convention.md` and `.aib_brain/prompts/aib-context.md` were created or modified.
  - Success criteria 1-7 from request.md verified.

- **Handover Artifacts:**
  - `.aib_brain/conventions/context-convention.md` (new file)
  - `.aib_brain/prompts/aib-context.md` (modified file)
  - Cross-validation results in implementation.md

- **Post-Iteration Follow-ups:**
  - Execute the revised `aib-context.md` prompt on the AIB workspace to regenerate `.aib_memory/context.md` with the new universal structure (separate action, not part of this iteration).
  - Evaluate the regenerated context.md against the convention's quality gates and the rebuildability standard.

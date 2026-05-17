# 02-analysis — R-20260409-1322 — Decision Points vs Questionnaire

---

## 1. Executive Summary

- **Request ID**: R-20260409-1322

- **Request title**: Decision Points vs Questionnaire (decision-points-vs-questionaire)

- **Iteration ID**: 02 (Active, created 2026-04-09 20:56:23 +0300)

- **Iteration summary**: "remove questionnaire and plan prompts" — this iteration addresses the "Additional requirements" block in `request.md`, which were marked as having priority and were not analyzed in iteration 01.

- **Relation to iteration 01**: Iteration 01 (Completed) analyzed the original request scope: remove questionnaire auto-trigger from analysis, embed questions in `request.md` as `## Questions & Decisions`, revise analysis and request conventions, add Q&D stub to template. Iteration 02 supersedes and expands iteration 01 in three respects:
  1. `aib-questionnaire.md` is fully **deleted** (iteration 01 proposed to keep it as a standalone tool — iteration 02 overrides per latest-iteration-wins rule).
  2. `aib-plan.md` and `plan-convention.md` are fully **deleted** — analysis absorbs planning responsibility and drives plan content into `request.md`.
  3. `request-template.md` is **NOT modified** — iteration 01 proposed adding a Q&D stub; iteration 02 overrides: the template stays as-is, the analysis prompt extends `request.md` dynamically.

- **Core paradigm shift**: After this request is implemented, `request.md` is the **single implementation-driving artifact**. The analysis document becomes a reasoning/knowledge-capture log viewed by humans for auditability but not read by `implement`. All implementation-relevant information (assumptions, plan, testing, documentation, questions) is written into `request.md` by the `create-analysis` action.

- **Conflicts resolved**: Latest-iteration-wins rule applied. Iteration 02 overrides iteration 01 on the three points listed above.

---

## 2. Scope Interpretation

- **Explicitly in scope — iteration 01 items (carried forward)**:

  - `.aib_brain/prompts/aib-analysis.md`: Remove questionnaire auto-trigger; add instructions to embed Q&D, Assumptions, Plan, Testing, and Documentation sections into `request.md`.

  - `.aib_brain/conventions/analysis-convention.md`: Revise mandatory structure; remove sections that move to `request.md`; add rules for what remains; clarify that analysis is a reasoning artifact only.

  - `.aib_brain/conventions/request-convention.md`: Add specification for optional sections added by analysis (`## Assumptions`, `## Plan`, `## Testing`, `## Documentation`, `## Questions & Decisions`); relax validation to allow optional sections beyond the 6 mandatory ones.

  - `.aib_brain/Concepts.md`: Remove `create-questionnaire` and `create-plan` from supported actions, action contract matrix, and holistic workflow.

- **Explicitly in scope — iteration 02 additional requirements (priority)**:

  - `.aib_brain/prompts/aib-questionnaire.md`: **Delete** this file entirely.

  - `.aib_brain/prompts/aib-plan.md`: **Delete** this file entirely.

  - `.aib_brain/conventions/plan-convention.md`: **Delete** this file entirely.

  - `.aib_brain/prompts/aib-implement.md`: Remove reference to analysis as required input; add `request.md` as the sole implementation specification source.

- **Explicitly out of scope**:

  - `.aib_brain/templates/request-template.md` — NOT modified; keeps 6-section stub unchanged.
  - `.aib_brain/conventions/questionnaire-convention.md` — NOT modified (remains available for reference even though the questionnaire prompt is deleted).
  - Existing closed requests and their iteration artifacts — no migration required.
  - Tool scripts (`.aib_brain/tools/*.py`) — no changes needed; none enforce analysis/questionnaire/plan file creation.
  - Test suite (`tests/*.py`) — no test references to questionnaire or plan file creation exist; no changes required.

- **Implicitly in scope** (implicit rule — AIB framework):

  - Analysis-convention.md section 4.12 (Disambiguation Questionnaire) and section 18 (Canonical Disambiguation Questionnaire) must be removed because they exist to feed the plan's Decision Gates section, which is being deleted with `plan-convention.md`.

  - The `aib-analysis.md` prompt must continue confirming completion with `--- I am done with the analysis ---` and must describe re-run merging semantics for the newly added `request.md` sections.

  - `implementation.md` write behavior in `aib-implement.md` is unaffected — it remains append-only with iteration-tagged entries.

---

## 3. Domain Knowledge Essentials

- **AI Builder (AIB)**: A model-agnostic, file-system-first workflow framework stored in `.aib_brain/` (reusable brain assets) and `.aib_memory/` (project-specific memory). Conventions, prompts, and templates in `.aib_brain/` drive deterministic artifact generation.

- **request.md** (post-change): The **single implementation-driving artifact**. Contains everything `implement` needs: goal, background, scope, constraints, assumptions, plan, testing, documentation, and open questions. After this change, `implement` reads only `request.md` and relevant conventions, not analysis or plan files.

- **Analysis document** (post-change): A reasoning/knowledge-capture artifact. Documents the AI's thinking process, research findings, scope interpretation, and impact assessment. Read by humans for auditability. No longer read by `implement`.

- **Implementation-relevant content**: Anything that the `implement` action needs to correctly execute the request — assumptions, implementation tasks, test cases, documentation touchpoints, and open questions/decisions.

- **Reasoning content**: Context, research findings, domain knowledge, technical terms, impacts, and risks — valuable for human review and audit but not execution-driving.

- **QID (Question Identifier)**: A stable identifier (`Q<nnn>`) used to tag question blocks in `## Questions & Decisions` within `request.md`. QIDs enable deterministic re-run merging: answered questions (at least one `[x]` checkbox or non-empty free-text) are preserved verbatim; new questions are appended.

- **Re-run merging**: When `create-analysis` is executed a second time for the same request, the AI reads the current `request.md`, identifies which questions have been answered (by QID), preserves them, adds new unanswered questions, and fully replaces Plan/Testing/Documentation/Assumptions sections (as these are AI-generated, not user-entered).

- **Iteration supremacy rule**: Higher iteration ID overrides lower on conflicts. Iteration 02 overrides iteration 01 for the three diverging design decisions (questionnaire retention, template modification, plan absorption).

- **Impacted roles/personas**:
  - *Repository Developer*: Benefits from a single `request.md` file as the source of truth; no longer needs to consult separate analysis, questionnaire, or plan files during implementation.
  - *AIB Maintainer*: Removes three files from the framework; updates five files with revised responsibilities.
  - *AI Automation Agent*: Must generate implementation-complete `request.md` content during analysis; must NOT read analysis during implement execution.

---

## 4. Technical Knowledge & Terms

- **`.aib_brain/prompts/aib-analysis.md`**: The prompt executed to generate an analysis document and update `request.md`. After this change it absorbs all planning, testing, and documentation-touchpoint generation responsibilities previously held by `aib-plan.md`.

- **`.aib_brain/prompts/aib-plan.md`**: The prompt currently used to generate `<ITERATION_ID>-plan.md`. Will be deleted. Its responsibilities move to `aib-analysis.md` (which writes the plan into `request.md`).

- **`.aib_brain/conventions/plan-convention.md`**: The normative convention for plan document structure, including the Work Breakdown Structure (WBS) schema and Canonical Disambiguation Questionnaire. Will be deleted. The WBS task schema (with External Interfaces and Environment & Configuration additions) is absorbed into `request-convention.md` as the schema for the `## Plan` section.

- **WBS task schema (from plan-convention.md)**: The structured task format used in the Work Breakdown Structure section:
  - `Intent`, `Inputs`, `Outputs`, `Procedure`, `Done Criteria`, `Dependencies`, `Risk Notes`
  - Additions per this request: `External Interfaces (systems, data, modules)` and `Environment & Configuration` added per task.

- **`.aib_brain/conventions/analysis-convention.md`**: Will be drastically simplified. Sections that are implementation-relevant (Assumptions, Affected Documentation, Operational & Documentation Implications, Solution Options, Open Questions & Next Actions, Disambiguation Questionnaire, Canonical Disambiguation Questionnaire) are removed. Remaining sections cover reasoning/knowledge content only.

- **`.aib_brain/conventions/request-convention.md`**: Will be updated to document optional sections 7–11 added by analysis. Validation rules relaxed: from "exactly six sections" to "at least six mandatory sections; optional sections allowed."

- **`.aib_brain/prompts/aib-implement.md`**: Currently states "Use newest iteration artifacts as truth when conflicts exist." After this change: "Use `request.md` as the authoritative source of truth." Analysis files are no longer required inputs for implementation.

- **`create-plan` action**: A currently-supported AIB action backed by `aib-plan.md`. Will be removed as a supported action from `Concepts.md` when its prompt is deleted.

- **`create-questionnaire` action**: Currently supported, auto-triggered from analysis. Will be removed as a supported action (prompt deleted; convention retained for reference).

- **Atomic replacement**: When overwriting a file, the entire file content is replaced as a single write. This applies to `request.md` (with merged Q&D preservation) and `<ITERATION_ID>-analysis.md`.

---

## 5. Assumptions

- Assumption A1: The disambiguation questionnaire subsection (4.12) and section 18 (Canonical Disambiguation Questionnaire) of `analysis-convention.md` should be removed because their primary purpose was to feed the plan's Decision Gates section, which no longer exists as a separate artifact.
  - Rationale: With `plan-convention.md` deleted and the plan absorbed into `request.md`'s `## Plan` section, the canonical disambiguation questionnaire has no consumer.
  - Risk if false: If the canonical disambiguation questions serve another purpose (e.g., a human review gate), removing them could reduce analysis quality.
  - Falsification method: Review all references to "Canonical Disambiguation Questionnaire" and "Decision Gates" in remaining files to confirm no other consumers exist.

- Assumption A2: The `## Plan`, `## Testing`, `## Documentation`, and `## Assumptions` sections in `request.md` are fully AI-generated and may be replaced entirely on re-run (no user-entered data at risk). Only `## Questions & Decisions` contains user-entered answers and requires preservation semantics.
  - Rationale: Users do not edit the Plan/Testing/Documentation/Assumptions sections directly; they answer questions in Q&D and optionally add constraints manually.
  - Risk if false: If a user manually edits the Plan section, a re-run would overwrite their edits silently.
  - Falsification method: Add a note in `request-convention.md` that Plan/Testing/Documentation/Assumptions sections are AI-generated and may be overwritten; users who need to pin content should use the Q&D section.

- Assumption A3: The WBS task schema in the `## Plan` section preserves the existing plan-convention schema (Intent, Inputs, Outputs, Procedure, Done Criteria, Dependencies, Risk Notes) and adds `External Interfaces` and `Environment & Configuration` per task, exactly as the request specifies.
  - Rationale: The request explicitly calls out these two additions to the WBS schema; no other modifications to the task schema are requested.
  - Risk if false: If other WBS fields (e.g., milestones, acceptance handover) are also expected, the Plan section would be incomplete.
  - Falsification method: Re-read the request — "take the component of plan convention 'Work Breakdown Structure (WBS)' and complement each task with specific 'External interfaces', 'Environment & Configuration'" — no other WBS fields mentioned.

- Assumption A4: Removing `plan-convention.md` does not require any changes to tool scripts since the `create-plan` action was AI-driven (no `.aib_brain/tools/create-plan.py` script exists).
  - Rationale: Checked `Concepts.md` action contract matrix — `create-plan` is listed as AI-only (no script row).
  - Risk if false: If any script imports or references plan-convention.md, deletion would cause script errors.
  - Falsification method: `grep -r "plan-convention" .aib_brain/tools/` to verify no script references exist.

- Assumption A5: The `aib-documentation.md` prompt (called by `implement`) does not require changes as a result of this request. It is a documentation-update driver that operates on product-docs independently.
  - Rationale: Nothing in the request mentions `aib-documentation.md`. Its behavior (update product docs after implementation) is orthogonal to this change.
  - Risk if false: If `aib-documentation.md` references plan or questionnaire artifacts as inputs, it would break after deletion.
  - Falsification method: Read `aib-documentation.md` to verify it does not depend on plan or questionnaire files.

- Assumption A6: The `## Testing` section in `request.md` defines test cases at the intent level (what to test and expected outcome), not full test scripts. This is consistent with the request's phrase "defining what tests should be created and performed."
  - Rationale: `request.md` is a specification document, not a test file. Test scripts are produced during `implement`.
  - Risk if false: If the user expects executable test scripts in `request.md`, the format would be insufficient.
  - Falsification method: Cross-reference the request's success criteria — no mention of executable tests in `request.md`, only definitions.

---

## 6. Impact Assessment

### 6.1 Affected Components / Areas

| Component | Change |
| --- | --- |
| `.aib_brain/prompts/aib-analysis.md` | Modify — absorb planning/testing/documentation generation; remove questionnaire trigger |
| `.aib_brain/conventions/analysis-convention.md` | Modify (major) — remove 7 sections, retain ~6 reasoning sections |
| `.aib_brain/conventions/request-convention.md` | Modify — add optional sections 7–11 spec; relax validation |
| `.aib_brain/Concepts.md` | Modify — remove `create-questionnaire` and `create-plan` from actions and workflow |
| `.aib_brain/prompts/aib-implement.md` | Modify — remove analysis as required input; use `request.md` as sole truth |
| `.aib_brain/prompts/aib-questionnaire.md` | **Delete** |
| `.aib_brain/prompts/aib-plan.md` | **Delete** |
| `.aib_brain/conventions/plan-convention.md` | **Delete** |

### 6.2 Change Type and Dependencies

| File | Change Type | Dependency | Sequencing |
| --- | --- | --- | --- |
| `analysis-convention.md` | Modify (major) | Independent | Apply first |
| `request-convention.md` | Modify | Independent | Apply first |
| `aib-analysis.md` | Modify (major) | Depends on updated conventions | Apply after conventions |
| `aib-implement.md` | Modify | Depends on updated request-convention.md | Apply after conventions |
| `Concepts.md` | Modify | Independent | Apply after prompts/conventions |
| `aib-questionnaire.md` | Delete | None | Anytime |
| `aib-plan.md` | Delete | None | Anytime |
| `plan-convention.md` | Delete | None | Anytime |

### 6.3 Domain Impacts

- DOMAIN (ARCH): No impact on system topology or component inventory. Change is entirely within the AI-facing prompt/convention layer.

- DOMAIN (CMP): Direct impact. `create-analysis` action's outputs change (now includes request.md section updates); `create-questionnaire` and `create-plan` actions are removed. `CMP-01.md` should be updated to reflect the new analysis output contract.

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): Minor. Glossary term for "Plan" changes meaning: no longer a separate `<ITERATION_ID>-plan.md` file; plan content lives in `request.md`. `KNW-02.md` business process catalog may need a note update for the analysis workflow output.

- DOMAIN (RQT): `RQT-02.md` (FR-004: "system generates iteration artifacts in the request folder") should be updated. After this change, analysis generates one iteration artifact (`<ITERATION_ID>-analysis.md`) and updates `request.md` with multiple sections. No `questionnaire.md` or `plan.md` are generated.

- DOMAIN (OBS): No impact.
- DOMAIN (OPR): No impact.
- DOMAIN (SEC): No impact.

### 6.4 Constraints

- `request-template.md` MUST NOT be changed (explicit constraint from iteration 02 additional requirements).
- Test suite MUST pass without modification.
- Tool scripts MUST NOT be changed.
- Answered Q&D sections in any active `request.md` MUST be preserved on analysis re-run.
- Deletion of prompts/conventions is irreversible without VCS; should be intentional.
- `questionnaire-convention.md` is NOT deleted (only the prompt is deleted).

### 6.5 Required Documentation Updates

- `.aib_brain/Concepts.md` — Remove create-questionnaire and create-plan from invocation contract and holistic workflow.
- `RQT-02.md` (FR-004) — Update description of artifact outputs for create-analysis action.
- `CMP-01.md` — Update entry for create-analysis to reflect new outputs (updates request.md with plan/testing/documentation/assumptions/Q&D).
- `KNW-02.md` — Update business process "Create analysis" if formally documented.

### 6.6 Decision Points

- **DP-01 — Re-run behavior for AI-generated sections in request.md**: Should `## Plan`, `## Testing`, `## Documentation`, and `## Assumptions` sections in `request.md` be preserved or replaced on analysis re-run?
  - **DECISION: Replaced**. These sections are AI-generated from request context; they have no user-entered data. Replacing them ensures they stay current with the latest analysis findings. Only `## Questions & Decisions` contains user data and uses preservation semantics.

- **DP-02 — Format of `## Plan` section in request.md**: Full WBS schema vs. abbreviated version?
  - **DECISION: Full WBS schema from plan-convention.md plus External Interfaces and Environment & Configuration per task**. The request explicitly specifies this. The complete task schema provides implementation-ready instructions.

- **DP-03 — Canonical Disambiguation Questionnaire (section 18 of analysis-convention.md)**: Remove or keep?
  - **DECISION: Remove**. The canonical disambiguation questionnaire exists to feed the plan's Decision Gates section. With `plan-convention.md` deleted, this section is orphaned. Disambiguation still occurs — resolved decisions are documented in the `## Plan` section's task descriptions; unresolved ones become Q&D items in `request.md`.

- **DP-04 — `questionnaire-convention.md`**: Delete or keep?
  - **DECISION: Keep**. The request only says "questionnaire prompt shall be removed." It does not explicitly say to delete the convention. The convention remains for potential reference, even though the prompt that cited it is deleted. If future use cases for the questionnaire pattern emerge, the convention is available.

---

## 7. Research Plan and Findings

- **Methodology**: Internal-first review of all request artifacts, .aib_brain prompt files, convention files, template file, Concepts.md, tool scripts (via grep), and product documentation (assessed for relevance).

- **Evidence summary**:

  - `aib-analysis.md` prompt confirms current auto-trigger rule for questionnaire. Removing it and adding sections-in-request logic is structurally straightforward.

  - `analysis-convention.md` has 13 mandatory sections plus sections 18 (Canonical Disambiguation Questionnaire). Implementation-relevant sections (5, 9, 10, 11, 12, 13) plus section 18 are candidates for removal. Remaining sections (1–4, 6–8, Risks) cover reasoning/knowledge content. Net reduction: from 13 to ~7 mandatory sections.

  - `request-convention.md` currently specifies exactly 6 mandatory sections and enforces "All six required sections exist exactly once" with no provision for optional sections. This MUST be relaxed to allow analysis-added optional sections.

  - `plan-convention.md` is 400+ lines with 11 sections. The WBS task schema (section 3) is the only portion absorbed into `request-convention.md`. The Canonical Disambiguation Questionnaire (embedded in plan-convention.md's section headers) is consumed by analysis section 4.12; both are removed.

  - `aib-plan.md` prompt has no script backing (confirmed in Concepts.md — no `create-plan.py` entry). Safe to delete.

  - `aib-questionnaire.md` prompt has no script backing (confirmed — no `create-questionnaire.py` entry). Safe to delete.

  - `aib-implement.md` explicitly says "Use newest iteration artifacts as truth when conflicts exist." This must change to reference `request.md` as sole truth.

  - `tests/` directory: confirmed via grep that no test file references "questionnaire" or "plan" artifact generation. Test suite unaffected.

  - Tool scripts (`tools/*.py`): checked via grep — no references to `plan-convention.md`, `aib-plan.md`, or `aib-questionnaire.md` found.

  - `Concepts.md` action contract matrix lists `create-questionnaire` and `create-plan` as supported AI-only actions referencing their respective prompt files. Both entries must be removed from the matrix and from the holistic workflow section.

- **Gaps and unknowns**: None substantive. All design decisions resolved via workspace research and unambiguous request language.

- **Files Read**:

  - `.aib_memory/requests/R-20260409-1322-39-decision-points-vs-questionaire/request.md` — Active request; confirmed Additional requirements block and its priority claim.
  - `.aib_memory/requests/R-20260409-1322-39-decision-points-vs-questionaire/iterations.md` — Confirmed iteration 01 Completed, iteration 02 Active.
  - `.aib_memory/requests/R-20260409-1322-39-decision-points-vs-questionaire/01-analysis.md` — Iteration 01 analysis; identified conflicts with iter 02 on three design points.
  - `.aib_brain/prompts/aib-analysis.md` — Confirmed current auto-trigger logic and output structure.
  - `.aib_brain/prompts/aib-plan.md` — Confirmed AI-only prompt; no script; safe to delete.
  - `.aib_brain/prompts/aib-questionnaire.md` — Confirmed AI-only prompt; no script; safe to delete.
  - `.aib_brain/prompts/aib-implement.md` — Confirmed "newest iteration artifacts" language that must change.
  - `.aib_brain/conventions/analysis-convention.md` — Full read; confirmed 13-section structure, section 4.12, section 18; identified candidates for removal.
  - `.aib_brain/conventions/request-convention.md` — Full read; confirmed 6-section enforcement; identified relaxation needed.
  - `.aib_brain/conventions/plan-convention.md` — Full read; confirmed WBS schema; confirmed Canonical Disambiguation Questionnaire content.
  - `.aib_brain/templates/request-template.md` — Confirmed 6-section stub; template NOT to be changed.
  - `.aib_brain/Concepts.md` — Full read; confirmed action contract matrix entries and holistic workflow for create-questionnaire and create-plan.
  - `.aib_memory/references.md` — Read; built product-doc required-read set.
  - `tests/conftest.py` — Read; confirmed no questionnaire/plan references in test infrastructure.
  - `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — Stub content; no relevant detail. [SKIPPED — domain out of scope]
  - `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-004 confirmed relevant for documentation update.
  - `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Confirmed create-analysis entry needs output update.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` through `ARCH-07.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` through `DATA-09.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` through `SEC-04.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Glossary; no new terms required.
  - `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — Business process catalog; noted create-analysis process entry.
  - `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — Personas confirmed; no new personas introduced.

---

## 8. Rewrite Proposal of the Request

*See updated `request.md` file. The proposal below is the full rewrite in compliance with `request-convention.md` and reflects the combined iteration 01 + iteration 02 scope.*

*Note: `request.md` is being updated as a second output artifact of this analysis run (the primary artifact is this file). The `## Plan`, `## Testing`, `## Documentation`, `## Assumptions`, and `## Questions & Decisions` sections are added by this analysis as per the new pattern. The first 6 mandatory sections are rewritten for specificity and completeness.*

---

**Proposed `request.md` content (full rewrite)** — *see actual file write below this analysis*

---

## 9. Solution Options

No unresolved design forks exist for this iteration. All decision points (DP-01 through DP-04) were resolved by the AI through workspace research and unambiguous request language. No alternatives presented for user selection.

---

## 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0028 | AIB Concepts | `.aib_brain/Concepts.md` | Remove create-questionnaire and create-plan from action contract matrix and holistic workflow |
| — | Analysis convention | `.aib_brain/conventions/analysis-convention.md` | Major restructuring: remove 7 sections, retain reasoning content, add new purpose statement |
| — | Request convention | `.aib_brain/conventions/request-convention.md` | Add optional sections 7–11 spec; relax validation rules |
| — | Analysis prompt | `.aib_brain/prompts/aib-analysis.md` | Absorb plan/testing/documentation generation; remove questionnaire trigger |
| — | Implement prompt | `.aib_brain/prompts/aib-implement.md` | Remove analysis as required input; use request.md as sole truth |
| REF-0023 | RQT-02 - Requirements document | `.aib_memory/docs/03 Requirements/RQT-02.md` | FR-004 — update artifact output description for create-analysis |
| REF-0007 | CMP-01 - Notebook/script catalog | `.aib_memory/docs/04 Technology/Compute/CMP-01.md` | Update create-analysis action output description |

*Note: `.aib_brain/` files are listed here for completeness but have `edit_allowed=N` per `references.md` (REF-0028). These are brain asset evolution changes — the request explicitly targets these files. The `references.md` restriction applies to AI-driven documentation updates outside explicit request scope; it does not block authorized framework evolution requests.*

---

## 11. Operational & Documentation Implications

- **Runbooks**: None exist; no impact.
- **SLAs/SLOs**: Not applicable.
- **Monitoring/observability/logging**: No impact. Tool scripts unchanged; no log format changes.
- **Data quality rules**: Not applicable.
- **Product documentation**:
  - `RQT-02.md` (FR-004): Update to reflect that `create-analysis` now produces one analysis file AND updates `request.md` with plan/testing/documentation/assumptions/Q&D sections. No `questionnaire.md` or `plan.md` generated.
  - `CMP-01.md` (create-analysis action entry): Update outputs column.
  - `KNW-02.md` (business process "Create analysis"): If formally documented, update outputs section.

---

## 12. Risks

- Risk R1: Re-run data loss — analysis re-run incorrectly identifies an answered Q&D question as unanswered and overwrites the user's answer.
  - Probability: Medium
  - Impact: High (user data loss, trust erosion)
  - Mitigation: Convention defines unambiguous "answered" signal (at least one `[x]` OR non-empty free-text block). `create-analysis` prompt must log each QID preserve/add/flag decision in the analysis Executive Summary.
  - Owner (role): AIB Maintainer

- Risk R2: `request.md` bloat — adding Plan, Testing, Documentation, Assumptions, and Q&D sections makes `request.md` very long for complex requests.
  - Probability: Medium
  - Impact: Low (readability concern only; no functional impact)
  - Mitigation: Convention limits each Plan task to concise fields; Testing entries are intent-level (not full scripts); Documentation lists paths only.
  - Owner (role): AIB Maintainer

- Risk R3: Incomplete `aib-implement.md` update — if the implement prompt still reads analysis files after this change, it may receive stale or conflicting instructions.
  - Probability: Low (clear change required)
  - Impact: High (implementation could diverge from request scope)
  - Mitigation: Explicitly update the "Input resolution" block of `aib-implement.md` to reference `request.md` as sole truth and remove iteration-artifact reading.
  - Owner (role): AI Automation Agent (during implementation)

- Risk R4: Orphaned cross-references — `analysis-convention.md` references section 4.12 / section 18 internally; removing these sections may leave broken internal cross-references in the document.
  - Probability: Medium
  - Impact: Low (convention document quality issue)
  - Mitigation: Perform a full text search of `analysis-convention.md` for "4.12", "18", "Disambiguation", "Decision Gates", "canonical" before saving; update or remove all such references.
  - Owner (role): AI Automation Agent (during implementation)

- Risk R5: `aib-documentation.md` dependency on plan/questionnaire — if this prompt reads plan or questionnaire files as inputs, deletion would break it.
  - Probability: Low (suspected to be independent)
  - Impact: Medium
  - Mitigation: Read `aib-documentation.md` before implementation; verify it does not depend on deleted artifacts.
  - Owner (role): AI Automation Agent (during implementation)

---

## 13. Open Questions & Next Actions

All design decisions have been resolved internally via workspace research. No user-input questions remain.

- **Next action**: Rewrite `request.md` (as the second output of this analysis run) and then implement the changes described in sections 2 and 6.1 across the 8 target files.

---

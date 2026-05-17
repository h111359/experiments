# 01-analysis — R-20260409-1322 — Decision Points vs Questionnaire

---

## 1. Executive Summary

- **Request ID**: R-20260409-1322

- **Request title**: Decision Points vs Questionnaire (decision-points-vs-questionaire)

- **Iteration ID**: 01 (Active, created 2026-04-09)

- **High-level purpose**: Eliminate the separately-generated `<ITERATION_ID>-questionnaire.md` artifact by embedding open questions directly into the `request.md` file during the analysis run. Once a user answers those questions in `request.md`, those answers become recorded decisions available to subsequent iterations. Two sections are removed from the analysis mandatory structure: section 9 (Solution Options) and section 13 (Open Questions & Next Actions). Solution-option choices are re-expressed as questions embedded in `request.md`. A safety constraint requires that re-running analysis must never overwrite user-supplied answers in `request.md` unless an explicit decision conflict is detected.

- **Earlier iterations**: None — this is iteration 01.

- **Conflicts**: None detected.

---

## 2. Scope Interpretation

- **Explicitly in scope**:

  - `.aib_brain/prompts/aib-analysis.md`: remove the auto-trigger of `create-questionnaire`; add instructions directing the AI to embed all open/solution-option questions into the updated `request.md` rewrite.

  - `.aib_brain/conventions/analysis-convention.md`: remove sections 9 (Solution Options) and 13 (Open Questions & Next Actions) from the mandatory structure; renumber remaining sections; add normative rules governing how questions are written into `request.md` and how re-run merging works.

  - `.aib_brain/conventions/request-convention.md`: add specification for a new `## Questions & Decisions` section, including placement, format, QID stability rules, and re-run preservation semantics.

  - `.aib_brain/templates/request-template.md`: add a `## Questions & Decisions` stub section.

- **Explicitly out of scope**: None stated by user.

- **Implicitly in scope** (implicit rule - AIB framework):

  - `.aib_brain/Concepts.md` action-contract matrix still references the `create-questionnaire` auto-trigger from `create-analysis`; this document should be updated for accuracy. Treated as in-scope but lower priority than the primary convention/prompt files.

  - Existing closed requests that already contain `<ITERATION_ID>-questionnaire.md` files are not affected; no retroactive migration is required.

  - The `aib-questionnaire.md` prompt file itself is **not** in scope; it remains available as a standalone tool but will no longer be invoked automatically from the analysis workflow.

---

## 3. Domain Knowledge Essentials

- **AI Builder (AIB)**: A model-agnostic, file-system-first workflow framework stored in `.aib_brain/` (reusable brain assets) and `.aib_memory/` (workspace-specific memory artifacts). Conventions, prompts, and templates in `.aib_brain/` drive deterministic artifact generation.

- **Request (`request.md`)**: The primary human-facing specification file for a work unit. Located at `.aib_memory/requests/<request-folder>/request.md`. Currently has six mandatory sections. Editing is allowed only while the request is `Active`.

- **Questionnaire (`<ITERATION_ID>-questionnaire.md`)**: A separately generated file containing structured questions (QIDs) to clarify unresolved decision points before planning and implementation. Currently auto-triggered from the analysis workflow when open questions exist.

- **Decision Point**: A design fork that requires an explicit stakeholder choice before implementation can proceed. Currently captured in analysis section 4.6.6 and mirrored as questions in the questionnaire.

- **Iteration**: A numbered stage within a request. Artifacts are scoped per iteration. Higher iteration IDs override lower ones on conflicts.

- **Impacted roles/personas**:
  - *Repository Developer*: Answers questions directly in `request.md` instead of a separate questionnaire file.
  - *AIB Maintainer*: Updates brain assets (conventions, prompts, templates) per this request.
  - *AI Automation Agent*: Must apply merging logic when re-running analysis against a `request.md` that already contains answered questions.

- **Business processes touched**: `create-analysis` (BP-0002 derivative) and the request-rewrite step within that workflow.

---

## 4. Technical Knowledge & Terms

- **`.aib_brain/conventions/`**: Holds all normative AIB convention files. Convention changes take effect for all subsequent artifact generations; existing artifacts are NOT retroactively rewritten.

- **`.aib_brain/prompts/aib-analysis.md`**: The prompt executed to generate an analysis document. It currently auto-triggers `create-questionnaire` when section 13 contains at least one user-owned open question.

- **`.aib_brain/conventions/analysis-convention.md`**: Normative document defining mandatory structure, authoring rules, and quality gates for `<ITERATION_ID>-analysis.md` files.

- **`.aib_brain/conventions/request-convention.md`**: Normative document defining the file structure and content rules for `request.md`.

- **`.aib_brain/templates/request-template.md`**: Seed template for new `request.md` files; contains section stubs.

- **QID (Question Identifier)**: A stable identifier (e.g., `QID-BF-001`, `QID-AT-001`) assigned to each question. QIDs persist across re-runs to enable idempotent merging.

- **Re-run merging**: The process by which a second (or subsequent) analysis execution reads the existing `## Questions & Decisions` section of `request.md`, identifies answered questions by QID, and preserves those answers while adding new unanswered questions.

- **`[x]` checkbox**: Markdown syntax for a checked checkbox (`- [x]`), used to mark a selected option. An unchecked option is `- [ ]`. A question is considered "answered" when at least one option is `- [x]` or the free-text answer box is non-empty.

- **Conflict flag**: A textual marker, e.g., `[DECISION REVIEW NEEDED]`, added to a previously answered question when the re-run analysis concludes that the prior answer conflicts with a changed context.

---

## 5. Assumptions

- Assumption A1: The `## Questions & Decisions` section will be placed at the **end** of `request.md`, after `## Success criteria`, so it does not disrupt existing section ordering or tooling that parses the first six sections.
  - Rationale: All six current mandatory sections exist before this addition; appending avoids touching any existing parser or validation rules.
  - Risk if false: If tooling expects exactly six sections, adding a seventh breaks validation or template expectations.
  - Falsification method: Read all `request.md` validation rules in `request-convention.md` and tool scripts (`create-request.py`, `common.py`) for section-count enforcement.

- Assumption A2: A simplified QID-based format (QID header, question text, checkbox options, optional free-text block) is sufficient for embedding questions in `request.md` without replicating the full questionnaire-convention block layout.
  - Rationale: The full questionnaire block includes `Intent`, `Rationale`, `Impact Areas`, `Assumptions`, `Constraints & Guards` — this level of detail is excessive for inline use inside `request.md`. A compact format with QID, question, and answer options is both machine-parseable and human-readable.
  - Risk if false: If a simpler format does not uniquely identify questions across re-runs, merging becomes unreliable.
  - Falsification method: Verify QID uniqueness is preserved via the stable QID identifier; format change does not affect uniqueness.

- Assumption A3: All answers entered by the user in `## Questions & Decisions` are preserved verbatim on re-run as long as at least one checkbox is `[x]` or the free-text block is non-empty.
  - Rationale: This directly implements the user constraint "ensure answers are not lost during request rewriting."
  - Risk if false: If no deterministic "answered" signal exists, the merge logic has no reliable way to decide what to keep.
  - Falsification method: Define a clear "answered" rule in the convention (at least one `[x]` OR non-empty free-text block).

- Assumption A4: The `aib-questionnaire.md` prompt is kept as-is and is not auto-triggered anymore from the analysis workflow. It remains available as a manual standalone tool.
  - Rationale: The request explicitly says "do not create questionnaire anymore" in the analysis workflow; it does not say to delete the prompt.
  - Risk if false: If users still expect `create-questionnaire` to be triggered on analysis, they may be confused by its absence.
  - Falsification method: Re-read the request scope. Scope says "Change the analysis prompt, conventions, templates" — the questionnaire prompt is not listed.

- Assumption A5: The existing `Disambiguation Questionnaire` sub-section (4.12 in the current convention) within the analysis **remains** in the analysis document. The request only eliminates section 9 (Solution Options) and section 13 (Open Questions & Next Actions).
  - Rationale: The request explicitly names sections 9 and 13. Section 4.12 (Disambiguation Questionnaire, which answers canonical disambiguation questions in the analysis) is a different construct — it records answers to known template questions, not open issues for the user.
  - Risk if false: If the Disambiguation Questionnaire is also meant to move to request.md, significant convention re-architecture is needed.
  - Falsification method: Re-read request — "eliminate the analysis section '13. Open Questions & Next Actions' and use the questionnaire in request.md to define and ask the user for input on the open questions."

---

## 6. Impact Assessment

### 6.1 Affected Components / Areas

- `.aib_brain/prompts/aib-analysis.md` — prompt file controlling analysis artifact generation
- `.aib_brain/conventions/analysis-convention.md` — convention governing analysis document structure
- `.aib_brain/conventions/request-convention.md` — convention governing `request.md` structure
- `.aib_brain/templates/request-template.md` — seed template for new requests
- `.aib_brain/Concepts.md` — action contract matrix (update note on `create-questionnaire` auto-trigger)

### 6.2 Change Type and Dependencies

| File | Change Type | Dependency | Sequencing |
| --- | --- | --- | --- |
| `aib-analysis.md` | Modify | Depends on updated analysis-convention.md and request-convention.md | Apply after conventions are updated |
| `analysis-convention.md` | Modify (remove sections, add merging rules) | Independent | Apply first |
| `request-convention.md` | Modify (add new section spec) | Independent | Apply first |
| `request-template.md` | Modify (add section stub) | Depends on updated request-convention.md | Apply after request-convention.md |
| `Concepts.md` | Modify (remove auto-trigger note) | Independent | Apply last |

### 6.3 Domain Impacts

- DOMAIN (ARCH): No impact on system topology or component inventory. The change is purely in the AI-facing prompt/convention layer.
  - No relevant requirement IDs.

- DOMAIN (CMP): Indirect impact. The `create-analysis` action (`CMP-ART`-equivalent) no longer auto-triggers `create-questionnaire`. CMP-01 may need a note update if it documents the analysis action's outputs.

- DOMAIN (DATA): No impact detected.

- DOMAIN (DEV): No impact detected.

- DOMAIN (KNW): Glossary term TERM-0013 (Prompt Action) remains valid. No new terms required.

- DOMAIN (RQT): FR-004 ("The system generates iteration artifacts in the request folder") may need clarification that `create-analysis` now embeds questions in `request.md` instead of creating a separate questionnaire file. Low-impact update.

- DOMAIN (OBS): No impact detected.

- DOMAIN (OPR): No impact detected.

- DOMAIN (SEC): No impact detected.

### 6.4 Constraints

- `request.md` editing is only allowed while the request is `Active`; the analysis rewrite must not modify `request.md` of a closed request.
- Answered questions must not be overwritten unless a new analysis run detects an explicit conflict (changed scope or new evidence that contradicts the prior answer).
- The change must not break existing test suite (`tests/`) or tool scripts.
- New `## Questions & Decisions` section must be optional (absent in requests that have no open questions) to remain backward compatible with existing request files.

### 6.5 Required Documentation Updates

- `.aib_brain/conventions/analysis-convention.md` — Required update: remove sections 9 and 13; renumber; add merging rules.
- `.aib_brain/conventions/request-convention.md` — Required update: add `## Questions & Decisions` section specification.
- `.aib_brain/templates/request-template.md` — Required update: add stub.
- `.aib_brain/prompts/aib-analysis.md` — Required update: remove questionnaire auto-trigger; add embedded-question instructions.
- `.aib_brain/Concepts.md` — Minor update: action contract note.

### 6.6 Decision Points

- **DP-01 — Questions format in `request.md`**: What format should embedded questions use?

  - Option A: Full questionnaire-convention block (QID, Intent, Rationale, Impact Areas, Assumptions, Options, Selection UI, Constraints) — identical to current questionnaire.md structure.
    - Implication: High fidelity, familiar format, but request.md becomes verbose.
  - Option B: Simplified inline format (QID, question text, checkbox options, optional free-text block) — lightweight subset.
    - Implication: Readable and concise; QID provides merging stability; slightly less structured.
  - **DECISION: Option B (simplified inline format)**. Rationale: `request.md` is a specification document, not a questionnaire document. A compact inline format keeps it readable while providing the QID stability needed for reliable re-run merging. Full questionnaire detail belongs in standalone questionnaire files (when used manually).

- **DP-02 — Placement of `## Questions & Decisions` in `request.md`**: Where does the new section appear?

  - Option A: After `## Success criteria` (as the 7th section, optional).
  - Option B: Before `## Success criteria` (as the 5th section, required).
  - **DECISION: Option A — after `## Success criteria`, as an optional 7th section**. Rationale: Keeps the required six sections intact; questions are supplemental to the specification, not part of the specification core. Making it optional maintains backward compatibility.

- **DP-03 — Conflict detection signal**: How does re-run analysis signal that a prior answer should be reviewed?

  - Option A: Append `> [!NOTE] DECISION REVIEW NEEDED: <reason>` block to the question.
  - Option B: Replace the answer with `[CONFLICT — prior answer: <option>]` note.
  - **DECISION: Option A** — Append a non-destructive `> [!NOTE]` Markdown callout to the affected question so the prior answer is preserved and the reviewer knows why it needs attention.

---

## 7. Research Plan and Findings

- **Methodology**: Internal-first review of request artifacts, conventions, templates, prompt files, and product documentation.

- **Evidence summary**:
  - `aib-analysis.md` prompt auto-triggers `create-questionnaire` when section 13 has user-owned items. Removing this trigger eliminates the questionnaire artifact from the analysis workflow.
  - `analysis-convention.md` defines 13 mandatory sections. Sections 9 and 13 are confirmed candidates for removal. Section 4.12 (Disambiguation Questionnaire) is a separate section that answers canonical questions inside the analysis itself — confirmed as NOT being removed by this request.
  - `request-convention.md` specifies exactly six mandatory sections. Adding a 7th optional section is feasible without breaking existing validation, as long as the convention explicitly marks it optional.
  - `request-template.md` is a six-section empty stub. Adding the new section stub is trivial.
  - `questionnaire-convention.md` and `aib-questionnaire.md` are unchanged; they remain available for manual standalone use.
  - No existing tool scripts parse `request.md` for section count beyond existence checks.

- **Gaps and unknowns**: None. All design decisions are resolvable via workspace research and stated request intent.

- **Proposed validation actions**:
  - After implementation, run `create-analysis` on a test request; verify: (a) no `questionnaire.md` is created, (b) `request.md` is rewritten with a `## Questions & Decisions` section, (c) re-running analysis preserves answered questions.

- **Files Read**:
  - `.aib_brain/prompts/aib-analysis.md` — Prompt source; confirms auto-trigger logic and output section descriptions.
  - `.aib_brain/prompts/aib-questionnaire.md` — Questionnaire prompt; confirms it is a separate, self-contained prompt not touched by this request.
  - `.aib_brain/conventions/analysis-convention.md` — Full convention read; confirmed section numbering, section 9, section 13, and Disambiguation Questionnaire (section 4.12).
  - `.aib_brain/conventions/request-convention.md` — Full read; confirmed six mandatory sections and validation rules.
  - `.aib_brain/conventions/questionnaire-convention.md` — Read to understand QID format and question block canonical structure.
  - `.aib_brain/templates/request-template.md` — Read to confirm stub structure.
  - `.aib_brain/Concepts.md` — Read; confirmed action contract matrix references questionnaire auto-trigger.
  - `.aib_memory/references.md` — Read; built product-doc required-read set.
  - `.aib_memory/context.md` — Synthesized product context; confirmed active personas, functional requirements.
  - `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — Stub-only content.
  - `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-004 confirmed relevant.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Architecture overview; confirms file-first deterministic design.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — ADRs; no existing ADR directly relevant.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — Sequence diagrams; no analysis-related sequences defined.
  - `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — Resource catalog; no impact.
  - `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Script catalog; confirms `create-analysis` action; may need minor note update.
  - `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Glossary; no new terms required.
  - `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — Business processes; analysis workflow BP referenced.
  - `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — Personas confirmed.
  - `.aib_memory/requests/R-20260409-1152-add-comments-in-the-code/01-analysis.md` — Reference analysis; confirmed current 13-section structure in practice.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — Stub only. [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` through `DATA-08.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Analytics/DATA-06.md`, `DATA-09.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — [SKIPPED — domain out of scope]
  - `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` through `SEC-04.md` — [SKIPPED — domain out of scope]

---

## 8. Rewrite Proposal of the Request

*See updated `request.md` file. The proposal below is the full rewrite in compliance with `request-convention.md`.*

---

**Proposed `request.md` content** (see actual file rewrite below this analysis):

---
```
## Goal

Refactor the AIB analysis workflow so that open questions and solution-option alternatives are embedded as a `## Questions & Decisions` section directly inside `request.md` instead of being written to a separate `<ITERATION_ID>-questionnaire.md` artifact. Answered questions in `request.md` serve as recorded decisions for subsequent iterations.

## Background

The current `create-analysis` workflow produces two output files: `<ITERATION_ID>-analysis.md` and `<ITERATION_ID>-questionnaire.md`. The questionnaire contains decision-point questions that duplicate the Decision Points sub-section (4.6.6) already captured in the analysis. This redundancy increases maintenance effort and requires the user to manually copy answers back between files. Eliminating the separate questionnaire file consolidates the Q&A workflow into `request.md`, which is already the canonical specification artifact for the active request.

## Scope

The following files must be changed:

1. `.aib_brain/prompts/aib-analysis.md`
   - Remove the rule that auto-triggers `create-questionnaire` when section 13 has user-owned open questions.
   - Add instructions directing the AI to write all open questions and solution-option questions into the `## Questions & Decisions` section of the rewritten `request.md`.
   - On re-run: first read the existing `## Questions & Decisions` section of `request.md`; preserve all questions whose QID already exists and for which at least one checkbox is `[x]` or the free-text block is non-empty; add new unanswered questions; append a `> [!NOTE] DECISION REVIEW NEEDED: <reason>` callout to any answered question whose prior answer appears to conflict with the updated analysis context.

2. `.aib_brain/conventions/analysis-convention.md`
   - Remove section 9 (Solution Options) from mandatory structure.
   - Remove section 13 (Open Questions & Next Actions) from mandatory structure.
   - Renumber the remaining sections accordingly.
   - Add normative rules describing the questions-in-request.md pattern: format, QID requirement, re-run merging, conflict marking.

3. `.aib_brain/conventions/request-convention.md`
   - Add specification for an optional 7th section `## Questions & Decisions`.
   - Placement: after `## Success criteria`.
   - Content: zero or more question blocks. Each block has: stable QID (`Q<nnn>`), question text, checkbox options (`- [ ] / - [x]`), optional free-text answer block.
   - Re-run preservation rule: answered questions (at least one `[x]` or non-empty answer block) MUST NOT be removed or overwritten on analysis re-run.

4. `.aib_brain/templates/request-template.md`
   - Append stub: `## Questions & Decisions` (empty, no question blocks initially).

5. `.aib_brain/Concepts.md`
   - Update action-contract matrix entry for `create-analysis` to remove the statement about auto-triggering `create-questionnaire`.

## Out of scope

- `.aib_brain/prompts/aib-questionnaire.md` — not modified; remains available as a standalone manual tool.
- `.aib_brain/conventions/questionnaire-convention.md` — not modified.
- Existing closed requests and their questionnaire files — no migration required.
- Retroactive changes to any existing `request.md` files.
- Changes to tool scripts (`.aib_brain/tools/*.py`) unless a script currently enforces six-section-only validation for `request.md`.

## Constraints

- When analysis is re-executed (idempotent re-run), answers already entered by the user in `request.md → ## Questions & Decisions` MUST be preserved unless a conflict is explicitly detected.
- The `## Questions & Decisions` section MUST be optional; requests with no open questions MUST NOT have an empty shell section added.
- The simplified inline question format inside `request.md` MUST use stable QIDs (`Q<nnn>`) so re-run merging is deterministic.
- The change MUST NOT break existing test suite (`tests/*.py`) or alter the behavior of any tool script.

## Success criteria

- Running `create-analysis` on an active request produces `<ITERATION_ID>-analysis.md` only; no `<ITERATION_ID>-questionnaire.md` is generated.
- The rewritten `request.md` contains a `## Questions & Decisions` section with all open questions when the analysis identifies unknowns or decision forks.
- Re-running `create-analysis` on a request where the user has answered questions in `request.md` preserves all answered questions unmodified.
- Analysis sections "9. Solution Options" and "13. Open Questions & Next Actions" are absent from all newly generated analysis documents.
- The `request-convention.md` and `analysis-convention.md` pass a manual review verifying backward compatibility for existing closed requests.
```
---

---

## 9. Solution Options

**Option A — Keep separate questionnaire; auto-populate `## Decisions` in `request.md` from answered questionnaire**

- Overview: Retain the existing `questionnaire.md` artifact. After the user answers the questionnaire, a new `sync-decisions` step copies answers into a `## Decisions` section of `request.md`.
- Benefits: No format changes to questionnaire; existing users familiar with questionnaire flow are unaffected.
- Trade-offs: Adds a new `sync-decisions` step; does not eliminate duplication between analysis Decision Points and questionnaire questions.
- Constraints: Requires a new tool or prompt for the sync step.
- Risks: Duplication remains; two sources of truth for decisions.
- Expected effort: Medium (new sync step required).
- Acceptance-test idea: Verify answered questionnaire is reflected in `request.md` Decisions section.

**Option B — Embed questions directly in `request.md` with simplified inline QID format (Recommended)**

- Overview: Remove questionnaire auto-trigger from `create-analysis`. Embed all open questions and solution-option forks as a new `## Questions & Decisions` section in `request.md` using a compact QID + checkbox format. Re-run logic merges answers.
- Benefits: Single file for specification + Q&A; eliminates duplication; user answers in place; no separate file to manage.
- Trade-offs: `request.md` gains a new optional section; AI must implement merge logic on re-run.
- Constraints: QID format in `request.md` must be simple enough to parse reliably.
- Risks: Merge logic incorrectly identifies a question as "answered" or "unanswered" if format is inconsistently applied.
- Expected effort: Low–Medium (convention updates + prompt updates).
- Acceptance-test idea: Re-run analysis after answering questions; confirm answers are preserved and no new questionnaire file is created.

**Option C — Fully inline format without QIDs; accept risk of merge collisions**

- Overview: Embed questions in `request.md` as plain prose or numbered lists without QID stability.
- Benefits: Minimal format overhead.
- Trade-offs: No stable merge key; re-run cannot reliably detect previously answered questions.
- Constraints: Requires human manual management of answers on every re-run.
- Risks: High — answers can be silently overwritten on re-run.
- Expected effort: Low (convention update only).
- Acceptance-test idea: Re-run analysis; verify whether answers are preserved (likely fail).

**Recommendation**: **Option B** — the QID-based simplified inline format directly satisfies the stated request goals, eliminates duplication, and provides deterministic merge semantics. Option A preserves unnecessary duplication. Option C is unsafe for the stated constraint about answer preservation.

---

## 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| — | `aib-analysis.md` prompt | `.aib_brain/prompts/aib-analysis.md` | Remove questionnaire auto-trigger; add embedded-questions instructions |
| — | Analysis convention | `.aib_brain/conventions/analysis-convention.md` | Remove sections 9 and 13; renumber; add merging rules |
| — | Request convention | `.aib_brain/conventions/request-convention.md` | Add `## Questions & Decisions` section specification |
| — | Request template | `.aib_brain/templates/request-template.md` | Add section stub |
| REF-0028 | AIB Concepts | `.aib_brain/Concepts.md` | Remove `create-questionnaire` auto-trigger from action contract matrix |

*Note: The above files are brain assets (`edit_allowed=N` per `references.md` for REF-0028 `Concepts.md`). The request-convention and analysis-convention files are also brain assets. All changes are in-scope for AIB-framework-evolution requests.*

---

## 11. Operational & Documentation Implications

- **Runbooks**: None currently exist; no impact.
- **SLAs/SLOs**: Not applicable.
- **Monitoring/observability/logging**: No impact. Tool scripts are unchanged; no log format changes.
- **Data quality rules**: Not applicable.
- **Product documentation**:
  - `RQT-02.md` (FR-004): Should note that `create-analysis` no longer produces a questionnaire artifact; instead embeds questions in `request.md`. Low-priority update.
  - `CMP-01.md` (CMP-ART for create-analysis): The output of the analysis action changes; the outputs column should note embedded questions in `request.md` instead of a questionnaire file. Low-priority update.
  - `KNW-02.md` (business process "Create analysis"): If this process is formally documented, its outputs section should be updated to reflect the single-artifact output and the Q&A-in-request pattern.

---

## 12. Risks

- Risk R1: Re-run merge collision — the analysis re-run incorrectly classifies an answered question as unanswered and overwrites the user's answer.
  - Probability: Medium
  - Impact: High (user data loss, trust erosion)
  - Mitigation: Define a strict and unambiguous "answered" signal in the convention (at least one `[x]` OR non-empty free-text block); require the AI to log each QID decision (preserve/add/flag) in a re-run summary note appended to the analysis executive summary.
  - Owner (role): AIB Maintainer

- Risk R2: request.md becomes cluttered for long-lived requests with many unanswered questions — reducing readability.
  - Probability: Low
  - Impact: Medium
  - Mitigation: Convention rule stating that answered questions should be collapsed to a single-line summary after the answer is recorded; analysis should limit open questions to high-impact items only.
  - Owner (role): AIB Maintainer

- Risk R3: Confusion about the role of the standalone `aib-questionnaire.md` prompt — users may be unclear whether to still invoke it.
  - Probability: Medium
  - Impact: Low
  - Mitigation: Add a deprecation note or redirect comment at the top of `aib-questionnaire.md` explaining when it is appropriate (manual standalone use only; not invoked by analysis).
  - Owner (role): AIB Maintainer

- Risk R4: Existing analysis convention references section 9 and section 13 in quality gates and interaction rules — incomplete update could leave broken cross-references.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Perform a full text search of `analysis-convention.md` for "section 9", "section 13", "Solution Options", "Open Questions" before saving; verify all cross-references are updated.
  - Owner (role): AI Automation Agent (during implementation)

---

## 13. Open Questions & Next Actions

All design decisions (DP-01, DP-02, DP-03) have been resolved internally via workspace research. No user-input questions remain open at this time.

This section is intentionally minimal.

- **Next action**: Implement the changes described in the Rewrite Proposal (section 8) across the five target files.

---

## Goal

Restructure `.aib_brain/prompts/aib-analysis.md` to reduce cognitive load and improve execution determinism. The prompt is currently too long, deeply nested, and mixes multiple concerns within individual sections, increasing the risk of step-skipping and misinterpretation by AI agents. The goal is to apply clear separation of concerns, eliminate redundant constraint duplication, and add an Execution Model Summary and a Failure Handling section without changing any authoritative behavioral rules.

## Background

As of v1.2.8, `aib-analysis.md` governs the AI agent's analysis workflow for the AIB framework. A review identified nine structural issues (labeled 2.1–2.9 in the input) that each increase the probability of execution errors:

- Section 7.5 (Q-block Generation Rules) mixes workflow steps, validation rules, output rules, and behavioral constraints in a single block.
- Section 4 (Preflight) combines state resolution, input reading, Q&A execution, context loading, and amendments in one overloaded phase.
- The Decision Points Catalog table lacks a defined category taxonomy and enforcement of allowed tag values.
- The "explicit source requirement" for autonomous resolution is overly strict, causing the agent to over-generate Q-blocks and ignore obvious conventions.
- The same constraint is restated across multiple sections, increasing maintenance cost and the risk of inconsistency.
- The Standard Flow Final Step (section 8) mixes conditional execution, template comparison logic, script behavior, and reset semantics in a single block.
- There is no high-level Execution Model Summary to orient the AI agent before it begins.
- Failure modes beyond register inconsistency and empty input are unspecified.
- Legacy references to "Questions & Decisions" remain in some sections despite the authoritative rename to `## Decisions`.

## Scope

- Restructure Section 7.5 of `aib-analysis.md` into three clearly separated sub-sections: Decision Identification, Decision Classification, and Q-block Generation Rules.

- Refactor Section 4 (Preflight) into four labeled execution phases: State Resolution, Input Acquisition, State Mutation (Q&A, Amendments), and Context Enrichment.

- Add a defined category taxonomy and allowed-value enforcement for the Decision Points Catalog table (Category field and Tag field).

- Relax the "explicitly and unambiguously stated" requirement for autonomous resolution to "explicitly stated OR strongly implied by established convention", with a mandatory rationale when using implied knowledge.

- Introduce a `## Global Constraints` section near the top of the prompt to consolidate repeated constraints (no archive reads, single input reset per run, Q-blocks only in first cycle), and replace inline repetitions with references (e.g., "See GC-02").

- Split Section 8 (Standard Flow Final Step) into three sub-sections: Eligibility Check (stub detection logic), Finalize Script Invocation, and Post-conditions.

- Add an `## Execution Model Summary` section at or near the top of the prompt, describing the six execution phases in order.

- Add a `## Failure Handling` section specifying halt-with-error behavior for: missing mandatory files, script execution failures, and corrupted convention files.

- Perform a global find-and-replace of any remaining "Questions & Decisions" wording and standardize to `## Decisions` throughout the document.

## Out of scope

- Changes to any other prompt file (e.g., `aib-implement.md`, `aib-context.md`).

- Changes to tool scripts (`.aib_brain/tools/*.py`).

- Changes to convention files (`.aib_brain/conventions/*.md`).

- Changes to the authoritative behavioral rules — only structure and clarity changes are in scope; no rule semantics are altered.

- Changes to `input.md`, `context.md`, `requests_register.md`, or any memory artifact other than what is written by this analysis run.

- Updating automated tests beyond what is strictly necessary to validate the restructured prompt.

## Constraints

- The restructured prompt MUST produce identical behavioral outcomes to the current prompt for all current test cases.

- No section numbering scheme is mandated — any clear, consistent numbering or labeling system that reduces cognitive load is acceptable.

- The prompt MUST remain a single Markdown file at `.aib_brain/prompts/aib-analysis.md`.

- All authoritative invariants (e.g., the halt gate for multiple Active requests, the single input reset per run, the Q-block Q&A cycle) MUST be preserved verbatim or by clear reference.

- The `Global Constraints` section, if introduced as a new section, MUST NOT conflict with or override any existing behavioral rule.

## Success criteria

- The restructured `aib-analysis.md` prompt has a distinct `## Execution Model Summary` section near the top describing all six execution phases.

- Section 7.5 (or its renamed equivalent) is split into at least three clearly separated sub-sections covering Decision Identification, Decision Classification, and Q-block Generation Rules.

- Section 4 (Preflight or its renamed equivalent) is organized into at least four labeled phases: State Resolution, Input Acquisition, State Mutation, and Context Enrichment.

- The Decision Points Catalog specifies a Category taxonomy (allowed values listed) and Tag allowed values (`ask` / `resolve-autonomously`).

- A `## Failure Handling` section exists and covers at minimum: missing mandatory files, script execution failure, and corrupted convention files.

- A `## Global Constraints` section (or equivalent deduplication mechanism) exists and all previously duplicated constraint statements are replaced with a single authoritative location plus reference.

- No occurrence of "Questions & Decisions" remains in the document.

- All existing automated tests continue to pass after the restructuring.

- The document remains a single Markdown file at `.aib_brain/prompts/aib-analysis.md`.

## Assumptions

- A1: All 12 verbatim strings asserted by `tests/test_analysis_prompt_structure.py` can be preserved during the restructuring of sections 4, 7.5, and 8, because the restructuring only adds surrounding headings and phase labels without rewriting constrained prose.
  - Risk if false: One or more existing tests fail after implementation, requiring a targeted fix to restore the asserted string.

- A2: The current `aib-analysis.md` contains no occurrence of "Questions & Decisions" as a heading or in body text. Issue 2.9 from the input is therefore a no-op for the prompt file itself.
  - Risk if false: A residual occurrence exists and must be replaced; no behavioral impact.

- A3: The "strongly implied by established convention" relaxation of the autonomous-resolution rule will not require changes to any convention file — only the wording in section 7.5 of `aib-analysis.md` is changed.
  - Risk if false: Convention files would need coordinated updates; low probability.

- A4: Adding `## Execution Model Summary`, `## Global Constraints`, and `## Failure Handling` as new top-level sections does not conflict with any existing section numbering assertion in the test suite, because the tests check for content strings, not section numbers.
  - Risk if false: A test asserts a specific section number that shifts; low probability given current test file review.

- A5: The Global Constraints section will list at minimum GC-01 through GC-03 covering: no archive reads, single input reset per run, Q-blocks only in first analysis cycle. These are the three constraints duplicated most broadly across the current prompt.
  - Risk if false: Fewer GCs are sufficient; no functional risk.

## Plan

### Task 1: Add `## Execution Model Summary` section

#### Intent
Insert a new top-level section near the top of `aib-analysis.md` (after the Objective section) providing a six-phase execution overview.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — updated with `## Execution Model Summary` section.

#### Procedure
Open `.aib_brain/prompts/aib-analysis.md` and locate the boundary between Section 1 (Objective) and Section 2 (Inputs & External Dependencies).

Insert a new `## Execution Model Summary` section between those two sections with the following content:

```
## Execution Model Summary

This prompt operates as a deterministic multi-phase workflow. Each phase is strictly ordered and must complete before the next begins.

1. **Preflight** — Resolve register state, read inputs, apply any answered Q&A, apply amendments, and load context.
2. **Branch handling** — Auto-create request (when no Active request exists) OR proceed with existing Active request.
3. **Analysis generation** — Produce `analysis-<request_id>.md` with 8 mandatory sections.
4. **Request enrichment** — Update `request-<request_id>.md` with Assumptions, Plan, Documentation, and Decisions.
5. **Q-block generation** (optional) — Write AI-generated questions to `input.md ## Questions` when genuine decision forks exist.
6. **Finalization** — Archive `input.md` (conditional on non-stub state) and reset to seed template via `finalize-input.py`.
```

#### Done criteria
`aib-analysis.md` contains the string `Execution Model Summary` as a `##` heading. All existing tests in `test_analysis_prompt_structure.py` continue to pass.

#### Dependencies
None.

#### Risk notes
None. This is a pure addition with no modification of existing text.

---

### Task 2: Add `## Global Constraints` section

#### Intent
Consolidate the three most-duplicated cross-cutting constraints into a central registry section near the top of `aib-analysis.md`, and replace inline duplications with GC references.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — updated with `## Global Constraints` section and inline GC references.

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, immediately after the new `## Execution Model Summary` section (Task 1), insert a `## Global Constraints` section with at minimum the following entries:

```
## Global Constraints

These constraints apply throughout the entire prompt execution. Individual sections reference them by GC identifier rather than restating them.

- **GC-01 — No archive reads:** `inputs/input-archive-*.md` files in request folders MUST NOT be read or referenced during any phase of this prompt.
- **GC-02 — Single input reset:** `input.md` MUST be reset exactly once per run. The reset is performed either by the Auto-Request Creation Branch (section 4.7, step 6) or by the Standard Flow Final Step (section 8). Never both.
- **GC-03 — Q-blocks in first cycle only:** Q-blocks are generated only when this is the first analysis run for the active request (i.e., no answered Q-blocks exist in `input.md`). On re-run after answers, no new Q-blocks are generated.
- **GC-04 — Halt on missing mandatory files:** If any mandatory file listed in section 2.1 (Inputs) cannot be read, execution MUST HALT with an explicit error message identifying the missing file.
- **GC-05 — No partial writes on halt:** When execution halts due to any error condition, MUST NOT write any output files. The workspace state must remain unchanged.
```

After inserting the section, locate each inline duplication of these rules in the document body and append `(See GC-0N)` after the relevant sentence.

#### Done criteria
`aib-analysis.md` contains the string `Global Constraints` as a `##` heading with at least 5 GC-numbered entries. All existing tests pass.

#### Dependencies
Task 1 (section insertion order).

#### Risk notes
Inline reference placement must not alter the meaning of the sentence it annotates. Reviewer should verify that GC references are additive, not replacements.

---

### Task 3: Add `## Failure Handling` section

#### Intent
Add an explicit failure handling section specifying halt-with-error behavior for: missing mandatory files, script execution failures, and corrupted convention files.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — updated with `## Failure Handling` section.

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, insert a `## Failure Handling` section after `## Global Constraints` (Task 2) with at minimum the following content:

```
## Failure Handling

> **Trigger:** Any of the conditions below MUST cause an immediate execution HALT.
> **Rule:** On halt, output the specified literal error message and MUST NOT write any output files (See GC-05).

| Condition | Error message |
| --- | --- |
| A mandatory input file (section 2.1) cannot be read | `ERROR: Cannot read mandatory file <path>. Execution halted.` |
| A convention file (`.aib_brain/conventions/*.md`) cannot be read | `ERROR: Cannot read convention file <path>. Execution halted.` |
| A tool script (`.aib_brain/tools/*.py`) exits with a non-zero code | `ERROR: Tool script <script> failed with exit code <N>. Execution halted.` |
| `request-<request_id>.md` is absent after Auto-Request Creation Branch completes | `ERROR: request-<request_id>.md was not created. Execution halted.` |
```

#### Done criteria
`aib-analysis.md` contains the string `Failure Handling` as a `##` heading. All existing tests pass.

#### Dependencies
Task 2 (section insertion order).

#### Risk notes
None. This is a pure addition.

---

### Task 4: Refactor Section 4 (Preflight) into four labeled phases

#### Intent
Insert phase headings within the existing Preflight section to group its steps into four clearly labeled phases, without altering any step text.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — Preflight steps grouped under Phase 1–4 labels.

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, within the `## 4. Mandatory Preflight` section, insert phase headings as follows:

- Before step 1 (Resolve register state): insert `### Phase 1 — State Resolution`
- Before step 2 (Resolve active request): insert `### Phase 2 — Input Acquisition` (steps 2–5 belong here)

Wait — re-examining the input's recommendation: Phase 1 = State Resolution, Phase 2 = Input Acquisition, Phase 3 = State Mutation, Phase 4 = Context Enrichment.

Apply as follows:
- Insert `### Phase 1 — State Resolution` before step 1 (covering steps 1–2).
- Insert `### Phase 2 — Input Acquisition` before step 3 (covering steps 3–5).
- Insert `### Phase 3 — State Mutation (Q&A and Amendments)` before the Answer Application Sub-flow and before step 9 amendment detection (covering section 4.8 trigger and step 9).
- Insert `### Phase 4 — Context Enrichment` before step 6 (covering steps 6–8).

Note: The Answer Application Sub-flow (section 4.8) is triggered from within Phase 2 step 5; the Phase 3 label documents it as a logical phase even though its procedural trigger is in step 5. Add a note to this effect.

#### Done criteria
`aib-analysis.md` contains at least the string `Phase 1 — State Resolution` and `Phase 2 — Input Acquisition` as level-3 headings. All existing tests pass.

#### Dependencies
Tasks 1–3 (section count context).

#### Risk notes
Phase label insertion must not break the numbered step references used by other sections of the prompt (e.g., "Preflight step 5", "step 6 of Preflight"). Verify that all cross-references still resolve after insertion.

---

### Task 5: Split Section 7.5 into three sub-sections

#### Intent
Divide the Q-block Generation Rules section into three clearly separated sub-sections: Decision Identification, Decision Classification, and Q-block Generation.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — section 7.5 reorganized into 7.5.1, 7.5.2, 7.5.3.

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, locate section `### 7.5 Q-block Generation Rules` and restructure it as follows:

- Insert `#### 7.5.1 Decision Identification` before `**Step 1 — Decision Fork Enumeration**` content.
- Insert `#### 7.5.2 Decision Classification (ask vs resolve-autonomously)` before `**Step 2 — Mandatory pre-check**` content.
- Insert `#### 7.5.3 Q-block Generation` before `**Step 3 — Ambiguity detection and Q-block generation**` content.

Keep all existing text within each sub-section verbatim; only add the sub-section headings.

Also, within `#### 7.5.2`, update the autonomous-resolution wording from:

> `explicitly and unambiguously stated`

to:

> `explicitly stated or strongly implied by established convention`

and add immediately after: `When using implied knowledge, the rationale MUST name the specific convention file and section in the Decision Points Catalog.`

#### Done criteria
`aib-analysis.md` contains strings `7.5.1`, `7.5.2`, and `7.5.3` as sub-section labels. The string `explicitly stated or strongly implied` is present. The string `explicitly and unambiguously stated` is absent. All existing tests pass.

#### Dependencies
None.

#### Risk notes
The wording change in 7.5.2 must not weaken the intent: the new wording must still require a named source (convention file + section) when using implied knowledge, preventing it from being used as a rationalization for avoiding questions.

---

### Task 6: Add Decision Points Catalog taxonomy

#### Intent
Add allowed-value definitions for the `Category` and `Tag` columns of the Decision Points Catalog table within the Implementation Alternatives description in `aib-analysis.md`.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — Decision Points Catalog schema extended with allowed values.

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, locate the `### Decision Points Catalog` subsection description within `## Implementation Alternatives` (section 6.2).

Immediately after the table definition, insert the following allowed-value specification:

```
**Category** MUST be one of: `Architecture`, `Data Model`, `UX/UI`, `Integration`, `Performance`, `Testing`, `Documentation`.

**Tag** MUST be one of: `ask` (a Q-block is raised for developer input) or `resolve-autonomously` (resolved by the AI with a documented rationale citing a named source).
```

#### Done criteria
`aib-analysis.md` contains the string `Category` with at least the allowed-value list and `Tag MUST be one of`. All existing tests pass.

#### Dependencies
None.

#### Risk notes
None. This is a pure addition to the table description.

---

### Task 7: Split Section 8 into three sub-sections

#### Intent
Divide the Standard Flow Final Step into three clearly separated sub-sections: Eligibility Check, Finalize Script Invocation, and Post-conditions.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — section 8 reorganized into 8.1, 8.2, 8.3.

#### Procedure
In `.aib_brain/prompts/aib-analysis.md`, locate `## 8. Standard Flow Final Step` and restructure as follows:

- Insert `### 8.1 Eligibility Check` before the trigger guard block (the `> **Trigger guard:**` note) and before the stub-detection step 1.
- Insert `### 8.2 Finalize Script Invocation` before the `finalize-input.py` invocation step 2 (the `python .aib_brain/tools/finalize-input.py ...` block).
- Insert `### 8.3 Post-conditions` after the script invocation, listing: the reset inherently clears any `## Questions` section; no further file writes are permitted after this step.

Keep all existing text verbatim; only add the sub-section headings and the Post-conditions content.

All verbatim test-asserted strings must remain in their existing positions within the sub-sections:
- `evaluate whether \`.aib_memory/input.md\` is in a non-stub state` → in 8.1
- `archive the pre-reset \`input.md\` content` → in 8.2
- `If stub-equivalent: skip archive creation for this standard-flow reset.` → in 8.2

#### Done criteria
`aib-analysis.md` contains strings `8.1`, `8.2`, and `8.3` as sub-section labels. All three verbatim test-asserted strings remain present. All existing tests pass.

#### Dependencies
None.

#### Risk notes
The trigger guard note (which excludes this step when called from `aib-implement.md`) must remain in 8.1 (Eligibility Check) and must not be accidentally moved inside the Finalize Script Invocation sub-section.

---

### Task 8: Add regression tests for new sections

#### Intent
Add automated test assertions for the three new top-level sections introduced in Tasks 1–3, to prevent future accidental removal.

#### Outputs
`tests/test_analysis_prompt_structure.py` — new test class `TestNewStructuralSections` with three test methods.

#### Procedure
Open `tests/test_analysis_prompt_structure.py`.

Add a new class `TestNewStructuralSections` with the following test methods:

1. `test_execution_model_summary_present` — asserts `"Execution Model Summary" in content` of `ANALYSIS_PROMPT`.
2. `test_global_constraints_present` — asserts `"Global Constraints" in content` of `ANALYSIS_PROMPT`.
3. `test_failure_handling_present` — asserts `"Failure Handling" in content` of `ANALYSIS_PROMPT`.

#### Done criteria
Running `pytest tests/test_analysis_prompt_structure.py` passes all tests including the three new ones.

#### Dependencies
Tasks 1–3 (the sections must exist before the tests pass).

#### Risk notes
None.

---

### Task 9: Run full automated test suite

#### Intent
Verify that all changes to `aib-analysis.md` and `test_analysis_prompt_structure.py` produce zero test failures.

#### Outputs
Terminal output confirming all tests in `tests/` pass.

#### Procedure
From the workspace root, run:

```
pytest tests/ -v
```

Inspect output. If any test fails, identify the failing test, trace the assertion to the affected file, and fix the implementation before proceeding.

#### Done criteria
`pytest tests/` exits with code 0 and all tests report `PASSED`.

#### Dependencies
Tasks 1–8 (all implementation changes complete).

#### Risk notes
If a test-asserted verbatim string is accidentally modified during restructuring, it will appear as a specific assertion failure pointing to the exact string. Fix by restoring the exact string.

---

### Task 10: Update documentation

#### Intent
Update `.aib_memory/context.md` to reflect the restructured `aib-analysis.md` and append implementation change bullets to `logs/next_version_changes.md`.

#### Outputs
- `.aib_memory/context.md` — updated sections describing the analysis workflow and FR-004.
- `logs/next_version_changes.md` — new bullets appended.

#### Procedure
Open `.aib_memory/context.md`.

In the `## Business Context` section, under `Execute analysis workflow`, add: "The prompt includes an `## Execution Model Summary` section, a `## Global Constraints` section (GC-01 through GC-05), and a `## Failure Handling` section. Section 4 (Preflight) is organized into four labeled phases. Section 7.5 is split into three sub-sections. Section 8 is split into three sub-sections."

Acceptance test: the string `Execution Model Summary` appears in `context.md`.

In the `## Requirements Summary` section, under FR-004, update the description to reference the new structural sections.

Acceptance test: FR-004 description does not describe a single monolithic Preflight section.

Open `logs/next_version_changes.md` and append one bullet per logical change implemented:

- `- Add Execution Model Summary section to aib-analysis.md.`
- `- Add Global Constraints registry (GC-01 through GC-05) to aib-analysis.md.`
- `- Add Failure Handling section to aib-analysis.md.`
- `- Refactor aib-analysis.md Preflight into four labeled phases.`
- `- Split aib-analysis.md section 7.5 into Decision Identification, Classification, and Generation sub-sections.`
- `- Add Decision Points Catalog category taxonomy and tag allowed values to aib-analysis.md.`
- `- Relax autonomous-resolution rule to allow strongly implied convention with named source rationale.`
- `- Split aib-analysis.md section 8 into Eligibility Check, Finalize Script Invocation, and Post-conditions sub-sections.`
- `- Add regression tests for Execution Model Summary, Global Constraints, and Failure Handling sections.`

Acceptance test: `logs/next_version_changes.md` ends with the above bullets and no prior bullets are modified.

#### Dependencies
Tasks 1–9 (implementation complete and tested).

#### Risk notes
Context.md is auto-generated by `aib-context.md` prompt; manual edits may be overwritten on the next context generation run. This is a known limitation; the update is still required by the instructions.md directive.

## Documentation

- `.aib_memory/context.md` — update Business Context and FR-004 to reference the new structural sections in `aib-analysis.md` (Execution Model Summary, Global Constraints, Failure Handling, phased Preflight, sub-divided Q-block rules and Standard Flow Final Step).

- `logs/next_version_changes.md` — append one bullet per logical change implemented, as specified in Task 10.

## Decisions

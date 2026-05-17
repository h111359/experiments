## Goal

Restructure the analysis output format and update the `aib-analysis.md` prompt to produce a leaner, more actionable analysis artifact: remove sections that duplicate or add little decision value; add new sections for internet best practices and implementation alternatives; improve Q-block generation by explicitly identifying implementation variants before generating questions; and add a minimum-questions configuration option to `input.md`.

## Background

The current `analysis-<request_id>.md` output contains nine mandatory sections, several of which either duplicate content already captured in `request.md` (Testing is already planned and tracked there) or add verbose context without driving implementation decisions (Domain Knowledge Essentials, Technical Knowledge & Terms, Multi-Perspective Stakeholder Review). Formatting inconsistencies — bold titles instead of markdown headings, and no empty lines between items — reduce readability.

The analysis prompt currently generates Q-blocks reactively by detecting specification ambiguities, but lacks an explicit step for identifying implementation approach alternatives. This means the developer may receive fewer and less-targeted questions than needed, or face a second round of questions on a subsequent run. Adding an explicit "Implementation Alternatives" step surfaces all significant decision points in a single pass, giving the developer greater transparency and decision ownership.

A minimum-questions configuration option in `input.md` lets the developer signal how many decisions they want surfaced per run, defaulting to zero so the AI only asks when genuinely needed.

## Scope

- `.aib_brain/prompts/aib-analysis.md` — add Implementation Alternatives identification step before Q-block generation; update Q-block generation rules to derive questions from identified alternatives; update output section instructions to reflect removed and added sections; update all seed template strings; update standard-flow final step language

- `.aib_brain/conventions/analysis-convention.md` — revise mandatory section list (remove Domain Knowledge Essentials, Technical Knowledge & Terms, Testing, Multi-Perspective Stakeholder Review; add Best Practices and Implementation Alternatives); update formatting rules; redefine Executive Summary to Request ID + Title + Purpose only; define "Files read during this analysis run" as a separate heading; remove Evidence log sub-section requirement from Research Results

- `.aib_brain/tools/initialize.py` — add minimum-questions option to the input_seed string

- `.aib_brain/tools/close-request.py` — add minimum-questions option to the input_seed string

- `tests/` — add regression tests verifying removed sections are absent from `analysis-convention.md` and new sections are present; update any tests that reference old section counts or names

## Out of scope

- Changes to `aib-implement.md` prompt

- Changes to `aib-context.md` prompt

- Changes to `request-convention.md`

- Changes to the request lifecycle tooling scripts beyond seed template string updates in `initialize.py` and `close-request.py`

- UI or rendering changes to the CLI menu

## Constraints

- The analysis document must remain a reasoning artifact only; `implement` MUST NOT read it

- All changes to `analysis-convention.md` must remain consistent with changes to `aib-analysis.md`

- Existing passing tests must not regress

- Python scripts must continue to use stdlib only (Python 3.10+)

- Seed template changes in `initialize.py` and `close-request.py` must be identical to each other

## Success criteria

- SC-1: `analysis-convention.md` no longer lists Domain Knowledge Essentials, Technical Knowledge & Terms, Testing, or Multi-Perspective Stakeholder Review as mandatory sections

- SC-2: `analysis-convention.md` lists Best Practices and Implementation Alternatives as mandatory sections

- SC-3: Executive Summary in `analysis-convention.md` is defined as containing only Request ID, Title, and Purpose

- SC-4: "Files read during this analysis run" is defined as a separate heading (not a bullet embedded within another section)

- SC-5: Research Results in `analysis-convention.md` does not reference an Evidence log sub-section as required content

- SC-6: `aib-analysis.md` prompt includes an explicit Implementation Alternatives identification step before Q-block generation

- SC-7: `aib-analysis.md` generates a Q-block for each identified implementation alternative that has materially different implementation outcomes

- SC-8: `input.md` (and seed templates in `initialize.py` and `close-request.py`) include a minimum-questions configuration option defaulting to 0

- SC-9: Existing test suite passes without regressions (`pytest tests/` exits 0)

## Assumptions

- A1: The analysis document must remain a reasoning-only artifact after restructuring; `implement` must not read it. The current intent documented in `analysis-convention.md` and `context.md` is preserved.
  - Risk if false: `implement` may begin reading analysis artifacts, creating a tight coupling between the analysis format and the implementation flow.

- A2: "Files read during this analysis run" is defined as a top-level `## Files Read During This Analysis Run` section (a peer of other `##` content sections). The mandatory section count is 8 (not 7 as initially estimated). Decision confirmed by Q001 answer.
  - Risk if false: N/A — confirmed by developer.

- A3: The minimum-questions option uses a free-text line `- Minimum questions: 0` in `## Options` (developer edits the integer directly). Decision confirmed by Q002 answer.
  - Risk if false: N/A — confirmed by developer.

- A4: "Implementation Alternatives" is placed after "Best Practices" and before "AI Copilot Suggestions". Full order: Research Results → Best Practices → External Benchmarking → Minimal Spikes → Implementation Alternatives → AI Copilot Suggestions. Decision confirmed by Q003 answer.
  - Risk if false: N/A — confirmed by developer.

- A5: The existing `test_analysis_prompt_structure.py` tests will not break because they test for the absence of already-removed section names (not for the presence of Domain Knowledge Essentials or Multi-Perspective Stakeholder Review).
  - Risk if false: If any test positively asserts the presence of sections being removed, those tests must be updated.

- A6: `context.md` (FR-004 description) will need to be updated to reflect the new mandatory section list. The documentation task covers this.
  - Risk if false: `context.md` will describe a stale section structure, causing confusion on the next context regeneration.

## Plan

### Task 1: Update `analysis-convention.md`

#### Intent
Revise the mandatory section list and all associated content rules to reflect the new analysis document structure.

#### Outputs
`.aib_brain/conventions/analysis-convention.md` — fully rewritten mandatory section list and section-specific rules

#### Procedure
Read the current `.aib_brain/conventions/analysis-convention.md` in full.

Remove sections 2 (Domain Knowledge Essentials), 3 (Technical Knowledge & Terms), 8 (Testing), and 9 (Multi-Perspective Stakeholder Review) from the mandatory section list and their associated content rules.

Update the mandatory section list to the new order: 1. Executive Summary; 2. Research Results; 3. Best Practices; 4. External Benchmarking; 5. Minimal Spikes and Experiments; 6. Implementation Alternatives; 7. AI Copilot Suggestions.

Rewrite the Executive Summary section rule to require only: Request ID, Title, and Purpose. Add a `### Files Read During This Analysis Run` sub-section definition within the Executive Summary rule.

Rewrite the Research Results section rule to remove the Evidence log sub-section requirement. Keep pattern scan and workspace file inspection as the primary content.

Add a new `## Best Practices [REQ]` section rule: research-based internet best practices relevant to the request topic; minimum two findings; summarize and assess applicability; do not embed external links.

Add a new `## Implementation Alternatives [REQ]` section rule: list each identified approach as a named alternative with a one-sentence description, key trade-offs, and expected impact on the codebase. State which alternative is recommended and why.

Update all formatting rules in `.aib_brain/conventions/analysis-convention.md` to require markdown headings (`##`, `###`) instead of bold labels; require empty lines between items for readability; remove any mention of bold-title formatting.

#### Done criteria
- `analysis-convention.md` mandatory section list contains exactly 8 sections (Executive Summary, Files Read During This Analysis Run, Research Results, Best Practices, External Benchmarking, Minimal Spikes and Experiments, Implementation Alternatives, AI Copilot Suggestions).
- Sections Domain Knowledge Essentials, Technical Knowledge & Terms, Testing, Multi-Perspective Stakeholder Review are absent.
- Sections Best Practices, Implementation Alternatives, and Files Read During This Analysis Run are present with `[REQ]` markers.
- Executive Summary rule references only Request ID, Title, and Purpose (no Files Read sub-heading — Files Read is a top-level section).
- Research Results rule does not reference Evidence log.

#### Dependencies
None

#### Risk notes
Must not accidentally remove content rules for sections being kept (Research Results, External Benchmarking, Minimal Spikes and Experiments, AI Copilot Suggestions).

---

### Task 2: Update `aib-analysis.md` — output section instructions

#### Intent
Align the prompt's output generation instructions with the new analysis section structure defined in Task 1.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — updated Part 1 output section instructions

#### Procedure
Read the current `## Output — Part 1` section of `.aib_brain/prompts/aib-analysis.md`.

Remove generation instructions for Domain Knowledge Essentials, Technical Knowledge & Terms, Testing (as a Part 1 output), and Multi-Perspective Stakeholder Review.

Update the Executive Summary generation instruction to: produce only Request ID, Title, and Purpose; add a `### Files Read During This Analysis Run` sub-section listing all workspace files read during this run.

Update the Research Results generation instruction to remove the Evidence log requirement. Keep the pattern scan and workspace file inspection instructions.

Add a generation instruction for `## Best Practices`: research and list internet best practices relevant to the request topic; minimum two findings; each with a concise statement and an applicability assessment; do not embed external links.

Add a generation instruction for `## Implementation Alternatives`: before generating Q-blocks, explicitly enumerate all implementation approaches that lead to materially different outcomes; for each alternative provide a name, one-sentence description, key trade-offs, and expected codebase impact; mark the recommended alternative; this step MUST execute before the Q-block generation step.

#### Done criteria
- Part 1 output instructions reference exactly the 8 sections defined in Task 1.
- No instructions for Domain Knowledge Essentials, Technical Knowledge & Terms, Testing (as Part 1 output), or Multi-Perspective Stakeholder Review remain.
- Prompt has a dedicated `## Files Read During This Analysis Run` generation instruction (top-level `##` section, not sub-heading inside Executive Summary).
- Executive Summary instruction requires only Request ID, Title, and Purpose.
- Implementation Alternatives instruction is present and is explicitly ordered before Q-block generation.

#### Dependencies
Task 1 must be complete (convention drives prompt alignment check).

#### Risk notes
The analysis prompt is long; editing must be careful not to remove the Research Results instruction while removing the surrounding sections.

---

### Task 3: Update `aib-analysis.md` — Implementation Alternatives step and Q-block generation

#### Intent
Add an explicit Implementation Alternatives identification step to the main analysis flow and update Q-block generation rules to derive questions from identified alternatives.

#### Outputs
`.aib_brain/prompts/aib-analysis.md` — updated main flow with Implementation Alternatives step and updated Q-block generation rules

#### Procedure
In the main analysis flow of `.aib_brain/prompts/aib-analysis.md`, add a new step titled "**Implementation Alternatives identification (MUST execute before Q-block generation):**" after the research steps and before the "Ambiguity detection" step.

The new step must instruct the AI to: enumerate all implementation approaches that satisfy the request with materially different outcomes; for each approach list its name, a one-sentence description, key trade-offs, and expected codebase impact; mark the recommended approach; write the result to `## Implementation Alternatives` in the analysis document.

Update the "Ambiguity detection" / Q-block generation rules to state: after completing the Implementation Alternatives step, generate one Q-block per identified alternative where the developer's preference will materially affect the implementation; the Q-block must reference the alternative by name from the Implementation Alternatives section.

Update the soft limit for Q-blocks to: "Soft limit: 9 Q-blocks per run; this limit applies after mandatory alternatives-derived Q-blocks are generated; alternatives-derived Q-blocks MUST NOT be suppressed to meet the soft limit."

Update the minimum-questions handling: "If the developer has set a minimum-questions value greater than 0 in `input.md ## Options`, generate at least that many Q-blocks. If fewer genuine decision points exist than the minimum, document the shortfall in the analysis but do NOT generate low-value filler questions."

#### Done criteria
- `aib-analysis.md` contains an explicit Implementation Alternatives identification step in the main flow.
- The step is explicitly ordered before Q-block generation.
- Q-block generation rules reference implementation alternatives as a Q-block source.
- Minimum-questions handling is described.

#### Dependencies
Task 2 must be complete (removes conflicting output instructions that would be adjacent to the new step).

#### Risk notes
None — this is an additive change to the main flow; no existing flow steps are removed.

---

### Task 4: Add minimum-questions option to seed templates

#### Intent
Add a minimum-questions configuration option to the `input.md` seed template strings in `initialize.py` and `close-request.py`, and to the seed template string in `aib-analysis.md`.

#### Outputs
`.aib_brain/tools/initialize.py` — updated `input_seed` string

`.aib_brain/tools/close-request.py` — updated `input_seed` string

`.aib_brain/prompts/aib-analysis.md` — updated seed template strings in the standard-flow final step and Auto-Request Creation Branch reset step

#### Procedure
In `.aib_brain/tools/initialize.py`, locate the `input_seed` string. Add the line `- Minimum questions: 0\n` as a new item in the `## Options` section, after the two existing toggle lines, before the `\n## Input\n` line.

In `.aib_brain/tools/close-request.py`, locate the `input_seed` string. Apply the identical change as in `initialize.py`.

In `.aib_brain/prompts/aib-analysis.md`, locate all occurrences of the seed template string (there are two: in the Auto-Request Creation Branch step 8 and in the Standard flow final step). Update both to include the minimum-questions line.

Verify that the seed template string is now identical across all three files for the `## Options` section.

#### Done criteria
- `initialize.py input_seed` contains `- Minimum questions: 0`.
- `close-request.py input_seed` contains `- Minimum questions: 0`.
- Both `aib-analysis.md` seed template occurrences contain `- Minimum questions: 0`.
- All four occurrences are textually consistent in the `## Options` section.

#### Dependencies
Task 3 must be complete (aib-analysis.md is being edited in multiple tasks; serialize to avoid conflicts).

#### Risk notes
`test_questions_in_input_md.py` asserts that "Question threshold" is absent; the new "Minimum questions" option must not use the word "threshold" to avoid false test failures.

---

### Task 5: Add regression tests for new analysis-convention.md structure

#### Intent
Add automated tests asserting that the removed sections are absent from `analysis-convention.md` and that the new sections are present.

#### Outputs
`tests/test_analysis_prompt_structure.py` — new test class(es) for `analysis-convention.md` section structure

#### Procedure
Open `tests/test_analysis_prompt_structure.py`.

Add a new test class `TestAnalysisConventionSectionStructure` with the following test methods:

- `test_domain_knowledge_absent`: asserts "Domain Knowledge Essentials" not in `analysis-convention.md`.
- `test_technical_knowledge_absent`: asserts "Technical Knowledge & Terms" not in `analysis-convention.md`.
- `test_testing_section_absent`: asserts "Testing" does not appear as a `[REQ]` mandatory section heading.
- `test_multi_perspective_absent`: asserts "Multi-Perspective Stakeholder Review" not in `analysis-convention.md`.
- `test_best_practices_present`: asserts "Best Practices" in `analysis-convention.md`.
- `test_implementation_alternatives_present`: asserts "Implementation Alternatives" in `analysis-convention.md`.
- `test_minimum_questions_in_initialize_seed`: asserts "Minimum questions" in `initialize.py`.
- `test_minimum_questions_in_close_request_seed`: asserts "Minimum questions" in `close-request.py`.

Run `pytest tests/test_analysis_prompt_structure.py` to confirm all new tests pass and existing tests are unaffected.

#### Done criteria
- All 8 new test methods pass.
- All previously passing tests in `test_analysis_prompt_structure.py` continue to pass.
- `pytest tests/` exits with code 0.

#### Dependencies
Tasks 1–4 must be complete.

#### Risk notes
None — tests are additive; no existing tests are modified.

---

### Task 6: Update documentation

#### Intent
Update `context.md` to reflect the new mandatory analysis section list and the minimum-questions option, and update any other documentation files affected by this request.

#### Outputs
`.aib_memory/context.md` — updated FR-004 description and Component Map entries

#### Procedure
Open `.aib_memory/context.md`.

In the FR-004 entry, replace the list of 9 mandatory analysis sections with the new list of 7 sections: Executive Summary (with Files Read sub-section), Research Results, Best Practices, External Benchmarking, Minimal Spikes and Experiments, Implementation Alternatives, AI Copilot Suggestions.

In the FR-007 entry, add a sentence describing the minimum-questions option: "A `Minimum questions:` option in `input.md ## Options` (default 0) sets a floor for the number of Q-blocks generated per analysis run; the AI generates at least this many Q-blocks when genuine decision points exist."

In the Component Map, update the "Input Channel" row to mention the minimum-questions option in the `## Options` description.

Verify that no other `context.md` entry references the removed sections by name.

**Acceptance test:** `grep -i "Domain Knowledge Essentials\|Technical Knowledge & Terms\|Multi-Perspective Stakeholder Review" .aib_memory/context.md` returns no matches after the update (except within archived or historical references). `grep "Best Practices\|Implementation Alternatives" .aib_memory/context.md` returns at least one match each.

#### Done criteria
- FR-004 lists 7 mandatory analysis sections.
- FR-007 mentions the minimum-questions option.
- Component Map Input Channel entry mentions minimum-questions option.
- No surviving references to Domain Knowledge Essentials, Technical Knowledge & Terms, or Multi-Perspective Stakeholder Review remain in `context.md` (outside archived historical content).

#### Dependencies
Tasks 1–5 must be complete (document the final implemented state, not an intermediate state).

#### Risk notes
`context.md` is auto-generated by `aib-context.md`; manual edits will be overwritten on the next context regeneration run. This is acceptable for the current iteration — the next context run will pick up the convention and prompt changes and regenerate accurately.

## Documentation

- `.aib_memory/context.md` — FR-004 mandatory section list is stale (lists 9 sections; must be updated to 7); FR-007 does not mention the minimum-questions option; Component Map Input Channel entry does not mention the minimum-questions option.

## Questions & Decisions


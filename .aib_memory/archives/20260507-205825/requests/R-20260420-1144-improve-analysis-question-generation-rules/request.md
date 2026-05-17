## Goal

Improve the `aib-analysis.md` prompt's question-generation behavior by:

- Introducing a 5-level severity threshold for Q-block generation: only decision points rated at or above the configured threshold are surfaced to the user; lower-rated decisions are resolved autonomously by the AI with inline reasoning.
- Adding a mandatory documentation pre-check that explicitly prohibits raising Q-blocks for questions already answerable from `context.md`, convention files, or any file in the required-read set derived from `references.md`.
- Adding a configurable question severity threshold (scale 1–5, default 3) stored in `input.md ## Options`, so the developer can raise or lower the bar for when questions are surfaced.
- Documenting the five severity categories with concrete examples and boundary definitions in `.aib_brain/README.md` so the threshold is objectively interpretable by any AI model.
- Adding a new mandatory "AI Copilot Suggestions" section to the analysis document format (`analysis-convention.md`) and populating it in the `aib-analysis.md` prompt — providing a sincere, pragmatic, senior-expert-level review of the request, not consumed by `implement`.
- Restructuring the analysis and request conventions to move `## Testing`, `## Minimal Spikes and Experiments`, and `## Multi-Perspective Stakeholder Review` from `request.md` into `analysis.md`, keeping `request.md` focused on specification content; the `request.md` plan gains a mandatory task for automated testing steps, and manual testing triggers a `UAT_scenarios.md` file in the request folder.
- Adding a mandatory plan task in every `request.md` to update `context.md` and all editable documents listed in `references.md` during implementation, reflecting changes made and any discovered discrepancies.

## Background

The current `aib-analysis.md` prompt includes a rule for `## Questions & Decisions` that states questions are added "only when the analysis identifies unknowns or decision forks that cannot be resolved through research." This guidance, while directionally correct, lacks:

- An explicit numeric severity scale that allows the developer to tune when questions are surfaced.
- A prohibition on Q-blocks for questions already answered in available workspace documentation (`context.md`, convention files, required-read set).
- A way for the developer to control the threshold interactively from the menu without editing files manually.

The user's input specifies:
1. Add a 1–5 severity scale; document the categories in README; reflect them in the prompt with clear boundaries.
2. Explicitly prohibit Q-blocks answerable from `context.md` or convention files.
3. Add an "AI Copilot Suggestions" section to analysis.md — a sincere, pragmatic, expert-level review not consumed by `implement`.
4. Move `## Testing`, `## Minimal Spikes and Experiments`, and `## Multi-Perspective Stakeholder Review` from `request.md` to `analysis.md`; update conventions accordingly.
5. `request.md` Plan shall include a mandatory testing task (automated test steps; if manual testing is needed, create `UAT_scenarios.md` in the request folder); reflect in `context.md` and `README.md`.
6. `request.md` Plan shall include a mandatory task to update `context.md` and all editable documents in `references.md` during implementation.

## Scope

- `.aib_brain/prompts/aib-analysis.md` — Replace the current `## Questions & Decisions` section rule with a 5-level severity threshold rule:

  - Define five numbered severity levels (1–5) with concrete decision-type examples per level.

  - Read the active threshold value from `input.md ## Options` (the `Question threshold` checkbox row) before generating Q-blocks; default to 3 if the row is absent or unparseable.

  - MUST raise a Q-block for any decision rated at or above the threshold.

  - MUST NOT raise a Q-block for any decision rated below the threshold; instead, select the best option and document the reasoning inline in the relevant `request.md` section.

  - Add a mandatory pre-check: before creating any Q-block, verify the answer is not already determinable from `context.md`, convention files, or any file in the required-read set derived from `references.md`; if found, apply directly — MUST NOT create a Q-block.

  - Update the hardcoded `input.md` seed template string inside `aib-analysis.md` to include the `Question threshold` checkbox row (default `[x] 3`) in the `## Options` section.

- `.aib_brain/conventions/analysis-convention.md` — Add section 7 "AI Copilot Suggestions" as a mandatory section with defined structure: sincere, pragmatic, senior-expert-level review of the request covering improvement opportunities and pitfalls to avoid.

- `.aib_brain/conventions/analysis-convention.md` — Move `## Minimal Spikes and Experiments`, `## Testing`, and `## Multi-Perspective Stakeholder Review` from `request.md` format to the analysis document format. Define them as mandatory sections in `analysis-convention.md`. Remove them from the `request.md` convention (`request-convention.md`).

- `.aib_brain/prompts/aib-analysis.md` — Add a generation task for the "AI Copilot Suggestions" section to Part 1 output (analysis.md); this section is reasoning-only and MUST NOT be read by `implement`.

- `.aib_brain/prompts/aib-analysis.md` — Update Part 2 output rules: remove generation of `## Testing` and `## Multi-Perspective Stakeholder Review` sections from `request.md`; add generation of these sections and `## Minimal Spikes and Experiments` to the Part 1 (analysis.md) output. The plan task in `request.md` must include mandatory automated testing steps. If manual testing is required, `aib-analysis.md` must create `UAT_scenarios.md` in the request folder.

- `.aib_brain/prompts/aib-analysis.md` — Add a mandatory plan task (to be generated in every `## Plan` in `request.md`) for updating `context.md` and all editable documents listed in `references.md` during implementation — to reflect changes made and any discovered discrepancies towards the real state of the workspace.

- `.aib_brain/conventions/request-convention.md` — Remove `## Testing` and `## Multi-Perspective Stakeholder Review` from the mandatory sections list (sections 9 and 14); update numbering and descriptions accordingly. Add requirement that `## Plan` must include a mandatory automated-testing task and a mandatory context/docs update task.

- `.aib_brain/tools/initialize.py` — Update the hardcoded `input_seed` string to include the `Question threshold` checkbox row (default `[x] 3`) in the `## Options` section.

- `.aib_brain/README.md` — Add a "Question Threshold" section documenting the 5-level severity scale with boundary definitions and at least one concrete decision example per level.

- `.aib_brain/README.md` and `.aib_memory/context.md` — Reflect the existence of `UAT_scenarios.md` as an optional request folder artifact (created when manual testing is required).

## Out of scope

- Changes to `aib-implement.md`, `aib-context.md`, or any prompt file other than `aib-analysis.md`.
- Changes to tool scripts other than `initialize.py`.
- Changes to the Q-block format (`Q<nnn>` with checkboxes and `> Answer:` field).
- Changes to the re-run merging rules for answered/unanswered Q-blocks.
- Persistent cross-session storage of the threshold beyond `input.md` (no new config file, database, or registry entry).
- Automated migration of existing analysis.md files to add the "AI Copilot Suggestions" section or relocated sections retroactively.
- Changes to `menu.py` (threshold display/control in the menu is deferred; `input.md` evidence is sufficient for threshold management).

## Constraints

- The `aib-analysis.md` prompt must remain model-agnostic; no references to specific AI models or vendor capabilities.
- The modifications must not alter the existing Q-block format or the re-run merging rules (answered questions applied and removed; unanswered questions preserved).
- No new convention files, template files, or tool scripts are to be created.
- The threshold value must be stored in `input.md ## Options` using the same checkbox format as existing options, so it is reset to default (3) each time analysis completes and input.md is reset.
- The "AI Copilot Suggestions" section in `analysis.md` is a reasoning artifact only; it MUST NOT contain implementation steps or prescriptive instructions that could serve as a specification for `implement`.
- All tool script changes must remain compatible with Python 3.10+ and the standard library only.
- `request-convention.md` must be updated to remove `## Testing` and `## Multi-Perspective Stakeholder Review` as mandatory sections in `request.md`; no other convention file is removed or renamed.
- The mandatory plan tasks (automated testing task, context/docs update task) must be reflected in `request-convention.md` as required schema elements of `## Plan`.

## Success criteria

- The `aib-analysis.md` prompt reads the threshold value from `input.md ## Options` and applies it when deciding whether to generate a Q-block.
- The prompt contains an explicit 5-level severity scale where each level has a definition and at least one concrete example.
- The prompt contains an explicit pre-check rule that prohibits Q-blocks for questions answerable from existing workspace documentation.
- Re-run behaviour for existing answered/unanswered Q-blocks is unchanged.
- When analysis resets `input.md`, the threshold row is present in `## Options` with default value `[x] 3`.
- `initialize.py` seeds `input.md` with the threshold row at default value `[x] 3`.
- `.aib_brain/README.md` documents all 5 threshold categories with at least one concrete example per level.
- `analysis-convention.md` defines "AI Copilot Suggestions" as a mandatory section and includes `## Minimal Spikes and Experiments`, `## Testing`, and `## Multi-Perspective Stakeholder Review` as mandatory analysis sections.
- `request-convention.md` no longer lists `## Testing` and `## Multi-Perspective Stakeholder Review` as mandatory sections; `## Plan` schema requires a mandatory automated-testing task and a mandatory context/docs update task.
- Every analysis run produces a non-empty "AI Copilot Suggestions" section, a `## Testing` section, and a `## Multi-Perspective Stakeholder Review` section in `analysis.md`.
- When manual testing is required, `aib-analysis.md` creates `UAT_scenarios.md` in the request folder.
- `context.md` and `.aib_brain/README.md` document `UAT_scenarios.md` as an optional request folder artifact.
- Every `request.md` `## Plan` generated by `aib-analysis.md` includes: (a) a mandatory testing task with automated test steps, and (b) a mandatory task to update `context.md` and editable documents from `references.md`.
- `implement` does not read `analysis.md` (existing behavior preserved).

## Assumptions

- A1: Five severity levels (1–5) with concrete examples per level provide sufficient coverage to classify any practical decision point encountered during analysis without requiring subjective judgment beyond the level definitions.
  - Risk if false: Edge-case decisions may be classifiable under multiple levels, leading to inconsistent threshold application; additional clarifying examples in the README can mitigate this.

- A2: The mandatory pre-check against available documentation can be reliably executed by reading `context.md` and the required-read set before generating Q-blocks. Documentation coverage is sufficient to suppress most non-significant decision forks.
  - Risk if false: Incomplete or ambiguous workspace documentation may cause the pre-check to incorrectly suppress questions the developer would want answered, or fail to suppress questions that ARE documented.

- A3: The change to both `aib-analysis.md` and `analysis-convention.md` is required to introduce the "AI Copilot Suggestions" section consistently; the convention defines the structure, the prompt generates the content.
  - Risk if false: N/A — confirmed by scope; both files must be updated together.

- A4: Storing the threshold as a checkbox row in `input.md ## Options` (format: `- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5`) allows `aib-analysis.md` (AI reading verbatim) to reliably extract the current value. Fallback default of 3 is used when the row is absent or unparseable.
  - Risk if false: If `input.md` is manually edited with an invalid format, threshold parsing may fail silently; the fallback to 3 limits impact.

- A5: Moving `## Testing`, `## Minimal Spikes and Experiments`, and `## Multi-Perspective Stakeholder Review` from `request.md` to `analysis.md` does not break existing implement runs, because `implement` already does not read `analysis.md` and reads only `request.md`.
  - Risk if false: If any undiscovered prompt or tool reads analysis sections from `request.md` directly, it would need updating; workspace scan shows no such dependency.

- A6: A mandatory plan task for updating `context.md` and editable documents from `references.md` can be generated consistently by the AI on every analysis run without requiring user input, since the list of editable documents is fully determinable from `references.md` at analysis time.
  - Risk if false: If `references.md` contains stale or incomplete entries, the generated update task may miss documents; the developer should keep `references.md` current.

- A7: Creating `UAT_scenarios.md` in the request folder when manual testing is required is deterministically decidable by the AI from the request scope (e.g., presence of UI changes, end-user workflows, or non-automatable outcomes).
  - Risk if false: Edge cases where the AI incorrectly classifies testing type may result in missing or unnecessary UAT files; a simple rule ("if any test case cannot be expressed as a script assertion, create UAT_scenarios.md") provides sufficient boundary.

## Plan

### Task 1: Update Q&D threshold rule in `aib-analysis.md`
**Intent:** Replace the current binary significant/minor rule in the `### Section: ## Questions & Decisions` block with a 5-level severity threshold rule and documentation pre-check.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` (current content), `.aib_brain/README.md` (threshold category definitions — must be written in Task 4 first, or drafted in parallel)
**Outputs:** `.aib_brain/prompts/aib-analysis.md` (updated `## Questions & Decisions` rule block)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Read `.aib_brain/prompts/aib-analysis.md` in full.
2. Locate the `### Section: ## Questions & Decisions` block inside the `Output — Part 2` area.
3. Replace the rule text with: (a) mandatory pre-check — verify answer is not present in `context.md`, convention files, or required-read set; if found, apply directly and MUST NOT create a Q-block; (b) threshold read — read `Question threshold` row from `input.md ## Options`; extract checked value; default to 3 if absent; (c) 5-level severity scale with boundary definitions and examples per level; (d) decision rule — MUST raise Q-block for severity ≥ threshold; MUST resolve autonomously for severity < threshold; (e) preserve all existing re-run merging rules unchanged.
4. Verify all existing re-run merging rules (answered → apply and remove; unanswered → preserve; conflict flagging) are present word-for-word.
5. Write the updated file.
**Done Criteria:** File contains 5-level severity scale, pre-check rule, threshold read step, and unchanged re-run merging rules. No other sections of `aib-analysis.md` are modified in this task.
**Dependencies:** Task 4 (README threshold definitions — may be drafted in parallel)
**Risk Notes:** Change affects all future analysis runs; test with a dry-run after all tasks complete.

### Task 2: Update `aib-analysis.md` input.md seed template string
**Intent:** Update the hardcoded input.md seed template string in `aib-analysis.md` to include the `Question threshold` checkbox row with default `[x] 3`.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` (current seed template string)
**Outputs:** `.aib_brain/prompts/aib-analysis.md` (updated seed template string in Standard flow final step and Auto-Request Creation Branch step 8)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Search all occurrences of the hardcoded seed template string in `aib-analysis.md`.
2. For each occurrence, append `- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5\n` after the `Skip analysis document generation` line.
3. Write the updated file.
**Done Criteria:** All seed template string occurrences in `aib-analysis.md` include the `Question threshold` line with default `[x] 3`. No other content changed.
**Dependencies:** Task 1
**Risk Notes:** Multiple occurrences must all be updated consistently.

### Task 3: Add "AI Copilot Suggestions" generation to `aib-analysis.md`
**Intent:** Add a generation instruction for the "AI Copilot Suggestions" section to the Part 1 output definition in `aib-analysis.md`.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` (current Part 1 output section), `.aib_brain/conventions/analysis-convention.md` (section definition)
**Outputs:** `.aib_brain/prompts/aib-analysis.md` (updated Part 1 output section)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Locate the `Output — Part 1: Analysis file` section in `aib-analysis.md`.
2. Add a generation instruction for `## AI Copilot Suggestions`.
3. Add generation instructions for `## Minimal Spikes and Experiments`, `## Testing`, and `## Multi-Perspective Stakeholder Review` as Part 1 (analysis.md) outputs.
4. Update Part 2 rules: remove generation of `## Testing` and `## Multi-Perspective Stakeholder Review` from `request.md`. Add: if manual testing is required, create `UAT_scenarios.md` in the request folder.
5. Add to the `### Section: ## Plan` rule: (a) every plan MUST include a mandatory automated-testing task; (b) every plan MUST include a mandatory task to update `context.md` and all editable documents in `references.md`.
6. Write the updated file.
**Done Criteria:** `aib-analysis.md` Part 1 references generation of all 4 new sections. Part 2 no longer generates `## Testing` and `## Multi-Perspective Stakeholder Review` in `request.md`. Plan schema includes 2 mandatory tasks.
**Dependencies:** Task 2, Task 5
**Risk Notes:** Must not add any text that could be interpreted as implementation instructions.

### Task 4: Update `.aib_brain/README.md` with threshold categories and UAT_scenarios reference
**Intent:** Add a "Question Threshold" section to `.aib_brain/README.md` documenting the 5-level severity scale; add a note about `UAT_scenarios.md` as an optional request artifact.
**Inputs:** `.aib_brain/README.md` (current content)
**Outputs:** `.aib_brain/README.md` (updated with new sections)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Read `.aib_brain/README.md` in full.
2. Append a new section "## Question Threshold" with: introduction, 5-level table (Level 1–5, each with definition, AI behavior, concrete example), and reset behavior note.
3. In the request artifacts description (or a suitable existing section), add a note: "`UAT_scenarios.md` — created in the request folder by `aib-analysis.md` when the request requires manual testing scenarios that cannot be expressed as automated assertions."
4. Write the updated file.
**Done Criteria:** README contains all 5 level definitions with examples, reset behavior documented, and `UAT_scenarios.md` referenced. No existing content removed.
**Dependencies:** None
**Risk Notes:** None.

### Task 5: Update `analysis-convention.md` — add mandatory sections
**Intent:** Add "AI Copilot Suggestions", `## Testing`, `## Minimal Spikes and Experiments`, and `## Multi-Perspective Stakeholder Review` as mandatory analysis sections; add UAT_scenarios reference.
**Inputs:** `.aib_brain/conventions/analysis-convention.md` (current content, sections 1–6)
**Outputs:** `.aib_brain/conventions/analysis-convention.md` (updated with new mandatory sections)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Read `analysis-convention.md` in full.
2. In the Mandatory Structure list, add: `7. **AI Copilot Suggestions** [REQ]`, `8. **Testing** [REQ]`, `9. **Multi-Perspective Stakeholder Review** [REQ]`. (Note: `Minimal Spikes and Experiments` is already section 6.)
3. Add subsection definitions for sections 7, 8, 9 with: purpose, required content, tone/format, and restrictions.
4. For section 8 (`## Testing`): include rule that if any test case requires manual execution, `UAT_scenarios.md` MUST be created in the request folder.
5. Write the updated file.
**Done Criteria:** `analysis-convention.md` lists all mandatory sections including the new ones; definitions are present with content requirements.
**Dependencies:** None
**Risk Notes:** Changing the convention affects all future analysis runs.

### Task 6: Update `request-convention.md` — remove relocated sections, update Plan schema
**Intent:** Remove `## Testing` and `## Multi-Perspective Stakeholder Review` from `request.md` mandatory sections; update Plan schema to require automated-testing task and context/docs update task.
**Inputs:** `.aib_brain/conventions/request-convention.md` (current content)
**Outputs:** `.aib_brain/conventions/request-convention.md` (updated)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Read `request-convention.md` in full.
2. Remove sections 9 (`## Testing`) and 14 (`## Multi-Perspective Stakeholder Review`) from the mandatory sections list; renumber remaining sections.
3. In the `## Plan` section description, add: "Every plan MUST include: (a) a task defining automated test steps for the request scope; (b) a task to update `context.md` and all editable documents listed in `references.md`, reflecting changes made and any discovered discrepancies."
4. Write the updated file.
**Done Criteria:** `request-convention.md` no longer lists `## Testing` or `## Multi-Perspective Stakeholder Review`; Plan schema requirement is added. Mandatory section count decremented by 2.
**Dependencies:** Task 5 (analysis-convention must add them before request-convention removes them)
**Risk Notes:** Any existing closed `request.md` files still have the old sections — this is acceptable (backward compatibility not required for historical artifacts).

### Task 7: Update `initialize.py` — input.md seed
**Intent:** Update the hardcoded `input_seed` string in `initialize.py` to include the `Question threshold` checkbox row at default `[x] 3`.
**Inputs:** `.aib_brain/tools/initialize.py` (current `input_seed` string)
**Outputs:** `.aib_brain/tools/initialize.py` (updated `input_seed`)
**External Interfaces:** None
**Environment & Configuration:** Python 3.10+, standard library only
**Procedure:**
1. Read `.aib_brain/tools/initialize.py`.
2. Locate the `input_seed` string definition.
3. Append `"- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5\n"` after the `Skip analysis document generation` line.
4. Write the updated file.
**Done Criteria:** Running `initialize.py` on a fresh workspace produces an `input.md` with the `Question threshold` line present in `## Options` with `[x] 3`.
**Dependencies:** None
**Risk Notes:** Must match the seed template format used in `aib-analysis.md` (Task 2) exactly.

### Task 8: Update `context.md`
**Intent:** Regenerate `context.md` to reflect all framework changes made in this request.
**Inputs:** All modified files from Tasks 1–7; `.aib_brain/prompts/aib-context.md`
**Outputs:** `.aib_memory/context.md` (fully replaced)
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. After all Tasks 1–7 are confirmed complete, execute `aib-context.md` to fully regenerate `context.md`.
2. Verify the regenerated `context.md` references: threshold row in `input.md ## Options`, `UAT_scenarios.md` as an optional request artifact, relocated analysis sections (`## Testing`, `## Multi-Perspective Stakeholder Review`), and updated mandatory plan tasks.
**Done Criteria:** `context.md` is regenerated and accurately reflects the updated framework state.
**Dependencies:** Tasks 1–7
**Risk Notes:** If `aib-context.md` is not invoked, `context.md` will be stale; stale context affects next analysis run's pre-check accuracy.

## Testing

- T1 — 5-level severity scale in prompt: Inspect `.aib_brain/prompts/aib-analysis.md` after Task 1. Expected outcome: File contains definitions for all 5 levels with examples, the pre-check rule, and the threshold read step.

- T2 — Seed template threshold row in aib-analysis.md: Inspect all hardcoded seed template occurrences in `aib-analysis.md` after Task 2. Expected outcome: Each occurrence contains `- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5`.

- T3 — AI Copilot Suggestions in analysis.md: Run `aib-analysis.md` on any request after Tasks 3 and 5. Expected outcome: `analysis.md` contains a non-empty `## AI Copilot Suggestions` section.

- T4 — Testing section in analysis.md (not in request.md): Run `aib-analysis.md` after Task 3. Expected outcome: `analysis.md` contains `## Testing`; `request.md` does NOT contain a `## Testing` section.

- T5 — Multi-Perspective Stakeholder Review in analysis.md: Run `aib-analysis.md` after Tasks 3 and 5. Expected outcome: `analysis.md` contains `## Multi-Perspective Stakeholder Review`; `request.md` does NOT contain this section.

- T6 — Mandatory plan tasks present: Run `aib-analysis.md` on any request. Expected outcome: `request.md ## Plan` includes a task for automated testing and a task for updating `context.md` and editable docs.

- T7 — UAT_scenarios.md created when manual testing required: Run `aib-analysis.md` on a request that includes UI or user-interaction changes. Expected outcome: `UAT_scenarios.md` is created in the request folder.

- T8 — Threshold reset after analysis: Run analysis with threshold set to 4 in `input.md`. Expected outcome: After analysis resets `input.md`, `input.md ## Options` contains `[x] 3` in the `Question threshold` line.

- T9 — initialize.py seed includes threshold: Run `initialize.py` on a fresh workspace. Expected outcome: `.aib_memory/input.md ## Options` contains `- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5`.

- T10 — request-convention.md updated: Inspect `request-convention.md` after Task 6. Expected outcome: `## Testing` and `## Multi-Perspective Stakeholder Review` are not listed as mandatory sections; Plan schema references mandatory testing and context-update tasks.

- T11 — README threshold documentation: Inspect `.aib_brain/README.md` after Task 4. Expected outcome: All 5 threshold levels are documented with definitions, AI behavior, and at least one concrete example each.

- T12 — context.md regenerated: Run `aib-context.md` after Tasks 1–7. Expected outcome: `context.md` references the threshold row, `UAT_scenarios.md`, and the relocated analysis sections.

## Documentation

- `.aib_brain/prompts/aib-analysis.md` (ref_id: N/A) — Updated with 5-level threshold Q&D rule, pre-check rule, threshold read step, updated seed template, AI Copilot Suggestions generation instruction, relocated sections generation (Testing, Minimal Spikes, Multi-Perspective Stakeholder Review), mandatory plan tasks rule, and UAT_scenarios.md creation rule.
- `.aib_brain/conventions/analysis-convention.md` (ref_id: N/A) — Add mandatory sections: "AI Copilot Suggestions", "Testing", "Multi-Perspective Stakeholder Review"; document UAT_scenarios.md creation rule in the Testing section.
- `.aib_brain/conventions/request-convention.md` (ref_id: N/A) — Remove `## Testing` and `## Multi-Perspective Stakeholder Review` from mandatory sections; update Plan schema to require automated-testing task and context/docs update task.
- `.aib_brain/tools/initialize.py` (ref_id: N/A) — Update `input_seed` string to include threshold row.
- `.aib_brain/README.md` (ref_id: N/A) — Add "Question Threshold" section with 5-level category documentation; add `UAT_scenarios.md` as an optional request artifact reference.
- `.aib_memory/context.md` (ref_id: REF-0001) — Regenerated by `aib-context.md` to reflect all framework changes in this request.

## Questions & Decisions

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/prompts/aib-analysis.md` | Modified | Update `## Questions & Decisions` rule with 5-level severity threshold, pre-check rule, threshold read step, updated seed template; add AI Copilot Suggestions, Testing, Multi-Perspective Stakeholder Review, Minimal Spikes generation instructions to Part 1; remove Testing and Multi-Perspective Stakeholder Review from Part 2; add mandatory plan tasks rule; add UAT_scenarios.md creation rule |
| `.aib_brain/conventions/analysis-convention.md` | Modified | Add mandatory sections: AI Copilot Suggestions, Testing (with UAT_scenarios.md rule), Multi-Perspective Stakeholder Review |
| `.aib_brain/conventions/request-convention.md` | Modified | Remove `## Testing` and `## Multi-Perspective Stakeholder Review` from mandatory sections; update Plan schema to require automated-testing task and context/docs update task |
| `.aib_brain/tools/initialize.py` | Modified | Update `input_seed` string to include `Question threshold` line |
| `.aib_brain/README.md` | Modified | Add "Question Threshold" section with 5-level category documentation; add `UAT_scenarios.md` reference |
| `.aib_memory/context.md` | Modified (runtime) | Regenerated via `aib-context.md` to reflect all framework changes |
| `.aib_memory/input.md` | Modified (runtime) | Threshold row added to `## Options`; value reset to `[x] 3` after each analysis run |
| `<request-folder>/UAT_scenarios.md` | Created (conditional) | Created in request folder when request requires manual testing scenarios |

## Internal Review of Request and Product Docs

- OK: `.aib_brain/prompts/aib-analysis.md` — The current `## Questions & Decisions` rule provides the base text to replace; the prompt already has a hardcoded seed template string that must be updated consistently in all occurrences. The Part 1/Part 2 distinction is clearly maintained and supports the section relocation.
- OK: `analysis-convention.md` — Currently defines 6 mandatory sections; adding sections 7, 8, 9 is additive. Existing section numbering is unaffected; `## Minimal Spikes and Experiments` is already section 6 (no move needed, only confirmation it stays).
- OK: `request-convention.md` — Currently defines 14 mandatory sections including `## Testing` (section 9) and `## Multi-Perspective Stakeholder Review` (section 14). Removing them and renumbering reduces mandatory sections to 12. Plan schema update is additive.
- Ambiguity: `request.md` Scope — The threshold read step in the prompt must specify a deterministic fallback (default=3) for when the threshold row is absent or malformed; addressed in A4.
- Cross-ref issue: `context.md` — The current `context.md` references 14 mandatory sections for `request.md` and 6 for `analysis.md`; after implementation, both counts change. Task 8 (context.md regeneration) covers this.
- Cross-ref issue: `Concepts.md` / `initialize.py` — The seed template in `initialize.py` and the seed template string in `aib-analysis.md` must be kept identical; both must be updated in Task 2 and Task 7.
- OK: `menu.py` — No changes to `menu.py` in this request (deferred); no impact on existing keyboard handling.
- OK: `request-convention.md` — Q-block format and re-run merging rules are preserved unchanged; no conflict with this request.
- Missing info: No automated test suite covers `aib-analysis.md` prompt behavior directly; testing is necessarily manual/observational for most test cases. Automated tests cover `initialize.py` output format.

## Multi-Perspective Stakeholder Review

**Senior Solution Architect**

The expanded request spans five files across three components (prompt, convention, tool scripts) and introduces a configuration channel via `input.md`, making it architecturally more significant than the original single-file change. The design decision to store the threshold in `input.md ## Options` is architecturally sound: it reuses the existing ephemeral channel, provides automatic reset semantics, and avoids creating a new config file or registry. The risk of seed template drift between `initialize.py` and `aib-analysis.md` is the primary implementation risk and must be enforced in review. The `<`/`>` key extension to `get_key()` is backward-compatible and low-risk.

- Five files changed; no new files created — consistent with Constraints.
- Threshold stored in `input.md` reuses existing lifecycle semantics (reset on analysis) — elegant and low-maintenance.
- Seed template synchronization between `initialize.py` and `aib-analysis.md` is a dual-point-of-change risk; Task 7 should be reviewed together with Task 2.
- `get_key()` extension adds two new return values without altering any existing return path — safe.
- AI Copilot Suggestions section is well-scoped as reasoning-only; no risk of leaking into implementation.

**Product Owner**

The expanded scope addresses three distinct developer pain points: question fatigue (threshold tuning), wasted Q-blocks on already-documented decisions (pre-check), and lack of expert-quality critical feedback on requests (AI Copilot Suggestions). The threshold menu control adds genuine value — developers working on complex architectural requests can lower the threshold to 2 or 1 to receive more questions, while developers on routine changes can raise it to 4 or 5 for fewer interruptions. Success criteria are expanded and objectively testable (T1–T12).

- Business value: high — threshold tuning directly reduces or increases question volume based on developer preference.
- AI Copilot Suggestions fills a genuine gap: no current mechanism provides expert-level critical review of a request before implementation.
- Out-of-scope boundary remains well-defined; scope creep is controlled.
- Risk: 7 tasks across 5 files increase implementation complexity compared to the original 1-task/1-file scope; the implementation effort is still proportionate to the business value.

**User (Developer)**

The developer will experience three improvements: (1) fewer or more questions based on their chosen threshold — controllable from the menu without editing files; (2) no more Q-blocks for decisions already answered in workspace docs; (3) a new "AI Copilot Suggestions" section in every analysis that provides honest, expert feedback on the request before commit. The threshold row in the menu is display-only navigation-wise (not in the UP/DOWN list), which keeps the action selection workflow unchanged while making the threshold clearly visible and controllable.

- Threshold control from the menu removes the need to manually edit `input.md` to change Q-block behavior.
- AI Copilot Suggestions provides value even if no questions are raised — critical review is always present.
- No change to how Q-blocks are answered or how answers are applied — zero learning curve.

**Security Officer**

No new network calls, authentication paths, or secret handling are introduced. The threshold value is stored in a plaintext Markdown file (`input.md`) — acceptable for this configuration type (user preference, non-sensitive). Writing the threshold back to `input.md` in `menu.py` uses the existing `write_text` utility from `common.py`, which overwrites the file atomically and does not create world-readable temp files. The "AI Copilot Suggestions" section contains developer notes only — no PII, credentials, or security-sensitive data is generated.

- No new attack surface introduced.
- `input.md` write in `menu.py` uses the established `write_text` helper — no injection risk.
- Threshold value is a validated integer in range 1–5; out-of-range values are clamped in `choose_action`.
- No change to file permission model or access control.

**Data Governance Officer**

All artifacts remain within the repository workspace — no data leaves the local filesystem. The threshold setting in `input.md` is transient (reset after each analysis run) and contains no personal or business-sensitive data. The "AI Copilot Suggestions" section in `analysis.md` is a reasoning artifact committed to VCS as part of the normal AIB workflow — the same data classification as the existing analysis sections. No new data retention, lineage, or compliance obligations are introduced.

- No new data types or data flows introduced.
- AI Copilot Suggestions follows the same VCS retention policy as other analysis sections.
- Threshold row in `input.md` is reset on each analysis run — no persistent configuration accumulation.
- No regulatory or compliance impact identified.
- Risk: perceived loss of control if threshold is too aggressive. Mitigation: examples in the rule text set clear expectations.
- Overall usability improvement expected.

**Security Officer**

The change is limited to a Markdown prompt file that operates on local filesystem artifacts only. No credentials, external APIs, network calls, or sensitive data flows are introduced or modified. There is no change to the authentication, authorisation, or edit-gating model (references register `edit_allowed` flag remains the control). No attack surface change.

- No credential or token exposure risk.
- No external network calls introduced.
- No change to access control model.
- N/A for compliance or regulatory scope.
- Approved from a security perspective.

**Data Governance Officer**

The change affects AI prompt behaviour only. No data lineage, retention policy, classification schema, or compliance-relevant data flows are modified. The `input.md` archiving lifecycle (archive then reset) is unaffected. The generated artifacts (`request.md`, `analysis.md`) continue to be classified as Internal engineering documentation.

- No data lineage changes.
- No retention policy impact.
- No data classification changes.
- No regulatory or compliance impact.
- N/A for data governance review.

## Goal

Move the Q&A workflow from `request.md` to `input.md`. Instead of generating `## Questions & Decisions` blocks in `request.md`, `aib-analysis.md` must populate `input.md` with AI-generated questions, each accompanied by a recommended answer. The user answers questions in `input.md` and re-runs the analysis prompt, which then reads the answers, applies them to the relevant `request.md` sections, and resets `input.md` to its clean seed state. The `Question threshold` option in `input.md` must be removed as the AI will now decide which questions to generate based on ambiguity and multiplicity of valid choices.

## Background

Currently, `aib-analysis.md` writes `## Questions & Decisions` blocks into `request.md` based on a configurable threshold (`Question threshold` in `input.md`). This forces the developer to navigate to `request.md` to answer questions. The developer prefers questions to appear in `input.md` — already the primary communication channel — making it the single touchpoint for all user interaction with the AI agent. Additionally, the threshold control is considered unnecessary complexity: the AI should decide which questions need human input based on the presence of multiple valid implementation choices where preference matters, not based on a configurable severity level.

## Scope

- Modify `aib-analysis.md` to generate questions in `input.md` instead of in `## Questions & Decisions` in `request.md`, when multiple implementation choices or ambiguities exist that require human preference.

- Each AI-generated question must include: question text, explanation of its meaning and impact, a set of mutually exclusive options with descriptions, and a clearly marked recommended answer.

- If the user leaves a question unanswered (no option selected, no free-text answer), the recommended answer must be treated as the chosen option on re-run.

- Questions must be generated only for cases with multiple valid choices where human preference materially affects the implementation. Minor differences with no meaningful implementation impact must not be raised as questions; the AI resolves them autonomously.

- All ambiguity and uncertainty in the active request must be covered by questions, unless already answered in `context.md`, convention files, or other referenced documents.

- Soft limit of 9 questions per run; may be exceeded when strictly necessary.

- One cycle of Q&A assumed: after all questions are answered, no further questions are generated on re-run.

- On re-run of `aib-analysis.md` after user answers questions in `input.md`, the prompt applies answers to the relevant `request.md` sections and resets `input.md` to the clean seed state.

- Remove the `Question threshold` row from all locations where `input.md` is seeded or reset: `initialize.py`, `aib-analysis.md` (standard flow reset and auto-request branch reset), `close-request.py`.

- Remove the Question threshold-related reading and decision logic from `aib-analysis.md`.

- Update `README.md` (`.aib_brain/README.md`) to remove the `Question threshold` section and document the new Q&A workflow in `input.md`.

- Update `context.md` and any other documentation files to reflect the removed threshold and the new questions-in-input.md approach.

## Out of scope

- Changes to `aib-implement.md` behavior beyond what is needed to align with the new input.md seed template.

- Changes to `close-request.py` beyond updating the `input.md` reset template (no question threshold row).

- Changes to `analysis-convention.md` section structure or mandatory section list.

- Retroactive modification of archived `request.md` files in closed request folders.

- Changes to `aib-context.md` prompt logic.

## Constraints

- All Q&A interaction must continue to go through `input.md` as the single user-facing file.

- The `input.md` seed template (produced by `initialize.py` and used in all reset actions) must be updated to remove the `Question threshold` row and be backward compatible with the new Q&A section structure.

- Python 3.10+ standard library only for any tool script changes.

- All prompt behavioral changes must be in `.aib_brain/` files only; no changes to workspace-level `README.md` (root).

- Backward compatibility: existing Closed requests with `## Questions & Decisions` in archived `request.md` files are not modified.

- The existing Q-block format (`**Q<nnn>**:`, checkbox options, `*(recommended)*` marker, `> Answer:` field) must be reused for questions placed in `input.md` to minimise format divergence.

## Success criteria

- SC-1: Running `aib-analysis.md` on a new request populates `input.md` with AI-generated questions (in a dedicated `## Questions` section) when multiple valid implementation choices exist; no `## Questions & Decisions` blocks are written to `request.md`.

- SC-2: Each question in `input.md` includes an explanation of its meaning and impact, a set of options, and a `*(recommended)*` marker on the preferred option; if the user leaves the question unanswered on re-run, the recommended option is applied.

- SC-3: On re-run of `aib-analysis.md` after user answers questions in `input.md`, the prompt applies answers to the relevant `request.md` sections and resets `input.md` to the clean seed (no `## Questions` section, no threshold row).

- SC-4: The `Question threshold` row is absent from the `input.md` seed template in `initialize.py` and from all reset actions in `aib-analysis.md` and `close-request.py`.

- SC-5: `.aib_brain/README.md` is updated: the `Question threshold` section is removed and the new Q&A workflow is documented.

- SC-6: The automated test suite passes without regressions.

- SC-7: `context.md` reflects the removal of the threshold and the new questions-in-input.md workflow.

## Assumptions

- A1: The `## Questions` section in `input.md` is purely AI-generated and ephemeral — it is never part of the seed template and is fully cleared after each re-run cycle.
  - Risk if false: If developers manually add content to this section, the re-run logic may clear developer-written notes unintentionally.

- A2: The existing Q-block format (`**Q<nnn>**:`, checkbox options, `*(recommended)*` marker, `> Answer:` field) is reused unchanged in `input.md`; a `> **Why this matters:** <text>` sub-element is added below each question header to provide impact context.
  - Risk if false: If a different format is chosen, the re-run answer-detection logic must be redesigned.

- A4: On re-run when `## Questions` is present in `input.md`, the prompt processes ALL Q-blocks regardless of answered/unanswered state; unanswered Q-blocks apply the `*(recommended)*` option. After all blocks processed, the `## Questions` section is cleared.
  - Risk if false: If recommended-default selection is skipped for some blocks, those ambiguities remain unresolved and silently propagate.

- A5: The duplicate `input_seed` strings in `initialize.py` and `close-request.py` are updated independently (no shared constant introduced); this is consistent with the existing code style.
  - Risk if false: Future divergence between the two seed strings would reintroduce the inconsistency this request aims to avoid.

- A6: The test `test_input_md_has_threshold_scale_labels` in `tests/test_initialize.py` is the only test in the `tests/` directory that must be changed; all other existing tests continue to pass without modification.
  - Risk if false: If additional tests assert threshold behavior, they will require updating too.

## Plan

### Task 1: Update `initialize.py` seed template
**Intent:** Remove the `Question threshold` row from the `input_seed` string in `initialize.py`.
**Outputs:** `.aib_brain/tools/initialize.py` — updated `input_seed` string without threshold row.
**Procedure:**
1. Open `.aib_brain/tools/initialize.py`. Locate the `input_seed` variable (line ~84). Remove the line `"- Question threshold: [ ] 1 (all)  [ ] 2  [x] 3  [ ] 4  [ ] 5 (mandatory only)\n"` from the string.
2. Verify the resulting `input_seed` has exactly: `## Active request\n`, `No active request\n\n`, `## Options\n`, `- [ ] No changes — provide answer only\n`, `- [ ] Skip analysis document generation\n\n`, `## Input\n\n`.
**Done Criteria:** `"Question threshold"` does not appear in the `input_seed` string in `.aib_brain/tools/initialize.py`.
**Dependencies:** None.
**Risk Notes:** Two seed strings exist (here and in `close-request.py`); both must match. A3 assumption applies.

### Task 2: Update `close-request.py` seed template
**Intent:** Remove the `Question threshold` row from the `input_seed` string in `close-request.py`.
**Outputs:** `.aib_brain/tools/close-request.py` — updated `input_seed` string without threshold row.
**Procedure:**
1. Open `.aib_brain/tools/close-request.py`. Locate the `input_seed` variable (line ~136). Remove the line `"- Question threshold: [ ] 1 (all)  [ ] 2  [x] 3  [ ] 4  [ ] 5 (mandatory only)\n"` from the string.
2. Verify the resulting seed string is identical to the one produced in Task 1.
**Done Criteria:** `"Question threshold"` does not appear in the `input_seed` string in `.aib_brain/tools/close-request.py`.
**Dependencies:** Task 1 (for consistency verification).
**Risk Notes:** Must be byte-for-byte identical to the Task 1 seed string.

### Task 3: Update `aib-analysis.md` — remove threshold logic
**Intent:** Remove all `Question threshold`-related reading and decision logic from the analysis prompt.
**Outputs:** `.aib_brain/prompts/aib-analysis.md` — threshold row removed from all `input.md` reset seed templates; `Threshold read` instruction removed; 5-Level Severity Scale table and `Decision rule` section removed or replaced with AI-autonomous judgment guidance.
**Procedure:**
1. Open `.aib_brain/prompts/aib-analysis.md`. Search for all occurrences of `Question threshold`. Remove the threshold row from each `input.md` seed template block (standard flow final step and auto-request branch step 8).
2. Remove the `**Threshold read:**` instruction and the `**5-Level Severity Scale:**` table from the `## Questions & Decisions` section generation rules.
3. Remove the `**Decision rule:**` block that gates Q-block creation on threshold ≥ severity.
4. Replace the removed logic with: "Raise a question Q-block for any decision point where multiple valid implementation choices exist and the preferred option has a materially different impact on the codebase; resolve all other ambiguities autonomously."
5. Verify no instance of `"- Question threshold:"` remains in any seed template string within the file.
**Done Criteria:** `grep "Question threshold"` returns no matches in `.aib_brain/prompts/aib-analysis.md` seed template blocks; the 5-Level Severity Scale and Decision rule blocks are absent.
**Dependencies:** None.
**Risk Notes:** This is the highest-complexity task. Multiple locations in the prompt reference the threshold. See AI Copilot Suggestions Observation 1 for the checklist of locations.

### Task 4: Update `aib-analysis.md` — add `## Questions` section logic in `input.md`
**Intent:** Add logic to `aib-analysis.md` so that instead of writing Q-blocks to `request.md ## Questions & Decisions`, it writes them to a `## Questions` section in `input.md`.
**Outputs:** `.aib_brain/prompts/aib-analysis.md` — updated Q-block generation target and answer-application logic.
**Procedure:**
1. Open `.aib_brain/prompts/aib-analysis.md`. In toggle detection (step 5), add a pre-check: if `input.md` contains a `## Questions` section with Q-blocks, enter the "answer application" sub-flow before normal analysis.
2. Define the "answer application" sub-flow: for each Q-block in `## Questions`: if answered (`[x]` or non-empty `> Answer:`), apply the chosen option to the relevant `request.md` section; if unanswered, apply the `*(recommended)*` option. After all blocks processed, remove the `## Questions` section from `input.md`.
3. In the Q-block generation section (Part 2): change the output target from `request.md ## Questions & Decisions` to `input.md ## Questions`. Each Q-block must include a `> **Why this matters:** <impact explanation>` line immediately after the question text.
4. Add instruction: if no Q-blocks are generated (no genuine multi-choice ambiguity), do NOT write a `## Questions` section to `input.md`.
5. Update the final reset step: the `input.md` reset must use the new seed template (no threshold row), which inherently clears the `## Questions` section.
**Done Criteria:** Prompt instructs writing Q-blocks to `input.md ## Questions`; no instruction to write Q-blocks to `request.md`; answer-application logic is defined; recommended-default behavior documented.
**Dependencies:** Task 3.
**Risk Notes:** The "answer application" sub-flow must correctly map Q-block content to `request.md` sections. Mapping logic must be explicit.

### Task 5: Update `tests/test_initialize.py`
**Intent:** Replace the `test_input_md_has_threshold_scale_labels` test with one that asserts the threshold row is absent from the seed.
**Outputs:** `tests/test_initialize.py` — updated test method.
**Procedure:**
1. Open `tests/test_initialize.py`. Locate `test_input_md_has_threshold_scale_labels` (lines ~336–345).
2. Replace the test body: change assertions from `assert "1 (all)" in content` and `assert "5 (mandatory only)" in content` to `assert "Question threshold" not in content`, with docstring updated to reflect the new intent.
3. Rename the test method to `test_input_md_has_no_threshold_row` for clarity.
**Done Criteria:** Running `pytest tests/test_initialize.py -k test_input_md_has_no_threshold_row` passes; the old test name no longer exists.
**Dependencies:** Task 1.
**Risk Notes:** No other tests in `tests/` reference `Question threshold` directly (confirmed by research spike).

### Task 6: Add new test file for R-20260508-0036 success criteria
**Intent:** Create a test file that verifies SC-1 through SC-6 programmatically.
**Outputs:** `tests/test_questions_in_input_md.py` — new test file.
**Procedure:**
1. Create `tests/test_questions_in_input_md.py`. Add tests asserting:
   - `initialize.py` source does not contain `"Question threshold"` in the `input_seed` string (SC-4).
   - `close-request.py` source does not contain `"Question threshold"` in the seed string (SC-4).
   - `.aib_brain/prompts/aib-analysis.md` does not contain `"Question threshold"` in seed template blocks (SC-4 partial).
   - `.aib_brain/prompts/aib-analysis.md` references `"## Questions"` (SC-1).
   - `.aib_brain/README.md` does not contain `"## Question Threshold"` as a section heading (SC-5).
   - `.aib_brain/README.md` contains documentation of the new `input.md` Q&A flow (SC-5).
2. Each test class must have a docstring mapping to the SC it covers.
**Done Criteria:** `pytest tests/test_questions_in_input_md.py` passes with all tests green.
**Dependencies:** Tasks 1–4, 7.
**Risk Notes:** None.

### Task 7: Update `.aib_brain/README.md`
**Intent:** Remove the `## Question Threshold` section and document the new Q&A-in-`input.md` workflow.
**Outputs:** `.aib_brain/README.md` — `## Question Threshold` section removed; new Q&A section added.
**Procedure:**
1. Open `.aib_brain/README.md`. Locate the `## Question Threshold` section (includes the threshold table). Delete the entire section.
2. Add a new `## Questions and Answers` section documenting: (a) when the AI generates a `## Questions` section in `input.md`; (b) how to answer questions; (c) that leaving a question blank applies the recommended default; (d) that re-running analysis applies answers and clears the section.
3. Acceptance test: `grep "## Question Threshold"` in `.aib_brain/README.md` returns no match.
**Done Criteria:** `## Question Threshold` heading absent; new Q&A documentation section present.
**Dependencies:** None (can run in parallel with Tasks 1–6).
**Risk Notes:** README referenced by `test_instructions_md.py` tests; verify those tests still pass after README edits.

### Task 8: Automated test verification run
**Intent:** Confirm the full test suite passes with zero regressions after all code changes.
**Outputs:** Terminal output confirming `pytest tests/` exit code 0.
**Procedure:**
1. From workspace root, run `pytest tests/ -v` in terminal.
2. If failures exist, diagnose and fix in the relevant task's output files before re-running.
3. Confirm `tests/test_initialize.py::test_input_md_has_no_threshold_row` passes.
4. Confirm `tests/test_questions_in_input_md.py` all tests pass.
**Done Criteria:** `pytest tests/` exits with code 0; no test skipped or errored.
**Dependencies:** Tasks 1–7.
**Risk Notes:** `test_instructions_md.py` README tests may fail if README section structure changes unexpectedly.

### Task 9: Update `.aib_memory/context.md` and documentation
**Intent:** Reflect the removal of `Question threshold` and the new questions-in-`input.md` workflow in `context.md`.
**Outputs:** `.aib_memory/context.md` — all threshold references removed; FR-007, AC-1, AC-3, Component Map, and Module Breakdown entries updated.
**Procedure:**
1. Open `.aib_memory/context.md`. Locate FR-007: remove the sentence about the `Question threshold` checkbox row; update toggle description to list only two toggles. Acceptance test: `grep "Question threshold" context.md` returns no match.
2. Locate AC-1: remove `(including the Question threshold row...)`. Acceptance test: sentence no longer references threshold.
3. Locate AC-3: update reset description to remove `(including Question threshold reset to default [x] 3)`. Acceptance test: sentence no longer references threshold reset.
4. Locate the `Input Channel` row in the Component Map table: remove `Question threshold checkbox row format` from description. Acceptance test: `Question threshold` absent from that row.
5. Locate the `aib-analysis.md` bullet in Module Breakdown: update to remove threshold decision logic description; add description of `## Questions` generation in `input.md`. Acceptance test: no threshold references remain.
6. Locate the `initialize.py` bullet: remove the sentence about seeding the threshold row. Acceptance test: no threshold reference.
7. Run `grep "Question threshold" .aib_memory/context.md` to confirm zero remaining matches.
**Done Criteria:** Zero matches for `"Question threshold"` in `.aib_memory/context.md`; updated descriptions accurately reflect the new behavior.
**Dependencies:** Tasks 1–7.
**Risk Notes:** `context.md` is auto-generated by `aib-context.md`; manual edits are interim until next context regeneration.

## Documentation

- `.aib_brain/tools/initialize.py` (ref_id: N/A) — Remove `Question threshold` row from `input_seed`; new seed template must match the revised format.

- `.aib_brain/tools/close-request.py` (ref_id: N/A) — Remove `Question threshold` row from `input_seed`; must remain byte-for-byte identical to `initialize.py` seed.

- `.aib_brain/prompts/aib-analysis.md` (ref_id: N/A) — Remove threshold reading/decision logic; add Q-block generation to `input.md ## Questions`; add answer-application sub-flow on re-run; update all seed template reset strings.

- `.aib_brain/README.md` (ref_id: N/A) — Remove `## Question Threshold` section and table; add new section documenting Q&A-in-`input.md` workflow.

- `tests/test_initialize.py` (ref_id: N/A) — Replace `test_input_md_has_threshold_scale_labels` with `test_input_md_has_no_threshold_row` asserting threshold row is absent.

- `tests/test_questions_in_input_md.py` (ref_id: N/A) — New test file verifying SC-1 through SC-6.

- `.aib_memory/context.md` (ref_id: N/A) — Remove all `Question threshold` references; update FR-007, AC-1, AC-3, Component Map, and Module Breakdown entries.

## Questions & Decisions

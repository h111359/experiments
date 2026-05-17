## Goal

Improve human readability of `request.md` files by reformatting plan task fields as markdown sub-headers, adding empty lines between sections and procedure steps, and applying broader formatting improvements throughout the file.

## Background

The current `request.md` format uses bold inline labels (`**Intent:**`, `**Outputs:**`, `**Procedure:**`, `**Done Criteria:**`, `**Dependencies:**`, `**Risk Notes:**`) for plan task sub-fields. These dense labels collapse into visually monolithic blocks that are hard to scan. Procedure steps have no spacing between them, increasing reading friction. The developer has identified the file as difficult to read by humans and requested both targeted and broader formatting improvements.

## Scope

- Update the plan task schema in `.aib_brain/conventions/request-convention.md` to use level-4 markdown headers (`####`) instead of bold labels for task sub-fields (Intent, Outputs, Procedure, Done Criteria, Dependencies, Risk Notes).

- Update the plan task schema in `.aib_brain/prompts/aib-analysis.md` to match the new header-based format.

- Add an explicit requirement for empty lines between procedure steps in `.aib_brain/conventions/request-convention.md` and `.aib_brain/prompts/aib-analysis.md`.

- Prohibit markdown tables in `request.md` in the convention and prompt.

- Propose and document additional readability improvements (e.g., top-level section spacing, list formatting consistency) in `.aib_brain/conventions/request-convention.md`.

- Update automated tests in `tests/test_analysis_prompt_structure.py` to reflect the new schema field format.

## Out of scope

- Changes to `analysis-convention.md` or `analysis.md` artifact format.
- Changes to `implementation.md` format.
- Changes to `context.md` format or `context-convention.md`.
- Retroactive reformatting of archived (closed) `request.md` files.
- Python tool script changes.

## Constraints

- All 10 mandatory sections must continue to be present in `request.md`.
- Changes to the plan schema must not break the deterministic AI generation of `request.md`.
- Test updates must cover both the new formatting expectations and confirm no regressions.
- Must not alter request lifecycle semantics or register behavior.

## Success criteria

- All plan task sub-fields use level-4 markdown headers (`####`) in the convention and prompt schema.
- Procedure steps within plan tasks are separated by empty lines.
- The convention explicitly prohibits markdown tables in `request.md`.
- Top-level sections are separated by consistent empty lines.
- Tests in `tests/test_analysis_prompt_structure.py` pass with assertions updated for the new schema.
- `.aib_brain/conventions/request-convention.md` reflects the new formatting standard.
- `.aib_brain/prompts/aib-analysis.md` generates conformant output per the updated convention.

## Assumptions

- A1: The plan task schema embedded in `aib-analysis.md` is the canonical source for generated `request.md` Plan sections; updating it and `request-convention.md` together is sufficient to change all future output.
  - Risk if false: If other prompts or tools also embed the schema, they would need updating too.

- A2: Level-4 headings (`####`) are the correct heading level for plan task sub-fields — they sit below `### Task N` (level 3) and do not conflict with any existing heading hierarchy in `request.md`.
  - Risk if false: If some rendering environment treats `####` headings as visually too prominent or too small, a different level or format may be preferred.

- A3: The existing positive test assertion `assert "**Outputs:**" in content` in `test_analysis_prompt_structure.py` must be replaced (not supplemented) with an equivalent `#### Outputs` assertion, since the bold-label format will be removed.
  - Risk if false: If `**Outputs:**` is retained alongside `#### Outputs`, the old test would not fail, but the convention would be inconsistent.

- A4: No currently active or in-progress `request.md` files need to be reformatted as part of this change; only future-generated files are affected.
  - Risk if false: If the team expects retroactive reformatting, additional scripting would be required.

- A5: "Propose other formatting improvements" in the developer's input is bounded to the Plan section improvements already identified; no open-ended refactoring of other sections is expected.
  - Risk if false: If the developer expects broader improvements, additional analysis would be needed.

## Plan

### Task 1: Update plan schema in `request-convention.md`

#### Intent

Replace bold inline labels with level-4 markdown headers and add empty-line spacing rules in the Plan section of `request-convention.md`.

#### Outputs

Updated `.aib_brain/conventions/request-convention.md` with:
- Level-4 headings (`####`) for all six plan task sub-fields.
- Explicit rule requiring one empty line between consecutive procedure steps.
- Explicit rule prohibiting markdown tables in `request.md`.
- Explicit rule requiring one empty line between consecutive `### Task N` blocks.

#### Procedure

1. Open `.aib_brain/conventions/request-convention.md` and locate the Plan task schema block (currently using bold labels).

2. Replace each bold label in the schema template (`**Intent:**`, `**Outputs:**`, `**Procedure:**`, `**Done Criteria:**`, `**Dependencies:**`, `**Risk Notes:**`) with the corresponding level-4 heading (`#### Intent`, `#### Outputs`, `#### Procedure`, `#### Done criteria`, `#### Dependencies`, `#### Risk notes`).

3. Add an explicit formatting rule in the Formatting Rules section of `.aib_brain/conventions/request-convention.md` stating that: one blank line separates each `### Task N` block from the next; one blank line separates each `####` sub-field from its content; and procedure steps are separated by one blank line.

4. Add a rule to the Formatting Rules section of `.aib_brain/conventions/request-convention.md` explicitly prohibiting markdown tables in `request.md`.

5. Re-read `.aib_brain/conventions/request-convention.md` and verify the schema block uses only `####` labels and the new rules are present.

#### Done Criteria

- The Plan schema block in `request-convention.md` uses `####` headings.
- No bold inline label (`**Intent:**` etc.) remains in the schema block.
- Empty-line and table-prohibition rules are present in the Formatting Rules section.

#### Dependencies

None.

#### Risk Notes

If `**Outputs:**` bold label is present elsewhere in the convention (outside the schema block), it should be preserved or converted contextually — verify during edit.

---

### Task 2: Update plan schema in `aib-analysis.md`

#### Intent

Synchronise the plan task schema in `aib-analysis.md` with the updated convention, replacing bold labels with `####` headings and adding empty-line guidance.

#### Outputs

Updated `.aib_brain/prompts/aib-analysis.md` with the same structural changes as Task 1 applied to the embedded Plan schema block.

#### Procedure

1. Open `.aib_brain/prompts/aib-analysis.md` and locate the Plan task schema block (inside the `## Plan` output specification).

2. Replace each bold label in the schema template with the corresponding `####` heading, mirroring the changes made in Task 1 to `.aib_brain/conventions/request-convention.md`.

3. Add guidance within the schema block stating that procedure steps must be separated by one blank line.

4. Re-read the affected section of `.aib_brain/prompts/aib-analysis.md` and verify schema consistency with the updated convention.

#### Done Criteria

- The plan schema in `aib-analysis.md` uses `####` headings matching the convention.
- Bold inline plan labels are absent from the schema block.
- Empty-line requirement for procedure steps is stated.

#### Dependencies

Task 1.

#### Risk Notes

`test_analysis_prompt_structure.py` currently asserts `"**Outputs:**" in content` for `aib-analysis.md`. This assertion will fail after this task; Task 3 must be completed before or immediately after.

---

### Task 3: Update test assertions in `test_analysis_prompt_structure.py`

#### Intent

Update automated test assertions to reflect the new `####` heading format for plan task sub-fields.

#### Outputs

Updated `tests/test_analysis_prompt_structure.py` with:
- Positive assertions for `#### Outputs` (replacing `**Outputs:**`) in both `aib-analysis.md` and `request-convention.md`.
- Negative assertions confirming `**Intent:**` and `**Done Criteria:**` are absent from both files.
- (Optional) An assertion that no markdown table delimiter (`| ---`) appears in the plan schema block.

#### Procedure

1. Open `tests/test_analysis_prompt_structure.py` and locate the `TestPlanSchemaFieldsInAnalysisPrompt` and `TestPlanSchemaFieldsInRequestConvention` classes.

2. In `TestPlanSchemaFieldsInAnalysisPrompt`, change the `test_outputs_field_present` assertion from `assert "**Outputs:**" in content` to `assert "#### Outputs" in content`.

3. In `TestPlanSchemaFieldsInRequestConvention`, change the `test_outputs_field_present` assertion from `assert "**Outputs:**" in content` to `assert "#### Outputs" in content`.

4. Add a new test method to each class asserting `"**Intent:**" not in content` (scoped to the plan schema block or the whole file).

5. Run `python -m pytest tests/test_analysis_prompt_structure.py` from the workspace root and review terminal output to confirm all tests pass.

#### Done Criteria

- All tests in `test_analysis_prompt_structure.py` pass.
- Assertions for `#### Outputs` are present and passing.
- Assertions for `**Outputs:**` (old format) are removed.

#### Dependencies

Task 1, Task 2.

#### Risk Notes

Literal-string test assertions are brittle. If the prompt or convention uses `#### Outputs` with different surrounding whitespace, assertions may fail. Verify surrounding context is consistent.

---

### Task 4: Run full test suite regression

#### Intent

Confirm that no existing tests are broken by the formatting changes.

#### Outputs

Test run evidence (pass/fail) for the full test suite.

#### Procedure

1. Run `python -m pytest tests/` from the workspace root and capture terminal output.

2. Review output for failures not related to Task 3 changes; triage any unexpected failures against the changed files.

3. If failures are found, map them to the changed files in Tasks 1–3 and remediate before proceeding.

#### Done Criteria

- All tests in `tests/` pass.
- No regressions outside the intentional Task 3 changes.

#### Dependencies

Task 3.

#### Risk Notes

Pre-existing test instability (if any) may appear as regressions; triage before attributing to this request's changes.

---

### Task 5: Update documentation and context

#### Intent

Synchronise `.aib_memory/context.md` with the finalised formatting convention and update the `## Documentation` section of this request file.

#### Outputs

Updated `.aib_memory/context.md` reflecting new `request.md` plan format; updated `## Documentation` in `.aib_memory/request-R-20260510-1238.md`.

#### Procedure

1. Open `.aib_memory/context.md` and locate the Requirements Summary or Architecture section that describes `request.md` plan task schema; update any references to bold-label fields to reflect `####` headings; acceptance test: no bold plan-schema labels remain in `context.md` that contradict the new convention.

2. Open `.aib_memory/request-R-20260510-1238.md` and verify the `## Documentation` section lists all files changed in this implementation run; acceptance test: every changed file appears in the list with a rationale.

#### Done Criteria

- `context.md` does not reference bold plan-schema labels as the current format.
- `## Documentation` lists all files changed by this request.

#### Dependencies

Task 1, Task 2, Task 3.

#### Risk Notes

`context.md` is auto-generated by `aib-context.md`; manual edits should be noted for the next context regeneration run.

## Documentation

- `.aib_brain/conventions/request-convention.md` — Update plan task schema to use `####` headings; add empty-line and table-prohibition formatting rules.
- `.aib_brain/prompts/aib-analysis.md` — Update embedded plan schema to match convention; add procedure step spacing guidance.
- `tests/test_analysis_prompt_structure.py` — Update `**Outputs:**` assertions to `#### Outputs`; add negative assertions for old bold-label format.
- `.aib_memory/context.md` — Reflect updated plan task schema format in product documentation.

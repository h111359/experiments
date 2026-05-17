Files read during this implementation run:
- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/request-R-20260510-1238.md`
- `.aib_memory/context.md`
- `.aib_brain/conventions/request-convention.md`
- `.aib_brain/prompts/aib-analysis.md`
- `tests/test_analysis_prompt_structure.py`
- `.aib_brain/conventions/implementation-convention.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/context-convention.md`

## Implementation Log

### Entry 2026-05-10 14:00

#### Scope

Replace bold inline plan task labels (`**Intent:**`, `**Outputs:**`, etc.) with level-4 markdown headings (`####`) in both `request-convention.md` and `aib-analysis.md`; add empty-line spacing and table-prohibition formatting rules to the convention; update test assertions in `test_analysis_prompt_structure.py` to assert the new heading format and assert the old bold labels are absent; update `context.md` to reflect the new schema.

#### Changes

- Updated `.aib_brain/conventions/request-convention.md`: replaced bold inline schema labels with `####` headings in the Plan task schema block; added level-4 heading rule, blank-line-between-tasks rule, blank-line-between-subfield-and-content rule, blank-line-between-procedure-steps rule, and table-prohibition rule to the Formatting Rules section.
- Updated `.aib_brain/prompts/aib-analysis.md`: replaced bold inline schema labels with `####` headings in the embedded Plan schema block; added blank-line-between-procedure-steps requirement to the schema comment.
- Updated `tests/test_analysis_prompt_structure.py`: changed `test_outputs_field_present` assertions from `**Outputs:**` to `#### Outputs` in both `TestPlanSchemaFieldsInAnalysisPrompt` and `TestPlanSchemaFieldsInRequestConvention`; added `test_intent_bold_label_absent` negative assertions to both classes; updated module docstring to reflect new assertion descriptions.
- Updated `.aib_memory/context.md`: replaced two references to the old `**Outputs:**`-based plan task schema description with the new `####`-heading description including empty-line and table-prohibition rules.

#### Tests

- unit: `tests/test_analysis_prompt_structure.py` — all 22 tests PASSED (including new `test_intent_bold_label_absent` and updated `test_outputs_field_present` assertions).
- regression: full suite `tests/` (189 tests, excluding `test_semver_workflow_structure.py` which has a pre-existing `yaml` module dependency not installed in the environment) — all 189 tests PASSED.

#### Outcome

Success. All success criteria met: plan task sub-fields use `####` headings in both the convention and the prompt schema; procedure steps are required to be separated by one blank line; markdown tables are explicitly prohibited; all tests pass with no regressions.

#### Evidence

```
============================= test session starts =============================
collected 189 items
...
============================ 189 passed in 11.71s =============================
```

#### Notes (Optional)

`test_semver_workflow_structure.py` was excluded from the run due to a pre-existing missing `yaml` module dependency in the local environment. This is unrelated to this request's changes and was present before this implementation run.

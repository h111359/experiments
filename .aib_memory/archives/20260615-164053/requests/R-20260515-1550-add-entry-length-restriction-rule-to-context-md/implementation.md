Files read from `.aib_memory/` during this implementation run:
- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/plan-R-20260515-1550.md`
- `.aib_memory/context.md`

## Implementation Log

### Entry 2026-05-15 15:55

#### Scope

Add an explicit two-sentence entry-length enforcement bullet to the `aib-context.md` Phase 4 formatting checklist, matching the style of existing checklist bullets. Extend `tests/test_context_formatting_rules.py` with two new test methods verifying rule 16 is enforced in both `context-convention.md` and `aib-context.md`.

#### Changes

- Added bullet "Each bullet or list item MUST NOT exceed two sentences. If an entry requires more than two sentences, split it into two or more separate bullet items." to Phase 4 "Formatting requirements" block in `.aib_brain/prompts/aib-context.md`.
- Added method `test_sentence_limit_rule_present` to class `TestContextConventionFormattingRules` in `tests/test_context_formatting_rules.py`, asserting "MUST NOT exceed two sentences" is present in `context-convention.md`.
- Added method `test_sentence_limit_enforcement_in_prompt` to class `TestContextPromptFormattingChecklist` in `tests/test_context_formatting_rules.py`, asserting "MUST NOT exceed two sentences" is present in `aib-context.md`.
- Appended curated change bullet to `logs/next_version_changes.md`.
- Updated `.aib_brain/README.md` to fix discrepancies: removed `*(recommended)*` marker reference from Q&A section, corrected first-option fallback description, replaced `request.md` with `plan-<id>.md` in Use Cases and Request Folder Artifacts table, removed stale `templates/` subfolder from folder structure, removed stale `answer-<timestamp>.md` and `UAT_scenarios.md` (legacy names) from Request Folder Artifacts table.
- Updated `.aib_memory/context.md` preamble timestamp, `test_context_formatting_rules.py` description, and `aib-context.md` Workspace File Inventory entry to reflect Phase 4 two-sentence enforcement.

#### Tests

- Unit/regression: `pytest tests/test_context_formatting_rules.py -v` — 7 tests, all PASSED (includes 2 new tests: `test_sentence_limit_rule_present`, `test_sentence_limit_enforcement_in_prompt`).

#### Outcome

All success criteria met. The two-sentence limit enforcement is now present in `aib-context.md`, tested, and documented. No unresolved failures or blockers.

#### Evidence

```
tests/test_context_formatting_rules.py::TestContextConventionFormattingRules::test_no_tables_rule_present PASSED
tests/test_context_formatting_rules.py::TestContextConventionFormattingRules::test_blank_line_between_bullets_rule_present PASSED
tests/test_context_formatting_rules.py::TestContextConventionFormattingRules::test_heading_depth_cap_rule_present PASSED
tests/test_context_formatting_rules.py::TestContextConventionFormattingRules::test_sentence_limit_rule_present PASSED
tests/test_context_formatting_rules.py::TestContextPromptFormattingChecklist::test_no_tables_prohibition_in_prompt PASSED
tests/test_context_formatting_rules.py::TestContextPromptFormattingChecklist::test_blank_line_requirement_in_prompt PASSED
tests/test_context_formatting_rules.py::TestContextPromptFormattingChecklist::test_sentence_limit_enforcement_in_prompt PASSED
7 passed in 0.03s
```

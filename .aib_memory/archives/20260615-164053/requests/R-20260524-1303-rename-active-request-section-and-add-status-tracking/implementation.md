Implementation record for request R-20260524-1303: Rename Active request section and add status tracking.

Files read during this run:
- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/context.md`
- `.aib_memory/plan-R-20260524-1303.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/implementation-convention.md`
- `.aib_brain/tools/finalize-input.py`
- `.aib_brain/tools/close-request.py`
- `.aib_brain/tools/initialize.py`
- `.aib_brain/prompts/aib-analyze.md`
- `tests/test_finalize_input.py`
- `tests/test_close_request.py`
- `tests/test_initialize.py`
- `tests/test_menu.py`
- `tests/test_questions_in_input_md.py`

## Implementation Log

### Entry 2026-05-24 14:30

#### Scope
Renamed the `## Active request` section heading to `## Status` in all `input.md` seed templates across `finalize-input.py`, `close-request.py`, and `initialize.py`. Added `State: <value>` tracking lines (`analysis_ready` for finalize-input.py, `idle` for close-request.py and initialize.py). Updated `_is_stub_equivalent` in `finalize-input.py` to neutralize both variable lines under `## Status`. Updated `aib-analyze.md` to emit step-completion notes after each of steps S01–S10 and to set `State: questions_generated` when Q-blocks are generated (S08.3). Updated all affected tests and context.md.

#### Changes
- Updated `_SEED_TEMPLATE` in `.aib_brain/tools/finalize-input.py`: replaced `## Active request` heading with `## Status` and added `State: analysis_ready` line.
- Updated `_is_stub_equivalent` in `.aib_brain/tools/finalize-input.py`: replaced single-line regex for `## Active request` with two-line regex for `## Status` heading neutralizing both request ID and State value lines.
- Updated `input_seed` in `.aib_brain/tools/close-request.py`: replaced `## Active request` with `## Status` and added `State: idle`.
- Updated `input_seed` in `.aib_brain/tools/initialize.py`: replaced `## Active request` with `## Status` and added `State: idle`.
- Updated `.aib_brain/prompts/aib-analyze.md`: fixed Execution Model Summary from "9-step" to "10-step"; added `S0N.X. Output a short step-completion note` sub-step at end of each step S01–S10; added S08.3 instruction to set `State: questions_generated`; renumbered old S08.3 to S08.4; added S08.5 completion note.
- Updated `_SEED_TEMPLATE` and `_NON_STUB_INPUT` constants in `tests/test_finalize_input.py` to use `## Status` and `State: analysis_ready`.
- Updated `test_input_md_reset_contains_request_id` in `tests/test_finalize_input.py` to assert `## Status` and `State: analysis_ready` are present.
- Added `TestStubEquivalenceStateVariants` test class in `tests/test_finalize_input.py` verifying stub equivalence is preserved when only State value differs.
- Updated mock input.md and assertions in `tests/test_close_request.py` to use `## Status` and assert `State: idle`.
- Updated `test_creates_input_md` assertion in `tests/test_initialize.py` from `## Active request` to `## Status`; added `State: idle` assertion.
- Updated `_INPUT_MD_SEED`, `_INPUT_MD_WITH_CONTENT`, `_INPUT_MD_WITH_QUESTIONS` constants and inline test strings in `tests/test_menu.py` to use `## Status` with appropriate State values.
- Updated assertion in `tests/test_questions_in_input_md.py` from `## Active request` to `## Status`.
- Updated `.aib_memory/context.md`: replaced "9-step" with "10-step" (two occurrences); updated `input.md` glossary entry to describe `## Status` section and `State: <value>` line with all four allowed values; added step-completion notes and S08 state-override to analysis workflow description.
- Appended change bullets to `logs/next_version_changes.md`.

#### Tests
- Unit: `tests/test_finalize_input.py` — all 14 tests pass (including new `TestStubEquivalenceStateVariants`).
- Unit: `tests/test_close_request.py` — all tests pass including updated `test_resets_input_md_when_exists` assertions.
- Unit: `tests/test_initialize.py` — all tests pass including updated `test_creates_input_md` assertion.
- Unit: `tests/test_menu.py` — all 75 tests pass with updated constants and inline strings.
- Full suite: `pytest tests/` — 298 passed, 11 pre-existing failures in `test_analysis_prompt_structure.py` (unchanged from baseline).

#### Outcome
All implementation tasks completed successfully. The `## Status` section heading and `State:` tracking line are in place across all seed templates. The `_is_stub_equivalent` function handles the two-variable-line structure correctly. The `aib-analyze.md` prompt now emits step-completion notes after each step and sets `State: questions_generated` when Q-blocks are generated. No new test failures were introduced.

#### Evidence
- Test run: `pytest tests/test_finalize_input.py tests/test_close_request.py tests/test_initialize.py tests/test_menu.py -v` → 117 passed.
- Test run: `pytest tests/` → 298 passed, 11 pre-existing failures (unchanged from baseline).

#### Notes (Optional)
The 11 pre-existing failures in `test_analysis_prompt_structure.py` were verified to exist on the baseline branch before any changes were applied. They are not in scope for this request.

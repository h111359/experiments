Files from `.aib_memory/` considered during this implementation:
- `.aib_memory/context.md` (REF-0001)
- `.aib_memory/references.md`
- `.aib_memory/requests/R-20260420-1727-analysis-prompt-and-workflow-improvements/request.md`

## Implementation Log

### Entry 2026-04-20 18:30

#### Scope
Fix the stale `input.md` bug after implement (Q001 → Option B: reset logic added to `close-request.py`), add scale-direction labels to the Question threshold row in the `input.md` seed template, add a `*(recommended)*` marker to the Q-block format in `aib-analysis.md` and `request-convention.md`, and add an ambiguity-detection instruction to the `## Questions & Decisions` section of `aib-analysis.md`. Impacted components: `close-request.py`, `initialize.py`, `aib-analysis.md`, `request-convention.md`, and tests.

#### Changes
- Updated `.aib_brain/tools/close-request.py`: added `input.md` reset logic after `update_requests_register` — resets to seed template with "No active request" when the file exists; skips silently when absent. Updated module docstring to reflect the new responsibility.
- Updated `.aib_brain/tools/initialize.py`: replaced `[ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5` with `[ ] 1 (all)  [ ] 2  [x] 3  [ ] 4  [ ] 5 (mandatory only)` in the `input_seed` constant (SC-02).
- Updated `.aib_brain/prompts/aib-analysis.md`: replaced the threshold row in all three inline seed template strings (toggle-detection reset at step 4, Auto-Request Creation Branch reset at step 8, standard flow final step reset at step 9) with the labeled format (SC-03).
- Updated `.aib_brain/prompts/aib-analysis.md`: renamed `**Q-block format (unchanged):**` to `**Q-block format:**`, added `*(recommended)*` suffix to Option B in the example block, and added a SHOULD/MAY instruction for the marker (SC-04, SC-06).
- Updated `.aib_brain/prompts/aib-analysis.md`: inserted `**Ambiguity detection (MUST execute before decision rule):**` block before the `**Decision rule:**` block in `## Questions & Decisions` (SC-05).
- Updated `.aib_brain/conventions/request-convention.md`: added `*(recommended)*` suffix to Option B in the Q-block schema example and added the SHOULD/MAY marker instruction (SC-06).
- Added `tests/test_close_request.py`: `test_resets_input_md_when_exists` — asserts that `input.md` is reset to seed template (with "No active request", "1 (all)", "5 (mandatory only)") after close.
- Added `tests/test_close_request.py`: `test_does_not_fail_when_input_md_missing` — asserts that close-request succeeds (rc 0) when `input.md` does not exist.
- Added `tests/test_initialize.py`: `test_input_md_has_threshold_scale_labels` — asserts that the seeded `input.md` contains "1 (all)" and "5 (mandatory only)".

#### Tests
- unit: `tests/test_close_request.py::TestCloseRequest::test_resets_input_md_when_exists` — pass
- unit: `tests/test_close_request.py::TestCloseRequest::test_does_not_fail_when_input_md_missing` — pass
- unit: `tests/test_initialize.py::TestInitialize::test_input_md_has_threshold_scale_labels` — pass
- regression: full test suite (81 tests) — all pass

#### Outcome
All 81 tests pass. All four task areas (bug fix, threshold labels, Q-block recommended marker, ambiguity detection) are implemented and verified. Success criteria SC-01 through SC-06 are satisfied.

#### Evidence
- `python -m pytest tests/ -v` → `81 passed in 2.10s`
- `.aib_brain/tools/initialize.py` line 63: `"- Question threshold: [ ] 1 (all)  [ ] 2  [x] 3  [ ] 4  [ ] 5 (mandatory only)\n\n"`
- `.aib_brain/prompts/aib-analysis.md`: 3 seed string occurrences updated; ambiguity detection block inserted at line 140; Q-block format updated at lines 153 and 158.
- `.aib_brain/conventions/request-convention.md`: Q-block schema updated at lines 95 and 99.
- `.aib_brain/tools/close-request.py`: input.md reset block added at lines 84–96.

Files consulted from .aib_memory/:
- `.aib_memory/request.md` — authoritative scope, plan, and success criteria
- `.aib_memory/context.md` — workspace product context
- `.aib_memory/instructions.md` — persistent workspace directives (next_version_changes.md directive)

## Implementation Log

### Entry 2026-05-08 11:00
#### Scope
Move Q&A workflow from `request.md` to `input.md`. Removed `Question threshold` row and threshold-based decision logic from `aib-analysis.md`, `initialize.py`, and `close-request.py`. Added AI-autonomous Q-block generation targeting `input.md ## Questions` with answer-application sub-flow on re-run. Updated README, tests, and `context.md` to reflect the new workflow. Covers Tasks 1–9 from the request plan.

#### Changes
- Removed `Question threshold` row from `input_seed` string in `.aib_brain/tools/initialize.py`.
- Removed `Question threshold` row from `input_seed` string in `.aib_brain/tools/close-request.py`.
- Updated `.aib_brain/prompts/aib-analysis.md`: removed threshold row from all three seed template strings; removed `Threshold read`, `5-Level Severity Scale`, and `Decision rule` blocks from `## Questions & Decisions` section; changed Q-block generation target from `request.md ## Questions & Decisions` to `input.md ## Questions`; added `> **Why this matters:**` line to Q-block format; added Answer Application Sub-flow in toggle detection step 5; updated standard flow final step and auto-request branch step 8 reset strings; noted Q-block generation rules with AI-autonomous judgment guidance.
- Updated `.aib_brain/README.md`: removed `## Question Threshold` section and table; added `## Questions and Answers` section documenting the new Q&A workflow in `input.md`.
- Renamed `test_input_md_has_threshold_scale_labels` to `test_input_md_has_no_threshold_row` in `tests/test_initialize.py`; updated assertions to verify threshold row is absent.
- Fixed `test_resets_input_md_when_exists` in `tests/test_close_request.py`: replaced `assert "1 (all)" in content` and `assert "5 (mandatory only)" in content` with `assert "Question threshold" not in content`.
- Created `tests/test_questions_in_input_md.py` with tests covering SC-1 through SC-5 (threshold removal, Q-block target, impact line, recommended marker, answer-application sub-flow, README documentation).
- Updated `.aib_memory/context.md`: removed all `Question threshold` references from FR-007, AC-1, AC-3, Component Map Input Channel row, Module Breakdown `initialize.py` bullet, `aib-analysis.md` bullet, and ALG-0003; added descriptions of new Q&A workflow in `input.md`.
- Appended change bullets to `logs/next_version_changes.md`.

#### Tests
- unit: `tests/test_initialize.py::TestInitialize::test_input_md_has_no_threshold_row` — pass
- unit: `tests/test_close_request.py::TestCloseRequest::test_resets_input_md_when_exists` — pass
- unit: `tests/test_questions_in_input_md.py::TestThresholdRemovedFromSeedTemplates` (3 tests) — pass
- unit: `tests/test_questions_in_input_md.py::TestAnalysisPromptQuestionsSection` (6 tests) — pass
- unit: `tests/test_questions_in_input_md.py::TestReadmeQandADocumentation` (2 tests) — pass
- integration: `pytest tests/ --ignore=tests/test_semver_workflow_structure.py` — 160 passed, 0 failed

#### Outcome
Successful. All 160 tests pass with zero regressions. The `Question threshold` row is absent from all seed templates and prompt logic. Q-blocks are now generated in `input.md ## Questions` with an AI-autonomous judgment model. The Answer Application Sub-flow on re-run processes all Q-blocks and clears the section. README and `context.md` reflect the new workflow.

#### Evidence
- `pytest tests/ --ignore=tests/test_semver_workflow_structure.py -q` output: `160 passed in 9.91s`
- `tests/test_questions_in_input_md.py` — new file, all tests green
- `tests/test_initialize.py::TestInitialize::test_input_md_has_no_threshold_row` — green

Files read from `.aib_memory/` during this implementation run:
- `.aib_memory/requests/R-20260426-1458-keep-active-request-files-in-aib-memory-until-implemented/request.md`
- `.aib_memory/references.md`
- `.aib_memory/context.md`
- `.aib_memory/instructions.md`

## Implementation Log

### Entry 2026-04-26 15:30

#### Scope
Implement the two-phase artifact placement workflow: active-request artifacts (`request.md`, `analysis.md`, `UAT_scenarios.md`) are written to `.aib_memory/` root during analysis and moved to the request subfolder upon successful implementation. Changes span `aib-analysis.md`, `aib-implement.md`, `close-request.py`, a new `move-request-artifacts.py` tool script, two convention files, and a new test file.

#### Changes
- Updated `.aib_brain/prompts/aib-analysis.md`: changed all artifact write targets from `<request-folder>/request.md`, `<request-folder>/analysis.md`, and `<request-folder>/UAT_scenarios.md` to `.aib_memory/request.md`, `.aib_memory/analysis.md`, and `.aib_memory/UAT_scenarios.md` respectively; updated Part 1 and Part 2 output descriptions and Inputs section.
- Created `.aib_brain/tools/move-request-artifacts.py`: new Python script that deterministically moves `request.md`, `analysis.md`, and `UAT_scenarios.md` from `.aib_memory/` root to the active request's subfolder; idempotent (skips missing files); uses `shutil.move` for cross-filesystem safety.
- Updated `.aib_brain/prompts/aib-implement.md`: clarified that `request.md` is read from `.aib_memory/request.md`; added `move-request-artifacts.py` invocation step before `close-request.py`.
- Updated `.aib_brain/tools/close-request.py`: added guarded `_load_move_artifacts()` call via `importlib.util` before marking request Closed; move failure logs a warning but does not block close.
- Updated `.aib_brain/conventions/analysis-convention.md`: replaced single-location rule in Section 3 with a two-phase placement rule (active at `.aib_memory/`, archived at request subfolder).
- Updated `.aib_brain/conventions/request-convention.md`: replaced File Location & Naming section with a two-phase placement rule for `request.md`.
- Created `tests/test_artifact_placement.py`: 7 test cases covering T1–T5 (move script behavior) and T6–T7 (close-request integration).

#### Tests
- Unit/integration: `pytest tests/test_artifact_placement.py` — 7 tests, all PASSED
- Regression: `pytest tests/` — 107 tests total, all PASSED

#### Outcome
All 7 new tests pass. All 100 pre-existing tests pass (107 total). No unresolved test failures or blockers.

#### Evidence
```
============================= test session starts =============================
collected 107 items

tests/test_artifact_placement.py::TestMoveRequestArtifacts::test_t1_moves_request_md PASSED
tests/test_artifact_placement.py::TestMoveRequestArtifacts::test_t2_moves_analysis_md PASSED
tests/test_artifact_placement.py::TestMoveRequestArtifacts::test_t3_moves_uat_scenarios_md PASSED
tests/test_artifact_placement.py::TestMoveRequestArtifacts::test_t4_skips_missing_uat_scenarios PASSED
tests/test_artifact_placement.py::TestMoveRequestArtifacts::test_t5_idempotent_second_call PASSED
tests/test_artifact_placement.py::TestCloseRequestArtifactPlacement::test_t6_close_moves_artifacts_to_request_folder PASSED
tests/test_artifact_placement.py::TestCloseRequestArtifactPlacement::test_t7_close_completes_when_no_artifacts_at_root PASSED
...
107 passed in 8.58s
```

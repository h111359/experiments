Implementation for R-20260515-1335 — Rename request.md to plan.md and restructure sections.

Artifacts considered: `.aib_memory/plan-R-20260515-1335.md`, `.aib_memory/analysis-R-20260515-1335.md`.

## Implementation Log

### Entry 2026-05-15 14:10

#### Scope
Rename the per-request planning artifact from `request-<ID>.md` to `plan-<ID>.md`, reduce its mandatory schema from 10 sections to 4 (Goal, Constraints, Success criteria, Plan), relocate human-facing content (Background, Scope, Out of scope) to a new `## Request Context` section in `analysis-<ID>.md`, and rename the governing convention from `request-convention.md` to `plan-convention.md`. Updated all tool scripts, prompts, tests, and context documentation to reflect the new naming and schema.

#### Changes
- Created `.aib_brain/conventions/plan-convention.md` with 4-section schema (Goal, Constraints, Success criteria, Plan); deleted `.aib_brain/conventions/request-convention.md`.
- Updated `.aib_brain/conventions/analysis-convention.md`: added section 4.6 `## Request Context [REQ]` with Background, Scope, Out of scope sub-headings; updated mandatory section count to 6.
- Updated `.aib_brain/tools/move-request-artifacts.py`: changed `_ARTIFACT_TYPES` from `("request", "analysis", "UAT_scenarios")` to `("plan", "analysis", "UAT_scenarios")`.
- Updated `.aib_brain/tools/common.py`: renamed `REQUIRED_REQUEST_SECTIONS` to `REQUIRED_PLAN_SECTIONS` with 4 entries; renamed `validate_request_md` to `validate_plan_md`; updated `artifact_name()` docstring.
- Updated `.aib_brain/tools/menu.py`: `detect_guidance_state()` now calls `artifact_name("plan", ...)` and uses `plan_md_path` variable.
- Updated `.aib_brain/prompts/aib-analysis.md`: all `request-<ID>.md` references changed to `plan-<ID>.md`; added section 6.3 for `## Request Context` generation; updated mandatory section list to 4; updated Part 2 renaming; removed legacy sections 7.1 and 7.3.
- Updated `.aib_brain/prompts/aib-implement.md`: Step 4 reads `plan-<request_id>.md` from `.aib_memory/plan-<request_id>.md`.
- Updated `tests/test_analysis_prompt_structure.py`: renamed constants and test classes; updated assertions for 4-section schema and `plan-convention.md`.
- Updated `tests/test_artifact_placement.py`: all `request-{req_id}.md` fixture and assertion references changed to `plan-{req_id}.md`.
- Updated `tests/test_close_request.py`: `_make_request` helper writes to `plan.md` with 4-section content.
- Updated `tests/test_tools_common.py`: import and constant renamed; test class renamed; 4-section content used.
- Updated `tests/test_initialize.py`: three fixture path references changed from `request.md` to `plan.md`.
- Updated `tests/test_menu.py`: `_make_request_md` helper writes `plan-{req_id}.md`; docstrings updated.
- Updated `.aib_memory/context.md`: all `request-<ID>.md`, `request-convention.md`, and related references replaced with `plan-<ID>.md`, `plan-convention.md`; section counts updated; SEQ-002 and SEQ-003 updated.

#### Tests
- Unit/integration: ran `python -m pytest tests/ -v` — 284 passed, 0 failed.

#### Outcome
All 8 tasks completed successfully. The per-request planning artifact is now named `plan-<ID>.md` with a 4-section schema. Analysis artifacts include a `## Request Context` section. All tooling, conventions, prompts, and tests are consistent with the new naming. All 284 tests pass.

#### Evidence
- `python -m pytest tests/ -v` output: `284 passed, 4 subtests passed in 8.95s`.
- `Select-String` grep on `.aib_memory/context.md` for stale patterns (`request-<ID>`, `request-convention`, `validate_request_md`, `REQUIRED_REQUEST`) returned zero matches.

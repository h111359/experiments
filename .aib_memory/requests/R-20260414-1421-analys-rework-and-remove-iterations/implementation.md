# Implementation Log

Append-only entries. Add a new section for every execution update.

Files from `.aib_memory/` taken into consideration:
- `.aib_memory/requests_register.md`
- `.aib_memory/references.md`
- `.aib_memory/requests/R-20260414-1421-analys-rework-and-remove-iterations/request.md`
- `.aib_memory/docs/03 Requirements/RQT-02.md`
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md`
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md`
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md`

## Implementation Log

### Entry 2026-04-14 15:30

#### Scope

Remove iteration tracking from the AIB framework. Eliminate all iteration-related scripts, conventions, templates, menu actions, prompt references, and product-doc content. Rework `aib-analysis.md` to output `analysis.md` (no iteration prefix), apply answered Q&D questions to `request.md` sections, and detect `## Amend Request` blocks. Add `## Amend Request` transient section definition to `request-convention.md`.

#### Changes

- Updated `.aib_brain/tools/menu.py`: removed `SCRIPT_CREATE_ITERATION` and `SCRIPT_CLOSE_ITERATION` constants; added both to `EXCLUDE_SCRIPTS`; removed `active_iteration_id` field and `has_active_iteration` property from `MenuState`; removed iteration-tracking logic from `resolve_menu_state()`; removed Create iteration and Close iteration hardcoded action dicts from `build_script_actions()`; removed iteration filtering branches from `filter_visible_actions()`; updated Create request description.
- Updated `.aib_brain/tools/create-request.py`: removed `iterations.md` creation block; removed unused `CLOSED` and `format_markdown_table` imports; updated module docstring.
- Updated `.aib_brain/conventions/analysis-convention.md`: renamed target files from `<ITERATION_ID>-analysis.md` to `analysis.md` in header, Section 2, Section 3, Section 4.1, Section 8, and Section 9 maintenance rules; removed iteration supremacy rule; updated research method step 1.
- Updated `.aib_brain/conventions/request-convention.md`: removed Iteration 01 auto-creation requirement; updated Q&D re-run rule to apply-and-remove; added `## Amend Request` transient section definition.
- Updated `.aib_brain/conventions/implementation-convention.md`: updated entry format (removed `— Iteration <ID>` from heading, removed `<ID>` field description); updated Cross-Artifact Consistency, Validation Rules, Example; updated authoring model note.
- Updated `.aib_brain/conventions/requests_register-convention.md`: removed iteration seed files from create-request automation behavior.
- Updated `.aib_brain/prompts/aib-analysis.md`: changed output path to `analysis.md`; removed iteration resolution from preflight; added `## Amend Request` detection step; changed Q&D answered-questions behaviour from preserve to apply-and-remove; updated re-run summary.
- Updated `.aib_brain/prompts/aib-implement.md`: removed "Resolve active iteration from request iterations.md" from Input resolution.
- Updated `.aib_brain/prompts/aib-reverse-engineer.md`: removed active iteration resolution and conflict rule; removed iteration id from implementation.md entry fields.
- Updated `.aib_brain/Concepts.md`: removed `create-iteration` and `close-iteration` from Supported actions, common input resolution rules, Action contract matrix, Holistic workflow, Concurrency rules, Iteration files naming section (entirely removed), Content of request folder example, What each file means (removed iterations.md entry, updated analysis.md description), Minimal list of templates, Minimal tools, Minimal conventions, Minimal prompts; updated Objectives; removed iteration-related concept bullets.
- Updated `.aib_brain/README.md`: removed `create-iteration.py` and `close-iteration.py` from Common Commands; updated Typical Daily Flow; removed aib-questionnaire.md and aib-plan.md from Available prompt files; updated Recommended order; updated section heading and scenario descriptions; removed "When to Create a New Iteration vs a New Request" section.
- Updated `.aib_memory/docs/03 Requirements/RQT-02.md`: FR-002 updated (removed iterations.md); FR-003 deprecated; FR-004 updated to analysis.md; Acceptance Criteria item 2 updated; Constraints updated.
- Updated `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md`: TERM-0006 (Iteration) marked Deprecated; change log entry added.
- Updated `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md`: BP-0002 updated (removed iteration 01 seeding); TERM-0006 removed from Cross-Mappings; change log entry added.
- Updated `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md`: change log entry added noting iteration lifecycle removal.
- Deleted `.aib_brain/tools/create-iteration.py`.
- Deleted `.aib_brain/tools/close-iteration.py`.
- Deleted `.aib_brain/conventions/iterations-convention.md`.
- Deleted `.aib_brain/conventions/questionnaire-convention.md`.
- Deleted `.aib_brain/templates/iterations-template.md`.
- Deleted `tests/test_create_iteration.py`.
- Deleted `tests/test_close_iteration.py`.
- Updated `tests/test_create_request.py`: replaced `test_successful_creation_writes_iterations_md` with `test_successful_creation_does_not_create_iterations_md`.
- Updated `tests/test_lifecycle_e2e.py`: removed create-iteration and close-iteration steps from full lifecycle test; removed `_parse_iterations` helper; replaced `test_close_request_auto_closes_active_iteration` with `test_close_request_succeeds_without_iterations`; updated docstring.
- Updated `tests/test_menu.py`: removed `iter_id` from `_make_state()`; removed `test_active_request_with_active_iteration`; replaced `test_active_request_no_iter_shows_close_request_create_iteration` and `test_active_request_with_iter_shows_close_iteration` with `test_active_request_shows_close_request` and `test_active_request_no_iterations_file`; updated `test_returns_list_of_actions` threshold; updated `test_core_scripts_present` to only check create/close-request.py.

#### Tests

- unit/integration: `pytest tests/ -v` — 69 passed, 0 failed (exit code 0).
- T3 — create-request produces no iterations.md: `test_successful_creation_does_not_create_iterations_md` PASS.
- T2 — menu shows no iteration actions: `test_active_request_shows_close_request` and `test_no_active_request_shows_create_request_only_lifecycle_script` PASS.
- T7 — test suite passes after deletions: all 69 tests PASS.
- T8 — residual iteration reference check: PASS — no active iteration references remain in non-historical files (excluding context.md per A2, __pycache__, and backward-compatible close-request.py iteration auto-close).
- T9 — product docs check: ARCH-01, RQT-02, KNW-01, KNW-02 — no `create-iteration.py`, `close-iteration.py`, or `iteration 01` references.

#### Outcome

Success. All 11 planned tasks completed. 69/69 tests pass. Iterations fully removed from the AIB framework. `analysis.md` is now the canonical per-request analysis artifact. `## Amend Request` transient section mechanism added. Answered Q&D questions are now applied and removed on re-run. Note: `.aib_memory/context.md` will need to be regenerated via `aib-context.md` per Assumption A2.

#### Evidence

```
============================= 69 passed in 7.30s ==============================
```

- All deleted files confirmed absent via Remove-Item success.
- Residual grep for `iteration_id|ITERATION_ID|iterations\.md|create-iteration|close-iteration` confirms no active violations in product-doc and brain asset files.

#### Notes (Optional)

- `close-request.py` retains backward-compatible iteration auto-close logic (gracefully handles old requests with `iterations.md`). Not removed since it causes no harm and was not in request scope.
- `.aib_memory/context.md` was not regenerated in this run (per Assumption A2 — user should run `aib-context.md` after this change).

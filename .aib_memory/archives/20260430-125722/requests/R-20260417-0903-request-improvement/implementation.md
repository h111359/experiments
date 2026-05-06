# Implementation Log — R-20260417-0903 request improvement

### Entry 2026-04-17 12:20

#### Scope

All 12 tasks from the approved plan in `request.md` were implemented in a single session.

#### Changes

**Task 1 — initialize.py: seed input.md**
- Added `input.md` seeding block in `.aib_brain/tools/initialize.py` after the `context.md` block.
- Writes `.aib_memory/input.md` with seed template containing `## Active request`, `## Options`, and `## Input` sections; idempotent (skips if file already exists).

**Task 2 — create-request.py: remove template seeding**
- Removed `load_template` and `validate_request_md` imports from `.aib_brain/tools/create-request.py`.
- Removed `request.md` and `implementation.md` file creation blocks.
- Tool now only creates the request folder and register row.

**Task 3 — aib-analysis.md: auto-request branch + toggles**
- Completely rewrote `.aib_brain/prompts/aib-analysis.md`.
- Added Auto-Request Creation Branch (triggered when no Active request): reads `input.md`, derives title, calls `create-request.py`, generates `request.md`, archives `input.md` to `inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`, resets `input.md`.
- Added toggle detection: "No changes" writes timestamped `answer.md` and stops; "Skip analysis" skips `analysis.md` but still updates `request.md`.

**Task 4 — aib-implement.md: auto-analyze + on-demand impl.md + auto-close**
- Completely rewrote `.aib_brain/prompts/aib-implement.md`.
- Zero-Active-request case now triggers Auto-Analysis Branch instead of error.
- `implementation.md` generated from scratch (no pre-seeded template required).
- Added auto-close step: `python .aib_brain/tools/close-request.py --workspace .` as final step.
- `inputs/input-archive-*.md` explicitly excluded from reading.

**Task 5 — menu.py: remove lifecycle, add prompts, remove exit**
- Added `create-request.py` and `close-request.py` to `EXCLUDE_SCRIPTS`.
- Removed `SCRIPT_CREATE_REQUEST` and `SCRIPT_CLOSE_REQUEST` constants.
- `build_script_actions()` now uses dynamic discovery only (no hardcoded lifecycle entries).
- `filter_visible_actions()` is now a pass-through.
- Added `print_prompt_reference()` showing 3 copy-paste prompts.
- `render_menu()` calls `print_prompt_reference()`; removed `"0) Exit"` option.
- `choose_action()` no longer returns `None` on QUIT key; `main()` loops continuously.

**Task 6 — analysis-convention.md: restructure sections**
- Removed code scan and internal review from section 4.4.
- Added mandatory section 5 (External Benchmarking) and section 6 (Minimal Spikes and Experiments).
- Renumbered old 5→7 (Maintenance), 6→8 (Formatting), 7→9 (Determinism), 8→10 (Prohibited).

**Task 7 — request-convention.md: 14 sections, remove Amends**
- Updated section count from 12 to 14.
- Removed `## Amends` section; added sections 12 (Code and Asset Scan), 13 (Internal Review), 14 (Multi-Perspective Stakeholder Review).
- Validation rules updated to forbid `## Amends`.

**Task 8 — version bump v1.1.2 → v1.2.0**
- Deleted `.aib_brain/v1.1.2`; created `.aib_brain/v1.2.0`.

**Task 9 — release_bookkeeping.py: brain zip**
- Added `import zipfile`; added `_create_brain_zip()` function; called from `main()` after `_rotate_marker()`.
- Creates `versions/aib_brain_vX.Y.Z.zip`; idempotent.

**Task 10 — README: update installation section**
- Updated Installation section to reference `versions/aib_brain_v1.2.0.zip`.

**Task 11 — Tests: update all affected test files**
- `test_create_request.py`: replaced creation-writes-request-md test with two no-seeding tests.
- `test_initialize.py`: added `test_creates_input_md` and `test_input_md_idempotent`.
- `test_menu.py`: rewrote `TestFilterVisibleActions` (pass-through); replaced `test_core_scripts_present` with `test_lifecycle_scripts_absent`.
- `test_lifecycle_e2e.py`: updated assertions to verify `request.md`/`implementation.md` NOT created.

**Task 12 — Tests pass + context.md regenerated + request closed**
- `pytest tests/ -v`: 73 passed, 0 failed.
- `.aib_memory/context.md` fully replaced with v1.2.0 content via `aib-context.md` prompt logic.
- Request closed via `python .aib_brain/tools/close-request.py --workspace .`.

#### Tests

All 73 tests passed on first run after all changes (`pytest tests/ -v`, 0 failures).

#### Outcome

All 12 tasks implemented successfully. No regressions. Request closed.

#### Evidence

- `.aib_brain/v1.2.0` exists; `.aib_brain/v1.1.2` deleted.
- `pytest tests/ -v` → 73 passed, 0 failed.
- `close-request.py --workspace .` → `Closed request: R-20260417-0903`.
- `requests_register.md` row for R-20260417-0903 has `state = Closed`.

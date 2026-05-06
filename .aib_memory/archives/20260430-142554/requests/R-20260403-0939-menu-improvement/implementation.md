# Implementation Log

Append-only entries. Add a new section for every execution update.

## Implementation Log

### Entry 2026-04-03 12:00 — Iteration 04

#### Scope

All five improvement areas for the AIB interactive menu and request-lifecycle workflow, as specified in R-20260403-0939 `request.md` §Goal and fully specified through iterations 01–04. Changes cover `menu.py` (Improvements 1–4), `close-request.py` (Improvement 5), new tests in `test_common.py`, and four product-doc updates. Aligned with 04-plan WBS Tasks 1–9.

#### Changes

- Updated `EXCLUDE_SCRIPTS` in `.aib_brain/tools/menu.py` to include `"reverse-engineer.py"` and `"test_common.py"` (Task 1)
- Changed `_detect_copilot_cli()` subprocess command from `["gh", "copilot", "--version"]` to `["copilot", "--version"]` in `.aib_brain/tools/menu.py` (Task 2)
- Updated `render_menu()` in `.aib_brain/tools/menu.py`: added `cli_available: bool` parameter; removed `[script]` suffix from Script action lines; removed `[prompt_file]` suffix from Prompt action lines; added conditional Prompt section — navigable entries when `cli_available=True`, static informational block when `cli_available=False` (Task 3)
- Removed `print("\nRunning command:")` and `print(" ".join(command))` from `run_action()` in `.aib_brain/tools/menu.py` (Task 4)
- Updated `choose_action()` in `.aib_brain/tools/menu.py`: added eager `cli_available = _detect_copilot_cli()` call before `while True` loop; passed `cli_available` to `render_menu()`; set `total_items = len(script_actions)` when CLI absent; gated ENTER and DIGIT prompt navigation on `cli_available` (Task 5)
- Replaced `run_prompt_action()` body in `.aib_brain/tools/menu.py` with `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` — no `capture_output` (Task 6)
- Added `COMPLETED`, `format_markdown_table`, `write_text` to imports in `.aib_brain/tools/close-request.py` (Task 7)
- Replaced `raise ValidationError("Cannot close request while an iteration is Active")` guard in `.aib_brain/tools/close-request.py` with auto-close loop: iterates active iterations, sets state to COMPLETED, writes updated iterations.md, prints notice per iteration (Task 7)
- Added `subprocess` import and `TestCloseRequestAutoClose` test class to `.aib_brain/tools/test_common.py`: `test_close_request_auto_closes_active_iteration` (subprocess invocation, asserts returncode 0, "Auto-closed iteration" in output, iteration state COMPLETED) and `test_exclude_scripts_contains_new_entries` (importlib load of menu.py, asserts `"reverse-engineer.py"` and `"test_common.py"` in `EXCLUDE_SCRIPTS`) (Task 8)
- Updated `ARCH-01.md` AIB Command Menu row Description to reference `copilot --version` detection, `EXCLUDE_SCRIPTS`, and static informational block (Task 9)
- Updated `CMP-01.md` CMP-ART-0005 `edge_cases_and_validation` to include auto-close notice (Task 9)
- Updated `CMP-01.md` CMP-ART-0006 `edge_cases_and_validation` to include CLI gating, static block, and EXCLUDE_SCRIPTS note (Task 9)
- Updated `RQT-02.md` FR-008 to include copilot CLI requirement and informational fallback (Task 9)
- Added TERM-0013 Prompt Action row to `KNW-01.md` Term Entries table and Change Log (Task 9)

#### Tests

- Unit/integration: `pytest .aib_brain/tools/test_common.py` — 81 passed, 6 subtests passed, 0 failed (exit code 0)
- New test `TestCloseRequestAutoClose::test_close_request_auto_closes_active_iteration` — PASSED
- New test `TestCloseRequestAutoClose::test_exclude_scripts_contains_new_entries` — PASSED

#### Outcome

All five improvement areas successfully implemented. Pytest suite passes 100%. Product-doc updates applied to ARCH-01, CMP-01, RQT-02, KNW-01. No residual risks or blockers.

#### Evidence

```
==================== 81 passed, 6 subtests passed in 0.41s ====================
```

#### Notes (Optional)

Invocation for subprocess.run uses bare string without `-p` flag, matching `request.md` §Goal item 3 verbatim. Static informational block uses `-p` flag for display as specified in 04-plan Decision Gates §D.

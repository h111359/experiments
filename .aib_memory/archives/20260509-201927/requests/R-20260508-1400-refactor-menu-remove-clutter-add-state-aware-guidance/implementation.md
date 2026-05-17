Files read from `.aib_memory/` during this implementation run:
- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/request.md`
- `.aib_memory/context.md`

## Implementation Log

### Entry 2026-05-09 11:00

#### Scope

Refactored `.aib_brain/tools/menu.py` to remove UI clutter (copy-paste prompt block, Refresh action, auto-discovery mechanism) and add a dynamic state-aware guidance block. Replaced auto-discovery (`discover_tool_scripts` + `EXCLUDE_SCRIPTS`) with an explicit hard-coded action list (`_SCRIPT_ACTIONS`) containing only `reverse-engineer.py`. Updated `tests/test_menu.py` with new tests covering the hard-coded list and all seven guidance states.

#### Changes

- Removed `EXCLUDE_SCRIPTS` set definition and the comment block above it from `menu.py`.
- Removed `_REFRESH_ACTION` sentinel constant from `menu.py`.
- Removed `discover_tool_scripts()` function from `menu.py`.
- Removed `print_prompt_reference()` function from `menu.py`.
- Added `_SCRIPT_ACTIONS` hard-coded list constant to `menu.py` containing only `reverse-engineer.py`.
- Added `_GUIDANCE_MESSAGES` dict to `menu.py` with guidance text for all seven workspace states.
- Replaced `build_script_actions()` implementation to return the hard-coded `_SCRIPT_ACTIONS` list (no filesystem discovery).
- Updated `filter_visible_actions()` docstring to remove reference to `EXCLUDE_SCRIPTS`.
- Added `_extract_section()` helper to `menu.py` for extracting Markdown H2 section bodies.
- Added `_is_context_empty()` helper to `menu.py` for detecting absent or blank `context.md`.
- Added `_detect_guidance_state()` function to `menu.py` implementing the seven-state detection logic with try/except returning `"unknown"` on error.
- Updated `render_menu()` signature to accept `workspace: Path` parameter; removed inline prompt reference block; added state-aware guidance block and context-empty guidance line.
- Updated `choose_action()` to remove `_REFRESH_ACTION` injection and its type-check handling; added `workspace` argument to `render_menu()` call.
- Updated `tests/test_menu.py` imports to include `_detect_guidance_state`, `_is_context_empty`, and `render_menu`.
- Removed `test_excluded_scripts_absent` test from `TestBuildScriptActions` (references removed `EXCLUDE_SCRIPTS`).
- Added `TestHardCodedActionList` test class with five tests covering SC-03, SC-04, SC-10, SC-11.
- Added `TestDetectGuidanceState` test class with ten tests covering all seven states (SC-05 to SC-15).
- Added `TestGuidanceMessagesKeys` test class asserting the exact seven keys in `_GUIDANCE_MESSAGES` (SC-17).
- Added `TestIsContextEmpty` test class with three tests.
- Added `TestRenderMenuGuidance` test class with four tests covering SC-01, SC-02, SC-16.
- Updated `logs/next_version_changes.md` with curated change bullets per workspace directive.
- Updated `.aib_memory/context.md` to reflect menu refactoring changes in FR-010, component map, module description, configuration section, test strategy, and file inventory.

#### Tests

- Unit test run: `python -m pytest tests/test_menu.py -q` — 69 tests passed, 0 failed.
- Full suite run: `python -m pytest -q --ignore=tests/test_semver_workflow_structure.py` — 182 tests passed, 0 failed (test_semver_workflow_structure.py excluded due to pre-existing missing optional `yaml` dependency).

#### Outcome

All success criteria met. No unresolved test failures or blockers. The menu now presents an explicit hard-coded action list with no auto-discovery, no Refresh option, no inline copy-paste prompt block, and a dynamic state-aware guidance block. All seven states are detectable and display correct guidance text. The context-empty guidance line appears when `context.md` is absent or empty.

#### Evidence

```
tests/test_menu.py: 69 passed in 0.61s
Full suite (excl. test_semver_workflow_structure.py): 182 passed in 10.81s
```

#### Notes (Optional)

The `test_semver_workflow_structure.py` failure is pre-existing and unrelated to this request scope (missing `yaml` module in the local environment). The pre-existing error was present before this implementation run.

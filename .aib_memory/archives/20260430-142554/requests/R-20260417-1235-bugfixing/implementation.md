Files read during this implementation run:
- `.aib_memory/requests/R-20260417-1235-bugfixing/request.md`
- `.aib_memory/references.md`
- `.aib_memory/context.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/implementation-convention.md`

## Implementation Log

### Entry 2026-04-17 12:50
#### Scope
Fix two bugs introduced by R-20260417-0903: (1) `reverse-engineer.py` was incorrectly listed in `EXCLUDE_SCRIPTS` in `menu.py`, leaving no discoverable actions and causing a fatal error on menu launch; (2) `.aib_memory/input.md` was absent because `initialize.py` was not re-run after the seeding feature was added. Changes affect `.aib_brain/tools/menu.py`, `tests/test_menu.py`, and the workspace `.aib_memory/` directory.

#### Changes
- Removed `"reverse-engineer.py"` from `EXCLUDE_SCRIPTS` set in `.aib_brain/tools/menu.py` so `reverse-engineer.py` is discoverable by `discover_tool_scripts()`.
- Added `test_reverse_engineer_present` test method to `TestBuildScriptActions` in `tests/test_menu.py` to prevent silent re-exclusion in the future.
- Ran `python .aib_brain/tools/initialize.py --workspace .` to create `.aib_memory/input.md` with the canonical seed template (`## Active request`, `## Options`, `## Input`).

#### Tests
- unit: `tests/test_menu.py::TestBuildScriptActions::test_reverse_engineer_present` — pass
- unit: `tests/test_menu.py::TestBuildScriptActions::test_excluded_scripts_absent` — pass
- unit: `tests/test_menu.py::TestFilterVisibleActions::test_lifecycle_scripts_not_in_actions` — pass
- integration: full test suite `pytest tests/ -v` — 74 passed, 0 failed

#### Outcome
All three tasks completed successfully. `reverse-engineer.py` is now discoverable in the menu. `.aib_memory/input.md` exists with the correct seed content. All 74 tests pass (73 pre-existing + 1 new regression test).

#### Evidence
- `.aib_brain/tools/menu.py` — `EXCLUDE_SCRIPTS` no longer contains `"reverse-engineer.py"`
- `.aib_memory/input.md` — created with canonical seed template confirmed by filesystem check
- `pytest tests/ -v` output: `74 passed in 2.52s`

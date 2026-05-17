Implementation record for request R-20260509-2024 — Remove Reverse Engineer option from menu.

Files taken into consideration from `.aib_memory/`:
- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/request.md`
- `.aib_memory/context.md`

## Implementation Log

### Entry 2026-05-09 21:00
#### Scope
Remove the Reverse Engineer entry from `_SCRIPT_ACTIONS` in `menu.py`, making the list empty. Reorder `render_menu()` to display the state-aware guidance block before the numbered options list. Update `tests/test_menu.py` to remove the two now-invalid Reverse Engineer tests, update the count assertion, and add a new ordering test. Update FR-010 in `context.md` to reflect that the hard-coded list is now empty and that the guidance block appears before options.

#### Changes
- Removed the Reverse Engineer dict entry from `_SCRIPT_ACTIONS` in `.aib_brain/tools/menu.py`; list is now `[]`.
- Reordered `render_menu()` in `.aib_brain/tools/menu.py` so the `── Next Step ──` guidance block and context-empty line render before the numbered options loop and `0) Quit` footer; added blank separator line between guidance and options.
- Removed `test_reverse_engineer_present` from `tests/test_menu.py` (`TestHardCodedActionList`).
- Removed `test_reverse_engineer_title` from `tests/test_menu.py` (`TestHardCodedActionList`).
- Updated `test_no_glob_discovery` in `tests/test_menu.py` to assert `len(actions) == 0` and removed the second assertion referencing `reverse-engineer.py`; updated inline comment.
- Added `test_render_menu_guidance_before_options` to `TestRenderMenuGuidance` in `tests/test_menu.py` asserting that `── Next Step ──` index is less than `0) Quit` index in the rendered output.
- Updated FR-010 in `.aib_memory/context.md` to state the hard-coded list is empty by default and that the guidance block is rendered before the numbered options list.
- Appended two curated bullets to `logs/next_version_changes.md`.

#### Tests
- Unit, `tests/test_menu.py::TestHardCodedActionList::test_no_glob_discovery`: pass — asserts `len(actions) == 0`.
- Unit, `tests/test_menu.py::TestRenderMenuGuidance::test_render_menu_guidance_before_options`: pass — asserts guidance block precedes options list in rendered output.
- Full suite, `pytest tests/` (excluding pre-existing `test_semver_workflow_structure.py` yaml import error): 181 passed.

#### Outcome
All success criteria met. `_SCRIPT_ACTIONS` is `[]` (SC-1). `render_menu()` renders the guidance block before the options list (SC-2). `test_no_glob_discovery` passes asserting `len(actions) == 0` (SC-3). `test_reverse_engineer_present` and `test_reverse_engineer_title` are removed (SC-4). All 181 tests pass (SC-5). FR-010 in `context.md` no longer references `reverse-engineer.py` as a list member (SC-6). No unresolved blockers.

#### Evidence
- `pytest tests/ --ignore=tests/test_semver_workflow_structure.py -x -q` output: `181 passed in 10.64s`

#### Notes (Optional)
`tests/test_semver_workflow_structure.py` has a pre-existing `ModuleNotFoundError: No module named 'yaml'` that is outside the scope of this request; it was excluded from the test run.

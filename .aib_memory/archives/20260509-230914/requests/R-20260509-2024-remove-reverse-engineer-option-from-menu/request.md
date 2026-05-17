## Goal

Remove the "Reverse Engineer" option from the interactive AIB menu and reorder the menu display so that the numbered options list appears after the "-- Next Step --" state guidance block.

## Background

The interactive menu (`menu.py`) currently exposes one hard-coded developer-facing action: "Reverse Engineer — Walk the workspace and emit a JSON Lines file inventory." The developer no longer wants this action surfaced in the menu. Additionally, the menu currently renders the numbered options list before the state-aware guidance block; the developer wants the guidance block displayed first so the recommended next step is the first thing visible below the active-request status line.

## Scope

- `.aib_brain/tools/menu.py` — remove the Reverse Engineer entry from `_SCRIPT_ACTIONS`, making the list empty; reorder `render_menu()` to display the "-- Next Step --" guidance block before the numbered options list.

- `tests/test_menu.py` — remove `test_reverse_engineer_present` and `test_reverse_engineer_title` (now inapplicable); update `test_no_glob_discovery` to assert 0 items in the hard-coded list instead of 1.

- `.aib_memory/context.md` — update FR-010 to remove the reference to `reverse-engineer.py` being in the hard-coded menu list; reflect that the list is now empty by default.

## Out of scope

- Deleting or modifying `.aib_brain/tools/reverse-engineer.py` (the script remains; only its menu entry is removed).

- `tests/test_reverse_engineer.py` — tests the reverse-engineer script itself, not the menu entry.

- `.aib_brain/tools/test_common.py` — the `test_exclude_scripts_contains_new_entries` test in this file references `EXCLUDE_SCRIPTS` which does not exist in the current menu; this pre-existing inconsistency is not in scope.

## Constraints

- All tests in `tests/` must pass after the change.
- Python 3.10+ standard library only; no third-party dependencies.
- Do not add or remove any other actions from the menu.
- The `reverse-engineer.py` script file must not be deleted or modified.

## Success criteria

- SC-1: `_SCRIPT_ACTIONS` in `menu.py` is an empty list.
- SC-2: `render_menu()` renders the "-- Next Step --" guidance block before the numbered options list.
- SC-3: `test_no_glob_discovery` passes, asserting `len(actions) == 0`.
- SC-4: `test_reverse_engineer_present` and `test_reverse_engineer_title` are removed from `tests/test_menu.py`.
- SC-5: `pytest tests/` exits with code 0 (all tests pass).
- SC-6: FR-010 in `context.md` no longer states that the hard-coded list contains `reverse-engineer.py`.

## Assumptions

- A1: The `reverse-engineer.py` script file must remain on disk; only its menu entry is removed. Risk if false: if the script is expected to be deleted too, the clean-up is incomplete.

- A2: The render ordering change (guidance block before options) applies only to `render_menu()`; no other function or test produces the menu frame independently. Risk if false: a duplicate rendering path would also need updating.

- A3: Adding an ordering assertion test (T4) is in scope as part of the test task to prevent silent regression. Risk if false: the ordering could be accidentally reverted without detection.

## Plan

### Task 1: Remove Reverse Engineer from `_SCRIPT_ACTIONS`
**Intent:** Empty the `_SCRIPT_ACTIONS` list in `menu.py` by removing the Reverse Engineer entry.
**Outputs:** `.aib_brain/tools/menu.py` (modified — `_SCRIPT_ACTIONS` becomes `[]`)
**Procedure:**
1. Open `.aib_brain/tools/menu.py`.
2. Locate the `_SCRIPT_ACTIONS` list (lines ~27–44).
3. Remove the entire dict entry for Reverse Engineer, leaving `_SCRIPT_ACTIONS: list[dict[str, Any]] = []`.
4. Preserve the surrounding comment block explaining the list's purpose.
**Done Criteria:** `_SCRIPT_ACTIONS` is `[]`; `build_script_actions(tools_dir)` returns an empty list.
**Dependencies:** None
**Risk Notes:** None.

### Task 2: Reorder `render_menu()` — guidance block before options
**Intent:** Move the "-- Next Step --" guidance block and context-empty line to render before the numbered options list.
**Outputs:** `.aib_brain/tools/menu.py` (modified — `render_menu()` block order changed)
**Procedure:**
1. Open `.aib_brain/tools/menu.py`, locate `render_menu()`.
2. Identify the four logical blocks: (a) active-request line, (b) options loop + "0) Quit", (c) guidance block, (d) context-empty line.
3. Reorder to: (a) active-request line → (c) guidance block → (d) context-empty line → (b) options loop + "0) Quit".
4. Add a blank separator line between the context-empty line and the start of the options loop for visual clarity.
**Done Criteria:** In rendered output, the `── Next Step ──` string appears before the first numbered action line (or before "0) Quit" when the list is empty).
**Dependencies:** Task 1 (empty list simplifies verification).
**Risk Notes:** ANSI `\033[J]` erase-trailing-content must remain as the last write to prevent stale rows.

### Task 3: Update `tests/test_menu.py`
**Intent:** Remove now-invalid Reverse Engineer tests and update the count assertion in `test_no_glob_discovery`.
**Outputs:** `tests/test_menu.py` (modified)
**Procedure:**
1. Open `tests/test_menu.py`.
2. Remove the method `test_reverse_engineer_present` from `TestHardCodedActionList`.
3. Remove the method `test_reverse_engineer_title` from `TestHardCodedActionList`.
4. In `test_no_glob_discovery`, replace `assert len(actions) == 1` with `assert len(actions) == 0` and remove the second assertion `assert actions[0]["script"] == "reverse-engineer.py"`. Update the inline comment to reflect the list is intentionally empty.
5. Add a new test `test_render_menu_guidance_before_options` in `TestRenderMenuGuidance` (or a suitable class) that captures `render_menu()` output and asserts `output.index("── Next Step ──") < output.index("0) Quit")`.
**Done Criteria:** `pytest tests/test_menu.py` exits with code 0.
**Dependencies:** Tasks 1 and 2.
**Risk Notes:** The new ordering test uses `str.index()` which raises `ValueError` if the substring is absent; this is intentional — it will fail loudly if the marker text changes.

### Task 4: Update documentation
**Intent:** Reflect the menu change in `context.md` and append a curated entry to `logs/next_version_changes.md`.
**Procedure:**
1. Open `.aib_memory/context.md`.
   - Locate FR-010. Update the sentence "the list contains `reverse-engineer.py`" to state "the list is empty by default (no permanently visible actions beyond the conditionally injected close-request action)."
   - Acceptance test: FR-010 no longer mentions `reverse-engineer.py` as a list member.
2. Open `logs/next_version_changes.md`.
   - Append two bullets:
     - `- Remove Reverse Engineer action from the interactive menu.`
     - `- Reorder menu to display state guidance block before the numbered options list.`
   - Acceptance test: file ends with a trailing newline and contains both bullets.
**Done Criteria:** Both files updated as described; `pytest tests/` still exits with code 0.
**Dependencies:** Tasks 1–3.
**Risk Notes:** None.

## Documentation

- `.aib_memory/context.md` (ref_id: N/A) — FR-010 references `reverse-engineer.py` as a member of the hard-coded menu list; must be updated to reflect the list is now empty.

## Questions & Decisions


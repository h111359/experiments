## Goal

Remove the reverse-engineer option from the interactive AIB menu. Assess whether `reverse-engineer.py` is still a valid tool in the framework and, if it has no remaining value, eliminate it entirely.

## Background

The interactive menu in `menu.py` dynamically discovers Python scripts in `.aib_brain/tools/` that are not in the `EXCLUDE_SCRIPTS` set. `reverse-engineer.py` is currently not excluded and therefore appears as a menu option. However, `FR-010` specifies that the menu must expose only the three core prompt invocations (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) and must NOT expose lifecycle commands. The reverse-engineer functionality as a user-facing workflow is fully absorbed by `aib-context.md`, which handles workspace scanning internally and may optionally invoke `reverse-engineer.py` as a helper tool. Exposing the script directly as a menu item misleads users into running it standalone, which only generates a JSONL file inventory — not the actual `context.md` output.

## Scope

- Assess whether `reverse-engineer.py` still has standalone value or whether it only serves as an optional internal helper for `aib-context.md`.

- Add `reverse-engineer.py` to the `EXCLUDE_SCRIPTS` set in `menu.py` to remove it from the interactive menu.

- If assessment confirms the script is retained as an internal helper: keep the file, add it to `EXCLUDE_SCRIPTS` only.

- If assessment confirms the script has no remaining value: delete `reverse-engineer.py` from `.aib_brain/tools/`.

- Update any test file that references `reverse-engineer.py` in the menu context if the test asserts its presence in discovered scripts.

## Out of scope

- Changes to `aib-context.md` prompt logic.

- Changes to `.aib_brain/Concepts.md` (edit_allowed = N).

- Changes to `.aib_memory/context.md` (auto-generated, not hand-edited).

- Introducing new prompts or menu items.

## Constraints

- `EXCLUDE_SCRIPTS` in `menu.py` is the authoritative mechanism for hiding scripts from the menu; no other filtering mechanism should be introduced.

- `.aib_brain/` files MUST NOT be modified by tool scripts; only the AI agent (this workflow) may edit them.

- `edit_allowed = N` on `Concepts.md` means it cannot be modified.

- Python 3.10+ standard library only for tool scripts.

## Success criteria

- Running the AIB menu does not display a "Reverse Engineer" option.

- `reverse-engineer.py` either remains as an excluded internal helper or is deleted, based on analysis findings.

- All tests pass after the change.

- No partial writes or broken states are introduced.

## Assumptions

- A1: `reverse-engineer.py` is retained as an internal helper tool because `aib-context.md` explicitly documents it as an optional helper for Phase 3 workspace scanning.
  - Risk if false: If the script is no longer needed at all, it should be deleted; retaining dead code increases maintenance surface unnecessarily.

- A2: The test method `test_reverse_engineer_present` in `tests/test_menu.py` (line 167) was written to guard the opposite behavior (script visible in menu) and must be deleted, not merely negated, since `test_excluded_scripts_absent` already covers the post-change behavior.
  - Risk if false: If the test is only negated rather than removed, it may create misleading coverage expectations.

## Plan

### Task 1: Add reverse-engineer.py to EXCLUDE_SCRIPTS in menu.py
**Intent:** Remove `reverse-engineer.py` from the dynamic menu discovery by adding it to the `EXCLUDE_SCRIPTS` deny-list.
**Inputs:** `.aib_brain/tools/menu.py` — the `EXCLUDE_SCRIPTS` set definition at module level.
**Outputs:** `.aib_brain/tools/menu.py` — `EXCLUDE_SCRIPTS` updated to include `"reverse-engineer.py"`.
**External Interfaces:** None.
**Environment & Configuration:** None — no config keys or secrets.
**Procedure:**
1. Open `.aib_brain/tools/menu.py`.
2. Locate the `EXCLUDE_SCRIPTS` set definition.
3. Add `"reverse-engineer.py"` as a new entry in the set.
**Done Criteria:** `"reverse-engineer.py"` appears in `EXCLUDE_SCRIPTS`; running `discover_tool_scripts` does not return it; the menu no longer lists a Reverse Engineer option.
**Dependencies:** None.
**Risk Notes:** None.

### Task 2: Remove the test_reverse_engineer_present test method from test_menu.py
**Intent:** Delete the regression test that asserts `reverse-engineer.py` IS in the menu (which conflicts with the new behavior).
**Inputs:** `tests/test_menu.py` — `test_reverse_engineer_present` method at line 167.
**Outputs:** `tests/test_menu.py` — method deleted.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Open `tests/test_menu.py`.
2. Locate the `test_reverse_engineer_present` method.
3. Delete the entire method including its docstring.
**Done Criteria:** The method no longer exists in `test_menu.py`; all remaining tests pass.
**Dependencies:** Task 1.
**Risk Notes:** None — the general `test_excluded_scripts_absent` test will cover the new behavior transitively.

## Testing

- T1 — Menu does not show reverse-engineer: Run the AIB menu and verify no "Reverse Engineer" item appears in the numbered action list. Expected outcome: Only non-excluded tool scripts appear; "Reverse Engineer" is absent.

- T2 — discover_tool_scripts excludes the script: In `test_menu.py`, run `test_excluded_scripts_absent`; verify it passes with `"reverse-engineer.py"` now in `EXCLUDE_SCRIPTS`. Expected outcome: Test passes without modification.

- T3 — reverse-engineer.py script logic still works: Run `tests/test_reverse_engineer.py`. Expected outcome: All test cases pass; the script itself is functional as an internal helper.

- T4 — Full test suite passes: Run `pytest` from the workspace root. Expected outcome: All tests pass with zero failures.

- T5 — Re-run idempotency: Add `"reverse-engineer.py"` to `EXCLUDE_SCRIPTS` again (no-op, already present). Expected outcome: Behavior is unchanged; no error; menu still does not show the option.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — `context.md` must be regenerated after implementation to reflect the updated `menu.py` behavior (Reverse Engineer no longer in menu; `reverse-engineer.py` excluded from dynamic discovery).

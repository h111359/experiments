## Goal

Restore a visible `0) Quit` option in the AIB interactive CLI menu so the user can exit the menu by pressing `0` or `q`/`Q`, producing a clean exit with no error traceback.

## Background

The AIB interactive menu (`menu.py`) was previously rebuilt to eliminate screen blink (R-20260417-1440). During that rework the quit/exit action was removed — `render_menu()` no longer shows a "0) Quit" line, `choose_action()` ignores the `QUIT` key returned by `get_key()`, and `main()` treats `None` from `choose_action()` as a no-op loop rather than an exit signal. Users pressing `q`, `Q`, or `0` see no reaction, and the only way to leave the menu is Ctrl+C (which now exits cleanly but is not discoverable).

## Scope

- `.aib_brain/tools/menu.py` — the sole file in scope:

  - `render_menu()`: Display a fixed `0) Quit` line as part of the menu output (below the numbered script actions, before or after the Refresh entry).

  - `choose_action()`: Handle `QUIT` key (`q`/`Q`) and `DIGIT:0` by returning `None` to signal a quit intent to the caller.

  - `main()`: Change the `if action is None: continue` branch to `if action is None: break` so the event loop exits cleanly when `choose_action()` returns `None`.

## Out of scope

- Changes to any other tool script.

- Keyboard shortcut changes — `q`/`Q` already maps to `"QUIT"` in `get_key()`; no change needed there.

- Changes to `.aib_brain/conventions/`, `.aib_memory/references.md`, or any register file.

- Introduction of external dependencies.

- Changes to `run.bat` or `run.sh` launchers.

## Constraints

- Must use the Python standard library only (NFR-004).

- Must be compatible with Python 3.10+.

- Must work on both Windows and Unix/Mac terminals.

- Existing unit tests in `tests/test_menu.py` must continue to pass without modification.

- The `0) Quit` display must be a fixed (non-navigable by UP/DOWN) line so that the 1-based cursor navigation index for script actions is unchanged.

## Success criteria

1. The rendered menu displays `  0) Quit` (or similar) as a visible fixed line.

2. Pressing `0` or `q`/`Q` while the menu is displayed exits the menu loop and returns to the shell prompt cleanly (exit code 0, no traceback).

3. All existing tests in `tests/test_menu.py` pass without modification.

4. Pressing `q`, `Q`, or `0` from within any numbered menu item highlight still exits cleanly.

## Assumptions

- A1: `get_key()` already returns `"QUIT"` for `q`/`Q` and `"DIGIT:0"` for the `0` digit — confirmed by code inspection; no change needed in `get_key()`.
  - Risk if false: Additional changes to `get_key()` would be required; low risk.

- A2: The `0) Quit` display line is a fixed footer — not part of the 1-based cursor navigation — so UP/DOWN selection cycling and existing `selected_index` logic are unaffected.
  - Risk if false: If navigation is expected to include the quit item, the selection model would need extension; not required per user request.

- A3: Returning `None` from `choose_action()` and `break`-ing the loop in `main()` is the correct exit mechanism; the existing `try/except KeyboardInterrupt` block already produces a clean exit at the same level.
  - Risk if false: None identified; `break` is safe within the try block.

## Plan

### Task 1: Display `0) Quit` in `render_menu()`
**Intent:** Add a fixed `  0) Quit` line to the rendered menu buffer so the quit option is visible to the user.
**Inputs:** `menu.py` — `render_menu()` function; `io.StringIO` buffer pattern already in place.
**Outputs:** Modified `render_menu()` that appends `  0) Quit\n` after the numbered items and before the trailing erase escape.
**External Interfaces:** Terminal stdout.
**Environment & Configuration:** No configuration needed.
**Procedure:**
1. In `render_menu()`, after the `for idx, action in enumerate(script_actions, ...)` loop, add `buf.write("  0) Quit\n")` immediately before the `buf.write("\033[J")` trailing erase line.
**Done Criteria:** Running the menu shows `  0) Quit` below the numbered items.
**Dependencies:** None.
**Risk Notes:** None.

### Task 2: Handle quit keys in `choose_action()`
**Intent:** Make pressing `0` or `q`/`Q` return `None` from `choose_action()` to signal exit intent.
**Inputs:** `menu.py` — `choose_action()` key-dispatch block.
**Outputs:** Modified `choose_action()` with `if key == "QUIT": return None` and `if key == "DIGIT:0": return None` handlers.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. After the `if key == "TIMEOUT": continue` block and before the `if key == "UP":` block, add:
   ```python
   if key == "QUIT":
       return None
   if key == "DIGIT:0":
       return None
   ```
**Done Criteria:** Pressing `q`/`Q`/`0` causes `choose_action()` to return `None`.
**Dependencies:** None.
**Risk Notes:** None.

### Task 3: Exit cleanly in `main()` on `None` return
**Intent:** Change the `if action is None: continue` guard in `main()` to `break` so the program exits the event loop when `choose_action()` returns `None`.
**Inputs:** `menu.py` — `main()` function.
**Outputs:** Modified `main()` with `if action is None: break` replacing `continue`.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. In `main()`, inside the `try` block, change `if action is None: continue` to `if action is None: break`.
**Done Criteria:** After pressing `q`/`Q`/`0`, the program exits to the shell with exit code 0.
**Dependencies:** Task 2.
**Risk Notes:** The `try/except KeyboardInterrupt` already wraps the loop; `break` exits cleanly.

## Testing

- T1 — quit key causes choose_action to return None: Patch `render_menu`, `resolve_menu_state`, `build_script_actions` to no-ops; feed `get_key` returning `"QUIT"`; call `choose_action()`; assert return value is `None`. Expected outcome: `None` returned.

- T2 — digit 0 causes choose_action to return None: Same setup, feed `get_key` returning `"DIGIT:0"`; assert return value is `None`. Expected outcome: `None` returned.

- T3 — render_menu output contains `0) Quit`: Capture `sys.stdout` via `StringIO`; call `render_menu(state, [], 0)`; assert `"0) Quit"` in captured output. Expected outcome: substring present.

- T4 — existing test suite passes: Run `pytest tests/test_menu.py`; assert 38 passed. Expected outcome: 38 passed, 0 failed.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — Update `menu.py` description in Technical Design and Workspace File Inventory to reflect restored quit option.

## Questions & Decisions

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/menu.py` | Modified | Add `0) Quit` display line in `render_menu()`; add quit key handlers in `choose_action()`; change `continue` to `break` in `main()`. |
| `tests/test_menu.py` | Read-only dependency | Existing tests must continue to pass without modification. |
| `.aib_memory/context.md` | Modified | Description of `menu.py` updated to reflect restored quit option. |

## Internal Review of Request and Product Docs

- OK: `request.md` — Goal, Scope, and Success criteria are specific and testable; no ambiguity.
- OK: `menu.py` — `get_key()` already produces `"QUIT"` and `"DIGIT:0"`; no contradiction with the implementation plan.
- OK: `context.md` — Correctly documents the "no exit option" state; this will be updated as part of the request.
- Missing info: No prior ADR documents the original decision to remove the quit option; context references R-20260403-0939 but the rationale is not captured in the current workspace. Assumption: the decision is now reversed per the current request.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The change is architecturally trivial: three targeted edits to a single function in a single file. The return value contract of `choose_action()` already accommodates `None`; `main()` already has a comment noting `None` means "no action selected". The only architectural decision is whether `0) Quit` should be part of the navigable cursor list or a fixed footer — a fixed footer is correct because it avoids reindexing all existing numeric shortcuts and keeps the navigation model unchanged.
- No new modules, abstractions, or dependencies are introduced.
- The exit pathway is now explicit and consistent with the Ctrl+C path.
- No performance or reliability implications.
- Clean separation: display, dispatch, and loop-exit are each changed in their own layer.

### Product Owner

The user explicitly requested this feature, citing the prior existence of the option. The success criteria are measurable (visible line, clean exit, passing tests). Scope is well-bounded to one file. The change directly improves the developer experience with zero feature trade-offs.
- Business value: removes confusion and friction for all CLI menu users.
- Acceptance criteria are complete and testable.
- No risk of scope creep; the change is a three-line delta.
- No documentation gap: `context.md` will be updated.

### User

From the developer's perspective, the menu currently provides no visible way to exit other than Ctrl+C, which is not printed anywhere. Restoring `0) Quit` makes the menu self-documenting and reduces cognitive load.
- The `0` key is immediately adjacent to the `1`–`9` shortcut keys; natural muscle memory.
- `q`/`Q` as an alternative quit key is a standard terminal convention.
- No friction is introduced; no existing workflow changes.

### Security Officer

No security surface is affected. The quit pathway terminates the process; it does not read, write, or transmit data. No authentication, authorization, or secret-handling logic is involved.
- No new attack surface introduced.
- No credentials or data exposed by the change.
- No subprocess is spawned on quit.

### Data Governance Officer

No data assets, registers, or artifacts are read or written by the quit pathway. The change has zero data governance impact.
- No PII or sensitive data is processed.
- No retention, classification, or lineage implications.
- No compliance obligations are affected.


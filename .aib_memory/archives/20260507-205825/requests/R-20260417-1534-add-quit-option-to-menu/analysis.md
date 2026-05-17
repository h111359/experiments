## Executive Summary

- **Request ID:** R-20260417-1534

- **Request title:** Add quit option to menu

- **High-level purpose:** Restore the discoverability and usability of the menu exit pathway by re-adding a visible `0) Quit` menu line and wiring the `QUIT` / `DIGIT:0` key events to a clean program exit in `choose_action()` and `main()`.

- **Root cause:** During R-20260417-1440 (blink-free rendering), `render_menu()` was rewritten as a pure buffer flush. The quit display line was never included in the new buffer; simultaneously `choose_action()` has no handler for the `QUIT` key that `get_key()` already produces, so pressing `q`/`Q`/`0` silently loops.

- **Impact scope:** Three small, isolated changes to `menu.py`: one line added to `render_menu()` output buffer; two key-dispatch branches added to `choose_action()`; one branch changed in `main()`.

- **No new dependencies:** change is pure Python standard library; existing `get_key()` already produces the `"QUIT"` sentinel.

- **Test impact:** Existing 38 menu tests continue to pass; one or two new focused unit tests will cover the quit key handling.

- **Risk:** Minimal. The change restores a previously present feature; it does not alter screen rendering, auto-refresh, or action execution paths.

- **`request.md` updates this run:** `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`, `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`, `## Multi-Perspective Stakeholder Review` added.

## Domain Knowledge Essentials

- **AIB interactive menu:** The terminal-based launcher (`menu.py`) that surfaces AIB tool scripts to the developer. It renders a numbered list, reads single keypresses, and dispatches to action handlers.

- **Quit / Exit option:** A menu entry (conventionally at position 0) that allows the user to leave the menu loop and return to the shell without executing any tool action.

- **Discoverability:** A UX principle meaning the user should be able to discover available actions by reading the menu, without prior knowledge. Hiding the quit pathway behind an undocumented Ctrl+C reduces discoverability.

- **Personas affected:**
  - **Developer** — primary user of the CLI menu; benefits from a visible and reliable quit pathway.
  - **AIB Maintainer** — owns the menu code; benefits from a clean, explicit exit contract in the code.

## Technical Knowledge & Terms

- **`menu.py`** — The sole file in scope. Located at `.aib_brain/tools/menu.py`. Provides `render_menu()`, `choose_action()`, `get_key()`, and `main()`.

- **`get_key(timeout)`** — Already maps `q`/`Q` keypresses to the `"QUIT"` string sentinel. `DIGIT:0` is produced for the `0` digit key. No changes needed in `get_key()`.

- **`choose_action()`** — The main input loop. Calls `render_menu()`, then `get_key()`, then dispatches. Currently the `"QUIT"` key falls through (no handler); `DIGIT:0` is also unhandled because the numeric dispatch guard is `1 <= numeric <= len(script_actions)`.

- **`render_menu()`** — Accumulates the full menu into an `io.StringIO` buffer and flushes in one `sys.stdout.write()`. The `0) Quit` line needs to be appended to this buffer as a fixed footer.

- **`main()`** — The program entry point. Currently: `if action is None: continue` — treats None as a no-op. To exit cleanly on quit, this must become `if action is None: break`.

- **Return value contract of `choose_action()`** — Currently returns `dict | None`; `None` is documented as "no action selected". Returning `None` on quit is already the correct signal; only `main()` needs to act on it by breaking the loop instead of continuing.

- **`_REFRESH_ACTION`** — The sentinel dict for the Refresh item (type=`"refresh"`). The quit entry does not need a sentinel dict; it is purely a display line and a key handler.

- **Files read for evidence:** `.aib_brain/tools/menu.py` (full), `tests/test_menu.py` (full), `.aib_memory/requests_register.md`, `.aib_memory/references.md`, `.aib_memory/context.md`.

## Research Results

### Pattern scan

- **Prior art within this workspace:** The context document (`context.md`) states "No exit option" as a design choice introduced in R-20260403-0939 (Menu improvement) and retained through subsequent requests. The current request explicitly reverses that decision for discoverability reasons.

- **Standard CLI menu conventions:** The `0` key for quit/exit is the most common convention in numbered terminal menus (as seen in Unix `dialog`, Python `curses`-based TUIs, and interactive selection scripts). It is not surprising or ambiguous to the target user.

- **`get_key()` already produces `"QUIT"` for `q`/`Q`:** The plumbing is in place; only the dispatch and display layers need updating.

- **No risk of collision with `_REFRESH_ACTION`:** Refresh is currently the last numbered item (its index equals `len(script_actions) - 1` after `_REFRESH_ACTION` is appended). The quit option at `0` is outside the 1-based numeric index range and does not displace or reindex existing items.

- **`main()` `try/except KeyboardInterrupt` block** (added in the previous bugfix): The clean Ctrl+C handler already calls `sys.stdout.write("\n")` and returns. The `break` for quit will also exit the `while True` loop and reach the end of `main()`, achieving the same clean exit without duplicating logic.

## External Benchmarking

- **Unix `select`-style numbered menus (e.g., bash `select` builtin):** `select` presents items numbered from 1; the user types a number and presses Enter. Quit is handled by pressing Ctrl+C or entering an empty line. AIB's menu uses single-keypress dispatch, so `0` as a quit shortcut is more ergonomic than requiring Enter. The pattern of reserving `0` for "exit/back" is widely established in interactive selection UIs.
  - Takeaway: `0 = quit` is the standard; adopted as-is.

- **Python `curses`-based TUI menus (e.g., `npyscreen`, `urwid` demos):** These libraries always provide an explicit quit binding (typically `q` or `ESC`) displayed in a status bar. AIB already maps `q`/`Q` to `"QUIT"` in `get_key()`; displaying it in the menu footer is the missing piece.
  - Takeaway: Visible key legend for quit is a usability requirement in all reference implementations; confirms the fix is necessary.

## Minimal Spikes and Experiments

**Spike 1 — Verify `get_key()` already returns `"QUIT"` for `q`/`Q` and `"DIGIT:0"` for `0`:**
Reading the Windows branch of `get_key()`: `if first in ("q", "Q"): return "QUIT"` — confirmed. `if first.isdigit(): return f"DIGIT:{first}"` — confirmed `"DIGIT:0"` for `0` key.

**Spike 2 — Verify `choose_action()` never handles `"QUIT"` or `"DIGIT:0"`:**
The `if key.startswith("DIGIT:")` branch guards: `if 1 <= numeric <= len(script_actions)`. For `numeric = 0`, `1 <= 0` is `False`, so the branch is skipped and the loop continues — confirmed unhandled. The `"QUIT"` key has no dispatch branch at all — confirmed unhandled.

**Spike 3 — Verify `main()` `None`-return behavior:**
`if action is None: continue` — currently loops; changing to `break` exits the `while True` loop. The `try/except KeyboardInterrupt` wraps the loop, so a `break` exits cleanly to the function's end — confirmed safe.

**Conclusion:** No structural risk. Three targeted edits suffice.

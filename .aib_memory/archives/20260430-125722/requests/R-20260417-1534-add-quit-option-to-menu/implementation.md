Implementation log for request R-20260417-1534 — Add quit option to menu.

## .aib_memory/ files considered

- `.aib_memory/requests_register.md` — active request resolved from here
- `.aib_memory/references.md` — required-read set built from here
- `.aib_memory/context.md` — product-doc reviewed per context-convention.md
- `.aib_memory/requests/R-20260417-1534-add-quit-option-to-menu/request.md` — authoritative scope, plan, and constraints

## Implementation Log

### Entry 2026-04-17 15:45

#### Scope

Restored the `0) Quit` option to the AIB interactive CLI menu. Three targeted edits to `.aib_brain/tools/menu.py`: added a fixed `0) Quit` footer line to `render_menu()`; added `QUIT` and `DIGIT:0` key handlers in `choose_action()` that return `None`; changed `if action is None: continue` to `if action is None: break` in `main()` so the event loop exits cleanly.

#### Changes

- Modified `render_menu()` in `menu.py`: added `buf.write("  0) Quit\n")` after the numbered items loop and before the trailing `\033[J` erase sequence, making the quit option visible as a fixed footer.
- Modified `choose_action()` in `menu.py`: added `if key == "QUIT": return None` and `if key == "DIGIT:0": return None` handlers immediately after the `TIMEOUT` handler, before the `UP`/`DOWN`/`ENTER`/`DIGIT` dispatch block.
- Modified `main()` in `menu.py`: changed `if action is None: continue` to `if action is None: break` so a `None` return from `choose_action()` exits the event loop cleanly.
- Created `.aib_memory/requests/R-20260417-1534-add-quit-option-to-menu/test_quit_option.py` with T1, T2, T3 tests.

#### Tests

- Unit | `test_quit_option.py::TestQuitKeyReturnsNone::test_quit_key_returns_none` | PASS — T1: `choose_action()` returns `None` on `"QUIT"` key.
- Unit | `test_quit_option.py::TestDigit0ReturnsNone::test_digit0_returns_none` | PASS — T2: `choose_action()` returns `None` on `"DIGIT:0"` key.
- Unit | `test_quit_option.py::TestRenderMenuShowsQuit::test_render_menu_contains_quit_line` | PASS — T3: `"0) Quit"` present in `render_menu()` output.
- Unit | `tests/test_menu.py` (38 tests) | PASS — all 38 existing tests pass without modification.
- Full suite | `tests/` (73 tests) | PASS — 73 passed in 6.08 s.

#### Outcome

Success. Pressing `0` or `q`/`Q` in the menu now exits cleanly to the shell with exit code 0 and no traceback. The `0) Quit` line is visible in the rendered menu. All existing and new tests pass.

#### Evidence

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.0.1, pluggy-1.6.0
rootdir: C:\Hristo\projects\AI_Builder
collected 73 items

73 passed in 6.08s
==============================
```

New tests (request folder):
```
test_quit_option.py::TestQuitKeyReturnsNone::test_quit_key_returns_none PASSED
test_quit_option.py::TestDigit0ReturnsNone::test_digit0_returns_none PASSED
test_quit_option.py::TestRenderMenuShowsQuit::test_render_menu_contains_quit_line PASSED
3 passed in 0.33s
```

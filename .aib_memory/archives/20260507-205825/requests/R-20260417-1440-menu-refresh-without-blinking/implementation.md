Implementation log for request R-20260417-1440 — Menu refresh without blinking.

## .aib_memory/ files considered

- `.aib_memory/requests_register.md` — active request resolved from here
- `.aib_memory/references.md` — required-read set built from here
- `.aib_memory/context.md` — product-doc reviewed per context-convention.md
- `.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/request.md` — authoritative scope, plan, and constraints

## Implementation Log

### Entry 2026-04-17 14:55

#### Scope

Eliminated visible blank-screen blink during menu redraws in `.aib_brain/tools/menu.py` by replacing the subprocess-based `clear_screen()` with ANSI escape sequences, buffering the entire `render_menu()` output into a single stdout write, adding a configurable timeout to `get_key()` for auto-refresh, and enabling Windows ANSI VT processing via a one-time ctypes call at startup.

#### Changes

- Added `import io` and `import time` to the module-level imports in `menu.py`.
- Added module-level constant `_REFRESH_TIMEOUT_S: float = 3.0` adjacent to `_REFRESH_ACTION`.
- Added `_enable_ansi_windows()` helper function that uses `ctypes.windll.kernel32` to set `ENABLE_VIRTUAL_TERMINAL_PROCESSING` (0x0004) on the stdout handle; wrapped in `try/except` for graceful degradation.
- Replaced `clear_screen()` body: removed `os.system("cls"/"clear")` subprocess call; replaced with `sys.stdout.write("\033[H\033[J"); sys.stdout.flush()`. Function name and signature preserved.
- Replaced `render_menu()` body: removed `clear_screen()` call and all `print()` / `print_prompt_reference()` calls; inlined the prompt reference block; accumulated the complete menu string into an `io.StringIO` buffer starting with `"\033[H\033[J"` and appending `"\033[J"` after the last item; flushed with a single `sys.stdout.write(buf.getvalue()); sys.stdout.flush()`.
- Updated `get_key()` signature to `get_key(timeout: float | None = None) -> str`; added full docstring; Windows branch: wrapped `msvcrt.getwch()` in a 50 ms kbhit polling loop with `time.monotonic()` deadline when timeout is set; Unix branch: added `select.select()` pre-check before `tty.setraw()` when timeout is set; returns `"TIMEOUT"` sentinel when no key arrives within the deadline.
- Updated `choose_action()`: changed `get_key()` call to `get_key(timeout=_REFRESH_TIMEOUT_S)`; added `if key == "TIMEOUT": continue` guard before existing key-dispatch block.
- Updated `main()`: added `_enable_ansi_windows()` call after `ensure_memory_initialized_if_missing()` and before the render loop.
- Created `.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/test_clear_screen_ansi.py` with tests T1 and T2 from the request plan.

#### Tests

- Unit | `tests/test_menu.py` (38 tests) | PASS — all 38 existing tests pass without modification, confirming backward compatibility.
- Unit | `test_clear_screen_ansi.py::TestClearScreenNoSubprocess::test_os_system_not_called` | PASS — T1: `os.system` call count is 0 after `clear_screen()`.
- Unit | `test_clear_screen_ansi.py::TestClearScreenAnsiOutput::test_ansi_cursor_home_written` | PASS — T2a: `\033[H` present in captured stdout.
- Unit | `test_clear_screen_ansi.py::TestClearScreenAnsiOutput::test_ansi_erase_screen_written` | PASS — T2b: `\033[J` present in captured stdout.
- Unit | `test_clear_screen_ansi.py::TestClearScreenAnsiOutput::test_both_ansi_sequences_present` | PASS — T2c: both sequences present together.
- Full suite | `tests/` (73 tests) | PASS — 73 passed in 6.12 s.

#### Outcome

Success. All four tasks implemented as specified. `clear_screen()` no longer spawns a subprocess; `render_menu()` issues a single stdout write per render cycle; `get_key()` returns `"TIMEOUT"` after 3 seconds of idle, triggering auto-refresh in `choose_action()`; Windows ANSI VT processing is enabled at startup. No external dependencies introduced; standard library only.

#### Evidence

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.0.1, pluggy-1.6.0
rootdir: C:\Hristo\projects\AI_Builder
collected 73 items

...
73 passed in 6.12s
==============================
```

New tests (request folder):
```
.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/test_clear_screen_ansi.py::TestClearScreenNoSubprocess::test_os_system_not_called PASSED
.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/test_clear_screen_ansi.py::TestClearScreenAnsiOutput::test_ansi_cursor_home_written PASSED
.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/test_clear_screen_ansi.py::TestClearScreenAnsiOutput::test_ansi_erase_screen_written PASSED
.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/test_clear_screen_ansi.py::TestClearScreenAnsiOutput::test_both_ansi_sequences_present PASSED
4 passed in 0.35s
```

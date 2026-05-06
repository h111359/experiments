## Goal

Improve the AIB interactive menu so that it refreshes the active request status (or absence thereof) without causing visible screen blinking or flashing. The current clear-and-redraw mechanism causes a brief blank-screen flash (blink) between every render cycle, which degrades the user experience during keyboard navigation.

## Background

The interactive menu in `.aib_brain/tools/menu.py` uses a tight input loop: on every keypress it calls `render_menu()`, which in turn calls `clear_screen()`. `clear_screen()` invokes `os.system("cls")` on Windows or `os.system("clear")` on Unix — spawning a subprocess to erase the terminal. Between the subprocess-triggered erase and Python's subsequent content write, there is a brief moment where the terminal is blank, perceived by the user as a blink or flash.

Additionally, the input "refresh itself" implies the desire for the active request display to be responsive — either by reducing the render latency or by enabling periodic state re-checks — so the active request section always reflects the current workspace state smoothly.

## Scope

- `.aib_brain/tools/menu.py` — the sole file in scope:

  - `clear_screen()` function: replace `os.system("cls"/"clear")` with a blink-free terminal clear mechanism using ANSI escape sequences, with Windows ANSI support enablement.

  - `render_menu()` function: ensure it uses the updated clear mechanism and produces a single-write output where possible to minimise the blank window between clear and redraw.

  - Buffer the entire menu output before writing to stdout, so the terminal is updated as a single atomic write.

  - `get_key()` function: add an optional `timeout` parameter; on Windows implement via `msvcrt.kbhit()` polling loop (50 ms poll interval); on Unix implement via `select.select()` with timeout. Return the `"TIMEOUT"` sentinel string when no key is pressed within the timeout window.

  - `choose_action()` function: call `get_key(timeout=_REFRESH_TIMEOUT_S)` and treat `"TIMEOUT"` returns as re-render triggers with no action selected, providing auto-refresh every 3 seconds during user idle.

  - Add module-level constant `_REFRESH_TIMEOUT_S: float = 3.0`.

## Out of scope

- Changes to any tool scripts other than `menu.py`.

- Changes to `.aib_brain/conventions/`, `.aib_memory/references.md`, or any register file.

- Introduction of external (non-standard-library) dependencies.

- Replacement of the menu architecture with a curses-based TUI.

- Background daemon threads for UI refresh (the `get_key(timeout)` approach replaces this entirely without threads).

- Changes to `run.bat` or `run.sh` launchers.

## Constraints

- Must use the Python standard library only (NFR-004).

- Must be compatible with Python 3.10+ (NFR-004).

- Must work on Windows (cmd, PowerShell, Windows Terminal) and Unix/Mac terminals.

- ANSI escape code support on legacy Windows cmd.exe must be handled gracefully (fallback acceptable).

- Existing unit tests in `tests/test_menu.py` must continue to pass without modification.

- `clear_screen()` is used only within `render_menu()`; changes must not break its contract for callers.

- The auto-refresh interval must be defined as a named module-level constant (`_REFRESH_TIMEOUT_S`), not as an inline literal.

## Success criteria

1. Navigating the menu with UP / DOWN arrow keys or DIGIT keypresses produces no visible blank-screen flash between redraws on Windows Terminal and common Unix terminals.

2. The "Active request" line correctly shows the active request ID and title (or "No active request") after every render cycle.

3. All existing tests in `tests/test_menu.py` pass without modification.

4. The fix uses only Python standard-library features; no new dependencies are introduced.

5. The implementation works on both Windows (Python 3.10+ / Windows Terminal) and Unix-like systems.

6. When the user does not press any key for 3 seconds, the menu re-renders automatically, picking up any change to the active request state.

## Assumptions

- A1: The target runtime is Windows 10+ (Windows Terminal or cmd.exe with VT support) and common Unix/Mac terminals. Legacy Windows versions (pre-1511) are not a supported target.
  - Risk if false: The ctypes-based ANSI enablement will silently fail, and the fallback to `os.system("cls")` will leave the blink in place on those systems; blink elimination goal is not met for that environment.

- A2: `clear_screen()` is called exclusively from `render_menu()`, meaning changes to `clear_screen()` affect only the menu rendering path.
  - Risk if false: Other code paths relying on the subprocess-clear behaviour could break; however, a code scan confirms no other callers exist.

- A3: The test suite patches `clear_screen` by name (`patch("menu.clear_screen")`); renaming or removing the function would break existing tests. The function signature `() -> None` must be preserved.
  - Risk if false: Tests fail; however, the convention is to preserve the function.

- A4: Menu content height is stable within a session (the number of tool scripts discovered by `build_script_actions` does not change while the menu is running). This makes the cursor-home + erase-to-end strategy safe without line-count tracking.
  - Risk if false: If new `.py` scripts are added to `tools/` while the menu is running, the item count could change. Appending `\033[J` (erase from cursor to end of screen) after the last rendered line mitigates stale content.

- A5: A polling interval of 50 ms for Windows `msvcrt.kbhit()` provides acceptable responsiveness for the auto-refresh feature without perceptible CPU overhead on the target development machines.
  - Risk if false: If 50 ms polling causes noticeable CPU usage in resource-constrained environments, the interval may need tuning; however, the constant `_REFRESH_TIMEOUT_S` and the polling interval are co-located in `get_key()`, making adjustment straightforward.

## Plan

### Task 1: Enable ANSI VT processing on Windows
**Intent:** Add a one-time ANSI enablement call for Windows so subsequent escape sequences are interpreted by the console.
**Inputs:** `menu.py` — module level or `main()` entry point; Python `ctypes` module (standard library).
**Outputs:** Modified `menu.py` with a `_enable_ansi_windows()` helper called once at startup.
**External Interfaces:** `ctypes.windll.kernel32.GetStdHandle`, `SetConsoleMode` (Windows API).
**Environment & Configuration:** Windows 10+ only; the call is wrapped in `try/except` for graceful failure on non-Windows or inaccessible handles.
**Procedure:**
1. Add `_enable_ansi_windows()` function: if `os.name == "nt"`, obtain `STD_OUTPUT_HANDLE` (-11), call `GetConsoleMode`, OR in `ENABLE_VIRTUAL_TERMINAL_PROCESSING` (0x0004), call `SetConsoleMode`.
2. Call `_enable_ansi_windows()` once at the top of `main()` before the first render.
**Done Criteria:** On Windows, `\033[2J` written to stdout clears the screen without literal characters appearing.
**Dependencies:** None.
**Risk Notes:** ctypes may be unavailable in restricted environments; the `try/except` ensures graceful degradation.

### Task 2: Replace `clear_screen()` with ANSI in-place clear
**Intent:** Replace the subprocess-based `os.system("cls"/"clear")` with a direct ANSI write to eliminate the blank-screen blink.
**Inputs:** `menu.py` — `clear_screen()` function.
**Outputs:** Modified `clear_screen()` that writes `\033[H\033[J` to stdout via `sys.stdout.write`.
**External Interfaces:** Terminal stdout.
**Environment & Configuration:** Works on ANSI-capable terminals after Task 1 enablement.
**Procedure:**
1. Replace the body of `clear_screen()` with `sys.stdout.write("\033[H\033[J"); sys.stdout.flush()`.
2. Keep the function name `clear_screen` and signature `() -> None` unchanged.
**Done Criteria:** `clear_screen()` no longer spawns a subprocess; screen content is erased and cursor is at top-left.
**Dependencies:** Task 1 (ANSI enabled on Windows before first call).
**Risk Notes:** On terminals without ANSI support (rare), the escape characters will be printed literally; acceptable degradation.

### Task 3: Buffer `render_menu()` output into a single write
**Intent:** Accumulate the entire menu string in memory and write it to stdout in one call, reducing intermediate-state visibility.
**Inputs:** `menu.py` — `render_menu()` function; `io.StringIO` (standard library).
**Outputs:** Modified `render_menu()` using `io.StringIO` buffer, ending with a single `sys.stdout.write()`.
**External Interfaces:** Terminal stdout.
**Environment & Configuration:** No special configuration needed.
**Procedure:**
1. At the start of `render_menu()`, replace `clear_screen()` call with building output into a `StringIO` starting with `"\033[H\033[J"`.
2. Replace all `print()` calls in `render_menu()` with `buf.write(... + "\n")`.
3. At the end, add `sys.stdout.write(buf.getvalue()); sys.stdout.flush()`.
**Done Criteria:** `render_menu()` issues exactly one `sys.stdout.write()` call per render cycle; no `print()` or `clear_screen()` calls remain inside it.
**Dependencies:** Task 2.
**Risk Notes:** None identified; `io.StringIO` is always available.

### Task 4: Add timeout to `get_key()` and wire auto-refresh in `choose_action()`
**Intent:** Enable idle auto-refresh every 3 seconds by making `get_key()` return a `"TIMEOUT"` sentinel when no key is pressed within the timeout window, and handling it in `choose_action()` as a re-render trigger.
**Inputs:** `menu.py` — `get_key()` function, `choose_action()` function; `msvcrt` (Windows), `select` (Unix); both standard library.
**Outputs:** Modified `get_key(timeout=None)` with platform-specific timeout logic; modified `choose_action()` passing `timeout=_REFRESH_TIMEOUT_S`; new module-level constant `_REFRESH_TIMEOUT_S = 3.0`.
**External Interfaces:** Terminal stdin; `msvcrt.kbhit()` / `msvcrt.getwch()` (Windows); `select.select()` + `tty` / `termios` (Unix).
**Environment & Configuration:** No external config; `_REFRESH_TIMEOUT_S` is the sole tunable.
**Procedure:**
1. Add `_REFRESH_TIMEOUT_S: float = 3.0` at module level (near `_REFRESH_ACTION`).
2. Add `timeout: float | None = None` parameter to `get_key()`.
3. Windows branch: wrap existing `msvcrt.getwch()` call in a polling loop — use `time.monotonic()` deadline; check `msvcrt.kbhit()` every 50 ms (`time.sleep(0.05)`); return `"TIMEOUT"` if deadline expires before a key arrives.
4. Unix branch: before `tty.setraw()`, if `timeout` is set, call `select.select([sys.stdin], [], [], timeout)`; if the result list is empty, restore terminal settings and return `"TIMEOUT"`; otherwise proceed with the existing `sys.stdin.read(1)` flow.
5. In `choose_action()`, update both `get_key()` call sites to `get_key(timeout=_REFRESH_TIMEOUT_S)` and add `if key == "TIMEOUT": continue` (re-render loop) before the existing key-dispatch block.
**Done Criteria:** With no keypress, `choose_action()` re-renders the menu every ~3 seconds; existing key handling (UP/DOWN/ENTER/DIGIT/QUIT) is unaffected.
**Dependencies:** Task 3 (render pipeline stable before wiring auto-refresh).
**Risk Notes:** `time.sleep(0.05)` in the Windows polling loop introduces ~50 ms maximum overshoot on the timeout; acceptable for a 3-second interval.

## Testing

- T1 — clear_screen uses no subprocess: Patch `os.system` and call `clear_screen()`; assert `os.system` was NOT called. Expected outcome: `os.system` call count is 0.

- T2 — clear_screen writes ANSI escape to stdout: Redirect `sys.stdout` to a `StringIO`; call `clear_screen()`; assert the written string contains `\033[H` and `\033[J`. Expected outcome: ANSI sequences present in stdout capture.

- T3 — render_menu produces single write: Patch `sys.stdout.write`; call `render_menu(state, actions, 0)`; assert `sys.stdout.write` was called exactly once. Expected outcome: call count equals 1.

- T4 — render_menu output contains active request text: Capture stdout; call `render_menu` with a state containing a known request ID; assert the rendered output contains the request ID string. Expected outcome: request ID appears in the single write output.

- T5 — render_menu output contains "No active request" when state is empty: Capture stdout; call `render_menu` with `MenuState(None, None, None)`; assert output contains "No active request". Expected outcome: string present in output.

- T6 — existing test_menu tests pass unchanged: Run the full `tests/test_menu.py` suite. Expected outcome: all tests pass with zero failures or errors.

- T7 — get_key returns TIMEOUT when timeout elapses with no input (Unix): Patch `select.select` to return `([], [], [])`; call `get_key(timeout=0.1)`; assert return value is `"TIMEOUT"`. Expected outcome: `"TIMEOUT"` string returned, no stdin read attempted.

- T8 — get_key returns TIMEOUT when timeout elapses with no input (Windows): Patch `msvcrt.kbhit` to always return `0`; call `get_key(timeout=0.1)`; assert return value is `"TIMEOUT"`. Expected outcome: `"TIMEOUT"` string returned within the timeout window.

- T9 — choose_action re-renders on TIMEOUT without selecting action: Patch `get_key` to return `"TIMEOUT"` once then `"QUIT"`; call `choose_action()`; assert no action is returned and `render_menu` was called at least twice. Expected outcome: loop iterates on TIMEOUT; exits cleanly on QUIT.

- T10 — keyboard navigation does not blink (manual verification): Launch menu in Windows Terminal; press UP/DOWN keys repeatedly; observe no blank-screen flash between renders. Expected outcome: menu updates smoothly with no visible white flash.

- T11 — auto-refresh updates active request display: With menu running, close the active request externally (via `close-request.py`); wait 3 seconds without pressing any key; observe the "Active request" line update to "No active request". Expected outcome: menu reflects the new state after the auto-refresh cycle.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — update the AIB Command Menu component description to reflect that the menu now uses ANSI in-place rendering instead of subprocess-based screen clear, and that the menu auto-refreshes every 3 seconds when the user is idle.

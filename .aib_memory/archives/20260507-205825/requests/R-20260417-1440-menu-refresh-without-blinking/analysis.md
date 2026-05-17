# Analysis: Menu refresh without blinking

## Executive Summary

- **Request ID:** R-20260417-1440

- **Request title:** Menu refresh without blinking

- **High-level purpose:** Eliminate the blank-screen flash caused by `os.system("cls"/"clear")` in `clear_screen()` and add idle auto-refresh every 3 seconds so the active request status stays current even when the user is not actively navigating.

- **Scope interpretation:** The original request excluded background polling threads for auto-refresh. Input provided via `input.md` during this analysis run explicitly requested a 3-second auto-refresh when the user is idle. This is achieved via a non-blocking `get_key(timeout)` mechanism — no background threads required. The "Background polling threads" exclusion has been removed from Out of scope accordingly.

- **Key technical decisions:**
  - Replace `os.system("cls"/"clear")` with `sys.stdout.write("\033[H\033[J")` after enabling ANSI VT processing on Windows via `ctypes`.
  - Buffer the full menu output in `io.StringIO` and write in a single `sys.stdout.write()` call per render cycle.
  - Add `timeout` parameter to `get_key()` using `msvcrt.kbhit()` polling (Windows) and `select.select()` (Unix). Return `"TIMEOUT"` sentinel on expiry.
  - Wire `choose_action()` to call `get_key(timeout=_REFRESH_TIMEOUT_S)` and re-render on `"TIMEOUT"`.

- **`request.md` changes made in this run:** Scope expanded (auto-refresh via `get_key()` timeout, `choose_action()` TIMEOUT handling, `_REFRESH_TIMEOUT_S` constant); Out of scope updated (background thread exclusion removed); Constraints updated (constant naming); Success criteria updated (criterion 6 added); Assumptions fully replaced; Plan fully replaced; Testing fully replaced; Documentation fully replaced.

- **Risks:** ANSI fallback on legacy Windows (pre-1511); CPU cost of 50 ms polling; `select.select()` interaction with raw mode on some Unix implementations.

---

## Domain Knowledge Essentials

- **AIB Interactive Menu:** The terminal-based launcher (`menu.py`) that presents copy-paste prompt invocations and discovered tool scripts. Controlled by keyboard (UP/DOWN/ENTER/DIGIT/QUIT).

- **Active Request:** The single request in state `Active` tracked in `requests_register.md`. The menu displays its ID and title (or "No active request") on every render.

- **Render cycle:** The sequence: read state → build action list → clear screen → print menu → wait for keypress. Triggered on every keypress or on timeout expiry (after this request).

- **Blink / flash:** The brief moment where the terminal shows a blank screen between `cls`/`clear` and the subsequent content write. Perceived as a white or black flash by the user; degrades perceived responsiveness.

- **Idle / idle auto-refresh:** A period during which the user has not pressed any key. Auto-refresh ensures the menu re-reads workspace state and re-renders itself even without user input, so an externally-created or externally-closed request becomes visible without a manual keypress.

- **Impacted role/persona:** Developer — the primary user who navigates the menu to launch AIB tool scripts.

- **Business process touched:** "AIB Command Menu" — one of the six core AIB processes defined in the architecture.

- **Acceptance impact:** UX and responsiveness — eliminating visual noise and enabling automatic state updates improves menu polish without changing functional behaviour.

---

## Technical Knowledge & Terms

- **ANSI escape sequence:** A sequence of bytes starting with `ESC` (`\033`) used to control cursor position, screen clearing, and text styling in ANSI-compatible terminals.

- **`\033[H`:** ANSI CSI cursor-home sequence — moves the cursor to row 1, column 1 without erasing content.

- **`\033[J`:** ANSI CSI erase-from-cursor-to-end-of-screen sequence — erases all content from the current cursor position to the bottom of the screen. Combined with `\033[H`: positions cursor at top-left, then erases all visible content.

- **`ENABLE_VIRTUAL_TERMINAL_PROCESSING` (0x0004):** A Windows console mode flag that enables ANSI/VT100 escape sequence processing in `cmd.exe` and PowerShell windows. Available from Windows 10 version 1511 onwards.

- **`ctypes.windll.kernel32.SetConsoleMode`:** Win32 API function that sets the console output mode flags, used to enable VT processing. Must be called after `GetStdHandle(-11)` (STD_OUTPUT_HANDLE) to obtain the console handle.

- **`io.StringIO`:** Python standard-library in-memory string buffer. Used here to accumulate the entire menu output string before issuing a single `sys.stdout.write()`, preventing intermediate partial-renders.

- **`msvcrt.kbhit()`:** Windows-only standard-library function that returns non-zero if a keypress is waiting in the console input buffer. Non-blocking; used in a polling loop to implement a timeout on `get_key()`.

- **`msvcrt.getwch()`:** Windows-only standard-library function that reads a wide character from the console without echoing it. Blocking; only called after `kbhit()` confirms a key is available.

- **`select.select(rlist, wlist, xlist, timeout)`:** POSIX I/O multiplexing call from Python's `select` standard-library module. When called with `[sys.stdin]` in `rlist` and a numeric `timeout`, returns an empty list if no data arrives within the timeout — enabling a clean non-blocking key read on Unix.

- **`tty.setraw(fd)` / `termios.tcgetattr` / `tcsetattr`:** Unix standard-library utilities to switch a terminal file descriptor to raw mode (no line-buffering, no echo), enabling character-by-character input reading. Original settings must be restored in a `finally` block covering all paths.

- **`"TIMEOUT"` sentinel:** A new string return value added to `get_key()` indicating that no key was pressed within the timeout window. Handled in `choose_action()` as a re-render trigger (loop continues without selecting an action).

- **`_REFRESH_TIMEOUT_S`:** A module-level float constant in `menu.py` defining the auto-refresh interval in seconds (3.0). Externalising the value allows tests and future callers to control it without modifying inline logic.

- **Files read during analysis:**
  - `.aib_brain/tools/menu.py` — primary implementation target; analysed for `clear_screen()`, `render_menu()`, `get_key()`, and `choose_action()` structure and call sites.
  - `tests/test_menu.py` — reviewed to understand existing test contracts, patching patterns, and required backward-compatibility constraints.
  - `.aib_memory/context.md` — product context, component map, NFRs (NFR-004: standard library only, Python 3.10+).
  - `.aib_brain/Concepts.md` — invocation contract, action matrix, workflow guardrails.
  - `.aib_memory/references.md` — reference register; identified REF-0001 (`context.md`) as the only documentation update target.

---

## Research Results

**Pattern: subprocess-based screen clear vs. ANSI in-place update**

- Evidence → Implication: `os.system("cls")` in `clear_screen()` spawns a new process (~10–30 ms overhead on Windows); the subprocess-exit-to-Python-write gap is the observable blink. `sys.stdout.write("\033[H\033[J")` writes directly to the same file descriptor with no subprocess gap, eliminating the blank-screen window.

**Pattern: Single-write buffered render**

- Evidence → Implication: `render_menu()` currently calls `print()` 10–20 times (banner + menu items). Each `print()` flushes individually, creating a top-to-bottom "paint" effect. Buffering into `io.StringIO` and issuing one `sys.stdout.write()` reduces the observable partial-render window to near zero.

**Pattern: Non-blocking key read with timeout for idle auto-refresh**

- Evidence → Implication: `choose_action()` calls `get_key()` which blocks indefinitely. Providing an optional `timeout` parameter (Windows: `kbhit()` poll at 50 ms intervals; Unix: `select.select()`) allows the loop to time out after 3 seconds and re-render — implementing auto-refresh without background threads.

**Pattern: Windows ANSI enablement via ctypes**

- Evidence → Implication: Windows console windows do not process ANSI sequences by default in all configurations. `SetConsoleMode` with `ENABLE_VIRTUAL_TERMINAL_PROCESSING` is the recommended enablement path. Windows Terminal (modern default) already processes ANSI, making the call a harmless no-op there; it specifically helps legacy `cmd.exe`. Wrapping in `try/except` ensures no failure on non-Windows or restricted environments.

**Backward compatibility with `test_menu.py`**

- Evidence → Implication: The test suite patches `clear_screen` by exact name. The function name and `() -> None` signature must be preserved. Task 2 preserves both. `get_key()` has no existing unit tests, so adding a `timeout=None` keyword argument is fully backward-compatible.

---

## External Benchmarking

- **`tqdm` progress bar library (Python):** Uses `sys.stdout.write("\r" + content)` and avoids `os.system("clear")` entirely. Confirms that writing to stdout directly with cursor-control sequences is the standard approach for flicker-free terminal updates in Python. **Adopted** — same principle applied here with `\033[H\033[J`.

- **`htop` (C, Unix) and `top` (C, Unix):** Both use `ncurses` for full-screen rendering with no flicker. Demonstrate that in-place screen updates via terminal escape sequences are the industry standard for TUI applications. **Adapted** — curses is excluded by constraint; the ANSI escape sequence approach replicates the core principle without the curses dependency.

- **`click` library's `clear()` function:** Calls `os.system("cls"/"clear")` — the same approach as the current `clear_screen()`. Explicitly documented as producing a flash on some terminals. This benchmarks the current state as a known deficiency in the Python CLI ecosystem; the ANSI approach is the recognised upgrade path. **Rejected as a dependency** (standard library only); the pattern it uses is what we are replacing.

- **Python `select` module timeout pattern (POSIX standard):** Used by `asyncio`, `xmlrpc.server`, and many CPython internals for non-blocking I/O. The pattern `select.select([fd], [], [], timeout)` returning an empty list on expiry is idiomatic and well-tested across platforms. **Adopted** for the Unix `get_key(timeout)` implementation.

- **`msvcrt.kbhit()` polling pattern (Windows stdlib):** Used by numerous Windows Python CLI utilities for non-blocking keyboard reads. Polling at 50 ms intervals provides a maximum timeout overshoot of 50 ms — well within the human perception threshold for a 3-second interval. **Adopted** for the Windows `get_key(timeout)` implementation.

---

## Minimal Spikes and Experiments

- **Spike: ANSI VT processing via ctypes on Windows**
  - Hypothesis: Calling `SetConsoleMode` with `ENABLE_VIRTUAL_TERMINAL_PROCESSING` is sufficient to make `\033[H\033[J` clear the screen on Windows 10+ without visible flash.
  - Approach: Static code analysis of Python standard library `ctypes` usage patterns; review of Microsoft Win32 Console API documentation for `SetConsoleMode` / `GetConsoleMode`.
  - Outcome: Confirmed. The flag value `0x0004` is stable since Windows 10 v1511 (build 10586). The approach is used by `pip` and documented in Microsoft's VT terminal sequence reference.
  - Conclusion: Implementation is: `GetStdHandle(-11)` → `GetConsoleMode` → OR with `0x0004` → `SetConsoleMode`. Wrap in `try/except` for graceful fallback on pre-1511 Windows or non-Windows platforms.

- **Spike: Backward compatibility of adding `timeout=None` to `get_key()`**
  - Hypothesis: Adding `timeout=None` as a keyword argument to `get_key()` preserves all existing callers, since `choose_action()` is the only caller and calls `get_key()` with no arguments.
  - Approach: Full text search of `menu.py` for all occurrences of `get_key(`.
  - Outcome: Confirmed. `choose_action()` contains the only two call sites of `get_key()`, both with no arguments. Adding `timeout=None` is fully backward-compatible; default behaviour is unchanged.
  - Conclusion: No caller modifications required for existing call sites; Task 4 then updates `choose_action()` to pass `timeout=_REFRESH_TIMEOUT_S`.

- **Spike: `select.select()` interaction with `tty.setraw()` on Unix**
  - Hypothesis: `select.select([sys.stdin], [], [], 3.0)` correctly reports stdin readability when a key is pressed while in `tty.setraw()` mode.
  - Approach: Review of POSIX specification for `select(2)` with respect to raw-mode ttys; examination of CPython `tty` module source.
  - Outcome: Confirmed. POSIX guarantees that `select` reflects readability of the underlying file descriptor regardless of terminal mode; `tty.setraw()` does not affect `select` semantics.
  - Conclusion: Implementation order must be: `tty.setraw()` first, then `select.select()`, then `sys.stdin.read(1)`, with `tcsetattr` restore in the `finally` block covering all code paths.


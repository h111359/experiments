# Executive Summary

- Request ID: R-20260403-1844

- Request title: Bugfixing - error in cli analysis prompt execution

- Iteration ID: 01

- High-level purpose: Diagnose and fix a `UnicodeDecodeError` that crashes the AIB Command Menu (`menu.py`) when the GitHub Copilot CLI subprocess emits non-ASCII UTF-8 bytes on Windows, and improve observability so such streaming-thread failures are captured in the per-action execution log file.

- The error originates in `_stream_pipe` (menu.py, line ~104). The `subprocess.Popen` call in `_run_and_tee` uses `text=True` without specifying `encoding="utf-8"`. On Windows, Python defaults to the system code page (`cp1252`), which cannot decode certain UTF-8 byte sequences (e.g., `0x8f`), leading to a `UnicodeDecodeError`.

- The secondary issue is that the crash in the streaming thread is never written to the per-action log file. The `_stream_pipe` function's `try/finally` block only closes the pipe; it does not catch and record the exception. The threading infrastructure prints the traceback to stderr, but since the stderr streaming thread is also crashing for the same reason, the error is lost.

- This is iteration 01; no prior iterations exist for this request.

- No conflicts with earlier iterations.

# Scope Interpretation

- **In scope (explicit):** Diagnose the `UnicodeDecodeError` in `_stream_pipe` when Copilot CLI emits non-ASCII output on Windows.

- **In scope (explicit):** Fix the encoding issue so the menu handles UTF-8 subprocess output correctly.

- **In scope (explicit):** Investigate why the error is not captured in the per-action execution log file and fix the logging gap.

- **In scope (explicit):** If the root cause cannot be fully resolved, improve logging/observability so future failures produce actionable diagnostic evidence.

- **In scope (implicit rule - AIB framework):** Update affected product documentation (OBS-01, CMP-01) to reflect any changes to logging behavior or script catalog entries.

- **In scope (implicit rule - AIB framework):** Add or update automated tests covering the fix.

- **Out of scope (explicit):** No out-of-scope items explicitly stated in the request; the following are excluded by domain irrelevance: changes to non-menu tool scripts, Copilot CLI internals, upstream Python threading bugs.

# Domain Knowledge Essentials

- **AIB Command Menu (TERM-0013 / CMP-ART-0006):** Interactive terminal launcher (`menu.py`) that exposes tool scripts and prompt actions. Prompt actions invoke GitHub Copilot CLI (`copilot -p`) as a subprocess and stream stdout/stderr to the terminal in real time while simultaneously writing to a per-action log file.

- **Prompt Action:** A menu entry that maps to a `.aib_brain/prompts/aib-*.md` file. When Copilot CLI is detected, the action is executable; otherwise it is displayed as informational only.

- **Per-action execution log:** A flat-text file at `logs/aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log` containing `[START]`, `[CMD]`, `[OUT]`, `[ERR]`, and `[EXIT]` markers (OBS-01).

- **Impacted personas:** DEVELOPER (runs the menu daily), MAINTAINER (owns `.aib_brain` assets and menu.py).

- **Business process touched:** The "Create Analysis" prompt action flow (UC, SEQ-004) — the user selects a prompt action from the menu, menu.py spawns Copilot CLI, streams output, and writes to the log.

- **Acceptance impact:** When the bug triggers, the entire streaming pipeline crashes. The user sees an unhandled traceback on the terminal, no useful output is captured, and the log file is incomplete (missing `[OUT]`/`[ERR]`/`[EXIT]` lines). The developer cannot use prompt actions in workspaces where the Copilot CLI emits non-ASCII content.

# Technical Knowledge & Terms

- **`subprocess.Popen` with `text=True`:** Opens subprocess pipes in text mode. If no `encoding` keyword is provided, Python uses `locale.getpreferredencoding(False)`, which returns `cp1252` on most Western Windows systems.

- **`cp1252` (Windows-1252):** A single-byte character encoding that covers Latin characters. Byte values `0x81`, `0x8D`, `0x8F`, `0x90`, `0x9D` are undefined and cause `UnicodeDecodeError` if encountered.

- **UTF-8:** Variable-width encoding used by Copilot CLI and most modern tools. Multi-byte sequences can contain byte values that are undefined in cp1252.

- **`_stream_pipe`:** A function executed in a `threading.Thread`; reads a pipe line-by-line and writes each line to both a destination stream (stdout/stderr) and a log file. Located at menu.py line ~99.

- **`_run_and_tee`:** Orchestrator function that spawns `Popen`, creates two threads (one per pipe), waits for process completion, and writes the `[EXIT]` marker. Located at menu.py line ~111.

- **`threading.Thread` exception handling:** Uncaught exceptions in thread targets are caught by `Thread._bootstrap_inner`, which prints the traceback to `sys.stderr`. They do not propagate to the join()-ing thread.

- **Popen tee pattern:** The design pattern used by menu.py to simultaneously stream subprocess output to terminal and to a log file via pipe-reading threads.

- **`encoding` parameter of `Popen`:** When provided alongside `text=True`, overrides the default encoding for all pipes (stdout, stderr, stdin). Available since Python 3.6.

- **`errors` parameter of `Popen`:** When provided alongside `text=True` and `encoding`, specifies how encoding/decoding errors are handled (e.g., `"replace"`, `"backslashreplace"`). Provides resilience against unexpected byte sequences.

# Assumptions

- Assumption A1: The GitHub Copilot CLI outputs UTF-8 encoded text on all platforms.
    - Rationale: Modern CLI tools, including GitHub CLI and Copilot extensions, default to UTF-8. The error byte `0x8f` is consistent with a UTF-8 multi-byte character misinterpreted as cp1252.
    - Risk if false: If Copilot CLI uses a different encoding on some systems, the fix would need an encoding-detection layer or a configurable encoding parameter.
    - Falsification method: Run `copilot -p "echo non-ascii"` on multiple Windows systems and inspect raw byte output.

- Assumption A2: Adding `encoding="utf-8"` to the `Popen` call is sufficient; the `errors` parameter default (`"strict"`) is acceptable for normal operation.
    - Rationale: UTF-8 is self-synchronizing and Copilot CLI output should be valid UTF-8. Strict mode surfaces any true encoding mismatch immediately.
    - Risk if false: A rare malformed byte sequence would still crash the thread.
    - Falsification method: Add `errors="replace"` as an additional safety net and test with deliberately malformed output.

- Assumption A3: The log file is always writable when an exception occurs in `_stream_pipe`, i.e., the `log_file` handle is still open and its `write` method is callable.
    - Rationale: `_stream_pipe` is called within the `with open(log_path, ...)` context manager in `_run_and_tee`, so the log file remains open for the lifetime of the subprocess.
    - Risk if false: If the log file is closed prematurely, the exception-logging enhancement would also fail.
    - Falsification method: Review the `_run_and_tee` function's context manager scope; confirmed it covers the thread join.

- Assumption A4: The multiple `▶ Running copilot CLI...` messages in the terminal output indicate the user triggered the prompt action multiple times from the menu, not a single invocation spawning multiple processes.
    - Rationale: Each invocation of `run_prompt_action` prints this message once. The menu returns to the selection loop after failure.
    - Risk if false: If a single invocation can print multiple copies, there may be a re-entry or loop bug.
    - Falsification method: Code review of `run_prompt_action` and `choose_action`; confirmed one message per invocation.

# Impact Assessment

## Affected Components / Areas

- **AIB Command Menu** (`menu.py`, CMP-ART-0006): The `_stream_pipe` and `_run_and_tee` functions require modification.
- **Test suite** (`tests/test_menu.py`, CMP-ART-0008): New tests needed for UTF-8 subprocess output and error-in-thread logging.
- **OBS-01 logging** (action execution logs): The log schema may gain a new marker (e.g., `[THREAD-ERROR]`) or an `[ERR]` annotation for thread exceptions.

## Change Type and Dependencies

- `menu.py` / `_run_and_tee`: **modify** — add `encoding="utf-8"` (optionally `errors="replace"`) to `Popen`.
- `menu.py` / `_stream_pipe`: **modify** — add exception handling that writes the error to the log file.
- `tests/test_menu.py`: **modify** — add tests for UTF-8 output and thread-exception logging.
- Internal dependency: `_stream_pipe` ← `_run_and_tee` ← `run_prompt_action` / `run_action`.
- No external dependencies affected.

## Domain Impacts

- DOMAIN (ARCH): No structural architecture change. The Popen tee pattern is preserved.

- DOMAIN (CMP): CMP-ART-0006 (AIB Command Menu) edge_cases_and_validation column should note UTF-8 encoding enforcement.
    - Relevant requirement IDs: CMP-ART-0006

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): No impact detected.

- DOMAIN (RQT): FR-008 (interactive menu with real-time output streaming) is affected — the fix ensures FR-008 works on Windows when non-ASCII output is present.
    - Relevant requirement IDs: FR-008

- DOMAIN (OBS): OBS-01 (logging) — the log event schema may need amendment if a `[THREAD-ERROR]` marker is introduced; at minimum, the convention should note that thread exceptions are now captured.
    - Relevant requirement IDs: OBS-01

- DOMAIN (SEC): No impact detected.

- DOMAIN (OPR): No impact detected.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (DEV): No impact detected.

## Constraints

- Python 3.10+ compatibility must be maintained (NFR-004).
- The fix must not break existing tests in `tests/test_menu.py`.
- The fix must not alter the log file format in a way that breaks existing parsing expectations unless the new marker is additive.
- The `_stream_pipe` function is called from daemon threads; any exception handling must be thread-safe (use the existing `lock`).

## Required Documentation Updates

- OBS-01 - Logging
    Required update? YES
    Reason: If a `[THREAD-ERROR]` marker is added or if the exception-logging behavior changes, OBS-01 must document it.

- CMP-01 - Notebook/Script Catalog
    Required update? YES
    Reason: CMP-ART-0006 edge_cases_and_validation should note UTF-8 encoding enforcement on Popen.

## Decision Points

- **DP-1: Should `errors="replace"` be added in addition to `encoding="utf-8"`?**
    - Option A: `encoding="utf-8"` only (strict mode). Surfaces any future encoding mismatch immediately.
    - Option B: `encoding="utf-8", errors="replace"`. Maximum resilience; replaces undecodable bytes with U+FFFD. Slight loss of diagnostic fidelity.
    - Recommended: Option B — the menu is a user-facing tool; crashing the streaming thread on a rare byte is worse than a replacement character. The error is still visible in the output and log.

- **DP-2: Should a new log marker `[THREAD-ERROR]` be introduced, or should thread exceptions be logged under the existing `[ERR]` prefix?**
    - Option A: New `[THREAD-ERROR]` marker. Explicit distinction from subprocess stderr.
    - Option B: Reuse `[ERR]` prefix. Simpler; no schema change needed.
    - Recommended: Option A — the distinction is valuable for debugging. Thread errors are infrastructure failures, not subprocess output.

# Research Plan and Findings

## Methodology

1. Internal docs scan: read request.md, iterations.md, Concepts.md, references.md, analysis-convention.md, request-convention.md.
2. Product-doc scan: read all product-doc files listed in references.md for contextual understanding.
3. Source code analysis: read menu.py (full file), common.py, and test_menu.py to identify the root cause, trace the error, and assess existing test coverage.
4. Pattern matching: compared the Popen call with Python standard library documentation for `encoding` parameter behavior.

## Evidence Summary

| Evidence | Implication |
| --- | --- |
| Traceback: `cp1252.py line 23, UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f` | Popen is using system default encoding (cp1252) instead of UTF-8 |
| `menu.py` line ~130: `subprocess.Popen(..., text=True)` with no `encoding` kwarg | Confirmed root cause — missing `encoding="utf-8"` |
| `_stream_pipe` has `try/finally` but no `except` block | Thread exception is not caught or logged; explains why error is absent from log file |
| Log file shows only `[START]` and `[CMD]` markers | The stdout/stderr streaming threads crashed before writing any `[OUT]`/`[ERR]` lines; `[EXIT]` may or may not have been written depending on timing |
| `test_menu.py` has `TestRunAndTee` class with 7 tests | No test covers non-ASCII subprocess output or thread exception scenarios |

## Gaps and Unknowns

- Cannot verify from the provided evidence whether the `[EXIT]` marker was written to the log (only the beginning of the log was shown).
- Cannot determine the exact non-ASCII character that Copilot CLI emitted (byte `0x8f` is in position 2 of some output line).

## Proposed Validation Actions

- After the fix: run the menu in a workspace where Copilot CLI emits non-ASCII characters and verify the output streams correctly.
- Add automated tests that simulate non-ASCII subprocess output.

## Files Read

- `.aib_memory/requests/R-20260403-1844-bugfixing-error-in-cli-analysis-prompt-execution/request.md` — Contains the terminal traceback and log excerpt showing the UnicodeDecodeError and incomplete log file.
- `.aib_memory/requests/R-20260403-1844-bugfixing-error-in-cli-analysis-prompt-execution/iterations.md` — Confirmed iteration 01 is Active.
- `.aib_memory/requests/R-20260403-1844-bugfixing-error-in-cli-analysis-prompt-execution/implementation.md` — Empty; no prior implementation.
- `.aib_memory/references.md` — Built the required-read set of 27 product-doc files.
- `.aib_memory/requests_register.md` — Confirmed R-20260403-1844 is the single Active request.
- `.aib_brain/Concepts.md` — Reviewed AIB framework concepts, lifecycle model, and invocation contract.
- `.aib_brain/conventions/analysis-convention.md` — Loaded analysis structure requirements.
- `.aib_brain/conventions/request-convention.md` — Loaded request rewrite requirements.
- `.aib_brain/tools/menu.py` — Full file read; identified root cause at Popen call (line ~130) and _stream_pipe (line ~99).
- `.aib_brain/tools/common.py` — Reviewed shared helpers; confirmed `read_text`/`write_text` use `encoding="utf-8"`.
- `tests/test_menu.py` — Reviewed all existing tests; confirmed no UTF-8/encoding coverage.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Confirmed AIB Command Menu component description and Popen tee pattern reference.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — Confirmed SEQ-004 scenario for prompt action execution.
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — Confirmed log marker schema and UTF-8 encoding specification.
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Confirmed CMP-ART-0006 entry for menu.py.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Reviewed glossary for relevant terms (TERM-0013 Prompt Action).
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — Confirmed resource catalog; no changes needed.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — Confirmed FR-008 requirement for interactive menu with streaming.
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — Confirmed DEVELOPER and MAINTAINER personas.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — [SKIPPED — domain out of scope] Topology/network; placeholder content only.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — [SKIPPED — domain out of scope] Capacity model; no relevance to encoding bug.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — [SKIPPED — domain out of scope] ADRs; no active ADR for this topic.
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — [SKIPPED — domain out of scope] Algorithm specification; not applicable.
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — [SKIPPED — domain out of scope] Data ingestion; not applicable.
- `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — [SKIPPED — domain out of scope] Data models; not applicable.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — [SKIPPED — domain out of scope] Data lineage; not applicable.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — [SKIPPED — domain out of scope] Data storage; not applicable.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — [SKIPPED — domain out of scope] Data consumption; not applicable.
- `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — [SKIPPED — domain out of scope] Metrics catalog; not applicable.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — [SKIPPED — domain out of scope] Data quality; not applicable.
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — [SKIPPED — domain out of scope] Data archiving; not applicable.
- `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — [SKIPPED — domain out of scope] Dashboard inventory; not applicable.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — [SKIPPED — domain out of scope] Business process catalog.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — [SKIPPED — domain out of scope] Access management; not applicable.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — [SKIPPED — domain out of scope] Infrastructure data protection; not applicable.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — [SKIPPED — domain out of scope] Secrets management; not applicable.
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — [SKIPPED — domain out of scope] Network security; not applicable.
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — [SKIPPED — domain out of scope] Product charter; no direct relevance.

# Rewrite Proposal of the Request

## Goal

Fix the `UnicodeDecodeError` in `.aib_brain/tools/menu.py` that crashes the AIB Command Menu's streaming threads (`_stream_pipe`) when the GitHub Copilot CLI subprocess emits non-ASCII UTF-8 characters on Windows. Additionally, fix the logging gap that prevents thread exceptions from being captured in the per-action execution log file (`logs/aib-action-*.log`).

## Background

The AIB Command Menu (`menu.py`, CMP-ART-0006) uses `subprocess.Popen` with `text=True` in the `_run_and_tee` function to spawn Copilot CLI and tee its output. On Windows, `text=True` without an explicit `encoding` parameter defaults to the system code page `cp1252`. When Copilot CLI outputs UTF-8 multi-byte characters (e.g., byte `0x8f`), `cp1252` cannot decode them, causing `UnicodeDecodeError` in the `_stream_pipe` threading target. The exception kills the streaming thread, and because `_stream_pipe` has no exception handler that writes to the log, the error is never recorded in the log file.

Evidence from a separate test workspace (`ai-builder-test-07`):
- Terminal output: `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8f in position 2: character maps to <undefined>`
- Log file: contains only `[START]` and `[CMD]` markers; no `[OUT]`, `[ERR]`, or error information.

## Scope

- Modify `_run_and_tee` in `.aib_brain/tools/menu.py` to add `encoding="utf-8"` and `errors="replace"` to the `subprocess.Popen` call.
- Modify `_stream_pipe` in `.aib_brain/tools/menu.py` to catch exceptions (including but not limited to `UnicodeDecodeError`) and write them to the log file under a `[THREAD-ERROR]` marker before re-raising or terminating the thread.
- Add automated tests in `tests/test_menu.py` covering: (a) subprocess output with non-ASCII UTF-8 characters streamed correctly; (b) thread exception caught and logged to the log file.
- Update product documentation OBS-01 to document the `[THREAD-ERROR]` log marker.
- Update product documentation CMP-01 (CMP-ART-0006) to note UTF-8 encoding enforcement.

## Out of scope

- Changes to Copilot CLI itself or its output encoding.
- Changes to non-menu tool scripts (initialize.py, create-request.py, etc.).
- Changes to the Python threading module or standard library.
- Platform-specific encoding detection or configuration.

## Constraints

- Python 3.10+ compatibility must be maintained (NFR-004).
- All existing tests in `tests/test_menu.py` must continue to pass.
- The log file format change (new `[THREAD-ERROR]` marker) must be additive — existing `[START]`, `[CMD]`, `[OUT]`, `[ERR]`, `[EXIT]` markers are unchanged.
- The `_stream_pipe` exception handler must be thread-safe (use the existing `lock` for log writes).

## Success criteria

- The AIB Command Menu successfully streams Copilot CLI output containing non-ASCII UTF-8 characters without crashing on Windows.
- Thread exceptions in `_stream_pipe` are written to the per-action log file with a `[THREAD-ERROR]` marker.
- The `[EXIT]` marker is always written to the log file, even when streaming threads fail.
- All existing tests pass; at least 2 new tests verify the encoding fix and the exception-logging fix.
- OBS-01 and CMP-01 documentation are updated to reflect the changes.

# Solution Options

## Option A: Minimal Encoding Fix

**Overview:** Add `encoding="utf-8"` to the `Popen` call in `_run_and_tee`. No change to exception handling in `_stream_pipe`.

**Benefits:**
- Smallest possible change; eliminates the root cause.
- No new log markers or schema changes.

**Trade-offs:**
- Does not address the logging gap. If any other exception occurs in `_stream_pipe` in the future, it will again be invisible in the log.
- Does not add resilience against malformed UTF-8 (strict mode).

**Constraints:** None beyond baseline.

**Risks:**
- Future exceptions in streaming threads remain unlogged.

**Expected effort:** Very low (single line change + 1 test).

**Acceptance-test ideas:**
- Test that subprocess emitting UTF-8 non-ASCII is streamed without error.

## Option B: Encoding Fix + Exception Logging + Resilient Decoding (Recommended)

**Overview:** Add `encoding="utf-8", errors="replace"` to the `Popen` call. Add exception handling in `_stream_pipe` that catches exceptions, writes a `[THREAD-ERROR]` entry to the log file (thread-safe via the existing lock), and then terminates the thread gracefully. Update OBS-01 and CMP-01 documentation.

**Benefits:**
- Eliminates the root cause.
- `errors="replace"` provides resilience against any unexpected byte sequence (replaces with U+FFFD).
- Thread exceptions are now observable in the log file, enabling future diagnostics.
- Documentation stays accurate.

**Trade-offs:**
- Introduces a new log marker `[THREAD-ERROR]` — minor schema addition.
- `errors="replace"` silently replaces bad bytes rather than failing loudly. This is acceptable for a user-facing streaming tool.

**Constraints:** Log format addition must be documented in OBS-01.

**Risks:**
- If `errors="replace"` masks a real encoding mismatch, the user sees `�` instead of the intended character. This is preferable to a crash.

**Expected effort:** Low (modify 2 functions in menu.py, add 2–3 tests, update 2 docs).

**Acceptance-test ideas:**
- Test that subprocess emitting UTF-8 non-ASCII is streamed without error and appears in log.
- Test that a simulated exception in `_stream_pipe` is captured in the log under `[THREAD-ERROR]`.
- Test that `[EXIT]` is written even if a streaming thread fails.

**Recommendation:** Option B. It addresses both the immediate bug and the systemic observability gap, with minimal additional complexity.

# Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | CMP-ART-0006 edge_cases_and_validation must note UTF-8 encoding enforcement on Popen |
| REF-0021 | OBS-01 - Logging | .aib_memory/docs/04 Technology/Observability/OBS-01.md | Log event schema must document the new [THREAD-ERROR] marker |

# Operational & Documentation Implications

- **Runbooks:** No change. The existing procedure ("open the most recent `logs/aib-action-*.log` file") remains valid; developers now gain additional diagnostic data from `[THREAD-ERROR]` entries.

- **SLAs/SLOs:** No change. AIB operates locally; no service-level commitments are affected.

- **Monitoring/observability/logging/alerts/dashboards:** The per-action log file schema gains an additive `[THREAD-ERROR]` marker. OBS-01 must be updated to document this marker (see Affected Documentation above).

- **Data quality rules:** No change.

- **Product documentation artifacts:**
    - OBS-01: Add `[THREAD-ERROR]` to the log event schema table and taxonomy.
    - CMP-01: Update CMP-ART-0006 `edge_cases_and_validation` to note `encoding="utf-8", errors="replace"` on Popen.

# Risks

- Risk R1: Copilot CLI uses an encoding other than UTF-8 on some Windows configurations.
    - Probability: Low
    - Impact: Medium — the fix would not decode output correctly; `errors="replace"` would produce replacement characters.
    - Mitigation: UTF-8 is the documented default for modern CLI tools. The `errors="replace"` parameter prevents crashes. If encountered, a follow-up can add encoding auto-detection.
    - Owner (role): MAINTAINER

- Risk R2: The `[THREAD-ERROR]` marker introduces a breaking change for any external log-parsing tooling.
    - Probability: Low
    - Impact: Low — no known external tooling parses AIB action logs; the marker is additive.
    - Mitigation: Document the marker in OBS-01. Existing markers remain unchanged.
    - Owner (role): MAINTAINER

- Risk R3: `errors="replace"` silently masks genuine encoding problems, leading to corrupted output without user awareness.
    - Probability: Low
    - Impact: Low — the replacement character (U+FFFD `�`) is visually obvious in terminal and log output.
    - Mitigation: Users can inspect the log for `�` characters. If frequent, it indicates a deeper encoding mismatch requiring investigation.
    - Owner (role): DEVELOPER

# Disambiguation Questionnaire

- **Q1: What encoding does the subprocess output use?**
    - Chosen Answer: UTF-8
    - Rationale: Modern CLI tools default to UTF-8; the error byte pattern is consistent with UTF-8 multi-byte sequences misread as cp1252.
    - Evidence / Reference: Terminal traceback in request.md; Python documentation for `subprocess.Popen` encoding behavior.
    - Impact if changed: Would need encoding detection or a configurable encoding parameter.

- **Q2: Should thread exceptions crash the thread or attempt recovery?**
    - Chosen Answer: Log the exception and terminate the thread gracefully (no recovery attempt).
    - Rationale: Once a decoding error occurs mid-stream, the pipe state is unreliable. Logging and terminating is the safest approach.
    - Evidence / Reference: Python threading documentation — unhandled exceptions in threads are caught by `_bootstrap_inner` and printed to stderr.
    - Impact if changed: Attempting recovery (e.g., skip the bad line) could lead to partial/corrupt output in the log.

- **Q3: Should the log marker for thread exceptions be `[ERR]` or a new `[THREAD-ERROR]`?**
    - Chosen Answer: New `[THREAD-ERROR]` marker.
    - Rationale: `[ERR]` is already defined as subprocess stderr content (OBS-01). Thread infrastructure failures are a different category.
    - Evidence / Reference: OBS-01 taxonomy table.
    - Impact if changed: Using `[ERR]` would conflate subprocess errors with infrastructure failures.

- **Q4: Is `errors="replace"` or `errors="backslashreplace"` preferable?**
    - Chosen Answer: `errors="replace"`
    - Rationale: `replace` produces a visible marker character (U+FFFD) that is terminal-friendly. `backslashreplace` produces escape sequences that are harder to read in terminal output.
    - Evidence / Reference: Python codecs documentation.
    - Impact if changed: `backslashreplace` would show `\x8f` instead of `�` — more diagnostic but less user-friendly.

# Open Questions & Next Actions

No open questions remain. The root cause is identified from the provided evidence, the fix strategy is clear, and all decision points have recommended options.

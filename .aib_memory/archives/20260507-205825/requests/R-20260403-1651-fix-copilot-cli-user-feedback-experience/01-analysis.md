# Analysis - Iteration 01

## Executive Summary

- Request ID: R-20260403-1651

- Request title: Fix Copilot CLI User Feedback Experience

- Iteration ID: 01

- High-level purpose: Improve the observability and interactivity of the AIB Command Menu when executing Copilot CLI prompt actions by adding real-time output streaming, file-based logging, user input passthrough, and robust error reporting.

- The current `run_prompt_action()` function in `menu.py` invokes the `copilot` CLI via `subprocess.run()` with `capture_output=True`, which suppresses all output until the process terminates. The user sees a blank screen during long-running AI operations with no feedback on progress, warnings, or errors.

- If the user presses Enter during execution, the keystroke is buffered and consumed by the post-execution `input()` calls or by the menu's `get_key()` loop, potentially causing unintended navigation or skipping result display.

- On failure, only the first line of stderr/stdout and the exit code are shown; full details require an explicit opt-in prompt.

- There is no file-based logging of any kind — neither for script actions nor for prompt actions. Transient terminal output is the only record.

- The `copilot` CLI subprocess cannot request user input because `stdin` is not connected (it is inherited as the default pipe or captured).

- No prior iterations exist for this request.

## Scope Interpretation

- In scope: Modifications to the `run_prompt_action()` function in `.aib_brain/tools/menu.py` to stream output in real time to the terminal and to a log file.

- In scope: Modifications to `run_action()` in `.aib_brain/tools/menu.py` to apply the same real-time streaming and logging for script actions.

- In scope: Introduction of a session log file mechanism under a defined location (e.g., `logs/` or a configurable path) that captures timestamped stdout, stderr, and return codes for every action execution.

- In scope: Connecting `stdin` to the `copilot` subprocess so that the Copilot CLI can prompt the user for input during execution.

- In scope: Protecting the terminal from accidental keystrokes during subprocess execution by either disabling raw-mode key capture or clearly indicating that the process is running.

- In scope: Improving error reporting on failure to include structured output (exit code, full stdout, full stderr) without requiring a secondary opt-in prompt.

- In scope: Updating tests in `tests/test_menu.py` to cover the new streaming and logging behavior.

- In scope: Updating product documentation ARCH-01, CMP-01, OBS-01, ARCH-06 to reflect the new logging and interaction model.

- (implicit rule - AIB framework) Documentation updates for all affected product-doc artifacts referenced in `.aib_memory/references.md`.

- Out of scope: Changing the Copilot CLI itself or its installation/detection mechanism.

- Out of scope: Adding a GUI or web-based interface for observability.

- Out of scope: Modifying GitHub Actions CI workflows or release bookkeeping scripts.

- Out of scope: Adding remote/cloud logging or telemetry.

## Domain Knowledge Essentials

- **AIB Command Menu**: Terminal UI launcher (`menu.py`) that presents script actions (Python tool scripts) and prompt actions (Copilot CLI-driven AI workflows) in a navigable list.

- **Prompt Action**: A menu entry that invokes `copilot -p "Execute the prompt defined in <file>" --allow-all-tools` as a subprocess. Currently the primary pain point — output is invisible during execution.

- **Script Action**: A menu entry that runs a Python tool script (e.g., `create-request.py`) as a subprocess. Shares the same output-capture problem.

- **Developer (DEVELOPER persona)**: The primary user who interacts with the menu from a local terminal. Needs real-time feedback to trust the process, diagnose issues mid-flight, and provide input when the AI requests it.

- **AI Agent (AI_AGENT persona)**: Executes prompt-driven workflows. May need to ask clarifying questions via the terminal during execution.

- **Observability**: Currently limited to release logs (`logs/version_*.md`) and implementation logs. No runtime execution logging exists for menu actions.

## Technical Knowledge & Terms

- **subprocess.run()**: Python standard library function for synchronous subprocess execution. With `capture_output=True`, it buffers all stdout/stderr until the process exits — the root cause of the blank-screen problem.

- **subprocess.Popen()**: Lower-level Python subprocess API that supports real-time streaming of stdout/stderr via line-by-line iteration or `select`/`poll` mechanisms.

- **stdin passthrough**: Connecting the parent process's stdin to the child subprocess so that the child can read user input. Requires `stdin=None` (inherit) or explicit `stdin=sys.stdin` in subprocess calls.

- **Tee pattern**: Writing output simultaneously to the terminal (for real-time visibility) and to a log file (for persistence). Commonly implemented by reading from subprocess pipes and writing to both destinations.

- **msvcrt / termios**: Platform-specific modules used in `menu.py`'s `get_key()` for raw keyboard input. These set the terminal to raw mode, which can interfere with subprocess stdin if not properly restored.

- **run.bat / run.sh**: Shell wrappers that launch `menu.py` with the workspace path. They are the entry point for users.

- **copilot CLI**: GitHub Copilot command-line tool invoked via `copilot -p "<prompt>" --allow-all-tools`. Expected to be interactive (can produce output incrementally and may request input).

- **CMP-ART-0006**: The compute catalog entry for the AIB command menu, which documents its purpose and behavior.

## Assumptions

- Assumption A1: The `copilot` CLI writes output incrementally to stdout/stderr (not all at once on exit), so real-time streaming will produce meaningful progressive feedback.
  - Rationale: CLI tools designed for interactive use typically flush output per line or per chunk.
  - Risk if false: Streaming would produce no benefit over the current approach; output would still appear only at the end.
  - Falsification method: Run `copilot -p "..." --allow-all-tools` manually in a terminal and observe whether output appears incrementally.

- Assumption A2: The `copilot` CLI reads from stdin when it needs user input (standard Unix/Windows convention).
  - Rationale: Interactive CLI tools use stdin for prompts; the `--allow-all-tools` flag suggests interactive operation.
  - Risk if false: User input passthrough would not work; a different IPC mechanism would be needed.
  - Falsification method: Run `copilot` manually with a prompt that requires user clarification and observe stdin behavior.

- Assumption A3: A `logs/` directory at the workspace root is an acceptable location for session execution logs.
  - Rationale: The `logs/` directory already exists and is used for release version logs; adding execution logs there maintains consistency.
  - Risk if false: Log files would need a different location, requiring additional configuration.
  - Falsification method: Confirm with the user that `logs/` is the desired log location.

- Assumption A4: The terminal environment supports ANSI escape codes for status indicators (e.g., spinner, progress prefix).
  - Rationale: Modern terminals on Windows (Windows Terminal, VS Code integrated terminal) and Unix terminals support ANSI codes.
  - Risk if false: Status indicators would render as garbled text in legacy terminals.
  - Falsification method: Test with `cmd.exe` legacy console vs. Windows Terminal.

- Assumption A5: Log files should be append-only per session and not rotated automatically.
  - Rationale: Simplicity; the user is expected to manage log cleanup manually or via VCS ignore rules.
  - Risk if false: Disk usage could grow unbounded in long-lived workspaces.
  - Falsification method: Ask user about retention preferences.

## Impact Assessment

### Affected Components / Areas

- `.aib_brain/tools/menu.py` — `run_prompt_action()` and `run_action()` functions: core change targets.

- `.aib_brain/tools/menu.py` — `get_key()` function: may need adjustment to avoid raw-mode interference with subprocess stdin.

- `logs/` directory — new execution log files will be written here.

- `tests/test_menu.py` — tests must be updated for new streaming/logging behavior.

- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — must be populated with the new logging specification.

- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — component inventory description for AIB Command Menu needs update.

- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — CMP-ART-0006 entry needs update to reflect logging and streaming.

- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — runtime interaction sequences need a new scenario for prompt action execution with streaming.

### Change Type and Dependencies

- `.aib_brain/tools/menu.py` — **modify** — core application logic. No external dependencies beyond Python stdlib.

- `logs/` — **add** (new log files) — downstream of menu.py changes. The directory already exists.

- `tests/test_menu.py` — **modify** — depends on menu.py changes being finalized first.

- OBS-01, ARCH-01, CMP-01, ARCH-06 — **modify** — documentation updates depend on implementation being finalized.

### Domain Impacts

- DOMAIN (ARCH): Impact detected. The AIB Command Menu component description in ARCH-01 must be updated to reflect real-time streaming, logging, and stdin passthrough capabilities. A new runtime interaction sequence in ARCH-06 should document the prompt action execution flow.
  - Relevant: ARCH-01, ARCH-06

- DOMAIN (CMP): Impact detected. CMP-ART-0006 in CMP-01 must be updated to document the logging output and streaming behavior.
  - Relevant: CMP-01

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): No impact detected. Existing glossary terms (TERM-0013 Prompt Action) remain valid.

- DOMAIN (RQT): Impact detected. FR-008 in RQT-02 may need refinement to specify real-time feedback and logging requirements.
  - Relevant: RQT-02

- DOMAIN (OBS): Impact detected. OBS-01 must be populated with the execution logging specification.
  - Relevant: OBS-01

- DOMAIN (SEC): No impact detected. No secrets or credentials are involved; logs must not capture sensitive data.

### Constraints

- Python 3.10+ stdlib only — no third-party dependencies may be introduced for logging/streaming (per existing CMP-01 environment specification).

- Cross-platform compatibility — must work on Windows (cmd.exe, PowerShell, Windows Terminal) and Unix (bash, zsh).

- The Copilot CLI detection (`_detect_copilot_cli()`) and gating logic must not be altered.

- Log files must not contain secrets, credentials, tokens, or sensitive PII (per analysis convention and security policy).

- The menu's interactive keyboard navigation (arrow keys, digit shortcuts) must continue to function correctly when no subprocess is running.

### Required Documentation Updates

- ARCH-01 - High-level Architecture
  Required update? YES
  Reason: AIB Command Menu component description must include streaming, logging, and stdin passthrough.

- ARCH-06 - Runtime interaction sequences
  Required update? YES
  Reason: New sequence scenario for prompt action execution with real-time streaming.

- CMP-01 - Notebook/script catalog
  Required update? YES
  Reason: CMP-ART-0006 entry must reflect logging output path, streaming behavior.

- OBS-01 - Logging
  Required update? YES
  Reason: Must be populated with execution logging specification (currently a stub).

- RQT-02 - Requirements document
  Required update? YES
  Reason: FR-008 should specify real-time feedback and logging.

### Decision Points

- Decision D1: Log file location and naming scheme.
  - Option A: `logs/aib-session-<YYYYMMDD>-<HHmmss>.log` — one log file per menu session.
  - Option B: `logs/aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log` — one log file per action execution.
  - Option C: `.aib_memory/logs/<action>.log` — per-action append-only log under memory.
  - Implications: Option A is simplest but produces large files; Option B gives fine-grained traceability; Option C keeps logs with memory artifacts but adds VCS noise.
  - Recommended: **Option B** — one log file per action execution provides the best traceability and keeps files manageable. The `logs/` directory is already gitignored-friendly and used for release logs.

- Decision D2: How to handle stdin for the copilot subprocess.
  - Option A: Inherit stdin (`stdin=None` in Popen) — simplest; copilot can read directly from terminal.
  - Option B: Proxy stdin through a wrapper that logs input — provides complete session transcript but adds complexity.
  - Implications: Option A is reliable and simple; Option B risks buffering issues and platform-specific problems.
  - Recommended: **Option A** — direct stdin inheritance. Logging user input raises privacy concerns and adds complexity without proportional benefit.

- Decision D3: Real-time output mechanism.
  - Option A: `subprocess.Popen()` with line-by-line read from stdout/stderr pipes, writing to both terminal and log file (tee pattern).
  - Option B: `subprocess.Popen()` with `stdout=None, stderr=None` (inherit) for terminal display, plus a separate mechanism (e.g., `tee` command or shell redirection) for logging.
  - Implications: Option A gives full control over output formatting and logging; Option B is simpler but logging requires platform-specific shell wrappers.
  - Recommended: **Option A** — Popen with tee pattern. Provides cross-platform control and enables structured log formatting with timestamps.

## Research Plan and Findings

- Methodology: Internal docs scan of all product-doc files listed in references.md; code scan of `.aib_brain/tools/menu.py`, `.aib_brain/tools/common.py`, `run.bat`, `run.sh`; pattern scan of existing test files.

- Evidence summary:
  - `run_prompt_action()` (menu.py lines ~600-635) uses `subprocess.run(["copilot", ...], capture_output=True, text=True)` — confirms output is fully buffered.
  - `run_action()` (menu.py lines ~530-560) uses the same `subprocess.run(..., capture_output=True)` pattern — same problem for script actions.
  - `get_key()` (menu.py lines ~340-390) sets terminal to raw mode using `msvcrt` (Windows) or `termios` (Unix) — this raw mode is only active during menu navigation, not during subprocess execution, so it should not interfere with subprocess stdin.
  - `run.bat` and `run.sh` are simple wrappers; they do not set up any logging infrastructure.
  - OBS-01 is a stub — no logging specification exists.
  - CMP-ART-0006 documents the menu but does not mention logging or streaming.
  - No `.gitignore` entry was found for `logs/*.log` patterns (only `logs/version_*.md` files are committed).

- Gaps and unknowns:
  - Whether the `copilot` CLI flushes stdout incrementally or only on exit.
  - Whether the `copilot` CLI actually uses stdin for user prompts or uses a different mechanism (e.g., separate TTY).
  - User preference on log retention and `.gitignore` rules for execution logs.

- Proposed validation actions:
  - Manual test: run `copilot -p "..." --allow-all-tools` in a raw terminal to observe output and input behavior.
  - Spike: prototype `Popen`-based tee in an isolated script to validate cross-platform streaming.

- **Files Read**:
  - `.aib_brain/tools/menu.py` — confirmed `capture_output=True` in both `run_prompt_action()` and `run_action()`; identified `get_key()` raw-mode scope.
  - `.aib_brain/tools/common.py` — reviewed shared helpers; no logging infrastructure present.
  - `.aib_brain/run.bat` — simple wrapper, no logging.
  - `.aib_brain/run.sh` — simple wrapper, no logging.
  - `.aib_brain/Concepts.md` — confirmed action contract and invocation rules.
  - `.aib_brain/conventions/analysis-convention.md` — convention for this document.
  - `.aib_brain/conventions/request-convention.md` — convention for request.md rewrite.
  - `.aib_memory/references.md` — full reference listing reviewed.
  - `.aib_memory/requests/R-20260403-1651-fix-copilot-cli-user-feedback-experience/request.md` — original request reviewed.
  - `.aib_memory/requests/R-20260403-1651-fix-copilot-cli-user-feedback-experience/iterations.md` — confirmed iteration 01 is Active.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — confirmed AIB Command Menu component entry; needs update.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — ADRs reviewed; no existing ADR for logging.
  - `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — runtime sequences reviewed; needs new scenario.
  - `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — resource catalog reviewed; no new resources needed.
  - `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — CMP-ART-0006 confirmed; needs update.
  - `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — algorithms reviewed; no impact.
  - `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — data sources reviewed; no impact.
  - `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — data models reviewed; no impact.
  - `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — data consumption reviewed; no impact.
  - `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — archiving policy reviewed; execution logs should follow same retention principles.
  - `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — dashboard inventory reviewed; no impact.
  - `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — glossary reviewed; no new terms needed beyond existing TERM-0013.
  - `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — business processes reviewed; no impact.
  - `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — personas and use cases reviewed; confirms DEVELOPER pain points.
  - `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — stub; must be populated.
  - `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — stub; no impact.
  - `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-008 confirmed; needs refinement.
  - `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — stub; no impact.
  - `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — stub; no impact.

## Rewrite Proposal of the Request

See the updated `request.md` file which will be written as part of this analysis output. The rewrite provides named actors, specific acceptance criteria, explicit out-of-scope items, and traceability to affected artifacts.

## Solution Options

### Option A: Popen Tee Pattern with Inherited stdin

- **Overview**: Replace `subprocess.run(..., capture_output=True)` in both `run_prompt_action()` and `run_action()` with `subprocess.Popen()`. Read stdout/stderr via line-by-line iteration and write each line to both `sys.stdout`/`sys.stderr` (terminal) and a timestamped log file. Pass `stdin=sys.stdin` (or `stdin=None`) to allow the subprocess to read user input directly.

- **Benefits**:
  - Real-time terminal output — user sees progress, warnings, and errors as they occur.
  - Persistent log file — full session transcript available for post-mortem analysis.
  - User input works — copilot CLI can prompt for clarification.
  - Cross-platform — Python stdlib only (`subprocess`, `threading` for dual-stream reading, `pathlib`, `datetime`).
  - Minimal change footprint — only `run_prompt_action()` and `run_action()` need modification.

- **Trade-offs**:
  - Slightly more complex code than current `subprocess.run()` one-liner.
  - Dual-stream (stdout + stderr) reading requires either threading or `selectors` to avoid deadlock.
  - When stdin is inherited, `capture_output` for stdin is not possible (cannot log user input without a proxy).

- **Constraints**: Must not introduce third-party dependencies. Must handle Windows and Unix.

- **Risks**: If copilot CLI does not flush output, streaming may still appear delayed. Mitigation: test and document; this is a limitation of the external CLI, not the menu.

- **Expected effort**: Small to medium. Core change is ~50-80 lines of Python across two functions plus a logging helper. Test updates proportional.

- **High-level acceptance-test ideas**:
  - Verify that output from a slow subprocess appears incrementally in the terminal.
  - Verify that a log file is created in `logs/` with timestamped content.
  - Verify that a subprocess requesting stdin input receives the user's response.
  - Verify that on failure, full output is visible in both terminal and log file.

### Option B: Shell-Level Tee with Log Redirect

- **Overview**: Wrap the subprocess command in a shell invocation that uses OS-level `tee` (Unix) or PowerShell `Tee-Object` (Windows) to split output to terminal and a log file. Keep `stdin` inherited.

- **Benefits**:
  - Minimal Python code changes — the tee logic is delegated to the shell.
  - Proven OS-level tools for output splitting.

- **Trade-offs**:
  - Platform-specific: requires different command construction for Windows vs. Unix.
  - Less control over log formatting (no Python-level timestamps per line).
  - Harder to test in a Python test harness.
  - Error handling across the shell wrapper is less deterministic.

- **Constraints**: Requires `tee` on Unix (standard) and `Tee-Object` on Windows (PowerShell only, not available in cmd.exe).

- **Risks**: cmd.exe users would not get logging. PowerShell detection adds complexity. Shell escaping of copilot prompts could be fragile.

- **Expected effort**: Small code change but medium integration/testing effort due to platform branching.

- **High-level acceptance-test ideas**:
  - Same as Option A but with additional platform-specific test cases.

### Recommendation

**Option A (Popen Tee Pattern)** is recommended. It provides full control, cross-platform consistency, structured logging with timestamps, and keeps all logic within Python — consistent with the existing AIB tool architecture that uses Python stdlib exclusively.

## Disambiguation Questionnaire

**Question:** Q1 — What is the minimal shippable outcome for this iteration (MSI) and what is explicitly excluded?
**Chosen Answer / Value:** MSI = real-time output streaming + log file creation + stdin passthrough for both script and prompt actions. Excluded: GUI-based log viewer, remote telemetry, copilot CLI modifications.
**Rationale:** These three capabilities directly address the user's three stated pain points (no visibility, no error info, no input).
**Evidence / Reference:** request.md Goal section; ARCH-01 component inventory; CMP-01 CMP-ART-0006.
**Impact if changed:** Reducing MSI scope would leave at least one pain point unresolved; expanding it would increase risk for this iteration.

**Question:** Q2 — Which user-visible changes (if any) MUST be demonstrable at iteration end?
**Chosen Answer / Value:** (a) Running a prompt action shows incremental copilot output in the terminal. (b) A log file appears in `logs/` after action execution. (c) If copilot asks a question, the user can type a response.
**Rationale:** Directly maps to the three request goals.
**Evidence / Reference:** request.md Goal section.
**Impact if changed:** Removing any demo criterion would fail the corresponding success criterion.

**Question:** Q3 — What are the non-functional targets applicable to this iteration?
**Chosen Answer / Value:** Latency: first output line must appear within 2 seconds of subprocess start (assuming copilot CLI cooperates). Log write: synchronous, no data loss on normal exit. Platform: Windows + Unix.
**Rationale:** Users expect near-instant feedback; logs must be reliable.
**Evidence / Reference:** NFR-004 Python 3.10+ requirement; CMP-ART-0006 environment spec.
**Impact if changed:** Relaxing latency target would reduce urgency; tightening it would require buffered output pre-fetch.

- Q4, Q5, Q6: Data & Contracts questions | Chosen Answer / Value: N/A — this change does not introduce new data sources, schemas, serialization formats, or ingestion pipelines. Log files are plain text with no schema contract. | Rationale: The change is a UI/observability enhancement within an existing CLI tool. | Evidence / Reference: DATA-01, DATA-02, DATA-05. | Impact if changed: If structured log format were required, a schema definition would be needed.

**Question:** Q7 — Which algorithm/specification variant is in scope?
**Chosen Answer / Value:** Popen tee pattern (Option A from Solution Options). Line-by-line stdout/stderr reading with concurrent dual-stream output via threading.
**Rationale:** Cross-platform, stdlib-only, full control over formatting.
**Evidence / Reference:** Solution Options section; Python subprocess documentation.
**Impact if changed:** Switching to Option B (shell tee) would require platform-specific branching and reduce test coverage.

- Q8, Q9: Accuracy/hardware constraints | Chosen Answer / Value: N/A — no accuracy thresholds apply; execution is local workstation, no concurrency caps beyond OS limits. | Rationale: This is a terminal UI enhancement, not an algorithm. | Evidence / Reference: CMP-02 (no new algorithm). | Impact if changed: N/A.

- Q10, Q11: Interfaces & Integration | Chosen Answer / Value: N/A — no new API endpoints, message topics, or inter-service contracts. The only interface change is the subprocess invocation pattern within menu.py. Backward compatibility: the menu's external interface (keyboard navigation, action list) is unchanged. | Rationale: Internal refactor of subprocess handling only. | Evidence / Reference: ARCH-01 component inventory; ARCH-06 interaction sequences. | Impact if changed: If the copilot CLI's invocation interface changes, the command construction in `run_prompt_action()` would need to adapt.

- Q12, Q13, Q14: Security, Privacy, Compliance | Chosen Answer / Value: Identities: same as current (local OS user). Data classification: Internal. Log files MUST NOT contain secrets or PII. Secrets injection: N/A — no new secrets introduced. | Rationale: Logging terminal output does not change the security posture if sensitive content is not logged. | Evidence / Reference: SEC-01 through SEC-04 (stubs); DATA-08 archiving policy. | Impact if changed: If copilot output contains sensitive data, log sanitization would be required.

**Question:** Q15 — Which metrics/logs/traces prove the change is healthy?
**Chosen Answer / Value:** (a) Log file created in `logs/` with non-zero size after each action execution. (b) Log file contains timestamped entries for start, output lines, and exit code. (c) No Python exceptions or tracebacks in stderr during normal operation.
**Rationale:** These are the minimum indicators that streaming and logging are functioning.
**Evidence / Reference:** OBS-01 (to be populated).
**Impact if changed:** Additional metrics would require instrumentation beyond the current scope.

- Q16, Q17: Alerts & Runbooks | Chosen Answer / Value: N/A — no alerting infrastructure exists; this is a local CLI tool. No runbooks/SOPs exist that need updating. | Rationale: Local developer tool with no production monitoring. | Evidence / Reference: OBS-01 (stub); KNW-02 business processes. | Impact if changed: N/A.

**Question:** Q18 — Which product docs must be created or updated?
**Chosen Answer / Value:** ARCH-01 (update component description), ARCH-06 (add sequence scenario), CMP-01 (update CMP-ART-0006), OBS-01 (populate from stub), RQT-02 (refine FR-008). All have `edit_allowed=Y`.
**Rationale:** These are the docs directly affected by the code change per impact assessment.
**Evidence / Reference:** references.md; Impact Assessment section above.
**Impact if changed:** Omitting any update would leave documentation inconsistent with implementation.

**Question:** Q19 — What acceptance evidence will be recorded and where?
**Chosen Answer / Value:** Test results from `tests/test_menu.py` covering streaming, logging, stdin, and error scenarios. Implementation log entry in `implementation.md`.
**Rationale:** Aligns with existing AIB practice of recording implementation evidence.
**Evidence / Reference:** Concepts.md holistic workflow; request-convention.md Success criteria.
**Impact if changed:** Reducing test coverage would weaken confidence in cross-platform behavior.

**Question:** Q20 — What is the rollback strategy if acceptance fails?
**Chosen Answer / Value:** Revert the commit(s) modifying `menu.py` and related test files. Log files created during testing can be deleted. No database or infrastructure rollback required.
**Rationale:** All changes are file-based and version-controlled; git revert is sufficient.
**Evidence / Reference:** ARCH-01 environments; DATA-08 archiving policy.
**Impact if changed:** N/A — git revert is the standard rollback mechanism.

## Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | AIB Command Menu component description must include streaming, logging, stdin passthrough capabilities |
| REF-0005 | ARCH-06 - Runtime interaction sequences | .aib_memory/docs/04 Technology/Architecture/ARCH-06.md | New runtime sequence scenario for prompt/script action execution with real-time streaming |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | CMP-ART-0006 entry must reflect logging output and streaming behavior |
| REF-0021 | OBS-01 - Logging | .aib_memory/docs/04 Technology/Observability/OBS-01.md | Must be populated with execution logging specification (currently stub) |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | FR-008 should specify real-time feedback and logging requirements |

## Operational & Documentation Implications

- **Logging**: A new category of log files (`logs/aib-action-*.log`) will be created at runtime. These are transient operational artifacts, not release logs. They should be added to `.gitignore` to avoid VCS noise.

- **Observability**: OBS-01 must be populated to define the log format, retention expectations, and health indicators for execution logging.

- **Monitoring/alerts**: Not applicable — this is a local CLI tool with no remote monitoring infrastructure.

- **Runbooks/SOPs**: No formal runbooks exist; none need to be created for this change.

- **Data quality rules**: Not applicable — log files have no schema contract.

- **Product documentation**: Five product-doc files must be updated (see Affected Documentation table above).

## Risks

- Risk R1: Copilot CLI does not flush stdout incrementally.
  - Probability: Low
  - Impact: Medium — streaming would show output in large chunks rather than line-by-line, degrading but not eliminating the user experience improvement.
  - Mitigation: Test manually; document the limitation. Consider adding a "waiting..." indicator that updates periodically regardless of output.
  - Owner (role): DEVELOPER

- Risk R2: Threading for dual-stream reading introduces race conditions or platform-specific bugs.
  - Probability: Low
  - Impact: High — could cause output interleaving, log corruption, or deadlocks.
  - Mitigation: Use well-established patterns (daemon threads reading from pipes, main thread joining). Write focused unit tests for the tee helper.
  - Owner (role): AIB Maintainers
  - Contingency: Fall back to sequential read (stdout first, then stderr) if threading proves unreliable.

- Risk R3: Log files accumulate unbounded disk usage in long-lived workspaces.
  - Probability: Medium
  - Impact: Low — individual log files are small (KB range); accumulation is slow for typical usage.
  - Mitigation: Document retention expectations in OBS-01. Consider adding a log cleanup command in a future iteration if needed.
  - Owner (role): DEVELOPER

- Risk R4: Accidental keystroke during subprocess execution causes unintended behavior.
  - Probability: Medium
  - Impact: Low — with stdin inherited, keystrokes go to the subprocess (copilot CLI) rather than the menu. If copilot ignores unexpected input, there is no harm. If copilot interprets it as a response, the user may need to re-run.
  - Mitigation: Display a clear "Running..." banner before subprocess starts, instructing the user not to type unless prompted.
  - Owner (role): DEVELOPER

## Open Questions & Next Actions

1. Does the `copilot` CLI flush stdout incrementally or buffer until exit? (Owner: DEVELOPER, Trigger: before implementation starts, Resolution: manual test in terminal)

2. Does the `copilot` CLI read from stdin for user prompts, or does it use a different mechanism? (Owner: DEVELOPER, Trigger: before implementation starts, Resolution: manual test with a prompt that requires user input)

3. Should execution log files be added to `.gitignore`? (Owner: User, Trigger: before implementation, Resolution: confirm preference)

4. Is `logs/` the preferred directory for execution logs, or should a separate directory (e.g., `logs/sessions/` or `.aib_memory/logs/`) be used? (Owner: User, Trigger: before implementation, Resolution: confirm preference)

5. What log retention policy should apply to execution logs — unbounded, time-based cleanup, count-based rotation? (Owner: User, Trigger: before implementation, Resolution: confirm preference or accept default of unbounded)

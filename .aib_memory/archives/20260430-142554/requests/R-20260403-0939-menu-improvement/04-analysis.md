# 1. Executive Summary

- **Request ID:** R-20260403-0939

- **Request title:** Menu Improvement

- **Iteration ID:** 04

- **High-level purpose:** Stabilization and implementation-readiness confirmation. Iterations 01–03 fully resolved all scope ambiguities, open questions, and CLI binary identity. Iteration 04 validates that the analysis baseline remains accurate against the current code state (no changes made since iteration 03), normalizes the `request.md` to strict six-section request-convention format, and confirms the specification is immediately actionable for implementation.

- **Prior iterations:**
  - Iteration 01 (Completed 2026-04-03 10:57:01 +0300): First analysis + questionnaire; five open questions across scope, CLI binary, menu clutter, and test coverage.
  - Iteration 02 (Completed 2026-04-03 11:16:26 +0300): Refined analysis; four of five questions resolved by request.md Goal updates; 02-questionnaire.md produced with one remaining item: QID-BF-001 (CLI binary identity).
  - Iteration 03 (Completed 2026-04-03 11:35:01 +0300): QID-BF-001 resolved (bare `copilot` binary confirmed); full implementation-ready specification produced; no open questions.
  - Iteration 04 (Active): Implementation-readiness confirmation; validates all findings against live code; produces six-section convention-compliant `request.md` rewrite.

- **Conflicts resolved:** None since iteration 03. All iteration 02 and 03 conflicts (especially Assumption A1 — `gh copilot` vs. bare `copilot`) remain resolved as confirmed in iteration 03. No new contradictions detected.

- **Code-state confirmation:** Direct source read of `menu.py` and `close-request.py` confirms all five improvement areas are unimplemented. The specification from iteration 03 applies in its entirety without adjustment.

- **Expected outcome:** Iteration 04 analysis is the last gate before implementation. No questionnaire will be triggered. Implementation can proceed on all five areas simultaneously or sequentially per the sequencing table in §6.2.


# 2. Scope Interpretation

- **In scope — explicit (5 improvement areas; identical to iteration 03):**

  Improvement 1: Add `"reverse-engineer.py"` and `"test_common.py"` to `EXCLUDE_SCRIPTS` in `menu.py` (line 16).

  Improvement 2: Update `_detect_copilot_cli()` detection from `["gh", "copilot", "--version"]` to `["copilot", "--version"]`; move call to pre-loop in `choose_action()`; add `cli_available: bool` parameter to `render_menu()`; gate prompt section rendering on CLI presence; when absent, render static non-navigable informational block.

  Improvement 3: Replace `run_prompt_action()` body with `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` without `capture_output`; remove all copy/paste text.

  Improvement 4: Remove `if script: line += f" [{script}]"` suffix in `render_menu()` Script actions loop; remove `line += f" [{paction['prompt_file']}]"` suffix in Prompt actions loop; remove `print("\nRunning command:")` and `print(" ".join(command))` from `run_action()`.

  Improvement 5: In `close-request.py`, replace `raise ValidationError("Cannot close request while an iteration is Active")` guard with auto-close logic; add `COMPLETED`, `format_markdown_table`, `write_text` imports from `common`.

- **Out of scope — explicit (unchanged):**

  No changes to prompt `.md` files.

  No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `common.py`.

  No new Python dependencies.

  No changes to CI workflow or release bookkeeping.

  No changes to `collect_parameters()`.

- **Implicit in scope:**

  (implicit rule - AIB framework) Documentation updates required when code components change: ARCH-01, CMP-01, RQT-02, KNW-01.

  (implicit rule - AIB framework) Test coverage must be extended in `test_common.py` for the `close-request` auto-close path and for `EXCLUDE_SCRIPTS` content.


# 3. Domain Knowledge Essentials

- **AI Builder (AIB):** Model-agnostic, file-first framework for specification-driven development. The interactive menu (`menu.py`) is the primary developer access point for all AIB lifecycle tools.

- **AIB Command Menu (CMP-ART-0006):** Terminal UI launcher (`menu.py`). Surfaces two sections: Script actions (lifecycle tool scripts) and Prompt actions (AI-driven `.aib_brain/prompts/aib-*.md` triggers). Primary persona: DEVELOPER. Runs on both Windows (`msvcrt`) and POSIX (`termios`).

- **Script action:** A menu entry mapping to a `*.py` tool script discovered via `build_script_actions()` + `discover_tool_scripts()`. Only files not in `EXCLUDE_SCRIPTS` are surfaced.

- **Prompt Action (pending TERM-0013):** A menu entry mapping to a `.aib_brain/prompts/aib-*.md` file. When `copilot` binary is available, it executes the prompt interactively. When absent, displayed informatively only.

- **`copilot` CLI:** Standalone binary detected by `copilot --version` exit code 0. Confirmed as the correct binary by QID-BF-001 answer in 02-questionnaire.md. Machine-dependent availability; absence must not break the menu.

- **Iteration auto-close:** `close-request.py` currently blocks with `ValidationError` when an active iteration exists. The improvement removes this block by auto-closing the iteration(s) first, then closing the request in a single command.

- **Impacted roles/personas:** DEVELOPER (daily menu user, close-request operator). AI_AGENT reads prompts directly and is not affected by menu navigation changes.

- **Business process touched:** AIB lifecycle management — request closure and developer tool access.


# 4. Technical Knowledge & Terms

- **`menu.py`** — `.aib_brain/tools/menu.py`. Interactive terminal UI using unbuffered key input. Current `EXCLUDE_SCRIPTS` (line 16): `{"menu.py", "common.py", "initialize.py"}`.

- **`EXCLUDE_SCRIPTS`** — `set[str]` constant. Controls which `.py` files in `tools/` are hidden from the Script actions section. Must be extended to `{"menu.py", "common.py", "initialize.py", "reverse-engineer.py", "test_common.py"}`.

- **`_detect_copilot_cli()`** — Lines 57–79 of `menu.py`. Currently uses `["gh", "copilot", "--version"]`; result cached in `_COPILOT_CLI_AVAILABLE`. Must change to `["copilot", "--version"]`. Must be called eagerly before the `while True` loop in `choose_action()`, not lazily inside `run_prompt_action()`.

- **`render_menu()`** — Lines 549–590 of `menu.py`. Currently: Script loop appends `if script: line += f" [{script}]"`; Prompt loop appends `line += f" [{paction['prompt_file']}]"`. Both must be removed. Signature must gain `cli_available: bool` parameter for conditional prompt section rendering:
  - `cli_available = True` → current navigable Prompt actions section.
  - `cli_available = False` → static block headed `--- Prompt actions (Copilot CLI not detected — informational only) ---` with lines `  • <Title>  →  copilot "Execute the prompt defined in <path>"`.

- **`run_action()`** — Lines 504–543 of `menu.py`. Contains `print("\nRunning command:")` (line ~514) and `print(" ".join(command))` (line ~515). Both must be removed.

- **`run_prompt_action()`** — Lines 595–620 of `menu.py`. Currently prints copy/paste text and conditionally a `gh copilot suggest "..."` string but never calls `subprocess.run`. Must replace body with `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` (no `capture_output`). Remove all print/copy-paste text.

- **`choose_action()`** — Lines 622–661 of `menu.py`. Must call `_detect_copilot_cli()` before the `while True` loop; pass result to `render_menu()`; when CLI absent, set `total_items = len(script_actions)` so Prompt actions indices are non-navigable.

- **`close-request.py`** — Guard `if active_iterations: raise ValidationError("Cannot close request while an iteration is Active")` at lines ~55–57. `COMPLETED`, `format_markdown_table`, `write_text` are NOT yet imported. Replacement logic mirrors `close-iteration.py` write pattern: `write_text(path, "# Iterations\n\n" + format_markdown_table(header, rows))`.

- **`close-iteration.py`** — Reference implementation for the iteration write operation; confirms `COMPLETED`, `format_markdown_table`, `write_text`, `now_iso` are importable from `common`.

- **`common.py`** — Provides all required utilities; no changes needed.

- **`test_common.py`** — Comprehensive test file for `common.py` helpers. No `TestCloseRequestAutoClose` class exists yet. Must add: (a) test that `close-request` with active iteration auto-closes it and proceeds; (b) test that `EXCLUDE_SCRIPTS` contains `"reverse-engineer.py"` and `"test_common.py"`.

- **Python 3.10+ / stdlib only (NFR-004).** No new packages.

- **Cross-platform constraint:** `subprocess.run(["copilot", ...])` without `capture_output` passes stdin/stdout/stderr through on both Windows and POSIX.

- **Static informational block format (CLI absent):** `  • <Title>  →  copilot "Execute the prompt defined in <relative_path>"`.


# 5. Assumptions

- Assumption A1: The `copilot` binary resolved by the OS `PATH` when `subprocess.run(["copilot", "--version"])` is called is the intended Copilot CLI binary on all developer machines where this feature is expected to work.
  - Rationale: Confirmed by user's QID-BF-001 answer in 02-questionnaire.md (option B + Other: "If copilot is installed, the cmd command for running it is `copilot`"). Unchanged from iteration 03.
  - Risk if false: Detection returns `False` on machines where the binary name differs; prompt actions fall back to static informational mode. Correct fallback; not a defect.
  - Falsification method: Run `copilot --version` on all target developer machines; confirm exit code 0.

- Assumption A2: The `copilot` binary accepts a raw prompt string after the option "-p " as next positional argument: `copilot -p "Execute the prompt defined in <path>"`.
  - Rationale: request.md Goal item 3 and QID-BF-001 answer consistently specify this invocation form. 
  - Falsification method: Run `copilot -p "Execute the prompt defined in test.md"` manually on the target machine before implementation.

- Assumption A3: Moving `_detect_copilot_cli()` from lazy to eager (pre-loop in `choose_action()`) introduces no perceptible startup delay given the 5-second timeout and typical <200 ms response.
  - Rationale: Local binary lookup on well-configured machines is fast. `_COPILOT_CLI_AVAILABLE` cache prevents repeated lookups.
  - Risk if false: Slower startup on edge-case machine configurations (e.g., network-mounted drives with slow PATH traversal).
  - Falsification method: Measure menu startup latency with eager detection; acceptable if <1 s.

- Assumption A4: `close-request.py` can import `COMPLETED`, `format_markdown_table`, and `write_text` from `common` without changes to `common.py`.
  - Rationale: All three names are defined in `common.py` and already imported by `close-iteration.py`. Confirmed by direct code read.
  - Risk if false: Runtime `ImportError` on `close-request` execution.
  - Falsification method: Inspect `common.py` for `COMPLETED =`, `def format_markdown_table`, `def write_text`.

- Assumption A5: `collect_parameters()` verbosity is intentionally preserved; no UX smoothing applies to it.
  - Rationale: Not named in request.md Improvement 4 or Functional expectations. Confirmed by iteration 01 QID-AT-002 resolution.
  - Risk if false: User may expect smoother parameter input; missed improvement would require a new request.
  - Falsification method: Review "Functional expectations" in request.md — no mention of `collect_parameters()`.


# 6. Impact Assessment

## 6.1 Affected Components / Areas

- `.aib_brain/tools/menu.py` — 6 changes: (1) `EXCLUDE_SCRIPTS` extension (+2 entries); (2) `_detect_copilot_cli()` binary update (`gh copilot` → `copilot`); (3) `render_menu()` suffix removal + `cli_available` parameter + static block branch; (4) `run_action()` command print removal; (5) `choose_action()` pre-loop detection + gating; (6) `run_prompt_action()` real `copilot` execution.

- `.aib_brain/tools/close-request.py` — 1 change: guard replacement with auto-close iteration logic + import additions.

- `.aib_brain/tools/test_common.py` — New test class `TestCloseRequestAutoClose`: (a) test auto-close path; (b) test `EXCLUDE_SCRIPTS` membership.

- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Component Inventory row "AIB Command Menu": update Description to reflect CLI-gated prompt actions, static informational block, and `EXCLUDE_SCRIPTS` non-tool exclusions.

- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — CMP-ART-0005 `edge_cases_and_validation`; CMP-ART-0006 `edge_cases_and_validation`.

- `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-008: update to reflect CLI-gated prompt action navigation.

- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Add TERM-0013 "Prompt Action".

## 6.2 Change Type and Dependencies

| Area | Change type | Dependencies | Sequencing |
| --- | --- | --- | --- |
| `menu.py` — `EXCLUDE_SCRIPTS` | modify (1 line) | none | First (independent) |
| `menu.py` — `_detect_copilot_cli()` binary update | modify (1 line) | none | First (independent) |
| `menu.py` — `render_menu()` suffix removal + CLI gating | modify (2 lines removed + signature + branch) | updated `_detect_copilot_cli()` | After binary update |
| `menu.py` — `run_action()` command print removal | modify (2 lines removed) | none | First (independent) |
| `menu.py` — `choose_action()` pre-loop detection + gating | modify (3 lines) | `render_menu()` CLI-gating | After render_menu update |
| `menu.py` — `run_prompt_action()` real execution | modify (replace body) | `choose_action()` gating | After choose_action update |
| `close-request.py` — auto-close iteration | modify (guard replacement + imports) | `COMPLETED`, `format_markdown_table`, `write_text` | Independent |
| `test_common.py` — new test class | add (~30 lines) | all code changes above | Last |
| Documentation updates | modify | code changes completed | Final |

## 6.3 Domain Impacts

- DOMAIN (ARCH): Minor. ARCH-01 Component Inventory — AIB Command Menu description must reference `copilot` detection, static informational block, and `EXCLUDE_SCRIPTS` mechanism.
  - Relevant: ARCH-01 Component Inventory row "AIB Command Menu".

- DOMAIN (CMP): Moderate. CMP-ART-0005 `edge_cases_and_validation`: add auto-close-iteration side effect. CMP-ART-0006 `edge_cases_and_validation`: add CLI-gating and `EXCLUDE_SCRIPTS` notes.
  - Relevant: CMP-01 rows CMP-ART-0005 and CMP-ART-0006.

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): Low. Glossary requires TERM-0013 "Prompt Action" (currently missing; TERM-0012 is the last entry).
  - Relevant: KNW-01.

- DOMAIN (RQT): Low. FR-008 must be updated to specify CLI-gated prompt action navigation.
  - Relevant: RQT-02 FR-008.

- DOMAIN (DEV/DSR/FNL/OBS/OPR/SEC): No impact detected.

## 6.4 Constraints

- Python 3.10+ / stdlib only (NFR-004). No new packages.
- Cross-platform: Windows and POSIX. `subprocess.run(["copilot", ...])` without `capture_output` passes through stdin/stdout/stderr on both platforms.
- `_detect_copilot_cli()` must remain cached (`_COPILOT_CLI_AVAILABLE` global) to avoid repeated subprocess calls on every menu render cycle.
- `close-request.py` auto-close must guard on non-empty `active_iterations`; empty list → skip auto-close silently.
- No new top-level functions or new modules; all changes are inline edits within existing functions plus import additions.

## 6.5 Required Documentation Updates

- ARCH-01 — AIB Command Menu component description
  Required update? YES
  Reason: CLI-gated prompt actions (detection via `copilot --version`), static informational block when CLI absent, `EXCLUDE_SCRIPTS` mechanism for non-tool scripts.

- CMP-01 — CMP-ART-0005 and CMP-ART-0006
  Required update? YES
  Reason: CMP-ART-0005 `edge_cases_and_validation`: add auto-close-iteration side effect. CMP-ART-0006 `edge_cases_and_validation`: add CLI-gating and `EXCLUDE_SCRIPTS` exclusion notes.

- RQT-02 — FR-008
  Required update? YES
  Reason: Specify that prompt actions require `copilot` CLI detection; when absent, informational display only.

- KNW-01 — Glossary
  Required update? YES
  Reason: Add TERM-0013 "Prompt Action".

## 6.6 Decision Points

**Decision 1 — CLI binary confirmed as `copilot` (no subcommand).**
- DECISION: `["copilot", "--version"]` for detection; `["copilot", f"Execute the prompt defined in {path}"]` for execution. Confirmed by QID-BF-001 in iteration 03. No open alternatives.

**Decision 2 — Static block header text when CLI absent.**
- DECISION: Replace `--- Prompt actions (AI-driven) ---` header with `--- Prompt actions (Copilot CLI not detected — informational only) ---`. Each prompt renders as `  • <Title>  →  copilot "Execute the prompt defined in <relative_path>"`.

**Decision 3 — Eager vs lazy CLI detection.**
- DECISION: Eager (pre-loop in `choose_action()`). Required so `render_menu()` can gate the Prompt section on first render without selecting an action. The cached result prevents repeated overhead.


# 7. Research Plan and Findings

**Methodology:** Internal docs review — full read of iteration 01–03 artifacts, source code re-read of `menu.py` and `close-request.py`, and product-doc scoped reads for impacted domains.

**Evidence summary:**

- `menu.py` `EXCLUDE_SCRIPTS` (line 16): `{"menu.py", "common.py", "initialize.py"}` — neither `"reverse-engineer.py"` nor `"test_common.py"` present. Direct evidence: Improvement 1 unimplemented.

- `menu.py` `_detect_copilot_cli()` (lines 57–79): `["gh", "copilot", "--version"]` still present. Direct evidence: Improvement 2 (binary update) unimplemented.

- `menu.py` `render_menu()` (lines 549–590): `if script: line += f" [{script}]"` and `line += f" [{paction['prompt_file']}]"` still present; `cli_available` parameter absent. Direct evidence: Improvements 2 (CLI gating) and 4 (suffix removal) unimplemented.

- `menu.py` `run_action()` (lines 504–543): `print("\nRunning command:")` and `print(" ".join(command))` still present. Direct evidence: Improvement 4 (command print removal) unimplemented.

- `menu.py` `run_prompt_action()` (lines 595–620): still prints copy/paste text; `_detect_copilot_cli()` call still inside this function (lazy); `subprocess.run(["copilot", ...])` absent. Direct evidence: Improvements 2 (eager detection) and 3 (real execution) unimplemented.

- `menu.py` `choose_action()` (lines 622–661): `_detect_copilot_cli()` not called before `while True` loop; `total_items` not conditioned on CLI presence. Direct evidence: Improvement 2 (navigation gating) unimplemented.

- `close-request.py` (lines ~55–57): `raise ValidationError("Cannot close request while an iteration is Active")` still present; `COMPLETED`, `format_markdown_table`, `write_text` not in imports. Direct evidence: Improvement 5 unimplemented.

- `implementation.md`: Empty — no implementation log entries. Confirms no partial work exists.

- `03-analysis.md` section 13: No open questions. QID-BF-001 resolved. Confirmed still accurate.

- `ARCH-01.md`: AIB Command Menu description does not mention CLI-gated prompt actions or `EXCLUDE_SCRIPTS`. Update still required.

- `CMP-01.md`: CMP-ART-0005 `edge_cases_and_validation` = `"Fail if invalid lifecycle state"` (no auto-close mention). CMP-ART-0006 `edge_cases_and_validation` = `"Must surface failures clearly"` (no CLI-gating mention). Updates still required.

- `RQT-02.md`: FR-008 = `"The system supports launching tool scripts via an interactive menu."` — no CLI-gating language. Update still required.

- `KNW-01.md`: TERM-0012 is last entry; TERM-0013 absent. Update still required.

**Gaps and unknowns:** None. All prior open items from iterations 01–03 are resolved. Assumption A2 (copilot invocation format) is the only remaining pre-implementation validation recommended; it does not block analysis.

**Proposed validation (pre-implementation):** Run `copilot "Execute the prompt defined in .aib_brain/prompts/aib-create-analysis.md"` on the target developer machine manually and observe behavior. Non-blocking.

**Files Read:**

- `.aib_memory/requests/R-20260403-0939-menu-improvement/request.md` — Active request; complete 5-area specification confirmed present.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/iterations.md` — Iterations 01–03 Completed; Iteration 04 Active.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/03-analysis.md` — Full read; all 13 sections reviewed; complete specification confirmed; no open questions in section 13.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/implementation.md` — Empty; no implementation started; all 5 areas remain pending.
- `.aib_memory/references.md` — Full required-read product-doc set identified.
- `.aib_brain/prompts/aib-create-analysis.md` — Prompt being executed; preflight and output rules confirmed.
- `.aib_brain/conventions/analysis-convention.md` — Full read; all section requirements and quality rubric confirmed.
- `.aib_brain/conventions/request-convention.md` — Six required sections confirmed; formatting rules confirmed.
- `.aib_brain/tools/menu.py` — Full code read (lines 1–700); all 6 improvement touchpoints confirmed unimplemented.
- `.aib_brain/tools/close-request.py` — Full code read; guard at lines ~55–57 confirmed; missing imports confirmed.
- `.aib_brain/tools/test_common.py` — Partial read; no `TestCloseRequestAutoClose` class; no `EXCLUDE_SCRIPTS` test confirmed.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — POPULATED; AIB Command Menu row confirmed; update still required.
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — POPULATED; CMP-ART-0005 and CMP-ART-0006 confirmed; updates still required.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — POPULATED; FR-008 confirmed; update still required.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — POPULATED; TERM-0012 is last entry; TERM-0013 absent; update still required.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — `[SKIPPED — domain out of scope]`


# 8. Rewrite Proposal of the Request

## Goal

Update `menu.py` and `close-request.py` to address five independent improvement areas:

1. Add `"reverse-engineer.py"` and `"test_common.py"` to `EXCLUDE_SCRIPTS` in `menu.py` so they no longer appear as Script actions.
2. Gate prompt-action rendering on `copilot` CLI availability: when `copilot --version` returns exit code 0, render prompt actions as navigable entries; when absent, render a static non-navigable informational block. Update `_detect_copilot_cli()` to use `["copilot", "--version"]` instead of `["gh", "copilot", "--version"]`.
3. When the user selects a prompt action and CLI is available, execute `subprocess.run(["copilot", f"Execute the prompt defined in {path}"])` without `capture_output`. Remove all copy/paste text from `run_prompt_action()`.
4. Remove the `[script]` suffix from Script action lines and the `[prompt_file]` suffix from Prompt action lines in `render_menu()`. Remove `print("\nRunning command:")` and `print(" ".join(command))` from `run_action()`.
5. In `close-request.py`, replace the guard that raises `ValidationError` when an active iteration exists with logic that auto-closes the active iteration(s), prints a notice per closed iteration, and then proceeds to close the request.

## Background

The AIB interactive menu is the primary developer access point for AIB lifecycle tools. Unnecessary entries (`reverse-engineer.py`, `test_common.py`), verbose output (raw command lines, bracketed filenames), and a blocked close-request workflow (fails when an active iteration exists) degrade developer experience and introduce friction in the daily AIB workflow.

## Scope

- `menu.py`: `EXCLUDE_SCRIPTS` constant; `_detect_copilot_cli()` binary string; `render_menu()` suffix removal and `cli_available` parameter; `run_action()` command print removal; `choose_action()` pre-loop detection and navigation gating; `run_prompt_action()` body replacement.
- `close-request.py`: Import block additions (`COMPLETED`, `format_markdown_table`, `write_text`); guard replacement with auto-close logic.
- `test_common.py`: New `TestCloseRequestAutoClose` test class; new test for `EXCLUDE_SCRIPTS` membership.
- Documentation: ARCH-01 (AIB Command Menu component description), CMP-01 (CMP-ART-0005 and CMP-ART-0006 `edge_cases_and_validation`), RQT-02 (FR-008), KNW-01 (add TERM-0013).

## Out of scope

- No changes to any `.aib_brain/prompts/*.md` files.
- No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, or `common.py`.
- No new Python package dependencies.
- No changes to CI workflow or release bookkeeping.
- No changes to `collect_parameters()`.

## Constraints

- Python 3.10+ with stdlib only; no third-party packages (NFR-004).
- Cross-platform: Windows (`msvcrt`) and POSIX (`termios`) compatibility must be maintained.
- `copilot` CLI detection must be session-cached (`_COPILOT_CLI_AVAILABLE` global) to avoid repeated subprocess calls on every render cycle.
- The auto-close logic in `close-request.py` must only execute when `active_iterations` is non-empty; an empty list must silently skip and proceed as before.
- `close-request` on an already-closed request must continue to raise `ValidationError("Request already closed")`; idempotency is not extended to re-closing.
- `subprocess.run(["copilot", ...])` must not use `capture_output` so that the interactive CLI session renders directly in the developer's terminal.

## Success criteria

1. Launching the menu: neither "Reverse Engineer" nor "Test Common" appears in any rendered section.
2. On a machine where `copilot --version` returns non-zero or binary is not found: no Prompt action rows have navigable indices; a static informational block is shown with each prompt's title and invocation string.
3. On a machine where `copilot --version` returns exit code 0: selecting a prompt action launches `copilot "Execute the prompt defined in <path>"` as an interactive terminal session; no copy/paste text is shown; the menu re-renders after `copilot` exits.
4. Running any script action: the terminal no longer displays `Running command:` or the raw Python command string; no `[script]` or `[prompt_file]` suffixes appear on menu lines.
5. `python close-request.py --workspace .` while an iteration is Active: exits code 0, prints `"Auto-closed iteration <id> before closing request."` for each auto-closed iteration, then `"Closed request: R-..."`.
6. `pytest .aib_brain/tools/test_common.py` passes at 100% after new test cases are added.


# 9. Solution Options

## Option A — Targeted direct code changes (recommended)

**Overview:** Smallest set of inline edits to `menu.py` and `close-request.py` satisfying all five improvement areas. No new modules, configuration files, or abstractions.

**Benefits:** Minimal diff (~60–80 changed/added lines in two source files, ~30 lines for new test class, ~5 documentation field updates); easy to review; fully consistent with existing code patterns; no structural changes beyond the `cli_available` parameter addition.

**Trade-offs:** `EXCLUDE_SCRIPTS` requires manual maintenance when new non-tool `.py` files are added to `tools/`; no automatic enforcement.

**Constraints:** Python 3.10+ / stdlib only; cross-platform requirements met by existing architecture.

**Risks:** If `copilot` binary invocation format changes in future CLI versions, `run_prompt_action()` requires updating (low risk, low impact).

**Expected effort:** Low — all changes are small, isolated, and well-specified with exact line references.

**Acceptance test ideas:** Visual menu inspection; pytest at 100%; manual `copilot` invocation test on target machine.

DECISION: Option A accepted. Targeted and isolated; no architectural deviation; direct path to all five acceptance criteria.

## Option B — Allowlist-based script discovery

**Overview:** Replace `EXCLUDE_SCRIPTS` blocklist with an explicit allowlist of known tool scripts in `discover_tool_scripts()`.

**Benefits:** Future-proof against accidental re-appearance of new non-tool `.py` files in the menu.

**Trade-offs:** More invasive refactor of `discover_tool_scripts()` and `build_script_actions()`; maintenance burden shifts from blocklist to allowlist; outside request scope.

**Constraints:** Out of scope per request.md "Out of scope" section.

**Expected effort:** Medium.

Not recommended for this iteration. Consider as a separate future request.


# 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | AIB Command Menu component description: add CLI-gated prompt actions (`copilot --version` detection), static informational block, `EXCLUDE_SCRIPTS` non-tool exclusions |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | CMP-ART-0005 `edge_cases_and_validation`: add auto-close-iteration side effect; CMP-ART-0006 `edge_cases_and_validation`: add CLI-gating and EXCLUDE_SCRIPTS notes |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | FR-008: update to specify CLI-gated prompt action navigation and `copilot` execution |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Add TERM-0013 "Prompt Action" |


# 11. Operational & Documentation Implications

- **Runbooks:** No runbook changes required. `menu.py` and `close-request.py` are interactive developer tools operating locally.

- **SLAs/SLOs:** Not applicable.

- **Monitoring/observability:** No structured log changes. `close-request.py` auto-close prints a human-readable notice to stdout per auto-closed iteration (`"Auto-closed iteration <id> before closing request."`). No structured event or OBS-01 change required.

- **Data quality rules:** Not applicable.

- **Product documentation artifact updates:**
  - `ARCH-01` Component Inventory — AIB Command Menu row Description: update to reference `copilot` CLI-gating (detection via `copilot --version` exit code 0), static informational block when CLI absent, and the `EXCLUDE_SCRIPTS` mechanism for non-tool scripts.
  - `CMP-01` CMP-ART-0005 `edge_cases_and_validation`: change from `"Fail if invalid lifecycle state"` to `"Fail if invalid lifecycle state; auto-closes active iteration(s) before closing request and prints notice per closed iteration."`.
  - `CMP-01` CMP-ART-0006 `edge_cases_and_validation`: change from `"Must surface failures clearly"` to `"Must surface failures clearly; prompt actions require copilot CLI (non-navigable static info block when absent); non-tool scripts (reverse-engineer.py, test_common.py) excluded from discovery via EXCLUDE_SCRIPTS."`.
  - `RQT-02` FR-008: change from `"The system supports launching tool scripts via an interactive menu."` to `"The system supports launching tool scripts via an interactive menu; prompt actions are only navigable when the copilot CLI binary is detected (copilot --version exit code 0); when absent, prompt actions are displayed as a static informational list."`.
  - `KNW-01`: Add row `TERM-0013 | Prompt Action | A menu entry in the AIB Command Menu mapping to an .aib_brain/prompts/aib-*.md file; executable via the copilot binary when available on PATH; displayed as a static informational entry otherwise. | Create Analysis menu entry | AIB Maintainers | — | menu, workflow | Proposed | 1`.


# 12. Risks

- Risk R1: `copilot` interactive pass-through behaves unexpectedly on some terminal or OS configurations.
  - Probability: Low
  - Impact: Medium — prompt actions would hang or produce garbled output on affected machines.
  - Mitigation: Test `subprocess.run(["copilot", "Execute the prompt defined in ..."])` without `capture_output` on both Windows and POSIX target machines before merging; document required OS/terminal preconditions if issues arise.
  - Owner (role): DEVELOPER

- Risk R2: Auto-closing an active iteration in `close-request.py` fails midway (e.g., disk error), leaving `iterations.md` in a partially written state.
  - Probability: Low
  - Impact: High — iteration state becomes inconsistent; subsequent tool runs may fail or produce duplicate active entries.
  - Mitigation: Use the same `write_text` atomic replacement pattern from `close-iteration.py`. Validate `format_markdown_table` output before write. No additional guard needed beyond existing file-write semantics.
  - Owner (role): AIB Maintainers

- Risk R3: `EXCLUDE_SCRIPTS` does not auto-grow; future non-tool `.py` files added to `tools/` will silently reappear in the menu.
  - Probability: Medium (as codebase grows)
  - Impact: Low — cosmetic defect (unwanted extra menu entries).
  - Mitigation: Document in ARCH-01 and CMP-01 that all non-tool `.py` files in `tools/` must be listed in `EXCLUDE_SCRIPTS`. Allowlist approach deferred to a future request.
  - Owner (role): AIB Maintainers

- Risk R4: `copilot` binary accepts the prompt string in a different invocation format than specified (Assumption A2 false).
  - Probability: Low — user confirmed this invocation form in QID-BF-001.
  - Impact: Medium — `copilot` exits with an error or displays help text instead of executing the prompt.
  - Mitigation: Pre-implementation manual validation: run `copilot "Execute the prompt defined in .aib_brain/prompts/aib-create-analysis.md"` on the target machine. Non-blocking for analysis; blocks `run_prompt_action()` implementation if found incorrect.
  - Owner (role): DEVELOPER

- Risk R5: Moving CLI detection from lazy to eager introduces perceptible startup delay on edge-case machines.
  - Probability: Low — 5-second timeout is the upper bound; typical response <200 ms.
  - Impact: Low — slight UX degradation on first menu load; cached after first call.
  - Mitigation: `_COPILOT_CLI_AVAILABLE` cache prevents repeated delays. Acceptable as-is.
  - Owner (role): DEVELOPER


# 13. Open Questions & Next Actions

No open questions remain. All user-owned items from all prior iterations are fully resolved:

- QID-BF-001 (CLI binary identity): Resolved in iteration 03 — use bare `copilot` binary.
- QID-BF-002, QID-BF-003, QID-AT-001, QID-AT-002 (from iteration 01): Resolved by request.md Goal section updates confirmed in iteration 02.

**Next action:** Proceed to implementation of all five improvement areas. Pre-implementation validation recommended (non-blocking): run `copilot "Execute the prompt defined in .aib_brain/prompts/aib-create-analysis.md"` on the target developer machine to confirm Assumption A2 before implementing `run_prompt_action()`.

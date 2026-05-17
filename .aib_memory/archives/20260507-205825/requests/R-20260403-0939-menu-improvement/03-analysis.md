# 1. Executive Summary

- **Request ID:** R-20260403-0939

- **Request title:** Menu Improvement

- **Iteration ID:** 03

- **High-level purpose:** Follow-up analysis after iteration 02 (completed 2026-04-03 11:16:26 +0300). Iteration 02 produced a complete, implementation-ready analysis and questionnaire (02-questionnaire.md) containing one open question (QID-BF-001: CLI binary identity). The user has now answered QID-BF-001 in 02-questionnaire.md, confirming that option B and "Other" are both marked: the intended Copilot CLI binary is the standalone `copilot` command, not the `gh copilot` GitHub CLI extension. This iteration incorporates that answer, invalidates Assumption A1 from iteration 02, and produces a fully resolved implementation-ready specification.

- **Prior iterations:**
  - Iteration 01 (Completed 2026-04-03 10:57:01 +0300): First analysis + questionnaire; 5 questions (QID-BF-001 through QID-AT-002). All implicitly answered by the updated request.md Goal section.
  - Iteration 02 (Completed 2026-04-03 11:16:26 +0300): Refined analysis; resolved 4 of 5 questionnaire items from iteration 01; produced 02-questionnaire.md with one remaining open item (QID-BF-001 — CLI binary). No implementation entries yet.
  - Iteration 03 (Active): Incorporates QID-BF-001 answer. Expected to be the last analysis iteration before implementation.

- **Conflicts resolved:** Iteration 02 Assumption A1 is now confirmed FALSE. The correct CLI binary is bare `copilot`, not `gh copilot`. All detection and invocation references in the iteration 02 rewrite proposal that used `["gh", "copilot", ...]` must be updated to `["copilot", ...]`. The existing `_detect_copilot_cli()` function in `menu.py` currently uses `["gh", "copilot", "--version"]`; it must be changed to `["copilot", "--version"]`.

- **Key changes scoped:** `menu.py` (5 targeted edits with updated CLI binary references), `close-request.py` (1 targeted edit), `test_common.py` (new test cases), documentation updates (`ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`). Scope is identical to iteration 02 except CLI invocation strings use `copilot` instead of `gh copilot`.

- **Expected outcome if accepted:** All open questions resolved; implementation can proceed without further clarification.


# 2. Scope Interpretation

- **In scope — explicit (5 improvement areas; unchanged from iteration 02 except CLI binary):**

  Improvement 1: Add `"reverse-engineer.py"` and `"test_common.py"` to `EXCLUDE_SCRIPTS` in `menu.py`.

  Improvement 2: Gate prompt actions on `copilot` CLI availability; when absent, render a static non-navigable informational block. Detection: `["copilot", "--version"]` (updated from iteration 02's `["gh", "copilot", "--version"]`). The existing `_detect_copilot_cli()` function must be updated accordingly.

  Improvement 3: When CLI present and user selects a prompt action, call `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` without `capture_output`. Remove copy/paste text from `run_prompt_action()`.

  Improvement 4: Remove `[script]` suffix from Script action lines and `[prompt_file]` suffix from Prompt action lines in `render_menu()`. Remove `print("\nRunning command:")` and `print(" ".join(command))` from `run_action()`.

  Improvement 5: In `close-request.py`, replace the `ValidationError("Cannot close request while an iteration is Active")` guard with auto-close logic (unchanged from iteration 02).

- **Out of scope — explicit (unchanged from iteration 02):**

  No changes to prompt `.md` files.

  No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `common.py`.

  No new Python dependencies.

  No changes to CI workflow or release bookkeeping.

  No changes to `collect_parameters()`.

- **Implicit in scope:**

  (implicit rule - AIB framework) Documentation updates required when code components are changed: `ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`.

  (implicit rule - AIB framework) Test coverage must be extended in `test_common.py` for the `close-request` auto-close path.


# 3. Domain Knowledge Essentials

- **AI Builder (AIB):** Model-agnostic framework for specification-driven development. The interactive menu (`menu.py`) is the primary developer access point.

- **AIB Command Menu (CMP-ART-0006):** Terminal UI launcher; surfaces Script actions (lifecycle tool scripts) and Prompt actions (AI-driven `.aib_brain/prompts/aib-*.md` triggers). Primary persona: DEVELOPER.

- **Prompt Action:** A menu entry mapping to a `.aib_brain/prompts/aib-*.md` file. When the `copilot` binary is available, it executes the prompt via `copilot "Execute the prompt defined in <path>"`. When absent, it is displayed informatively only.

- **`copilot` CLI:** A standalone CLI binary (the exact CLI at `.aib_brain/run.bat` invocation level). Detected by running `copilot --version` and checking for exit code 0. Availability is machine-dependent; absence must not break the menu.

- **Iteration lifecycle:** `close-request.py` previously blocked if an active iteration existed; the improvement removes this block by auto-closing the iteration first (unchanged from iteration 02).

- **Impacted roles/personas:** DEVELOPER (daily menu user). AI_AGENT reads prompts directly via prompt files and is not affected by menu navigation changes.

- **Business process touched:** AIB lifecycle management — request closure (close-request flow) and developer tool usage.


# 4. Technical Knowledge & Terms

- **`menu.py`** — `.aib_brain/tools/menu.py`. Interactive terminal UI. Uses `msvcrt` (Windows) / `termios` (POSIX) for unbuffered key input.

- **`EXCLUDE_SCRIPTS`** — `set[str]` constant at line 16: `{"menu.py", "common.py", "initialize.py"}`. Must be extended to include `"reverse-engineer.py"` and `"test_common.py"`.

- **`_detect_copilot_cli()`** — Lines 57–79. Currently uses `["gh", "copilot", "--version"]`. **Must change to `["copilot", "--version"]`.** Result is session-cached in `_COPILOT_CLI_AVAILABLE`. Must be called eagerly before the render loop in `choose_action()` — not only inside `run_prompt_action()` — so `render_menu()` can gate prompt sections.

- **`render_menu()`** — Lines 549–590. Script action loop appends `if script: line += f" [{script}]"` (must remove). Prompt action loop appends `line += f" [{paction['prompt_file']}]"` (must remove). Signature must gain `cli_available: bool` parameter to conditionally render prompt actions as navigable entries or as a static informational block.

- **`run_action()`** — Lines 504–543. Contains `print("\nRunning command:")` (line ~514) and `print(" ".join(command))` (line ~515). Both must be removed.

- **`run_prompt_action()`** — Lines 595–620. Currently prints copy/paste text and conditionally the `gh copilot suggest` command string, but never calls `subprocess.run`. Must be replaced with: `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` without `capture_output`. All print/copy-paste text removed.

- **`choose_action()`** — Lines 622–661. Must call `_detect_copilot_cli()` once before the `while True` loop; pass the result as `cli_available` to `render_menu()`; when CLI absent, set `total_items = len(script_actions)` only so prompt indices are non-navigable.

- **`close-request.py`** — Guard at lines ~55–57: `if active_iterations: raise ValidationError("Cannot close request while an iteration is Active")`. Replace with auto-close logic using `COMPLETED`, `format_markdown_table`, `write_text` from `common`. Pattern mirrors `close-iteration.py`.

- **`close-iteration.py`** — Reference implementation for iteration-close write: `format_markdown_table(header, rows)` + `write_text(iterations_path, "# Iterations\n\n" + content)`.

- **`common.py`** — Provides `COMPLETED`, `format_markdown_table`, `write_text`, `now_iso` — all exportable; `close-iteration.py` already imports them, confirming availability.

- **Python 3.10+ / stdlib only** — NFR-004. No new packages.

- **`copilot` binary invocation (confirmed):** Detection: `["copilot", "--version"]`. Execution: `["copilot", f"Execute the prompt defined in {paction['prompt_file']}"]`. Without `capture_output` for interactive pass-through.

- **Static informational block format (CLI absent):** Each prompt renders as `  • <Title>  →  copilot "Execute the prompt defined in <relative_path>"`.


# 5. Assumptions

- Assumption A1: The `copilot` binary resolved by the OS `PATH` when `subprocess.run(["copilot", "--version"])` is called is the intended Copilot CLI binary on all developer machines where this feature is expected to work.
  - Rationale: The user explicitly answered QID-BF-001 (02-questionnaire.md) selecting option B ("Use `["copilot", "--version"]` for detection") and supplementing with "If copilot is installed, the cmd command for running it is `copilot`". This confirms the standalone `copilot` binary is the target.
  - Risk if false: If `copilot` is not on PATH on some developer machines, detection returns False and prompt actions silently fall back to static informational mode. This is the correct fallback behavior and does not constitute a defect.
  - Falsification method: Run `copilot --version` on the developer machine; confirm exit code 0.

- Assumption A2: The `copilot` binary accepts a raw prompt string as its first positional argument (no subcommand like `suggest` needed): `copilot "Execute the prompt defined in <path>"`.
  - Rationale: The user's QID-BF-001 answer (option B) and Other text do not mention a subcommand. The original request.md Goal item 3 specifies `subprocess.run(["copilot", "Execute the prompt defined in <path>"])` without any subcommand.
  - Risk if false: If the binary requires a subcommand (e.g., `copilot run "..."` or `copilot suggest "..."`), the invocation will either error or display help text instead of executing the prompt.
  - Falsification method: Run `copilot "Execute the prompt defined in test.md"` manually on the target machine and observe behavior.

- Assumption A3: Moving `_detect_copilot_cli()` call from lazy (inside `run_prompt_action()`) to eager (before the `while True` loop in `choose_action()`) introduces no perceptible startup delay due to the existing 5-second timeout and typical `copilot --version` response being <200 ms.
  - Rationale: The detection subprocess calls a local binary that responds quickly. The 5-second timeout in `_detect_copilot_cli()` is the upper bound; in practice the call completes in milliseconds.
  - Risk if false: If the `copilot` lookup takes multiple seconds on some machines (e.g., network-mounted drives), menu startup may feel slow.
  - Falsification method: Measure menu startup latency with pre-loop detection on the developer machine; acceptable if <1 s.

- Assumption A4: `close-request.py` can import `COMPLETED`, `format_markdown_table`, and `write_text` from `common` without any changes to `common.py`.
  - Rationale: All three names are already defined in `common.py` and imported by `close-iteration.py`. Confirmed by code read.
  - Risk if false: Runtime ImportError on `close-request` execution.
  - Falsification method: Grep `common.py` for `COMPLETED =`, `def format_markdown_table`, `def write_text`.

- Assumption A5: The `collect_parameters()` function verbosity (banner + per-field hint lines) is intentionally preserved; no UX smoothing applies to it.
  - Rationale: Not named in request.md Goal item 4 nor in Functional expectations. Consistent with iteration 01 QID-AT-002 resolution.
  - Risk if false: User may expect smoother parameter input; leaving it unchanged is a missed improvement.
  - Falsification method: Review request.md "Functional expectations" — none mention `collect_parameters()`.


# 6. Impact Assessment

## 6.1 Affected Components / Areas

- `.aib_brain/tools/menu.py` — 6 changes: (1) `EXCLUDE_SCRIPTS` extension; (2) `_detect_copilot_cli()` binary update (`gh copilot` → `copilot`); (3) `render_menu()` suffix removal + CLI-gating parameter; (4) `run_action()` command print removal; (5) `choose_action()` pre-loop detection and navigation gating; (6) `run_prompt_action()` real `copilot` execution.

- `.aib_brain/tools/close-request.py` — 1 change: guard replacement with auto-close iteration logic.

- `.aib_brain/tools/test_common.py` — New test cases: (a) close-request auto-close path; (b) `EXCLUDE_SCRIPTS` containing the two non-tool scripts.

- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — AIB Command Menu row: update description to reflect CLI-gated prompt actions and `EXCLUDE_SCRIPTS` exclusions.

- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — CMP-ART-0005 and CMP-ART-0006 `edge_cases_and_validation` fields.

- `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-008: specify CLI-gated prompt action navigation and execution.

- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Add TERM-0013 "Prompt Action".

## 6.2 Change Type and Dependencies

| Area | Change type | Dependencies | Sequencing |
| --- | --- | --- | --- |
| `menu.py` — EXCLUDE_SCRIPTS | modify (1 line) | none | First |
| `menu.py` — `_detect_copilot_cli()` binary update | modify (1 line: `gh copilot` → `copilot`) | none | First (independent) |
| `menu.py` — `render_menu()` suffix removal + CLI gating | modify (2 lines removed + signature + branch) | updated `_detect_copilot_cli()` | After binary update |
| `menu.py` — `run_action()` command print removal | modify (2 lines removed) | none | Independent |
| `menu.py` — `choose_action()` pre-loop detection + gating | modify (pre-loop call + `total_items` branch) | `render_menu()` CLI-gating | After render_menu update |
| `menu.py` — `run_prompt_action()` real execution | modify (replace body) | `choose_action()` gating | After choose_action update |
| `close-request.py` — auto-close iteration | modify (guard replacement) | `COMPLETED`, `format_markdown_table`, `write_text` | Independent |
| `test_common.py` — new test class | add (~30 lines) | all code changes above | Last |
| Documentation updates | modify | code changes completed | Final |

## 6.3 Domain Impacts

- DOMAIN (ARCH): Minor. AIB Command Menu description in ARCH-01 must reflect prompt-action CLI gating (`copilot` binary), the static informational block, and the non-tool script exclusion.
  - Relevant: ARCH-01 Component Inventory row "AIB Command Menu".

- DOMAIN (CMP): Moderate. CMP-ART-0005 `edge_cases_and_validation` must note the auto-close-iteration side effect. CMP-ART-0006 `edge_cases_and_validation` must note prompt-action CLI gating and `EXCLUDE_SCRIPTS` exclusions.
  - Relevant: CMP-01 rows CMP-ART-0005 and CMP-ART-0006.

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): Low. Glossary requires TERM-0013 "Prompt Action".
  - Relevant: KNW-01.

- DOMAIN (RQT): Low. FR-008 must be updated to specify that prompt actions gate on `copilot` CLI availability.
  - Relevant: RQT-02 FR-008.

- DOMAIN (DEV/DSR/FNL/OBS/OPR/SEC): No impact detected.

## 6.4 Constraints

- Python 3.10+ / stdlib only (NFR-004). No new packages.
- Cross-platform: Windows and POSIX. `subprocess.run(["copilot", ...])` without `capture_output` passes through stdin/stdout/stderr on both platforms, provided `copilot` is on PATH.
- `_detect_copilot_cli()` must remain cached (`_COPILOT_CLI_AVAILABLE` global) to avoid repeated subprocess calls on every menu render cycle.
- `close-request.py` auto-close must only run when `active_iterations` is non-empty; if empty, skip auto-close path (no crash).

## 6.5 Required Documentation Updates

- ARCH-01 — AIB Command Menu component description
  Required update? YES
  Reason: CLI-gated prompt actions (using `copilot` binary), static informational block, EXCLUDE_SCRIPTS exclusions.

- CMP-01 — CMP-ART-0005 and CMP-ART-0006
  Required update? YES
  Reason: CMP-ART-0005 edge_cases: add auto-close-iteration side effect. CMP-ART-0006 edge_cases: add CLI-gating (`copilot` binary) and EXCLUDE_SCRIPTS notes.

- RQT-02 — FR-008
  Required update? YES
  Reason: Specify CLI-gated prompt action navigation and `copilot` binary execution.

- KNW-01 — Glossary
  Required update? YES
  Reason: Add TERM-0013 "Prompt Action".

## 6.6 Decision Points

**Decision 1 — CLI invocation form: confirmed `copilot` (bare binary, no subcommand)**

- DECISION: Use `["copilot", "--version"]` for detection and `["copilot", f"Execute the prompt defined in {paction['prompt_file']}"]` for execution. This resolves the Assumption A1 ambiguity from iteration 02. No further options to evaluate; user answer is conclusive.

**Decision 2 — Prompt section header when CLI absent: unchanged from iteration 02**

- DECISION: Replace `--- Prompt actions (AI-driven) ---` header with `--- Prompt actions (Copilot CLI not detected — informational only) ---` and render static bullet rows using the format `  • <Title>  →  copilot "Execute the prompt defined in <relative_path>"`.


# 7. Research Plan and Findings

**Methodology:** Internal docs review of all prior iteration artifacts + full source code read of affected files.

**Evidence summary:**

- `02-questionnaire.md` QID-BF-001: Option B checked (`["copilot", "--version"]` detection) and Other checked with answer "If copilot is installed, the cmd command for running it is `copilot`". **Implication:** `_detect_copilot_cli()` must change `["gh", "copilot", "--version"]` → `["copilot", "--version"]`; `run_prompt_action()` must use `["copilot", ...]`.

- `menu.py` `_detect_copilot_cli()` (lines 57–79): currently `["gh", "copilot", "--version"]` — direct 1-line change required.

- `menu.py` `run_prompt_action()` (lines 595–620): currently prints `gh copilot suggest "..."` but never executes. Must be rewritten to `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])`.

- `menu.py` `EXCLUDE_SCRIPTS = {"menu.py", "common.py", "initialize.py"}` (line 16): must add `"reverse-engineer.py"`, `"test_common.py"`.

- `menu.py` `render_menu()` (lines 549–590): `if script: line += f" [{script}]"` and `line += f" [{paction['prompt_file']}]"` confirmed present; both must be removed. Signature must accept `cli_available: bool`.

- `menu.py` `run_action()` (lines 504–543): `print("\nRunning command:")` and `print(" ".join(command))` confirmed present at lines ~514–515; both must be removed.

- `menu.py` `choose_action()` (lines 622–661): CLI detection currently only inside `run_prompt_action()`. Must add `cli_available = _detect_copilot_cli()` before the render loop; pass it to `render_menu()`; when False, set `total_items = len(script_actions)`.

- `close-request.py` (full file): guard `if active_iterations: raise ValidationError(...)` confirmed at lines ~55–57. `COMPLETED`, `format_markdown_table`, `write_text` are NOT yet imported. Must add to import block from `common`.

- `close-iteration.py`: reference write pattern confirmed — `write_text(path, "# Iterations\n\n" + format_markdown_table(header, rows))`.

- `test_common.py`: no `TestCloseRequestAutoClose` class exists. New class must be added with at least: (a) test that `close-request` with active iteration auto-closes it; (b) test that `EXCLUDE_SCRIPTS` contains the two non-tool filenames.

- `implementation.md`: empty (no implementation started). All 5 improvement areas remain to be implemented.

- Product docs: state from iteration 02 confirmed unchanged — ARCH-01, CMP-01, RQT-02, KNW-01 updates all still required and not yet applied.

**Gaps and unknowns:** None. The only open item from iteration 02 (QID-BF-001) is now resolved. No unresolvable gaps remain.

**Files Read:**

- `.aib_memory/requests/R-20260403-0939-menu-improvement/request.md` — Active request confirmed; all five improvement areas and acceptance criteria confirmed.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/iterations.md` — Iterations 01–02 Completed; Iteration 03 Active.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/02-analysis.md` — Full read; all 13 sections reviewed; Assumption A1 (now overridden) and open question confirmed.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/02-questionnaire.md` — QID-BF-001 answered: option B + Other = use bare `copilot` binary.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/implementation.md` — Empty; no implementation started.
- `.aib_memory/references.md` — Full required-read product-doc set identified.
- `.aib_brain/prompts/aib-create-analysis.md` — Prompt being executed; preflight rules confirmed.
- `.aib_brain/conventions/analysis-convention.md` — Full read; all section requirements confirmed.
- `.aib_brain/conventions/request-convention.md` — Request format confirmed.
- `.aib_brain/tools/menu.py` — Full code read: `EXCLUDE_SCRIPTS`, `_detect_copilot_cli()`, `render_menu()`, `run_action()`, `run_prompt_action()`, `choose_action()` all confirmed with exact locations.
- `.aib_brain/tools/close-request.py` — Full code read; guard and import block confirmed.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — POPULATED; AIB Command Menu row confirmed; update required.
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — POPULATED; CMP-ART-0005 and CMP-ART-0006 confirmed; updates required.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — POPULATED; FR-008 confirmed; update required.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — POPULATED; 12 terms (TERM-0001 to TERM-0012); TERM-0013 needed.
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

Update the AIB interactive command menu (`menu.py`) and the `close-request.py` tool script to address five distinct, independent improvement areas:

1. **Exclude non-tool scripts from Script actions.** Add `"reverse-engineer.py"` and `"test_common.py"` to the `EXCLUDE_SCRIPTS` constant in `menu.py` (line 16). These files are auto-discovered by `build_script_actions()` via `discover_tool_scripts()` but are not user-facing tools. After the change, neither entry appears in the Script actions section of the rendered menu.
   - **Actors:** DEVELOPER (menu user), `menu.py` (`EXCLUDE_SCRIPTS` constant).
   - **Trigger:** Any menu render.
   - **Acceptance criterion (AC-1):** Launching the menu renders no entry titled "Reverse Engineer" or "Test Common" in the Script actions section.

2. **Gate prompt actions on `copilot` CLI availability.** Call `_detect_copilot_cli()` once before the `while True` loop in `choose_action()`; pass result as `cli_available: bool` to `render_menu()`. Update `_detect_copilot_cli()` to use `["copilot", "--version"]` for detection (replacing current `["gh", "copilot", "--version"]`). When `cli_available` is `True`, render the Prompt actions section as navigable entries (unchanged from current). When `False`, replace the navigable section with a static non-navigable block headed `--- Prompt actions (Copilot CLI not detected — informational only) ---` with one line per prompt: `  • <Title>  →  copilot "Execute the prompt defined in <relative_path>"`. Set `total_items = len(script_actions)` in `choose_action()` when CLI is absent.
   - **Actors:** DEVELOPER (menu user), `_detect_copilot_cli()` (detection), `render_menu()` (rendering), `choose_action()` (navigation).
   - **Trigger:** Menu render.
   - **Acceptance criterion (AC-2):** On a machine where `copilot --version` returns non-zero or is not found: no prompt action rows have navigable indices; the static informational block is shown. On a machine where it returns 0: prompt actions are navigable.

3. **Execute prompt actions via `copilot` when CLI is present.** When the user selects a prompt action and CLI is available, call `subprocess.run(["copilot", f"Execute the prompt defined in {paction['prompt_file']}"])` without `capture_output` so the interactive CLI session renders in the terminal. After `copilot` exits, return to the menu. Remove all print/copy-paste text from `run_prompt_action()`.
   - **Actors:** DEVELOPER (selects prompt action), `run_prompt_action()` (executes CLI), `copilot` binary (performs AI interaction).
   - **Trigger:** User selects a navigable prompt action.
   - **Acceptance criterion (AC-3):** Selecting a prompt action launches `copilot "Execute the prompt defined in ..."` as an interactive terminal process; no copy/paste text is shown; on `copilot` exit, the menu re-renders.

4. **Remove display clutter from menu rendering and action execution.** In `render_menu()`: remove the `if script: line += f" [{script}]"` clause from the Script actions loop; remove the `line += f" [{paction['prompt_file']}]"` line from the Prompt actions loop. In `run_action()`: remove the `print("\nRunning command:")` line and the `print(" ".join(command))` line. No changes to `collect_parameters()`.
   - **Actors:** DEVELOPER (menu user), `render_menu()`, `run_action()`.
   - **Trigger:** Any menu render; any script action execution.
   - **Acceptance criterion (AC-4):** Menu lines have no bracketed filename suffixes; running a script action does not print `Running command:` or the raw Python command string.

5. **Allow `close-request` to succeed when an active iteration exists.** In `close-request.py`, replace the guard:
   ```python
   if active_iterations:
       raise ValidationError("Cannot close request while an iteration is Active")
   ```
   with logic that:
   (a) Imports `COMPLETED`, `format_markdown_table`, and `write_text` from `common` (add to existing import block).
   (b) Iterates over `active_iterations`; for each, sets `r[it_col["state"]] = COMPLETED` and `r[it_col["closed_at"]] = now_iso()`.
   (c) Writes updated `iterations.md` using `write_text(iterations_path, "# Iterations\n\n" + format_markdown_table(it_header, it_rows))`.
   (d) Prints `f"Auto-closed iteration {r[it_col['iteration_id']]} before closing request."` for each auto-closed iteration.
   (e) Proceeds to close the request as normal.
   - **Actors:** DEVELOPER (runs `close-request`), `close-request.py` (tool), `iterations.md` (data).
   - **Trigger:** `python close-request.py --workspace .` while an active iteration exists.
   - **Acceptance criterion (AC-5):** Command exits code 0; prints `"Auto-closed iteration <id> before closing request."` for each; prints `"Closed request: R-..."`. Running a second time (request already closed) raises `ValidationError("Request already closed")`.

## Background

The AIB interactive menu is the primary developer access point for AIB lifecycle tools. Unnecessary entries, verbose output, and blocked workflows degrade developer experience and introduce errors.

## Scope

- `menu.py`: `EXCLUDE_SCRIPTS` extension; `_detect_copilot_cli()` binary change (`gh copilot` → `copilot`); `render_menu()` suffix removal and CLI-gating parameter; `run_action()` command-line removal; `choose_action()` pre-loop detection and navigation gating; `run_prompt_action()` real `copilot` execution.
- `close-request.py`: Guard replacement with auto-close logic; add `COMPLETED`, `format_markdown_table`, `write_text` to imports.
- `test_common.py`: New test cases for close-request auto-close path and `EXCLUDE_SCRIPTS` coverage.
- Documentation: `ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`.

## Out of scope

- No changes to prompt `.md` files.
- No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `common.py`.
- No new Python dependencies.
- No changes to CI workflow or release bookkeeping.
- No changes to `collect_parameters()`.

## Functional expectations

- Menu renders without `[script]` / `[prompt_file]` suffixes on any action line.
- When `copilot` CLI absent: prompt section replaced by static informational block; navigation indices `[1..n]` cover only Script actions.
- When `copilot` CLI present: prompt actions are navigable and execute `copilot "Execute the prompt defined in <path>"` on selection.
- `close-request` with active iteration: exits code 0, auto-closes iteration, prints notice per closed iteration.
- `close-request` with no active iteration: behavior unchanged.

## Non-functional expectations

- No new Python package dependencies.
- Cross-platform (Windows + POSIX).
- Idempotent: `close-request` on already-closed request still raises `ValidationError("Request already closed")`.
- Session-cached CLI detection: `copilot --version` called at most once per menu session.

## Measurable acceptance criteria

1. **AC-1:** Launching the menu: neither "Reverse Engineer" nor "Test Common" appears in any section.
2. **AC-2:** On a machine without `copilot` on PATH: no prompt action rows are navigable; a static `  • <Title>  →  copilot "Execute the prompt defined in ..."` list is shown below the Script actions section.
3. **AC-3:** On a machine with `copilot`: selecting a prompt action launches `copilot "Execute the prompt defined in ..."` interactively; no copy/paste text appears.
4. **AC-4:** Running any script action: the terminal no longer displays `Running command:` or the raw Python command string.
5. **AC-5:** `python close-request.py --workspace .` while an iteration is Active: exits code 0, prints `"Auto-closed iteration <id> before closing request."`, then `"Closed request: R-..."`.
6. **AC-6:** `pytest .aib_brain/tools/test_common.py` passes at 100%.


# 9. Solution Options

## Option A — Targeted direct code changes (recommended)

**Overview:** The smallest set of direct modifications to `menu.py` and `close-request.py` satisfying all five improvement areas. No new modules, configuration files, or abstractions.

**Benefits:** Minimal diff; easy to review; consistent with existing patterns; no structural changes to function signatures beyond the new `cli_available` parameter.

**Trade-offs:** `EXCLUDE_SCRIPTS` requires manual maintenance for future non-tool scripts added to the `tools/` directory.

**Constraints:** Python 3.10+ / stdlib only.

**Risks:** If `copilot` binary invocation format changes in future CLI versions, `run_prompt_action()` would need updating (low risk, low impact).

**Expected effort:** Low — approximately 60–80 lines changed/added across two source files, ~30 lines for new test class, and ~5 documentation field updates.

**Acceptance test ideas:** Visual inspection of menu output; `copilot` subprocess invocation confirmed in `run_prompt_action()`; `pytest test_common.py` at 100%.

DECISION: Option A accepted. Targeted and isolated changes; no architectural deviation.

## Option B — Allowlist approach for script discovery

**Overview:** Replace `EXCLUDE_SCRIPTS` (blocklist) with an explicit allowlist of known tool scripts. Avoids silent re-appearance of non-tool scripts as the codebase grows.

**Benefits:** Future-proof against accidental menu pollution.

**Trade-offs:** More invasive change to `discover_tool_scripts()` and `build_script_actions()`; requires explicit maintenance of the allowlist; out of scope per request.md.

**Constraints:** Out of scope per request.md "Out of scope" section.

**Expected effort:** Medium — requires refactoring `discover_tool_scripts()`.

Not recommended for this iteration.


# 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | AIB Command Menu description: reflect CLI-gated prompt actions (`copilot` binary), static informational block, non-tool script exclusions |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | CMP-ART-0005 edge_cases: add auto-close-iteration side effect; CMP-ART-0006 edge_cases: add CLI-gating and EXCLUDE_SCRIPTS notes |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | FR-008: update to specify CLI-gated prompt action navigation and `copilot` execution |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Add TERM-0013 "Prompt Action" |


# 11. Operational & Documentation Implications

- **Runbooks:** No runbook changes required. The menu and close-request are interactive developer tools.

- **SLAs/SLOs:** Not applicable.

- **Monitoring/observability:** No structured log changes. The `close-request.py` auto-close prints a human-readable notice to stdout per auto-closed iteration. No structured event required.

- **Data quality rules:** Not applicable.

- **Product documentation artifact updates:**
  - `ARCH-01` Component Inventory — AIB Command Menu row: update Description to reference `copilot` CLI-gating (detection via `copilot --version`), static informational block when CLI absent, and the `EXCLUDE_SCRIPTS` mechanism for non-tool scripts.
  - `CMP-01` CMP-ART-0005 `edge_cases_and_validation`: replace `"Fail if invalid lifecycle state"` with `"Fail if invalid lifecycle state; auto-closes active iteration before closing request and prints notice per closed iteration."`.
  - `CMP-01` CMP-ART-0006 `edge_cases_and_validation`: replace `"Must surface failures clearly"` with `"Must surface failures clearly; prompt actions require copilot CLI (non-navigable static info block when absent); non-tool scripts (reverse-engineer.py, test_common.py) excluded from discovery via EXCLUDE_SCRIPTS."`.
  - `RQT-02` FR-008: revise to `"The system supports launching tool scripts via an interactive menu; prompt actions are only navigable when the copilot CLI binary is detected (copilot --version exit code 0); when absent, prompt actions are displayed as a static informational list."`.
  - `KNW-01`: Add row `TERM-0013 | Prompt Action | A menu entry in the AIB Command Menu mapping to an .aib_brain/prompts/aib-*.md file; executable via the copilot binary when it is available on PATH; displayed as a static informational entry otherwise. | Create Analysis menu entry | AIB Maintainers | — | menu, workflow | Proposed | 1`.


# 12. Risks

- Risk R1: `copilot` interactive pass-through incompatible on some terminal or OS configuration.
  - Probability: Low
  - Impact: Medium — prompt actions would hang or produce garbled output.
  - Mitigation: Test `subprocess.run(["copilot", ...])` without `capture_output` on both Windows and POSIX target machines before merge.
  - Owner (role): DEVELOPER

- Risk R2: Auto-closing an active iteration in `close-request.py` fails midway, leaving `iterations.md` in a partially written state.
  - Probability: Low
  - Impact: High — iteration state becomes inconsistent; subsequent tool runs may fail.
  - Mitigation: Use the same `write_text` atomic replacement pattern from `close-iteration.py`. Validate `format_markdown_table` output before write.
  - Owner (role): AIB Maintainers

- Risk R3: `EXCLUDE_SCRIPTS` does not auto-grow; future test or helper `.py` files in `tools/` will silently reappear in the menu.
  - Probability: Medium (as codebase grows)
  - Impact: Low — cosmetic defect (extra menu entries).
  - Mitigation: Document the convention in ARCH-01 or CMP-01 that all non-tool `.py` files in `tools/` must be listed in `EXCLUDE_SCRIPTS`. Consider allowlist approach in a future request.
  - Owner (role): AIB Maintainers

- Risk R4: `copilot` binary accepts the prompt string in a different format than `copilot "Execute the prompt defined in <path>"` (Assumption A2 false).
  - Probability: Low — user confirmed this invocation form in QID-BF-001.
  - Impact: Medium — `copilot` exits with an error or displays help text instead of executing the prompt.
  - Mitigation: Validate manually by running `copilot "Execute the prompt defined in test.md"` on the target machine before implementing.
  - Owner (role): DEVELOPER

- Risk R5: Moving CLI detection from lazy to eager introduces perceptible startup delay if `copilot --version` is slow on some machines.
  - Probability: Low — the 5-second timeout in `_detect_copilot_cli()` is the upper bound.
  - Impact: Low — slight UX degradation on first menu load.
  - Mitigation: The cached `_COPILOT_CLI_AVAILABLE` prevents repeated delays on subsequent renders. Acceptable as-is.
  - Owner (role): DEVELOPER


# 13. Open Questions & Next Actions

No open questions remain. All user-owned items from previous iterations are resolved:

- QID-BF-001 (CLI binary): Resolved by 02-questionnaire.md answer — use bare `copilot` binary.
- QID-BF-002, QID-BF-003, QID-AT-001, QID-AT-002 from iteration 01: All resolved by request.md Goal section updates (confirmed in iteration 02 analysis).

**Next action:** Proceed to implementation. One Risk R4 pre-validation is recommended (confirm `copilot "<prompt>"` invocation format on target machine) but is not blocking — it can be performed as the first step of the implementation phase.

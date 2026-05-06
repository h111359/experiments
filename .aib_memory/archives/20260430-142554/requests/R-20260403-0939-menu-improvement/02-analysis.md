# 1. Executive Summary

- **Request ID:** R-20260403-0939

- **Request title:** Menu Improvement

- **Iteration ID:** 02

- **High-level purpose:** Follow-up analysis after iteration 01 (completed 2026-04-03 10:57:01 +0300). Iteration 01 produced an analysis and questionnaire with 4 user-owned open questions and 5 questionnaire items. The request.md Goal section has since been updated with implementation-ready specifications that implicitly resolve all open questions. This iteration confirms those resolutions, refines concrete code-change specifications, addresses a CLI invocation inconsistency between the request.md and iteration 01's rewrite proposal, and is designed to be the final analysis before implementation proceeds.

- **Prior iterations:** Iteration 01 yielded: analysis `01-analysis.md`, questionnaire `01-questionnaire.md`. No implementation.md entries exist yet. The questionnaire asked 5 questions (QID-BF-001 through QID-AT-002); the request.md Goal section answers all 5 definitively (see Scope Interpretation).

- **Conflicts resolved:** The request.md Goal section and the iteration 01 Section 8 rewrite proposal diverge on the GitHub Copilot CLI invocation format (`["copilot", ...]` vs `["gh", "copilot", "suggest", ...]`). This analysis resolves the conflict in favour of `["gh", "copilot", "suggest", ...]` consistent with the existing `_detect_copilot_cli()` implementation (see Assumption A1). The user should confirm during Assumption A1 falsification if a different CLI binary is intended.

- **Key changes scoped:** `menu.py` (5 targeted edits), `close-request.py` (1 targeted edit), `test_common.py` (new test cases), documentation updates (`ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`).

- **Expected outcome if accepted:** Iteration 01 questionnaire items fully resolved; implementation can proceed without further clarification.


# 2. Scope Interpretation

- **In scope — explicit (5 improvement areas from request.md Goal):**

  Improvement 1: Add `"reverse-engineer.py"` and `"test_common.py"` to `EXCLUDE_SCRIPTS` in `menu.py`. Confirmed answer to QID-AT-001 (Option A — extend EXCLUDE_SCRIPTS, not allowlist).

  Improvement 2: Gate prompt actions on `gh copilot` CLI availability; when absent, render a static non-navigable informational block. Confirmed answer to QID-BF-002 (Option A — static block in same menu screen). CLI detection must move from lazy (action-time) to eager (menu-entry time) to support conditional rendering.

  Improvement 3: When CLI present and user selects a prompt action, call `subprocess.run(["gh", "copilot", "suggest", "Execute the prompt defined in <path>"])` without `capture_output`. Remove existing copy/paste text from `run_prompt_action()`.

  Improvement 4: Remove `[script]` suffix from Script action lines and `[prompt_file]` suffix from Prompt action lines in `render_menu()`. Remove `print("\nRunning command:")` and `print(" ".join(command))` from `run_action()`. Confirmed answer to QID-BF-001 (Option A — keep descriptions, remove bracketed suffixes only). Confirmed answer to QID-AT-002 (Option A — leave `collect_parameters()` unchanged).

  Improvement 5: In `close-request.py`, replace the `ValidationError("Cannot close request while an iteration is Active")` guard with auto-close logic that writes `Completed` state and current timestamp to `iterations.md` and prints `"Auto-closed iteration <id> before closing request."` before proceeding. Confirmed answer to QID-BF-003 (Option A — print notice, no confirmation prompt).

- **Out of scope — explicit (from request.md):**

  No changes to prompt `.md` files.

  No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `common.py`.

  No new Python dependencies.

  No changes to CI workflow or release bookkeeping.

- **Implicit in scope:**

  (implicit rule - AIB framework) Documentation updates are required when code components are changed: `ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`.

  (implicit rule - AIB framework) Test coverage must be extended in `test_common.py` for the `close-request` auto-close path.


# 3. Domain Knowledge Essentials

- **AI Builder (AIB):** Model-agnostic framework for specification-driven development. The interactive menu (`menu.py`) is the primary developer access point.

- **AIB Command Menu (CMP-ART-0006):** Terminal UI launcher; surfaces Script actions (lifecycle tool scripts) and Prompt actions (AI-driven `.aib_brain/prompts/aib-*.md` triggers). Primary persona: DEVELOPER.

- **Prompt Action:** A menu entry that maps to a `.aib_brain/prompts/aib-*.md` file. When GitHub Copilot CLI is available, it executes the prompt via `gh copilot suggest`. When CLI is absent it is displayed informatively only.

- **GitHub Copilot CLI (`gh copilot`):** Optional CLI extension to the GitHub CLI. Detected via `gh copilot --version`. Availability is machine-dependent. Absence must not break the menu; presence enables real prompt execution.

- **Iteration lifecycle:** A request may have multiple sequential iterations. `close-request.py` previously blocked if an active iteration existed; the improvement removes this block by auto-closing the iteration first.

- **Impacted roles/personas:** DEVELOPER (daily menu user). AI_AGENT (reads prompts directly via prompt files; not affected by menu navigation changes).

- **Business process touched:** AIB lifecycle management — specifically request creation/closure (UC-005 equivalent, close-request flow) and developer tool usage.


# 4. Technical Knowledge & Terms

- **`menu.py`** — `.aib_brain/tools/menu.py`. Interactive terminal UI. Uses `msvcrt` (Windows) / `termios` (POSIX) for unbuffered key input.

- **`EXCLUDE_SCRIPTS`** — `set[str]` constant in `menu.py`; current value: `{"menu.py", "common.py", "initialize.py"}`. `discover_tool_scripts()` skips any `.py` file listed here.

- **`build_script_actions()`** — Constructs the ordered list of script actions. Hardcodes the 4 lifecycle scripts first, then appends any extras discovered by `discover_tool_scripts()`. `reverse-engineer.py` and `test_common.py` are currently discovered as extras because they are absent from `EXCLUDE_SCRIPTS`.

- **`render_menu()`** — Renders the terminal menu. Currently appends `[{script}]` to each script action line (line ~570) and `[{paction['prompt_file']}]` to each prompt action line (~583). Both suffixes must be removed. Additionally must accept a `cli_available: bool` parameter to conditionally render prompt actions as navigable or as a static informational block.

- **`run_action()`** — Executes a script action. Contains `print("\nRunning command:")` and `print(" ".join(command))` at lines ~520–521 (before the `subprocess.run` call). Both lines must be removed.

- **`run_prompt_action()`** — Currently shows copy/paste instructions and (when CLI detected) a `gh copilot suggest` command string, but never executes anything. Must be rewritten to: (a) call `subprocess.run(["gh", "copilot", "suggest", chat_prompt])` without `capture_output` when CLI is available; (b) remove all copy/paste text; (c) return to menu after CLI exits. This function is called only when CLI is confirmed available (see `choose_action()` gating change).

- **`_detect_copilot_cli()`** — Lazy-cached detection using `["gh", "copilot", "--version"]`. Currently called only on prompt action selection. Must be called eagerly (once per `choose_action()` loop iteration or before the loop) so the result is available for `render_menu()` conditional rendering.

- **`choose_action()`** — Main navigation loop. Must be updated to: (a) detect CLI availability before calling `render_menu()`; (b) pass `cli_available` to `render_menu()`; (c) when CLI absent, exclude prompt action indices from navigation (`total_items = len(script_actions)` only); (d) when CLI present, navigation and execution remain as today.

- **`close-request.py`** — Current guard (`lines ~55–57`): `if active_iterations: raise ValidationError("Cannot close request while an iteration is Active")`. Replace with: iterate over `active_iterations`, set `state = COMPLETED`, set `closed_at = now_iso()`, write updated `iterations.md` using `format_markdown_table` + `write_text`, then print `"Auto-closed iteration {id} before closing request."` for each. Execution then proceeds to close the request.

- **`close-iteration.py`** — Reference implementation for the iteration-close filesystem write. Uses `format_markdown_table(header, rows)` + `write_text(iterations_path, "# Iterations\n\n" + content)`. The same pattern must be used in `close-request.py`.

- **`common.py`** — Provides `COMPLETED`, `format_markdown_table`, `write_text`, `now_iso` — all already imported or importable in `close-request.py`. No new imports from external packages needed.

- **Python 3.10+ / stdlib only** — NFR-004 from RQT-02. No new packages.

- **Cross-platform** — Windows (primary, `run.bat`) and POSIX (`run.sh`) must both be supported. `subprocess.run` without `capture_output` passes stdin/stdout/stderr through to the terminal on both platforms.

- **`gh copilot suggest`** — CLI invocation: `gh copilot suggest "Execute the prompt defined in <path>"`. Executed without `capture_output` for interactive pass-through. Detection: `["gh", "copilot", "--version"]` (already the current implementation in `_detect_copilot_cli()`).

- **Invocation string format for informational block (CLI absent):** Each prompt entry renders as:
  `  • <Title>  →  gh copilot suggest "Execute the prompt defined in <relative_prompt_file>"`


# 5. Assumptions

- Assumption A1: `copilot` in request.md Goal item 2 (`copilot --version`) and item 3 (`subprocess.run(["copilot", ...])`) is shorthand for `gh copilot`, not a separate standalone `copilot` binary.
  - Rationale: The existing `_detect_copilot_cli()` function already uses `["gh", "copilot", "--version"]`, which implies the implementation was intentionally targeting the GitHub CLI extension. The iteration 01 Section 8 rewrite proposal explicitly used `["gh", "copilot", "suggest", ...]`. There is no widely distributed standalone `copilot` binary on standard developer machines. The acceptance criterion in request.md (item 3) also says `copilot suggest "..."` which matches `gh copilot suggest "..."` syntax.
  - Risk if false: If the user intends a different `copilot` binary (e.g., a VS Code CLI tool), the subprocess call with `["gh", "copilot", "suggest", ...]` would fail silently or with FileNotFoundError, and detection via `gh copilot --version` would not match the intended tool.
  - Falsification method: User confirms whether the intended executable is `gh copilot` (GitHub CLI extension) or a different binary named `copilot`. Also verify by running `copilot --version` on the target machine to see if it resolves.

- Assumption A2: The `collect_parameters()` parameter input banner (`"Parameter input"` / `"---------------"`) and per-field hint lines are intentionally left unchanged.
  - Rationale: The request.md Goal item 4 specifically scopes the UX cleanup to `render_menu()` suffix removal and `run_action()` command-line removal. `collect_parameters()` is not mentioned. Iteration 01 QID-AT-002 recommended Option A (leave unchanged); the request.md Goal confirms this by not naming `collect_parameters()`.
  - Risk if false: User may expect a smoother parameter collection flow; leaving it verbose would be a missed UX improvement.
  - Falsification method: Review request.md "Functional expectations" — none mention `collect_parameters()`.

- Assumption A3: The static informational block for prompt actions (CLI absent) is rendered within the same menu screen, below the Script actions section, replacing the `--- Prompt actions (AI-driven) ---` navigable section. It is non-navigable and non-selectable.
  - Rationale: Request.md functional expectations state "When CLI absent: prompt section replaced by static informational text; indices [1..n] map only to script actions." "Replaced" implies the same screen position; "static" and "non-selectable" are requirements.
  - Risk if false: If user expects a different layout (e.g., separate view), the single-screen static block would be rejected.
  - Falsification method: User reviews the rendered static block output during acceptance testing.

- Assumption A4: CLI detection (`_detect_copilot_cli()`) is converted from purely lazy (first prompt action selection) to pre-loop detection within `choose_action()`: called once before entering the `while True` render loop. The per-session cache (`_COPILOT_CLI_AVAILABLE`) prevents repeated subprocess calls on subsequent renders.
  - Rationale: `render_menu()` must know CLI availability to conditionally render sections. Detecting inside the render call per loop iteration is also valid but the cache makes it equivalent. Calling before the loop is the cleaner design.
  - Risk if false: If the initial detection call adds perceptible startup delay, the user experience degrades. Mitigated by the 5-second timeout already in `_detect_copilot_cli()` and typical `gh --version` response being <200 ms.
  - Falsification method: Measure menu startup latency with and without the pre-call on the developer machine.

- Assumption A5: `close-request.py` can import `COMPLETED`, `format_markdown_table`, and `write_text` from `common.py` without changes to `common.py`.
  - Rationale: All three names are already defined in `common.py` and imported in other tool scripts (`close-iteration.py` imports `COMPLETED`, `format_markdown_table`, `write_text`). Adding them to `close-request.py`'s import block is sufficient.
  - Risk if false: If `common.py` does not export `COMPLETED` or `write_text`, the import will fail at runtime.
  - Falsification method: Grep `common.py` for `COMPLETED =` and `def write_text`.


# 6. Impact Assessment

## 6.1 Affected Components / Areas

- `.aib_brain/tools/menu.py` — 5 targeted changes (see Section 7 evidence log for exact locations).

- `.aib_brain/tools/close-request.py` — 1 targeted change: guard replacement with auto-close logic.

- `.aib_brain/tools/test_common.py` — New test cases for: (a) `close-request` auto-close path; (b) `EXCLUDE_SCRIPTS` containing `reverse-engineer.py` and `test_common.py`.

- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Update AIB Command Menu component description.

- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — Update CMP-ART-0005 (close-request) and CMP-ART-0006 (menu) `edge_cases_and_validation` fields.

- `.aib_memory/docs/03 Requirements/RQT-02.md` — Update FR-008 (interactive menu) to specify CLI-gated prompt action behavior.

- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Add TERM-0013 "Prompt Action".

## 6.2 Change Type and Dependencies

| Area | Change type | Dependencies | Sequencing |
| --- | --- | --- | --- |
| `menu.py` — EXCLUDE_SCRIPTS | modify (1 line) | none | First |
| `menu.py` — `render_menu()` suffix removal | modify (2 lines removed) | none | Independent |
| `menu.py` — `run_action()` command print removal | modify (2 lines removed) | none | Independent |
| `menu.py` — `render_menu()` + `choose_action()` CLI gating | modify (signature + branch logic) | `_detect_copilot_cli()` pre-call | After EXCLUDE_SCRIPTS |
| `menu.py` — `run_prompt_action()` real execution | modify (replace body) | CLI gating in `choose_action()` | After CLI gating |
| `close-request.py` — auto-close iteration | modify (guard replacement) | `COMPLETED`, `format_markdown_table`, `write_text` from `common.py` | Independent |
| `test_common.py` — new tests | add | all above code changes applied | Last |
| Documentation updates | modify | code changes completed | Final |

## 6.3 Domain Impacts

- DOMAIN (ARCH): Minor. AIB Command Menu description in ARCH-01 must reflect prompt-action CLI gating and the addition of `reverse-engineer.py` / `test_common.py` to `EXCLUDE_SCRIPTS`.
  - Relevant: ARCH-01 Component Inventory row "AIB Command Menu".

- DOMAIN (CMP): Moderate. CMP-ART-0005 `edge_cases_and_validation` must note that close-request auto-closes active iterations. CMP-ART-0006 `edge_cases_and_validation` must note prompt-action CLI-gating behaviour and the excluded scripts.
  - Relevant: CMP-01 rows CMP-ART-0005 and CMP-ART-0006.

- DOMAIN (DATA): No impact detected.

- DOMAIN (KNW): Low. Glossary requires TERM-0013 "Prompt Action" to distinguish from TERM-0011 "Tool Script".
  - Relevant: KNW-01.

- DOMAIN (RQT): Low. FR-008 must be updated to specify that prompt actions require CLI and that non-tool scripts are excluded from discovery.
  - Relevant: RQT-02 FR-008.

- DOMAIN (DEV/DSR/FNL/OBS/OPR/SEC): No impact detected.

## 6.4 Constraints

- Python 3.10+ / stdlib only (NFR-004). No new packages.
- Cross-platform: Windows (`msvcrt`) and POSIX (`termios`). The `subprocess.run(["gh", "copilot", "suggest", ...])` call without `capture_output` passes through on both platforms.
- Exactly one active iteration lifecycle rule: `close-request.py` auto-close must be guarded to only run when `active_iterations` is non-empty — if empty, skip the auto-close path entirely (i.e., no crash when no active iteration exists).
- `_detect_copilot_cli()` must remain cached (`_COPILOT_CLI_AVAILABLE` global) to avoid repeated subprocess calls on every menu render cycle.

## 6.5 Required Documentation Updates

- ARCH-01 — AIB Command Menu component description
  Required update? YES
  Reason: Prompt-action gating behaviour; excluded non-tool scripts.

- CMP-01 — CMP-ART-0005 and CMP-ART-0006
  Required update? YES
  Reason: CMP-ART-0005 edge_cases: add auto-close-iteration side effect. CMP-ART-0006 edge_cases: add CLI-gating and EXCLUDE_SCRIPTS note.

- RQT-02 — FR-008
  Required update? YES
  Reason: Must specify CLI-gated prompt actions and non-tool script exclusion.

- KNW-01 — Glossary
  Required update? YES
  Reason: Add TERM-0013 "Prompt Action" (previously flagged as conditional in iteration 01; confirmed required given the complexity of the new CLI-gated behavior).

## 6.6 Decision Points

**Decision 1 — CLI invocation form: `gh copilot suggest` vs bare `copilot`**

- Option 1A: Use `["gh", "copilot", "suggest", chat_prompt]` — consistent with current detection (`gh copilot --version`), iteration 01 rewrite, and `gh` CLI ecosystem conventions.
  - Recommended: YES.

- Option 1B: Use `["copilot", chat_prompt]` — matches the literal subprocess list in request.md Goal item 3 but would require changing detection to `["copilot", "--version"]` and is inconsistent with the existing `_detect_copilot_cli()` implementation.

- Option 1C: Use `["copilot", "suggest", chat_prompt]` — mirrors `gh copilot suggest` but under a bare `copilot` binary; only valid if a standalone `copilot` CLI exists on target machines.

**Decision 2 — Prompt section header when CLI absent**

- Option 2A: Replace `--- Prompt actions (AI-driven) ---` header with `--- Prompt actions (Copilot CLI not detected — informational only) ---` and render static bullet rows beneath it.
  - Recommended: YES — clear indication to the developer why the section is non-interactive.

- Option 2B: Omit the prompt section entirely when CLI absent.
  - Not recommended — information about available prompts is still useful even without execution capability.


# 7. Research Plan and Findings

**Methodology:** Internal docs scan + full source code read of all affected files.

**Evidence summary:**

- `menu.py` `EXCLUDE_SCRIPTS = {"menu.py", "common.py", "initialize.py"}` — does not contain `reverse-engineer.py` or `test_common.py`. Both appear in the menu via `discover_tool_scripts()`. **Implication:** extending the set removes them.

- `render_menu()` script loop: `if script: line += f" [{script}]"` — appends script filename suffix. Must be removed.

- `render_menu()` prompt loop: `line += f" [{paction['prompt_file']}]"` — appends prompt file suffix. Must be removed.

- `run_action()`: `print("\nRunning command:")` and `print(" ".join(command))` appear before the `subprocess.run` call (lines ~520–521). Both must be removed.

- `run_prompt_action()`: current body shows copy/paste text and conditionally shows a `gh copilot suggest` command string, but never executes `subprocess.run`. Must be replaced with an executable call.

- `choose_action()`: `discover_prompt_actions()` called unconditionally; prompt actions always navigable (`total_items = len(script_actions) + len(prompt_actions)`). Must be gated: when CLI absent, `total_items = len(script_actions)` and prompt section rendered as static block.

- `_detect_copilot_cli()`: uses `["gh", "copilot", "--version"]`; result cached in `_COPILOT_CLI_AVAILABLE`. Currently called only inside `run_prompt_action()`. Must be called before `render_menu()` for gating to work.

- `close-request.py` guard (lines ~55–57): `if active_iterations: raise ValidationError("Cannot close request while an iteration is Active")`. Must be replaced. `close-iteration.py` provides the canonical pattern: set `state = COMPLETED`, `closed_at = now_iso()`, write `"# Iterations\n\n" + format_markdown_table(header, rows)` to `iterations_path`. `COMPLETED`, `format_markdown_table`, `write_text` must be added to `close-request.py` imports from `common`.

- `test_common.py`: contains tests for `common.py` helpers (table parsing, register operations, etc.). Does NOT contain tests for `close-request` auto-close behaviour. New test class `TestCloseRequestAutoClose` must be added.

- `common.py` imports available: `COMPLETED` is defined as a constant; `format_markdown_table` and `write_text` are functions. All three are already exported by `close-iteration.py`'s import list, confirming they are available.

- `KNW-01` glossary: 12 terms (TERM-0001 to TERM-0012). No "Prompt Action" term exists. TERM-0013 must be added.

- `CMP-01` CMP-ART-0005 `edge_cases_and_validation` field: currently `"Fail if invalid lifecycle state"`. Must add: `"Auto-closes active iteration before closing request; prints notice per closed iteration."`.

- `CMP-01` CMP-ART-0006 `edge_cases_and_validation` field: currently `"Must surface failures clearly"`. Must add: `"Prompt actions require gh copilot CLI; non-tool scripts (reverse-engineer.py, test_common.py) excluded from discovery."`.

**Gaps and unknowns:**

- CLI binary name ambiguity: confirmed as assumption A1 (`copilot` in request.md = `gh copilot`). No unresolvable gap; implementation follows `gh copilot suggest` form.

- No gaps in code understanding; all affected functions fully read.

**Files Read:**

- `.aib_memory/requests/R-20260403-0939-menu-improvement/request.md` — Active request; Goal, Scope, Functional expectations, Acceptance criteria confirmed.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/iterations.md` — Iteration 01 Completed, Iteration 02 Active.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/01-analysis.md` — Prior iteration analysis; all 13 sections read; open questions and questionnaire context confirmed.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/01-questionnaire.md` — 5 questionnaire items confirmed; all implicitly answered by request.md Goal section.
- `.aib_memory/requests/R-20260403-0939-menu-improvement/implementation.md` — Append-only; no entries yet.
- `.aib_memory/references.md` — Full required-read product-doc set identified (27 entries).
- `.aib_brain/prompts/aib-create-analysis.md` — Prompt being executed; preflight rules confirmed.
- `.aib_brain/conventions/analysis-convention.md` — Full convention read; all section requirements confirmed.
- `.aib_brain/conventions/request-convention.md` — Request format convention confirmed.
- `.aib_brain/Concepts.md` — Invocation contract confirmed; `close-request` action contract confirmed.
- `.aib_brain/tools/menu.py` — Full file read; all affected functions identified with exact code locations.
- `.aib_brain/tools/close-request.py` — Full file read; active-iteration guard confirmed.
- `.aib_brain/tools/close-iteration.py` — Full file read; reference write pattern confirmed.
- `.aib_brain/tools/test_common.py` — Full file read; confirmed no close-request tests exist; test structure understood.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — POPULATED; AIB Command Menu component row confirmed.
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — POPULATED; CMP-ART-0005 and CMP-ART-0006 rows confirmed; fields to update identified.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — POPULATED; FR-008 confirmed; NFR-004 (Python 3.10+) confirmed.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — POPULATED; 12 terms; no "Prompt Action" term; TERM-0013 needed.
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — POPULATED; DEVELOPER persona confirmed as primary menu user.
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
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — `[SKIPPED — domain out of scope]`
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — `[SKIPPED — domain out of scope]`


# 8. Rewrite Proposal of the Request

## Goal

Update the AIB interactive command menu (`menu.py`) and the `close-request.py` tool script to address five distinct, independent improvement areas:

1. **Exclude non-tool scripts from Script actions.** Add `"reverse-engineer.py"` and `"test_common.py"` to the `EXCLUDE_SCRIPTS` constant in `menu.py`. These files are auto-discovered by `build_script_actions()` via `discover_tool_scripts()` but are not user-facing tools: `reverse-engineer.py` is a JSON-inventory helper for the `aib-reverse-engineer.md` prompt; `test_common.py` is a pytest test file. After the change, neither entry appears in the Script actions section of the rendered menu.
   - **Actors:** DEVELOPER (menu user), `menu.py` (tool).
   - **Trigger:** Any menu render.
   - **Acceptance criterion (AC-1):** Launching the menu renders no entry titled "Reverse Engineer" or "Test Common" in the Script actions section.

2. **Gate prompt actions on GitHub Copilot CLI availability.** Detect CLI availability by calling `_detect_copilot_cli()` once at the start of `choose_action()` before entering the render loop (result is session-cached). Pass `cli_available: bool` to `render_menu()`. When `True`, render the Prompt actions section as today (navigable entries). When `False`, replace the navigable Prompt actions section with a static non-navigable informational block headed `--- Prompt actions (Copilot CLI not detected — informational only) ---` with one bullet per discovered prompt in the form `  • <Title>  →  gh copilot suggest "Execute the prompt defined in <relative_path>"`. Adjust `total_items` in `choose_action()` to `len(script_actions)` when CLI is absent so prompt indices are not navigable.
   - **Actors:** DEVELOPER (menu user), `_detect_copilot_cli()` (detection), `render_menu()` (rendering), `choose_action()` (navigation).
   - **Trigger:** Menu render.
   - **Acceptance criterion (AC-2):** On a machine where `gh copilot --version` returns non-zero (or binary not found): no prompt action rows have navigable indices; the static informational block is shown with invocation strings. On a machine where it returns 0: all prompt actions are navigable.

3. **Execute prompt actions via `gh copilot suggest` when CLI is present.** When the user selects a prompt action and CLI is available, call `subprocess.run(["gh", "copilot", "suggest", f"Execute the prompt defined in {paction['prompt_file']}"])` without `capture_output` so the interactive CLI session renders in the terminal. After `gh copilot suggest` exits, return to the menu. Remove the existing copy/paste suggestion text and the `print(f"GitHub Copilot CLI command: ...")` block from `run_prompt_action()`.
   - **Actors:** DEVELOPER (selects prompt action), `run_prompt_action()` (executes CLI), `gh copilot` (performs AI interaction).
   - **Trigger:** User selects a navigable prompt action.
   - **Acceptance criterion (AC-3):** Selecting a prompt action launches `gh copilot suggest "Execute the prompt defined in ..."` as an interactive terminal process; no copy/paste text is shown; on `gh copilot` exit, the menu re-renders.

4. **Remove display clutter from menu rendering and action execution.** In `render_menu()`: remove the `if script: line += f" [{script}]"` clause from the Script actions loop and remove the `line += f" [{paction['prompt_file']}]"` line from the Prompt actions loop. In `run_action()`: remove the `print("\nRunning command:")` line and the `print(" ".join(command))` line. No changes to `collect_parameters()`.
   - **Actors:** DEVELOPER (menu user), `render_menu()`, `run_action()`.
   - **Trigger:** Any menu render; any script action execution.
   - **Acceptance criterion (AC-4):** Menu lines have no bracketed filename suffixes; running a script action does not print `Running command:` or the raw Python command string to the terminal.

5. **Allow `close-request` to succeed when an active iteration exists.** In `close-request.py`, replace the guard:
   ```python
   if active_iterations:
       raise ValidationError("Cannot close request while an iteration is Active")
   ```
   with logic that:
   (a) Imports `COMPLETED`, `format_markdown_table`, and `write_text` from `common`.
   (b) Iterates over `active_iterations`; for each, sets `r[it_col["state"]] = COMPLETED` and `r[it_col["closed_at"]] = now_iso()`.
   (c) Writes updated `iterations.md` as `"# Iterations\n\n" + format_markdown_table(it_header, it_rows)`.
   (d) Prints `f"Auto-closed iteration {r[it_col['iteration_id']]} before closing request."` for each auto-closed iteration.
   (e) Proceeds to close the request as normal.
   - **Actors:** DEVELOPER (runs `close-request`), `close-request.py` (tool), `iterations.md` (data).
   - **Trigger:** `python close-request.py --workspace .` while an active iteration exists.
   - **Acceptance criterion (AC-5):** Command exits code 0; prints `"Auto-closed iteration <id> before closing request."` for each auto-closed iteration; prints `"Closed request: R-..."`. Running it a second time (request already closed) still raises `ValidationError("Request already closed")`.

## Background

The AIB interactive menu is the primary developer access point for AIB lifecycle tools. Unnecessary entries, verbose output, and blocked workflows degrade developer experience and introduce errors.

## Scope

- `menu.py`: `EXCLUDE_SCRIPTS` extension; `render_menu()` suffix removal and CLI-gating; `run_action()` command-line removal; `choose_action()` CLI-detection and navigation gating; `run_prompt_action()` real CLI execution.
- `close-request.py`: Guard replacement with auto-close logic.
- `test_common.py`: New test cases for close-request auto-close path.
- Documentation: `ARCH-01`, `CMP-01`, `RQT-02`, `KNW-01`.

## Out of scope

- No changes to prompt `.md` files.
- No changes to `initialize.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py`, `common.py`.
- No new Python dependencies.
- No changes to CI workflow or release bookkeeping.
- No changes to `collect_parameters()`.

## Functional expectations

- Menu renders without `[script]` / `[prompt_file]` suffixes on any action line.
- When CLI absent: prompt section replaced by static informational block; navigation indices `[1..n]` cover only Script actions.
- When CLI present: prompt actions are navigable and execute `gh copilot suggest "Execute the prompt defined in <path>"` on selection.
- `close-request` with active iteration: exits code 0, auto-closes iteration, prints notice per closed iteration.
- `close-request` with no active iteration: behavior unchanged.

## Non-functional expectations

- No new Python package dependencies.
- Cross-platform (Windows + POSIX).
- Idempotent: `close-request` on already-closed request still raises `ValidationError("Request already closed")`.
- Session-cached CLI detection: `gh copilot --version` called at most once per menu session.

## Measurable acceptance criteria

1. **AC-1:** Launching the menu: neither "Reverse Engineer" nor "Test Common" appears in any section.
2. **AC-2:** On a machine without `gh copilot`: no prompt action rows are navigable; a static `  • <Title>  →  gh copilot suggest "..."` list is shown below the Script actions section.
3. **AC-3:** On a machine with `gh copilot`: selecting a prompt action launches `gh copilot suggest "Execute the prompt defined in ..."` interactively; no copy/paste text appears.
4. **AC-4:** Running any script action: the terminal no longer displays `Running command:` or the raw Python command string.
5. **AC-5:** `python close-request.py --workspace .` while an iteration is Active: exits code 0, prints `"Auto-closed iteration <id> before closing request."`, then `"Closed request: R-..."`.
6. **AC-6:** `pytest .aib_brain/tools/test_common.py` passes at 100%.


# 9. Solution Options

See iteration 01 Section 9 for a full Option A / Option B comparison. Both options remain valid; the recommendation is unchanged.

## Recommendation: Option A — Targeted Direct Code Changes

- **Overview:** The smallest set of direct modifications to `menu.py` and `close-request.py` satisfying all five improvement areas. No new modules, configuration files, or abstractions.
- **Benefits:** Minimal diff, easy to review, consistent with existing patterns.
- **Trade-offs:** `EXCLUDE_SCRIPTS` requires manual maintenance for future non-tool scripts.
- **Expected effort:** Low — approximately 60–80 lines changed/added across two source files plus ~30 lines in `test_common.py` (new test class) plus documentation row updates.
- **Acceptance test ideas:** Visual inspection of menu output; integration test for `close-request` with active iteration; `pytest test_common.py` 100% pass.

DECISION: Option A accepted. Changes are targeted and isolated. No architectural changes required.


# 10. Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | AIB Command Menu component description update: CLI-gated prompt actions, excluded non-tool scripts |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | CMP-ART-0005 edge_cases: add auto-close-iteration side effect; CMP-ART-0006 edge_cases: add CLI-gating and EXCLUDE_SCRIPTS notes |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | FR-008 update: specify CLI-gated prompt action navigation and execution |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | Add TERM-0013 "Prompt Action" |


# 11. Operational & Documentation Implications

- **Runbooks:** No runbook changes required. The menu and close-request are interactive developer tools.

- **SLAs/SLOs:** Not applicable.

- **Monitoring/observability:** No structured log changes. The `close-request.py` auto-close prints a human-readable notice to stdout per auto-closed iteration; no structured event required.

- **Data quality rules:** Not applicable.

- **Product documentation artifact updates:**
  - `RQT-02` FR-008: Revise to state that the interactive menu gates prompt-action navigation on `gh copilot` CLI availability and executes `gh copilot suggest` when available.
  - `ARCH-01` Component Inventory — AIB Command Menu row: update Description to reference CLI gating and the EXCLUDE_SCRIPTS mechanism for non-tool scripts.
  - `CMP-01` CMP-ART-0005 `edge_cases_and_validation`: append `"Auto-closes active iteration before closing request; prints notice per closed iteration."`.
  - `CMP-01` CMP-ART-0006 `edge_cases_and_validation`: replace current value with `"Must surface failures clearly; prompt actions require gh copilot CLI (non-navigable + static info block when absent); non-tool scripts (reverse-engineer.py, test_common.py) excluded from discovery."`.
  - `KNW-01`: Add row `TERM-0013 | Prompt Action | A menu entry in the AIB Command Menu that maps to an .aib_brain/prompts/aib-*.md file; executable via gh copilot suggest when GitHub Copilot CLI is available; displayed as a static informational entry otherwise. | Create Analysis menu entry | AIB Maintainers | — | menu, workflow | Proposed | 1`.


# 12. Risks

- Risk R1: `gh copilot suggest` interactive behavior incompatible on some terminal or OS configuration.
  - Probability: Low
  - Impact: Medium — prompt actions would hang or produce garbled output.
  - Mitigation: Test on Windows and POSIX before merge. Confirm the subprocess call without `capture_output` passes through stdin/stdout/stderr correctly.
  - Owner (role): DEVELOPER

- Risk R2: Auto-closing an active iteration in `close-request.py` fails midway, leaving `iterations.md` in a partially written state.
  - Probability: Low
  - Impact: High — iteration state becomes inconsistent; subsequent tool runs may fail.
  - Mitigation: Use the same `write_text` atomic replacement pattern from `close-iteration.py`. Ensure `format_markdown_table` output is validated before write.
  - Owner (role): AIB Maintainers

- Risk R3: `EXCLUDE_SCRIPTS` does not auto-grow; future test or helper `.py` files in `tools/` will silently reappear in the menu.
  - Probability: Medium (as codebase grows)
  - Impact: Low — cosmetic defect (extra menu entries).
  - Mitigation: Document the convention in ARCH-01 or CMP-01 that all non-tool `.py` files in `tools/` must be listed in `EXCLUDE_SCRIPTS`. Consider allowlist approach in a future request.
  - Owner (role): AIB Maintainers

- Risk R4: CLI binary ambiguity (`copilot` vs `gh copilot`) — if the user intended a different binary than `gh copilot`, the detection and execution calls will fail silently (FileNotFoundError caught by the `except (FileNotFoundError, ...)` block in `_detect_copilot_cli()`).
  - Probability: Low (see Assumption A1)
  - Impact: Medium — prompt actions would always appear as CLI-absent (static informational mode) even when intended CLI is present.
  - Mitigation: User validates Assumption A1 and confirms `gh copilot` or alternative before implementation.
  - Owner (role): DEVELOPER

- Risk R5: Moving CLI detection from lazy to eager (before the render loop) introduces a startup delay if `gh copilot --version` takes longer than expected.
  - Probability: Low — mitigated by the 5-second timeout already in `_detect_copilot_cli()`.
  - Impact: Low — slight UX degradation on first menu load.
  - Mitigation: The cached value (`_COPILOT_CLI_AVAILABLE`) prevents repeated delays on subsequent renders. Acceptable as-is.
  - Owner (role): DEVELOPER


# 13. Open Questions & Next Actions

1. **Validate Assumption A1: `copilot` in request.md = `gh copilot`.**
   - Owner: User
   - Trigger: Before implementation begins.
   - Resolution path: User confirms whether the intended CLI binary is `gh copilot` (GitHub CLI extension) or a different binary named `copilot`. If confirmed as `gh copilot`: implementation proceeds as specified. If a different binary: update detection command and subprocess invocation accordingly.

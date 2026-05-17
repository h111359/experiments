# Request

The cli menu contains options Reverse Engineer and Test_common which should not be there. Also Prompt actions should be selectable only if github copilot cli is detected installed and chosing an option from Prompt actions should lead to real execution via the copilot cli, not just displaying the prompt for manual execution in the chat. In case no cli is detected - list in minimalistic way the invocation strings for all possible prompts, witout giving option for execution from the menu (just informative).

Check the whole menu and remove unnecessary information like showing the command to be executed. Also make the experience of the user more smooth - no unnecessary texts or confirmation.

Closing a request with active iteration shall be allowed and shall result in closing the iteration as well - change the flow 

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
2. On a machine where `copilot --version` returns non-zero or the binary is not found: no Prompt action rows have navigable indices; a static informational block is shown with each prompt's title and invocation string.
3. On a machine where `copilot --version` returns exit code 0: selecting a prompt action launches `copilot "Execute the prompt defined in <path>"` as an interactive terminal session; no copy/paste text is shown; the menu re-renders after `copilot` exits.
4. Running any script action: the terminal no longer displays `Running command:` or the raw Python command string; no `[script]` or `[prompt_file]` suffixes appear on menu lines.
5. `python close-request.py --workspace .` while an iteration is Active: exits code 0, prints `"Auto-closed iteration <id> before closing request."` for each auto-closed iteration, then `"Closed request: R-..."`.
6. `pytest .aib_brain/tools/test_common.py` passes at 100% after new test cases are added.
# Request

## Goal

Remove all GitHub Copilot CLI automation from the AIB codebase (code, menu, documentation). Rename four AIB prompt files to a shorter, vendor-neutral naming scheme and update every live reference to these files throughout the repository. Register `.aib_memory/context.md` as a permanent entry in `.aib_memory/references.md` and seed a minimal stub file during workspace initialization. Wire the `aib-context.md` prompt to execute as a final step inside the renamed `aib-documentation.md` prompt. Apply three display improvements to the CLI menu: remove the redundant "AI Builder" prefix line, add the full request title next to the request ID in the active request display, and remove both the "--- Script actions ---" and "--- Prompt actions (AI-driven) ---" section headers while keeping the script action rows.

## Background

Prior versions of AIB added a GitHub Copilot CLI integration (`copilot -p … --allow-all-tools`) to the interactive terminal menu so that prompt actions could be launched from the CLI. This introduced a vendor-specific runtime dependency contrary to AIB's core vendor-agnostic design principle (NFR-001 in RQT-02). In practice, prompts are executed via IDE-native AI interfaces (e.g., VS Code Copilot Chat, Claude Code) and the CLI path is unused. The Concepts.md vendor-agnostic principle explicitly states that tool-specific extensions must not provide unique functionality. Removing the integration aligns the product with its stated design, simplifies the menu, and eliminates dead code and tests.

## Scope

1. **Remove Copilot CLI from `menu.py`:**
   - Delete: `_COPILOT_CLI_AVAILABLE` global; `_detect_copilot_cli()`; `run_prompt_action()`; `discover_prompt_actions()`; `_PROMPT_TITLE_OVERRIDES`; `_PROMPT_DESC_OVERRIDES`; `_PROMPT_ORDER`.
   - Modify `render_menu()`: remove `cli_available` parameter; remove `print("AI Builder")` line; remove `print("--- Script actions ---")` line; remove the `if cli_available:` / `else:` prompt-action rendering blocks.
   - Modify `render_menu()` active request display: show `{active_request_id} – {active_request_title}` when a request is active, or `"No active request"` when none exists.
   - Modify `choose_action()`: remove `cli_available = _detect_copilot_cli()` call; remove CLI-dependent `total_items` logic; remove prompt action routing from `ENTER` and `DIGIT:` handlers.
   - Modify `MenuState` dataclass: add field `active_request_title: str | None`.
   - Modify `resolve_menu_state()`: extract `title` column from the active register row and populate `active_request_title`.

2. **Remove Copilot CLI tests from `tests/test_menu.py`:**
   - Delete `TestRunPromptAction` class entirely.
   - Delete `TestDetectCopilotCli` class entirely.
   - Delete `TestDiscoverPromptActions` class entirely.
   - Remove `_detect_copilot_cli`, `discover_prompt_actions`, `run_prompt_action` from the import list.

3. **Rename prompt files (in `.aib_brain/prompts/`):**
   - `aib-create-analysis.md` → `aib-analysis.md`
   - `aib-create-plan.md` → `aib-plan.md`
   - `aib-create-questionnaire.md` → `aib-questionnaire.md`
   - `aib-update-documentation.md` → `aib-documentation.md`

4. **Update all live cross-references to renamed prompt files:**
   - In `aib-analysis.md` (new name): replace `aib-create-questionnaire.md` → `aib-questionnaire.md`.
   - In `aib-documentation.md` (new name): add step "Execute `.aib_brain\prompts\aib-context.md`" before the final confirm statement.
   - In `aib-implement.md`: replace `aib-update-documentation.md` → `aib-documentation.md`.
   - In `.aib_brain/Concepts.md` lines 315–317: replace old file-name references with renamed names.
   - In `.aib_brain/Concepts.md` line 139 area: remove or replace the Copilot CLI-specific invocation example in the vendor-agnostic paragraph.

5. **Add `context.md` to `references.md`:**
   - Append one row: `ref_id=REF-0029`, `title=AIB Product Context`, `path=.aib_memory/context.md`, `type=other`, `edit_allowed=N`, `source=user`, `notes=Auto-generated context synthesis; refresh via aib-context.md prompt`.

6. **Update `initialize.py` to seed `context.md`:**
   - After the references.md seeding block, write `.aib_memory/context.md` with a minimal stub if and only if the file does not already exist. No template file required. Stub: `# Product Context\n\n> Seeded by AIB initialize. Run the context prompt (aib-context.md) to populate this file.\n`.

7. **Update product documentation (all files with `edit_allowed=Y`):**
   - ARCH-01: Rewrite the AIB Command Menu component description to remove all Copilot CLI detection sentences, informational block text, and stdin inheritance for prompt actions; describe as a pure Python script launcher.
   - CMP-01 CMP-ART-0006: Remove Copilot CLI gating text from `edge_cases_and_validation` column.
   - RQT-02 FR-008: Rewrite to describe menu providing script actions only; remove all references to Copilot CLI availability gating.
   - KNW-01 TERM-0013: Update definition to remove CLI dependency; update `examples` column from `aib-create-analysis.md` to `aib-analysis.md`; increment version.

## Out of scope

- Historical/closed request artifact files (analyses, plans, implementations) that reference old prompt names — they are immutable audit records.
- Renaming action identifier names (`create-analysis`, `create-questionnaire`, `create-plan`) in the Concepts.md action contract matrix.
- `docs/Copilot_Issue_Assignment_Rules.md` — documents issue-assignment governance, not CLI prompt integration.
- Adding a `product-documentation-convention.md` mapping row for `context.md` (deferred; not required for `type=other`).
- Modifying the `.aib_brain/conventions/context-convention.md` file.

## Constraints

- Python stdlib only; no new third-party imports.
- `edit_allowed=N` for the `context.md` row in `references.md`.
- The `context.md` seeding in `initialize.py` must be idempotent (skip if file already exists).
- All existing non-CLI tests must pass after all code changes.
- Do not modify any `.aib_brain/` conventions files beyond Concepts.md (which is a prompt/framework file, not a convention file).

## Success criteria

1. Running the CLI menu shows no prompt action section and no "--- Script actions ---" or "--- Prompt actions ---" header lines.
2. The active request line in the menu displays both ID and full title when a request is active.
3. None of the four old prompt file names exist under `.aib_brain/prompts/`.
4. All live references to old prompt file names in non-historical files are updated to new names.
5. `aib-documentation.md` contains an explicit step that invokes `aib-context.md`.
6. Running `initialize.py` on a new workspace creates `.aib_memory/context.md` with stub content; re-running does not overwrite an existing file.
7. `.aib_memory/references.md` contains a row for `.aib_memory/context.md` at REF-0029 with `type=other`, `edit_allowed=N`.
8. The full test suite (`python -m pytest tests/`) passes with all three CLI test classes removed.
9. No occurrence of `copilot` CLI invocation syntax (`copilot -p`, `copilot --version`) remains in `menu.py`, ARCH-01, CMP-01, RQT-02, or KNW-01.
10. `MenuState` carries `active_request_title` and `resolve_menu_state()` populates it from the requests register.

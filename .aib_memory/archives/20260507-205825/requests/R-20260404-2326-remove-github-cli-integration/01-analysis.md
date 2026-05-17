## Executive Summary

- **Request ID:** R-20260404-2326

- **Request Title:** Remove github cli integration

- **Iteration ID:** 01

- **High-level purpose:** This request removes all GitHub Copilot CLI automation and dependent constructs from the AIB codebase (menu logic, tests, documentation), renames four prompt files to a shorter, vendor-neutral naming scheme, registers `.aib_memory/context.md` as a permanent reference entry and seeds it during workspace initialization, wires the `aib-context.md` prompt to execute as part of the documentation update workflow, and cleans up two cosmetic display strings in the CLI menu (redundant "AI Builder" prefix, missing request title, and "--- Script actions ---" section header).

- **Earlier iterations:** None. This is the first iteration of this request.

- **Scope summary:** Six categories of change — (1) remove Copilot CLI integration from code; (2) rename four prompt files and update all their references; (3) add `context.md` to references register and seed it during `initialize`; (4) wire `aib-context.md` execution inside `aib-documentation.md` (renamed from `aib-update-documentation.md`); (5) update product documentation to reflect removed CLI capability; (6) fix CLI menu display strings.

- **Conflicting prior iterations:** None.

---

## Scope Interpretation

- **In scope — remove GitHub Copilot CLI:** Delete `_detect_copilot_cli()`, `_COPILOT_CLI_AVAILABLE`, `run_prompt_action()`, `discover_prompt_actions()`, `_PROMPT_TITLE_OVERRIDES`, `_PROMPT_DESC_OVERRIDES`, `_PROMPT_ORDER` from `menu.py`; remove `cli_available` parameter and all CLI-dependent rendering branches from `render_menu()` and `choose_action()`; remove the "--- Prompt actions (AI-driven) ---" and "--- Prompt actions (Copilot CLI not detected — informational only) ---" rendering blocks entirely; remove all associated test classes/imports from `test_menu.py`.

- **In scope — rename prompt files:** Rename `aib-create-analysis.md` → `aib-analysis.md`, `aib-create-plan.md` → `aib-plan.md`, `aib-create-questionnaire.md` → `aib-questionnaire.md`, `aib-update-documentation.md` → `aib-documentation.md` in the `.aib_brain/prompts/` directory and update every live reference to these files across the repo.

- **In scope — references.md addition:** Add a row for `.aib_memory/context.md` to `.aib_memory/references.md`; definition of `type` and `edit_allowed` is a decision point (see Section 5.6 and Section 9).

- **In scope — initialize.py seeding:** Modify `initialize.py` to write a minimal `.aib_memory/context.md` stub during workspace initialization (no template file required; inline content is sufficient).

- **In scope — execute aib-context.md from aib-documentation.md:** Add an explicit invocation step to the (renamed) `aib-documentation.md` that triggers execution of `aib-context.md` as part of the documentation update workflow.

- **In scope — menu display changes:** Remove the lone `print("AI Builder")` line from `render_menu()`; extend active request display to include the full request title alongside the ID; remove the `print("--- Script actions ---")` line but preserve the individual action rows below it.

- **In scope — product documentation updates:** ARCH-01, CMP-01, RQT-02, KNW-01 all contain Copilot CLI-specific text that must be updated; KNW-01 TERM-0013 definition and examples reference old prompt file name and CLI availability.

- **Implicit in scope — aib-implement.md cross-reference update** (implicit rule - AIB framework): `aib-implement.md` contains an explicit `Execute .aib_brain\prompts\aib-update-documentation.md` instruction; this must be updated to `aib-documentation.md` after the rename.

- **Implicit in scope — Internal cross-references inside prompt files** (implicit rule - AIB framework): `aib-analysis.md` (formerly `aib-create-analysis.md`) references `aib-create-questionnaire.md` internally; must be updated to `aib-questionnaire.md`.

- **Implicit in scope — Concepts.md file-name references** (implicit rule - AIB framework): Lines 315–317 of `.aib_brain/Concepts.md` list file paths for `aib-create-analysis.md`, `aib-create-questionnaire.md`, `aib-create-plan.md`; and line 139 contains a Copilot CLI example; both require updating.

- **Out of scope (explicit request):** No exclusions stated. The following are excluded by analysis ruling:
  - Historical/closed request artifacts (analysis, plan, implementation files) referencing old names — they are immutable audit records.
  - Action identifier names in Concepts.md (`create-analysis`, `create-questionnaire`, `create-plan`) — these are contract-level identifiers, distinct from file names; renaming is not requested.
  - `docs/Copilot_Issue_Assignment_Rules.md` — this is meta-documentation about GitHub Copilot assignment behavior, not CLI integration; out of scope unless explicitly confirmed.
  - `.aib_memory/context.md` content — only existence/registration and seeding are in scope; the content is managed by `aib-context.md` execution.

---

## Domain Knowledge Essentials

- **AI Builder (AIB):** Minimal, model-agnostic framework for specification-driven development. Provides deterministic, file-first workflows for managing requests/iterations and generating convention-governed documentation.

- **GitHub Copilot CLI (gh copilot / copilot):** A command-line interface extension to GitHub's Copilot AI service that allows invoking Copilot prompts from a terminal via `copilot -p "..."`. AIB previously used it as the runner for prompt actions in the CLI menu. This dependency is being fully removed.

- **Vendor/model agnosticism:** Core AIB principle. Both NFR-001 and Concepts.md declare that AIB must be executable across different AI tooling (VS Code Copilot, Claude Code, Cursor, etc.). Removing the Copilot CLI integration reinforces this principle by eliminating tool-specific runtime coupling.

- **Prompt file:**  A Markdown document under `.aib_brain/prompts/` named `aib-*.md`. Defines the instructions an AI agent executes to produce a specific AIB artifact (analysis, questionnaire, plan, etc.). Previously also surfaced as navigable menu items when the CLI was present.

- **Menu (AIB Command Menu):** Terminal UI provided by `menu.py`, launched via `run.bat` / `run.sh`. After this change, it will only list and execute Python tool scripts — prompt files will no longer appear in the menu.

- **Impacted roles/personas:**
  - Developer (DEVELOPER): Primary user of the CLI menu; will see a simplified menu with script actions only.
  - AI Automation Agent (AI_AGENT): Executes prompts directly in the AI chat/coding interface; unaffected by removal of CLI gating.
  - AIB Maintainer: Owns brain assets; must update conventions, docs, and tool code.

- **Business processes touched:** BP-0001 (Initialize — now seeds context.md), all analysis/plan/documentation workflows (renamed prompts), developer interaction via menu (simplified UI).

---

## Technical Knowledge & Terms

- **`menu.py`:** Python module implementing the interactive terminal menu for AIB tool scripts. Contains script-action routing, prompt-action discovery, and CLI detection logic. Located at `.aib_brain/tools/menu.py`.

- **`_detect_copilot_cli()`:** Session-cached function in `menu.py` that runs `copilot --version` via subprocess to check Copilot CLI availability. Result stored in global `_COPILOT_CLI_AVAILABLE`. To be removed entirely.

- **`run_prompt_action()`:** Function in `menu.py` that builds and executes `copilot -p "<prompt_path>" --allow-all-tools` via `subprocess.Popen`. Inherits stdin for interactive Copilot CLI sessions. To be removed entirely.

- **`discover_prompt_actions()`:** Scans `.aib_brain/prompts/` for `aib-*.md` files and returns a list of action dicts used to render prompt menu entries. Used only by menu — to be removed entirely.

- **`MenuState`:** Frozen dataclass in `menu.py` holding resolved `active_request_id`, `active_request_folder`, `active_iteration_id`. Requires a new field `active_request_title: str | None` to support the full-name display change.

- **`render_menu()`:** Renders the complete terminal menu output (banner, active state, action list). Currently accepts `cli_available: bool` parameter and conditionally renders prompt action sections. After change: parameter removed, prompt sections removed, section headers removed, and full request title included.

- **`_PROMPT_TITLE_OVERRIDES`, `_PROMPT_DESC_OVERRIDES`, `_PROMPT_ORDER`:** Module-level dicts in `menu.py` that map prompt file stems to human-readable titles and descriptions, and define ordering. Used only by `discover_prompt_actions`. To be removed.

- **`pytest` test suite (`tests/test_menu.py`):** Contains `TestDetectCopilotCli`, `TestRunPromptAction`, and `TestDiscoverPromptActions` test classes that cover the CLI-integration code. These test classes must be removed along with the functions they test. Imports of removed functions must also be cleaned up.

- **`initialize.py`:** Python tool script that seeds `.aib_memory` on first use. Must be updated to write a minimal stub for `.aib_memory/context.md`.

- **`aib-context.md` prompt:** Produces a full replacement of `.aib_memory/context.md` by synthesizing all product documentation. Must be invoked by `aib-documentation.md`.

- **`aib-documentation.md` prompt (renamed):** Will trigger `aib-context.md` execution as a final step, ensuring context.md is regenerated after any documentation update.

- **`references.md` row type for `context.md`:** Two candidates — `product-doc` (triggers convention enforcement in update-documentation workflow, requires `context-convention.md` mapping) or `other` (bypass enforcement, used for non-doc references). See Decision Points.

- **NFR-001 (vendor-agnostic):** Removing CLI tightens compliance — the menu becomes purely Python tool scripting with no AI-vendor runtime dependency.

- **Non-functional:** No security, performance, reliability, or observability implications detected. Change is purely structural/behavioral to framework code.

---

## Assumptions

- Assumption A1: The four prompt file renames apply to live prompt files only in `.aib_brain/prompts/`; historical/closed request artifact content that references old file names is intentionally preserved as an immutable audit trail.
  - Rationale: Closed requests are non-editable per lifecycle rules (request-convention.md); modifying them would break audit traceability.
  - Risk if false: If maintainer expects closed request files to be backfilled, manual remediation of dozens of historical artifact files would be required.
  - Falsification method: Explicitly ask maintainer if closed-request artifacts must also be updated.

- Assumption A2: The `discover_prompt_actions()` function and all related dictionaries (`_PROMPT_TITLE_OVERRIDES`, `_PROMPT_DESC_OVERRIDES`, `_PROMPT_ORDER`) in `menu.py` are removed entirely since they exist solely to support the CLI prompt-action flow being deleted.
  - Rationale: No other consumer of these constructs exists within `menu.py` or elsewhere in the active codebase.
  - Risk if false: If another feature or future extension relies on prompt discovery, removing it creates rework.
  - Falsification method: Search codebase for any other consumers of `discover_prompt_actions`.

- Assumption A3: `context.md` should be registered in `references.md` as `type=other` with `edit_allowed=N` rather than `type=product-doc`.
  - Rationale: `type=product-doc` triggers convention-enforcement preflight in `aib-documentation.md`, requiring a mapping row and convention file for `context.md`. While `context-convention.md` exists, adding the mapping would extend the scope of this request. `type=other` keeps it in scope as a read reference without enforcement side-effects.
  - Risk if false: If `type=product-doc` is preferred, the product-documentation-convention.md mapping and the enforcement preflight logic must be updated to handle `context.md`; this enlarges scope.
  - Falsification method: See Decision Point DP-1 below.

- Assumption A4: The action identifier names (`create-analysis`, `create-questionnaire`, `create-plan`) in Concepts.md's action contract matrix are unchanged; only the file-name references within the file-path columns are updated.
  - Rationale: Request text says "rename the prompts" (file names), not "rename the actions". Changing action identifiers would require updating the action contract matrix and potentially all tooling that references action names.
  - Risk if false: Inconsistency between file names and action names may create confusion; downstream prompts that reference the old action names by string would need updating.
  - Falsification method: Verify that no prompt or tool script performs string matching on action identifier names.

- Assumption A5: `docs/Copilot_Issue_Assignment_Rules.md` is out of scope for this request; it documents GitHub Copilot's behavior for issue assignment (governance), not the CLI integration being removed.
  - Rationale: File is in `docs/` (not `.aib_brain/` or `.aib_memory/`), is not referenced in `references.md`, and its content is unrelated to the `copilot -p` CLI invocation being removed.
  - Risk if false: If the file contains CLI-specific instructions, it would need updating.
  - Falsification method: Verify that `docs/Copilot_Issue_Assignment_Rules.md` contains no instructions related to `copilot -p` or menu prompt execution.

---

## Impact Assessment

### Affected Components / Areas

- `menu.py` — primary code change; major simplification
- `tests/test_menu.py` — major test removal (three test classes)
- `.aib_brain/prompts/aib-create-analysis.md` — file rename
- `.aib_brain/prompts/aib-create-plan.md` — file rename
- `.aib_brain/prompts/aib-create-questionnaire.md` — file rename
- `.aib_brain/prompts/aib-update-documentation.md` — file rename
- `.aib_brain/prompts/aib-analysis.md` — (new name) content update: internal cross-reference to `aib-questionnaire.md`
- `.aib_brain/prompts/aib-documentation.md` — (new name) content update: add `aib-context.md` invocation step
- `.aib_brain/prompts/aib-implement.md` — content update: reference to `aib-update-documentation.md` → `aib-documentation.md`
- `.aib_brain/Concepts.md` — minor content update: file-name references on lines 315–317, copilot CLI example on line 139
- `.aib_memory/references.md` — add context.md row
- `.aib_brain/tools/initialize.py` — add context.md stub seeding
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — documentation update
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — documentation update (CMP-ART-0006)
- `.aib_memory/docs/03 Requirements/RQT-02.md` — documentation update (FR-008)
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — documentation update (TERM-0013)

### Change Type and Dependencies

| Artifact | Change type | Dependencies / Sequencing |
|---|---|---|
| `menu.py` — remove CLI functions | Remove | Must happen before test removal (tests import functions) |
| `menu.py` — update `MenuState`+`resolve_menu_state` | Modify | Resolves `title` column from register; prerequisite for display changes |
| `menu.py` — update `render_menu` / `choose_action` | Modify | Depends on updated `MenuState` |
| `tests/test_menu.py` — remove CLI test classes | Remove | Depends on `menu.py` changes (avoid import errors) |
| `tests/test_menu.py` — update discover tests | Remove/Modify | Only if `discover_prompt_actions` is removed entirely |
| Prompt file renames (×4) | Rename | Independent; must happen before internal cross-reference updates |
| Prompt internal cross-references | Modify | Depends on rename being done first |
| `aib-implement.md` cross-reference | Modify | Depends on `aib-documentation.md` rename |
| `aib-documentation.md` — add aib-context.md step | Modify | Depends on rename; independent of code changes |
| `references.md` — add context.md row | Modify | Independent; prerequisite for `initialize.py` change |
| `initialize.py` — seed context.md | Modify | Depends on `references.md` row decision |
| Product doc updates (ARCH-01, CMP-01, RQT-02, KNW-01) | Modify | Independent; can proceed in parallel with code changes |

### Domain Impacts

- DOMAIN (ARCH): Impact detected.
  - Relevant IDs: ARCH-01
  - AIB Command Menu component description references copilot CLI detection, static informational block, and stdin inheritance for prompt actions — all must be removed or reworded to describe a pure script launcher.

- DOMAIN (CMP): Impact detected.
  - Relevant IDs: CMP-01 (CMP-ART-0006)
  - AIB command menu edge case description mentions copilot CLI gating, static informational block — must be updated.

- DOMAIN (RQT): Impact detected.
  - Relevant IDs: RQT-02 FR-008
  - FR-008 currently specifies: "prompt actions require copilot CLI availability and display as informational only when CLI is absent" — must be rewritten to describe menu without prompt actions.

- DOMAIN (KNW): Impact detected.
  - Relevant IDs: KNW-01 (TERM-0013), KNW-02
  - TERM-0013 "Prompt Action" definition references copilot CLI and old prompt file name `aib-create-analysis.md`; must be updated to reflect that prompt actions are no longer menu-executable.
  - KNW-02 business process catalog: no direct CLI references found; no change needed.

- DOMAIN (OBS): No impact detected.
  - Log files now only cover script actions (not prompt executions); OBS-01 policy still satisfied.

- DOMAIN (DATA): No impact detected.

- DOMAIN (SEC): No impact detected.
  - CLI subprocess invocation (`copilot --allow-all-tools`) is removed; removes an implicit external process execution surface. Marginally positive security posture.

- DOMAIN (OPR): No impact detected.

### Constraints

- Must not modify closed request artifacts (lifecycle rule: closed requests are immutable).
- Must not modify `.aib_brain/` non-prompt/non-tools files beyond the specific ones listed (Concepts.md update only for identified references).
- Python stdlib only; no new dependencies may be introduced.
- Changes to `menu.py` must preserve backward compatibility with `MenuState` usage in tests not related to CLI removal.
- Test suite must remain 100% passing after all changes.

### Required Documentation Updates

- ARCH-01 — High-level Architecture
  - Required update? YES
  - Reason: AIB Command Menu component description mentions copilot CLI detection, informational block rendering, and stdin inheritance for prompt actions.

- CMP-01 — Notebook/Script Catalog
  - Required update? YES
  - Reason: CMP-ART-0006 edge_cases_and_validation column contains copilot CLI gating text.

- RQT-02 — Requirements document
  - Required update? YES
  - Reason: FR-008 specifies copilot CLI availability as a gate for prompt actions.

- KNW-01 — Domain glossary
  - Required update? YES
  - Reason: TERM-0013 "Prompt Action" definition and examples column reference copilot CLI and old file name `aib-create-analysis.md`.

- ARCH-04 — ADR
  - Required update? NO (no new architectural decision is strictly needed; the request is a cleanup/removal, not a new architectural direction. An ADR may optionally document the decision to remove CLI integration, but is not mandated.)

### Decision Points

**DP-1: `type` value for `context.md` row in `references.md`**

- Option A: `type=product-doc`, `edit_allowed=N`
  - Benefits: Included in required-read set for analysis/plan prompts, enriching agent context.
  - Trade-offs: Triggers convention-enforcement preflight in `aib-documentation.md`; requires adding a mapping row to `product-documentation-convention.md` and a `context-convention.md` stub in the convention mapping. Enlarges scope.
  - Risk: Convention mapping update could break the fail-closed enforcement if not done correctly.
  - Recommended: NO for this request (defer to a follow-up request if desired).

- Option B (Recommended): `type=other`, `edit_allowed=N`
  - Benefits: Registers context.md as a known workspace artifact without triggering enforcement; clean and minimal.
  - Trade-offs: Prompts will not auto-include context.md in their required-read set; agents must explicitly read it.
  - Risk: Low. Context.md is already read by `aib-context.md` prompt directly; its value as a ref entry is primarily for discoverability and governance.
  - Recommended: YES.

---

## Research Plan and Findings

**Methodology:** Internal workspace file scan. Targeted reads of all active (non-historical) source files.

**Evidence summary:**

- `.aib_brain/tools/menu.py`: Confirmed full copilot CLI integration surface — three major functions, three dicts, one global var, one parameter to `render_menu`, and CLI-conditional routing in `choose_action`. The "AI Builder" prefix appears on line `print("AI Builder")` directly before the active request display. The "--- Script actions ---" title appears in `render_menu` before the script actions loop.

- `tests/test_menu.py`: Confirmed `TestDetectCopilotCli` (5 tests), `TestRunPromptAction` (7 tests), and `TestDiscoverPromptActions` (5 tests) are CLI-dependent test classes. Import list on lines 17–27 includes `_detect_copilot_cli`, `discover_prompt_actions`, `run_prompt_action`.

- `.aib_brain/prompts/`: Confirmed all four target files exist with current names. `aib-create-analysis.md` contains explicit reference to `aib-create-questionnaire.md` (line: "Execute `.aib_brain\prompts\aib-create-questionnaire.md` only when this condition is true"). `aib-implement.md` contains explicit reference to `aib-update-documentation.md` (line: "Execute `.aib_brain\prompts\aib-update-documentation.md`").

- `.aib_brain/Concepts.md` lines 315–317: Confirmed hard-coded references to `aib-create-analysis.md`, `aib-create-questionnaire.md`, `aib-create-plan.md`. Line 139: Copilot CLI used as an explicit example in the vendor-agnostic paragraph; should be updated to use a generic example.

- `.aib_memory/references.md`: Confirmed context.md is NOT currently registered. Only `.aib_brain\Concepts.md` as `type=domain` with `edit_allowed=N`.

- `.aib_memory/docs/`: Confirmed ARCH-01, CMP-01, RQT-02, and KNW-01 contain Copilot CLI references that need updating. ARCH-04 requires no update.

- `initialize.py`: Confirmed context.md is not currently seeded. Code seeds `requests_register.md` and `references.md` from templates; context.md seeding must be added as an inline write (no template).

- `run.bat`, `run.sh`: No copilot CLI references; no changes needed.

- `README.md`: No copilot CLI integration references; no changes needed.

- `docs/Copilot_Issue_Assignment_Rules.md`: Text infers governance doc for issue assignment (confirmed from `logs/versions_log.md` entry). Not related to CLI prompt execution. Out of scope.

**Gaps/unknowns:**
  - None material; all question gaps are resolved by analysis (see decision points above).

**Files Read:**

- `.aib_brain/prompts/aib-create-analysis.md` — confirmed it references `aib-create-questionnaire.md` internally; auto-trigger instruction confirmed
- `.aib_brain/prompts/aib-create-plan.md` — confirmed rename only needed; no internal cross-references to update
- `.aib_brain/prompts/aib-create-questionnaire.md` — confirmed rename only needed
- `.aib_brain/prompts/aib-update-documentation.md` — confirmed structure; identified where `aib-context.md` invocation step must be added (before confirm statement)
- `.aib_brain/prompts/aib-implement.md` — confirmed reference to `aib-update-documentation.md`; must be updated
- `.aib_brain/prompts/aib-context.md` — confirmed purpose and structure; no internal references to renamed files
- `.aib_brain/tools/menu.py` — full read; all CLI-related code catalogued
- `.aib_brain/tools/initialize.py` — confirmed seeding logic; no context.md seeding present
- `.aib_brain/Concepts.md` — confirmed lines 315–317 and line 139 content
- `.aib_memory/references.md` — confirmed 27 rows, no context.md row
- `.aib_memory/requests_register.md` — active request and iteration resolved
- `.aib_memory/requests/R-20260404-2326-remove-github-cli-integration/request.md` — primary input
- `.aib_memory/requests/R-20260404-2326-remove-github-cli-integration/iterations.md` — confirmed iteration 01 Active
- `.aib_brain/conventions/analysis-convention.md` — full read; convention applied to this document
- `.aib_brain/conventions/request-convention.md` — full read; applied to rewrite section
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — confirmed CLI references in AIB Command Menu row
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — confirmed CLI references in CMP-ART-0006
- `.aib_memory/docs/03 Requirements/RQT-02.md` — confirmed FR-008 CLI references
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — confirmed TERM-0013 CLI reference
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — confirmed no CLI references
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — confirmed no CLI references
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — confirmed no change needed
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — stub; no relevant content
- `tests/test_menu.py` — confirmed three CLI-dependent test classes and affected imports
- `.aib_brain/run.bat` — confirmed no CLI references
- `.aib_brain/run.sh` — confirmed no CLI references
- `README.md` — confirmed no CLI references
- `.aib_memory/context.md` — read; auto-generated synthesis; not in references.md currently
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` through `DATA-09.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` through `SEC-04.md` — [SKIPPED — domain out of scope]

---

## Rewrite Proposal of the Request

*(Required per analysis convention §4.8 and §7. This is the actionable version of the request for implementation.)*

---

### Goal

Remove all GitHub Copilot CLI automation from the AIB codebase. Rename four AIB prompt files to a shorter, consistent naming scheme and update every active reference to these files. Register `.aib_memory/context.md` as a permanent entry in references.md and seed a minimal stub during workspace initialization. Wire `aib-context.md` execution inside the renamed `aib-documentation.md` prompt. Apply cosmetic display improvements to the CLI menu (remove redundant "AI Builder" prefix, add full request title to active request line, remove "--- Script actions ---" and "--- Prompt actions ---" section headers). Update all affected product documentation.

### Background

Prior iterations of AIB added GitHub Copilot CLI integration to the interactive menu so that prompt actions could be launched directly from the terminal. This created a vendor-specific runtime dependency inconsistent with AIB's core vendor-agnostic principle (NFR-001). The CLI integration is unused in practice since prompts are executed via IDE-native AI interfaces (e.g., VS Code Copilot Chat). Removing it simplifies the menu, removes dead code, and aligns the product with its stated agnostic design.

### Scope

1. **Remove Copilot CLI from `menu.py`:**
   - Delete: `_COPILOT_CLI_AVAILABLE` global; `_detect_copilot_cli()`; `run_prompt_action()`; `discover_prompt_actions()`; `_PROMPT_TITLE_OVERRIDES`; `_PROMPT_DESC_OVERRIDES`; `_PROMPT_ORDER`.
   - Modify `render_menu(signature, body)`: remove `cli_available` parameter, remove `print("AI Builder")` line, remove `print("--- Script actions ---")` line, remove the `if cli_available:` / `else:` prompt-action rendering blocks. Change active request display from `req_text = state.active_request_id or "No active request"` to `req_text = f"{state.active_request_id} – {state.active_request_title}" if state.active_request_id else "No active request"`.
   - Modify `choose_action()`: remove `cli_available = _detect_copilot_cli()` call; remove `if cli_available:` block from `total_items` calculation; remove prompt action routing from the `ENTER` and `DIGIT:` handlers.
   - Modify `MenuState` dataclass: add field `active_request_title: str | None = None`.
   - Modify `resolve_menu_state()`: extract `title` column from the active register row and populate `active_request_title`.

2. **Remove Copilot CLI tests from `tests/test_menu.py`:**
   - Delete `TestRunPromptAction` class entirely.
   - Delete `TestDetectCopilotCli` class entirely.
   - Delete `TestDiscoverPromptActions` class entirely.
   - Remove `_detect_copilot_cli`, `discover_prompt_actions`, `run_prompt_action` from the import list.

3. **Rename prompt files:**
   - `aib-create-analysis.md` → `aib-analysis.md`
   - `aib-create-plan.md` → `aib-plan.md`
   - `aib-create-questionnaire.md` → `aib-questionnaire.md`
   - `aib-update-documentation.md` → `aib-documentation.md`

4. **Update internal prompt cross-references and Concepts.md file-name references:**
   - In `aib-analysis.md`: replace `aib-create-questionnaire.md` → `aib-questionnaire.md`.
   - In `aib-documentation.md`: add step "Execute `.aib_brain\prompts\aib-context.md`" before the final confirm statement.
   - In `aib-implement.md`: replace `aib-update-documentation.md` → `aib-documentation.md`.
   - In `.aib_brain/Concepts.md` lines 315–317: replace all three old file-name references with new names.
   - In `.aib_brain/Concepts.md` line 139: remove the phrase "GitHub copilot CLI" from the vendor-agnostic paragraph or replace with a generic example.

5. **Add `context.md` to `references.md`:**
   - Append one row: `ref_id=REF-0029`, `title=AIB Product Context`, `path=.aib_memory/context.md`, `type=other`, `edit_allowed=N`, `source=user`, `notes=Auto-generated context synthesis; refresh via aib-context.md prompt`.

6. **Update `initialize.py` to seed `context.md`:**
   - After the existing `references.md` seeding block, add an unconditional write of `.aib_memory/context.md` with minimal stub content if the file does not exist. No template file required. Stub content: `# Product Context\n\n> Seeded by AIB initialize. Run the context prompt (aib-context.md) to populate this file.\n`.

7. **Update product documentation:**
   - ARCH-01: Rewrite AIB Command Menu description to remove copilot CLI detection sentences and informational block rendering; describe it as a pure script launcher.
   - CMP-01 CMP-ART-0006: Remove copilot CLI gating text from `edge_cases_and_validation` and `source_assets` columns.
   - RQT-02 FR-008: Rewrite to describe menu with script actions only; remove "copilot CLI availability" gate language.
   - KNW-01 TERM-0013: Update definition to remove CLI dependency; update `examples` column to `aib-analysis.md`; increment version.

### Out of scope

- Historical/closed request artifacts referencing old prompt file names.
- Renaming action identifiers (`create-analysis`, `create-questionnaire`, etc.) in Concepts.md action contract.
- `docs/Copilot_Issue_Assignment_Rules.md`.
- Adding `context.md` row to `product-documentation-convention.md` (deferred; not needed for `type=other`).

### Constraints

- Python stdlib only; no new imports.
- All existing tests must pass after changes.
- `edit_allowed=N` for context.md row in references.md.
- Stub must not be overwritten if `context.md` already exists (consistent with how `requests_register.md` seeding works).

### Success Criteria

1. Running the CLI menu (`run.bat` / `run.sh`) shows no prompt action section and no "--- Script actions ---" or "--- Prompt actions ---" header lines.
2. Active request line in the menu shows both ID and full title (e.g., `R-20260404-2326 – Remove github cli integration`).
3. None of the four renamed prompt files appear under their old names in `.aib_brain/prompts/`.
4. All references to old prompt names in live (non-historical) files are updated.
5. `aib-documentation.md` contains an explicit step invoking `aib-context.md`.
6. `initialize.py` creates `.aib_memory/context.md` as a stub when initializing a new workspace.
7. `.aib_memory/references.md` contains a row for `context.md`.
8. Test suite passes with all three CLI-related test classes removed.
9. No `copilot` CLI references remain in ARCH-01, CMP-01, RQT-02, or KNW-01.
10. `menu.py` imports `subprocess` only for `_run_and_tee` (script execution); no `copilot` process invocations remain.

---

## Solution Options

### Option A — Full removal with complete test and doc cleanup (Recommended)

**Overview:** Remove all Copilot CLI code from `menu.py`, remove all three CLI-dependent test classes from `test_menu.py`, rename all four prompt files, update all live references, add context.md to references.md and initialize.py, update four product docs, and apply all menu display improvements. This is the complete execution of the request.

**Benefits:**
- Achieves full vendor neutrality; eliminates dead code and dead tests.
- Menu is simpler and easier to maintain.
- Test suite coverage stays meaningful (tests only cover behavior that still exists).
- Documentation accurately reflects the new system state.

**Trade-offs:**
- Larger diff; touches 14+ files across code, prompts, docs.
- Removing test classes permanently loses coverage of the removed code (acceptable because the code is removed).

**Constraints:** Python stdlib only; all existing non-CLI tests must pass.

**Risks:** Merge conflicts in menu.py if parallel work exists; manageable via isolation.

**Expected effort:** Medium (~2–4 hours of implementation + validation).

**Acceptance test ideas:**
- `python -m pytest tests/` — all tests pass.
- Manual: run `run.bat`, verify menu shows only script actions without section headers; verify active request line includes title.
- File check: none of the four old file names exist in `.aib_brain/prompts/`.
- Content check: `grep -r "copilot" .aib_brain/tools/menu.py` returns no results.
- References check: `.aib_memory/references.md` contains REF-0029 with path `.aib_memory/context.md`.

### Option B — Phased removal (Not recommended)

**Overview:** Remove CLI code from `menu.py` in one phase; rename prompts and update docs in a second iteration.

**Benefits:** Smaller individual diffs; easier to review per change.

**Trade-offs:** Requires opening a second active request; delays completion; removes no naming inconsistency during the first phase. Not warranted for a change of this size.

**Risks:** Incomplete state between phases breaks the rename consistency goal.

**Recommendation:** Option A. All changes are tightly related and manageable in a single iteration.

---

## Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | AIB Command Menu description contains Copilot CLI references to remove |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | CMP-ART-0006 edge case column contains Copilot CLI gating text |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | FR-008 specifies Copilot CLI as gate for prompt actions |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | TERM-0013 (Prompt Action) references CLI and old prompt file name |

---

## Operational & Documentation Implications

- **Product documentation artifacts:** ARCH-01, CMP-01, RQT-02, KNW-01 require updates as listed above. The synthesis file `context.md` must be regenerated after doc updates via `aib-context.md`.

- **Menu runtime behavior:** The menu will launch faster (no startup subprocess check for `copilot --version`) and display simpler, header-free action lists.

- **Workflow change for developers:** Prompt actions (`aib-analysis.md`, `aib-documentation.md`, etc.) are executed directly via the IDE AI interface (VS Code Copilot Chat, Claude, etc.) rather than through the terminal menu. This is already the actual practice; the menu just removes the previously unused CLI path.

- **Test suite:** Net reduction in test count (~17 test methods removed from three classes). Remaining tests cover script actions, menu state resolution, streaming, logging — all still valid.

- **`initialize` output:** A new workspace will now also contain a `context.md` stub file. No negative side effects.

- **Logging:** Per-action log files remain for script actions. Prompt execution logs (previously written when using `run_prompt_action`) will no longer be generated from the menu (prompts are now only run in the AI IDE interface).

---

## Risks

- Risk R1: Test assertions that reference prompt-related items (e.g., `TestDiscoverPromptActions.test_respects_prompt_order` checking titles "Create Analysis", "Create Plan") will cause import errors if menu functions are removed but test file imports are not cleaned up first.
  - Probability: High (known from code inspection)
  - Impact: High (test suite fails to import)
  - Mitigation: Remove import statements and test classes atomically in the same change; run `pytest --collect-only` before submitting.
  - Owner (role): AIB Maintainer

- Risk R2: Active test `TestFilterVisibleActions._make_actions` accesses `from menu import build_script_actions, TOOLS_DIR` with `# type: ignore[attr-defined]` annotation — implying `TOOLS_DIR` might be expected to exist as a module-level constant. If this constant was incidentally removed during cleanup, the test will fail at import time.
  - Probability: Low (only one test line uses it with a type-ignore; `TOOLS_DIR` does not appear as a module-level constant in current menu.py source)
  - Impact: Medium (one test class fails to run)
  - Mitigation: Verify `TOOLS_DIR` usage in test file before making changes; update the test helper to use an inline Path() expression if needed.
  - Owner (role): AIB Maintainer

- Risk R3: Renaming `aib-update-documentation.md` to `aib-documentation.md` while simultaneously adding a step to it creates a compounded change. If the rename is done first and the reference update in `aib-implement.md` is delayed, executing the implement prompt in between will reference a non-existent file.
  - Probability: Low (single-developer workspace; changes applied atomically)
  - Impact: Medium (implement prompt fails until fully patched)
  - Mitigation: Apply all rename + internal reference updates in one implementation pass; do not leave the workspace in a half-renamed state.
  - Owner (role): AIB Maintainer

- Risk R4: Adding a `context.md` seeding step to `initialize.py` but omitting the `if file exists: skip` guard could silently overwrite an existing, populated `context.md` when `initialize` is run in a pre-existing workspace.
  - Probability: Medium (consistent with how other files are seeded; easy to forget guard)
  - Impact: High (data loss of the synthesized context)
  - Mitigation: Explicitly add an existence check before writing the stub, matching the pattern used for `requests_register.md`.
  - Owner (role): AIB Maintainer

- Risk R5: If Concepts.md line 139 retains a partial Copilot CLI reference after editing, the vendor-agnostic principle paragraph becomes inconsistent. Incomplete edits to prose paragraphs are easy to miss.
  - Probability: Low
  - Impact: Low (cosmetic inconsistency, not a functional defect)
  - Mitigation: After editing, search Concepts.md for remaining occurrences of "copilot CLI" (case-insensitive).
  - Owner (role): AIB Maintainer

---

## Disambiguation Questionnaire

**Q1 — What `type` should `context.md` use in `references.md`?**
- Chosen Answer / Value: `type=other`, `edit_allowed=N`
- Rationale: Avoids triggering convention-enforcement preflight in update-documentation workflow; keeps scope small; context.md is a synthesized artifact, not a primary product doc.
- Evidence / Reference: `.aib_brain/prompts/aib-update-documentation.md` (convention enforcement block); `.aib_memory/references.md` type validation rule.
- Impact if changed: Would require adding a convention mapping row in `product-documentation-convention.md` and a context.md entry in the mapping; enlarges scope.

**Q2 — Should action identifiers (`create-analysis`, etc.) in Concepts.md be renamed?**
- Chosen Answer / Value: No; action identifiers are contract-level names independent of file names.
- Rationale: The request states "rename the prompts" (file names), not "rename the actions". Changing action names in the contract matrix risks breaking any downstream tooling or agent instructions that reference them by string.
- Evidence / Reference: `.aib_brain/Concepts.md` action contract matrix; request.md goal section.
- Impact if changed: Would require updating the action contract matrix, the action descriptions in Concepts.md, and potentially searching for any hard-coded action name references in tool scripts/prompts.

**Q3 — Should closed/historical request artifacts be updated to reference new prompt names?**
- Chosen Answer / Value: No; historical artifacts are immutable audit records.
- Rationale: `request-convention.md` specifies that closed requests become read-only. Backfilling historical analyses/plans with new file names would be purely cosmetic and violates the immutability principle.
- Evidence / Reference: `.aib_brain/conventions/request-convention.md` Lifecycle & Editing Rules section ("after closure: request.md becomes read-only").
- Impact if changed: Would require editing dozens of closed iteration artifact files with no functional benefit.

**Q4 — Should `docs/Copilot_Issue_Assignment_Rules.md` be modified?**
- Chosen Answer / Value: No.
- Rationale: The file documents GitHub Copilot's issue-assignment governance behavior (per `logs/versions_log.md` entry that added it), not CLI integration.
- Evidence / Reference: `logs/versions_log.md` line: "Added file `docs\Copilot_Issue_Assignment_Rules.md` with the expected behavior of GitHub copilot when working on an Issue."
- Impact if changed: Not applicable; no CLI-specific content expected.

---

## Open Questions & Next Actions

1. **[Owner: AIB Maintainer] DP-1 Confirmation** — Confirm `type=other` for `context.md` row in `references.md`. If `type=product-doc` is preferred instead, create a follow-up request to add the product-documentation-convention mapping and context.md convention file. Trigger: before implementation of item 5 (references.md update). Resolution path: User accepts Option B (type=other) by default; no blocking.

2. **[Owner: AI Agent] Validate A5 assumption** — Verify that `docs/Copilot_Issue_Assignment_Rules.md` contains no `copilot -p` CLI invocation instructions before finalizing scope. Resolution path: read and confirm during implementation preflight; no user input needed.

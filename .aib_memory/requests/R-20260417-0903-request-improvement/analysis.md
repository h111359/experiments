## Executive Summary

- **Request ID:** R-20260417-0903

- **Request Title:** request improvement

- **High-level purpose:** Introduce seven coordinated improvements to the AIB v1.1.2 framework: (1) establish `.aib_memory/input.md` as the ephemeral primary user-agent communication channel with two behavioral toggles (no-changes mode producing a timestamped `answer.md`; no-analysis mode skipping `analysis.md` generation); (2) automate request creation from `aib-analysis.md` when no active request exists, and automate request closing from `aib-implement.md` after successful implementation; (3) make `request.md` AI-generated from `input.md` content and `implementation.md` generated on-demand, eliminating all template pre-seeding from `create-request.py`; (4) reshape the CLI menu to display copy-paste-ready prompt invocations only, removing lifecycle commands and the exit option; (5) restructure conventions — move code/asset scan and internal review to `request.md`, add multi-perspective stakeholder review, and promote external benchmarking and spikes to mandatory standalone sections in `analysis.md`; (6) bump product version to v1.2.0; (7) extend `release_bookkeeping.py` to archive `.aib_brain/` as a versioned zip in `versions/` per version bump.

- **Version target:** v1.2.0 from current v1.1.2. MINOR version step is justified because template seeding removal and menu lifecycle command removal constitute breaking workflow changes for existing users.

- **Impacted files (summary):** `initialize.py`, `create-request.py`, `menu.py`, `aib-analysis.md`, `aib-implement.md`, `analysis-convention.md`, `request-convention.md`, `release_bookkeeping.py`, `README.md`, `tests/test_initialize.py`, `tests/test_create_request.py`, `tests/test_menu.py`. Version marker: `.aib_brain/v1.1.2` → `.aib_brain/v1.2.0`.

- **All three Q&D questions answered in this run:** Q001 (archive naming), Q002 (separate sections for internal review vs. stakeholder review), Q003 (zip files committed to VCS). All three are applied as embedded instructions to the relevant mandatory sections of `request.md` and removed from `## Questions & Decisions`.

- **Context.md version discrepancy identified:** `context.md` states "Current version: v1.0.14" but the active SemVer marker in `.aib_brain/` is `v1.1.2`. Context.md has not been regenerated to reflect versions released since v1.0.14. Task 12 must regenerate context.md and correct the version to v1.2.0.

- **Non-standard `## Purpose` section** detected at the end of `request.md` after `## Questions & Decisions`. Content is the user-authored design specification for `input.md` template. Not a convention-defined section; left in place as informational context.

- **`request.md` sections updated in this run:** `## Scope` (Q001 archive path applied), `## Constraints` (Q003 VCS constraint added), `## Assumptions` (fully replaced, deferred-decision notes from Q001/Q003 removed), `## Plan` (fully replaced, archive naming and separate-sections clarifications incorporated), `## Testing` (fully replaced), `## Documentation` (fully replaced), `## Questions & Decisions` (all answered questions removed; section omitted as empty).

***

## Domain Knowledge Essentials

**Business terminology:**

- **AIB Framework (AI Builder):** A minimal, model-agnostic, file-based framework for specification-driven AI development. All workflow state is persisted as Markdown files; no cloud infrastructure is provisioned. Structured as two lifecycle-separated folders: `.aib_brain/` (replaceable framework assets) and `.aib_memory/` (persistent workspace artifacts).

- **Request:** A bounded unit of work governed by a lifecycle (Active → Closed). Exactly one request may be Active at a time. Encapsulated in a `request.md` file inside a dedicated folder under `.aib_memory/requests/`. Registered in `requests_register.md`.

- **Ephemeral input channel:** A fixed-path file (`.aib_memory/input.md`) that holds the user's current intent message. Processed once by `aib-analysis.md`, then archived with a timestamp and reset to a seed template. The file is write-once-per-cycle; its state between cycles carries no meaning.

- **Seed template:** Pre-defined skeleton content written to `input.md` on initialization or post-processing reset. Provides a structured starting point with three sections: `## Active request`, `## Options` (two behavioral toggle checkboxes), and `## Input`.

- **Behavioral toggle / checklist option:** A Markdown checkbox (` - [ ] `) in `input.md`'s `## Options` section that the AI agent reads to select a behavioral mode:
  - No-changes mode: agent provides a timestamped `answer.md` in the request folder without modifying `request.md`.
  - No-analysis mode: agent skips `analysis.md` generation entirely.

- **Input archive:** A timestamped copy of `input.md` content stored in a per-request subfolder (`inputs/`) for audit. Filename format: `input-archive-<YYYY-MM-DD_HH-MI-SS>.md`. Multiple archives accumulate when analysis is run multiple times with no active request. Automation agents MUST NOT read these files after creation.

- **Versioned archive:** A zip file capturing the complete `.aib_brain/` state at a given version, stored at `versions/aib_brain_vX.Y.Z.zip`. Committed to VCS to enable direct download from GitHub without additional release infrastructure.

- **Version bump:** Rotation of the SemVer marker file in `.aib_brain/`. MINOR increment (Y in X.Y.Z) signifies new features or backward-incompatible workflow changes.

**Impacted roles/personas:**

- **Developer** — creates intent in `input.md`, reviews AI-generated `request.md`, runs the CLI menu for non-lifecycle tool scripts.

- **AI Automation Agent** — executes `aib-analysis.md`, `aib-implement.md`, and `aib-context.md`; reads `input.md` as the authoritative intent source for the current cycle.

- **AIB Maintainer** — owns `.aib_brain/` assets; performs framework upgrades; does not interact with `.aib_memory/`.

**Business processes touched:**

- **Workspace initialization** — now seeds `input.md` with the structured template in addition to existing artifacts.

- **Request creation** — shifts from explicit CLI lifecycle command to AI-driven interpretation of `input.md` content. "Create request" and "Close request" menu items are removed.

- **Analysis workflow** — gains a "no active request" execution branch; gains two new behavioral toggles; gains timestamped input archiving.

- **Implementation workflow** — generates `implementation.md` on-demand from scratch; auto-closes the request upon completion via `close-request.py`.

- **CLI menu interaction** — lifecycle commands removed; copy-paste-ready prompt invocations added; exit option removed.

- **Release bookkeeping** — extended with a zip step producing `versions/aib_brain_vX.Y.Z.zip`.

**Acceptance impact:** The entire request creation lifecycle shifts from explicit CLI invocation to AI-driven interpretation of `input.md`. Existing users must stop using "Create request" and "Close request" from the menu; they interact exclusively via `input.md` and AI prompts. This is a breaking workflow change justifying MINOR version increment.

***

## Technical Knowledge & Terms

**Technologies and components:**

- **Python 3.10+ standard library:** The only permitted runtime for tool scripts; no third-party packages. Key modules for this request: `zipfile` (archive creation), `pathlib`, `datetime`, `subprocess`.

- **`initialize.py`:** Seeds `.aib_memory/` on first run. Currently creates `requests_register.md`, `references.md`, and a stub `context.md`. Does NOT create `input.md` today — this gap is filled by Task 1.

- **`create-request.py`:** Currently creates request folder, register row, `request.md` (from template via `load_template()`), and `implementation.md` (hardcoded stub via `write_text()`). After Task 2: creates folder and register row only; no artifact seeding. Imports `load_template` and `validate_request_md` from `common.py` — both become unused and must be removed from the import block.

- **`menu.py`:** Interactive CLI launcher. Has hardcoded `SCRIPT_CREATE_REQUEST` and `SCRIPT_CLOSE_REQUEST` constants. `build_script_actions()` prepends them as entries 1 and 2. `discover_tool_scripts()` handles dynamic discovery of non-excluded scripts. An exit/quit option exists in the main interactive loop. After Task 5: lifecycle scripts removed from hardcoded list and added to `EXCLUDE_SCRIPTS`; exit option removed; `print_prompt_reference()` function added.

- **`aib-analysis.md` (this prompt):** Currently fails if no Active request. After Task 3: adds "no active request" branch reading `input.md`; adds no-changes and no-analysis toggle processing; archives `input.md` with timestamp to `inputs/` subfolder; resets `input.md` to seed template.

- **`aib-implement.md`:** Currently requires pre-existing `implementation.md` and fails if no active request. After Task 4: generates `implementation.md` from scratch; auto-invokes `close-request.py` after confirmed successful completion; triggers `aib-analysis.md` flow if no active request.

- **`release_bookkeeping.py`:** Currently handles SemVer marker rotation (delete old, create new) and version log creation. After Task 9: adds `zipfile.ZipFile` step to create `versions/aib_brain_vX.Y.Z.zip`; idempotent (skips if zip already exists).

- **`analysis-convention.md`:** Currently lists Research Results as containing 5 sub-items (internal review, code scan, pattern scan, external benchmarking, spikes). After Task 6: removes internal review and code scan from analysis (moved to `request.md`); promotes external benchmarking and spikes to mandatory standalone sections (sections 5 and 6).

- **`request-convention.md`:** Currently defines 12 sections; section 12 is `## Amends`. After Task 7: adds three new AI-generated sections — Code and Asset Scan, Internal Review of Request and Product Docs (separate section, Q002 answer), and Multi-Perspective Stakeholder Review (separate section, Q002 answer); removes `## Amends` (replaced by `input.md`); makes all sections mandatory; renumbers.

**Data models and constraints:**

- `input.md` schema: fixed sections `## Active request` (status line), `## Options` (two checkboxes), `## Input` (free text). Path: `.aib_memory/input.md`. Reset to seed template after each processing cycle.

- Input archive schema: `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`. Multiple archives per request are possible. Agents MUST NOT read these files.

- `versions/` location: `<workspace-root>/versions/`. Folder already exists in the workspace. Zip naming: `aib_brain_vX.Y.Z.zip`. Committed to VCS.

- Current SemVer marker: `.aib_brain/v1.1.2`. Target: `.aib_brain/v1.2.0`.

**Non-functional attributes:**

- **Model-agnosticism:** All changes must be valid Markdown and Python; no model-specific constructs or API calls.

- **Standard library only:** No `pip install` steps; `zipfile`, `pathlib`, `datetime` modules are sufficient.

- **Idempotency:** Analysis re-runs fully replace AI-generated sections; `release_bookkeeping.py` skips if target zip already exists.

- **Fail-closed:** Halt gates in `aib-analysis.md` and `aib-implement.md` must not be weakened; both must still stop on zero or multiple Active requests.

- **VCS cleanliness:** `versions/*.zip` files are committed to VCS intentionally (Q003 answer). `.gitignore` must not exclude them.

**Key terms and acronyms defined:**

- **SemVer:** Semantic Versioning — version scheme X.Y.Z where X = major, Y = minor (new features or backward-incompatible changes), Z = patch (backward-compatible bug fixes).

- **EXCLUDE_SCRIPTS:** A constant `set[str]` in `menu.py` listing script filenames to hide from the interactive menu, preventing auto-discovery.

- **Popen tee pattern:** Subprocess spawned via `subprocess.Popen` with two background threads streaming stdout and stderr simultaneously to the terminal and a log file.

- **Fail-closed:** Behavior where a component refuses to produce any output on a validation failure rather than continuing with a partial result.

- **Ephemeral:** Describes a file with a fixed path that is fully replaced on each processing cycle; its inter-cycle state is not meaningful.

- **WBS:** Work Breakdown Structure — a hierarchical decomposition of a request into discrete, independently verifiable tasks.

- **Copy-paste prompt invocation:** A CLI-displayable string the user copies and pastes into an AI coding interface to invoke an AIB prompt.

**Files read for this analysis:**

- `.aib_memory/requests/R-20260417-0903-request-improvement/request.md` — active request definition

- `.aib_memory/references.md` — reference registry

- `.aib_memory/context.md` (REF-0001) — product context

- `.aib_brain/Concepts.md` (REF-0002) — domain concepts

- `.aib_brain/conventions/analysis-convention.md` — convention for this document

- `.aib_brain/conventions/request-convention.md` — convention for `request.md`

- `.aib_brain/tools/menu.py` — current menu implementation

- `.aib_brain/tools/create-request.py` — current create-request implementation

- `.aib_brain/tools/initialize.py` — current initialize implementation

- `.aib_brain/prompts/aib-implement.md` — current implement prompt

- `scripts/release_bookkeeping.py` — current release bookkeeping script

***

## Research Results

### 1. Internal-first review of `request.md` and relevant docs

**Review findings:**

- The request is mature: all six mandatory sections are non-empty; 12 tasks are fully defined in `## Plan`; 13 test cases in `## Testing`; 2 documentation entries in `## Documentation`.

- **All three Q&D questions are answered** and are applied as embedded instructions in this analysis run:
  - Q001 `[x] Other`: Archive naming → `input-archive-<YYYY-MM-DD_HH-MI-SS>.md` in an `inputs/` subfolder. Applied to Scope (archive path bullet) and Assumptions A2 (cleaned text; "Decision deferred to Q001" removed).
  - Q002 `[x] Option B`: Internal review and multi-perspective stakeholder review remain two separate sections in `request.md`. Applied to Plan Task 7 wording to make the separation explicit.
  - Q003 `[x] Option A`: Zip files committed to VCS. Applied to Constraints (new bullet added) and Assumptions A4 ("Decision deferred to Q003" removed).

- **Inline `**Amendment:**` notations** exist in the Scope, Assumptions, and Success criteria mandatory sections. These are user edits to mandatory sections reflecting authoritative scope; preserved as-is per lifecycle rules.

- **Non-standard `## Purpose` section** at end of `request.md` after Q&D: contains the user's design specification for the `input.md` template. Informational context; not a convention-defined section; left in place.

- **Context.md version discrepancy:** `context.md` states "Current version: v1.0.14" but the active `.aib_brain/` SemVer marker is `v1.1.2`. Context.md has not been regenerated to reflect versions released after v1.0.14.
  - Evidence: `.aib_brain/v1.1.2` file confirmed present via file search → implication: context.md is stale and must be regenerated to v1.2.0 in Task 12.

- **FR-002 in `context.md`** states: "Creating a request produces a request folder containing `request.md` and `implementation.md`." After Task 2 this is no longer true. FR-002 must be updated during Task 12 context regeneration.

- **`Concepts.md` invocation contract** lists `create-request` and `close-request` as user-facing supported actions. After this request these become non-user-facing. `Concepts.md` has `edit_allowed=N`; the AIB Maintainer must review and update it manually or via a dedicated future request.

- **`versions/` folder already exists** in the workspace root (per Task 9 amendment in `request.md`). Folder creation step is pre-satisfied; only `.gitkeep` placeholder (if absent) and `release_bookkeeping.py` zip step remain.

- **`request-convention.md` section 12 is `## Amends`:** The request scope explicitly removes this section from the convention (replaced by `input.md`). Task 7 must delete section 12 and renumber. Risk: existing `request.md` files in closed requests have no `## Amends` section — acceptable since closed requests are read-only.

- **`test_lifecycle_e2e.py` and `test_close_request.py`** may assert that `request.md` and `implementation.md` exist after `create-request.py` runs. These tests must be reviewed as part of Task 11. Assumption A7 captures this risk.

### 2. Code and asset scan for components impacted

| File | Change type | Reason |
| --- | --- | --- |
| `.aib_brain/tools/initialize.py` | Modify | Add `input.md` seed block after `context.md` seeding |
| `.aib_brain/tools/create-request.py` | Modify | Remove `load_template`, `validate_request_md`, `request.md` write, `implementation.md` write; remove unused imports |
| `.aib_brain/tools/menu.py` | Modify | Remove `SCRIPT_CREATE_REQUEST` and `SCRIPT_CLOSE_REQUEST` constants; add both to `EXCLUDE_SCRIPTS`; remove lifecycle entries from `build_script_actions()`; add `print_prompt_reference()`; remove exit option from main loop |
| `.aib_brain/prompts/aib-analysis.md` | Modify | Add no-active-request branch; add no-changes and no-analysis toggle handling; update archive naming to `inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md` |
| `.aib_brain/prompts/aib-implement.md` | Modify | Add auto-analyze branch for no active request; generate `implementation.md` on-demand; add `close-request.py` auto-close step; exclude `inputs/input-archive-*.md` from input resolution |
| `.aib_brain/conventions/analysis-convention.md` | Modify | Remove code scan and internal review from Research Results; add External Benchmarking (section 5) and Minimal Spikes (section 6) as mandatory standalone sections; renumber |
| `.aib_brain/conventions/request-convention.md` | Modify | Add Code/Asset Scan, Internal Review of Request and Product Docs (separate), Multi-Perspective Stakeholder Review (separate) as new AI-generated sections; remove `## Amends`; make all sections mandatory; update numbering and validation rules |
| `.aib_brain/v1.1.2` | Delete | Version marker rotation from v1.1.2 |
| `.aib_brain/v1.2.0` | Create | New version marker |
| `scripts/release_bookkeeping.py` | Modify | Add `zipfile.ZipFile` step producing `versions/aib_brain_vX.Y.Z.zip`; add idempotency check |
| `versions/` | Existing | Already present; add `.gitkeep` placeholder if absent; ensure not `.gitignore`d |
| `README.md` | Modify | Replace manual `.aib_brain/` copy instruction with `versions/` zip download instruction referencing v1.2.0 |
| `tests/test_initialize.py` | Modify | Add assertion that `input.md` is created with seed template sections |
| `tests/test_create_request.py` | Modify | Remove assertions checking for `request.md` and `implementation.md` in the request folder |
| `tests/test_menu.py` | Modify | Remove lifecycle entry and exit option assertions; add prompt display assertion |
| `tests/test_lifecycle_e2e.py` | Review | May assert `create-request.py` creates `request.md`; verify and update if needed |
| `tests/test_close_request.py` | Review | May depend on `request.md` existing in request folder; verify and update if needed |
| `.aib_memory/context.md` | Regenerate (Task 12) | Reflect v1.2.0, `input.md` artifact, updated FR-002, auto-close behavior, new menu, `versions/` folder, new convention sections |

**No changes to:** `close-request.py`, `reverse-engineer.py`, `common.py`, `conftest.py`, `.github/workflows/aib-semver-patch-bump-and-log.yml` (beyond the zip step in `release_bookkeeping.py`).

### 3. Pattern scan against organizational standards and prior similar solutions

- **Single responsibility for artifact creation:** Moving `request.md` generation from `create-request.py` (script) to `aib-analysis.md` (AI prompt) is consistent with the established AIB pattern where AI-facing prompts generate their own artifacts. Prior example: `aib-analysis.md` already generates `analysis.md` and updates `request.md`; extending it to generate `request.md` de novo on the no-active-request branch follows the same pattern.

- **Timestamped archive naming:** The `input-archive-<YYYY-MM-DD_HH-MI-SS>.md` pattern aligns with the existing `aib-action-<timestamp>-<action-id>.log` naming convention used by `menu.py` for action execution logs. Consistent timestamp format improves predictability and sort order.

- **EXCLUDE_SCRIPTS pattern:** Adding `create-request.py` and `close-request.py` to the existing `EXCLUDE_SCRIPTS` set is the established mechanism for hiding scripts from the menu (already used for `initialize.py`, `reverse-engineer.py`, `menu.py`, `common.py`, `test_common.py`). No new patterns introduced.

- **Convention-governed AI artifact generation:** Fully replacing AI-generated sections on each re-run is the established pattern for `## Assumptions`, `## Plan`, `## Testing`, and `## Documentation`. The three new `request.md` sections follow the same idempotent-replacement convention.

- **Ephemeral fixed-path file pattern:** `.aib_memory/input.md` is analogous to `.aib_memory/context.md` — both are fully replaced on each processing cycle. The key difference: `context.md` has no archive; `input.md` generates a timestamped archive before reset to preserve audit traceability.

### 4. External benchmarking

- **Ephemeral input channel design:** Fixed-path input files replaced per cycle are common in agent orchestration frameworks (LangGraph state files, CrewAI task inputs). The file-based approach trades real-time streaming for audit persistence and model-agnosticism — appropriate for AIB's file-first design. Behavioral toggles via Markdown checkboxes avoid requiring users to learn new CLI flags and are consistent with the existing Markdown-editing interaction model.

- **Convention restructuring — analysis as reasoning, request as specification:** Moving operational sections (code scan, internal review) from `analysis.md` to `request.md` aligns with the principle that specification artifacts contain implementation-actionable content while reasoning artifacts contain rationale only. This separation is consistent with IEEE 830 Software Requirements Specification conventions and standard agile practices distinguishing backlog items from engineering analysis.

- **Multi-perspective stakeholder review:** Generating AI-authored stakeholder perspectives (architect, product owner, user, security officer, data governance officer) as structured sections within the specification is consistent with modern Requirements Engineering practices such as ATAM (Architecture Trade-off Analysis Method), which requires explicit viewpoint-based reviews before implementation begins.

- **Zip-based framework distribution:** Version-tagged zip archives committed to VCS are appropriate for minimal frameworks without package managers or release pipelines. Limitation: binary zip files grow the repository over time; a pruning policy for old archives should be considered in a future request if repository size becomes a concern.

- **Self-documenting menus displaying runnable prompts:** Displaying copy-paste invocations rather than running commands directly is well-established in developer tooling (e.g., `make help` targets, `task --list`). The proposed display follows this pattern: show what to run, let the user invoke it in their preferred interface.

### 5. Result of minimal spikes/experiments

- **No spikes required.** All implementation steps use well-established patterns within the existing codebase: Python standard library only; `zipfile` module for archive creation; Markdown editing for convention files. No novel integration points or external dependencies have been identified.

- **Conditional routing in `aib-analysis.md`:** The two new behavioral toggles (no-changes mode, no-analysis mode) require conditional branching within the prompt text. This is a specification authoring concern, not a technical spike — the branching logic is analogous to existing preflight halt gates already present in the prompt.

- **Risk note — no-changes mode `answer.md` placement:** The "no-changes mode" produces a timestamped `answer.md` in the request folder. The exact placement (request folder root vs. a dedicated subfolder) is not specified in the current request scope. The request folder root is assumed during implementation unless the implementer has reason to prefer a subfolder; this should be documented in the implementation log.

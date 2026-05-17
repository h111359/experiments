## 1. Executive Summary

- **Request ID:** R-20260414-1421
- **Request Title:** Analys rework and remove iterations
- **Iteration ID:** 01
- **High-level purpose:** Remove the iteration concept and its entire machinery (scripts, menu actions, conventions, templates, prompts references, documentation) from the AIB framework; rework the `create-analysis` prompt to consume answered Questions & Decisions, emit them as embedded instructions, and delete them; introduce a lightweight `## Amend Request` section mechanism so users can express request amendments inline and have them applied on the next analysis run.

- **Earlier iterations:** None — this is the first and only iteration.

- **Conflicts resolved:** Not applicable (no prior iterations exist).

- **Sections written to `request.md` during this run:** `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`. No `## Questions & Decisions` section was added because all decision points were resolvable through workspace research. See Section 8 for the full rewrite summary.


## 2. Scope Interpretation

- **In scope — Goal 1:** Remove the `create-iteration` and `close-iteration` lifecycle actions from the supported actions list in `Concepts.md`, the menu actions in `menu.py`, and the EXCLUDE_SCRIPTS list audit.

- **In scope — Goal 1:** Delete the script files `create-iteration.py` and `close-iteration.py` from `.aib_brain/tools/`.

- **In scope — Goal 1:** Remove iteration creation from `create-request.py` (currently creates `iterations.md` and writes an iteration 01 row).

- **In scope — Goal 1:** Delete convention files `iterations-convention.md` and `questionnaire-convention.md` from `.aib_brain/conventions/`.

- **In scope — Goal 1:** Delete template file `iterations-template.md` from `.aib_brain/templates/`.

- **In scope — Goal 1:** Rename analysis output from `<ITERATION_ID>-analysis.md` to `analysis.md` — update `analysis-convention.md`, `request-convention.md`, `Concepts.md` (file naming section), and `aib-analysis.md` prompt.

- **In scope — Goal 1:** Update `aib-implement.md` prompt to remove iteration resolution step.

- **In scope — Goal 1:** Update `Concepts.md` — remove `create-iteration`/`close-iteration` from Supported Actions, Action Contract Matrix, Holistic Workflow, Concepts section, and file naming.

- **In scope — Goal 1:** Update `README.md` (root) and `.aib_brain/README.md` to remove all iteration workflow references.

- **In scope — Goal 1:** Update product docs `RQT-02` (remove FR-003, update FR-004), `KNW-01` (remove TERM-0006 Iteration term), `KNW-02` (update BP-0002 no longer seeds iterations.md), `ARCH-01` (tool scripts component description).

- **In scope — Goal 1:** Delete `tests/test_create_iteration.py` and `tests/test_close_iteration.py`.

- **In scope — Goal 1:** Update `tests/test_create_request.py` to assert `iterations.md` is NOT created.

- **In scope — Goal 1:** Assess `tests/conftest.py` and `tests/test_lifecycle_e2e.py` for iteration-dependent assertions; update as needed.

- **In scope — Goal 2:** Modify `aib-analysis.md` re-run behaviour for `## Questions & Decisions`: answered questions (checkbox checked OR non-empty `> Answer:`) are applied as embedded plain-text instructions to the relevant mandatory sections of `request.md`, then removed from `## Questions & Decisions`. The section is omitted from `request.md` when all questions are answered and applied.

- **In scope — Goal 3:** Define a transient `## Amend Request` section in `request-convention.md`. Update `aib-analysis.md` to detect, apply, and clear this section before normal analysis processing.

- **Out of scope:** Changes to the CI release bookkeeping workflow, GitHub Actions, or SemVer marker logic.

- **Out of scope:** Changes to `aib-documentation.md`, `aib-reverse-engineer.md`, or `aib-context.md` prompts (no iteration references requiring update).

- **Out of scope:** Cloud infrastructure, external services.

- **Implicit — AIB framework rule:** Because `Concepts.md`, `ARCH-01`, `RQT-02`, `KNW-01`, `KNW-02` are product documentation for this workspace, they must be updated when the corresponding behaviour changes. (implicit rule - AIB framework)

- **Implicit — AIB framework rule:** Tests for deleted scripts become dead code and must also be removed. (implicit rule - AIB framework)


## 3. Domain Knowledge Essentials

- **AI Builder (AIB):** A minimal, model-agnostic, file-first framework for specification-driven development. Governs structured work through requests, conventions, prompts, and tool scripts, producing auditable Markdown artifacts.

- **Request:** The primary tracked work unit in AIB. Has a stable ID, lifecycle states (Active/Closed), and a governing `request.md` file.

- **Iteration:** A numbered sub-unit within a request originally intended to track sequential clarification passes. Each iteration could produce analysis, questionnaire, and plan files with a numeric prefix (e.g., `01-analysis.md`). This concept is being **removed** by this request.

- **Brain Folder (`.aib_brain/`):** Stores reusable, framework-level assets — prompts, conventions, templates, and tool scripts. Humans may update this folder explicitly; AIB scripts may not modify it during normal implementation. This request explicitly modifies brain assets as its primary output.

- **Memory Folder (`.aib_memory/`):** Workspace-specific artifacts — requests, registers, product docs. Changed by tool scripts and AI agent prompts.

- **Questions & Decisions section (`## Questions & Decisions` in `request.md`):** AI-generated blocks for unresolvable unknowns. Users check answer options or write free text. This request changes the re-run behaviour so answered questions are consumed and removed, not preserved.

- **Amendment Notation (`## Amend Request`):** A new lightweight mechanism for users to express intent to modify the request without having to directly edit individual mandatory sections. Consumed and cleared by `create-analysis`.

- **Impacted persona — Repository Developer:** Will notice shorter menus (no iteration actions) and a simplified request lifecycle.

- **Impacted persona — AIB Maintainer:** Will manage fewer conventions, templates, and scripts.

- **Impacted persona — AI Automation Agent:** Will no longer resolve `active_iteration_id`; analysis output path changes from `<ITERATION_ID>-analysis.md` to `analysis.md`.


## 4. Technical Knowledge & Terms

- **`menu.py`:** Interactive launcher for AIB tool scripts exposed via a terminal menu. Provides `MenuState` (dataclass tracking active request ID, folder, title, and iteration ID), `resolve_menu_state()`, `build_script_actions()`, and `filter_visible_actions()`. This is the primary component needing iteration removal.

- **`EXCLUDE_SCRIPTS`:** A set in `menu.py` listing script filenames hidden from the menu. Currently: `{"menu.py", "common.py", "initialize.py", "reverse-engineer.py", "test_common.py"}`. After this request, `create-iteration.py` and `close-iteration.py` are candidates for exclusion or deletion.

- **`SCRIPT_CREATE_ITERATION` / `SCRIPT_CLOSE_ITERATION`:** String constants in `menu.py` referencing iteration scripts. Currently used in `filter_visible_actions()` to conditionally display iteration actions based on `MenuState.has_active_iteration`.

- **`MenuState.active_iteration_id`:** Frozen-dataclass field tracking active iteration from `iterations.md`. Its `has_active_iteration` property drives conditional visibility. Both will be removed.

- **`create-request.py`:** Currently creates `iterations.md` alongside `request.md` and `implementation.md`. The `iterations.md` creation block and `ACTIVE, now_iso` iteration seeding will be removed.

- **`analysis-convention.md`:** Normative convention for `<ITERATION_ID>-analysis.md`. Section 3 defines file naming with iteration prefix. Section 8 Seed step references `<ITERATION_ID>-analysis.md`. All instances will change to `analysis.md`.

- **`request-convention.md`:** Governs `request.md` schema. Section "Optional Sections" will gain a definition for the transient `## Amend Request` section. The analysis file reference (currently `<ITERATION_ID>-analysis.md`) will be updated.

- **`aib-analysis.md` prompt:** The invocation spec for `create-analysis`. Currently: resolves `iteration_id`; creates `<ITERATION_ID>-analysis.md`; Q&D re-run rule preserves answered questions verbatim. After this request: no iteration ID; creates `analysis.md`; answered Q&D are applied as instructions then removed; detects `## Amend Request` and applies amendments before analysis.

- **`aib-implement.md` prompt:** Resolves active iteration from `iterations.md`. This step is removed; analysis file path reference is updated.

- **`iterations-convention.md` / `questionnaire-convention.md`:** Convention files for now-deleted artifacts. Both to be deleted.

- **`iterations-template.md`:** Seed template for `iterations.md`. To be deleted.

- **Testing:** `test_create_iteration.py` and `test_close_iteration.py` test the two iteration scripts being removed. Both test files will be deleted. `conftest.py` and `test_lifecycle_e2e.py` likely assert presence of `iterations.md` or iteration-prefixed files; those assertions must be removed or updated.

- **Python 3.10+:** Runtime requirement for all tool scripts. No changes to the Python dependency.

- **Markdown-first:** All AIB artifacts are plain Markdown. No breaking serialization changes.

- **`## Amend Request` transient section:** Proposed new optional section in `request.md` written by the user to express inline amendments. Detected by the analysis prompt before normal processing, applied to mandatory sections, then cleared (section removed). Not to be preserved across runs.


## 5. Impact Assessment

### 5.1 Affected Components / Areas

- `menu.py` — modify (remove iteration tracking and actions)
- `.aib_brain/tools/create-request.py` — modify (remove iterations.md creation)
- `.aib_brain/tools/create-iteration.py` — remove
- `.aib_brain/tools/close-iteration.py` — remove
- `.aib_brain/prompts/aib-analysis.md` — modify (analysis path, Q&D re-run, amendment detection)
- `.aib_brain/prompts/aib-implement.md` — modify (remove iteration resolution)
- `.aib_brain/conventions/analysis-convention.md` — modify (file naming)
- `.aib_brain/conventions/request-convention.md` — modify (amendment section, analysis path)
- `.aib_brain/conventions/iterations-convention.md` — remove
- `.aib_brain/conventions/questionnaire-convention.md` — remove
- `.aib_brain/templates/iterations-template.md` — remove
- `.aib_brain/Concepts.md` — modify (remove iteration actions, update file naming, update workflow)
- `README.md` (root) — modify (remove iteration references)
- `.aib_brain/README.md` — modify (remove iteration commands and workflow)
- `.aib_memory/docs/03 Requirements/RQT-02.md` — modify (remove FR-003, update FR-004)
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — modify (remove TERM-0006)
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — modify (update BP-0002)
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — modify (tool scripts component)
- `tests/test_create_iteration.py` — remove
- `tests/test_close_iteration.py` — remove
- `tests/test_create_request.py` — modify (assert no iterations.md)
- `tests/conftest.py` and `tests/test_lifecycle_e2e.py` — review and update

### 5.2 Change Type and Dependencies

- `create-iteration.py` removal: depends on menu.py update (remove action reference) and test removal. No downstream script consumes it.

- `close-iteration.py` removal: same dependency pattern as create-iteration.py.

- `create-request.py` change: no downstream dependency — `iterations.md` is no longer a required artifact.

- `analysis.md` naming: `analysis-convention.md`, `request-convention.md`, `Concepts.md`, and `aib-analysis.md` prompt must all be updated atomically to prevent convention/reality mismatch.

- Q&D consumption behaviour: `aib-analysis.md` change is self-contained; no other file encodes the preservation rule except this prompt.

- Amendment notation: requires both `aib-analysis.md` update (detection & apply) and `request-convention.md` update (define the section).

- Sequencing: file deletions should occur last (after code changes are validated); test updates should happen before deletions to avoid broken references.

### 5.3 Domain Impacts

- DOMAIN (ARCH): ARCH-01 component inventory for AIB Tool Scripts must drop create-iteration.py and close-iteration.py from description. Minor update.

- DOMAIN (CMP): No impact detected.

- DOMAIN (DATA): No impact detected.

- DOMAIN (DEV): Moderate impact — two tool scripts deleted, menu.py significantly trimmed, create-request.py simplified. Test suite reduced by two test files.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (KNW): KNW-01 loses TERM-0006 (Iteration definition). KNW-02 BP-0002 description updated.

- DOMAIN (RQT): RQT-02 loses FR-003 and gains simplified FR-004; acceptance criteria updated.

- DOMAIN (OBS): No impact detected — logs structure is unchanged.

- DOMAIN (OPR): No impact detected — CI workflow unchanged.

- DOMAIN (SEC): No impact detected — write-gating and permissions model unchanged.


## 6. Research Plan and Findings

### Methodology

1. Internal-first review of `request.md`, `iterations.md`, `Concepts.md`, `references.md`, `context.md`.
2. Full directory scan of `.aib_brain/` to map all affected assets.
3. Code scan of `menu.py`, `create-request.py`, `create-iteration.py`, `close-iteration.py` for iteration-dependent logic.
4. Read both convention files proposed for removal (`iterations-convention.md`, `questionnaire-convention.md`) to assess residual dependencies.
5. Read relevant product docs: ARCH-01, RQT-01, RQT-02, KNW-01, KNW-02, KNW-03.
6. grep scan across `.aib_brain/` for `iteration_id|ITERATION_ID|active iteration|iterations\.md` to confirm all surfaces.

### Evidence Summary

- `menu.py` uses two named constants (`SCRIPT_CREATE_ITERATION`, `SCRIPT_CLOSE_ITERATION`) and tracks `active_iteration_id` in `MenuState`. `filter_visible_actions()` has two dedicated branches for iteration scripts. All four touch-points must be removed.

- `create-request.py` writes `iterations.md` with a hardcoded row for iteration `01 Active`. The write block is self-contained and removable without cascading effects on other parts of the script.

- The analysis output `<ITERATION_ID>-analysis.md` appears in six places: `analysis-convention.md` (Section 3 & Section 8), `request-convention.md` (optional sections list), `Concepts.md` (file naming section), `aib-analysis.md` prompt (goal + output definition), and `aib-implement.md` prompt (input resolution).

- `questionnaire-convention.md` exists but has no corresponding prompt in `.aib_brain/prompts/` (no `aib-questionnaire.md`). It is truly vestigial.

- `iterations-convention.md` is referenced in no active prompt. It describes `<ITERATION_ID>-questionnaire.md` and `<ITERATION_ID>-plan.md` as artifacts — both already removed. Removing this convention creates no active-path breakage.

- `iterations-template.md` is in `.aib_brain/templates/` but is not referenced from any currently active script (create-request.py builds the table inline). Safe to delete.

- RQT-02 has an explicit `FR-003` for Active iteration management. This requirement is rendered obsolete by this request.

- KNW-01 has `TERM-0006` for "Iteration" which should be removed for consistency.

- KNW-02 `BP-0002` describes "seeds default iteration 01" in the create-request steps.

- Test files `test_create_iteration.py` and `test_close_iteration.py` are specifically for the scripts being removed.

- `conftest.py` and `test_lifecycle_e2e.py` were identified as potentially containing `iterations.md`-related assertions; must be read and updated during implementation.

### Gaps and Unknowns

- `conftest.py` and `test_lifecycle_e2e.py` not fully read — exact iteration assertions not confirmed. Identified as a gap; implementation must audit these files before final deletion of iteration scripts.

- `common.py` not fully read — may contain iteration-specific helpers. Implementation must verify.

### Proposed Validation Actions

- After menu.py change: run the menu interactively and confirm iteration actions absent.
- After create-request.py change: run `python create-request.py` on a temp workspace and confirm no `iterations.md` created.
- After test deletions: run full test suite; confirm no import or fixture errors.

### Files Read

- `.aib_memory/requests/R-20260414-1421-analys-rework-and-remove-iterations/request.md` — Active request content; three-goal scope confirmed.
- `.aib_memory/requests/R-20260414-1421-analys-rework-and-remove-iterations/iterations.md` — Active iteration 01 confirmed.
- `.aib_memory/references.md` — Full references list; 27 product-docs + domain + other entries read.
- `.aib_brain/conventions/analysis-convention.md` — 12-section convention; file naming at Section 3; confirmed ITERATION_ID prefix throughout.
- `.aib_brain/conventions/request-convention.md` — Request schema; optional sections 7–11 listed; amendment section not yet defined.
- `.aib_brain/Concepts.md` — Full invocation contract, lifecycle rules, file naming, folder structure.
- `.aib_memory/context.md` — Synthesized context with component map and FRs.
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — Stub; no substantive content.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — FR-001 through FR-009; FR-003 and FR-004 directly impacted.
- `.aib_brain/conventions/iterations-convention.md` — Confirmed vestigial; describes questionnaire/plan artifacts already removed.
- `.aib_brain/conventions/questionnaire-convention.md` — Confirmed vestigial; no matching prompt.
- `.aib_brain/tools/menu.py` — Full read; identified four iteration touch-points.
- `.aib_brain/tools/create-iteration.py` — Full read; confirmed self-contained script.
- `.aib_brain/tools/close-iteration.py` — Full read; confirmed self-contained script.
- `.aib_brain/tools/create-request.py` — Full read; confirmed iterations.md write block.
- `.aib_brain/prompts/aib-analysis.md` — Full read; confirmed iteration ID resolution and Q&D preservation rule.
- `.aib_brain/prompts/aib-implement.md` — Full read; confirmed iteration resolution step.
- `README.md` — Full read; iteration workflow steps confirmed.
- `.aib_brain/README.md` — Full read; multiple iteration command examples confirmed.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-01.md` — Read; component inventory confirms iteration scripts in Tool Scripts component.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md` — Read; TERM-0006 confirmed.
- `.aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md` — Read; BP-0002 seeds iteration 01.
- `.aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md` — Read; no direct iteration references in persona/use-case definitions.
- `.aib_brain/conventions/context-convention.md` — Read; product-agnostic structure; no iteration-specific references.
- `.aib_brain/prompts/aib-context.md` — Read; auto-generates context.md; no iteration-specific steps.
- `.aib_memory/docs/04 Technology/Architecture/ARCH-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-04.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Architecture/ARCH-06.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Inventory/ARCH-07.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Compute/CMP-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Compute/CMP-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Sources/DATA-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Models/DATA-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-04.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-05.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Analytics/DATA-06.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-07.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Data Workspace/DATA-08.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Analytics/DATA-09.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Observability/OBS-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-01.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-02.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-03.md` — [SKIPPED — domain out of scope]
- `.aib_memory/docs/04 Technology/Access and Security/SEC-04.md` — [SKIPPED — domain out of scope]


## 7. Risks

- Risk R1: Incomplete iteration reference sweep
  - Probability: Medium
  - Impact: High
  - Mitigation: grep scan for `iteration_id|ITERATION_ID|iterations\.md` across the full workspace before closing implementation. Fix any remaining references.
  - Owner (role): AI Automation Agent
  - Contingency: If a stale iteration reference is discovered post-implementation, open a follow-up request to patch it.

- Risk R2: E2E and conftest test breakage
  - Probability: Medium
  - Impact: Medium
  - Mitigation: Fully read `conftest.py` and `test_lifecycle_e2e.py` during implementation (Task 9), update iteration-dependent fixtures and assertions before deleting scripts.
  - Owner (role): AI Automation Agent

- Risk R3: `common.py` residual iteration helpers
  - Probability: Low
  - Impact: Medium
  - Mitigation: Read `common.py` fully during implementation; remove or retain helpers that are not exclusively for iteration scripts.
  - Owner (role): AI Automation Agent
  - Contingency: If shared helpers are also used by other scripts, keep them and only remove iteration-specific call-sites.

- Risk R4: Analysis re-run idempotency regression for Q&D consumption
  - Probability: Low
  - Impact: Medium
  - Mitigation: Define the apply-and-remove logic precisely in `aib-analysis.md`; add an explicit idempotency test (T5 in `## Testing`). A question already absent from `## Questions & Decisions` must not cause errors.
  - Owner (role): AI Automation Agent

- Risk R5: `## Amend Request` section not cleared on re-run
  - Probability: Low
  - Impact: Medium
  - Mitigation: The `aib-analysis.md` prompt must specify that the section is always removed after application, even if the amendment is empty. Add test T6 verifying section removal.
  - Owner (role): AI Automation Agent


## 8. Request Rewrite Summary

- **`## Assumptions`** written: Three implementation-affecting assumptions identified during analysis — (A1) `common.py` has no iteration-exclusive helpers beyond those used by deleted scripts; (A2) `context.md` will be regenerated via `aib-context.md` after this change rather than manual update; (A3) the convention file `questionnaire-convention.md` has no active prompt referencing it.

- **`## Plan`** written: 11 tasks covering menu.py update, create-request.py update, analysis file renaming across conventions and prompts, amendment notation definition and prompt update, Concepts.md/README/product-doc updates, and deletion of iteration scripts/tests/conventions/template. Tasks are sequenced to avoid broken-reference windows.

- **`## Testing`** written: 9 intent-level test cases covering file existence, menu behaviour, script behaviour, Q&D consumption, amendment application, and full test suite health.

- **`## Documentation`** written: Lists all documentation files requiring revision as a result of this request, with `ref_id` cross-references to `.aib_memory/references.md`.

- **`## Questions & Decisions`** not written: All decision forks were resolvable through direct workspace research. No user-facing questions are needed for this iteration.

- **QID log:** No QIDs exist on first run; none were added, none were preserved. No decision-review flags raised.

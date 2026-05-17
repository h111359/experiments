## Executive Summary
- This analysis covers iteration `01` for request `R-20260321-2314`, focused on improving the `.aib_brain` interactive menu and bootstrapping behavior.
- Core intent: make `.aib_memory` initialization automatic on launcher start (only when missing), and make the interactive menu context-aware (only show valid next actions, and show active request/iteration status concisely).
- Current evidence: `.aib_brain/run.bat` calls `.aib_brain/tools/menu.py`; `menu.py` renders a static banner and reads a static `menu_config.json` containing an explicit “Initialize” action; `initialize.py` always writes/overwrites `.aib_memory/requests_register.md` and `.aib_memory/references.md`.
- Key decisions needed in this iteration: where to trigger the auto-initialize check (launcher vs menu), what “initialized” means (folder-only vs key files), and how to implement dynamic menu visibility (hard-coded logic vs config-driven conditions).
- Expected outcome if accepted: running `.aib_brain/run.bat` is safe and self-healing when `.aib_memory` is missing; the menu is shorter and only offers state-valid actions; the menu stops repeating usage instructions that are already documented in `.aib_brain/README.md`.

## Request Context Snapshot
- Request ID: `R-20260321-2314`
- Request title (folder slug): `issue-23`
- Iteration ID: `01` (state: Active; created_at: `2026-03-21 23:14:52 +0200`)
- High-level purpose: streamline AIB workflow by auto-initializing `.aib_memory` when missing, and by making the command menu state-aware and more compact.
- Constraints inherited from `request.md`: 
  - Initialization must be automatic on `run.bat` execution; no menu entry is needed for initialization.
  - Initialization must run only when `.aib_memory/` does not exist; if it exists, it must not be changed.
  - Menu must be dynamic (hide impossible actions depending on whether an active request / iteration exists).
  - Menu must not display the two provided instruction blocks; those must live in `.aib_brain/README.md`.
  - Menu must display active request and iteration concisely (or indicate none).
- Scope delta vs prior iteration: none (this is the first iteration).

## Scope Interpretation
- In scope:
  - Add an automatic startup check that ensures `.aib_memory/` exists; if missing, initialize it.
  - Remove the “Initialize AIB memory” action from the interactive menu (because initialization is automatic).
  - Make menu options conditional on state:
    - When no active request exists: do not show “Close request” (and other request/iteration closing actions); show “Create request”.
    - When an active request exists: do not show “Create request”; show request/iteration actions that are valid.
    - When no active iteration exists: do not show “Close iteration”.
    - When an active iteration exists: do not show “Create iteration”.
  - Remove menu screen text that duplicates the provided usage instruction blocks; move/ensure them in `.aib_brain/README.md`.
  - Display “active request” and “active iteration” status in the menu.
- Out of scope:
  - Changing the core request/iteration lifecycle rules beyond what is required for dynamic visibility.
  - Introducing additional UI features beyond visibility + concise status (no extra pages/modes).
- Implicitly in scope:
  - Update `.aib_brain/README.md` to include the exact instruction blocks moved out of the menu. (implicit rule - AIB framework)
  - Update relevant tool scripts/configs to keep behavior deterministic and consistent. (implicit rule - AIB framework)

## Domain Knowledge Essentials
- AIB workspace: a repository structured around `.aib_brain` (tools + prompts) and `.aib_memory` (state + request artifacts).
- Active request: at most one request in `.aib_memory/requests_register.md` with state `Active`.
- Active iteration: at most one iteration in a request’s `iterations.md` with state `Active`.
- Roles/personas:
  - Developer/operator: runs `.aib_brain/run.bat` and uses the menu to execute lifecycle actions.
  - Maintainer: updates tool scripts and documentation to keep workflow consistent.
- Acceptance impact (product perspective): fewer “gotchas” (missing initialization), faster navigation (shorter menu), reduced clutter (instructions live in README), lower chance of executing invalid actions.

## Technical Knowledge & Terms
- `.aib_brain/run.bat`: Windows launcher that invokes the interactive menu.
- `.aib_brain/tools/menu.py`: Python interactive TUI-like menu that reads `.aib_brain/tools/menu_config.json` and runs actions.
- `.aib_brain/tools/initialize.py`: script that creates `.aib_memory` structure and seeds default artifacts.
- `.aib_memory`: workspace-local state folder containing:
  - `.aib_memory/requests_register.md` (request registry)
  - `.aib_memory/references.md` (references registry)
  - `.aib_memory/requests/<request-folder>/...` (request artifacts)
- “Dynamic menu”: menu contents depend on workspace state (whether `.aib_memory` exists, whether there is an active request, whether there is an active iteration).

## Assumptions
- Assumption A1: “Initialize when `.aib_memory` does not exist” means checking for the directory only (not individual files).
  - Rationale: the request explicitly names the folder existence check as the trigger.
  - Risk if false: if `.aib_memory` exists but is incomplete/corrupted, the menu may fail later (and the user expected self-healing).
  - Falsification method: confirm whether the desired behavior is folder-only or “folder OR key files missing” before implementing.
- Assumption A2: Removing the initialization action from the menu is acceptable even for users who want to re-seed references/docs.
  - Rationale: the request explicitly states there is no need for a menu entry and initialization should be automatic.
  - Risk if false: maintainers may lose a convenient path for re-initialization in a clean/safe way.
  - Falsification method: confirm whether a “manual re-init” path is still needed (e.g., direct CLI invocation only).
- Assumption A3: The menu can determine active request and iteration solely from `.aib_memory/requests_register.md` and the active request’s `iterations.md`.
  - Rationale: this is how the tool scripts enforce lifecycle state today.
  - Risk if false: menu may display incorrect status if additional state sources exist.
  - Falsification method: scan for any other state files used by tools; verify create/close scripts only use these sources.
- Assumption A4: The “dynamic menu” requirements apply only to the four lifecycle actions (create/close request, create/close iteration), and not to all future auto-discovered scripts.
  - Rationale: the request explicitly calls out those actions and behaviors; menu also auto-discovers scripts.
  - Risk if false: auto-discovered scripts may need state gating too, requiring a broader design.
  - Falsification method: confirm whether dynamic visibility should apply to all actions or only the lifecycle subset.
- Assumption A5: The two instruction blocks provided in the request must appear verbatim in `.aib_brain/README.md`.
  - Rationale: the request provides exact strings and says they should be described in README.
  - Risk if false: changes could be rejected due to wording mismatch.
  - Falsification method: confirm whether exact text is required or whether equivalent wording is acceptable.

## Impact Assessment
### Affected Components / Areas
- `.aib_brain/run.bat` (startup behavior)
- `.aib_brain/tools/menu.py` (banner text, state display, dynamic action list)
- `.aib_brain/tools/menu_config.json` (remove/adjust init action; potentially add gating metadata)
- `.aib_brain/tools/initialize.py` (idempotence considerations if auto-run; must avoid changing existing `.aib_memory`)
- `.aib_brain/README.md` (move usage instruction blocks here)
- `.aib_memory` runtime state (consumed by menu for status)

### Change Type and Dependencies
- `.aib_brain/run.bat`
  - Change type: modify
  - Dependencies: depends on Python availability; may call initialization conditionally before launching menu.
  - Sequencing: initialization check must occur before menu loads state.
- `.aib_brain/tools/menu.py`
  - Change type: modify
  - Dependencies: depends on `.aib_memory` state to decide which actions to show and which status to print.
  - Sequencing: must compute state, then filter actions, then render.
- `.aib_brain/tools/menu_config.json`
  - Change type: modify
  - Dependencies: consumed by `menu.py`; may need to carry per-action metadata for filtering.
  - Sequencing: update together with `menu.py` logic.
- `.aib_brain/tools/initialize.py`
  - Change type: modify (potentially)
  - Dependencies: must be safe when invoked automatically; must not overwrite existing `.aib_memory` content.
  - Sequencing: either (a) keep as-is and only run when `.aib_memory` is missing, or (b) make it idempotent and safe to re-run.

### Domain Impacts
- DOMAIN (ARCH): No impact detected.
- DOMAIN (CMP): No impact detected.
- DOMAIN (DATA): No impact detected.
- DOMAIN (DEV): Impacts developer workflow/UX for AIB tool execution (menu behavior and initialization path).
- DOMAIN (DSR): No impact detected.
- DOMAIN (FNL): No impact detected.
- DOMAIN (KNW): No impact detected.
- DOMAIN (RQT): No impact detected.
- DOMAIN (OBS): No impact detected.
- DOMAIN (OPR): Minor operational process impact: changes to how operators launch and interpret the menu.
- DOMAIN (SEC): No impact detected.

### Constraints
- Must not modify `.aib_memory` if it already exists (per request).
- Must keep menu concise; remove duplicated instruction blocks.
- Must keep the menu deterministic: action numbering and key shortcuts should remain intuitive when actions are filtered.
- Must not introduce secrets/credentials into generated artifacts.

### Required Documentation Updates
- ARCH-01 - High-level architecture
  Required update? NO
  Reason: workflow/UI tooling change only.
- RQT-02 - Requirements document
  Required update? NO
  Reason: no product requirement changes; only tooling UX and `.aib_brain/README.md` are impacted.
- OBS-01 - Logging
  Required update? NO
  Reason: no changes to logging/telemetry requirements are requested.
- SEC-01 - Access management
  Required update? NO
  Reason: no authentication/authorization changes are requested.

### Decision Points
- Decision D1: What constitutes “initialized” for auto-init?
  - Option 1: Only check folder existence (`.aib_memory/` exists => do nothing).
    - Implications: strictly matches request wording; may leave partially-initialized states unfixed.
    - Recommended: YES (matches stated constraint “otherwise don’t change it”).
  - Option 2: Check for key files (folder exists but missing `requests_register.md`/`references.md` => initialize missing only).
    - Implications: more robust; may violate “don’t change it” unless carefully defined.
    - Recommended: Only if stakeholder confirms.
- Decision D2: Where to place auto-init logic?
  - Option 1: In `.aib_brain/run.bat` (wrapper performs the check and runs `initialize.py` once).
    - Implications: Windows-specific; `run.sh` would need a parallel change for parity.
    - Recommended: If the request is Windows-only; otherwise also implement in `menu.py` for portability.
  - Option 2: In `menu.py` (menu self-checks workspace state before loading actions).
    - Implications: cross-platform; single source of truth; requires careful handling of CLI `--workspace`.
    - Recommended: YES (more robust across launchers).
- Decision D3: How to implement “dynamic menu”?
  - Option 1: Filter actions in `menu.py` based on computed state, using hard-coded rules keyed by script name.
    - Implications: minimal config changes; straightforward; must be maintained as actions evolve.
    - Recommended: YES for MVP.
  - Option 2: Add `visibility_conditions` metadata per action in `menu_config.json`.
    - Implications: more scalable/configurable; adds parsing/validation complexity.
    - Recommended: If menu actions are expected to grow significantly.

### Estimated Implementation Complexity
- Medium
  - Rationale: changes span launcher/menu/config plus safe initialization behavior; dynamic filtering must preserve user shortcuts and keep deterministic IDs.
  - Confidence: Medium (requirements are clear, but edge cases around partial initialization and auto-discovered scripts may require clarification).

## Research Plan and Findings
- Methodology:
  - Internal docs scan: `.aib_brain/README.md`, `.aib_brain/prompts/aib-create-analysis.md`, conventions.
  - Repository scan: `.aib_brain/run.bat`, `.aib_brain/tools/menu.py`, `.aib_brain/tools/initialize.py`, lifecycle scripts.
  - State model scan: `.aib_memory/requests_register.md` expectation in scripts; `iterations.md` active iteration model.
- Evidence summary:
  - `run.bat` directly launches `menu.py` with a `--workspace` argument.
  - `menu.py` prints a large ASCII banner with the exact usage instructions the request wants removed.
  - `menu_config.json` includes an explicit “Initialize AIB memory” action.
  - `initialize.py` writes/overwrites `requests_register.md` and `references.md` unconditionally, so it must not be invoked when `.aib_memory` already exists (to meet the request).
- Gaps/unknowns:
  - Whether “initialized” means folder-only or key-file completeness.
  - Whether dynamic gating should apply to auto-discovered non-lifecycle scripts.
  - Whether `run.sh` must also be updated for parity (request explicitly mentions `run.bat`).
- Proposed validation actions:
  - Spike: simulate states (no `.aib_memory`, no active request, active request with active iteration, active request without active iteration) and verify menu options match expectations.
  - SME input: confirm whether initialization should ever be manually accessible.
- Evidence log (evidence -> implication):
  - `initialize.py` overwrites registry files -> auto-init must be guarded strictly (only when `.aib_memory` missing).
  - `menu.py` banner includes the instruction blocks -> removing them reduces menu clutter, but the exact text must be preserved in `.aib_brain/README.md`.
  - Lifecycle scripts enforce “single active request/iteration” -> menu can safely compute state from existing tables.

## Rewrite Proposal of the Request
```md
## Goal
Make `.aib_brain` startup and the interactive command menu more state-aware and compact.

1) Automatic initialization
- When `.aib_brain/run.bat` is executed, automatically check whether `.aib_memory/` exists.
- If `.aib_memory/` does not exist, run initialization to create and seed it.
- If `.aib_memory/` exists, do not modify anything inside it.
- Do not expose a separate menu action for initialization.

2) Dynamic menu actions
- The menu must show only valid next actions based on the current state:
  - If there is no active request: show “Create request” and hide “Close request”, “Create iteration”, and “Close iteration”.
  - If there is an active request: hide “Create request” and show “Close request”.
  - If there is no active iteration: hide “Close iteration” and show “Create iteration”.
  - If there is an active iteration: hide “Create iteration” and show “Close iteration”.

3) Move menu instructions to documentation
- Remove these instruction blocks from the menu UI and place them in `.aib_brain/README.md`:

AI Builder terminal command menu
Launch with .aib_brain/run.bat (Windows) or .aib_brain/run.sh (Linux/macOS).
Use Up/Down arrows + Enter, or press the action number directly.
Press Q to quit from the menu.

AI Builder
Command menu for .aib_brain/tools scripts (launchers in .aib_brain)

4) Display active state
- The menu must display the active request ID (or explicitly state none).
- The menu must display the active iteration ID for the active request (or explicitly state none).

## Background
The current menu is static and includes usage instructions inline. Initialization is currently manual and can be forgotten, causing tooling failures.

## Scope
- Update the launcher/menu/config/scripts required to implement automatic initialization and dynamic menu visibility.
- Update `.aib_brain/README.md` to include the removed instruction blocks.

## Out of scope
- No additional menu pages or features beyond dynamic visibility and concise active state display.

## Constraints
- Do not change an existing `.aib_memory/` folder.

## Success criteria
- Running `.aib_brain/run.bat` in a fresh workspace (no `.aib_memory`) results in `.aib_memory/` being created and the menu opening successfully.
- Running `.aib_brain/run.bat` in an already-initialized workspace does not modify `.aib_memory/`.
- The menu only shows actions valid for the current request/iteration state.
- The menu does not display the two instruction blocks; `.aib_brain/README.md` contains them.
- The menu displays active request and iteration state concisely.
```

## Solution Options
- Option A (Recommended): Implement state detection + filtering in `menu.py`, keep `menu_config.json` mostly static
  - Overview: `menu.py` determines state (memory present, active request, active iteration) and filters the actions list before rendering.
  - Benefits: minimal configuration changes; cross-platform; aligns with current Python-first architecture.
  - Trade-offs: filtering logic is code-based (less configurable).
  - Constraints: must keep numbering stable for the visible actions.
  - Risks: filtering may inadvertently hide auto-discovered scripts if rules are too broad.
  - Expected effort: Medium (1–2 focused iterations).
  - Acceptance tests: verify each state combination produces the correct visible actions.
- Option B: Extend `menu_config.json` with explicit visibility rules
  - Overview: add metadata like `requires_active_request`, `requires_active_iteration`, etc., and implement a generic evaluator in `menu.py`.
  - Benefits: scalable as more actions are added.
  - Trade-offs: config schema evolution + validation needed.
  - Constraints: must handle missing metadata for auto-discovered scripts.
  - Risks: schema drift, invalid configs breaking menu.
  - Expected effort: Medium to High depending on validation strictness.
  - Acceptance tests: schema validation + state-based filtering.
- Recommendation: Option A for this request (fast, deterministic), with a path to evolve into Option B if needed.

## Suggested Implementation Approach
- Add an initialization guard that triggers only when `.aib_memory/` is missing:
  - Prefer implementing the guard in `menu.py` (so it works for `run.bat` and `run.sh` equally), optionally mirrored in `run.bat`.
  - Ensure the guard never runs `initialize.py` when `.aib_memory/` exists to avoid overwriting seeded files.
- Implement state detection:
  - Determine “active request” by reading `.aib_memory/requests_register.md` and finding a single `Active` row.
  - Determine “active iteration” by reading the active request’s `iterations.md` and finding a single `Active` row.
- Filter visible actions based on state:
  - Remove/hide the “Initialize AIB memory” action entirely.
  - Hide/show create/close request and create/close iteration actions per rules.
- Update menu rendering:
  - Remove the large instruction blocks from `ascii_banner()` and from the UI subtitle; show concise active request/iteration status.
- Document updates:
  - Add the provided instruction blocks to `.aib_brain/README.md` (verbatim if required).
- Capture steps in `<ITERATION_ID>-plan.md` once this analysis is accepted.

## Suggested Testing Approach
- Manual functional checks (primary):
  - Fresh workspace (no `.aib_memory`): run `.aib_brain/run.bat`, confirm `.aib_memory` is created and menu opens.
  - Initialized workspace: run `.aib_brain/run.bat`, confirm `.aib_memory` timestamps/content are unchanged (no overwrite of `requests_register.md`/`references.md`).
  - No active request: confirm menu shows “Create request” and hides close/create/close iteration.
  - Active request with active iteration: confirm menu hides “Create request” and “Create iteration”, shows “Close request” (if allowed by iteration state) and “Close iteration”.
  - Active request without active iteration: confirm menu shows “Create iteration” and “Close request”.
- Lightweight script-level sanity (optional):
  - Add a small non-interactive state-evaluation function in `menu.py` and unit-test it if a test harness exists; otherwise keep verification manual.

## Affected Documentation
| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| N/A | No affected documents identified at this stage. | N/A | The change impacts `.aib_brain` tooling and `.aib_brain/README.md`, not the product-doc set referenced in `.aib_memory/references.md`. |

## Operational & Documentation Implications
- Operators will no longer need to manually run initialization before using the menu in a fresh workspace.
- Menu UX becomes state-aware, reducing the chance of invalid actions and reducing the visible option list.
- `.aib_brain/README.md` becomes the authoritative place for the menu usage instructions.
- If a maintainer needs re-seeding behavior later, they may need to run `initialize.py` directly (unless a separate safe “repair” tool is introduced in a future request).

## Risks
- Risk R1: Automatic initialization overwrites existing `.aib_memory` files if the guard is implemented incorrectly.
  - Probability: Medium
  - Impact: High
  - Mitigation: guard strictly on directory absence; avoid calling `initialize.py` when `.aib_memory` exists; add explicit checks for `requests_register.md` and `references.md` overwrite paths.
  - Owner (role): Maintainer
- Risk R2: Dynamic menu filtering causes confusing action numbering or hides needed actions unexpectedly.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: filter before numbering; display only visible actions and renumber 1..N; validate across all supported states.
  - Owner (role): Developer/operator
- Risk R3: Ambiguity about whether `run.sh` must match the new behavior leads to inconsistent cross-platform experience.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: implement initialization + dynamic logic inside `menu.py` so both launchers benefit; update both launchers only if needed.
  - Owner (role): Maintainer

## Dependencies / Externalities
- Human inputs: confirm whether the instruction blocks must be verbatim in `.aib_brain/README.md`.
- Human inputs: confirm whether “initialized” is strictly folder existence or includes key-file completeness.
- Environment prerequisites: Python must be available on PATH for `.aib_brain/run.bat`.

## Open Questions & Next Actions
1. Confirm what counts as “initialized”: folder-only or folder + key files? (Owner: Requestor; Trigger: before implementation starts; Resolution path: clarify requirement in request comments or next iteration.)
2. Confirm whether the instruction blocks must be included verbatim in `.aib_brain/README.md`. (Owner: Requestor; Trigger: before README edit is finalized; Resolution path: approve exact wording.)
3. Confirm whether dynamic gating applies only to the four lifecycle actions or to all menu actions (including future auto-discovered scripts). (Owner: Maintainer; Trigger: before implementing filtering logic; Resolution path: define filtering scope.)

## Appendices
- Current state evidence:
  - `initialize.py` overwrites `.aib_memory/requests_register.md` and `.aib_memory/references.md` unconditionally, so it must only run when `.aib_memory/` is missing.
  - `menu.py` currently embeds the usage instruction blocks in the ASCII banner and shows a static set of actions from `menu_config.json`.
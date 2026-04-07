## Executive Summary
- Request `R-20260321-2314` (folder: `issue-23`) is about improving `.aib_brain` startup/menu UX: auto-initialize `.aib_memory` only when missing, and make the menu dynamic (show only valid next actions) while displaying active request/iteration concisely.

- This analysis covers iteration `02` (Active) and supersedes any conflicting guidance from iteration `01` per iteration-supremacy rules.

- Key implementation reality: `.aib_brain/run.bat` and `.aib_brain/run.sh` both call `.aib_brain/tools/menu.py`; `menu.py` currently prints the instruction blocks that must be removed from the menu UI, and `menu_config.json` currently contains an explicit “Initialize AIB memory” action.

- The initializer `.aib_brain/tools/initialize.py` currently writes seed files (`.aib_memory/requests_register.md`, `.aib_memory/references.md`) unconditionally, so automatic initialization MUST be guarded to avoid changing an existing `.aib_memory/` folder.

- The request as written leaves several acceptance details unspecified (the `request.md` sections `Scope`, `Out of scope`, `Constraints`, `Success criteria` are empty), so this iteration must explicitly capture assumptions and produce a questionnaire to make decisions answerable before plan/implementation.

- Primary decision points: what “initialized” means (folder-only vs key files), where to place the auto-init check (launcher vs `menu.py`), and how to define dynamic visibility for both configured actions and auto-discovered scripts.

- Expected outcome if stakeholders accept the recommendations: a shorter menu that never offers invalid lifecycle actions, a safe startup that self-initializes only when `.aib_memory/` is absent, and documentation moved into `.aib_brain/README.md` (not duplicated in menu).

## Scope Interpretation
- In scope: add an automatic check on startup to ensure `.aib_memory/` exists; if missing, initialize it; if it exists, do not change it.

- In scope: remove/avoid a visible menu action for initialization; initialization becomes automatic when launching the menu.

- In scope: make the menu dynamic for lifecycle actions (create/close request, create/close iteration) so only valid next steps are visible.

- In scope: remove the two provided instruction blocks from the menu UI and ensure they are described in `.aib_brain/README.md`.

- In scope: display the active request (or “none”) and active iteration (or “none”) concisely in the menu.

- Out of scope: expanding the menu into additional pages/modes, adding extra features beyond the specified dynamic visibility + concise status.

- Out of scope: changing AIB lifecycle rules (single active request; single active iteration) beyond what is required to compute visibility.

- Implicitly in scope according to AIB rules: update any touched workflow documentation to keep behavior and docs consistent. (implicit rule - AIB framework)

## Domain Knowledge Essentials
- AIB request lifecycle: a workspace has at most one Active request registered in `.aib_memory/requests_register.md`, and each request has an `iterations.md` register with at most one Active iteration.

- Primary persona: developer/operator running `.aib_brain/run.bat` (or `.aib_brain/run.sh`) and using the interactive menu to execute lifecycle steps.

- Business objective: reduce friction and prevent invalid operations by showing only valid next actions and by ensuring state exists when the tool is run.

- Acceptance from a product/ops perspective: the menu must be shorter (no duplicated instructions) and safer (no accidental state overwrites), with a clear display of current active context.

## Technical Knowledge & Terms
- `.aib_memory/`: repository-local state folder that stores registries (`requests_register.md`, `references.md`) and request artifacts.

- “Initialize” (AIB memory initialization): creation of `.aib_memory/` structure plus seeding default docs/registries via `.aib_brain/tools/initialize.py`.

- “Dynamic menu”: the list of visible actions changes based on current state (presence of active request and active iteration).

- “Auto-discovered scripts”: `menu.py` scans `.aib_brain/tools/*.py` and auto-adds them to `menu_config.json` if missing.

- “Idempotence” (in this context): startup should not mutate existing `.aib_memory/` content and should lead to stable menu behavior given the same state.

## Assumptions
- Assumption A1: “Check for existence of `.aib_memory/`” means directory existence only; if the directory exists, the system must not attempt to heal missing files.
  - Rationale: the request explicitly uses the folder existence as the trigger and says “otherwise don’t change it”.
  - Risk if false: users may expect repair behavior when the folder exists but key seed files are missing/corrupted.
  - Falsification method: confirm with stakeholder whether “initialized” is folder-only or “folder OR key files missing”.

- Assumption A2: Implementing the auto-init check inside `.aib_brain/tools/menu.py` is acceptable as fulfilling “should happen automatically when `run.bat` is executed”.
  - Rationale: `run.bat` always executes `menu.py`; placing the check at the start of `menu.py` makes it automatic for both Windows and Linux/macOS launchers.
  - Risk if false: stakeholders may require the logic to live strictly in `run.bat` (and separately in `run.sh`).
  - Falsification method: confirm whether the acceptance criteria is “on menu startup” or “in launcher scripts specifically”.

- Assumption A3: Dynamic menu rules apply at minimum to the lifecycle actions (create/close request, create/close iteration) and do not require gating every auto-discovered action.
  - Rationale: the request explicitly calls out those lifecycle actions; gating every tool may add unintended complexity.
  - Risk if false: the menu may still show other actions that are invalid without an active request/iteration.
  - Falsification method: inventory current tools and confirm which actions must be hidden in each state.

- Assumption A4: The menu may compute “active request” and “active iteration” solely from `.aib_memory/requests_register.md` and the active request’s `iterations.md`.
  - Rationale: those are the documented registries and the apparent source of truth for lifecycle scripts.
  - Risk if false: the menu could display misleading status if other state sources exist.
  - Falsification method: scan lifecycle scripts for any additional state locations and validate single-source-of-truth.

- Assumption A5: The two instruction blocks provided in the request must be preserved verbatim in `.aib_brain/README.md`.
  - Rationale: the request supplies exact text blocks and states they “should be described in README.md”.
  - Risk if false: exact text may not be required and could be simplified, but simplification may be rejected if “verbatim” was intended.
  - Falsification method: confirm whether exact wording is required or equivalent wording is acceptable.

- Assumption A6: The dynamic menu can renumber visible actions and remain acceptable as long as numeric shortcuts remain consistent within the current view.
  - Rationale: `menu.py` normalizes IDs to 1..N and uses single-digit shortcuts; hiding actions necessarily affects numbering.
  - Risk if false: stakeholders may require stable action numbers regardless of visibility.
  - Falsification method: confirm whether stable IDs across states are required.

## Impact Assessment
### Affected Components / Areas
- `.aib_brain/tools/menu.py` (banner text, visibility logic, active state display, startup initialization check).

- `.aib_brain/tools/menu_config.json` (removal of explicit initialize action; or marking it hidden/unused).

- `.aib_brain/tools/initialize.py` (may remain unchanged if startup check is folder-only; otherwise may need idempotence safeguards).

- `.aib_brain/run.bat` and `.aib_brain/run.sh` (optional if auto-init is implemented in `menu.py`; otherwise must be updated).

- `.aib_brain/README.md` (must contain the removed instruction blocks).

### Change Type and Dependencies
- `.aib_brain/tools/menu.py`
  - Change type: modify
  - Dependencies: depends on `.aib_memory` state (exists? active request? active iteration?) and on the registry formats.
  - Sequencing implications: state detection must occur before rendering and before action selection; auto-init (if needed) must occur before reading registries.

- `.aib_brain/tools/menu_config.json`
  - Change type: modify
  - Dependencies: loaded/rewritten by `menu.py`; must stay valid JSON.
  - Sequencing implications: if config schema is extended (e.g., visibility metadata), `menu.py` must handle missing fields gracefully.

- `.aib_brain/tools/initialize.py`
  - Change type: none or modify
  - Dependencies: uses shared helpers from `common.py` and seeds `.aib_memory` registries.
  - Sequencing implications: MUST NOT run when `.aib_memory/` exists, unless requirements are expanded to allow “repair”.

### Domain Impacts
- DOMAIN (ARCH): No impact detected.

- DOMAIN (CMP): No impact detected.

- DOMAIN (DATA): No impact detected.

- DOMAIN (DEV): Impact detected — developer workflow via startup/menu behavior changes.

- DOMAIN (DSR): No impact detected.

- DOMAIN (FNL): No impact detected.

- DOMAIN (KNW): No impact detected.

- DOMAIN (RQT): No impact detected.

- DOMAIN (OBS): No impact detected (unless logging behavior is extended).

- DOMAIN (OPR): Impact detected — operational usability of launching and selecting actions.

- DOMAIN (SEC): No impact detected (no credentials/secrets handling changes implied).

### Constraints
- Must not modify an existing `.aib_memory/` directory (request requirement).

- Must remove the two instruction blocks from the menu UI and ensure they exist in `.aib_brain/README.md`.

- Must keep menu behavior deterministic and user-friendly (single-digit shortcuts, predictable selection).

- Must not introduce secrets, tokens, or sensitive PII into `.aib_memory` artifacts.

### Required Documentation Updates
- ARCH-01 - High-level architecture
  Required update? NO
  Reason: tooling/launcher change only.

- RQT-02 - Requirements document
  Required update? NO
  Reason: product requirements are not changed; this is internal tooling UX.

- OBS-01 - Logging
  Required update? NO
  Reason: no logging requirement changes are requested.

- SEC-01 - Access management
  Required update? NO
  Reason: no access/security mechanism changes are requested.

### Decision Points
- Decision D1: What constitutes “initialized” for auto-init?
  - Option 1: Folder-only check (`.aib_memory/` exists => do nothing).
    - Implications: strict compliance with “otherwise don’t change it”; does not self-heal partial state.
    - Recommended: YES (matches the explicit constraint and minimizes risk of unintended changes).
  - Option 2: Folder + key-file repair (if folder exists but key files missing, seed missing only).
    - Implications: more robust; may violate “don’t change it” unless explicitly allowed.
    - Recommended: Only if stakeholder confirms.

- Decision D2: Where to implement the auto-init check?
  - Option 1: In `menu.py`.
    - Implications: satisfies `run.bat` and `run.sh` without duplicating logic; single source of truth.
    - Recommended: YES.
  - Option 2: In both launchers (`run.bat` + `run.sh`).
    - Implications: shell-specific branching; risk of drift across OS.
    - Recommended: Only if stakeholder requires launcher-only logic.

- Decision D3: How to implement “dynamic menu” visibility?
  - Option 1: Hard-code visibility rules in `menu.py` for the lifecycle actions.
    - Implications: smallest change; less config complexity.
    - Recommended: YES (MVP).
  - Option 2: Extend `menu_config.json` schema with `visibility_conditions` per action.
    - Implications: scalable; requires schema parsing/validation and defaults for auto-discovered scripts.
    - Recommended: Consider if many actions will need gating.

- Decision D4: What state combinations must be supported explicitly?
  - Option 1: Gate only on “active request exists” and “active iteration exists”.
    - Implications: directly matches request examples.
    - Recommended: YES.
  - Option 2: Add additional states (e.g., “memory missing”, “register malformed”).
    - Implications: better robustness; adds error-handling policy decisions.
    - Recommended: Only if required by stakeholders.

## Research Plan and Findings
- Methodology used:
  - Review request artifacts: `.aib_memory/requests/R-20260321-2314-issue-23/request.md` and `iterations.md`.
  - Conventions review: analysis + request + questionnaire conventions.
  - Repository scan: `.aib_brain/run.bat`, `.aib_brain/run.sh`, `.aib_brain/tools/menu.py`, `.aib_brain/tools/menu_config.json`, `.aib_brain/tools/initialize.py`, `.aib_brain/README.md`.
  - Product docs scan: all `product-doc` files listed in `.aib_memory/references.md`.

- Evidence summary (what was found and why it matters):
  - `run.bat` and `run.sh` both invoke `menu.py` -> placing auto-init in `menu.py` covers both launchers.
  - `menu.py` currently prints the instruction blocks in its ASCII banner -> these must be removed from menu output.
  - `menu_config.json` includes an explicit “Initialize AIB memory” action -> conflicts with “no need of menu entry”.
  - `initialize.py` always writes seed registries -> reinforces the need for a strict guard (do not run if `.aib_memory/` exists).
  - Product-doc files are seeded placeholders -> they do not currently constrain this tooling change beyond general domain coverage.

- Gaps and unknowns (unverified):
  - Whether “initialized” is folder-only or includes “repair missing key files”.
  - Whether dynamic visibility should apply beyond the lifecycle actions to additional auto-discovered scripts.
  - Exact expected display format for active request/iteration (full folder name vs request ID only).

- Proposed validation actions:
  - State-matrix test: verify visible actions and displayed status for (a) no `.aib_memory`, (b) `.aib_memory` exists but no active request, (c) active request with active iteration, (d) active request with no active iteration.
  - Regression test: ensure `initialize.py` is never invoked automatically when `.aib_memory/` exists.

- Evidence log (evidence -> implication):
  - `menu.py` prints usage instructions -> move these instructions to `.aib_brain/README.md` and keep menu concise.
  - `menu.py` normalizes action IDs -> dynamic visibility will change numbering unless stable-ID design is adopted.
  - `initialize.py` overwrites seed files -> only safe to auto-run when `.aib_memory/` is absent.

## Rewrite Proposal of the Request
```md
## Goal
Improve AI Builder startup and the interactive command menu so it is self-initializing (when needed) and state-aware.

## Background
The current menu is static, includes usage instructions in the UI, and requires manual initialization of `.aib_memory`, which can be forgotten.

## Scope
- Automatic initialization on launch:
  - When launching the menu via `.aib_brain/run.bat` or `.aib_brain/run.sh`, automatically check whether `.aib_memory/` exists.
  - If `.aib_memory/` does not exist, initialize it (create `.aib_memory` and seed default registries/docs).
  - If `.aib_memory/` exists, do not modify any files under it.
  - Remove the “Initialize AIB memory” action from the interactive menu.

- Dynamic menu:
  - If there is no active request: show “Create request” and hide “Close request”, “Create iteration”, “Close iteration”.
  - If there is an active request: hide “Create request” and show “Close request”.
  - If there is no active iteration: hide “Close iteration” and show “Create iteration”.
  - If there is an active iteration: hide “Create iteration” and show “Close iteration”.

- Menu content cleanup:
  - Remove these blocks from the menu UI and include them in `.aib_brain/README.md`:

AI Builder terminal command menu
Launch with .aib_brain/run.bat (Windows) or .aib_brain/run.sh (Linux/macOS).
Use Up/Down arrows + Enter, or press the action number directly.
Press Q to quit from the menu.

AI Builder
Command menu for .aib_brain/tools scripts (launchers in .aib_brain)

- Active state display:
  - Display active request ID (or “No active request”).
  - Display active iteration ID for that request (or “No active iteration”).

## Out of scope
- No new menu pages, filters, or UI modes beyond dynamic visibility and status display.
- No changes to request/iteration lifecycle rules beyond computing visibility.

## Constraints
- Do not modify an existing `.aib_memory/` folder.

## Success criteria
- Running `.aib_brain/run.bat` (or `.aib_brain/run.sh`) in a workspace with no `.aib_memory/` creates `.aib_memory/` and opens the menu successfully.
- Running the launcher when `.aib_memory/` already exists does not modify any `.aib_memory` contents.
- The menu shows only valid next actions based on active request/iteration state.
- The menu does not display the two instruction blocks, and `.aib_brain/README.md` contains them.
- The menu displays active request and iteration concisely.
```

## Solution Options
- Option A (Recommended): Implement auto-init + state detection + action filtering in `menu.py`
  - Overview: At startup, `menu.py` checks for `.aib_memory/` existence and invokes initialization only if missing; then it computes active request/iteration and filters the lifecycle actions accordingly.
  - Benefits: single source of truth across `run.bat` and `run.sh`; minimal config changes; easy to test.
  - Trade-offs: some logic is hard-coded; auto-discovered tools may still appear unless explicitly gated.
  - Constraints: must not mutate existing `.aib_memory`.
  - Risks: mis-detection of active request/iteration if registry parsing is incorrect.
  - Expected effort: Medium.
  - Acceptance-test ideas: state-matrix test for visibility + `.aib_memory` no-mutation assertion.

- Option B: Extend `menu_config.json` with explicit visibility metadata
  - Overview: Add schema fields like `requires_active_request`, `requires_active_iteration`, etc., and evaluate them generically in `menu.py`.
  - Benefits: scalable for more actions; configuration-driven.
  - Trade-offs: schema complexity and validation; migration for existing config; undefined behavior for auto-discovered scripts.
  - Constraints: must keep config compatible and deterministic.
  - Risks: invalid config breaks menu or hides needed actions.
  - Expected effort: Medium to High.
  - Acceptance-test ideas: schema validation test + state-based render snapshots.

## Affected Documentation
| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| — | No affected documents identified at this stage. | — | The change is limited to `.aib_brain` tooling and README, not product-doc content. |

## Operational & Documentation Implications
- Runbooks: update any “first run” instructions to reflect that initialization is automatic when `.aib_memory` is missing.

- Monitoring/observability: no new logging requirements identified; avoid adding verbose logs to the interactive menu.

- Documentation artifacts:
  - `.aib_brain/README.md` must include the two instruction blocks (and the menu must stop printing them).
  - Ensure any references to “Initialize once” in docs are updated to reflect the new behavior (if currently misleading).

## Risks
- Risk R1: Auto-init accidentally runs when `.aib_memory/` exists and overwrites seeded files.
  - Probability: Medium
  - Impact: High
  - Mitigation: guard strictly on directory existence; add explicit “do nothing if exists” path; add tests/spike to validate no writes.
  - Owner (role): Maintainer

- Risk R2: Dynamic filtering leads to confusing action numbering or hides necessary actions.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: define clear visibility rules; ensure visible list is always coherent; consider stable labels/ordering; validate with state-matrix.
  - Owner (role): Maintainer

- Risk R3: Active request/iteration detection is incorrect due to registry format edge cases.
  - Probability: Low
  - Impact: Medium
  - Mitigation: implement robust parsing with explicit error messages; treat parse errors as “unknown state” and fall back to safe minimal menu.
  - Owner (role): Developer/operator

## Open Questions & Next Actions
1. Confirm the exact meaning of “initialized” (folder-only vs key-file repair).
   - Owner (role): Product owner / Maintainer
   - Due date / trigger: Before implementation of auto-init
   - Resolution path: Answer iteration `02` questionnaire QID-AT-001

2. Confirm whether dynamic visibility must apply only to lifecycle actions or to additional auto-discovered tools.
   - Owner (role): Maintainer
   - Due date / trigger: Before implementing dynamic filtering
   - Resolution path: Answer iteration `02` questionnaire QID-AT-003

3. Confirm whether instruction blocks must be reproduced verbatim in `.aib_brain/README.md`.
   - Owner (role): Requester
   - Due date / trigger: Before editing README/menu banner
   - Resolution path: Answer iteration `02` questionnaire QID-BF-002

4. Define the expected active-status display format (what identifiers to show).
   - Owner (role): Requester
   - Due date / trigger: Before implementing status display
   - Resolution path: Answer iteration `02` questionnaire QID-BF-001

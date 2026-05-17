## Executive Summary

- **Request ID:** R-20260426-1458

- **Title:** Keep active request files in .aib_memory until implemented

- **High-level purpose:** Change the file-placement strategy for three active-request artifacts — `request.md`, `analysis.md`, and `UAT_scenarios.md` — so they reside directly at `.aib_memory/` root while a request is active, and are moved to the request subfolder immediately before the request is closed (post-implementation). All other AIB functionality remains unchanged.

- **Scope summary (re-run update):** Two prompt files (`aib-analysis.md`, `aib-implement.md`), two convention files (`analysis-convention.md`, `request-convention.md`), and `close-request.py` require targeted updates. A new Python tool script (`move-request-artifacts.py`) must be created to perform the deterministic move. `context.md` must be regenerated.

- **Key design decisions resolved in this re-run:** Q001 (close-without-implement orphan gap) resolved — Option B adopted: `close-request.py` invokes the move script before marking the request Closed, ensuring artifacts are always relocated regardless of whether `aib-implement.md` was used. User input amendments revised A2 (dedicated Python move script replaces prompt-level move instructions) and A4 (`close-request.py` handles the move as a safety net, consistent with Q001 Option B).

- **request.md updates in this re-run:** `## Assumptions` (A2 and A4 revised; A6 added), `## Plan` (Task 2 added for move script; Task 4 added for `close-request.py` modification; tasks renumbered), `## Documentation`, `## Questions & Decisions` (Q001 applied and removed), `## Code and Asset Scan for Impacted Components`, and `## Internal Review of Request and Product Docs` fully replaced. `## Scope` and `## Out of scope` updated to apply Q001 resolution.


## Domain Knowledge Essentials

**AI Builder (AIB):** A minimal, file-first, model-agnostic framework for specification-driven development. It manages structured work items (requests) and automates release bookkeeping through a combination of Markdown prompt files, Python tool scripts, and GitHub Actions CI.

**Request:** A bounded unit of work described in `request.md`. Exactly one request may be Active at any time; all others are Closed.

**Active request:** The single request in `state = Active` in `.aib_memory/requests_register.md`. All analysis and implementation work is scoped to this request.

**Request folder:** A dedicated subdirectory under `.aib_memory/requests/` named `<request_id>-<title-slug>`. It is the long-term archival home for all artifacts belonging to a request.

**`.aib_memory/` root:** The top-level workspace-state directory. Currently houses registers, `context.md`, `input.md`, and `instructions.md`. This request proposes adding temporary active-request artifacts here.

**Developer ergonomics:** The ease with which a developer navigates, edits, and references files during active work. Placing working files at `.aib_memory/` root reduces the number of folder-level navigations needed compared to `.aib_memory/requests/<request-folder>/`.

**Impacted roles/personas:**
- Developer — the primary beneficiary; works with `request.md` and `analysis.md` frequently during a request.
- AI Automation Agent — must write artifacts to the new locations and move them on implementation completion.
- AIB Maintainer — must update convention files to reflect the two-phase location rule.

**Business processes touched:**
- Communicate user intent (input.md → auto-request creation → analysis → implement)
- Execute analysis workflow
- Execute implement workflow


## Technical Knowledge & Terms

**`aib-analysis.md`:** The primary analysis prompt. Currently writes `request.md`, `analysis.md`, and `UAT_scenarios.md` to the request subfolder. After this change, writes them to `.aib_memory/` root.

**`aib-implement.md`:** The implementation prompt. Currently reads `request.md` from `.aib_memory/requests/<request-folder>/request.md`. After this change, reads from `.aib_memory/request.md` during active implementation, and moves all three artifacts to the request subfolder before invoking `close-request.py`.

**`analysis-convention.md`:** Normative convention for the structure and location of `analysis.md`. Section 3 (File Naming & Location) specifies `.aib_memory/requests/<request-folder>/analysis.md` as the target — this must be updated to a two-phase rule.

**`request-convention.md`:** Normative convention for `request.md`. The File Location & Naming section similarly specifies `.aib_memory/requests/` as the home — must be updated.

**`context.md`:** The synthesized product knowledge artifact, fully replaced by `aib-context.md` on each execution. Component Map entries for "Request Artifacts" and the "aib-analysis.md" prompt description must be updated.

**Two-phase file placement:** A design pattern where working files reside in a scratch/active area during active use and are relocated to a durable archive area upon completion. Analogous to Git's staging area / commit model.

**`close-request.py`:** Python script that marks the Active request as Closed in the register and resets `input.md`. Updated by this request to invoke `move-request-artifacts.py` before marking the request Closed, ensuring artifact files are always relocated even when `aib-implement.md` is not used.

**`move-request-artifacts.py`:** A NEW Python tool script to be created in `.aib_brain/tools/`. Performs the deterministic, idempotent move of `request.md`, `analysis.md`, and `UAT_scenarios.md` from `.aib_memory/` root to the active request's subfolder. Uses `shutil.move` with `Path.exists()` pre-check for idempotency; silently skips files not present at source.

**Move operation:** A filesystem rename/copy-delete that relocates a file from source to destination. Implemented by the new `move-request-artifacts.py` script using Python standard library (`shutil.move`, `pathlib.Path`). Not implemented via prompt instructions — using a dedicated script ensures deterministic, model-agnostic execution.

**Idempotency:** The property that running an operation multiple times produces the same outcome as running it once. `move-request-artifacts.py` must be idempotent — if called after files are already moved, it exits cleanly without error (`source.exists()` returns False; `shutil.move` is skipped).

**Files Read (evidence log):**
- `.aib_memory/context.md` → confirmed current file-placement behavior, FR-003, FR-004, ADR-0003.
- `.aib_brain/Concepts.md` → confirmed folder structure conventions, request lifecycle model.
- `.aib_brain/conventions/analysis-convention.md` → confirmed Section 3 specifies request-folder location.
- `.aib_brain/conventions/request-convention.md` → confirmed File Location & Naming section specifies request-folder location.
- `.aib_memory/references.md` → confirmed two product-doc entries; context.md has edit_allowed=Y.
- `tests/test_lifecycle_e2e.py` → confirmed tests check request folder structure but do NOT check `request.md` or `analysis.md` presence (they are AI-generated, not script-seeded).


## Research Results

**Pattern scan — organizational standards and prior similar solutions:**

- All prior requests in this workspace have generated `request.md` and `analysis.md` inside the request subfolder. No prior request altered this pattern.

- The `aib-analysis.md` prompt consistently references `<request-folder>/request.md` and `<request-folder>/analysis.md` throughout its instructions. These references must be audited and updated holistically to avoid partial rewrites that introduce inconsistent path resolution.

- The test suite (`tests/`) contains no automated assertions for the presence of `request.md` or `analysis.md` at specific paths within request folders (those are AI-generated artifacts not produced by Python scripts). New tests would need to be written as integration tests that simulate the two-phase placement behavior.

- `tests/test_lifecycle_e2e.py` already asserts that `create-request.py` does NOT write `request.md` into the request folder — which aligns with the proposed change (the folder starts empty; `request.md` appears only when analysis runs, now at `.aib_memory/` root).

- No tooling script (`create-request.py`, `close-request.py`, `initialize.py`) currently touches `request.md` or `analysis.md` at path-specific locations. However, per Q001 Option B resolution and user input amendments, `close-request.py` must be updated to invoke a new move script before closing. A new script `move-request-artifacts.py` must be created in `.aib_brain/tools/`.


## External Benchmarking

**Git staging area pattern (working copy → committed state):**
- Git separates the working tree (where files are actively edited) from the object store (permanent history). Files exist in the working tree during active development; they are "committed" (archived) only when explicitly staged and committed.
- Applicability: The proposed two-phase placement mirrors this pattern — `.aib_memory/` root acts as the "working tree" for active artifacts, and the request subfolder acts as the "commit" (archived state). This is a well-established ergonomic pattern.
- Assessment: Adopt. The analogy supports the design rationale and provides a mental model for developers.

**VS Code "active file" surface patterns:**
- Many VS Code extensions surface "current working file" references at a top-level location (e.g., the `.vscode/` directory contains only active/current settings, while historical settings are archived per-project). This reduces navigation depth for frequently accessed files.
- Applicability: Directly analogous to the proposed change — placing active artifacts at `.aib_memory/` root so they appear prominently in the file tree during active development.
- Assessment: Adopt the rationale; no specific code pattern to copy.

**Monorepo "workspace root scratch files" pattern:**
- Large monorepos (e.g., Google Bazel, Nx) often place build-generation artifacts and working state at repository root level (e.g., `.bazel/`, `.nx/`) during active builds, archiving them to history after completion.
- Applicability: Loose analogy — the AIB workspace is much smaller, but the principle of "active working state at root → archived state in dedicated subfolder" is consistent.
- Assessment: Confirms the design direction; no specific adoption needed.

**Separation of concerns in cleanup scripts (DevOps tooling):**
- Tools like `clean` targets in Makefiles and `post_install` hooks in packaging systems (pip, npm) separate the "do the work" step from the "clean up after" step into distinct, independently testable operations rather than embedding cleanup inline in the main operation.
- Applicability: Directly applicable — the decision to create a dedicated `move-request-artifacts.py` script rather than embedding move logic inside `close-request.py` or relying on prompt instructions follows this principle. A dedicated script is independently testable, reusable across both callers, and free from AI non-determinism risk.
- Assessment: Adopted. Validates the revised A2 design decision.


## Minimal Spikes and Experiments

**Spike: Path resolution in aib-analysis.md**

- Hypothesis: The path string `.aib_memory/requests/<request-folder>/request.md` appears multiple times in `aib-analysis.md` and must be globally replaced with `.aib_memory/request.md`.
- Approach: Read `aib-analysis.md` fully and count occurrences of file path patterns targeting request subfolder artifacts.
- Outcome: `aib-analysis.md` references request subfolder paths extensively: in the Inputs section, in the Auto-Request Creation Branch (step 5: "Generate `request.md` in `<request-folder>/`"), in Part 1 output description, in Part 2 output sections, and in the final step (reset `input.md`). All occurrences must be updated.
- Conclusion: Path changes in `aib-analysis.md` are a textual find-and-replace across multiple sections; the change is well-bounded but requires careful enumeration to avoid missing occurrences.

**Spike: Impact on close-request.py and the move operation**

- Hypothesis: `close-request.py` must be updated to invoke the move script before marking the request Closed, to handle the close-without-implement scenario (Q001 Option B).
- Approach: Read `close-request.py` source in full; identified that it calls `update_requests_register` and then resets `input.md`. No artifact file paths are in its current logic.
- Outcome: The move invocation must be added before `target[col["state"]] = CLOSED`. The call must be guarded so that a move failure does not prevent close from completing — a stuck close would leave the register in an inconsistent Active state.
- Conclusion: `close-request.py` modification is scoped and contained; a single insertion point before the state update line. The guard strategy (try/except or subprocess with check=False) must be chosen during implementation.

**Spike: Idempotency of shutil.move across platforms**

- Hypothesis: `shutil.move(src, dst)` can be called twice safely when the source has already been moved (i.e., source no longer exists).
- Approach: Reviewed Python 3.10+ standard library documentation for `shutil.move` behavior on a missing source path.
- Outcome: `shutil.move` raises `FileNotFoundError` when the source path does not exist. A bare call is NOT idempotent by itself.
- Conclusion: `move-request-artifacts.py` must wrap each move in an `if source.exists():` guard before calling `shutil.move`. This one-line guard makes the script fully idempotent at zero added complexity.


## AI Copilot Suggestions

**Observation 1 — Dedicated move script is the correct engineering choice (design quality)**
The revision from "prompt-level move instructions" to a dedicated Python script for artifact relocation is architecturally superior. Prompt instructions are AI-interpreted and non-deterministic across model versions; a Python script in `.aib_brain/tools/` executes deterministically, produces testable output, and is reusable across both `aib-implement.md` and `close-request.py` without duplication. The user's amendment to A2 is well-founded and materially improves the robustness of the design.
- Suggestion: Keep `move-request-artifacts.py` minimal — 40–60 lines of standard-library Python. Do not add configuration flags or extensibility hooks beyond the three target files and the active-request folder.

**Observation 2 — close-request.py modification needs a guard for graceful failure (implementation risk)**
Adding the move script call inside `close-request.py` introduces a new failure mode: if the move script raises an unexpected error (e.g., permission denied, or the script absent on an older installation), the close operation must still complete — a stuck close leaves the register in an inconsistent Active state. The move call must be guarded to fail gracefully.
- Suggestion: In `close-request.py`, invoke the move operation via a direct Python function import (not subprocess) wrapped in a `try/except Exception` block that logs a warning but does not re-raise. The close operation must always reach `update_requests_register` and the `input.md` reset step regardless of move outcome.

**Observation 3 — Concepts.md documents incorrect artifact locations after implementation (maintainability gap)**
`Concepts.md` (REF-0002, `edit_allowed = N`) currently states that `request.md` and `analysis.md` live in the request subfolder. After this request is implemented, `Concepts.md` will describe the old, pre-change behavior. Since `edit_allowed = N`, this request's implementation cannot update it.
- Suggestion: After implementation, the AIB Maintainer should open a follow-up request to update `Concepts.md` (or temporarily set `edit_allowed = Y` in `references.md`). The discrepancy is flagged in the Internal Review section of `request.md`.

**Observation 4 — Scope is well-sized; no scope creep detected**
With Q001 resolved and the move script added, the scope is complete and appropriately bounded. The addition of `close-request.py` modification and `move-request-artifacts.py` creation is necessary to achieve the stated goal without creating orphaned state — it is not scope creep, but a required fix surfaced during analysis. The plan is executable in one iteration.
- Suggestion: Resist adding any behavior to the move script beyond the three target files and the active-request folder. Configuration-driven or extensible move logic would be over-engineering at this scale.


## Testing

- T1 — Move script moves request.md to request subfolder: Place `request.md` at `.aib_memory/request.md` in a test workspace with one Active request. Run `python .aib_brain/tools/move-request-artifacts.py --workspace .`. Expected outcome: `request.md` present at `<request-folder>/request.md`; absent from `.aib_memory/`.

- T2 — Move script moves analysis.md to request subfolder: Same setup; place `analysis.md` at `.aib_memory/analysis.md`. Run move script. Expected outcome: `analysis.md` present at `<request-folder>/analysis.md`; absent from `.aib_memory/`.

- T3 — Move script moves UAT_scenarios.md when present: Place `UAT_scenarios.md` at `.aib_memory/UAT_scenarios.md`. Run move script. Expected outcome: `UAT_scenarios.md` present at `<request-folder>/UAT_scenarios.md`; absent from `.aib_memory/` root.

- T4 — Move script skips missing UAT_scenarios.md: Run move script when `UAT_scenarios.md` is absent from `.aib_memory/`. Expected outcome: Exit code 0; no exception raised; other present files moved successfully.

- T5 — Move script is idempotent: Run move script twice on the same workspace (second run has no files at `.aib_memory/` root). Expected outcome: Second run completes with exit code 0; no errors raised.

- T6 — close-request.py moves artifacts before closing: Place `request.md` and `analysis.md` at `.aib_memory/` root; run `python .aib_brain/tools/close-request.py --workspace .`. Expected outcome: Files moved to `<request-folder>/`; request state = `Closed` in `requests_register.md`; `input.md` reset to seed template.

- T7 — close-request.py closes successfully when no artifacts at root: Run `close-request.py` when `.aib_memory/` root has no artifact files. Expected outcome: Request marked `Closed`; `input.md` reset; no errors raised.

- T8 — All existing automated tests pass: Run `pytest tests/` against the updated codebase. Expected outcome: Exit code 0; no regressions.

- T9 (UAT) — Analysis writes artifacts to .aib_memory/ root: See UAT_scenarios.md — UAT-01.

- T10 (UAT) — Implementation invokes move script before close: See UAT_scenarios.md — UAT-02.

- T11 (UAT) — Direct close moves artifacts before closing: See UAT_scenarios.md — UAT-03.


## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The two-phase file placement pattern is architecturally sound and maps cleanly onto the single-Active-request invariant: at most one `request.md` and one `analysis.md` can reside at `.aib_memory/` root at any time without collision. With Q001 resolved (Option B adopted), the move is now performed by a dedicated Python script (`move-request-artifacts.py`) rather than prompt instructions — the correct choice for determinism and auditability. Both `aib-implement.md` and `close-request.py` invoke this script, closing all known artifact-orphan scenarios.

- The convention files must be updated before any new analysis run, not after, to preserve normative consistency.
- The close-without-implement path is now architecturally handled: `close-request.py` invokes the move script as a safety net before marking the request Closed.
- The move call in `close-request.py` must be guarded so that a script failure does not prevent close from completing — the close must always succeed to preserve register consistency.
- ADR-0003 (`.aib_brain/` not written by tool scripts at runtime) is preserved: the move script writes to `.aib_memory/`, not to `.aib_brain/`.
- The change is reversible: path strings can be reverted and the script removed if the approach proves problematic.

### Product Owner

The request delivers a clear ergonomic improvement: developers no longer need to navigate into a timestamped subfolder to access their working files. The business value is modest but real for frequent users. Scope is well-bounded; success criteria are measurable.

- Acceptance criteria cover file existence before and after implementation — sufficient for validation.
- The "close without implement" gap should be resolved before implementation to avoid a confusing user experience.
- No regression risk to existing closed requests (their archived files are unaffected).
- The request does not introduce new features; it relocates existing file outputs.

### User

From a developer's perspective, having `request.md` and `analysis.md` immediately visible in `.aib_memory/` is a meaningful quality-of-life improvement. Currently, navigating to `R-20260426-1458-keep-active-request-files-in-aib-memory-until-implemented/` for every edit is friction that interrupts flow.

- The developer must be aware that `request.md` at `.aib_memory/` is the ACTIVE working copy — editing the version inside the request subfolder during an active request would be futile.
- After implementation, the developer should expect the files to no longer be at `.aib_memory/` root; accidental edits to stale root copies post-close are prevented by the move.
- If the developer abandons (closes without implement), they must understand the orphaned files scenario and manually clean up.

### Security Officer

The change modifies only file paths within a local filesystem workspace. No authentication, authorization, network, or cloud resources are affected. The `.aib_memory/` directory is already VCS-tracked and repo-local.

- No new attack surface introduced.
- No secrets, credentials, or sensitive data are moved.
- File access controls are unchanged (all files readable/writable by the repository owner).
- Risk: if `.aib_memory/request.md` is exposed in a shared repository, it may reveal work-in-progress intent. This is the same risk as the current design; the change does not increase exposure.

### Data Governance Officer

All artifacts (`request.md`, `analysis.md`, `UAT_scenarios.md`) are Internal engineering documentation with no PII or regulated data. Their classification and retention requirements are unchanged by this proposal.

- Data lineage: artifact provenance is unchanged — they are still generated from `input.md` and archived in the request subfolder after implementation.
- Retention: no change; closed request folders remain in VCS history indefinitely.
- The `.aib_memory/` root-level files during active requests are ephemeral; they do not represent a new data category requiring governance controls.
- No compliance impact identified.

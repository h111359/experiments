# Analysis: R-20260430-1550 — Add attachments folder for AIB input enrichment

## Executive Summary

- **Request ID:** R-20260430-1550

- **Title:** Add attachments folder for AIB input enrichment

- **Purpose:** Extend the AIB input channel by adding `.aib_memory/attachments/` as a staging area for supplementary files. This allows developers to provide binary files, screenshots, structured data, or large text content alongside `input.md` without embedding it directly in the text field.

- **Core change:** `initialize.py` seeds the `attachments/` directory on init; `aib-analysis.md` reads files from it as additional input; files are moved to `<request-folder>/inputs/` when input is archived; `close-request.py` gains a non-blocking warning if the folder is non-empty at close time.

- **Impact scope:** Narrow and contained. Three components are affected: `initialize.py` (one `mkdir` call), `aib-analysis.md` prompt (input-reading and archiving steps), and `close-request.py` (safety-net check). No data model changes. No new dependencies.

- **`request.md` updates made during this run:** `## Assumptions`, `## Plan`, `## Documentation`, `## Questions & Decisions`, `## Code and Asset Scan for Impacted Components`, and `## Internal Review of Request and Product Docs` were written.


## Domain Knowledge Essentials

**AIB Input Channel** — The file `.aib_memory/input.md` is the primary, ephemeral communication file between the developer and the AI agent. It carries developer intent for the current analysis run and is archived + reset by `aib-analysis.md` after processing.

**Staging area** — A temporary holding location for files that will be consumed and relocated by a subsequent automated process. In this context, `.aib_memory/attachments/` is a staging area: files placed there are moved to the request folder during analysis, leaving the staging area empty.

**Auto-request creation branch** — The code path in `aib-analysis.md` triggered when no Active request exists and `input.md` is non-empty. It auto-creates a request, archives `input.md` to `<request-folder>/inputs/`, and then proceeds with standard analysis.

**Input archiving** — The act of copying `input.md` content to `<request-folder>/inputs/input-archive-<timestamp>.md` before resetting `input.md` to the seed template. Preserves the developer's original intent for audit purposes.

**Seed (idempotent)** — `initialize.py` creates directories and files only if they do not already exist, making re-runs safe.

**Roles impacted:**
- Developer — places files in `attachments/` as additional input context.
- AI Automation Agent — reads `attachments/` as part of input before drafting analysis, then moves files.
- AIB Maintainer — may need to update `.gitignore` or VCS rules depending on the decision on VCS tracking.

**Business processes touched:**
- "Communicate user intent" workflow (developer writes `input.md` + places attachments, AI reads both).
- "Execute analysis workflow" (auto-request branch archives input including attachments).


## Technical Knowledge & Terms

**`initialize.py`** — Tool script that seeds `.aib_memory/` structure from `.aib_brain/` templates. Uses `Path.mkdir(parents=True, exist_ok=True)` for idempotent directory creation.

**`aib-analysis.md`** — Prompt file (not a Python script) that instructs the AI agent to perform analysis. It contains declarative steps the AI follows; changes here are textual additions to the prompt's procedure.

**`close-request.py`** — Tool script that marks a request Closed, invokes `move-request-artifacts.py` as a safety net, and resets `input.md`.

**`move-request-artifacts.py`** — Moves `request.md`, `analysis.md`, `UAT_scenarios.md` from `.aib_memory/` root to `<request-folder>/`. Does NOT handle `attachments/` content (that move happens during analysis archiving, earlier in the lifecycle).

**`shutil.move`** — Python standard library function for moving files/directories; handles cross-filesystem operations.

**`Path.iterdir()`** — Python standard library method to list files in a directory non-recursively (flat scan).

**VCS tracking** — Whether files are committed to Git. The staging `attachments/` folder may contain binary or sensitive files; its tracking status must be decided (see Q001).

**NFR-004** — Non-functional requirement mandating Python 3.10+ standard library only for tool scripts.

**Files Read:**
- `.aib_memory/context.md` — product documentation; source of architecture and FR/NFR facts.
- `.aib_brain/Concepts.md` — normative lifecycle rules.
- `.aib_brain/tools/initialize.py` — existing init logic for reference.
- `.aib_brain/tools/close-request.py` — existing close logic for safety-net pattern.
- `.aib_brain/tools/move-request-artifacts.py` — existing move logic; confirms it does NOT handle attachments.
- `.aib_brain/prompts/aib-implement.md` — confirms attachments are out of scope for implement.
- `.aib_brain/conventions/analysis-convention.md` and `request-convention.md` — normative structure rules.
- `.gitignore` — current VCS exclusion rules.
- `tests/test_initialize.py` — existing test patterns for `initialize.py`.


## Research Results

**Pattern scan against existing AIB conventions and prior solutions:**

- `initialize.py` already uses `Path.mkdir(parents=True, exist_ok=True)` for `requests/` and `logs/` subdirectories. The same pattern applies directly to `attachments/`. No new pattern is needed.

- The auto-request creation branch in `aib-analysis.md` already uses Python to create the `inputs/` subfolder and write the archive file (step 6 of the Auto-Request Creation Branch). Appending a loop that moves files from `attachments/` to `<request-folder>/inputs/` is a natural extension of this existing archiving step.

- `close-request.py` already contains a safety-net try/except for `move-request-artifacts.py`. The non-blocking warning for non-empty `attachments/` follows the same pattern: attempt a check, print a warning, but never block the close.

- No prior AIB request has addressed multi-modal input. This is the first time the input channel expands beyond text.

- The `logs/` directory is excluded from VCS via `.gitignore`; the `attachments/` directory follows a different lifecycle (staging, then moved), so its VCS treatment needs an explicit decision (Q001).


## External Benchmarking

**Git staging areas (index):** Git itself uses a staging area (index) to hold changes before they are committed. Files in `attachments/` behave analogously — they are staged input artifacts that are consumed and relocated by a downstream process. This pattern validates the staging-area approach as well-established.

- Takeaway: The staging area metaphor is sound. The key invariant (staging area is empty after consumption) mirrors Git's behavior after a commit.

- Applicability: High. Adopt the pattern directly.

**AI prompt-chaining input enrichment (LangChain, AutoGPT patterns):** AI workflow frameworks commonly support multi-modal input through a designated input directory (e.g., LangChain's `DirectoryLoader` scans a folder and passes all files as documents). AIB's approach is simpler: the AI agent reads files from `attachments/` at the start of the analysis step.

- Takeaway: Flat-folder scan with explicit file listing before AI processing is a well-established pattern. Recursive scanning is typically optional and adds complexity. Starting with flat-scan is the correct scoping decision.

- Applicability: High for the flat-scan default. Recursive scanning deferred to a future request.

**VS Code workspace context folders:** VS Code's context mechanism allows developers to drop files into a designated folder to enrich the AI context window. AIB's `attachments/` folder mirrors this pattern at the workflow level rather than the IDE level.

- Takeaway: Developer familiarity with "drop files in a folder to include them" is high. No UX explanation is needed beyond README documentation.

- Applicability: High. Validates the usability of the approach.


## Minimal Spikes and Experiments

**Spike: Idempotent `attachments/` directory creation in `initialize.py`**
- Hypothesis: Adding `(memory_root / "attachments").mkdir(parents=True, exist_ok=True)` to `_seed_memory` is sufficient to create the directory idempotently without breaking existing tests.
- Approach: Code review of `initialize.py` `_seed_memory` function; cross-reference with existing `requests/` and `logs/` directory creation calls.
- Outcome: The pattern `Path.mkdir(parents=True, exist_ok=True)` is already used twice in `_seed_memory` for `requests/` and `logs/`. Adding a third call for `attachments/` follows the exact same structure. No test breakage expected since `exist_ok=True` prevents errors on re-run.
- Conclusion: The change is trivially safe. No spike execution needed beyond code review.

**Spike: Move files from attachments to request folder using standard library**
- Hypothesis: `shutil.move` correctly moves all files from a flat directory to a destination directory with a single loop, without external dependencies.
- Approach: Reviewed `move-request-artifacts.py` which already uses `shutil.move(str(source), str(dest))`. The same call pattern works for any file, not just named artifacts.
- Outcome: Confirmed. A simple `for f in attachments_dir.iterdir(): shutil.move(str(f), str(dest_folder))` loop is sufficient.
- Conclusion: Implementation is straightforward. No additional libraries or patterns required.

**Spike: VCS impact of `attachments/` folder**
- Hypothesis: The `attachments/` folder may need a `.gitignore` entry or a `.gitkeep` file to function correctly in VCS.
- Approach: Reviewed current `.gitignore`; reviewed how `logs/` is handled (excluded via wildcard for log files, not the directory itself).
- Outcome: Currently no `.gitignore` entry for `attachments/`. An empty directory is not tracked by Git (requires `.gitkeep` to be VCS-visible). The VCS tracking policy depends on Q001.
- Conclusion: VCS strategy requires a user decision (Q001). The implementation MUST handle both outcomes.


## AI Copilot Suggestions

**Observation 1 — The "No changes" toggle path creates a spec conflict that must be resolved before implementation.**
The current `aib-analysis.md` spec states: "This branch produces exactly two file writes." Adding attachment moves would break this invariant. The user must decide (Q003) whether attachments are moved in the "No changes" path. If attachments are to be moved, the spec in `aib-analysis.md` must be explicitly updated to allow for additional file moves. Failing to update the spec would create a latent inconsistency that silently breaks on the next analysis re-run. Suggestion: resolve Q003 before implementing the "No changes" path behavior, and update the invariant statement in the prompt if the decision is to move attachments.

**Observation 2 — The flat-folder-only constraint is appropriate for this iteration but should be explicit in the prompt.**
The request scopes to flat-folder scanning only. This is the correct pragmatic scope. However, if the `attachments/` folder is not explicitly documented as flat-only in `aib-analysis.md`, future users or AI agents may attempt to place subdirectories in `attachments/` and expect them to be handled. Suggestion: add a one-line note in `aib-analysis.md` stating that only files at the root of `attachments/` are processed; subdirectories are ignored.

**Observation 3 — `close-request.py` safety-net warning is a good defensive addition but will fire only in error conditions.**
The non-blocking warning for non-empty `attachments/` at close time is good defensive programming. However, in normal workflow, `attachments/` will always be empty by the time `close-request.py` runs (files are moved during analysis). The warning will only fire when someone invokes `close-request.py` without having run analysis (e.g., directly closing a request with files still in `attachments/`). Suggestion: the warning message should explicitly state "files were not archived; consider running analysis first" to guide the developer.

**Observation 4 — Scope appears well-sized for the stated goal.**
The request scope is appropriately narrow. It touches three components (`initialize.py`, `aib-analysis.md`, `close-request.py`) with minimal code changes. The explicit out-of-scope items (recursive scanning, binary extraction, multi-request queuing) are the right deferrals. No scope creep risk identified.

**Observation 5 — The upgrade path in `initialize.py` must also create `attachments/`.**
`initialize.py --upgrade` calls `_seed_memory` after archiving and clearing the memory directory, so the `attachments/` directory will be re-created automatically if the single `mkdir` call is placed in `_seed_memory`. No separate upgrade-path handling is needed. Confirm this during implementation by tracing the `--upgrade` code path.


## Testing

- T1 — Initialize creates attachments dir: Run `initialize.py` on a fresh workspace; verify `.aib_memory/attachments/` directory exists. Expected outcome: directory is present after initialization exits with code 0.

- T2 — Initialize is idempotent for attachments dir: Run `initialize.py` twice on the same workspace; place a file in `attachments/` between runs; verify the file is not deleted on the second run. Expected outcome: `attachments/` and its content survive the re-run.

- T3 — Upgrade creates attachments dir: Run `initialize.py --upgrade` on a workspace that did not have `attachments/`; verify directory is created. Expected outcome: `attachments/` exists after upgrade.

- T4 — Analysis reads attachment files: Place a text file in `.aib_memory/attachments/` before running `aib-analysis.md`; verify the analysis output references or acknowledges the attachment. Expected outcome: analysis artifact or request.md contains evidence that the attachment was read (manual verification — see UAT_scenarios.md — UAT-01).

- T5 — Attachments moved to request folder on analysis: After `aib-analysis.md` completes the auto-request creation branch, verify all files from `.aib_memory/attachments/` are present in `<request-folder>/inputs/` and `attachments/` is empty. Expected outcome: files relocated; staging area empty.

- T6 — Close-request warns on non-empty attachments: Place a file in `.aib_memory/attachments/` and invoke `close-request.py` without prior analysis; verify a warning is printed to stdout and the close operation still completes. Expected outcome: exit code 0; warning message printed; request marked Closed.

- T7 — Test suite passes after changes: Run `pytest tests/` from the workspace root; verify all existing tests pass. Expected outcome: 0 failures, 0 errors.

- T8 — Re-run idempotency: Run `aib-analysis.md` twice on the same request with empty `attachments/`; verify second run does not fail or create duplicate files. Expected outcome: second run produces updated analysis artifacts without error.

See UAT_scenarios.md — UAT-01 for the manual scenario covering T4 (attachment file read acknowledgement by AI agent).


## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The change is architecturally minimal and well-bounded. It introduces a new directory in the `.aib_memory/` staging area with clear lifecycle semantics: created on init, consumed during analysis, empty after archiving. The separation of concerns is maintained: `move-request-artifacts.py` is not changed (it handles post-implementation artifact relocation); the new attachment move is scoped to the analysis archiving step, which is the correct lifecycle phase. The flat-scan constraint is the right default; recursive scanning can be added later without breaking the current design. The main architectural risk is VCS ambiguity (Q001): if the `attachments/` folder is not gitignored and developers commit binary files, repository size may grow unexpectedly.

- The staging-and-move lifecycle is well-established and easy to reason about.
- No new architectural components or data flows are introduced; the change is additive.
- The safety-net warning in `close-request.py` follows the existing defensive pattern from `move-request-artifacts.py`.
- Risk: VCS policy for the staging folder must be explicit to avoid inadvertent binary file commits.
- Risk: If `aib-analysis.md` fails mid-run after moving some but not all attachments, the staging area may be partially empty. This edge case is acceptable for v1 but worth documenting.

### Product Owner

The business value is clear: richer input context enables more accurate analysis without developer friction. The scope is appropriately incremental. Success criteria are specific and testable. The one concern is the "No changes" toggle path (Q003): the current spec invariant ("exactly two file writes") may need updating, and this could affect the guarantee developers rely on when using that toggle. Until Q003 is answered, the "No changes" path behavior is underspecified.

- High business value for developers who need to provide non-text context (screenshots, data samples).
- SC-1 through SC-6 are well-defined and cover the main use cases.
- Q001 (VCS tracking) and Q003 ("No changes" path) are open and block final acceptance criteria definition.
- The out-of-scope items are appropriate; recursive scanning and OCR would significantly expand effort.

### User

From a developer's perspective, the workflow becomes more natural: drop files in `attachments/`, write the request in `input.md`, and run analysis. The files are consumed automatically. No manual file path references are needed in `input.md` unless the developer wants to draw attention to a specific attachment. The main friction point is discoverability: developers must know the `attachments/` folder exists and is monitored. README or `aib-analysis.md` documentation is essential for adoption.

- The "drop files to include them" interaction model is intuitive and familiar from other tools.
- No new command or action is required from the developer.
- If `attachments/` is not mentioned in README or the menu, developers will not discover it.
- Risk: a developer may leave files in `attachments/` from a previous run if the folder is not cleared; the safety-net warning in `close-request.py` partially mitigates this.

### Security Officer

The `attachments/` folder introduces a new file ingestion surface. Files placed there are read by the AI agent as part of the analysis context. Risks are limited to the development workstation environment (AIB operates locally, not in a cloud service). No network exposure is introduced. The main concern is accidental inclusion of sensitive files (credentials, private keys) in the analysis context: since the AI agent reads all files in `attachments/`, a developer who inadvertently places a `.env` or private key file there would expose it to the AI context window.

- No network attack surface is added; this is a local file operation.
- The staging-to-request-folder move does not expose files externally.
- Risk: developers may inadvertently include sensitive files in `attachments/`. A README note warning against placing credential files there is recommended.
- If VCS tracking is enabled (Q001 answered "track"), sensitive files committed to VCS would be a higher-risk outcome. The gitignore option mitigates this.

### Data Governance Officer

Attachments moved to the request folder become part of the audit trail for the request. This is consistent with how `input-archive-*.md` is used. The data lineage is clear: `attachments/<file>` → `<request-folder>/inputs/<file>` (archived). No data is transmitted externally. The main governance concern is retention: request folders accumulate attachment files indefinitely unless a cleanup policy exists. For internal engineering documentation this is acceptable, but should be noted.

- Data lineage is clear and traceable (source → destination follows the archive step).
- No external data transmission; all operations are local file system.
- Attachment files become part of the request audit trail, which is consistent with existing `input-archive-*.md` behavior.
- Retention risk: if large binary attachments are included frequently, the repository size may grow significantly over time (amplified by VCS tracking if Q001 is resolved as "track").
- No PII classification changes are introduced; this is an engineering workflow tool.

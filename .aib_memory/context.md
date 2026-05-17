# Product Context

> **Auto-generated** by `aib-refresh-context.md` on 2026-05-17 23:55 +03:00.
> Framework definition assets (`.aib_brain/`) are excluded by design — see `.aib_brain/` for AIB framework internals.
> This document is a synthesis of product documentation and workspace sources. It is fully replaced on each execution.

## Product Identity

AI Builder (AIB) is a repository-local framework for specification-driven development workflows and release bookkeeping.

- Primary actors are AIB users, and AIB developers.

- AIB developer — owns `.aib_brain/` assets, enforces conventions, manages CI workflows.



## Domain Knowledge

AIB operates in the software engineering / internal tooling domain. It supports the following key business processes:

- **Initialize AIB workspace**: Seeds `.aib_memory/` registers, `context.md`, and `input.md` from `.aib_brain/` assets and archives the previous `.aib_memory/` content.

- **Communicate user intent**: Developer writes into `.aib_memory/input.md`; the AI agent reads it, auto-creates a request, archives the input, and resets the file.

- **Execute analysis workflow**: AI agent generates `plan.md` (auto-request branch) and/or `analysis.md` with 5 mandatory sections (Overview, Files Read During This Analysis Run, Input Interpretation, Research Results, Implementation Alternatives); updates `plan.md` with Plan and Decisions sections. The analysis prompt requires a mandatory Decision Fork Enumeration step and a `### Decision Points` heading/sub-heading list within `## Implementation Alternatives` of the analysis document. When multiple valid implementation choices exist, AI-generated Q-blocks are written to `input.md ## Questions` for developer review. The prompt includes an `## Execution Model Summary` section, a `## Global Constraints` section (GC-01 through GC-06), and a `## Failure Handling` section. Section 4 (Preflight) is organized into four labeled phases: Phase 1 (State Resolution), Phase 2 (Input Acquisition), Phase 3 (State Mutation), and Phase 4 (Context Enrichment). Section 7.3 is split into three sub-sections: 7.3.1 Decision Identification, 7.3.2 Decision Classification, and 7.3.3 Q-block Generation. Section 8 is split into three sub-sections: 8.1 Eligibility Check, 8.2 Finalize Script Invocation, and 8.3 Post-conditions. Section 4.8 (Answer Application Sub-flow) begins with an all-answered pre-check that halts execution when any Q-block is unanswered, leaving `input.md` unchanged.

- **Execute implement workflow**: AI agent applies request scope, updates product docs, creates/appends `implementation.md`, and auto-closes the request upon successful completion.

- **Release bookkeeping**: CI-automated version bump (auto-applies PATCH when head marker equals the base; accepts any manually pre-applied MINOR or MAJOR bump), per-version log creation, and `.aib_brain/` zip archive in `versions/` on pull request events targeting `main`.

Organizational units: Product Team (request lifecycle), AIB Maintainers (framework assets), Repository Contributors (read/write access gated by repository permissions).

External dependencies:

- GitHub — repository hosting and version control.

- GitHub Actions — CI runner for automated release bookkeeping.

No regulatory bodies or external data providers are identified. All artifacts are classified as Internal engineering documentation.

### Glossary

**ADR**: Architecture Decision Record — a document capturing a significant architectural choice, its rationale, and consequences.

**AI Builder**: Minimal, model-agnostic framework for specification-driven development in a repository workspace. Abbreviated AIB.

**AIB**: Abbreviation for AI Builder.

**Analysis**: A reasoning artifact (`analysis-<request_id>.md`) generated per request; also updates `plan-<request_id>.md` with Plan and Decisions sections.

**Auto-close**: Behavior whereby `aib-implement.md` invokes `close-request.py` automatically after successful implementation.

**Auto-request**: Behavior of `aib-analyze.md` whereby, when no Active request exists and `input.md` is non-empty, it auto-creates a request and generates `plan.md` from `input.md` content.

**Brain Folder**: Folder (`.aib_brain/`) containing reusable AIB assets: prompts, conventions, and tool scripts.

**CI**: Continuous Integration — automated pipeline that runs on pull request events.

**Convention File**: A file in `.aib_brain/conventions/` that defines the required structure and validation rules for a specific product doc or coding standard.

**Curated Change Log**: `logs/next_version_changes.md` — append-only Markdown bullet list maintained by the AI agent during implementation; preferred source of `Changes:` bullets in the next per-version release log; reset to empty by CI after incorporation.

**FR**: Functional Requirement.

**Implementation Log**: Request-scoped on-demand record of changes, tests, and outcomes (`implementation.md`); created from scratch by `aib-implement.md`.

**Input Archive**: File written by `aib-analyze.md` to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md` preserving the original `input.md` content for audit; MUST NOT be read by any prompt.

**input.md**: Ephemeral primary user-agent communication channel. Seeded by `initialize.py`; written by the developer; read and processed by `aib-analyze.md`; reset to seed template after processing.

**instructions.md**: Persistent workspace-level behavioral directives file located at `.aib_memory/instructions.md`. Read by every AIB prompt as the first step before executing its main logic. Free-form Markdown; no schema enforcement. If absent or empty, prompts proceed normally. Seeded as an empty file by `initialize.py`; editable directly by users. Currently populated with the curated-change-log directive instructing the agent to maintain `logs/next_version_changes.md`.

**Memory Folder**: Folder (`.aib_memory/`) containing workspace-specific artifacts: requests, registers, `context.md`, and `input.md`.

**NFR**: Non-Functional Requirement.

**PII**: Personally Identifiable Information.

**Product Doc**: A convention-governed documentation file (e.g., `context.md`); editable by automation when the active request authorises the change.

**Prompt Action**: A `.aib_brain/prompts/aib-*.md` file that defines the instructions an AI agent executes to produce a specific AIB artifact. Invoked directly in an AI coding interface; model-agnostic.

**Request**: Tracked unit of work with a stable request identifier (`R-YYYYMMDD-HHmi`) and lifecycle state (`Active` or `Closed`).

**SemVer**: Semantic Versioning, following the pattern MAJOR.MINOR.PATCH.

**SemVer Marker File**: A single empty file in `.aib_brain/` whose filename encodes `vMAJOR.MINOR.PATCH`; represents the active product version.

**SLO**: Service Level Objective.

**Tool Script**: A Python script in `.aib_brain/tools/` implementing a deterministic AIB action.

**User Guide**: Self-contained HTML file located at `.aib_brain/user_guide.html`; browser-viewable reference documentation for AIB users covering the full AIB workflow, prompt invocations, Q&A mechanism, workspace structure, and glossary. Requires no network connectivity to open.

**VCS**: Version Control System (Git in this workspace).

**Versioned Archive**: Zip file created by CI per version bump, stored in `versions/aib_brain_vX.Y.Z.zip`; committed to VCS; used for AIB installation.

**Workspace**: The repository root containing both the AIB brain folder and memory folder plus any product-specific code and configuration.

## Concepts

The following entries define the core conceptual principles and guiding philosophy of the AIB framework, sorted alphabetically.

**Determinism**: AIB workflows are designed to produce the same output given the same input, making every prompt action reproducible and verifiable.

**Fail-closed**: When a required resource (convention file, register state, or mandatory input) is missing or invalid, AIB halts with an explicit error rather than proceeding with partial or guessed output.

**File-first**: All state, configuration, and artifacts are represented as Markdown files in the repository; no database, cloud service, or runtime state is used.

**Separation of concerns**: Framework assets (`.aib_brain/`) and workspace-specific artifacts (`.aib_memory/`) are strictly segregated; tool scripts never write to the brain folder.

## Constraints & Assumptions

### Technical Constraints

- Exactly one Active request is permitted per workspace at any time.

- Automation must not modify files outside `.aib_memory/` and the curated `logs/next_version_changes.md` unless the active request explicitly authorises the change.

- Tool scripts require Python 3.10+ with standard library only.

- `git` must be available on PATH in CI for release bookkeeping.

- `GITHUB_TOKEN` must have Read and Write permissions for marker rotation commit.

- Forked repository PRs are explicitly excluded from CI automation.

- `.aib_brain/` must never be modified by tool scripts; it is replaced only by AIB Maintainers during framework upgrades.

- `inputs/input-archive-*.md` files MUST NOT be read by any AIB prompt.

### Organizational Constraints

- All artifacts are treated as Internal engineering documentation.

- No secrets, credentials, or personal data should be stored in repository artifacts.

- Changes to `.aib_brain/` require AIB Maintainer review.

### Assumptions

- Workspace root is the repository root (confidence: high).

- Python 3.10+ is available on developer workstations (confidence: high).

- AI models and vendors may change; prompts and tools must remain model-agnostic (confidence: high).

- The framework remains file-based without database or cloud services (confidence: high).

- `input.md` content is written by humans (or integrated tooling), not automatically populated by other prompts (confidence: high).

### Validity Horizon

- The model-agnostic assumption should be revisited if future prompt capabilities require model-specific syntax or tooling that cannot be abstracted.

- The Python 3.10+ constraint should be revisited with each new Python major release to confirm standard library API stability.

## Requirements

Functional requirements:

- FR-001: The system manages exactly one Active request in the workspace at a time.

- FR-002: `create-request.py` creates a request folder and register entry; it does NOT seed `plan.md` or `implementation.md`.

- FR-003: The `aib-analyze.md` prompt auto-creates a request from `input.md` when no Active request exists; it archives `input.md` content and moves all non-`.gitkeep` files from `.aib_memory/attachments/` to `<request-folder>/inputs/` using `shutil.move`, then resets `input.md` as the **last action** of the run (after all analysis artifacts are fully written). In direct standard flow with an already Active request, the final reset is conditional: if `input.md` is non-stub (not seed-template-equivalent after line-ending and trailing-whitespace normalization), the pre-reset content is archived to `<request-folder>/inputs/input-archive-<timestamp>.md`; if stub-equivalent, archive creation is skipped.

  - After reset, the `## Active request` line in `input.md` reflects the current active request ID and title (format: `<request_id> — <title>`); the literal string `No active request` is NOT present after reset. Active-request artifacts (`plan-<request_id>.md`, `analysis-<request_id>.md`) are written to `.aib_memory/` root using ID-suffixed filenames (e.g. `.aib_memory/plan-R-20260509-2313.md`) while the request is active, preventing merge conflicts across branches.

- FR-004: The system generates an `analysis-<request_id>.md` artifact per request and updates `plan-<request_id>.md` with sections: Plan and Decisions. `## Decisions` in `plan.md` records resolved Q&A entries (questions asked and answered) in an append-only log.

  - The `analysis-<request_id>.md` artifact contains 5 mandatory sections: Overview (containing Request ID, Request title, and sub-sections Background, Scope, Out of scope — for human review only), Files Read During This Analysis Run, Input Interpretation, Research Results, and Implementation Alternatives. `## Implementation Alternatives` MUST contain a `### Decision Points` heading/sub-heading list enumerating all decision forks and tagging each as `ask` or `resolve-autonomously`.

  - The prompt enforces a preflight halt gate: if multiple Active requests exist, execution stops immediately with a human-readable error. The prompt structure includes: an `## Execution Model Summary` section describing the six execution phases; a `## Global Constraints` section (GC-01 through GC-06) consolidating cross-cutting rules; a `## Failure Handling` section specifying halt-with-error conditions; Section 4 (Preflight) organized into four labeled phases (State Resolution, Input Acquisition, State Mutation, Context Enrichment); Phase 4 — Context Enrichment opens with a brownfield context check that invokes `aib-refresh-context.md` when `context.md` is absent or empty, then continues to steps 6–9; Section 7.3 split into sub-sections 7.3.1 Decision Identification, 7.3.2 Decision Classification, and 7.3.3 Q-block Generation; and Section 8 split into sub-sections 8.1 Eligibility Check, 8.2 Finalize Script Invocation, and 8.3 Post-conditions.

  - Preflight step 8 reads all three convention files: `analysis-convention.md`, `plan-convention.md`, and `requirements-analysis-convention.md`. After reading `requirements-analysis-convention.md`, the agent evaluates every mandatory checklist item against the active request and surfaces the gate evaluation (item-by-item status, unmet items, and identified gaps) in `## Research Results` under a **Requirements Gate Evaluation** sub-heading; any mandatory item that cannot be satisfied by a reasonable documented assumption is tagged `ask` in the Decision Points section with a corresponding Q-block.

- FR-005: The `aib-implement.md` prompt generates `implementation.md` from scratch (no pre-seeded template), appends an implementation log entry, reads `plan-<request_id>.md` from `.aib_memory/plan-<request_id>.md` (the active location), and upon successful completion: (1) invokes `move-request-artifacts.py` to relocate active-request artifacts to the request subfolder, then (2) invokes `close-request.py` to close the request. `close-request.py` also invokes `move-request-artifacts.py` as a safety net before marking the request Closed; a move failure logs a warning but does not block close.

  - `close-request.py` resets `input.md` to the seed template with `No active request` as part of the close action.

- FR-006: If no Active request exists when `aib-implement.md` is invoked, it auto-triggers `aib-analyze.md` before proceeding. It does this autonomously without asking for user permission or confirmation.

- FR-007: A `Minimum questions:` option in `input.md ## Options` (default 0) sets a floor for the number of Q-blocks generated per analysis run; the AI generates at least this many Q-blocks when genuine decision points exist. When `aib-analyze.md` identifies decision points with multiple valid implementation choices where the preferred option has a materially different impact on the codebase, it generates a `## Questions` section in `input.md` with Q-blocks.

  - Each Q-block includes a `> **Why this matters:**` impact line, mutually exclusive options, and a `> Answer:` field. Exactly one option per Q-block MUST be marked `*(recommended)*` and placed first in the list; all other options carry no marker.

  - If any Q-block is unanswered on re-run, the Answer Application Sub-flow halts with an error message and leaves `input.md` unchanged; all Q-blocks must be answered before re-running analysis. After all Q-blocks are processed, the `## Questions` section is cleared from `input.md`.

  - No `Question threshold` row exists in `input.md`; the AI decides which decisions require user input based on the presence of multiple valid choices with materially different implementation impacts.

- FR-008: Each AIB prompt (`aib-analyze.md`, `aib-implement.md`) reads `.aib_memory/context.md` as part of its preflight (graceful when absent or empty). Developers may list any additional context files in `.aib_memory/instructions.md`; there is no separate references register.

- FR-009: The system reads the `context-convention.md` for the `context.md` product-doc artifact and fails closed if the convention file cannot be read.

- FR-012: Every AIB prompt (`aib-analyze.md`, `aib-implement.md`, `aib-refresh-context.md`) reads `.aib_memory/instructions.md` as the first step before executing its main logic. If the file is absent or empty, the prompt continues normally with no error.

  - If non-empty, its content is treated as persistent workspace-level behavioral directives that MUST be observed throughout the prompt's execution. `initialize.py` seeds an empty `instructions.md` on workspace initialization (idempotent: does not overwrite an existing file).

- FR-010: The interactive menu uses an explicit hard-coded action list (no glob-based auto-discovery); the list is empty by default (no permanently visible actions beyond the conditionally injected close-request action). A "Close current request" action (backed by `close-request.py`) is conditionally injected by `filter_visible_actions` when an active request exists and disappears automatically after the request is closed.

  - The menu displays a state-aware guidance block showing the developer's next recommended action based on the current workspace state — one of seven states: `idle`, `input_ready`, `request_incomplete`, `questions_pending`, `implementation_ready`, `amendment_pending`, or `unknown`. The guidance block is rendered before the numbered options list so the recommended next step is visible immediately after the active-request status line.

  - An additional guidance line is displayed when `context.md` is absent or empty. No inline copy-paste prompt reference block is displayed.

  - Lifecycle creation commands (`create-request.py`) are excluded from the menu. The `choose_action()` function guards UP/DOWN navigation with `if total_items > 0:` to prevent `ZeroDivisionError` when no actions are visible.

- FR-011: A PR bookkeeping workflow bumps the version marker (auto-applies PATCH when the PR branch marker equals the base marker; accepts any manually pre-applied MINOR or MAJOR bump on the branch), creates a new per-version log under `logs/`, and produces a versioned zip of `.aib_brain/` in `versions/`. The generated `Changes:` section prefers curated bullet entries from `logs/next_version_changes.md` when present and non-empty, and falls back to git commit subjects otherwise.

  - After successful incorporation, CI clears `logs/next_version_changes.md` to empty and commits the reset back to the PR branch. The CI commit message uses `chore: bump to <version> (PR #<number>)` as the subject line; when curated bullet entries were present, the commit message body contains those bullets (separated from the subject by a blank line per Git convention).

  - When curated entries are absent, only the subject line is used. Additionally, when `changes_body` is non-empty, a conditional workflow step posts a PR comment containing the curated changelog bullets via the `gh` CLI (using `continue-on-error: true` so a transient API failure never blocks the release).

  - This ensures changelog content reaches PR subscribers via GitHub notification email regardless of whether GitHub surfaces the commit body. The `permissions` block grants `pull-requests: write` for this comment-posting step.

- FR-013: `initialize.py` seeds a SemVer marker file (e.g. `v1.3.0`) as an empty file in `.aib_memory/` matching the installed `.aib_brain/` version; seeding is idempotent (skip when present; replace stale marker on `--force`). `common.py` provides a `get_semver(dir)` helper that returns the marker filename or None.

  - `initialize.py --upgrade` archives the current `.aib_memory/` (excluding `archives/`) to a timestamped subfolder under `.aib_memory/archives/`, clears non-archive content, re-seeds from brain assets, restores `context.md` and `instructions.md` unconditionally, and conditionally restores `requests_register.md` and the `requests/` directory based on an interactive prompt (defaults to migrate when non-interactive). When the user chooses to migrate requests (Y), `requests/` is MOVED from the archive to active memory: it is copied to `.aib_memory/requests/` and then deleted from the archive so that `requests/` exists in exactly one location after migration.

  - The archive will NOT contain a `requests/` subfolder after a successful migration. When the user declines migration (N), `requests/` remains exclusively in the archive and active memory receives only the freshly-seeded empty stub.

  - When the archived snapshot still contains a legacy `references.md`, the upgrade emits a one-shot informational warning listing every row whose normalised `path` is not one of the historical defaults (`.aib_memory/context.md`), instructing the developer to migrate those entries into `.aib_memory/instructions.md`; a malformed legacy file produces the explicit line `WARNING: legacy references.md is not parseable; skipping migration check.`. The warning is informational only and never alters the upgrade exit code.

  - After upgrade, the menu continues automatically without requiring a relaunch. At startup, `menu.py` compares brain and memory semver markers; if they differ or the memory marker is absent, an upgrade prompt is displayed with options to upgrade now or skip.

Non-functional requirements:

- NFR-001: Workflows must be model-agnostic and vendor-agnostic.

- NFR-002: Active request resolution must be deterministic (filesystem-only, fail on invalid state).

- NFR-003: Missing convention mapping must cause a fail-closed response with no partial writes.

- NFR-004: Tool scripts must run on Python 3.10+ using the standard library only.

- NFR-005: The release bookkeeping workflow must be idempotent on reruns.

- NFR-006: `inputs/input-archive-*.md` files in request folders MUST NOT be read by `aib-implement.md` or any other prompt.

Acceptance criteria:
1. Initialization creates `.aib_memory/` registers, `context.md`, and `input.md` with the seed template (containing `## Active request`, `## Options` with `Minimum questions: 0`, and `## Input` sections; no toggle lines; no `Question threshold` row).
2. Creating a request via `create-request.py` produces only the request folder and a register row; no `plan.md` or `implementation.md` in the folder.
3. Running `aib-analyze.md` with non-empty `input.md` and no Active request creates AI-generated `plan-<request_id>.md` (deferred to re-run when Q-blocks are generated; written in the single pass when no Q-blocks exist) at `.aib_memory/plan-<request_id>.md`, `analysis-<request_id>.md` at `.aib_memory/analysis-<request_id>.md`, archives `input.md`, and resets `input.md` to the seed template. In direct standard-flow runs with an existing Active request, the final reset archives pre-reset content only when `input.md` is non-stub (not seed-template-equivalent); stub-equivalent input skips archive creation.

4. ID-suffixed artifacts reside at `.aib_memory/` root while the request is active.

5. Running `aib-implement.md` on an Active request reads `plan-<request_id>.md` from `.aib_memory/plan-<request_id>.md`, creates `implementation.md` from scratch in the request subfolder, applies scope, moves active-request artifacts to the request subfolder via `move-request-artifacts.py`, and closes the request.

6. The CLI menu shows no lifecycle commands and no exit option; prompt invocations are displayed.

7. Release bookkeeping increments the patch version, writes a per-version log, and produces `versions/aib_brain_vX.Y.Z.zip`; the CI workflow commits `versions/` alongside `.aib_brain/` and `logs/` to the PR branch.

8. Exactly one SemVer marker exists in `.aib_brain/`.

9. After `initialize.py`, `.aib_memory/` contains exactly one semver marker file whose name matches the brain semver (SC-1). Re-running does not overwrite it (SC-2).

10. `menu.py` startup with matching markers shows the normal menu (SC-3); with mismatched or absent memory marker, it shows an upgrade prompt (SC-4).

## Architecture & Decisions

### Component Map

The workspace is composed of the following components.

- **AIB Brain Assets** (`.aib_brain/`) — Reusable prompts, conventions, and tool scripts; the deterministic workflow engine. Never modified by tool scripts; replaced by AIB Maintainers on framework upgrade.

- **Input Channel** (`.aib_memory/input.md` and `.aib_memory/attachments/`) — Ephemeral user-agent communication layer. `input.md` is seeded by `initialize.py`; read by `aib-analyze.md`; archived per request; reset after processing.

- Contains `## Active request`, `## Options` (a `Minimum questions: 0` configuration line setting the floor for Q-block generation per analysis run), and `## Input` sections. A `## Questions` section is appended by `aib-analyze.md` when AI-generated questions are needed; it is ephemeral and cleared after each Q&A cycle.

- During direct standard-flow analysis, `finalize-input.py` handles the conditional archive of pre-reset `input.md` (only when non-stub) and the seed-template reset. Reset to seed template with `No active request` by `close-request.py` upon request close.

- `attachments/` is a staging folder for supplementary input files (screenshots, specs, data samples); supports nested subdirectory structure; seeded with a `.gitkeep` placeholder by `initialize.py`; read by `aib-analyze.md` before drafting analysis (recursive walk, including subdirectories); files moved to `<request-folder>/inputs/` by `finalize-input.py` during archiving.

- **Attachments Staging Folder** (`.aib_memory/attachments/`) — Staging folder for developer-supplied supplementary input files (supports nested subdirectory structure). Seeded by `initialize.py` with a `.gitkeep` placeholder (VCS-trackable).

- Read by `aib-analyze.md` before drafting analysis (recursive walk, including subdirectories; text files read in full; binary files acknowledged by name). Files moved to `<request-folder>/inputs/` when `input.md` is archived, preserving relative subdirectory structure.

- `close-request.py` logs a non-blocking warning when the folder is non-empty at close time.

- **AIB Command Menu** (`.aib_brain/run.bat`, `.aib_brain/run.sh`, `.aib_brain/tools/menu.py`) — Terminal UI launcher; hard-coded developer-facing action list; state-aware guidance block; streams stdout/stderr via Popen tee pattern; writes per-action log files.

- **AIB Tool Scripts** (`.aib_brain/tools/*.py`) — Python scripts implementing deterministic AIB actions (initialize, create-request, close-request, move-request-artifacts, etc.).

- **Move Artifacts Script** (`.aib_brain/tools/move-request-artifacts.py`) — Moves active-request artifacts (`plan-<ID>.md`, `analysis-<ID>.md`) from `.aib_memory/` root to the active request's subfolder, preserving their ID-suffixed names; idempotent; invoked by `aib-implement.md` (pre-close) and `close-request.py` (safety net).

- **Finalize-Input Script** (`.aib_brain/tools/finalize-input.py`) — Atomically archives `input.md` (with stub-equivalence guard), moves non-`.gitkeep` attachment files from `.aib_memory/attachments/` to `<request-folder>/inputs/`, and resets `input.md` to the seed template with the active request ID injected. Invoked by `aib-analyze.md` instead of inline archive/reset operations.

- **AIB Conventions** (`.aib_brain/conventions/`) — Markdown files defining the required structure, formatting rules, and quality gates for each managed document type.

- **AIB Prompts** (`.aib_brain/prompts/`) — Markdown prompt files (`aib-*.md`) invoked directly in an AI coding interface to produce AIB artifacts.

- **AIB Memory Artifacts** (`.aib_memory/`) — Requests register, `context.md`, `input.md`, and `instructions.md`; persist workspace state.

- **Requests Register** (`.aib_memory/requests_register.md`) — Markdown table tracking all requests with their lifecycle state, folder path, and timestamps.

- **Workspace Instructions** (`.aib_memory/instructions.md`) — Persistent, free-form Markdown file containing workspace-level behavioral directives. Read by every AIB prompt (`aib-analyze.md`, `aib-implement.md`, `aib-refresh-context.md`) before executing its main logic.

- If absent or empty, prompts continue normally. Seeded as an empty file by `initialize.py` (idempotent); editable directly by users without any tool invocation.

- Currently contains the directive instructing the agent to maintain `logs/next_version_changes.md` (append-only bullets) during every implementation run. Also serves as the sanctioned channel for developer-supplied extra context paths AIB should treat as supplementary product-doc inputs.

- **Request Artifacts** (`.aib_memory/` active phase → `.aib_memory/requests/<request-folder>/` archived phase) — `plan-<ID>.md` and `analysis-<ID>.md` reside at `.aib_memory/` root using ID-suffixed names while the request is active (e.g. `plan-R-20260509-2313.md`); moved to the request subfolder keeping their ID-suffixed names (e.g. `plan-R-20260509-2313.md`, `analysis-R-20260509-2313.md`) by `move-request-artifacts.py` upon implementation completion before close. The request folder also contains `implementation.md` (created on-demand), `inputs/input-archive-*.md` for audit, and optionally `answer-<timestamp>.md`.

- **Release Bookkeeping Script** (`scripts/release_bookkeeping.py`) — Validates SemVer marker, determines target version (auto-applies PATCH when PR branch marker equals base; accepts any manually pre-bumped MINOR or MAJOR marker already on the branch), rotates marker file when needed, writes per-version log, and creates versioned `.aib_brain/` zip in `versions/`. Prefers curated bullets from `logs/next_version_changes.md` (path passed via `--next-version-changes-file`) over commit subjects when generating the `Changes:` section; resets the curated file to empty after successful incorporation.

- **Curated Change Log** (`logs/next_version_changes.md`) — Append-only Markdown bullet list maintained by the AI agent during each `aib-implement.md` run; consumed by `release_bookkeeping.py` as the preferred `Changes:` source for the next version log; reset to empty by CI after incorporation. VCS-tracked.

- **Versioned Archives** (`versions/`) — Versioned zip archives of `.aib_brain/` (`aib_brain_vX.Y.Z.zip`); committed to VCS; used for installation.

- **GitHub Actions Workflow** (`.github/workflows/aib-semver-patch-bump-and-log.yml`) — CI automation for SemVer bump on PR events targeting `main`. Auto-applies a PATCH bump when the branch carries the same marker as the base; accepts a manually pre-applied MINOR or MAJOR bump already on the branch. Produces an enriched git commit message: subject line `chore: bump to <version> (PR #<number>)` plus, when curated bullets were present, the bullet list as the commit body (passed via the `changes_body` step output from `release_bookkeeping.py`).

- Falls back to subject-only commit message when no curated entries exist. Also posts a PR comment containing the curated changelog bullets when `changes_body` is non-empty (conditional step with `continue-on-error: true` using `gh` CLI); requires `pull-requests: write` permission.

- **Action Execution Logs** (`.aib_memory/logs/`) — Per-action log files (`aib-action-<timestamp>-<action-id>.log`) written by `menu.py`; excluded from VCS.

- **Release Version Logs** (`logs/`) — Per-version log files (`version_vX.Y.Z_log.md`) written by CI; committed to VCS.

### Integration Points

- GitHub (VCS): repository hosting and PR events; data flows: developer push/pull, CI push (marker rotation + version log + zip).

- GitHub Actions (CI runner): receives PR events, executes release bookkeeping; data flows: process invocation, file writes back to PR branch.

### Key Architectural Decisions

### ADR-0001 — Single SemVer marker file for version

- Context: deterministic version detection without package managers.

- Decision: represent active version as exactly one empty file in `.aib_brain/` named `vMAJOR.MINOR.PATCH`.

- Rationale: tool-agnostic, easy to validate, low merge conflict risk.

- Consequences: strict enforcement required; multiple markers cause a fail state.

### ADR-0002 — Fail-closed convention enforcement

- Context: missing convention files can cause malformed docs or state drift.

- Decision: if a required convention mapping cannot be resolved, do not edit the product-doc and record a blocker.

- Rationale: prevents silent corruption; favors safety over leniency.

### ADR-0003 — Separation of brain and memory folders

- Context: framework assets must survive workspace-specific changes and be upgradeable as a unit.

- Decision: all reusable assets live in `.aib_brain/` (replaceable on upgrade); all workspace-specific artifacts live in `.aib_memory/` (persistent across upgrades).

- Consequences: `.aib_brain/` must never be written by tool scripts.

### ADR-0004 — Pre-merge CI write model for release bookkeeping

- Context: version log and marker rotation must be committed before the PR is merged.

- Decision: the GitHub Actions workflow commits directly to the PR branch before merge.

- Rationale: ensures the version log and bumped marker land atomically with the feature changes.

### ADR-0005 — input.md as ephemeral communication channel (v1.2.0)

- Context: requiring explicit "Create request" CLI commands added friction to the conversational workflow.

- Decision: introduce `input.md` as the primary user-agent communication file; `aib-analyze.md` auto-creates a request when no Active request exists and `input.md` is non-empty.

- Rationale: reduces ceremony; maintains the single-Active-request invariant; archives user input for audit.

- Consequences: `input.md` content is ephemeral; each analysis run archives and resets it.

### ADR-0006 — Remove template seeding from create-request.py (v1.2.0)

- Context: `plan.md` is now AI-generated from `input.md`; `implementation.md` is generated on-demand.

- Decision: `create-request.py` creates only the folder and register row; no `plan.md` or `implementation.md` seeded from templates.

- Rationale: AI-generated `plan.md` is richer than a template stub; `implementation.md` has no content before implementation begins.

### ADR-0007 — Auto-close on successful implementation (v1.2.0)

- Context: closing the request was a manual step prone to omission.

- Decision: `aib-implement.md` invokes `close-request.py` after confirmed successful implementation.

- Consequences: auto-close only fires after no unresolved test failures; reuses `close-request.py` without duplicating its logic.

### ADR-0008 — Curated change-log source for release bookkeeping

- Context: per-version logs generated only from raw git commit subjects were terse and inconsistent with user-visible changes.

- Decision: introduce `logs/next_version_changes.md` as a curated, append-only Markdown bullet list maintained by the AI agent via the `instructions.md` directive; `release_bookkeeping.py` prefers it over commit subjects and falls back when it is missing or empty; CI resets it to empty after successful incorporation.

- Rationale: improves changelog readability without external dependencies; preserves a deterministic fallback path; introduces no new persistent register.

- Consequences: lifecycle reset must be gated to skip the script's idempotent no-op early-exit branches; the curated file remains VCS-tracked but is expected to be empty between releases. The curated bullet content also flows into the CI commit message body: `release_bookkeeping.py` emits a `changes_body` output key (via `GITHUB_OUTPUT` heredoc) before resetting the curated file, and the workflow commit step constructs a multi-line git commit message (subject + blank line + body) when `changes_body` is non-empty.

- A complementary PR comment step also posts the curated bullets as a PR comment (conditional on non-empty `changes_body`, `continue-on-error: true`) to surface changelog content in GitHub PR notification emails, since GitHub notification emails display only the commit subject line, not the commit body.

### Technology Stack

- Language: Python 3.10+ (standard library only for tool scripts).

- Documentation format: Markdown.

- CI platform: GitHub Actions.

- Version control: Git / GitHub.

- No cloud infrastructure is provisioned; all resources are repo/CI/filesystem-based.

### Quality Attributes

Priorities in order: reliability (deterministic fail-closed) > scalability (chunked reads for large repos) > security (workspace-relative file IO only) > cost (file-based, no cloud spend).

## Technical Design

### Module Breakdown

**Tool scripts** (`.aib_brain/tools/`):

- `initialize.py` — Seeds `.aib_memory/` structure, writes `requests_register.md`, `context.md`, `input.md`, and `instructions.md`. Creates `.aib_memory/requests/`, `.aib_memory/logs/`, and `.aib_memory/attachments/` on initialization (idempotent via `exist_ok=True`); places a `.gitkeep` placeholder in `attachments/` on first creation.

- Fails without partial writes on invalid workspace state. The seeded `input.md` contains `## Active request`, `## Options` (only `Minimum questions: 0`), and `## Input` sections; no toggle lines; no `Question threshold` row.

- Seeds `instructions.md` as an empty file; does not overwrite an existing file. Seeds a `vMAJOR.MINOR.PATCH` semver marker in `.aib_memory/` matching the brain version; skips if already present (unless `--force`).

- `--upgrade` flag triggers archive/re-seed/restore procedure (see FR-013) and additionally inspects any legacy `references.md` captured in the archive, emitting an informational warning listing rows whose `path` is not one of the two historical defaults so the developer can migrate them into `instructions.md`.

- `create-request.py` — Validates no Active request, creates request folder with deterministic naming (`<request_id>-<title-slug>`), appends register row as Active. Does NOT write `plan.md` or `implementation.md`.

- `close-request.py` — Marks the Active request Closed; invokes `move-request-artifacts.py` as a safety-net before marking Closed (move failure logs a warning, does not block close). After updating the register, logs a non-blocking WARNING when `.aib_memory/attachments/` contains files other than `.gitkeep` (indicating missed archiving).

- Resets `input.md` to the seed template with `No active request` after the check (skips silently if `input.md` does not exist).

- `move-request-artifacts.py` — Moves `plan-<ID>.md` and `analysis-<ID>.md` from `.aib_memory/` root to the active request's subfolder, preserving their ID-suffixed names. Idempotent: skips each file if already absent at the source; safe to call twice.

- Uses `shutil.move` for cross-filesystem correctness. Raises `ValidationError` only for workspace-level errors (missing register, no active request).

- `menu.py` — Interactive tool launcher. Action list is fully hard-coded (`_SCRIPT_ACTIONS`): the list is empty by default (no permanently visible actions); no glob-based auto-discovery.

- A "Close current request" action (backed by `close-request.py`) is conditionally appended by `filter_visible_actions` when `state.has_active_request` is True; it disappears automatically on the next menu refresh after the request is closed. Displays a state-aware guidance block (`_detect_guidance_state` + `_GUIDANCE_MESSAGES`) showing the developer's next recommended action for one of seven workspace states: `idle`, `input_ready`, `request_incomplete`, `questions_pending`, `implementation_ready`, `amendment_pending`, `unknown`.

- When `context.md` is absent or empty, `_is_context_empty()` triggers an additional guidance line recommending the context generation prompt. Streams subprocess stdout/stderr via Popen tee pattern.

- Writes per-action log files to `.aib_memory/logs/`. Press `0`, `q`, or `Q` to quit.

- Uses ANSI escape sequences (`\033[H\033[J`) for blink-free screen clearing via `_enable_ansi_windows()` (one-time Windows VT enablement via ctypes at startup); buffers the entire menu into an `io.StringIO` and writes to stdout in a single call. Auto-refreshes every 3 seconds via `get_key(timeout=_REFRESH_TIMEOUT_S)` using `msvcrt.kbhit()` polling (Windows) or `select.select()` (Unix) — no background threads; `_REFRESH_TIMEOUT_S: float = 3.0` is the sole tunable constant.

- Renders a fixed `0) Quit` footer line; `choose_action()` returns `None` on `QUIT`/`DIGIT:0`; `main()` breaks the loop on `None`. At startup, `check_version_compatibility()` compares brain and memory semver markers; when they differ or the memory marker is absent, a mismatch banner and numbered prompt are shown ([1] Upgrade, [2] Skip).

- Choosing upgrade invokes `initialize.py --upgrade` as a subprocess; on success, continues to the normal menu automatically without requiring a relaunch; on failure, exits so the user can retry. Choosing skip continues to the normal menu.

- `file-inventory.py` — Walks the workspace filesystem and emits a deterministic JSON Lines file inventory for use by `aib-refresh-context.md`.

- `finalize-input.py` — Archives `input.md` (with stub-equivalence guard that ignores the active request ID value), moves non-`.gitkeep` attachment files from `.aib_memory/attachments/` to `<request-folder>/inputs/` (preserving subdirectory structure via `shutil.move`), and resets `input.md` to the seed template with the active request ID injected. Accepts `--workspace` (required) and `--request-id` (optional, defaults to Active).

- Invoked by `aib-analyze.md` instead of inline archive/reset operations.

- `common.py` — Shared utilities: `parse_markdown_table`, `format_markdown_table`, `read_text`, `write_text`, `slugify`, `now_iso`, `now_compact_request_id`, `ensure_workspace`, `get_semver`, `ValidationError`, and related helpers. `get_semver(dir: Path) -> str | None` globs for `vMAJOR.MINOR.PATCH` files in a directory; returns the filename if exactly one match, otherwise None (fail-safe).

- `parse_args()` includes the `--upgrade` flag for `initialize.py`.

**Prompt actions** (`.aib_brain/prompts/`):

- `aib-refresh-context.md` — generates or updates `.aib_memory/context.md` from workspace sources, applying a content currency rule that prohibits version history annotations and deprecated-concept glossary entries; Phase 5 includes a mandatory Rule 16 verification pass before writing. Reads `.aib_memory/instructions.md` as the first step (graceful: absent or empty = no-op).

- `aib-analyze.md` — Two-branch prompt: (1) if Active request exists, generates `analysis-<request_id>.md` at `.aib_memory/analysis-<request_id>.md` and updates `.aib_memory/plan-<request_id>.md` optional sections; (2) if no Active request exists, reads `input.md`, auto-creates a request via `create-request.py`, then invokes `finalize-input.py` to archive `input.md`, move attachments, and reset `input.md`, proceeds with analysis. In the no-Active-request branch, `plan-<request_id>.md` is written at `.aib_memory/plan-<request_id>.md` only when no Q-blocks are generated (single pass as part of Part 2 updates); when Q-blocks are generated, `plan-<request_id>.md` is deferred to re-run after Q&A, at which point the Answer Application Sub-flow creates it in full using the `## Input Interpretation` section from the analysis artifact.

- In both branches, a mandatory preflight step reads all text files in `.aib_memory/attachments/` (recursive walk, all files including subdirectories, skip `.gitkeep`) as supplementary input context before drafting analysis; binary files are acknowledged by name. All artifacts (`plan-<request_id>.md`, `analysis-<request_id>.md`) are written to `.aib_memory/` root (not inside the request subfolder) while the request is active.

- Reads `.aib_memory/instructions.md` as the first step (graceful: absent or empty = no-op). Standard flow also invokes `finalize-input.py` as its final step unless triggered from `aib-implement.md`; the script conditionally archives pre-reset content (only when non-stub) and resets `input.md` to the seed template.

- When analysis identifies decision points with multiple valid implementation choices where the preferred option has a materially different impact, Q-blocks are written to a `## Questions` section in `input.md` (not in `plan.md`). A mandatory Decision Fork Enumeration step tags all forks as `ask` or `resolve-autonomously` before generating Q-blocks; the `### Decision Points` heading/sub-heading list in `## Implementation Alternatives` records all forks with rationale.

- The default philosophy is ask-first: autonomous resolution requires an explicit, named source in workspace documentation. Each Q-block includes a `> **Why this matters:**` impact line, mutually exclusive options, and a `> Answer:` field.

- Exactly one option per Q-block is marked `*(recommended)*` and placed first in the list; all other options carry no marker. If any Q-block is unanswered on re-run, the Answer Application Sub-flow halts with an error message and leaves `input.md` unchanged; all Q-blocks must be answered before re-running analysis.

- On re-run, if `input.md` contains a `## Questions` section, the Answer Application Sub-flow processes all Q-blocks (applying chosen or first-listed options to relevant `plan.md` sections) and clears the section before proceeding with normal analysis. `## Decisions` in `plan.md` records the resolved Q&A log (append-only).

- The prompt MUST verify the answer is explicitly and unambiguously stated in a named, specific section before resolving autonomously; if not explicitly stated, the default is to raise a Q-block. No `Question threshold` row exists in `input.md`.

- Every plan generated in `plan-<request_id>.md` MUST include a mandatory automated-testing task and a mandatory context/docs update task. The `analysis-<request_id>.md` generated contains 5 mandatory sections: Overview, Files Read During This Analysis Run, Input Interpretation, Research Results, and Implementation Alternatives (with a mandatory `### Decision Points` heading/sub-heading list; the entire analysis document is a reasoning-only artifact, MUST NOT be read by `implement`).

- A `Minimum questions:` option in `input.md ## Options` (default 0) sets a floor for Q-block generation. Preflight step 8 reads all three convention files: `analysis-convention.md`, `plan-convention.md`, and `requirements-analysis-convention.md`; after reading `requirements-analysis-convention.md`, the agent evaluates every mandatory checklist item against the active request and surfaces the gate evaluation in `## Research Results` under a **Requirements Gate Evaluation** sub-heading; gaps that cannot be satisfied by a reasonable assumption are tagged `ask` in the Decision Points section with corresponding Q-blocks.

- `aib-implement.md` — Guides execution of the active request scope. Reads `.aib_memory/instructions.md` as the first step (graceful: absent or empty = no-op).

- Reads `plan-<request_id>.md` from `.aib_memory/plan-<request_id>.md` (the active location). Auto-triggers `aib-analyze.md` without user confirmation if no Active request exists.

- Generates `implementation.md` from scratch (no pre-seeded template required). Upon confirmed successful implementation: (1) invokes `move-request-artifacts.py` to relocate active-request artifacts to the request subfolder, then (2) invokes `close-request.py`; `close-request.py` resets `input.md` to seed template with `No active request` as part of close.

- Must NOT read `inputs/input-archive-*.md` files.

**Conventions** (`.aib_brain/conventions/`):

Each convention file defines the required structure, content guidance, formatting rules, and quality gates for a specific document type. Conventions cover: `context.md`, `plan.md`; `## Plan` requires a mandatory automated-testing task and a mandatory context/docs update task; Plan task schema uses level-4 markdown headings (`####`) for all sub-fields (Intent, Outputs, Procedure, Done criteria, Dependencies, Risk notes); procedure steps within a task are separated by one blank line; markdown tables are prohibited; every Procedure step MUST cite the exact file path it operates on; no `## Code and Asset Scan` or `## Internal Review` sections; no `## Amends` section; plan.md has 4 mandatory sections (Goal, Constraints, Success criteria, Plan)), `requests_register.md`, `implementation.md`, `analysis.md` (5 mandatory sections: Overview, Files Read During This Analysis Run, Input Interpretation, Research Results, Implementation Alternatives — the entire analysis document is a reasoning-only artifact, MUST NOT be read or acted on by `implement`), and a range of coding conventions (Python, JavaScript, SQL, CSS, HTML, React, Django, Flask, C#, Scala, DAX, UI/UX, general).

**Release bookkeeping** (`scripts/`):

- `release_bookkeeping.py` — Standalone script run in CI. Locates SemVer markers, computes bumped version, rotates marker file, writes new version log, and creates `versions/aib_brain_vX.Y.Z.zip` using `zipfile` from the standard library.

- Accepts `--next-version-changes-file` to point at the curated change log; selects `Changes:` source as curated entries first, commit subjects as fallback; resets the curated file to empty after successful incorporation (gated on `changed and used_curated`). Idempotent on reruns.

### Key Algorithms

**ALG-0001 — SemVer Version Bump**
Locates the base marker from the git tree and the worktree marker from the filesystem. Validates exactly one marker at each location. Computes target version: if head equals base, $v' = (X, Y, Z+1)$ (auto PATCH); if head > base, $v' = \text{head}$ (accept manual MINOR/MAJOR pre-bump); if head < base, halt with error. Rotates marker only when head equals base (delete old, create new). Writes new per-version log and creates brain zip. Idempotent on reruns.

**ALG-0002 — Active Request Resolution**
Reads `requests_register.md`, selects row with `state = Active`. Enforces invariant $|ActiveRequests| = 1$; fails with explicit error if zero or more than one Active. Filesystem-only.

**ALG-0003 — Auto-Request Creation from input.md**
`aib-analyze.md` reads `input.md`'s `## Input` section; derives a title; invokes `create-request.py`; invokes `finalize-input.py` to archive `input.md` to `inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`, move attachments, and reset `input.md` to the seed template; and for direct standard-flow runs with an already Active request, `finalize-input.py` archives pre-reset content only when `input.md` is non-stub while skipping archive creation when stub-equivalent; replaces `No active request` in `## Active request` with the active request ID and title. `plan.md` is created with all 4 mandatory sections (Goal, Constraints, Success criteria, Plan) only when no Q-blocks are generated — in a single pass as part of Part 2 updates. When Q-blocks are generated, `plan.md` is NOT written in the first pass; the Answer Application Sub-flow creates it in full on re-run after Q&A is resolved, using the `## Input Interpretation` section from the existing `analysis-<request_id>.md` as the primary source for sections 1–2.

### Inter-component Communication

All inter-component communication at runtime is local filesystem reads/writes (Markdown files). No network communication between components at runtime. CI pipeline communicates via git push to PR branch.

### Configuration

All tool scripts accept parameters via CLI arguments (`--workspace`, `--title`, `--request-id`, etc.). No config files or environment variables are required at runtime. The `_SCRIPT_ACTIONS` constant in `menu.py` is the authoritative hard-coded list of developer-facing menu actions; no glob-based script discovery is performed at runtime.

### Runtime Sequences

- SEQ-001: Initialize workspace — Developer invokes menu → tool scripts read `.aib_brain/` assets → create `.aib_memory/` structure → write registers and `input.md`.

- SEQ-002: Create request (AI-driven) — Developer writes intent to `input.md` → runs `aib-analyze.md` → prompt auto-creates request, archives input, generates `plan-<ID>.md` at `.aib_memory/plan-<ID>.md` and `analysis-<ID>.md` at `.aib_memory/analysis-<ID>.md`.

- SEQ-003: Implement request — Developer runs `aib-implement.md` → prompt reads `plan-<ID>.md` from `.aib_memory/plan-<ID>.md` → generates `implementation.md` in request subfolder → invokes `move-request-artifacts.py` (relocate ID-suffixed artifacts to request subfolder, preserving ID-suffixed names) → closes request via `close-request.py`.

- SEQ-004: Release bookkeeping in CI — PR event triggers GitHub Actions → release script locates markers → determines target version (auto PATCH when head equals base; accepts manual MINOR/MAJOR pre-bump) → rotates marker when needed → writes version log → creates `.aib_brain/` zip → pushes to PR branch.

- SEQ-005: Execute action with real-time streaming — Developer selects action in menu → menu spawns subprocess via Popen → tee pattern streams stdout/stderr to terminal → writes log file → reports exit code.

## Data Architecture

### Data Sources

The workspace filesystem is the sole data source for AIB.

- **Workspace repository filesystem** — Owner: Repository Maintainers. Ingestion method: on-demand batch read. Refresh frequency: ad-hoc. Classification: Internal.

AIB tools read a bounded set of Markdown files and write derived artifacts back to `.aib_memory/`. No external databases or APIs are ingested.

### Core Data Entities

The following entities represent the primary data objects managed by AIB.

- **REQUEST** — Primary key: `request_id`. Tracked work unit with lifecycle state; constraint: exactly one Active per workspace.

- **INPUT** — Primary key: N/A. Ephemeral user-agent communication channel (`input.md`); constraint: overwrite-friendly; reset to seed after processing.

- **CONTEXT** — Primary key: `path`. Convention-governed unified product knowledge file (`context.md`); constraint: updated on each `aib-refresh-context.md` run.

- **VERSION_LOG** — Primary key: `version`. Release bookkeeping artifact; constraint: one log per bumped version; never modified after creation.

- **BRAIN_ARCHIVE** — Primary key: `version_marker`. Versioned zip of `.aib_brain/` in `versions/`; constraint: created by CI on each version bump; idempotent.

Physical storage: register data is stored in Markdown files — `requests_register.md` holds REQUEST rows.

### Data Lineage

Developer input (`input.md`) → `aib-analyze.md` → `request.md` + `analysis.md` → `aib-implement.md` → `implementation.md` + curated bullets appended to `logs/next_version_changes.md` + auto-close. Release bookkeeping: git history (commit subjects, fallback) and `logs/next_version_changes.md` (curated, preferred) → `release_bookkeeping.py` → `logs/version_vX.Y.Z_log.md` + `.aib_brain/vX.Y.Z` marker + `versions/aib_brain_vX.Y.Z.zip` + reset of curated file to empty. `.aib_memory/context.md` is the unified product knowledge sink.

### Data Storage

- `.aib_memory/` — operational registers, `context.md`, `input.md`, `instructions.md`, `attachments/`, and request artifact folders; backed by Git history.

- `.aib_memory/attachments/` — staging folder for developer-supplied supplementary input files (supports nested subdirectory structure); seeded with a `.gitkeep` placeholder; emptied of developer files after each analysis archiving step.

- `.aib_memory/plan-<request_id>.md` — Active-phase location of the plan artifact (while the request is open, e.g. `plan-R-20260509-2313.md`); written by `aib-analyze.md`, read by `aib-implement.md`; moved to the request subfolder keeping its ID-suffixed name by `move-request-artifacts.py` upon implementation.

- `.aib_memory/analysis-<request_id>.md` — Active-phase location of the analysis artifact (while the request is open, e.g. `analysis-R-20260509-2313.md`); written by `aib-analyze.md`; moved to the request subfolder keeping its ID-suffixed name by `move-request-artifacts.py` upon implementation.

- `.aib_memory/requests/<request-folder>/` — per-request archived artifacts: `plan-<request_id>.md` (or `request-<request_id>.md` in requests predating the plan.md rename), `analysis-<request_id>.md`, `implementation.md`, `inputs/input-archive-*.md` (audit trail), and optionally `answer-<timestamp>.md`.

- `.aib_memory/logs/` — action execution logs; excluded from VCS; no auto-cleanup.

- `.aib_brain/` — framework assets including the active SemVer marker file; committed to VCS.

- `logs/` — release version logs; committed to VCS.

- `versions/` — versioned `.aib_brain/` zip archives; committed to VCS; used for installation.

### Data Access Patterns

- Requests Register: read by tool scripts to resolve Active request; read by agents to understand workspace state.

- `instructions.md`: read by every AIB prompt as the first step; provides workspace-level directives and any additional context paths the developer wants AIB to read.

- `input.md`: written by developer; read by `aib-analyze.md`; archived; reset.

- Primary access: direct filesystem read; no database engine.

### Data Retention and Classification

- All AIB artifacts classified as Internal; retained via Git history until decommission.

- Release version logs: committed and retained indefinitely.

- Brain archives: committed to VCS in `versions/`; retained per version.

- Input archives (`inputs/input-archive-*.md`): committed to VCS in per-request folder; audit trail; MUST NOT be read by any prompt beyond archiving.

- Action execution logs: local filesystem only, excluded from VCS, no automatic cleanup.

- No PII is intended to be stored; accidental PII or secrets treated as incidents requiring removal.

### Data Quality

- Tool scripts fail fast on invalid register state (duplicate Active requests, malformed IDs).

- Convention enforcement: missing mappings cause fail-closed response with no writes.

- Tool scripts and prompts fail closed on missing required convention or template files; no partial writes are emitted.

## Security & Compliance

### Access Control

Repository-level access is managed through GitHub repository permissions. AIB automation runs locally in the developer workspace and writes only to `.aib_memory/` (and the curated `logs/next_version_changes.md`). GitHub Actions CI workflow is restricted to PRs from the same repository; forked PRs are skipped. `GITHUB_TOKEN` requires Read and Write permissions in repository Actions settings.

### Data Protection

All artifacts are classified Internal. No cloud object storage, databases, or external endpoints are provisioned. Encryption: provider-managed (GitHub TLS in transit; GitHub storage at rest).

### Secrets Management

No secrets should be stored in repository artifacts. `GITHUB_TOKEN` is the only credential used and is provider-managed. If a secret is accidentally committed, it must be treated as an incident and removed.

### Network Security

All CI communication is over GitHub Actions managed infrastructure (HTTPS). No custom network endpoints are provisioned.

### Compliance

No regulatory requirements are identified. All artifacts are treated as Internal engineering documentation.

## Operations

### Deployment

Download the versioned `.aib_brain/` archive from the `versions/` folder in this repository. Unzip into the workspace root. Run `.aib_brain\run.bat` (Windows) or `.aib_brain/run.sh` (Linux/macOS) for the interactive menu. GitHub Actions workflow in `.github/workflows/` requires Actions permissions set to Read and Write. CI uses a pre-merge write model.

### Observability

Action execution logs (`.aib_memory/logs/aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log`): written by `menu.py`; UTF-8 flat text; markers in order: `[START]`, `[CMD]`, `[OUT]`, `[ERR]`, `[THREAD-ERROR]`, `[EXIT]`; excluded from VCS; no auto-cleanup.

Release version logs (`logs/version_vX.Y.Z_log.md`): generated by CI release bookkeeping; committed to VCS; retained indefinitely.

No remote log transport, monitoring dashboards, or alerting thresholds are configured.

### SLO and SLA

Best-effort for all resources. No formal SLO targets. Operational performance targets: initialize p95 under 5 minutes; request operations p95 under 2 minutes; CI release bookkeeping p95 under 10 minutes.

### On-call and Escalation

AIB brain assets and CI workflow owned and supported by AIB Maintainers. Request artifacts and product docs owned and supported by Product Team. No personal contact details are stored.

### Rollback

CI rollback: reset or rebase the PR branch to remove the stale version log, then rerun. Brain asset rollback: revert the PR and verify exactly one SemVer marker remains in `.aib_brain/`.

## Development Practices

### Developer Setup

1. Download the latest versioned archive from the `versions/` folder in this repository.
2. Unzip and place `.aib_brain/` at the workspace root.
3. Ensure Python 3.10+ is available on PATH.
4. Run `.aib_brain\run.bat` (Windows) or `.aib_brain/run.sh` (Linux/macOS).
5. Select "Initialize AIB workspace" on first use.
6. To start a request: write intent into `.aib_memory/input.md` under `## Input`, then run the `aib-analyze.md` prompt.
7. Install `pytest` for running the test suite (`pytest tests/` from workspace root).

### Testing Strategy

- `conftest.py` — Shared pytest fixtures: temporary workspace builder, path configuration.

- `tests/test_initialize.py` — Integration tests for `initialize.py`; includes assertion for `input.md` creation, idempotency, semver seeding (SC-1/SC-2), and upgrade procedure (SC-5/SC-6).

- `test_create_request.py` — Integration tests for `create-request.py`; verifies folder creation, register update, and that `request.md` / `implementation.md` are NOT created.

- `test_close_request.py` — Integration tests for `close-request.py`; includes `input.md` reset on close and graceful skip when `input.md` is absent.

- `test_lifecycle_e2e.py` — End-to-end lifecycle test: initialize → create-request → close-request; verifies `request.md` is NOT created by `create-request.py`.

- `test_menu.py` — Unit tests for `menu.py`: `MenuState`, `build_command`, `_run_and_tee`, `_make_log_path`, hard-coded action list verification (SC-03/SC-04/SC-10/SC-11), state-aware guidance state detection (SC-05 to SC-17), `_is_context_empty`, `render_menu` guidance block rendering, `check_version_compatibility` (SC-3/SC-4/SC-7), and related helpers.

- `test_reverse_engineer.py` — Unit tests for `file-inventory.py`: file inventory and exclusion logic.

- `tests/test_instructions_md.py` — Tests for the instructions.md feature: asserts `.aib_memory/instructions.md` exists, contains the persistent directive referencing `logs/next_version_changes.md`, all three prompts contain the pre-read step, and `.aib_brain/README.md` documents the feature with a security note.

- `tests/test_release_bookkeeping.py` — Integration tests for `scripts/release_bookkeeping.py`; covers curated-source preference, fallback when curated file is missing or empty, lifecycle reset of `logs/next_version_changes.md` after incorporation, idempotent rerun behavior, and regression tests for MINOR and MAJOR pre-bumped branch markers.

- `tests/test_tools_common.py` — Unit tests for `common.py` helpers.

- `tests/test_finalize_input.py` — Integration tests for `finalize-input.py`; covers archive logic, stub-equivalence skip, attachment relocation, seed-template reset, and CLI error handling.

- `test_artifact_placement.py` — Tests for the two-phase artifact placement workflow: T1 (move plan-<ID>.md), T2 (move analysis-<ID>.md), T5 (idempotent second call), T6 (close-request moves artifacts before closing), T7 (close-request completes when no artifacts at root).

- `tests/test_semver_workflow_structure.py` — Structural YAML tests for `.github/workflows/aib-semver-patch-bump-and-log.yml`: verifies `pull-requests: write` permission (SC-1), "Post changelog comment" step exists (SC-2), step condition `if: steps.bookkeeping.outputs.changes_body != ''` (SC-3), `continue-on-error: true` flag (SC-4), and `$CHANGES_BODY` env reference (SC-5).

- `tests/test_requirements_analysis_convention.py` — Structural integrity tests for `requirements-analysis-convention.md`: verifies file existence, mandatory preamble sections, all eight category sections, checkbox format, at least two framework citations (BABOK, IEEE, INVEST, SMART), and pass/threshold language in the Acceptance Gate Declaration section.

All tests use `tempfile.TemporaryDirectory` for isolation. 289 tests pass.

### CI/CD Pipeline

- Trigger: PRs to `main` on `opened`, `reopened`, `synchronize`; bot-triggered runs skipped.

- Gate: exactly one valid SemVer marker must exist in `.aib_brain/`.

- Actions: validate marker, bump patch, rotate marker file, write version log, create `.aib_brain/` zip in `versions/`, commit and push to PR branch (staged files: `.aib_brain/`, `logs/`, `versions/`); when curated `changes_body` is non-empty, post a PR comment containing the changelog bullets via `gh` CLI (`continue-on-error: true`).

- Prerequisite: GitHub Actions Read and Write permissions; `pull-requests: write` permission in workflow `permissions` block for PR comment posting; fork PRs excluded.

### Branching and PR Conventions

- Branch naming: `issue/<number>`.

- PRs must include: summary of `.aib_brain/` changes, SemVer bump justification, and migration notes for MAJOR changes.

- Squash merge is recommended.

### Known Developer Experience Notes

- Non-ASCII output on Windows handled by `encoding="utf-8"`, `errors="replace"` in Popen streaming.

- Action log files accumulate locally without auto-cleanup.

- Iteration lifecycle scripts (`create-iteration.py`, `close-iteration.py`) are deprecated and excluded from the menu; treated as legacy.

- The CLI menu conditionally shows "Close current request" when an active request is present; it disappears on close. Create request is exclusively handled by the AI prompts. The menu shows a state-aware guidance block telling the developer what to do next; no inline prompt-reference copy-paste block is displayed.

## Workspace File Inventory

All workspace files are listed below in ascending path order; excluded directories (`.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.git/`) are omitted.

- `.aib_brain/` — AIB framework assets: prompts, conventions, tool scripts, and the active SemVer marker; never modified by tool scripts.

- `.aib_brain/README.md` — User guide for working with AIB from the workspace root, including quick-start and prompt invocation reference. Scripts in `.aib_brain/tools/` are invoked automatically by AIB prompts; only `initialize.py` is intended for direct user invocation (first-time workspace setup).

- `.aib_brain/conventions/` — Convention files governing the structure and coding standards for each managed document type and programming language.

- `.aib_brain/conventions/analysis-convention.md` — Convention governing the structure and content requirements for `analysis-<request_id>.md` request artifacts; defines 5 mandatory sections (Overview, Files Read During This Analysis Run, Input Interpretation, Research Results, Implementation Alternatives).

- `.aib_brain/conventions/coding-csharp-convention.md` — Coding standards and patterns for C# (`.cs`) source files.

- `.aib_brain/conventions/coding-css-convention.md` — Coding standards and patterns for CSS, SCSS, SASS, and LESS stylesheet files.

- `.aib_brain/conventions/coding-dax-convention.md` — Coding standards and patterns for DAX formula files.

- `.aib_brain/conventions/coding-django-convention.md` — Coding standards and patterns for Django Python web application files.

- `.aib_brain/conventions/coding-flask-convention.md` — Coding standards and patterns for Flask Python web application files.

- `.aib_brain/conventions/coding-general-convention.md` — General coding standards applicable across all languages and file types.

- `.aib_brain/conventions/coding-html-convention.md` — Coding standards and patterns for HTML and HTM files.

- `.aib_brain/conventions/coding-javascript-convention.md` — Coding standards and patterns for JavaScript, MJS, and CJS files.

- `.aib_brain/conventions/coding-python-convention.md` — Coding standards and patterns for Python (non-framework) source files.

- `.aib_brain/conventions/coding-react-convention.md` — Coding standards and patterns for React JSX and TSX component files.

- `.aib_brain/conventions/coding-scala-convention.md` — Coding standards and patterns for Scala source files.

- `.aib_brain/conventions/coding-sql-convention.md` — Coding standards and patterns for SQL query files.

- `.aib_brain/conventions/coding-uiux-convention.md` — UI/UX design conventions applied alongside language conventions for files with design intent.

- `.aib_brain/conventions/context-convention.md` — Authoritative convention defining the required structure, content guidance, and formatting rules for `context.md`. Section 5 requires every requirement bullet to begin with a unique `FR-NNN` or `NFR-NNN` identifier; continuation content must be nested as a sub-bullet. Section 12 requires repetitive directory contents (3+ items sharing a naming pattern) to be grouped as a single summary bullet rather than listed individually.

- `.aib_brain/conventions/implementation-convention.md` — Convention defining the format, lifecycle, and append-only rules for `implementation.md` request artifacts.

- `.aib_brain/conventions/plan-convention.md` — Convention governing the structure and content requirements for `plan.md` plan artifacts; defines 4 mandatory sections (Goal, Constraints, Success criteria, Plan); Plan task schema uses level-4 markdown headings (`####`) for all sub-fields (Intent, Outputs, Procedure, Done criteria, Dependencies, Risk notes); procedure steps are separated by one blank line; markdown tables prohibited; every Procedure step MUST cite the exact file path it operates on; no `## Amends` section; plan is an execution-only specification for the AI Automation Agent.

- `.aib_brain/conventions/requests_register-convention.md` — Convention governing the structure and validation rules for `requests_register.md`.

- `.aib_brain/conventions/requirements-analysis-convention.md` — Convention defining a structured checklist-driven gate for evaluating business requirements quality before implementation. Covers eight category groups: Goal Clarity, Stakeholder and User Identification, Business Value and Justification, Scope Definition, Out of Scope, Constraints and Assumptions, Success Criteria and Acceptance, and Context Adequacy. Incorporates best practices from BABOK, IEEE 29148, INVEST, and SMART frameworks. Defines an explicit pass/fail Acceptance Gate Declaration.

- `.aib_brain/prompts/` — Prompt action files invoked in an AI coding interface to drive the AIB workflow.

- `.aib_brain/prompts/aib-analyze.md` — Prompt for auto-creating requests from `input.md` and producing analysis artifacts; delegates file-system operations (archive, attachment move, seed-template reset) to `finalize-input.py`.

- `.aib_brain/prompts/aib-refresh-context.md` — Prompt for producing or updating `.aib_memory/context.md` with a structured workspace knowledge synthesis governed by a content currency policy (current state only; no version annotations or deprecated-concept entries). Phase 2 step 1 applies the Section 12 grouping rule for directories containing three or more items sharing a repeating naming pattern. Phase 4 formatting checklist enforces: no Markdown tables, blank line between top-level list items, two-sentence maximum per bullet, and no bold field labels.

- `.aib_brain/prompts/aib-implement.md` — Prompt for executing the active request scope, generating `implementation.md` on-demand, and auto-closing the request on success.

- `.aib_brain/run.bat` — Windows entry point script that launches `menu.py` with the workspace root resolved automatically.

- `.aib_brain/run.sh` — Linux/macOS entry point script that launches `menu.py` with the workspace root resolved automatically.

- `.aib_brain/tools/` — Python tool scripts invoked by the CLI menu to perform AIB lifecycle operations.

- `.aib_brain/tools/close-request.py` — Tool script that transitions the active request to Closed state; invokes `move-request-artifacts.py` as a safety net before marking Closed (move failure logs a warning, does not block close); logs a non-blocking WARNING when `attachments/` is non-empty at close time; updates the requests register and resets `input.md`.

- `.aib_brain/tools/move-request-artifacts.py` — Tool script that moves `plan-<ID>.md` and `analysis-<ID>.md` from `.aib_memory/` root to the active request's subfolder, preserving their ID-suffixed names. Idempotent; skips missing files silently; uses `shutil.move` for cross-filesystem safety.

- `.aib_brain/tools/common.py` — Shared utility functions (register parsing, path resolution, file I/O, `get_semver`) used across all tool scripts.

- `.aib_brain/tools/create-request.py` — Tool script that creates a new request folder and register entry; does not seed `plan.md` or `implementation.md`.

- `.aib_brain/tools/initialize.py` — Tool script that seeds the `.aib_memory/` folder on first use; creates `requests/`, `logs/`, and `attachments/` subdirectories (with `.gitkeep` in `attachments/`); does not create `docs/`; seeds a matching semver marker in `.aib_memory/`; supports `--upgrade` for backup/re-seed/restore. When the upgrade Y (migrate) path is chosen, `requests/` is MOVED from the archive to active memory (removed from archive after copy) so it exists in exactly one location.

- `.aib_brain/tools/menu.py` — Interactive CLI menu; blink-free ANSI-based rendering; hard-coded action list; state-aware guidance block; auto-refresh every 3 seconds; close-request conditionally visible when active request exists; press 0/q/Q to quit; startup version-compatibility check with upgrade prompt.

- `.aib_brain/tools/file-inventory.py` — Tool script that emits a JSONL file inventory of the workspace for use by `aib-refresh-context.md`.

- `.aib_brain/tools/finalize-input.py` — Tool script that atomically archives `input.md` (stub-equivalence checked), moves non-`.gitkeep` attachment files from `.aib_memory/attachments/` to `<request-folder>/inputs/`, and resets `input.md` to the seed template with the active request ID injected.

- `.aib_brain/user_guide.html` — Self-contained, browser-viewable HTML user guide for the AIB framework; covers the full AIB workflow, prompt invocations, Q&A mechanism, workspace structure, and glossary with no external dependencies.

- `.aib_brain/v1.3.0` — Active SemVer marker file (empty file; filename encodes the current AIB framework version v1.3.0).

- `.aib_memory/` — Workspace-specific AIB memory artifacts.

- `.aib_memory/attachments/` — Staging folder for supplementary developer input files (supports nested subdirectory structure); seeded with `.gitkeep` by `initialize.py`; emptied of developer files after each analysis run.

- `.aib_memory/attachments/.gitkeep` — Placeholder that keeps the `attachments/` directory tracked in VCS when no developer files are staged.

- `.aib_memory/context.md` — This file; unified workspace product knowledge synthesis.

- `.aib_memory/input.md` — Ephemeral user-agent communication channel; seeded by `initialize.py`; reset after each analysis run.

- `.aib_memory/instructions.md` — Persistent workspace-level behavioral directives file; seeded as empty by `initialize.py`; read by all AIB prompts before execution; free-form Markdown; editable directly by users. Currently contains the curated-change-log directive instructing the agent to maintain `logs/next_version_changes.md`.

- `.aib_memory/requests_register.md` — Requests register tracking lifecycle state for all requests.

- `.aib_memory/v1.3.0` — Memory-side SemVer marker file; empty file whose filename matches the installed `.aib_brain/` version for compatibility checking at startup.

- `.aib_memory/archives/` — Timestamped archive subfolders created by `initialize.py --upgrade`; each subfolder contains the full pre-upgrade `.aib_memory/` content (excluding nested archives).

- `.aib_memory/requests/` — Contains request artifact subfolders following the pattern `R-YYYYMMDD-HHmi-<title-slug>/`; individual items are not listed.

- `.aib_memory/logs/` — Per-action execution log files; excluded from VCS.

- `.github/` — GitHub repository configuration folder.

- `.github/workflows/` — GitHub Actions workflow definitions.

- `.github/workflows/aib-semver-patch-bump-and-log.yml` — CI workflow that auto-bumps the SemVer patch version on PRs targeting main, rotates the marker file, writes the per-version log, creates the versioned brain zip, and optionally posts a PR changelog comment.

- `.gitignore` — Git ignore rules; excludes `.aib_memory/`, `.venv/`, `__pycache__/`, and other ephemeral artifacts from version control.

- `docs/` — Developer-facing supplementary documentation and prompt helpers stored outside the AIB brain folder.

- `docs/aib-refresh-context-AIB_version.md` — Prompt for refreshing `.aib_memory/context.md` with the current workspace knowledge synthesis.

- `docs/Analyze_AIB.prompt.md` — Developer-facing prompt template for running an AIB analysis session.

- `docs/Copilot_Issue_Assignment_Rules.md` — Rules governing how GitHub Copilot is assigned to issues in this repository.

- `docs/Development_and_Deployment_Specification.md` — Development and deployment specification document for the AIB project.

- `logs/` — Per-version release log files committed to VCS.

- `logs/next_version_changes.md` — Curated, append-only bullet list of user-visible changes maintained by the AI agent during implementation; preferred `Changes:` source for the next release log; reset to empty by CI after incorporation; VCS-tracked.

- `versions/` — Versioned `.aib_brain/` zip archives committed to VCS; used for installation.

- `write_analysis.py` — Developer utility script that writes an externally-drafted analysis file into `.aib_memory/`; not part of the AIB framework.

- `scripts/` — Standalone Python scripts for CI and administrative tasks.

- `scripts/release_bookkeeping.py` — CI release script; bumps patch version, rotates SemVer marker, writes version log, creates versioned zip archive in `versions/`, prefers curated change log over commit subjects, and resets the curated file after incorporation.

- `tests/` — Pytest test suite.

- `tests/conftest.py` — Shared pytest fixtures for test isolation.

- `tests/test_analysis_prompt_structure.py` — Structural tests asserting required sections and behaviour of `aib-analyze.md` and `analysis-convention.md`; includes assertions for removed sections, Plan schema fields, Decision Points Catalog, and brownfield check relocation (TestBrownfieldCheckRelocation).

- `tests/test_context_formatting_rules.py` — Regression tests asserting formatting rules are present in `context-convention.md` and that `aib-refresh-context.md` contains the corresponding formatting checklist. Covers no-tables, blank-line-between-bullets, heading-depth-cap, two-sentence entry-length enforcement (rule 16), requirements identifier rule (FR-NNN/NFR-NNN), and inventory grouping rule.

- `tests/test_artifact_placement.py` — Tests for two-phase artifact placement: verifies that `move-request-artifacts.py` moves `plan-<ID>.md` and `analysis-<ID>.md` from `.aib_memory/` root to the request subfolder; includes idempotency and close-request integration tests.

- `tests/test_close_request.py` — Integration tests for `close-request.py`; includes non-empty attachments warning assertion (SC-5).

- `tests/test_create_request.py` — Integration tests for `create-request.py`; verifies no `request.md`/`implementation.md` seeding.

- `tests/test_initialize.py` — Integration tests for `initialize.py`; includes `input.md` creation assertion, `instructions.md` seeding and idempotency assertions, `attachments/` creation (SC-1), and `attachments/` idempotency (SC-2).

- `tests/test_instructions_md.py` — Tests asserting `instructions.md` exists and contains the curated-change-log directive, all three prompts contain the pre-read step, and `README.md` documents the feature.

- `tests/test_lifecycle_e2e.py` — End-to-end lifecycle integration tests.

- `tests/test_menu.py` — Unit tests for `menu.py`.

- `tests/test_questions_in_input_md.py` — Tests asserting the Questions-in-input.md workflow: Q-block generation, answer application, section clearing behavior, and the all-answered pre-check gate that halts the Answer Application Sub-flow when any Q-block is unanswered.

- `tests/test_release_bookkeeping.py` — Integration tests for the curated-source preference, fallback, lifecycle reset, and idempotency of `scripts/release_bookkeeping.py`.

- `tests/test_reverse_engineer.py` — Unit tests for `file-inventory.py`.

- `tests/test_semver_workflow_structure.py` — Structural YAML tests verifying the semver bump workflow permissions block and post-changelog-comment step configuration.

- `tests/test_requirements_analysis_convention.py` — Structural integrity tests for `requirements-analysis-convention.md`: verifies file existence, preamble sections, eight category sections, checkbox format, framework citations, and pass/threshold gate language.

- `README.md` — Project overview and installation instructions referencing `versions/` folder.

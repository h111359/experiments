# Product Context

> **Auto-generated** by `aib-context.md` on 2026-04-17 17:15 +0300.
> This document is a synthesis of all product documentation and workspace sources, including `.aib_brain/` and `.aib_memory/`. It is fully replaced on each execution.

## Product Identity

AI Builder (AIB) is a minimal, model-agnostic framework for specification-driven development in a repository workspace. It provides deterministic, file-first workflows for managing structured work items (requests), maintaining convention-governed product documentation, and automating release bookkeeping via CI.

Primary actors:
- Developer — creates and reviews requests, interacts through `input.md` and prompt actions.
- AI Automation Agent — executes prompt-driven workflows to create requests, implement scope, and generate documentation.
- AIB Maintainer — owns `.aib_brain/` assets, enforces conventions, manages CI workflows.

The product is in active use. Current version: **v1.2.0**. It is scoped to repository-local operation and does not provision cloud infrastructure. Its explicit non-responsibilities include deep infrastructure provisioning and multi-workspace coordination.

## Business Context

AIB operates in the software engineering / internal tooling domain. It supports the following key business processes:

- **Initialize AIB workspace**: Seeds `.aib_memory/` registers, `context.md`, and `input.md` from `.aib_brain/` assets. Idempotent after first successful seed.
- **Communicate user intent**: Developer writes into `.aib_memory/input.md`; the AI agent reads it, auto-creates a request, archives the input, and resets the file.
- **Execute analysis workflow**: AI agent generates `request.md` (auto-request branch) and/or `analysis.md` with Assumptions, Plan, Testing, Documentation, Code Scan, Internal Review, and Multi-Perspective Stakeholder Review sections.
- **Execute implement workflow**: AI agent applies request scope, updates product docs, creates/appends `implementation.md`, and auto-closes the request upon successful completion.
- **Release bookkeeping**: CI-automated patch bump, per-version log creation, and `.aib_brain/` zip archive in `versions/` on pull request events targeting `main`.

Organizational units: Product Team (request lifecycle), AIB Maintainers (framework assets), Repository Contributors (read/write access gated by repository permissions).

External dependencies:
- GitHub — repository hosting and version control.
- GitHub Actions — CI runner for automated release bookkeeping.

No regulatory bodies or external data providers are identified. All artifacts are classified as Internal engineering documentation.

## Requirements Summary

Functional requirements:

- FR-001: The system manages exactly one Active request in the workspace at a time.
- FR-002: `create-request.py` creates a request folder and register entry; it does NOT seed `request.md` or `implementation.md` (removed in v1.2.0).
- FR-003: The `aib-analysis.md` prompt auto-creates a request from `input.md` when no Active request exists; it archives `input.md` content and resets the file as the **last action** of the run (after all analysis artifacts are fully written). After reset, the `## Active request` line in `input.md` reflects the current active request ID and title (format: `<request_id> — <title>`); the literal string `No active request` is NOT present after reset.
- FR-004: The system generates an `analysis.md` artifact per request and updates `request.md` with sections: Assumptions, Plan, Testing, Documentation, Questions & Decisions, Code and Asset Scan, Internal Review, and Multi-Perspective Stakeholder Review. The prompt enforces a preflight halt gate: if multiple Active requests exist, execution stops immediately with a human-readable error.
- FR-005: The `aib-implement.md` prompt generates `implementation.md` from scratch (no pre-seeded template), appends an implementation log entry, and auto-closes the request by invoking `close-request.py` upon successful completion.
- FR-006: If no Active request exists when `aib-implement.md` is invoked, it auto-triggers `aib-analysis.md` before proceeding. It does this autonomously without asking for user permission or confirmation.
- FR-007: The `input.md` file supports two opt-in toggles: "No changes — provide answer only" (writes timestamped `answer-<timestamp>.md` in the request folder and resets `input.md` with the active request ID; MUST NOT modify `request.md`, `analysis.md`, or any other file); "Skip analysis document generation" (updates `request.md` but skips `analysis.md` output).
- FR-008: The system reads `references.md` to determine which files may be edited (`edit_allowed = Y`).
- FR-009: The system reads the `context-convention.md` for the `context.md` product-doc artifact and fails closed if the convention file cannot be read.
- FR-010: The interactive menu displays copy-paste-ready prompt invocations for `aib-analysis.md`, `aib-implement.md`, and `aib-context.md`; it does NOT expose lifecycle commands (Create request, Close request) or an exit option.
- FR-011: A PR bookkeeping workflow bumps the patch version marker, creates a new per-version log under `logs/`, and produces a versioned zip of `.aib_brain/` in `versions/`.

Non-functional requirements:

- NFR-001: Workflows must be model-agnostic and vendor-agnostic.
- NFR-002: Active request resolution must be deterministic (filesystem-only, fail on invalid state).
- NFR-003: Missing convention mapping must cause a fail-closed response with no partial writes.
- NFR-004: Tool scripts must run on Python 3.10+ using the standard library only.
- NFR-005: The release bookkeeping workflow must be idempotent on reruns.
- NFR-006: `inputs/input-archive-*.md` files in request folders MUST NOT be read by `aib-implement.md` or any other prompt.

Acceptance criteria:
1. Initialization creates `.aib_memory/` registers, `context.md`, and `input.md` with the seed template.
2. Creating a request via `create-request.py` produces only the request folder and a register row; no `request.md` or `implementation.md` in the folder.
3. Running `aib-analysis.md` with non-empty `input.md` and no Active request creates a request folder with AI-generated `request.md`, archives `input.md`, and resets `input.md`.
4. Running `aib-implement.md` on an Active request creates `implementation.md` from scratch, applies scope, and closes the request.
5. The CLI menu shows no lifecycle commands and no exit option; prompt invocations are displayed.
6. Release bookkeeping increments the patch version, writes a per-version log, and produces `versions/aib_brain_vX.Y.Z.zip`; the CI workflow commits `versions/` alongside `.aib_brain/` and `logs/` to the PR branch.
7. Exactly one SemVer marker `v1.2.0` exists in `.aib_brain/`.

## Architecture & Key Decisions

### Component Map

| Component | Location | Responsibility |
| --- | --- | --- |
| AIB Brain Assets | `.aib_brain/` | Reusable prompts, conventions, templates, and tool scripts; the deterministic workflow engine. Never modified by tool scripts; replaced by AIB Maintainers on framework upgrade. |
| Input Channel | `.aib_memory/input.md` | Ephemeral user-agent communication file; seeded by `initialize.py`; read by `aib-analysis.md`; archived per request; reset after processing. |
| AIB Command Menu | `.aib_brain/run.bat`, `.aib_brain/run.sh`, `.aib_brain/tools/menu.py` | Terminal UI launcher; displays copy-paste prompt invocations; surfaces non-excluded tool scripts; streams stdout/stderr via Popen tee pattern; writes per-action log files. |
| AIB Tool Scripts | `.aib_brain/tools/*.py` | Python scripts implementing deterministic AIB actions (initialize, create-request, close-request, etc.). |
| AIB Conventions | `.aib_brain/conventions/` | Markdown files defining the required structure, formatting rules, and quality gates for each managed document type. |
| AIB Prompts | `.aib_brain/prompts/` | Markdown prompt files (`aib-*.md`) invoked directly in an AI coding interface to produce AIB artifacts. |
| AIB Templates | `.aib_brain/templates/` | Seed templates used by `initialize.py` to create initial `.aib_memory/` document stubs (register files; NOT request or implementation artifacts). |
| AIB Memory Artifacts | `.aib_memory/` | Requests, references register, `context.md`, and `input.md`; persist workspace state. |
| Requests Register | `.aib_memory/requests_register.md` | Markdown table tracking all requests with their lifecycle state, folder path, and timestamps. |
| References Register | `.aib_memory/references.md` | Markdown table listing all referenced files, their types, and whether automation may edit them. |
| Request Artifacts | `.aib_memory/requests/<request-folder>/` | Per-request folder containing `request.md` (AI-generated), `implementation.md` (created on-demand), optionally `analysis.md`; and `inputs/input-archive-*.md` for audit. |
| Release Bookkeeping Script | `scripts/release_bookkeeping.py` | Validates SemVer marker, bumps patch, rotates marker file, writes per-version log, and creates versioned `.aib_brain/` zip in `versions/`. |
| Versioned Archives | `versions/` | Versioned zip archives of `.aib_brain/` (`aib_brain_vX.Y.Z.zip`); committed to VCS; used for installation. |
| GitHub Actions Workflow | `.github/workflows/aib-semver-patch-bump-and-log.yml` | CI automation for patch bump on PR events targeting `main`. |
| Action Execution Logs | `.aib_memory/logs/` | Per-action log files (`aib-action-<timestamp>-<action-id>.log`) written by `menu.py`; excluded from VCS. |
| Release Version Logs | `logs/` | Per-version log files (`version_vX.Y.Z_log.md`) written by CI; committed to VCS. |

### Integration Points

- GitHub (VCS): repository hosting and PR events; data flows: developer push/pull, CI push (marker rotation + version log + zip).
- GitHub Actions (CI runner): receives PR events, executes release bookkeeping; data flows: process invocation, file writes back to PR branch.

### Key Architectural Decisions

**ADR-0001 — Single SemVer marker file for version**
- Context: deterministic version detection without package managers.
- Decision: represent active version as exactly one empty file in `.aib_brain/` named `vMAJOR.MINOR.PATCH`.
- Rationale: tool-agnostic, easy to validate, low merge conflict risk.
- Consequences: strict enforcement required; multiple markers cause a fail state.

**ADR-0002 — Fail-closed convention enforcement**
- Context: missing convention files can cause malformed docs or state drift.
- Decision: if a required convention mapping cannot be resolved, do not edit the product-doc and record a blocker.
- Rationale: prevents silent corruption; favors safety over leniency.

**ADR-0003 — Separation of brain and memory folders**
- Context: framework assets must survive workspace-specific changes and be upgradeable as a unit.
- Decision: all reusable assets live in `.aib_brain/` (replaceable on upgrade); all workspace-specific artifacts live in `.aib_memory/` (persistent across upgrades).
- Consequences: `.aib_brain/` must never be written by tool scripts.

**ADR-0004 — Pre-merge CI write model for release bookkeeping**
- Context: version log and marker rotation must be committed before the PR is merged.
- Decision: the GitHub Actions workflow commits directly to the PR branch before merge.
- Rationale: ensures the version log and bumped marker land atomically with the feature changes.

**ADR-0005 — input.md as ephemeral communication channel (v1.2.0)**
- Context: requiring explicit "Create request" CLI commands added friction to the conversational workflow.
- Decision: introduce `input.md` as the primary user-agent communication file; `aib-analysis.md` auto-creates a request when no Active request exists and `input.md` is non-empty.
- Rationale: reduces ceremony; maintains the single-Active-request invariant; archives user input for audit.
- Consequences: `input.md` content is ephemeral; each analysis run archives and resets it.

**ADR-0006 — Remove template seeding from create-request.py (v1.2.0)**
- Context: `request.md` is now AI-generated from `input.md`; `implementation.md` is generated on-demand.
- Decision: `create-request.py` creates only the folder and register row; no `request.md` or `implementation.md` seeded from templates.
- Rationale: AI-generated `request.md` is richer than a template stub; `implementation.md` has no content before implementation begins.

**ADR-0007 — Auto-close on successful implementation (v1.2.0)**
- Context: closing the request was a manual step prone to omission.
- Decision: `aib-implement.md` invokes `close-request.py` after confirmed successful implementation.
- Consequences: auto-close only fires after no unresolved test failures; reuses `close-request.py` without duplicating its logic.

### Technology Stack

- Language: Python 3.10+ (standard library only for tool scripts).
- Documentation format: Markdown.
- CI platform: GitHub Actions.
- Version control: Git / GitHub.
- No cloud infrastructure is provisioned; all resources are repo/CI/filesystem-based.

### Quality Attributes

Priorities in order: reliability (deterministic fail-closed) > scalability (chunked reads for large repos) > security (edit gating by references register) > cost (file-based, no cloud spend).

## Technical Design

### Module Breakdown

**Tool scripts** (`.aib_brain/tools/`):

- `initialize.py` — Seeds `.aib_memory/` structure, writes `references.md`, `requests_register.md`, `context.md`, and `input.md`. Idempotent; fails without partial writes on invalid workspace state.
- `create-request.py` — Validates no Active request, creates request folder with deterministic naming (`<request_id>-<title-slug>`), appends register row as Active. Does NOT write `request.md` or `implementation.md` (removed in v1.2.0).
- `close-request.py` — Marks the Active request Closed; auto-closes any open iterations (legacy) and prints a notice per iteration before closing.
- `menu.py` — Interactive tool launcher. Lifecycle scripts (`create-request.py`, `close-request.py`) and internal helpers (`reverse-engineer.py`) are in `EXCLUDE_SCRIPTS` and do not appear in the menu. Displays copy-paste-ready prompt invocations for `aib-analysis.md`, `aib-implement.md`, and `aib-context.md`. Streams subprocess stdout/stderr via Popen tee pattern. Writes per-action log files to `.aib_memory/logs/`. Press `0`, `q`, or `Q` to quit. Uses ANSI escape sequences (`\033[H\033[J`) for blink-free screen clearing via `_enable_ansi_windows()` (one-time Windows VT enablement via ctypes at startup); buffers the entire menu into an `io.StringIO` and writes to stdout in a single call. Auto-refreshes every 3 seconds via `get_key(timeout=_REFRESH_TIMEOUT_S)` using `msvcrt.kbhit()` polling (Windows) or `select.select()` (Unix) — no background threads; `_REFRESH_TIMEOUT_S: float = 3.0` is the sole tunable constant. Renders a fixed `0) Quit` footer line; `choose_action()` returns `None` on `QUIT`/`DIGIT:0`; `main()` breaks the loop on `None`.
- `reverse-engineer.py` — Walks the workspace filesystem and emits a deterministic JSON Lines file inventory for use by `aib-context.md`.
- `common.py` — Shared utilities: `parse_markdown_table`, `format_markdown_table`, `read_text`, `write_text`, `slugify`, `now_iso`, `now_compact_request_id`, `ensure_workspace`, `ValidationError`, and related helpers.
- `test_common.py` — Unit tests for `common.py` helpers; excluded from the interactive menu.

**Prompt actions** (`.aib_brain/prompts/`):

- `aib-context.md` — Synthesizes and fully replaces `.aib_memory/context.md` from workspace sources.
- `aib-analysis.md` — Two-branch prompt: (1) if Active request exists, generates `analysis.md` and updates `request.md` optional sections; (2) if no Active request exists, reads `input.md`, auto-creates a request via `create-request.py`, generates AI-authored `request.md` with all 14 mandatory sections (sections 1–6 non-empty), archives `input.md`, proceeds with analysis, then resets `input.md` with active request ID as the final step. Supports two opt-in toggles: "No changes" (writes only timestamped `answer-<timestamp>.md` in request folder, resets `input.md` with active request ID, MUST NOT modify `request.md`/`analysis.md`/any other file, then stops) and "Skip analysis" (update `request.md`, skip `analysis.md` output). Standard flow also resets `input.md` as its final step unless triggered from `aib-implement.md`.
- `aib-implement.md` — Guides execution of the active request scope. Auto-triggers `aib-analysis.md` without user confirmation if no Active request exists. Generates `implementation.md` from scratch (no pre-seeded template required). Invokes `close-request.py` after confirmed successful implementation. Must NOT read `inputs/input-archive-*.md` files.

**Conventions** (`.aib_brain/conventions/`):

Each convention file defines the required structure, content guidance, formatting rules, and quality gates for a specific document type. Conventions cover: `context.md`, `request.md` (14 mandatory sections including Code Scan, Internal Review, Multi-Perspective Stakeholder Review; no `## Amends` section), `references.md`, `requests_register.md`, `implementation.md`, `analysis.md` (6 mandatory sections: Executive Summary, Domain Knowledge Essentials, Technical Knowledge and Terms, Research Results, External Benchmarking, Minimal Spikes and Experiments), and a range of coding conventions (Python, JavaScript, SQL, CSS, HTML, React, Django, Flask, C#, Scala, DAX, UI/UX, general).

**Templates** (`.aib_brain/templates/`):

- `references-template.md` — Seed template for `references.md`; pre-populates `REF-0001` (AIB Context) and `REF-0002` (AIB Concepts) rows.
- `requests_register-template.md` — Seed template for `requests_register.md` with the canonical column schema.
- `request-template.md` — Legacy seed template; no longer used by `create-request.py` as of v1.2.0; retained for reference.

**Release bookkeeping** (`scripts/`):

- `release_bookkeeping.py` — Standalone script run in CI. Locates SemVer markers, computes bumped version, rotates marker file, writes new version log, and creates `versions/aib_brain_vX.Y.Z.zip` using `zipfile` from the standard library. Idempotent on reruns.

### Key Algorithms

**ALG-0001 — SemVer Patch Bump**
Locates the base marker from the git tree and the worktree marker from the filesystem. Computes target version: $v' = (X, Y, Z+1)$ where base is $(X, Y, Z)$. Validates exactly one marker at each location. Rotates marker (delete old, create new). Writes new per-version log and creates brain zip. Idempotent on reruns.

**ALG-0002 — Active Request Resolution**
Reads `requests_register.md`, selects row with `state = Active`. Enforces invariant $|ActiveRequests| = 1$; fails with explicit error if zero or more than one Active. Filesystem-only.

**ALG-0003 — Auto-Request Creation from input.md**
`aib-analysis.md` reads `input.md`'s `## Input` section; derives a title; invokes `create-request.py`; generates `request.md` from input content with all 14 mandatory sections (sections 1–6 non-empty); archives `input.md` to `inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md`; proceeds with standard analysis flow; resets `input.md` to seed template **as the last step** after all artifacts are confirmed written; replaces `No active request` in `## Active request` with the active request ID and title.

### Inter-component Communication

All inter-component communication at runtime is local filesystem reads/writes (Markdown files). No network communication between components at runtime. CI pipeline communicates via git push to PR branch.

### Configuration

All tool scripts accept parameters via CLI arguments (`--workspace`, `--title`, `--request-id`, etc.). No config files or environment variables are required at runtime. The `EXCLUDE_SCRIPTS` constant in `menu.py` governs which scripts are hidden from the interactive menu.

### Runtime Sequences

- SEQ-001: Initialize workspace — Developer invokes menu → tool scripts read `.aib_brain/` assets → create `.aib_memory/` structure → write registers and `input.md`.
- SEQ-002: Create request (AI-driven) — Developer writes intent to `input.md` → runs `aib-analysis.md` → prompt auto-creates request, archives input, generates `request.md` and `analysis.md`.
- SEQ-003: Implement request — Developer runs `aib-implement.md` → prompt generates `implementation.md` → closes request via `close-request.py`.
- SEQ-004: Release bookkeeping in CI — PR event triggers GitHub Actions → release script locates markers → bumps patch → rotates marker → writes version log → creates `.aib_brain/` zip → pushes to PR branch.
- SEQ-005: Execute action with real-time streaming — Developer selects action in menu → menu spawns subprocess via Popen → tee pattern streams stdout/stderr to terminal → writes log file → reports exit code.

## Data Architecture

### Data Sources

| Source | Owner | Ingestion method | Refresh frequency | Classification |
| --- | --- | --- | --- | --- |
| Workspace repository filesystem | Repository Maintainers | On-demand batch read | Ad-hoc | Internal |

The workspace filesystem is the sole source system. AIB tools read a bounded set of Markdown files and write derived artifacts back to `.aib_memory/`. No external databases or APIs are ingested.

### Core Data Entities

| Entity | Primary key | Description | Constraint |
| --- | --- | --- | --- |
| REQUEST | `request_id` | Tracked work unit with lifecycle state | Exactly one Active per workspace |
| INPUT | N/A | Ephemeral user-agent communication channel (`input.md`) | Overwrite-friendly; reset to seed after processing |
| REFERENCE | `ref_id` | Register row describing a file and its edit permissions | `path` must be unique |
| CONTEXT | `path` | Convention-governed unified product knowledge file (`context.md`) | Editable only when `edit_allowed = Y`; fully replaced on each `aib-context.md` run |
| VERSION_LOG | `version` | Release bookkeeping artifact | One log per bumped version; never modified after creation |
| BRAIN_ARCHIVE | `version_marker` | Versioned zip of `.aib_brain/` in `versions/` | Created by CI on each version bump; idempotent |

Physical storage: Markdown tables in fixed files — `requests_register.md` (REQUEST), `references.md` (REFERENCE).

### Data Lineage

Developer input (`input.md`) → `aib-analysis.md` → `request.md` + `analysis.md` → `aib-implement.md` → `implementation.md` + auto-close. Release bookkeeping: git history (source) → `release_bookkeeping.py` → `logs/version_vX.Y.Z_log.md` + `.aib_brain/vX.Y.Z` marker + `versions/aib_brain_vX.Y.Z.zip`. `.aib_memory/context.md` is the unified product knowledge sink.

### Data Storage

- `.aib_memory/` — operational registers, `context.md`, `input.md`, and request artifact folders; backed by Git history.
- `.aib_memory/requests/<request-folder>/` — per-request artifacts: `request.md`, `implementation.md`, optionally `analysis.md`, and `inputs/input-archive-*.md` (audit trail).
- `.aib_memory/logs/` — action execution logs; excluded from VCS; no auto-cleanup.
- `.aib_brain/` — framework assets including the active SemVer marker file (e.g., `v1.2.0`); committed to VCS.
- `logs/` — release version logs; committed to VCS.
- `versions/` — versioned `.aib_brain/` zip archives; committed to VCS; used for installation.

### Data Access Patterns

- Requests Register: read by tool scripts to resolve Active request; read by agents to understand workspace state.
- References Register: read by tool scripts and AI agents before any product-doc edit to confirm `edit_allowed = Y`.
- `input.md`: written by developer; read by `aib-analysis.md`; archived; reset.
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
- `edit_allowed` flag in references register is the primary quality gate for product-doc edits.

## Security & Compliance

### Access Control

Repository-level access is managed through GitHub repository permissions. AIB automation is gated by the references register: product-doc edits are only permitted when `edit_allowed = Y`. GitHub Actions CI workflow is restricted to PRs from the same repository; forked PRs are skipped. `GITHUB_TOKEN` requires Read and Write permissions in repository Actions settings.

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

Download the versioned `.aib_brain/` archive from the `versions/` folder in this repository (e.g., `versions/aib_brain_v1.2.0.zip`). Unzip into the workspace root. Run `.aib_brain\run.bat` (Windows) or `.aib_brain/run.sh` (Linux/macOS) for the interactive menu. GitHub Actions workflow in `.github/workflows/` requires Actions permissions set to Read and Write. CI uses a pre-merge write model.

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

1. Download `aib_brain_v1.2.0.zip` from the `versions/` folder in this repository.
2. Unzip and place `.aib_brain/` at the workspace root.
3. Ensure Python 3.10+ is available on PATH.
4. Run `.aib_brain\run.bat` (Windows) or `.aib_brain/run.sh` (Linux/macOS).
5. Select "Initialize AIB workspace" on first use.
6. To start a request: write intent into `.aib_memory/input.md` under `## Input`, then run the `aib-analysis.md` prompt.
7. Install `pytest` for running the test suite (`pytest tests/` from workspace root).

### Testing Strategy

- `conftest.py` — Shared pytest fixtures: temporary workspace builder, path configuration.
- `test_initialize.py` — Integration tests for `initialize.py`; includes assertion for `input.md` creation and idempotency.
- `test_create_request.py` — Integration tests for `create-request.py`; verifies folder creation, register update, and that `request.md` / `implementation.md` are NOT created.
- `test_close_request.py` — Integration tests for `close-request.py`; includes auto-close of iterations.
- `test_lifecycle_e2e.py` — End-to-end lifecycle test: initialize → create-request → close-request; verifies `request.md` is NOT created by `create-request.py`.
- `test_menu.py` — Unit tests for `menu.py`: `MenuState`, `build_command`, `_run_and_tee`, `_make_log_path`, lifecycle script exclusion from menu, and related helpers.
- `test_reverse_engineer.py` — Unit tests for `reverse-engineer.py`: file inventory and exclusion logic.
- `test_common.py` — Unit tests for `common.py` helpers (located in `.aib_brain/tools/`).

All tests use `tempfile.TemporaryDirectory` for isolation. All 73 tests pass as of v1.2.0 (updated by R-20260417-1254: removed `test_reverse_engineer_present`; `reverse-engineer.py` is now in `EXCLUDE_SCRIPTS` and excluded from the menu).

### CI/CD Pipeline

- Trigger: PRs to `main` on `opened`, `reopened`, `synchronize`; bot-triggered runs skipped.
- Gate: exactly one valid SemVer marker must exist in `.aib_brain/`.
- Actions: validate marker, bump patch, rotate marker file, write version log, create `.aib_brain/` zip in `versions/`, commit and push to PR branch (staged files: `.aib_brain/`, `logs/`, `versions/`).
- Prerequisite: GitHub Actions Read and Write permissions; fork PRs excluded.

### Branching and PR Conventions

- Branch naming: `issue/<number>`.
- PRs must include: summary of `.aib_brain/` changes, SemVer bump justification, and migration notes for MAJOR changes.
- Squash merge is recommended.

### Known Developer Experience Notes

- Non-ASCII output on Windows handled by `encoding="utf-8"`, `errors="replace"` in Popen streaming.
- Action log files accumulate locally without auto-cleanup.
- Iteration lifecycle scripts (`create-iteration.py`, `close-iteration.py`) are deprecated and excluded from the menu; treated as legacy.
- The CLI menu no longer provides Create request, Close request, or Exit options; these are handled by the AI prompts.

## Constraints & Assumptions

### Technical Constraints

- Exactly one Active request is permitted per workspace at any time.
- Automation must not modify files where `edit_allowed = N` in the references register.
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

- Legacy iteration-related references (`create-iteration.py`, `close-iteration.py`) may be removed from the codebase in a future version once all related test fixtures are updated.

## Glossary

**ADR**: Architecture Decision Record — a document capturing a significant architectural choice, its rationale, and consequences.

**AI Builder**: Minimal, model-agnostic framework for specification-driven development in a repository workspace. Abbreviated AIB.

**AIB**: Abbreviation for AI Builder.

**Analysis**: A reasoning artifact (`analysis.md`) generated per request; also updates `request.md` with Assumptions, Plan, Testing, Documentation, Questions & Decisions, Code and Asset Scan, Internal Review, and Multi-Perspective Stakeholder Review sections.

**Auto-close**: Behavior introduced in v1.2.0 whereby `aib-implement.md` invokes `close-request.py` automatically after successful implementation.

**Auto-request**: Behavior of `aib-analysis.md` introduced in v1.2.0; when no Active request exists and `input.md` is non-empty, it auto-creates a request and generates `request.md` from `input.md` content.

**Brain Folder**: Folder (`.aib_brain/`) containing reusable AIB assets: prompts, conventions, templates, and tool scripts.

**CI**: Continuous Integration — automated pipeline that runs on pull request events.

**Convention File**: A file in `.aib_brain/conventions/` that defines the required structure and validation rules for a specific product doc or coding standard.

**FR**: Functional Requirement.

**Implementation Log**: Request-scoped on-demand record of changes, tests, and outcomes (`implementation.md`); created from scratch by `aib-implement.md`.

**Input Archive**: File written by `aib-analysis.md` to `<request-folder>/inputs/input-archive-<YYYY-MM-DD_HH-MI-SS>.md` preserving the original `input.md` content for audit; MUST NOT be read by any prompt.

**input.md**: Ephemeral primary user-agent communication channel. Seeded by `initialize.py`; written by the developer; read and processed by `aib-analysis.md`; reset to seed template after processing.

**Iteration**: (Deprecated) A numbered step within a request. Removed as of R-20260414-1421.

**Memory Folder**: Folder (`.aib_memory/`) containing workspace-specific artifacts: requests, registers, `context.md`, and `input.md`.

**NFR**: Non-Functional Requirement.

**PII**: Personally Identifiable Information.

**Product Doc**: A convention-governed documentation file listed in the references register; editable by automation only when `edit_allowed = Y`.

**Prompt Action**: A `.aib_brain/prompts/aib-*.md` file that defines the instructions an AI agent executes to produce a specific AIB artifact. Invoked directly in an AI coding interface; model-agnostic.

**References Register**: Markdown table (`.aib_memory/references.md`) listing referenced files, their types, and whether automation may edit them.

**Request**: Tracked unit of work with a stable request identifier (`R-YYYYMMDD-HHmi`) and lifecycle state (`Active` or `Closed`).

**SemVer**: Semantic Versioning, following the pattern MAJOR.MINOR.PATCH.

**SemVer Marker File**: A single empty file in `.aib_brain/` whose filename encodes `vMAJOR.MINOR.PATCH`; represents the active product version.

**SLO**: Service Level Objective.

**Tool Script**: A Python script in `.aib_brain/tools/` implementing a deterministic AIB action.

**VCS**: Version Control System (Git in this workspace).

**Versioned Archive**: Zip file created by CI per version bump, stored in `versions/aib_brain_vX.Y.Z.zip`; committed to VCS; used for AIB installation.

**Workspace**: The repository root containing both the AIB brain folder and memory folder plus any product-specific code and configuration.

## Workspace File Inventory

- `.aib_brain/` — AIB framework assets: prompts, conventions, templates, tool scripts, and the active SemVer marker; never modified by tool scripts.
- `.aib_brain/Concepts.md` — Authoritative framework definition covering goals, concepts, objectives, invocation contract, and holistic workflow.
- `.aib_brain/README.md` — User guide for working with AIB from the workspace root, including quick-start and prompt invocation reference. Scripts in `.aib_brain/tools/` are invoked automatically by AIB prompts; only `initialize.py` is intended for direct user invocation (first-time workspace setup).
- `.aib_brain/conventions/` — Convention files governing the structure and coding standards for each managed document type and programming language.
- `.aib_brain/conventions/analysis-convention.md` — Convention governing the structure and content requirements for `analysis.md` request artifacts; defines 6 mandatory sections (Executive Summary, Domain Knowledge Essentials, Technical Knowledge and Terms, Research Results, External Benchmarking, Minimal Spikes and Experiments).
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
- `.aib_brain/conventions/context-convention.md` — Authoritative convention defining the required structure, content guidance, and formatting rules for `context.md`.
- `.aib_brain/conventions/implementation-convention.md` — Convention defining the format, lifecycle, and append-only rules for `implementation.md` request artifacts.
- `.aib_brain/conventions/references-convention.md` — Convention governing the structure and validation rules for `references.md`.
- `.aib_brain/conventions/request-convention.md` — Convention governing the structure and content requirements for `request.md` request artifacts; defines 14 mandatory sections including Code and Asset Scan, Internal Review, and Multi-Perspective Stakeholder Review; no `## Amends` section.
- `.aib_brain/conventions/requests_register-convention.md` — Convention governing the structure and validation rules for `requests_register.md`.
- `.aib_brain/prompts/` — Prompt action files invoked in an AI coding interface to drive the AIB workflow.
- `.aib_brain/prompts/aib-analysis.md` — Prompt for auto-creating requests from `input.md` and/or producing analysis artifacts; supports "No changes" and "Skip analysis" opt-in toggles.
- `.aib_brain/prompts/aib-context.md` — Prompt for producing or fully replacing `.aib_memory/context.md` with a structured workspace knowledge synthesis.
- `.aib_brain/prompts/aib-implement.md` — Prompt for executing the active request scope, generating `implementation.md` on-demand, and auto-closing the request on success.
- `.aib_brain/run.bat` — Windows entry point script that launches `menu.py` with the workspace root resolved automatically.
- `.aib_brain/run.sh` — Linux/macOS entry point script that launches `menu.py` with the workspace root resolved automatically.
- `.aib_brain/templates/` — Seed templates used by `initialize.py` to create default `.aib_memory/` register files.
- `.aib_brain/templates/references-template.md` — Seed template for `references.md`.
- `.aib_brain/templates/request-template.md` — Legacy seed template for `request.md`; no longer used by `create-request.py` as of v1.2.0.
- `.aib_brain/templates/requests_register-template.md` — Seed template for `requests_register.md`.
- `.aib_brain/tools/` — Python tool scripts invoked by the CLI menu to perform AIB lifecycle operations.
- `.aib_brain/tools/close-request.py` — Tool script that transitions the active request to Closed state and updates the requests register.
- `.aib_brain/tools/common.py` — Shared utility functions (register parsing, path resolution, file I/O) used across all tool scripts.
- `.aib_brain/tools/create-request.py` — Tool script that creates a new request folder and register entry; does not seed `request.md` or `implementation.md` (as of v1.2.0).
- `.aib_brain/tools/initialize.py` — Tool script that seeds the `.aib_memory/` folder with default artifacts including `input.md` on first use of a workspace.
- `.aib_brain/tools/menu.py` — Interactive CLI menu; blink-free ANSI-based rendering; auto-refresh every 3 seconds; lifecycle scripts excluded; displays copy-paste prompt invocations; press 0/q/Q to quit.
- `.aib_brain/tools/reverse-engineer.py` — Tool script that emits a JSONL file inventory of the workspace for use by `aib-context.md`.
- `.aib_brain/tools/test_common.py` — Unit tests for the shared utility functions in `common.py`.
- `.aib_brain/v1.2.0` — Active SemVer marker file (empty file; filename encodes the current AIB framework version v1.2.0).
- `.aib_memory/` — Workspace-specific AIB memory artifacts.
- `.aib_memory/context.md` — This file; unified workspace product knowledge synthesis.
- `.aib_memory/input.md` — Ephemeral user-agent communication channel; seeded by `initialize.py`; reset after each analysis run.
- `.aib_memory/references.md` — References register listing files, types, and edit permissions.
- `.aib_memory/requests_register.md` — Requests register tracking lifecycle state for all requests.
- `.aib_memory/requests/` — Per-request artifact folders.
- `.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/` — Request folder for R-20260417-1440: Menu refresh without blinking.
- `.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/request.md` — AI-generated request scope, plan, and constraints for the blink-free menu rendering feature.
- `.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/implementation.md` — Implementation log for R-20260417-1440; records ANSI-based rendering changes and test outcomes.
- `.aib_memory/requests/R-20260417-1440-menu-refresh-without-blinking/test_clear_screen_ansi.py` — Request-scoped unit tests: T1 (os.system not called) and T2 (ANSI sequences written) for the updated `clear_screen()`.
- `.aib_memory/requests/R-20260417-1534-add-quit-option-to-menu/` — Request folder for R-20260417-1534: Add quit option to menu.
- `.aib_memory/requests/R-20260417-1534-add-quit-option-to-menu/request.md` — AI-generated request scope and plan for restoring the 0) Quit option.
- `.aib_memory/requests/R-20260417-1534-add-quit-option-to-menu/analysis.md` — Analysis artifact for R-20260417-1534.
- `.aib_memory/requests/R-20260417-1534-add-quit-option-to-menu/implementation.md` — Implementation log for R-20260417-1534.
- `.aib_memory/requests/R-20260417-1534-add-quit-option-to-menu/test_quit_option.py` — Request-scoped unit tests: T1 (QUIT key returns None), T2 (DIGIT:0 returns None), T3 (render shows 0) Quit).
- `.aib_memory/requests/R-20260417-1554-aib-prompt-and-workflow-improvements/` — Request folder for R-20260417-1554: AIB prompt and workflow improvements.
- `.aib_memory/requests/R-20260417-1554-aib-prompt-and-workflow-improvements/request.md` — Request definition for aib-prompt-and-workflow-improvements.
- `.aib_memory/requests/R-20260417-1554-aib-prompt-and-workflow-improvements/analysis.md` — Analysis artifact for aib-prompt-and-workflow-improvements.
- `.aib_memory/requests/R-20260417-1554-aib-prompt-and-workflow-improvements/implementation.md` — Implementation log for aib-prompt-and-workflow-improvements.
- `.aib_memory/requests/R-20260417-1709-revise-aib-brain-readme-and-restrict-script-invocation/` — Request folder for R-20260417-1709: Revise aib_brain README and restrict script invocation.
- `.aib_memory/requests/R-20260417-1709-revise-aib-brain-readme-and-restrict-script-invocation/request.md` — AI-generated request scope, plan, and constraints for revising `.aib_brain/README.md` to prohibit direct tool script invocation.
- `.aib_memory/requests/R-20260417-1709-revise-aib-brain-readme-and-restrict-script-invocation/implementation.md` — Implementation log for R-20260417-1709.
- `.aib_memory/logs/` — Per-action execution log files; excluded from VCS.
- `logs/` — Per-version release log files committed to VCS.
- `versions/` — Versioned `.aib_brain/` zip archives committed to VCS; used for installation.
- `scripts/` — Standalone Python scripts for CI and administrative tasks.
- `scripts/release_bookkeeping.py` — CI release script; bumps patch version, rotates SemVer marker, writes version log, and creates versioned zip archive in `versions/`.
- `tests/` — Pytest test suite.
- `tests/conftest.py` — Shared pytest fixtures for test isolation.
- `tests/test_close_request.py` — Integration tests for `close-request.py`.
- `tests/test_create_request.py` — Integration tests for `create-request.py`; verifies no `request.md`/`implementation.md` seeding.
- `tests/test_initialize.py` — Integration tests for `initialize.py`; includes `input.md` creation assertion.
- `tests/test_lifecycle_e2e.py` — End-to-end lifecycle integration tests.
- `tests/test_menu.py` — Unit tests for `menu.py`.
- `tests/test_reverse_engineer.py` — Unit tests for `reverse-engineer.py`.
- `README.md` — Project overview and installation instructions referencing `versions/` folder.

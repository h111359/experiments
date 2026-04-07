# Product Context

> **Auto-generated** by `aib-context.md` on 2026-04-04 18:35 +0200.
> Framework definition assets (`.aib_brain/`) are excluded by design — see `.aib_brain/` for AIB framework internals.
> This document is a synthesis of product documentation and workspace sources. It is fully replaced on each execution.

## Product Identity

AI Builder (AIB) is a minimal, model-agnostic framework for specification-driven development in a repository workspace. It provides deterministic, file-first workflows for managing structured work items (requests and iterations), maintaining convention-governed product documentation, and automating release bookkeeping via CI. The active version is encoded as a single empty marker file (`vMAJOR.MINOR.PATCH`) in the `.aib_brain/` folder; the current release series is v1.0.x (per ARCH-01).

Primary actors: Repository Developer (creates and tracks requests using AIB tooling), AIB Maintainer (owns brain assets and enforces conventions), and AI Automation Agent (executes prompt-driven workflows within explicitly allowed scope).

Operational status: active. Scope boundary: AIB does not provision cloud infrastructure, manage external services, or enforce runtime security controls outside the workspace filesystem. It is not a runtime product; it is a development workflow framework (per KNW-03, per RQT-02).

## Business Context

AIB operates in the software engineering tooling domain, automating internal development workflow governance for teams using Git-based repositories. It supports the following business processes: workspace initialization (seeding memory registers and documentation stubs), request and iteration lifecycle management (create, progress, close), convention-governed product documentation authoring and updating, and CI-based release bookkeeping (SemVer patch bump and version log generation) (per KNW-02).

Organizational ownership: AIB Maintainers own `.aib_brain/` assets and enforce conventions; the Product Team owns workspace-specific `.aib_memory/` artifacts; Repository Maintainers own the AI_Builder repository.

Critical external dependencies: GitHub (repository hosting), GitHub Actions (CI runner for release bookkeeping). No external data providers or regulatory bodies are specified (per ARCH-01).

Key business events driving product activity: a developer starting new work (triggers request creation), a developer completing a work unit (triggers request/iteration close), a pull request targeting `main` (triggers CI release bookkeeping).

## Requirements Summary

### Functional Capabilities (per RQT-02)

- FR-001: The system manages exactly one Active request per workspace.
- FR-002: At request creation the system produces a request folder with `request.md`, `iterations.md`, and `implementation.md`.
- FR-003: The system manages exactly one Active iteration per request.
- FR-004: The system generates iteration artifacts in the request folder.
- FR-005: An implement workflow appends an entry to the request implementation log.
- FR-006: The system reads `references.md` to determine which files may be edited; automation must not modify files where `edit_allowed = N`.
- FR-007: The system reads per-document conventions and fails closed if a required mapping is missing.
- FR-008: An interactive command menu provides real-time output streaming to the terminal and per-action execution log files at `logs/aib-action-<timestamp>-<action-id>.log`.
- FR-009: A PR bookkeeping workflow bumps the patch version and writes a new version log without modifying existing logs.

### Non-Functional Requirements (per RQT-02)

- NFR-001: Workflows must be model-agnostic and vendor-agnostic.
- NFR-002: Deterministic rules must be used for resolving active request and iteration.
- NFR-003: The system must fail closed when a required convention mapping is missing.
- NFR-004: Tool scripts must be runnable with Python 3.10+.
- NFR-005: The release bookkeeping workflow must be idempotent on reruns.

### Acceptance Criteria (per RQT-02)

1. Initialization creates `.aib_memory` registers and product-doc stubs.
2. Creating a request registers one Active request and creates iteration 01 as Active.
3. Implementing a request appends an entry to the request implementation log.
4. Product-doc edits follow their conventions and respect edit permissions.
5. Release bookkeeping increments patch version and creates a new per-version log without modifying existing logs.

## Architecture & Key Decisions

### Component Map (per ARCH-01)

- **AIB Brain Assets** (`.aib_brain/`): Reusable prompts, conventions, templates, and tool scripts. Provides deterministic workflows and documentation conventions.
- **AIB Command Menu** (`.aib_brain/run.bat`, `.aib_brain/run.sh`, `.aib_brain/tools/menu.py`): Terminal UI launcher. Surfaces only non-excluded scripts (EXCLUDE_SCRIPTS); displays active request ID and title; streams subprocess stdout/stderr via Popen tee pattern; writes per-action log files to `logs/aib-action-<timestamp>-<action-id>.log`.
- **AIB Tool Scripts** (`.aib_brain/tools/*.py`): Python scripts implementing deterministic lifecycle actions (initialize, create-request, create-iteration, close-iteration, close-request, reverse-engineer).
- **AIB Memory Artifacts** (`.aib_memory/`): Requests, registers, and convention-governed product documentation. Persists workspace state.
- **Release Bookkeeping Script** (`scripts/release_bookkeeping.py`): Automates SemVer patch bump and per-version log generation. Invoked by CI.
- **GitHub Actions Workflow** (`.github/workflows/aib-semver-patch-bump-and-log.yml`): CI workflow triggering release bookkeeping on PR events targeting `main`.
- **Logs** (`logs/`): Release version logs and action execution logs for audit and traceability.

### Integration Points (per ARCH-01)

- Local workstation to Tool Scripts: Python process invocation, ad-hoc.
- Tool Scripts to `.aib_memory/` artifacts: file write (Markdown).
- GitHub Actions to Release Bookkeeping Script: process invocation (Python).
- Release Bookkeeping Script to `.aib_brain/` marker and `logs/`: file write.
- Developer and GitHub Actions to GitHub: git push/pull.

### Technology Stack

- Language: Python 3.10+, stdlib only (tool scripts, release bookkeeping, test suite).
- Documentation format: Markdown (all artifacts).
- Version control: Git and GitHub.
- CI/CD: GitHub Actions.
- No cloud infrastructure provisioned; all resources are repo/CI/filesystem-based (per ARCH-07).

### Architectural Decisions (per ARCH-04)

#### ADR-0001 — Single SemVer marker file for version

Decision: represent the active version as exactly one empty file in `.aib_brain/` named `vMAJOR.MINOR.PATCH`. Context: deterministic version detection without package managers. Alternatives considered: version JSON file (higher merge conflict risk); Git tags only (less discoverable in workspace-only contexts). Consequences: tool-agnostic and easy to validate; strict enforcement required to prevent multiple markers.

#### ADR-0002 — Fail-closed convention enforcement

Decision: if a mapping row or convention file cannot be resolved deterministically, do not edit the product-doc and record a blocker. Context: missing mappings can cause malformed documents or drift. Alternatives considered: best-effort edits with warnings (too risky). Consequences: prevents accidental corruption; can block until conventions are repaired.

### Architectural Principles (per ARCH-04)

- Determinism for state resolution and file generation.
- Safety via explicit edit scope (references register).
- Replaceable brain assets with workspace-specific memory.
- Vendor/model agnostic prompt design.
- Fail-closed on missing conventions.

## Technical Design

### Module Breakdown (per CMP-01)

- `initialize.py`: Seeds `.aib_memory/` folder structure, registers, and product-doc stubs from `.aib_brain/` templates. Idempotent; fails on invalid workspace state without partial writes.
- `create-request.py`: Validates no other Active request exists; creates request folder with `request.md`, `iterations.md`, `implementation.md`; updates requests register to Active.
- `create-iteration.py`: Appends a new iteration to the Active request's `iterations.md`; enforces exactly one Active iteration at a time.
- `close-iteration.py`: Marks the Active iteration as Completed. Fails if no Active iteration exists.
- `close-request.py`: Marks the Active request as Closed; auto-closes any Active iteration before closing the request and prints a notice per iteration.
- `menu.py`: Interactive command menu. Surfaces script actions only (no prompt action gating); displays active request ID and title; streams subprocess output via Popen tee pattern with `encoding="utf-8"`, `errors="replace"` for non-ASCII on Windows; catches streaming thread exceptions as `[THREAD-ERROR]`; writes per-action log files.
- `common.py`: Shared utilities for resolving active request and iteration (ALG-0002).
- `scripts/release_bookkeeping.py`: Implements ALG-0001 (SemVer Patch Bump). CLI arguments: `--base-ref`, `--brain-dir`, `--log-dir`, `--issue`, `--pr-number`, `--commit-subjects-file`, `--github-output`, `--dry-run`.

### Key Algorithms (per CMP-02)

#### ALG-0001 — SemVer Patch Bump

Locates the base marker from the git tree and the worktree marker from the filesystem. Computes target version as PATCH+1. Validates exactly one marker exists at each location. Rotates the marker file (delete old, create new). Writes a new per-version log file. Idempotent: if the log already exists and the marker is already bumped, exits with no changes. Requires git on PATH. Performance target: p95 under 2 minutes in CI (per CMP-02, `scripts/release_bookkeeping.py`).

#### ALG-0002 — Request Iteration Resolution

Reads `.aib_memory/requests_register.md` to find the row with `state = Active`. Reads the corresponding `iterations.md` to find the row with `state = Active`. Fails fast if zero or more than one Active record is found at either level. Filesystem-only; p95 under 1 second for a typical workspace (per CMP-02, `.aib_brain/tools/common.py`).

### Configuration and Parameterization (per ARCH-01, CMP-01)

- Active version: empty marker file `vMAJOR.MINOR.PATCH` in `.aib_brain/`.
- Edit permissions: `edit_allowed` column in `.aib_memory/references.md`.
- Excluded scripts: EXCLUDE_SCRIPTS set in `menu.py`.
- All tool scripts accept `--workspace` parameter defaulting to current directory.

### Design Patterns Applied

- File-as-record: each request and iteration is a row in a Markdown table; state transitions are deterministic rewrites of the table row.
- Convention-as-schema: each product-doc has a corresponding convention file governing required structure; missing convention causes fail-closed.
- Tee-streaming: subprocess output is simultaneously written to the terminal and a log file via threaded streaming.

## Data Architecture

### Data Sources (per DATA-01)

The workspace repository filesystem (SRC-0001) is the only data source. Owner: Repository Maintainers. Refresh frequency: ad-hoc. Classification: Internal. AIB tools read a bounded set of Markdown files from `.aib_brain/` and `.aib_memory/` and write derived artifacts back to `.aib_memory/`. Ingestion is on-demand batch read; error handling is fail-fast with no partial writes.

### Core Data Entities (per DATA-02)

- **REQUEST**: Tracked unit of work. Key: `request_id` (pattern R-YYYYMMDD-HHmi). State: Active or Closed. Constraint: exactly one Active per workspace.
- **ITERATION**: Numbered step within a request. Key: `request_id` + `iteration_id` (2-digit ascending). State: Active or Completed. Constraint: exactly one Active per request.
- **REFERENCE**: Register row describing a file and whether automation may edit it. Key: `ref_id` (REF-0001 pattern). `path` must be unique. `edit_allowed` enum: Y or N.
- **PRODUCT_DOC**: Convention-governed documentation file. Key: path. Edits only when `edit_allowed = Y`.
- **VERSION_LOG**: Release bookkeeping artifact. Key: version (vMAJOR.MINOR.PATCH). One log per bumped version; existing logs are never modified.

Relationships: REQUEST owns N ITERATIONs (REL_0001, identifying). REFERENCE rows point 1:1 to PRODUCT_DOC paths (REL_0002).

### Data Storage (per DATA-02)

Storage is the local filesystem backed by Git version control. Physical tables are Markdown tables in fixed files:

- `.aib_memory/requests_register.md` — requests register.
- `.aib_memory/references.md` — references register.
- `.aib_memory/requests/<request>/iterations.md` — iterations per request.

### Data Lineage

Developer or Agent invokes tool scripts -> tool scripts read `.aib_brain/` conventions and templates -> tool scripts write `.aib_memory/` artifacts. GitHub Actions invokes release bookkeeping -> bookkeeping reads git history and brain marker -> bookkeeping writes per-version log and rotates marker file (per ARCH-01, DATA-01).

DATA-03 (data lineage detail), DATA-04 (data storage strategy), DATA-06 (metrics catalog), and DATA-07 (data quality rules) are not yet populated.

### Data Access Patterns (per DATA-05)

Exposed datasets: AIB_Requests_Register (DS-0001) and AIB_References_Register (DS-0002). Consumers: Developer and AI Agent via direct filesystem reads (pull-based, on-demand). Connection: local filesystem with OS login and workspace ACLs; latency target p95 under 50 ms. No API layer; no database engine.

### Data Retention and Classification (per DATA-08)

All AIB artifacts are classified Internal. Retention is via git history until workspace decommission. Release version logs are committed and retained indefinitely. Action execution logs are excluded from version control and have no automatic cleanup. No PII is expected; if discovered, treat as an incident and remove with audit trail. Override OV-001 permits removal of accidental secrets with Repository Maintainer approval.

Dashboard inventory (DATA-09) is intentionally empty; no dashboards are tracked in this repository.

## Security & Compliance

### Edit Scope Control

Write access to product-docs is gated by the `edit_allowed` flag in `.aib_memory/references.md`. Automation must not modify any file where `edit_allowed = N` (per RQT-02 FR-006). Convention mapping must resolve deterministically before any edit is performed; missing mapping causes fail-closed behavior (per ADR-0002).

### Authentication and Authorization

Access to workspace files is controlled by OS-level permissions and repository ACLs. Repository contributors require repository access granted by Repository Maintainers. The GitHub Actions workflow uses `GITHUB_TOKEN` (provider-managed, read and write permissions) and is restricted to same-repository PRs; forks are skipped for security (per README.md).

### Data Protection

All AIB artifacts are classified Internal. No PII is expected or stored. No cloud infrastructure is provisioned by AIB; no encryption-at-rest configuration is managed by AIB. Secrets, credentials, keys, and tokens must not be stored in any AIB artifact. Accidental secret commits must be treated as an incident and removed (per DATA-08).

### Secrets Management

No secrets are managed by AIB. The GitHub Actions workflow uses only `GITHUB_TOKEN` (provider-managed). SEC-01 through SEC-04 (access management, infrastructure data protection, secrets management, and network security) are not yet populated with project-specific content.

### Compliance

No explicit regulatory requirements are identified. All artifacts are treated as Internal engineering documentation (per DATA-08).

## Operations

### Deployment

Deployment of `.aib_brain/` to workspaces: copy the `.aib_brain/` folder from the `main` branch into the target project workspace; run `.\.aib_brain\run.bat` (Windows) or `.aib_brain/run.sh` (Linux). Post-release verification: confirm exactly one SemVer marker in `.aib_brain/`, confirm tool scripts remain operational, and confirm `logs/` is preserved (per `docs/Development_and_Deployment_Specification.md`).

CI release bookkeeping runs automatically via the GitHub Actions workflow on PR events (`opened`, `reopened`, `synchronize`) targeting `main`. Pre-merge write model: commits marker rotation and new version log to the PR branch before merge. Infinite-loop prevention: runs triggered by `github-actions[bot]` are skipped. Repository setup requirements: Actions enabled, `GITHUB_TOKEN` with read and write permissions (per README.md).

### Observability and Logging (per OBS-01)

Two log categories:
1. Release version logs (`logs/version_vX.Y.Z_log.md`): generated by CI release bookkeeping; committed and retained indefinitely.
2. Action execution logs (`logs/aib-action-<YYYYMMDD>-<HHmmss>-<action-id>.log`): generated by the AIB Command Menu; excluded from version control via `.gitignore`; UTF-8 plain text; one file per action execution. Log markers in order: `[START]`, `[CMD]`, `[OUT]`, `[ERR]`, `[THREAD-ERROR]`, `[EXIT]`.

No remote transport, dashboards, or alerting thresholds are configured. Observability is limited to local log files and CI run outcomes.

### SLO and SLA (per ARCH-07)

All resources operate at best-effort SLA. No formal SLO targets are defined. Operational performance targets: initialize p95 under 5 minutes; request/iteration operations p95 under 2 minutes; release bookkeeping p95 under 10 minutes in CI.

### On-Call and Escalation

Owned by AIB Maintainers (brain assets, CI workflow) and Product Team (memory artifacts, product docs). No personal contact details are stored; no formal on-call rotation is documented.

### Rollback

CI release bookkeeping rollback: reset or rebase the PR branch to remove the stale version log, then rerun. Brain asset rollback: revert the PR and verify exactly one SemVer marker remains in `.aib_brain/` (per README.md, `docs/Development_and_Deployment_Specification.md`).

## Development Practices

### Repository Structure

- `.aib_brain/` — Reusable framework assets: prompts, conventions, templates, tool scripts. Excluded from workspace sources by design.
- `.aib_memory/` — Workspace-specific artifacts: requests, registers, product docs. Excluded from workspace sources by design.
- `scripts/` — Release bookkeeping automation (`release_bookkeeping.py`).
- `tests/` — Pytest test suite for all AIB tool scripts.
- `docs/` — Supporting documentation: Development and Deployment Specification, Copilot Issue Assignment Rules.
- `logs/` — Release version logs and transient action execution logs.
- `.github/workflows/` — GitHub Actions CI workflow.
- `.gitignore` — Excludes `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `aib_brain/tools/__pycache__/`, and transient action execution logs.

### Developer Setup (per README.md)

1. Copy `.aib_brain/` from the `main` branch into the target workspace.
2. Windows: run `.\.aib_brain\run.bat` in a terminal; Linux: run `.aib_brain/run.sh`.
3. Python 3.10+ must be available on PATH.
4. For testing: run `pytest tests/` from the workspace root with the virtual environment activated.

### Branching and PR Conventions (per `docs/Development_and_Deployment_Specification.md`)

- Branch naming: `issue/<number>` (e.g., `issue/123`). No `feature/`, `fix/`, or `breaking/` prefixes.
- PRs must include: summary of `.aib_brain/` changes, explicit SemVer bump justification, and migration notes when applicable.
- Squash merge is recommended.
- MAJOR version changes require a migration note in the PR.

### Testing Strategy (per CMP-01 CMP-ART-0008)

Automated test suite in `tests/` using pytest:
- `conftest.py` — shared fixtures: temporary workspace builder, path configuration, mock helpers.
- `test_initialize.py` — integration tests for workspace initialization.
- `test_create_request.py` — integration tests for request creation.
- `test_create_iteration.py` — integration tests for iteration creation.
- `test_close_iteration.py` — integration tests for iteration close.
- `test_close_request.py` — integration tests for request close (including auto-close of Active iterations).
- `test_lifecycle_e2e.py` — full lifecycle E2E: initialize to create-request to create-iteration to close-iteration to close-request.
- `test_menu.py` — unit tests for `menu.py`: MenuState (including request title), log path generation, streaming behavior, parameter collection, script action discovery.
- `test_reverse_engineer.py` — unit tests for reverse-engineer tool: file inventory and exclusion logic.

Tests use `tempfile.TemporaryDirectory` for isolation. All tests must pass before merge.

### CI/CD (per README.md, ARCH-07)

GitHub Actions workflow triggers on PR events targeting `main`. Required gates: SemVer marker validation must pass; version log creation must succeed; marker rotation must commit cleanly. Restricted to same-repository PRs.

## Constraints & Assumptions

### Technical Constraints

- Exactly one Active request per workspace at any time; enforced by tool scripts.
- Exactly one Active iteration per request at any time; enforced by tool scripts.
- Automation must not modify files where `edit_allowed = N` in `references.md`.
- Exactly one SemVer marker file must exist in `.aib_brain/` at all times; zero or multiple markers is an invalid state and causes CI failure.
- Tool scripts require Python 3.10+ with no third-party dependencies.
- Release bookkeeping requires `git` on PATH.
- All operations use workspace-relative paths.

### Organizational Constraints

- GitHub Actions workflow requires `GITHUB_TOKEN` with read and write permissions in repository settings.
- Forked PRs are excluded from CI release bookkeeping for security.
- Branches must follow `issue/<number>` naming convention.

### Assumptions

- Workspace root is the Git repository root (high confidence).
- Python 3.10+ is available on the developer workstation (high confidence).
- `.aib_brain/` assets are present before any tool script is run (high confidence).
- GitHub Actions is enabled in the repository (high confidence for CI workflows to function).
- No cloud infrastructure is required or provisioned by AIB (high confidence).
- The repository does not store personal data or secrets (high confidence; treat as incident if violated).

### Validity Horizon

Revisit SemVer policy assumptions on any planned MAJOR version bump. Revisit branching conventions if repository governance changes. Revisit Python version constraint if tooling requires upgrade beyond 3.10+.

## Glossary

**ADR**: Architecture Decision Record. A document recording an architectural decision, its context, alternatives, and consequences.

**AIB**: Short form of AI Builder.

**AIB Brain Assets**: The set of reusable framework files under `.aib_brain/`: prompts, conventions, templates, and tool scripts.

**AIB Command Menu**: Terminal UI launcher for AIB tool scripts, providing real-time streaming output, per-action log files, and copilot CLI gating.

**AIB Maintainer**: Persona responsible for owning `.aib_brain/` assets and enforcing conventions and deterministic behavior.

**AIB Memory Artifacts**: Workspace-specific files under `.aib_memory/`: requests, registers, and product documentation.

**Brain Folder**: The `.aib_brain/` folder containing reusable AIB framework assets.

**Convention File**: A file in `.aib_brain/conventions/` defining the required structure and validation rules for a specific product-doc type.

**Developer**: Persona representing a repository developer who creates and tracks requests using AIB tooling.

**EXCLUDE_SCRIPTS**: Configuration key in `menu_config.json` listing scripts excluded from the AIB Command Menu.

**FR**: Functional Requirement. A requirement specifying what the system must do.

**Implementation Log**: Request-scoped append-only record of changes, tests, and outcomes, stored as `implementation.md` in the request folder.

**Iteration**: Numbered step within a request. Exactly one Active iteration is permitted per request at any time.

**Memory Folder**: The `.aib_memory/` folder containing workspace-specific AIB artifacts.

**NFR**: Non-Functional Requirement. A requirement specifying quality attributes such as performance, reliability, or security.

**PR**: Pull Request. A GitHub mechanism for proposing, reviewing, and merging code changes to a target branch.

**Product Doc**: A convention-governed documentation file listed in the references register.

**Prompt Action**: A menu entry mapping to a `.aib_brain/prompts/aib-*.md` file. Executable when copilot CLI is available; informational display only when CLI is absent.

**References Register**: Markdown table in `.aib_memory/references.md` listing referenced files and whether automation may edit them.

**Request**: Tracked unit of work with a stable `request_id` (pattern R-YYYYMMDD-HHmi) and lifecycle state (Active or Closed). Exactly one Active request per workspace at a time.

**SemVer**: Semantic Versioning 2.0.0. Version format MAJOR.MINOR.PATCH where incompatible changes increment MAJOR, backward-compatible additions increment MINOR, and fixes increment PATCH.

**SemVer Marker File**: Single empty file in `.aib_brain/` whose filename encodes the active version as `vMAJOR.MINOR.PATCH`.

**Tool Script**: Python script in `.aib_brain/tools/` implementing a deterministic AIB lifecycle action.

## Workspace File Inventory

```
.github/workflows/aib-semver-patch-bump-and-log.yml
.gitignore
docs/Copilot_Issue_Assignment_Rules.md
docs/Development_and_Deployment_Specification.md
logs/aib-action-20260404-082220-close-request-py.log
logs/aib-action-20260404-082301-create-request-py.log
logs/aib-action-20260404-083551-aib_brain-prompts-aib-create-analysis-md.log
logs/aib-action-20260404-103334-close-iteration-py.log
logs/aib-action-20260404-103345-create-iteration-py.log
logs/aib-action-20260404-173025-close-request-py.log
logs/aib-action-20260404-182610-create-request-py.log
logs/version_v1.0.10_log.md
logs/version_v1.0.5_log.md
logs/version_v1.0.6_log.md
logs/version_v1.0.7_log.md
logs/version_v1.0.8_log.md
logs/version_v1.0.9_log.md
logs/versions_log.md
README.md
scripts/release_bookkeeping.py
tests/conftest.py
tests/test_close_iteration.py
tests/test_close_request.py
tests/test_create_iteration.py
tests/test_create_request.py
tests/test_initialize.py
tests/test_lifecycle_e2e.py
tests/test_menu.py
tests/test_reverse_engineer.py
```

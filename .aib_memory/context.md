# Product Context

> **Auto-generated** by `aib-refresh-context.md` on 2026-05-22 local time.
> Framework definition assets (`.aib_brain/`) are excluded by design — see `.aib_brain/` for AIB framework internals.
> This document is a synthesis of product documentation and workspace sources. It is fully replaced on each execution.

## Product Identity

AI Builder (AIB) is a repository-local framework for specification-driven development workflows and release bookkeeping.

- Primary actors are AIB users and AIB developers.

- AIB user — a developer who uses AIB to manage and implement feature requests in their own workspace.

- AIB developer — owns `.aib_brain/` assets, enforces conventions, manages CI workflows.

## Domain Knowledge

AIB operates in the software engineering and internal tooling domain. It supports the following key business processes.

- **Initialize AIB workspace**: Seeds `.aib_memory/` registers, `context.md`, and `input.md` from `.aib_brain/` assets and archives the previous `.aib_memory/` content.

- **Communicate user intent**: Developer writes into `.aib_memory/input.md`; the AI agent reads it, auto-creates a request, archives the input, and resets the file.

- **Execute analysis workflow**: AI agent generates `plan.md` (auto-request branch) and/or `analysis.md` with 5 mandatory sections (Overview, Files Read During This Analysis Run, Input Interpretation, Research Results, Decision Register); updates `plan.md` with Plan and Decisions sections. On every run — first pass or re-run — `aib-analyze.md` fully replaces (overwrites) `analysis-<request_id>.md`; appending to, prepending to, or partially editing the existing file is PROHIBITED.

- **Analysis workflow structure**: The analysis prompt follows a 9-step linear execution sequence: (1) Preflight + State Resolution, (2) Context Check, (3) Read Inputs, (4) Halt on Unanswered Questions, (5) Generate Analysis, (6) Archive Input and Reset, (7) Quality Check, (8) Q-block Generation, (9) Plan Generation. The prompt includes an `## Execution Model Summary` chapter, a `## Global Constraints` section (GC-01 through GC-07), and a `## Failure Handling` section.

- **Analysis Q-block rules**: Section 6.3 (Q-block Rules) is split into three sub-sections: 6.3.1 Decision Identification, 6.3.2 Decision Classification, and 6.3.3 Q-block Generation. Q-blocks support two formats: multiple-choice (with 3+ options and a recommended marker) and free-text (with `- Answer: ___` for unbounded information needs). Step 6 (Archive Input and Reset, section 5.6) is split into three sub-sections: 5.6.1 Eligibility Check, 5.6.2 Finalize Script Invocation, and 5.6.3 Post-conditions.

- **Analysis Decision Points requirement**: The analysis prompt requires a mandatory Decision Fork Enumeration step and a `### Decision Points` heading/sub-heading list within `## Decision Register` of the analysis document. When multiple valid implementation choices exist, AI-generated Q-blocks are written to `input.md ## Questions` for developer review.

- **Answer Application Sub-flow**: Section 7.2 (Answer Application Sub-flow) begins with an all-answered pre-check that halts execution when any Q-block is unanswered, leaving `input.md` unchanged. A Q-block is answered when at least one checkbox is marked `[x]` or the `- Answer:` line has non-empty text. `analysis-convention.md` section 3 is titled "File Naming, Location & Write Behavior (Normative)".

- **Execute implement workflow**: AI agent applies request scope, updates product docs, creates/appends `implementation.md`, and auto-closes the request upon successful completion.

- **Release bookkeeping**: CI-automated version bump (auto-applies PATCH when head marker equals the base; accepts any manually pre-applied MINOR or MAJOR bump), per-version log creation, and `.aib_brain/` zip archive in `versions/` on pull request events targeting `main`.

- **Video Tutorials**: `recordings/` at the repository root contains eight sequentially numbered WebM video files (01_installation through 08_context) providing step-by-step walkthroughs of the AIB workflow.

Organizational units: Product Team (request lifecycle), AIB Maintainers (framework assets), Repository Contributors (read/write access gated by repository permissions).

External dependencies for the product include the following.

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

## Concepts

AIB is built on a small set of guiding principles that distinguish it from generic task-management or project-tracking systems.

- **Convention-over-configuration**: All product and code quality rules are captured in convention files under `.aib_brain/conventions/`; no inline configuration is needed.

- **Determinism**: Given the same workspace state, every AIB prompt execution produces semantically equivalent output.

- **Ephemeral input channel**: `input.md` is intentionally reset after each analysis run so that the file never accumulates stale developer intent across requests.

- **Minimal footprint**: AIB adds only `.aib_brain/` and `.aib_memory/` to the workspace; it has no runtime dependencies beyond Python 3 and Git.

- **Request-scoped traceability**: Every unit of work has a stable identifier that links analysis, plan, implementation log, and closure artifacts together.

- **Specification-first development**: Every change is preceded by an analysis and a plan before any code is written.

## Constraints & Assumptions

AIB operates under several constraints and assumptions. These apply to all workspaces where AIB is deployed.

- AIB requires Python 3 and Git to be available in the environment for tool scripts to execute.

- The `.aib_brain/` folder must not be modified during active implementation work unless the request explicitly authorises it.

- `context.md` is fully replaced on each `aib-refresh-context.md` execution; no append semantics apply.

- All workspace artifacts are classified as Internal engineering documentation with no PII.

- It is assumed that the developer operates with read/write access to the repository and that CI has write access to push version bump commits.

## Requirements

AIB requirements are organized by functional area. The product has no externally published SLA.

- FR-001: AIB MUST provide a request register (`requests_register.md`) that tracks all requests with a stable ID and lifecycle state (Active or Closed).

- FR-002: AIB MUST auto-create a request from `input.md` content when no Active request exists and `input.md` is non-empty.

- FR-003: AIB MUST generate an analysis document (`analysis-<request_id>.md`) with five mandatory sections for every Active request.

- FR-004: AIB MUST update `plan-<request_id>.md` with a Plan and Decisions section after analysis generation.

- FR-005: AIB MUST write AI-generated Q-blocks to `input.md ## Questions` when genuine implementation decision forks exist.

- FR-006: AIB MUST support an Answer Application Sub-flow that applies developer-answered Q-blocks to `plan.md` and regenerates analysis without Q-blocks on re-run.

- FR-007: AIB MUST archive `input.md` before reset and reset it to the seed template at the end of each analysis run.

- FR-008: AIB MUST provide an implementation prompt (`aib-implement.md`) that auto-closes the request upon confirmed successful implementation.

- FR-009: AIB MUST automate SemVer PATCH version bump, per-version log creation, and `.aib_brain/` zip archival on CI pull request events targeting `main`.

- NFR-001: AIB prompt files MUST be model-agnostic and contain no vendor-specific instructions.

- NFR-002: AIB MUST NOT require network access at prompt execution time.

## Architecture & Decisions

AIB is structured as a two-folder framework: `.aib_brain/` (framework assets, versioned and distributed) and `.aib_memory/` (workspace-specific runtime artifacts, not distributed).

Key components include the following.

- `.aib_brain/prompts/` — Prompt action files that define AI agent execution logic for each AIB workflow step.

- `.aib_brain/conventions/` — Convention files that define required structure and quality rules for all product docs and code.

- `.aib_brain/tools/` — Python tool scripts implementing deterministic AIB actions (create-request, finalize-input, close-request, initialize, move-request-artifacts).

- `.aib_memory/` — Runtime workspace: request register, active plans, active analysis, `context.md`, `input.md`, and `instructions.md`.

- `.aib_memory/requests/` — Closed request archive folders, each containing plan, analysis, implementation, and input archives.

- `logs/` — Per-version release logs and the curated change log (`next_version_changes.md`).

- `versions/` — Versioned `.aib_brain/` zip archives created by CI on each release.

Architectural decisions include the following.

- ADR-001: Use a flat file Markdown register (`requests_register.md`) instead of a database to maximize portability and human readability.

- ADR-002: Distribute AIB as a versioned zip archive of `.aib_brain/` rather than a package manager dependency, keeping the framework self-contained and offline-capable.

- ADR-003: Co-locate Q-block generation rules with output specifications (section 6.3 of `aib-analyze.md`) to reduce navigation distance between generation instructions and classification rules.

- ADR-004: Use CI-automated SemVer PATCH bumps with manual override for MINOR and MAJOR to minimize developer ceremony around release numbering.

## Technical Design

AIB prompt files are plain Markdown documents executed by an AI coding agent. Tool scripts are Python 3 scripts that perform file system operations deterministically.

- `aib-analyze.md` implements a 9-step linear prompt structure: Objective; Execution Model Summary; Global Rules; Inputs/Outputs/Dependencies; Execution Procedure (steps 1–9); Output Specifications; Sub-flows; Completion Confirmation.

- `aib-implement.md` reads the active plan, applies code and documentation changes, runs tests, and invokes `move-request-artifacts.py` and `close-request.py` on success.

- `aib-refresh-context.md` rebuilds `context.md` from a deterministic workspace scan and synthesis, fully replacing the prior file.

- `create-request.py` creates a request folder under `.aib_memory/requests/` and appends a row to `requests_register.md`.

- `finalize-input.py` conditionally archives `input.md`, moves attachment files to the request inputs folder, and resets `input.md` to the seed template.

- `close-request.py` updates `requests_register.md` state to Closed, moves active artifacts (`plan-*.md`, `analysis-*.md`, `implementation.md`) into the request folder, and resets `input.md`.

- `release_bookkeeping.py` validates the SemVer marker, computes the next PATCH version, writes `logs/version_vX.Y.Z_log.md`, and creates `versions/aib_brain_vX.Y.Z.zip`; prefers `logs/next_version_changes.md` as the `Changes:` source over git commit subjects.

- `write_analysis.py` at the workspace root is a standalone utility for writing the analysis artifact.

## Data Architecture

AIB uses the workspace file system as its only data store; no database or external data service is involved.

- Request data is stored as individual request folders under `.aib_memory/requests/`, each containing `plan-<request_id>.md`, `analysis-<request_id>.md`, `implementation.md`, and an `inputs/` archive subfolder.

- The request register (`requests_register.md`) is a Markdown table with columns: `request_id`, `title`, `folder`, `state`, `created_at`, and `closed_at`.

- Active workspace artifacts (`plan-<request_id>.md`, `analysis-<request_id>.md`) live at `.aib_memory/` root during the active phase and are moved to the request folder on close.

- `input.md` is ephemeral: read and reset on each analysis run; archived content is retained in the request `inputs/` subfolder.

- `context.md` is fully replaced on each `aib-refresh-context.md` execution; no append semantics apply.

## Security & Compliance

AIB is an internal engineering tooling framework with no external user-facing surface and no data leaving the repository.

- Authentication is governed entirely by repository access controls (GitHub permissions); AIB itself has no authentication layer.

- No secrets, credentials, or PII are stored in any AIB artifact; convention files explicitly prohibit including them.

- All artifacts are Internal classification; no GDPR, HIPAA, or SOC2 obligations apply to AIB itself.

- CI workflows run in GitHub Actions with repository-scoped tokens; no elevated cloud permissions are required.

## Operations

AIB has no production service to operate; its operational surface is limited to the CI pipeline and developer local usage.

- The CI pipeline (`aib-semver-patch-bump-and-log.yml`) runs automatically on pull requests targeting `main` and performs version bump, log creation, and zip archival.

- Failure of the CI pipeline requires manual inspection of the workflow logs in GitHub Actions; the developer re-runs the failed job after fixing the root cause.

- No monitoring, alerting, or SLO targets apply to AIB; it is a developer tooling framework used on-demand.

## Development Practices

AIB development follows a specification-first workflow enforced by its own framework.

- All changes are initiated by writing developer intent into `.aib_memory/input.md`, triggering the AIB request lifecycle.

- Branching strategy: feature branches are created per request; pull requests target `main` and trigger the CI release pipeline on merge.

- Testing strategy: `pytest` is used; tests are located in `tests/` and cover tool scripts, prompt structure literals, convention compliance, and end-to-end lifecycle scenarios. Tests are run with `python -m pytest`.

- CI gates: the `aib-semver-patch-bump-and-log.yml` workflow validates the SemVer marker, bumps PATCH, writes the version log, and creates the versioned archive; the pipeline must pass before merge.

- Convention compliance is enforced through literal-presence tests in `tests/test_analysis_prompt_structure.py` and related test files that assert protected strings remain present across restructuring efforts.

## Workspace File Inventory

The workspace contains the following non-excluded files and directories, sorted by path.

- `.gitignore` — Git ignore rules for the repository.

- `README.md` — Top-level repository readme covering installation, video tutorials, and a reference to the user guide.

- `docs/` — Documentation and prompt files for workspace-level developer guidance.

- `docs/Analyze_AIB.prompt.md` — Prompt file for running AI-assisted analysis of the AIB codebase itself.

- `docs/aib-refresh-context-AIB_version.md` — Supplementary context refresh document for the AIB product version.

- `docs/Copilot_Issue_Assignment_Rules.md` — Rules governing how GitHub Copilot assigns issues in this repository.

- `docs/Development_and_Deployment_Specification.md` — Specification document covering development and deployment procedures.

- `logs/` — Contains per-version release log files and the curated change log; individual version logs follow the pattern `version_vX.Y.Z_log.md`.

- `logs/next_version_changes.md` — Curated append-only bullet list of changes for the next release; read by `release_bookkeeping.py` as the preferred `Changes:` source.

- `logs/` — Contains 38 per-version release log files following the pattern `version_vX.Y.Z_log.md`; individual items are not listed.

- `recordings/` — Contains 8 sequential WebM tutorial video files (01_installation through 08_context) providing step-by-step AIB workflow walkthroughs.

- `scripts/` — Python utility scripts for CI and release automation.

- `scripts/release_bookkeeping.py` — CI release bookkeeping script that bumps the SemVer marker, writes the version log, and creates the versioned archive.

- `tests/` — pytest test suite covering tool scripts, prompt structure, convention compliance, and lifecycle scenarios.

- `tests/conftest.py` — pytest configuration and shared fixtures for the test suite.

- `tests/test_analysis_prompt_structure.py` — Tests asserting structural and literal requirements of `aib-analyze.md` and related convention files.

- `tests/test_artifact_placement.py` — Tests verifying correct artifact placement during request lifecycle transitions.

- `tests/test_close_request.py` — Tests for the `close-request.py` tool script behavior.

- `tests/test_context_formatting_rules.py` — Tests asserting formatting rule compliance for `context.md`.

- `tests/test_create_request.py` — Tests for the `create-request.py` tool script behavior.

- `tests/test_finalize_input.py` — Tests for the `finalize-input.py` tool script behavior.

- `tests/test_initialize.py` — Tests for the `initialize.py` tool script behavior.

- `tests/test_instructions_md.py` — Tests asserting the structure and behavior of `instructions.md` handling.

- `tests/test_lifecycle_e2e.py` — End-to-end lifecycle tests covering the full AIB request workflow.

- `tests/test_menu.py` — Tests for the AIB menu or navigation behavior.

- `tests/test_questions_in_input_md.py` — Tests asserting Q-block handling in `input.md`.

- `tests/test_release_bookkeeping.py` — Tests for the `release_bookkeeping.py` CI script.

- `tests/test_requirements_analysis_convention.py` — Tests asserting compliance with the requirements analysis convention.

- `tests/test_reverse_engineer.py` — Tests for the reverse-engineering (brownfield context generation) behavior.

- `tests/test_semver_workflow_structure.py` — Tests asserting the SemVer workflow structure and marker file conventions.

- `tests/test_tools_common.py` — Tests for shared tool script utilities and common behaviors.

- `tests/test_user_guide_product_accuracy.py` — Tests asserting that the user guide accurately reflects the current AIB product state.

- `versions/` — Contains 26 versioned `.aib_brain/` zip archives following the pattern `aib_brain_vX.Y.Z.zip`; individual items are not listed.

- `write_analysis.py` — Standalone utility script for writing the analysis artifact.
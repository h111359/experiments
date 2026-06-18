# Product Context

## 1. Product Identity

AI Builder (AIB) is a minimal, model-agnostic framework for specification-driven development workflows and release bookkeeping. Operates as a repository-local toolset requiring only Python 3.

Primary actors: AIB users (developers who use AIB to manage and implement feature requests) and AIB developers (who own .aib_brain/ assets, enforce conventions, and manage CI workflows).

AIB is NOT a runtime service, IDE plugin, or cloud-hosted application. It is a local workspace framework, active and in use.

## Project overview

- N: AIB operates in software engineering and internal tooling domain.
- N: Supports specification-driven development: every change preceded by analysis and plan before code.
- I: Org units: Product Team (request lifecycle), AIB Maintainers (framework assets), Repository Contributors.
- I: External deps: GitHub (hosting) and GitHub Actions (CI runner for release bookkeeping).
- C: No regulatory bodies or external data providers identified.
- I: All artifacts classified as Internal engineering documentation with no PII.

## Change Management

- I: AIB uses CI-automated SemVer PATCH bumps with manual override for MINOR and MAJOR.
- I: Per-version log files created under logs/ by CI on pull request events targeting main.
- I: Curated change log logs/next_version_changes.md maintained by AI agent during implementation and consumed by CI.
- U: Curated change log reset to empty by CI after incorporation into version log.

## Domain

- N: AIB operates in software engineering domain supporting internal tooling development workflows.
- N: Key business process is request lifecycle from user intent through analysis, planning, implementation, and closure.
- N: Video tutorials in recordings/ provide step-by-step walkthroughs of AIB workflow (8 sequential WebM files).

## Concepts

- N: Convention-over-configuration means all product and code quality rules captured in convention files under .aib_brain/conventions/.
- N: Determinism means same workspace state produces semantically equivalent output for every AIB prompt execution.
- N: Ephemeral input channel means input.md intentionally reset after each analysis run so file never accumulates stale developer intent.
- N: Minimal footprint means AIB adds only .aib_brain/ and .aib_memory/ to workspace with no runtime deps beyond Python 3.
- N: Request-scoped traceability means every unit of work has stable identifier linking analysis, plan, implementation log, and closure artifacts.
- N: Specification-first development means every change preceded by analysis and plan before any code is written.

## Best Practices

- U: .aib_brain/ folder must not be modified during active implementation unless request explicitly authorises it.
- U: context.md is fully replaced on each aib-refresh-context.md execution with no append semantics.

## Functionality

- R: AIB MUST store active-request state in input.md YAML frontmatter (fields: request_id, title, state, options.minimum_questions); input.md is the single source of truth for active-request state.
- R: AIB MUST auto-create request from input.md content when no Active request exists and input.md is non-empty.
- R: AIB MUST write AI-generated Q-blocks to input.md Questions section when genuine implementation decision points exist.
- R: AIB MUST support Answer Application Sub-flow that applies developer-answered Q-blocks to the plan.
- R: AIB MUST archive input.md before reset and reset it to seed template at end of each analysis run.
- R: AIB MUST provide implementation prompt (aib-implement.md) that auto-closes request upon confirmed successful implementation.
- R: AIB MUST automate SemVer PATCH bump, per-version log creation, and .aib_brain/ zip archival on CI pull request events targeting main.
- R: AIB prompt files MUST be model-agnostic with no vendor-specific instructions.
- R: AIB MUST NOT require network access at prompt execution time.
- R: AIB MUST generate a self-sufficient plan-REQUEST_ID.md with exact file paths in all procedure steps and exact edit-context.py commands in context update tasks; implement MUST NOT read context.md.
- R: AIB MUST write all Q-blocks to input.md in unanswered state; AI MUST NOT pre-check options or populate Answer fields.
- R: AIB MUST generate analysis document named analysis-REQUEST_ID.md with six mandatory sections for every Active request.

## Technical Design

- D: AIB tracks active-request state via YAML frontmatter header in input.md managed by input-header.py; request history is implicitly available from .aib_memory/requests/ folder structure.
- D: AIB distributed as versioned zip archive of .aib_brain/ rather than package manager dependency.
- D: Q-block format templates defined in .aib_brain/conventions/q-block-convention.md as authoritative source.
- D: CI-automated SemVer PATCH bumps with manual override for MINOR and MAJOR minimize developer ceremony.
- D: context.md uses atomic statement format with type-letter-indexed entries; tools use text-based line matching for CRUD ops.
- I: edit-context.py provides CRUD operations (select, insert, delete) for individual atomic statements using text-based matching.
- I: verify-context.py validates context.md format compliance against context-convention.md with 10 automated checks.
- D: Context format verification is prompt-orchestrated with no tool coupling between edit-context.py and verify-context.py.

## Technology Stack

- I: AIB requires Python 3 as only runtime dep for core workflow.
- I: CI runs on GitHub Actions for automated release bookkeeping.
- I: Tool scripts implemented in Python using only standard library.

## Networking and Connectivity

- C: AIB does not require network access at prompt execution time.

## Data structures

- N: input.md YAML frontmatter header fields: request_id (~ when idle), title (~ when idle), state (idle|analysis_ready|questions_generated), options.minimum_questions (integer, default 0).
- N: Atomic statements in context.md follow format: - TYPE: text with 22 valid area names and 9 type letters.
- N: Each request has stable identifier following pattern R-YYYYMMDD-HHmi.

## Data flow

- I: Developer writes intent into input.md, AI agent reads it, auto-creates request, archives input, resets file.
- I: Implementation applies plan, auto-closes request, and generates implementation.md.
- I: Analysis generates analysis-REQUEST_ID.md and a self-sufficient plan-REQUEST_ID.md containing all information needed for implementation without consulting context.md.

## Processes

- I: Analysis workflow follows 11-step linear execution sequence including dedicated context review step S06.
- I: Release bookkeeping is CI-automated on pull request events targeting main.
- I: Implement workflow reads plan only (context.md is not read during implementation), executes tasks in order, runs tests, and closes request.

## User Interface

- I: User guide is self-contained HTML file at .aib_brain/user_guide.html requiring no network connectivity.
- I: Primary user interaction through .aib_memory/input.md as ephemeral communication channel.

## Security

- C: All workspace artifacts classified as Internal engineering documentation with no PII.
- C: No secrets, credentials, or tokens stored in any AIB artifact.

## Operations

- I: SemVer marker file in .aib_brain/ encodes active product version as empty file named vMAJOR.MINOR.PATCH.
- I: Versioned archives stored in versions/ as zip files created by CI per version bump.

## Development

- I: Tests located in tests/ and executed with python -m pytest tests/.
- I: Repo uses branching strategy with PRs targeting main for release.
- I: CI workflow defined in .github/ and triggers on pull request events.

## Deployment

- I: AIB deployed by unzipping versioned .aib_brain/ archive into workspace root.
- I: Initial setup requires running launcher script (.aib_brain/run.bat on Windows, .aib_brain/run.sh on Linux/macOS).

## Durability

- I: Closed request artifacts preserved in .aib_memory/requests/REQUEST-FOLDER/ for audit traceability.
- I: Input archives preserve original input.md content at REQUEST-FOLDER/inputs/input-archive-TIMESTAMP.md.

## Observability

- I: Per-version release logs under logs/ document changes for each version bump.
- I: implementation.md in each request folder records changes, tests, and outcomes.

## Documentation

- I: recordings/ contains 8 sequential WebM video tutorials covering full AIB workflow.
- I: Convention files under .aib_brain/conventions/ define required structure and validation rules for all product docs and code.
- I: context convention defines atomic statement format with 22 valid area names and 9 statement types.

## Files

.aib_brain/
  conventions/ — normative rules for context.md, code, and all AIB artifacts
  prompts/ — aib-analyze.md, aib-implement.md, aib-refresh-context.md
  tools/ — Python scripts: close-request.py, create-request.py, edit-context.py, file-inventory.py, finalize-input.py, initialize.py, input-header.py, menu.py, move-request-artifacts.py, verify-context.py
  user_guide.html — self-contained HTML user guide
  README.md — framework internals documentation
.aib_memory/
  context.md — product context (this file)
  input.md — developer intent channel and active-request state store (YAML frontmatter header)
  instructions.md — persistent workspace directives
  requests/ — 41+ closed request folders following pattern R-YYYYMMDD-HHmi-SLUG/
docs/ — project documentation files
logs/
  next_version_changes.md — curated change bullets for next CI release
  version logs — 37+ per-version logs following pattern version_vX.Y.Z_log.md
recordings/ — 8 sequential WebM tutorial files (01_installation through 08_context)
scripts/
  release_bookkeeping.py — CI release bookkeeping: SemVer bump and log generation
tests/ — automated pytest suite for AIB conventions and tools (22 test files)
versions/ — 29+ versioned .aib_brain/ zip archives following pattern aib_brain_vX.Y.Z.zip
README.md — project overview with installation instructions and video tutorial links

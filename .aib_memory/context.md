# Product Context

## 1. Product Identity

AI Builder (AIB) is a minimal, model-agnostic framework for specification-driven development workflows and release bookkeeping. Operates as a repository-local toolset requiring only Python 3 and Git.

Primary actors: AIB users (developers who use AIB to manage and implement feature requests) and AIB developers (who own .aib_brain/ assets, enforce conventions, and manage CI workflows).

AIB is NOT a runtime service, IDE plugin, or cloud-hosted application. It is a local workspace framework, active and in use.

## PO

- N: AIB operates in software engineering and internal tooling domain.
- N: Supports specification-driven development: every change preceded by analysis and plan before code.
- I: Org units: Product Team (request lifecycle), AIB Maintainers (framework assets), Repository Contributors.
- I: External deps: GitHub (hosting) and GitHub Actions (CI runner for release bookkeeping).
- C: No regulatory bodies or external data providers identified.
- I: All artifacts classified as Internal engineering documentation with no PII.

## CM

- I: AIB uses CI-automated SemVer PATCH bumps with manual override for MINOR and MAJOR.
- I: Per-version log files created under logs/ by CI on pull request events targeting main.
- I: Curated change log logs/next_version_changes.md maintained by AI agent during implementation and consumed by CI.
- U: Curated change log reset to empty by CI after incorporation into version log.

## DO

- N: AIB operates in software engineering domain supporting internal tooling development workflows.
- N: Key business process is request lifecycle from user intent through analysis, planning, implementation, and closure.
- N: Video tutorials in recordings/ provide step-by-step walkthroughs of AIB workflow (8 sequential WebM files).

## CO

- N: Convention-over-configuration means all product and code quality rules captured in convention files under .aib_brain/conventions/.
- N: Determinism means same workspace state produces semantically equivalent output for every AIB prompt execution.
- N: Ephemeral input channel means input.md intentionally reset after each analysis run so file never accumulates stale developer intent.
- N: Minimal footprint means AIB adds only .aib_brain/ and .aib_memory/ to workspace with no runtime deps beyond Python 3 and Git.
- N: Request-scoped traceability means every unit of work has stable identifier linking analysis, plan, implementation log, and closure artifacts.
- N: Specification-first development means every change preceded by analysis and plan before any code is written.

## BP

- U: .aib_brain/ folder must not be modified during active implementation unless request explicitly authorises it.
- U: context.md is fully replaced on each aib-refresh-context.md execution with no append semantics.

## FN

- R: AIB MUST provide request register (requests_register.md) tracking all requests with stable ID and lifecycle state (Active or Closed).
- R: AIB MUST auto-create request from input.md content when no Active request exists and input.md is non-empty.
- R: AIB MUST generate analysis document named analysis-REQUEST_ID.md with five mandatory sections for every Active request.
- R: AIB MUST write AI-generated Q-blocks to input.md Questions section when genuine implementation decision points exist.
- R: AIB MUST support Answer Application Sub-flow that applies developer-answered Q-blocks to the plan.
- R: AIB MUST archive input.md before reset and reset it to seed template at end of each analysis run.
- R: AIB MUST provide implementation prompt (aib-implement.md) that auto-closes request upon confirmed successful implementation.
- R: AIB MUST automate SemVer PATCH bump, per-version log creation, and .aib_brain/ zip archival on CI pull request events targeting main.
- R: AIB prompt files MUST be model-agnostic with no vendor-specific instructions.
- R: AIB MUST NOT require network access at prompt execution time.
- R: AIB MUST generate a self-sufficient plan-REQUEST_ID.md with exact file paths in all procedure steps and exact edit-context.py commands in context update tasks; implement MUST NOT read context.md.

## TD

- D: AIB uses flat file Markdown register (requests_register.md) instead of db for max portability and human readability.
- D: AIB distributed as versioned zip archive of .aib_brain/ rather than package manager dependency.
- D: Q-block format templates defined in .aib_brain/conventions/q-block-convention.md as authoritative source.
- D: CI-automated SemVer PATCH bumps with manual override for MINOR and MAJOR minimize developer ceremony.
- D: context.md uses atomic statement format with type-letter-indexed entries; tools use text-based line matching for CRUD ops.
- I: edit-context.py provides CRUD operations (select, insert, delete) for individual atomic statements using text-based matching.
- I: verify-context.py validates context.md format compliance against context-convention.md with 10 automated checks.
- D: Context format verification is prompt-orchestrated with no tool coupling between edit-context.py and verify-context.py.

## TS

- I: AIB requires Python 3 and Git as only runtime deps.
- I: CI runs on GitHub Actions for automated release bookkeeping.
- I: Tool scripts implemented in Python using only standard library.

## NW

- C: AIB does not require network access at prompt execution time.

## DS

- N: Request register is Markdown table with columns: request_id, title, folder, state, created_at, closed_at.
- N: Atomic statements in context.md follow format: - TYPE: text with 22 valid area codes and 9 type letters.
- N: Each request has stable identifier following pattern R-YYYYMMDD-HHmi.

## DF

- I: Developer writes intent into input.md, AI agent reads it, auto-creates request, archives input, resets file.
- I: Implementation applies plan, auto-closes request, and generates implementation.md.
- I: Analysis generates analysis-REQUEST_ID.md and a self-sufficient plan-REQUEST_ID.md containing all information needed for implementation without consulting context.md.

## PR

- I: Analysis workflow follows 11-step linear execution sequence including dedicated context review step S06.
- I: Release bookkeeping is CI-automated on pull request events targeting main.
- I: Implement workflow reads plan only (context.md is not read during implementation), executes tasks in order, runs tests, and closes request.

## UI

- I: User guide is self-contained HTML file at .aib_brain/user_guide.html requiring no network connectivity.
- I: Primary user interaction through .aib_memory/input.md as ephemeral communication channel.

## SC

- C: All workspace artifacts classified as Internal engineering documentation with no PII.
- C: No secrets, credentials, or tokens stored in any AIB artifact.

## OP

- I: SemVer marker file in .aib_brain/ encodes active product version as empty file named vMAJOR.MINOR.PATCH.
- I: Versioned archives stored in versions/ as zip files created by CI per version bump.

## DV

- I: Tests located in tests/ and executed with python -m pytest tests/.
- I: Repo uses branching strategy with PRs targeting main for release.
- I: CI workflow defined in .github/ and triggers on pull request events.

## DP

- I: AIB deployed by unzipping versioned .aib_brain/ archive into workspace root.
- I: Initial setup requires running launcher script (.aib_brain/run.bat on Windows, .aib_brain/run.sh on Linux/macOS).

## DR

- I: Closed request artifacts preserved in .aib_memory/requests/REQUEST-FOLDER/ for audit traceability.
- I: Input archives preserve original input.md content at REQUEST-FOLDER/inputs/input-archive-TIMESTAMP.md.

## OB

- I: Per-version release logs under logs/ document changes for each version bump.
- I: implementation.md in each request folder records changes, tests, and outcomes.

## DM

- I: recordings/ contains 8 sequential WebM video tutorials covering full AIB workflow.
- I: Convention files under .aib_brain/conventions/ define required structure and validation rules for all product docs and code.
- I: context convention defines atomic statement format with 22 valid area codes and 9 statement types.

## Files

.aib_brain/
  conventions/ — normative rules for context.md, code, and all AIB artifacts
  prompts/ — aib-analyze.md, aib-implement.md, aib-refresh-context.md
  tools/ — Python scripts: close-request.py, create-request.py, edit-context.py, file-inventory.py, finalize-input.py, initialize.py, menu.py, move-request-artifacts.py, verify-context.py
  user_guide.html — self-contained HTML user guide
  README.md — framework internals documentation
.aib_memory/
  context.md — product context (this file)
  input.md — ephemeral developer intent channel
  instructions.md — persistent workspace directives
  requests_register.md — all requests with lifecycle state
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

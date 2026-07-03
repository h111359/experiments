# Product Context

## Product

- AIB is a minimal, model-agnostic framework for specification-driven development workflows and release bookkeeping.
- AIB operates as a repository-local toolset requiring only Python 3 with no runtime dependencies.
- Primary actors are AIB users (developers who manage and implement feature requests) and AIB developers (who own .aib_brain/ assets, enforce conventions, and manage CI workflows).
- AIB is not a runtime service, IDE plugin, or cloud-hosted application; it is a local workspace framework, active and in use.
- AIB operates in software engineering and internal tooling domain.
- Supports specification-driven development: every change preceded by analysis and plan before code.
- External deps: GitHub (hosting) and GitHub Actions (CI runner for release bookkeeping).
- Org units: Product Team (request lifecycle), AIB Maintainers (framework assets), Repository Contributors.
- No regulatory bodies or external data providers identified.
- All artifacts classified as Internal engineering documentation with no PII.

## Concepts

- Key business process is request lifecycle from user intent through analysis, planning, implementation, and closure.
- Convention-over-configuration means all product and code quality rules captured in convention files under .aib_brain/conventions/.
- Determinism means same workspace state produces semantically equivalent output for every AIB prompt execution.
- Ephemeral input channel means input.md intentionally reset after each analysis run so file never accumulates stale developer intent.
- Minimal footprint means AIB adds only .aib_brain/ and .aib_memory/ to workspace with no runtime deps beyond Python 3.
- Request-scoped traceability means every unit of work has stable identifier linking analysis, plan, implementation log, and closure artifacts.
- Specification-first development means every change preceded by analysis and plan before any code is written.
- Context extensions are workspace files registered in context.md ## References with Location, Summary, and optional Update: false (read-only) or Update: true (writable); all AIB prompts use AI semantic relevance judgement on extension Summaries to decide whether to read the full extension file.
- ## Issues section in context.md captures identified contradictions and quality concerns as plain bullets; entries must be removed when resolved or no longer applicable.
- aib-input-from-context.md is a prompt that reads all [PLANNED] entries and Issues from context.md and appends structured goal bullets to input.md ## Input; fails with error when an active request already exists.
- [PLANNED] tagged entries in context.md represent features intended for future implementation; permitted inline in Product, Concepts, Solution, and Requirements sections with syntax dash-space-[PLANNED]-space-statement or dash-space-[PLANNED]-MUST:-space-text for Requirements; the tag is removed when the feature is implemented via a plan-driven edit-context.py delete + insert pair.
- memory_version_compatibility is a durable upgrade-progress token in aib-setup.yaml with three values: compatible (normal operation), not-compatible (version mismatch detected), initialized-not-populated (upgrade complete but migration prompt not yet confirmed); written as initialized-not-populated by initialize.py --upgrade and reset to compatible by menu.py on user confirmation.

## Requirements

- MUST: AIB auto-creates request from input.md content when no Active request exists and input.md is non-empty.
- MUST: AIB writes AI-generated Q-blocks to input.md Questions section when genuine implementation decision points exist.
- MUST: AIB supports Answer Application Sub-flow that applies developer-answered Q-blocks to the plan.
- MUST: AIB archives input.md before reset and resets it to seed template at end of each analysis run.
- MUST: AIB provides implementation prompt (aib-implement.md) that auto-closes request upon confirmed successful implementation.
- MUST: AIB automates SemVer PATCH bump, per-version log creation, and .aib_brain/ zip archival on CI pull request events targeting main.
- MUST: AIB prompt files are model-agnostic with no vendor-specific instructions.
- MUST NOT: AIB requires network access at prompt execution time.
- MUST: AIB generates plan-REQUEST_ID.md with exact file paths in all procedure steps and exact edit-context.py commands in context update tasks.
- MUST: AIB writes all Q-blocks to input.md in unanswered state; AI must not pre-check options or populate Answer fields.
- MUST: AIB generates analysis document named analysis-REQUEST_ID.md with six mandatory sections for every Active request.
- MUST NOT: .aib_brain/ folder is modified during active implementation unless request explicitly authorises it.
- MUST NOT: Secrets, credentials, or tokens are stored in any AIB artifact.
- MUST: Requirements section statements use [MUST|MUST NOT|OPTIONAL] modality prefix.
- MUST: verify-context.py MUST be updated whenever context-convention.md quality gates are changed.
- MUST: verify-input.py MUST be updated whenever input-convention.md validation rules are changed.
- MUST: AIB stores active-request state in input.md YAML frontmatter grouped into state: (tool-managed: request_id, title, status, verification results) and options: (user-configurable: minimum_questions, verification enabled flags); input.md is the single source of truth for active-request state.
- MUST: AIB provides log-entry.py tool that appends UTC-timestamped entries to .aib_memory/log_{request_id}.md (normal mode) or .aib_memory/log_general.md (--general mode) and emits them to stdout.
- MUST: log-entry.py exits with code 1 in normal mode when no active request is found in input.md YAML header; --general mode bypasses this check.
- MUST: [PLANNED] tag must be removed from context.md when the associated feature is implemented; removal must be plan-driven via explicit edit-context.py delete + insert pair in the plan context update task.
- MUST: Extension entries registered in context.md ## References with Update: true must be updated both during aib-refresh-context.md execution and after each aib-implement.md completion run.

## Solution

- AIB tracks active-request state via YAML frontmatter header in input.md managed by input-header.py; request history is implicitly available from .aib_memory/requests/ folder structure.
- AIB distributed as versioned zip archive of .aib_brain/ rather than package manager dependency.
- Q-block format templates defined in .aib_brain/conventions/q-block-convention.md as authoritative source.
- CI-automated SemVer PATCH bumps with manual override for MINOR and MAJOR minimize developer ceremony.
- edit-context.py provides CRUD operations (select, insert, delete) for individual statements using text-based matching.
- Context format verification is prompt-orchestrated with no tool coupling between edit-context.py and verify-context.py.
- AIB requires Python 3 as only runtime dep for core workflow.
- CI runs on GitHub Actions for automated release bookkeeping.
- Tool scripts implemented in Python using only standard library.
- AIB does not require network access at prompt execution time.
- Each request has stable identifier following pattern R-YYYYMMDD-HHmi.
- Developer writes intent into input.md, AI agent reads it, auto-creates request, archives input, resets file.
- Analysis generates analysis-REQUEST_ID.md and a plan-REQUEST_ID.md containing information needed for implementation.
- Analysis workflow follows 11-step linear execution sequence including dedicated context review step S06.
- Release bookkeeping is CI-automated on pull request events targeting main.
- Implement workflow reads plan, executes tasks in order, runs tests, and closes request.
- User guide is self-contained HTML file at .aib_brain/user_guide.html requiring no network connectivity.
- Primary user interaction through .aib_memory/input.md as ephemeral communication channel.
- SemVer marker file in .aib_brain/ encodes active product version as empty file named vMAJOR.MINOR.PATCH; memory-side version is tracked in .aib_memory/aib-setup.yaml under the memory_version key.
- Versioned archives stored in versions/ as zip files created by CI per version bump.
- Tests located in tests/ and executed with python -m pytest tests/.
- Repo uses branching strategy with PRs targeting main for release.
- CI workflow defined in .github/ and triggers on pull request events.
- AIB deployed by unzipping versioned .aib_brain/ archive into workspace root.
- Initial setup requires running launcher script (.aib_brain/run.bat on Windows, .aib_brain/run.sh on Linux/macOS).
- Closed request artifacts preserved in .aib_memory/requests/REQUEST-FOLDER/ for audit traceability.
- Per-version release logs under logs/ document changes for each version bump.
- recordings/ contains 8 sequential WebM video tutorials covering full AIB workflow.
- Convention files under .aib_brain/conventions/ define required structure and validation rules for all product docs and code.
- context.md uses a 6-section structure (Product, Concepts, Requirements, Solution, File Structure, References) replacing the prior 22-area classified-statement model.
- edit-context.py supports CRUD operations on Product, Concepts, Requirements, and Solution sections with format enforcement per section type.
- Analysis document Proposed Solution section uses three sub-sections: High-Level Concept, Execution Steps (task-action hierarchy using Task N headers and single-file-or-command action bullets; S09 planner reads this section for plan generation), and High-Level Concept only; Why this approach? sub-section removed; six mandatory top-level sections total.
- verify-context.py validates context.md format compliance against context-convention.md with a 12-check validation set.
- verify-input.py validates input.md YAML header, mandatory body sections, and Q-block format against input-convention.md and q-block-convention.md, exiting with code 0 on all checks passing and code 1 on any failure.
- aib-analyze.md invokes verify-input.py and verify-context.py within S01 preflight (after reading instructions.md) when their respective enabled flags are true; on failure halts with per-check fix suggestions.
- menu.py verify_input and verify_context commands run the respective verification scripts, update YAML result flags in input.md, and are hidden from the menu when their enabled flag is false.
- input.md YAML frontmatter uses two nested groups: state: (tool-managed: request_id, title, status (workflow state; values idle|analysis_ready|questions_generated), input_verification_result, context_verification_result) and options: (user-configurable: minimum_questions, input_verification_enabled, context_verification_enabled); parse_input_header() raises ValueError on old flat format.
- log-entry.py provides per-request audit logging with --general flag for non-request-scoped events; accepts --message and --workspace; log entries follow YYYYMMDD-HHmmss: message format in UTC; log file moved to request subfolder on close.
- aib-analyze.md supports --plan-only modifier that skips analysis generation and question generation, reads existing analysis for execution steps when available, and produces a plan with autonomous decision-making.
- aib-implement.md supports --exec-input modifier that replaces plan-file reading with direct execution from input.md ## Input section while retaining context.md for product-context awareness.
- aib-modify.md provides a direct-execution prompt that reads input.md ## Input as an implementation directive and applies changes immediately without analysis or request finalization, using context.md for product awareness.
- aib-create-request.md encapsulates the auto-request-creation logic (formerly Appendix A of aib-analyze.md) as a standalone reusable prompt invoked by both aib-analyze.md and aib-modify.md when no active request exists.
- aib-setup.yaml in .aib_memory/ is the human-editable YAML setup file with flat top-level keys memory_version and default_questions_number; replaces the empty vX.Y.Z file convention for memory-side version tracking; initialize.py generates it on workspace setup with inline defaults and restores it with memory_version merge on upgrade.
- Input archives preserve original input.md content at REQUEST-FOLDER/input-archive-TIMESTAMP.md.
- read-setup.py retrieves a single named option from .aib_memory/aib-setup.yaml; prints bare value to stdout; exits with code 1 and prints an error to stderr when the requested key is absent or the file is missing.
- context.md is fully replaced on each aib-refresh-context.md execution; during refresh, each [PLANNED] entry is re-evaluated against the current workspace and the [PLANNED] tag is removed when the feature is confirmed realized; entries that cannot be confirmed are preserved verbatim.
- aib-sync-spec.md is a standalone interactive prompt that auto-creates an AIB request, reads an external specification file path from input.md ## Input, parses the spec at sentence level, generates one Q-block per contradiction, and adds non-contradictory AI-classified future-intent items as [PLANNED] entries and current-state items as plain entries.
- aib-input-from-context.md reads context.md [PLANNED] entries and Issues and appends structured goal bullets (one per item) to input.md ## Input; halts with error if an active request exists.
- Writable extensions registered in context.md ## References with Update: true are updated both during aib-refresh-context.md execution and after each aib-implement.md completion run.
- aib-sync-spec.md and aib-input-from-context.md are listed under .aib_brain/prompts/ in the File Structure section.
- initialize.py --upgrade archives entire legacy .aib_memory/ to .aib_memory/archives/legacy_TIMESTAMP/ (plural archives/, legacy_ prefix, counter suffix on collision), sets memory_version_compatibility to initialized-not-populated in aib-setup.yaml, seeds fresh conforming memory, copies instructions.md unchanged from archive, generates placeholder context.md with # Product Context title and all five mandatory sections, generates migration-ready input.md using _build_input_seed() base with migration instructions structured as Goal/Sources/Reconstruction Targets/Constraints referencing archived context.md as primary source and archived input.md and aib-setup.yaml as optional sources, with conventions context-convention.md/input-convention.md/q-block-convention.md cited; archived requests are never restored to active memory.
- aib-setup.yaml in .aib_memory/ is the human-editable YAML setup file with flat top-level keys memory_version, default_questions_number, and memory_version_compatibility (values: compatible | not-compatible | initialized-not-populated); replaces the empty vX.Y.Z file convention for memory-side version tracking; initialize.py generates it on workspace setup with inline defaults and restores it with memory_version merge on upgrade; memory_version_compatibility is set to initialized-not-populated by initialize.py --upgrade and reset to compatible by menu.py on user confirmation of migration completion.
- menu.py displays a migration-completion screen when memory_version_compatibility is initialized-not-populated; screen offers Confirm Completed (calls set_setup_option to set field to compatible, continues to normal menu) and Exit; normal menu is blocked until field is compatible or absent.
- set_setup_option in common.py updates a single flat key in aib-setup.yaml by key name, appending the key if absent and preserving all other keys; symmetric counterpart to get_setup_option.

## File Structure

.aib_brain/
  conventions/ — normative rules for context.md, input.md, code, and all AIB artifacts (includes input-convention.md, log-convention.md)
  prompts/ — aib-analyze.md, aib-implement.md, aib-refresh-context.md, aib-modify.md, aib-create-request.md, aib-sync-spec.md, aib-input-from-context.md
  tools/ — Python scripts: close-request.py, common.py, create-request.py, edit-context.py, file-inventory.py, finalize-input.py, initialize.py, input-header.py, log-entry.py, menu.py, move-request-artifacts.py, read-setup.py, verify-context.py, verify-input.py
  user_guide.html — self-contained HTML user guide
  README.md — framework internals documentation
.aib_memory/
  context.md — product context (this file)
  input.md — developer intent channel and active-request state store (YAML frontmatter header)
  instructions.md — persistent workspace directives
  aib-setup.yaml — human-editable YAML setup file; flat top-level keys: memory_version, default_questions_number, memory_version_compatibility
  archives/ — Timestamped legacy archive subfolders created by initialize.py --upgrade; each subfolder named legacy_YYYYMMDD-HHMMSS/ contains the full pre-upgrade .aib_memory/ content
  requests/ — Active and closed request folders following pattern R-YYYYMMDD-HHmi-SLUG/
docs/ — project documentation files
logs/
  next_version_changes.md — curated change bullets for next CI release
  version logs — 48+ per-version logs following pattern version_vX.Y.Z_log.md
recordings/ — 8 sequential WebM tutorial files (01_installation through 08_context)
scripts/
  release_bookkeeping.py — CI release bookkeeping: SemVer bump and log generation
tests/ — automated pytest suite for AIB conventions and tools (22 test files)
versions/ — 35+ versioned .aib_brain/ zip archives following pattern aib_brain_vX.Y.Z.zip
README.md — project overview with installation instructions and video tutorial links

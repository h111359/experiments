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
- ## Issues section in context.md captures identified contradictions and quality concerns as plain bullets; entries must be removed when resolved or no longer applicable.
- aib-input-from-context.md is a prompt that reads all [PLANNED] entries and Issues from context.md and appends structured goal bullets to input.md ## Input; fails with error when an active request already exists.
- [PLANNED] tagged entries in context.md represent features intended for future implementation; permitted inline in Product, Concepts, Solution, and Requirements sections with syntax dash-space-[PLANNED]-space-statement or dash-space-[PLANNED]-MUST:-space-text for Requirements; the tag is removed when the feature is implemented via a plan-driven edit-context.py delete + insert pair.
- memory_version_compatibility is a durable upgrade-progress token in aib-setup.yaml with three values: compatible (normal operation), not-compatible (version mismatch detected), initialized-not-populated (upgrade complete but migration prompt not yet confirmed); written as initialized-not-populated by initialize.py --upgrade and reset to compatible by menu.py on user confirmation.
- Context extensions are AIB-managed Markdown files named context-EXTENSION-NAME.md and registered in mandatory context.md ## References entries with Location, Summary, Convention, Prompt, Read, and Update metadata; only Read and Update values are user-editable.
- Extension flags accept case-insensitive yes or no input and are normalized to lowercase; Read: yes extensions are loaded only when their Summary is semantically relevant.
- AIB .aib_brain/ Write Protection means every path under .aib_brain/ is protected from ordinary workflow writes; installation, upgrade, and framework-maintenance requests carrying a semantically explicit authorization statement supplied in input.md ## Input or the developer chat message and propagated verbatim into analysis and plan are the only exceptions.
- AIB bytecode prevention is self-contained: launchers export PYTHONDONTWRITEBYTECODE=1; prompt-prescribed AIB Python commands use -B; menu.py propagates the bytecode-disabled environment and uses -B for child tools; release_bookkeeping.py rejects packaged .aib_brain/ archives containing __pycache__/ or .pyc files.
- AIB scratch directory .aib_memory/scratch/ is the required AIB-managed location for task-specific helpers prescribed by .aib_brain/ instructions when those helpers are created inside the repository; initialize.py seeds it and finalize-input.py sweeps it at every analysis-time reset.

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
- MUST NOT: Secrets, credentials, or tokens are stored in any AIB artifact.
- MUST: Requirements section statements use [MUST|MUST NOT|OPTIONAL] modality prefix.
- MUST: verify-context.py MUST be updated whenever context-convention.md quality gates are changed.
- MUST: verify-input.py MUST be updated whenever input-convention.md validation rules are changed.
- MUST: AIB stores active-request state in input.md YAML frontmatter grouped into state: (tool-managed: request_id, title, status, verification results) and options: (user-configurable: minimum_questions, verification enabled flags); input.md is the single source of truth for active-request state.
- MUST: [PLANNED] tag must be removed from context.md when the associated feature is implemented; removal must be plan-driven via explicit edit-context.py delete + insert pair in the plan context update task.
- MUST: Every context.md contains the convention-defined context extension registry in ## References, in convention-defined order, with only Read and Update values user-editable.
- MUST: Extension entries registered in context.md ## References with Update: yes are refreshed by executing their registered Prompt during aib-refresh-context.md and after each successful aib-implement.md run.
- MUST NOT: AIB accepts legacy true or false values for context extension Read or Update fields.
- MUST: log-entry.py appends UTC-timestamped entries with YYYYMMDD-HHmmss: message format to .aib_memory/log.md in both idle and active workspace states; the file is created lazily on first write.
- MUST NOT: log-entry.py accepts the --general option; argparse rejects it as an unrecognized argument.
- MUST: Request closure archives the complete .aib_memory/log.md stream into the active request folder as log_REQUEST_ID.md by rename-to-staging rotation with conditional-newline binary append, fsyncs the archive before deleting the staging snapshot, and leaves .aib_memory/log.md empty.
- MUST NOT: .aib_brain/ paths are modified by ordinary AIB project workflows; installation, upgrade, and explicitly authorized framework-maintenance requests are the sole exceptions.
- MUST: Framework-maintenance requests targeting .aib_brain/ include an authorization statement semantically equivalent to the canonical example 'This request explicitly authorizes changes under .aib_brain/.' supplied in input.md ## Input or the developer chat message, and propagate it verbatim (with source) into analysis-REQUEST_ID.md ## Overview → ### Authorization and plan-REQUEST_ID.md ## Constraints.
- MUST: AIB launchers set PYTHONDONTWRITEBYTECODE=1 for the launcher process and its child processes; menu.py propagates the same environment and invokes Python child tools with -B; prompt-prescribed direct AIB Python commands use python -B or python3 -B.
- MUST: release_bookkeeping.py rejects packaging of .aib_brain/ when any __pycache__/ directory or .pyc file is present under .aib_brain/; archive validation exits with a non-zero code and lists every offending path.
- MUST: close-request.py keeps the request active and returns a non-zero exit code when runtime-log or clarification-history archival fails, including I/O errors; other artifact-move failures retain existing warn-and-continue behaviour.
- MUST: aib-clarify.md reads instructions.md before gathering context, observes applicable directives without invoking analysis or implementation, and supplies exact python -B or python3 -B commands to the user instead of executing scripts.
- MUST: aib-clarify.md directly records every presented question, implementation-impact explanation, offered option, user response, and revision in .aib_memory/clarification_questions.md; unanswered questions remain unanswered and persistence failures stop dependent workflow steps.
- MUST: Clarification history may begin before a request exists, survives request creation and analysis-time input reset, and archives alongside the runtime log as clarification_questions_REQUEST_ID.md with the active file left present and empty.
- MUST: Clarification-history archival preserves existing archive content, handles missing history, avoids duplicate content after repeated successful calls, and retains recoverable staged content on failure using the runtime log's at-least-once recovery contract.
- MUST: Every AIB prompt that reads context.md loads only semantically relevant extensions whose Read value resolves to yes; missing registered artifacts produce a warning and do not halt the caller. aib-clarify.md applies this policy directly within its self-contained workflow; other readers execute aib-context-read.md.
- MUST: Analysis preflight preserves Unicode request titles and the existing key=value header output on Windows without a manual environment-variable workaround, while retaining parsing and validation failures.

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
- edit-context.py supports CRUD operations on Product, Concepts, Requirements, and Solution sections with format enforcement per section type.
- verify-context.py validates context.md format compliance against context-convention.md with a 12-check validation set.
- verify-input.py validates input.md YAML header, mandatory body sections, and Q-block format against input-convention.md and q-block-convention.md, exiting with code 0 on all checks passing and code 1 on any failure.
- aib-analyze.md invokes verify-input.py and verify-context.py within S01 preflight (after reading instructions.md) when their respective enabled flags are true; on failure halts with per-check fix suggestions.
- menu.py verify_input and verify_context commands run the respective verification scripts, update YAML result flags in input.md, and are hidden from the menu when their enabled flag is false.
- input.md YAML frontmatter uses two nested groups: state: (tool-managed: request_id, title, status (workflow state; values idle|analysis_ready|questions_generated), input_verification_result, context_verification_result) and options: (user-configurable: minimum_questions, input_verification_enabled, context_verification_enabled); parse_input_header() raises ValueError on old flat format.
- aib-analyze.md supports --plan-only modifier that skips analysis generation and question generation, reads existing analysis for execution steps when available, and produces a plan with autonomous decision-making.
- aib-implement.md supports --exec-input modifier that replaces plan-file reading with direct execution from input.md ## Input section while retaining context.md for product-context awareness.
- aib-create-request.md encapsulates the auto-request-creation logic (formerly Appendix A of aib-analyze.md) as a standalone reusable prompt invoked by both aib-analyze.md and aib-modify.md when no active request exists.
- aib-setup.yaml in .aib_memory/ is the human-editable YAML setup file with flat top-level keys memory_version and default_questions_number; replaces the empty vX.Y.Z file convention for memory-side version tracking; initialize.py generates it on workspace setup with inline defaults and restores it with memory_version merge on upgrade.
- Input archives preserve original input.md content at REQUEST-FOLDER/input-archive-TIMESTAMP.md.
- read-setup.py retrieves a single named option from .aib_memory/aib-setup.yaml; prints bare value to stdout; exits with code 1 and prints an error to stderr when the requested key is absent or the file is missing.
- aib-sync-spec.md is a standalone interactive prompt that auto-creates an AIB request, reads an external specification file path from input.md ## Input, parses the spec at sentence level, generates one Q-block per contradiction, and adds non-contradictory AI-classified future-intent items as [PLANNED] entries and current-state items as plain entries.
- aib-input-from-context.md reads context.md [PLANNED] entries and Issues and appends structured goal bullets (one per item) to input.md ## Input; halts with error if an active request exists.
- aib-sync-spec.md and aib-input-from-context.md are listed under .aib_brain/prompts/ in the File Structure section.
- aib-setup.yaml in .aib_memory/ is the human-editable YAML setup file with flat top-level keys memory_version, default_questions_number, and memory_version_compatibility (values: compatible | not-compatible | initialized-not-populated); replaces the empty vX.Y.Z file convention for memory-side version tracking; initialize.py generates it on workspace setup with inline defaults and restores it with memory_version merge on upgrade; memory_version_compatibility is set to initialized-not-populated by initialize.py --upgrade and reset to compatible by menu.py on user confirmation of migration completion.
- menu.py displays a migration-completion screen when memory_version_compatibility is initialized-not-populated; screen offers Confirm Completed (calls set_setup_option to set field to compatible, continues to normal menu) and Exit; normal menu is blocked until field is compatible or absent.
- set_setup_option in common.py updates a single flat key in aib-setup.yaml by key name, appending the key if absent and preserving all other keys; symmetric counterpart to get_setup_option.
- aib-context-read.md centralizes context extension loading by applying normalized Read controls, Summary relevance, and non-blocking missing-artifact warnings.
- aib-refresh-context-data-model.md reconciles logical, physical, and analytical workspace models into context-data-model.md and validates the result with verify-context-data-model.py.
- initialize.py seeds the managed Context Data Model registry entry and a convention-valid no-model context-data-model.md during fresh initialization and upgrade.
- Context refresh and migration restore convention-managed extension metadata while preserving user-controlled Read and Update values.
- context.md uses Product, Concepts, Requirements, Solution, File Structure, mandatory References, and optional Issues sections, replacing the prior 22-area classified-statement model.
- Analysis document Proposed Solution section uses two sub-sections: High-Level Concept and Execution Steps; Execution Steps uses Task N headers and single-file-or-command action bullets consumed by the S09 planner; six mandatory top-level sections remain.
- context.md is fully replaced on each aib-refresh-context.md execution while preserving every [PLANNED] entry verbatim unless an explicit plan-driven edit-context.py delete and insert pair transitions it to current state.
- aib-modify.md provides a direct-execution prompt that applies input.md ## Input without analysis, uses context.md for product awareness, and archives artifacts and closes the request after successful completion.
- initialize.py --upgrade archives legacy .aib_memory under archives/legacy_TIMESTAMP, preserves workspace instructions and setup options, seeds conforming context and data-model extension artifacts with the managed registry, and prepares input.md for semantic context migration without restoring archived requests.
- aib-context-migration.md reconstructs context.md from a legacy archived version, reconciles the managed extension registry and empty data-model extension, and requires both context validators before completion.
- log-entry.py is a state-independent appender that writes UTC-timestamped entries in the YYYYMMDD-HHmmss: message format to .aib_memory/log.md and echoes each entry to stdout; it accepts --workspace and --message only.
- move-request-artifacts.py owns shared-log archival: renames .aib_memory/log.md to a staging snapshot, creates an empty new root, streams the snapshot into the active request folder as log_REQUEST_ID.md in binary mode with a conditional single-newline separator, fsyncs the archive, and deletes the staging snapshot; the workflow is single-writer and legacy log_general.md and root log_REQUEST_ID.md files are never modified.
- aib-update-adr-requirements.md is a subroutine prompt invoked by aib-implement.md (tag I), aib-modify.md (tag M), and aib-execute.md (tag E) that appends UTC-timestamped rows to .aib_memory/adr.md and .aib_memory/requirements.md, dedups by normalized-text match, retries once and halts caller on second failure, and follows .aib_brain/conventions/adr-requirements-convention.md; legacy A-tagged rows are preserved.
- The canonical .aib_brain/ write-protection policy lives in .aib_brain/conventions/coding-general-convention.md § 12; every writing prompt in .aib_brain/prompts/ carries the concise protection block and a reference to that canonical section.
- initialize.py seeds .aib_memory/scratch/ with a .gitkeep sentinel during fresh workspace setup and preserves the directory on --upgrade; finalize-input.py sweeps every file and subdirectory under .aib_memory/scratch/ except .gitkeep at the end of the archive/reset sequence, and .aib_brain/ instructions use scratch for in-repository task-specific helpers.
- aib-clarify.md uses eight workflow steps with instruction loading first, question recording at presentation, response and revision recording at reception, and a final copy-paste-ready Input proposal using headings at level 3 or below; q-block-convention.md defines stable QIDs and appended response events.
- .aib_memory/clarification_questions.md stores clarification history independently of input.md; move-request-artifacts.py shares its durable rotation helper with log.md, drains clarification_questions-staging-REQUEST_ID.md before newer entries, and appends to the request-folder clarification_questions_REQUEST_ID.md archive.
- SharedArchiveError distinguishes audit-stream archival failures from ordinary artifact-move failures; LogArchiveError and ClarificationArchiveError identify the failed stream so close-request.py preserves active state on path, rotation, append, fsync, or cleanup errors.
- aib-clarify.md defines workspace-instruction handling and context-extension loading directly in its own workflow and does not read, invoke, or delegate to other prompts; references to other workflows used as examples are adapted into local instructions.
- input-header.py, verify-input.py, and verify-context.py configure stdout and stderr as UTF-8 at CLI entry through common.configure_utf8_output; aib-analyze.md requires subprocess wrappers to decode both captured streams as UTF-8, preserving Unicode titles in the unchanged key=value header protocol.

## File Structure

.aib_brain/
  conventions/ — normative rules for context.md, input.md, code, and all AIB artifacts (includes input-convention.md, log-convention.md)
  prompts/ — aib-analyze.md, aib-clarify.md, aib-context-read.md, aib-context-migration.md, aib-create-request.md, aib-implement.md, aib-input-from-context.md, aib-modify.md, aib-refresh-context-data-model.md, aib-refresh-context.md, aib-sync-spec.md
  tools/ — Python scripts: close-request.py, common.py, create-request.py, edit-context.py, file-inventory.py, finalize-input.py, initialize.py, input-header.py, log-entry.py, menu.py, move-request-artifacts.py, read-setup.py, verify-context-data-model.py, verify-context.py, verify-input.py
  user_guide.html — self-contained HTML user guide
  README.md — framework internals documentation
.aib_memory/
  context.md — product context (this file)
  context-data-model.md — managed data-model context extension
  input.md — developer intent channel and active-request state store (YAML frontmatter header)
  log.md — active shared runtime log written by every log-entry.py invocation; archived into the active request folder as log_REQUEST_ID.md at request closure
  instructions.md — persistent workspace directives
  aib-setup.yaml — human-editable YAML setup file; flat top-level keys: memory_version, default_questions_number, memory_version_compatibility
  adr.md — append-only architecture-decision history maintained by aib-update-adr-requirements.md
  requirements.md — append-only user-requirements history maintained by aib-update-adr-requirements.md
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

## References

### Context Data Model
Location: .aib_memory/context-data-model.md
Summary: Logical, physical, and analytical schemas, entities, and relationships discovered in the workspace.
Convention: .aib_brain/conventions/context-data-model-convention.md
Prompt: .aib_brain/prompts/aib-refresh-context-data-model.md
Read: no
Update: yes

## Issues

- .aib_memory/instructions.md requires phase commits but does not define how request-scoped changes should be staged when unrelated working-tree changes already exist.
- log-entry.py allows newline characters inside --message, although the log convention requires exactly one line per invocation; message validation is currently outside the log-convention line-format scope.
- tests/test_close_request.py creates an obsolete unsuffixed plan.md fixture inside the request folder that is no longer used by the current tests and conflicts with the artifact naming convention.
- tests/test_artifact_placement.py labels its move cases T1 through T5 but implements T1, T2, and T5 only; the unimplemented cases and the log-move branch remain untested.
- .aib_brain/prompts/aib-execute.md retains aib-modify log labels and user-facing references even though its title and goal identify the Execute workflow.
- aib-analyze.md writes an analysis backup before its no-input halt check, directs plan generation toward archived input despite the archive-read prohibition, and detects contexts below 50 words without refreshing them.
- input-convention.md permits null, valid, and invalid verification results in its schema table but later requires verification-result flags to remain literal null.
- tests/test_analysis_prompt_structure.py contains stale prompt-name, section-name, and step-number descriptions even though most assertions target current prompt strings.
- Pre-existing helper scripts and cache directories under .aib_brain/tools/ remain out of scope and can cause archive validation to reject release packaging until a separately authorized cleanup removes the contamination.

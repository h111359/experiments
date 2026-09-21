# AIB Workspace Guide

Open [user_guide.html](.aib_brain/user_guide.html) in a browser for the full interactive user guide.

AI Builder (AIB) is a minimal but powerful framework for AI specification-driven development. AIB serves for software development, documentation creation, data processing and all other activities which can be achieved with AI.

## The Most Important Commands for Copy-Paste

**Launch the interactive menu:**

.aib_brain\run.bat        # Windows

sh .aib_brain/run.sh      # Linux / macOS

**Prompt Invocations**

Execute .aib_brain/prompts/aib-analyze.md

Execute .aib_brain/prompts/aib-implement.md

## Objectives:

  - To analyze the user input and to generate analysis and plan markdown files
  
  - To generate questions to the user for those aspects which can lead to different implementation
  
  - to write a detailed plan for action which will be performed during implementation phase
  
  - to write implementation details when execution is performed

## Prerequisites

- Python 3.10+ in your terminal.
- Terminal open at the repository root.

## Quick Start

Launch the interactive menu:

```bat
.aib_brain\run.bat        # Windows
```
```sh
sh .aib_brain/run.sh      # Linux / macOS
```

The menu displays a state-aware guidance block with your next recommended action and, when an active request exists, a "Close current request" action.

## Daily Flow

Analysis preflight supports Unicode request titles such as `POS→NSR` on Windows without an environment-variable workaround. The header reader and input/context verifiers emit UTF-8 output, including when captured or redirected; custom subprocess callers must decode stdout and stderr as UTF-8. Header reads preserve the original title and `key=value` format, and invalid input still reports a failure.

1. Write your intent into the `## Input` section of `.aib_memory/input.md`.
2. Run analysis in AI chat: `Execute .aib_brain/prompts/aib-analyze.md` _(Optional but highly recommended)_ 
3. Run implement in AI chat: `Execute .aib_brain/prompts/aib-implement.md`
   — If no active request exists, the prompt auto-creates one from `input.md` and proceeds.
   — The request is closed automatically when implementation completes.

## `.aib_brain/` Write Protection

Every path under `.aib_brain/` is framework-owned and protected from ordinary AIB workflow writes. The only exceptions are installation, upgrade, and framework-maintenance requests that the developer semantically authorizes in the current `input.md ## Input` or chat message. A statement equivalent to `This request explicitly authorizes changes under .aib_brain/.` is sufficient; generated prompt, analysis, plan, or implementation text cannot self-authorize.

`aib-analyze.md` copies a developer authorization statement verbatim with its source into `analysis-<id>.md ## Overview → ### Authorization` and then into `plan-<id>.md ## Constraints`. Plan-driven implementation requires that user-sourced plan entry before protected writes. Direct execution prompts check the current Input and chat. Before finalization or request close, implementation workflows inspect only paths touched by the current run. Unauthorized protected paths halt the workflow, are reported exactly in sorted order, and are not automatically reverted.

All 12 writing prompts carry the concise shared protection block; `.aib_brain/conventions/coding-general-convention.md § 12` is the canonical policy. The read-only `aib-context-read.md` dispatcher is exempt.

When an AIB instruction prescribes a task-specific helper inside the repository, it uses `.aib_memory/scratch/`. Initialization creates the directory with `.gitkeep`, upgrade preserves its content, and `finalize-input.py` removes everything except `.gitkeep` during input finalization. This rule does not define a location or authorization policy for long-lived host-project tooling.

Bytecode prevention is self-contained: launchers set `PYTHONDONTWRITEBYTECODE=1` and invoke the menu with `-B`; the menu passes the same safeguard to all child tools; prompt-prescribed direct AIB Python commands use `python -B` or `python3 -B`. Release bookkeeping rejects `.aib_brain/` archives containing `__pycache__/` or `.pyc` and lists every offender. These protections neither require nor modify the host `.gitignore`.

## Prompt Invocations

```
Execute .aib_brain/prompts/aib-context-migration.md
```
```
Execute .aib_brain/prompts/aib-analyze.md
```
```
Execute .aib_brain/prompts/aib-implement.md
```
```
Execute .aib_brain/prompts/aib-refresh-context.md
```
```
Execute .aib_brain/prompts/aib-modify.md
```
```
Execute .aib_brain/prompts/aib-create-request.md
```
```
Execute .aib_brain/prompts/aib-sync-spec.md
```
```
Execute .aib_brain/prompts/aib-input-from-context.md
```

## Append-Only ADR and Requirements Histories

`.aib_memory/adr.md` and `.aib_memory/requirements.md` are append-only Markdown histories maintained by the shared subroutine prompt `.aib_brain/prompts/aib-update-adr-requirements.md`, whose row schema, provenance-tag registry, UTC timestamp requirement, dedup rule, and retry-once-then-halt failure semantics are codified in `.aib_brain/conventions/adr-requirements-convention.md`. The subroutine is invoked as the final documentation step of every implementation-oriented run.

## Use Cases

**Full analysis → implement flow**
1. Write request into `input.md → ## Input`.
2. Run `aib-analyze.md` — auto-creates request, generates `analysis-<id>.md` and `plan-<id>.md`.
3. Review `plan-<id>.md`; adjust if needed.
4. Run `aib-implement.md` — executes scope and closes request automatically.

**Direct implement (no formal analysis)**
1. Write request into `input.md → ## Input`.
2. Run `aib-implement.md` — auto-creates request from input and implements.

**Refresh workspace context**
- Run `aib-refresh-context.md` at any time (no active request required) to refresh `.aib_memory/context.md`.

**Sync external spec with context**
- Place the path to a spec file in `input.md ## Input`.
- Run `aib-sync-spec.md` — it reads the spec at sentence level, generates Q-blocks for contradictions, and adds non-contradictory future-intent items as `[PLANNED]` entries.
- Answer any Q-blocks generated and re-run to complete the synchronisation.

**Generate input from context**
- Ensure no active request is open.
- Run `aib-input-from-context.md` — it collects all `[PLANNED]` entries and `## Issues` bullets from `context.md` and appends them as structured goal bullets to `input.md ## Input`.
- Then run `aib-analyze.md` or `aib-implement.md` to act on the collected goals.

## Workspace Instructions (`instructions.md`)

`.aib_memory/instructions.md` is a persistent directives file read by every AIB prompt before it executes. Write any workspace-specific rules here — coding conventions, naming rules, always/never behaviors. If absent or empty, all prompts continue normally.

**Do not store secrets, credentials, or PII in this file.**

## Questions and Answers

`aib-clarify.md` reads `.aib_memory/instructions.md` before gathering context and
observes its applicable directives without starting analysis or implementation.
Its workflow is self-contained: workspace-instruction handling and context-extension
loading are defined directly in the clarification prompt, without invoking other prompts.
It never runs scripts; when a command is needed, it supplies the exact command
for the user, with `python -B` or `python3 -B` for AIB tools.

During clarification, the agent directly records every presented Q-block in
`.aib_memory/clarification_questions.md`, including all options and recommended
markers, and appends user responses and numbered revisions as they arrive.
Unanswered questions stay explicitly unanswered. The record survives resumed
sessions and input resets; rereading it does not duplicate existing events.
The final output is a copy-paste-ready replacement for `## Input`, with headings
at level 3 or below. The transcript stays in the history file. A session must
support direct file editing; persistence failures stop the dependent step.

History may begin before a request exists. At request archival,
`move-request-artifacts.py` appends it to
`<request-folder>/clarification_questions_<request_id>.md` alongside the runtime
log and leaves the active file present and empty. Existing archive bytes are
preserved, missing history is harmless, and repeated successful archival does
not duplicate content. Both streams use durable staged rotation; a history
archival failure keeps the request active and preserves content for recovery
on the next call. Crash recovery can replay staged bytes, as for the runtime
log. See `conventions/log-convention.md` for recovery details. This history is
specific to clarification; other prompts and earlier transcripts are unaffected.

When `aib-analyze.md` identifies decision points with multiple valid implementation choices where the preferred option has a materially different impact on the codebase, it generates a `## Questions` section in `input.md`.

**How it works:**

1. After analysis runs, open `.aib_memory/input.md`. If any questions were generated, a `## Questions` section will appear at the end of the file.
2. Each question includes:
   - The question text.
   - A `> **Why this matters:**` line explaining the implementation impact.
   - For multiple-choice: mutually exclusive options with checkboxes; the first option is marked `*(recommended)*` as the AI's preferred choice.
   - For free-text: a `- Answer: ___` field when no bounded options exist.
   - Format templates and rules for both Q-block types are defined in `.aib_brain/conventions/q-block-convention.md`.
3. Answer questions by checking `[x]` next to your chosen option (multiple-choice), or writing a free-text answer after `- Answer:`.
4. If you leave a question unanswered, the Answer Application Sub-flow halts with an error message and leaves `input.md` unchanged. All Q-blocks must be answered before re-running analysis.
5. Re-run `aib-analyze.md` — the prompt reads your answers, applies them to the relevant `plan.md` sections, and clears the `## Questions` section from `input.md`.

**Note:** The `## Questions` section is ephemeral — it is never part of the `input.md` seed template and is fully cleared after each Q&A cycle.

## Context Management Features

### [PLANNED] Tags in `context.md`

Statements in `context.md` may be prefixed with `[PLANNED]` to mark future-intent features not yet implemented.

**Syntax by section:**
- Product, Concepts, Solution: `- [PLANNED] <statement text>`
- Requirements: `- [PLANNED] MUST: <text>` / `- [PLANNED] MUST NOT: <text>` / `- [PLANNED] OPTIONAL: <text>`

**Lifecycle:** When the described feature is implemented, the plan must include an `edit-context.py delete` + `edit-context.py insert` pair that removes the `[PLANNED]` prefix and replaces the entry with a plain statement. Automated scanning MUST NOT remove tags; only plan-driven removal is authoritative.

**Carve-out from pruning:** `[PLANNED]` entries are exempt from the "current state only" pruning rule in `aib-refresh-context.md`. They are forward-looking markers with an explicit removal lifecycle.

**Example — adding a planned entry:**
```
python -B .aib_brain/tools/edit-context.py --operation insert --area Concepts --planned --text "New feature description" --workspace .
```

### `## Issues` Section in `context.md`

An optional 7th section `## Issues` can be added to `context.md` to track identified contradictions and quality concerns.

**Format:** Plain bullets only — `- <description>`. No sub-headings or status fields.

**Lifecycle:** Issues entries MUST be removed when the issue is resolved or no longer applicable.

**Example — adding an issue:**
```
python -B .aib_brain/tools/edit-context.py --operation insert --area Issues --text "Inconsistency between X and Y needs resolution" --workspace .
```

### Context Extensions

`context.md ## References` is a mandatory, AIB-managed registry of all convention-defined context extensions. AIB owns each heading plus its `Location`, `Summary`, `Convention`, `Prompt`, and ordering. Users may edit only `Read` and `Update`.

Both controls accept case-insensitive `yes` or `no` and are normalized to lowercase during managed refresh or migration. Legacy `true` and `false` values are invalid.

- `Read: yes` makes an extension eligible for loading; `aib-context-read.md` still requires semantic relevance based on `Summary`.
- `Read: no` skips loading.
- `Update: yes` executes the registered `Prompt` during `aib-refresh-context.md` and after successful `aib-implement.md` runs.
- `Update: no` skips refresh.

**Canonical managed entry:**
```
### Context Data Model
Location: .aib_memory/context-data-model.md
Summary: Logical, physical, and analytical schemas, entities, and relationships discovered in the workspace.
Convention: .aib_brain/conventions/context-data-model-convention.md
Prompt: .aib_brain/prompts/aib-refresh-context-data-model.md
Read: no
Update: yes
```

Fresh initialization and upgrade create this registry plus `.aib_memory/context-data-model.md`. When no model is discovered, the extension contains the canonical no-model notice. `aib-refresh-context-data-model.md` performs exhaustive, conservative reconciliation and `verify-context-data-model.py` validates the result with eight checks.

If a registered Location, Convention, or Prompt artifact is missing, the calling workflow emits a warning and continues without that artifact. Context refresh and migration restore drifted AIB-managed metadata while preserving valid Read and Update choices. Legacy bibliographic References are not retained in the managed registry.

### `aib-sync-spec.md` — Synchronise Context with External Spec

**When to use:** You have an external specification file (requirements doc, design doc, architecture decision record) and want to synchronise its content with `context.md`.

**How to use:**
1. Write the path to the spec file in `input.md ## Input`.
2. Run: `Execute .aib_brain/prompts/aib-sync-spec.md`
3. If contradictions are detected, Q-blocks are generated. Answer them and re-run.
4. On the second run (or on first run if no contradictions), non-contradictory items are applied: future-intent items as `[PLANNED]` entries, current-state items as plain entries.

**Files affected:** `.aib_memory/context.md`, `.aib_memory/input.md`

### `aib-input-from-context.md` — Generate Input from Context

**When to use:** You want to turn accumulated `[PLANNED]` entries and `## Issues` from `context.md` into a structured implementation backlog in `input.md`.

**Precondition:** No active request may exist when this prompt runs. It fails with an error if `status != idle`.

**How to use:**
1. Ensure no active request is open.
2. Run: `Execute .aib_brain/prompts/aib-input-from-context.md`
3. Goal bullets are appended to `input.md ## Input`.
4. Then run `aib-analyze.md` to plan their implementation.

**Output format:**
- `[PLANNED]` entries → `- Implement: <statement text>`
- Issues entries → `- Resolve issue: <description>`

**Files affected:** `.aib_memory/input.md` (append only)

  - AIB shall be defined entirely in a folder called `.aib_brain/` with files and subfolders in it where are defined the prompts, templates, conventions and tools of the framework (generic, non-specific and replaceable part).
   
  - The artifacts in `.aib_brain/` shall be used to seed the folder `.aib_memory/` (if not existing) in the same folder where `.aib_brain/` is located. 
  
  - AIB work will be organized in a series of requests defined in files and file structure as per this document. In the requests are defined the context and specifications needed for AI to build or change the product accordingly the expectation of the human. 
  
  - The AI-produced output (the product) is driven by the functionalities defined in `.aib_brain/` and the information stored in `.aib_memory`. 
  
  - `.aib_brain/` installed in a project folder SHALL NOT be modified by ordinary AIB workflows. Installation, upgrade, and user-authorized framework-maintenance requests are the only exceptions.

  - The request to AIB shall be defined in file `input.md` in `.aib_memory/`. The active request state (request ID, title, state, options) is stored in a YAML frontmatter header at the top of `input.md`.

  - During a request, an analysis and plan for implementation will be created.
  
  - The artifacts of AIB shall be separated by their lifecycle. In `.aib_brain/` folder shall be stored reusable framework assets (prompts, conventions, tools). On upgrade this folder shall be replaceable entirely. In `.aib_memory/` shall be stored project specific artifacts - project-specific requests and iteration artifacts
  
  - All kind of formatting specifications, shared and common definitions, extended context or similar shall be located in `.aib_brain/conventions/` folder in markdown files.
  
  - Scripts to support AIB workflow shall be placed in `.aib_brain/tools/` folder. Python 3.10+ is the prime choice of programming language for the scripts.
  
  - Active request state is tracked in the YAML frontmatter header of `.aib_memory/input.md` grouped into two nested blocks: `state:` (tool-managed: `request_id`, `title`, `status` (idle|analysis_ready|questions_generated), `input_verification_result`, `context_verification_result`) and `options:` (user-configurable: `minimum_questions`, `input_verification_enabled`, `context_verification_enabled`). Only one active request can exist at a time. Closed requests are identifiable from their folder structure under `.aib_memory/requests/`.
  
  - The product knowledge for the workspace is consolidated in `.aib_memory/context.md`, updated by `aib-refresh-context.md` on each execution. 
  
  - Developers MAY use `.aib_memory/instructions.md` to flag any additional files that AIB prompts should read or treat with special care.

  - AIB shall be model and vendor agnostic. This means it shall be executable in all environments like VS Code with GitHub copilot, Claude Code, Cursor or similar and with different models like GPT 5.3 Codex, Claude Code 4.6 Opus, Gemini 3.1 or better.


### Folder structure

.aib_brain/
  - conventions/ (includes input-convention.md for input.md format spec, log-convention.md for audit log format, adr-requirements-convention.md for adr.md/requirements.md row schema, tag registry, dedup, and failure semantics)
  - prompts/
    - aib-context-migration.md (migration prompt; reconstructs context.md from a legacy archived version; reads the archive source path from input.md ## Input; applies lossless semantic transformation rules; run via aib-modify.md after initialize.py --upgrade)
    - aib-context-read.md (shared extension dispatcher; applies Read and semantic relevance controls and reports missing artifacts)
    - aib-analyze.md (analysis and planning prompt)
    - aib-implement.md (implementation and request-close prompt)
    - aib-refresh-context.md (context refresh prompt)
    - aib-refresh-context-data-model.md (registered data-model extension reconciliation prompt)
    - aib-modify.md (direct-execution prompt; applies input.md ## Input immediately without analysis cycle, then archives artifacts and closes the request)
    - aib-execute.md (direct-execution prompt with context-updating responsibility; identical to aib-modify.md except that Step 7.5 REQUIRES emitting and executing edit-context.py commands whenever context.md needs to change)
    - aib-create-request.md (standalone auto-request-creation prompt; formerly Appendix A of aib-analyze.md; invoked by aib-analyze.md and aib-modify.md when state == idle)
    - aib-sync-spec.md (interactive prompt that synchronises context.md with an external spec file; auto-creates request, generates Q-blocks for contradictions, adds non-contradictory items as [PLANNED] entries)
    - aib-input-from-context.md (reads [PLANNED] entries and Issues from context.md and appends goal bullets to input.md ## Input; fails if active request exists)
    - aib-update-adr-requirements.md (shared subroutine invoked as the final documentation step by aib-implement.md, aib-modify.md, and aib-execute.md; appends provenance-tagged rows to .aib_memory/requirements.md and .aib_memory/adr.md per .aib_brain/conventions/adr-requirements-convention.md)
  - tools/
    - close-request.py
    - create-request.py
    - edit-context.py (CRUD for atomic statements in context.md)
    - file-inventory.py
    - finalize-input.py
    - initialize.py
    - input-header.py (CRUD for YAML frontmatter header in input.md)
    - log-entry.py (state-independent appender; writes UTC-timestamped entries to .aib_memory/log.md and echoes each entry to stdout; accepts --workspace and --message only)
    - move-request-artifacts.py (moves plan and analysis artifacts from .aib_memory/ root to the active request subfolder; archives log.md and clarification_questions.md into request-suffixed files via rename-to-staging binary append with fsync-before-cleanup; either archival failure blocks closure)
    - read-setup.py (read a single option from .aib_memory/aib-setup.yaml; prints bare value to stdout; exits 1 on missing key or file)
    - verify-context.py (validates context.md format: 12 automated checks)
    - verify-context-data-model.py (validates context-data-model.md format: 8 automated checks)
    - verify-input.py (validates input.md format: 10 automated checks)
  - README.md
  - run.bat
  - run.sh
  - user_guide.html
  - vM.m.p (semver marker file — encodes the brain version; memory-side version is tracked separately in .aib_memory/aib-setup.yaml)
.aib_memory/
  - attachments/
  - requests/
  - scratch/ (managed task-specific helpers; .gitkeep retained when finalization sweeps content)
  - aib-setup.yaml (human-editable YAML setup file; flat top-level keys: memory_version, default_questions_number; replaces the empty vX.Y.Z file convention for memory-side version tracking)
  - context.md
  - context-data-model.md (managed logical, physical, and analytical model extension)
  - input.md
  - instructions.md
  - log.md (shared active runtime log; every log-entry.py invocation appends here; archived to <request-folder>/log_<request_id>.md at request closure)
  - clarification_questions.md (clarification Q-blocks, answers, and revisions; survives input reset; archived as clarification_questions_<request_id>.md and left empty)
  - adr.md (append-only architecture-decision history maintained by aib-update-adr-requirements.md per adr-requirements-convention.md)
  - requirements.md (append-only user-requirements history maintained by aib-update-adr-requirements.md per adr-requirements-convention.md)
logs/
  - next_version_changes.md
  - version_vX.Y.Z_log.md (per-version logs)
versions/
  - aib_brain_vX.Y.Z.zip (versioned archives)

## Request Folder Artifacts

| Artifact | Created by | Description |
| --- | --- | --- |
| `plan-<id>.md` | `aib-analyze.md` | Execution specification. Contains background, exact file paths in all procedure steps, and exact `edit-context.py` invocations for context updates. External files (including `context.md`) are still needed to execute the plan. Active copy lives at `.aib_memory/plan-<id>.md`; moved to request subfolder after implementation. |
| `analysis-<id>.md` | `aib-analyze.md` | Reasoning artifact (not read by `implement`). |
| `input-archive-*.md` | `aib-analyze.md` | Archived `input.md` per analysis run. Never read by prompts after archiving. |

## Upgrade Process

When `menu.py` detects a version mismatch between the brain version (`.aib_brain/vMAJOR.MINOR.PATCH`) and the memory version (`aib-setup.yaml → memory_version`), it automatically invokes `initialize.py --upgrade`.

### What the upgrade script does

1. **Archives the full pre-upgrade `.aib_memory/`** to `.aib_memory/archives/legacy_YYYYMMDD-HHMMSS/`. All existing memory files — `context.md`, `input.md`, `instructions.md`, `requests/`, `aib-setup.yaml` — are preserved in this timestamped subfolder. If two upgrades happen within the same second, a counter suffix is appended (`legacy_YYYYMMDD-HHMMSS-1`, etc.).
2. **Sets `memory_version_compatibility: initialized-not-populated`** in `aib-setup.yaml` so the menu knows migration is pending.
3. **Seeds a fresh conforming memory structure** from brain templates.
4. **Copies `instructions.md` unchanged and restores `scratch/` content** from the archive back to the new memory root so workspace-level directives and in-progress managed helpers are not lost merely because the framework is upgraded.
5. **Generates a valid placeholder `context.md`** with `# Product Context`, all mandatory content sections, and the canonical managed References registry. This placeholder passes the 12 checks in `verify-context.py` but must be populated from workspace evidence.
6. **Creates `context-data-model.md`** in the canonical no-model state so the registry never points to a missing extension; it passes the 8 checks in `verify-context-data-model.py`.
7. **Generates migration-ready `input.md`** using the standard idle YAML seed, pre-loaded with a single prose activation paragraph that directs the AI to run `.aib_brain/prompts/aib-context-migration.md` with the workspace-relative path to the archived legacy `context.md`. Migration restores managed registry metadata, converts recognizable legacy flags, and preserves user-controlled Read and Update values. When `context.md` is absent from the archive, the paragraph references `aib-refresh-context.md` instead.

Requests are **never** automatically restored to active memory. Legacy requests remain exclusively in `.aib_memory/archives/legacy_YYYYMMDD-HHMMSS/requests/`.

### After upgrade

After the upgrade completes, `memory_version_compatibility` is set to `initialized-not-populated` in `aib-setup.yaml`. On the next menu launch, a **migration-completion screen** is displayed instead of the normal menu. This screen blocks normal operation until the developer completes the migration:

1. Open an AI chat interface (VS Code Copilot, Claude Code, etc.).
2. Run: `Execute .aib_brain/prompts/aib-modify.md`
3. The activation paragraph in `input.md ## Input` directs the AI to run `aib-context-migration.md`, which reads the legacy `context.md` from the archive path specified in the input and reconstructs `context.md` using lossless semantic migration rules.
4. Once the migration prompt has completed successfully, return to the menu and choose **Confirm Completed**. The menu sets `memory_version_compatibility: compatible` and resumes normal operation.

All legacy files are available in the archive folder for reference. The AI reads the archived `context.md` (primary source) and optionally `input.md` and `aib-setup.yaml` to perform semantic reconstruction.


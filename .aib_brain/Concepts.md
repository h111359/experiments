## Goal: 

AI Builder (AIB) is a minimal but powerful framework for AI specification based development called. AIB serves for software development, documentation creation, data processing and all other activities which can be achieved with AI.

## Objectives:

  - to be able when I ask AIB to analyze the request and to generate an analysis markdown file in the active request folder under `.aib_memory/requests/<request-folder>/`
  
  - to be able when I ask AIB to generate questions to me that are embedded in `request.md` under `## Questions & Decisions`, which the user can answer directly in that file
  
  - to be able to write a plan for action based on the defined changes and fulfilled questions
  
  - to be able to write implementation details when execution is performed

## Invocation contract (normative)

The key words "MUST", "MUST NOT", "SHALL", "SHOULD", and "MAY" in this section are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174).

This section defines the deterministic action contract for user-triggered AIB operations.

### Supported actions

- `initialize`: Initialize AIB memory structures and default artifacts.
- `create-request`: Create and register a new request.
- `close-request`: Close the active request.
- `create-analysis`: Generate analysis document and update `request.md` with implementation-relevant sections (Assumptions, Plan, Testing, Documentation, Questions & Decisions).
- `reverse-engineer`: Reverse engineer the workspace to populate editable documentation based on conventions.
- `implement`: Execute the active request scope and update implementation record.

### Common input resolution rules

- Script-backed actions MUST invoke the corresponding tool scripts in `.aib_brain/tools/`.
- `initialize` MUST invoke `.aib_brain/tools/initialize.py`.
- `create-request` MUST invoke `.aib_brain/tools/create-request.py`.
- `close-request` MUST invoke `.aib_brain/tools/close-request.py`.
- The invocation MUST resolve `request_id` from explicit user input when provided.
- If `request_id` is not provided, the invocation MUST resolve the single `Active` request from `.aib_memory/requests_register.md`.
- If no `Active` request exists and no explicit `request_id` is provided, execution MUST fail with a validation error and MUST NOT create output files.

### Action contract matrix

| Action | Required context | Output target | Output rule |
| --- | --- | --- | --- |
| `initialize` | Workspace root with `.aib_brain/` present | `.aib_memory/`, `.aib_memory/requests_register.md`, `.aib_memory/requests/`, `.aib_memory/context.md`, `.aib_memory/input.md`, `.aib_memory/instructions.md` | MUST invoke `.aib_brain/tools/initialize.py` and seed memory using canonical schema and default seed rules. |
| `create-request` | Initialized memory; no other request in `Active` state | `.aib_memory/requests_register.md`, `.aib_memory/requests/<request-folder>/request.md`, `.aib_memory/requests/<request-folder>/implementation.md` | MUST invoke `.aib_brain/tools/create-request.py` and register one new `Active` request. |
| `close-request` | Resolved request in `Active` state | `.aib_memory/requests_register.md` | MUST invoke `.aib_brain/tools/close-request.py` and set request state to `Closed`. |
| `create-analysis` | Resolved request | `.aib_memory/requests/<request-folder>/analysis.md`; `request.md` (optional sections 7–11) | MUST generate full analysis content from prompt/conventions. MUST update `request.md` with Assumptions, Plan, Testing, Documentation, and Questions & Decisions sections as applicable. |
| `reverse-engineer` | Initialized memory + readable workspace sources | `.aib_memory/context.md` | MUST execute the workspace-scan evidence collection (Phase 3 + Reverse-Engineering Evidence Collection of `aib-context.md`) and populate `context.md` with explicit traceability to workspace sources. |
| `implement` | Resolved request | `.aib_memory/requests/<request-folder>/implementation.md` | MUST rely on `request.md` as the sole implementation specification. MUST NOT read analysis, questionnaire, or plan iteration artifacts. Auto-triggers `aib-context.md` upon completion. |

### Determinism and safety rules

- Each action MUST write only to its target output file(s) and any explicitly required register file(s).
- Each action SHOULD be idempotent with the same resolved inputs (re-running should converge to the same output intent).
- On validation failure, the action MUST return a human-readable error and MUST NOT leave partial writes.
- If a required output file already exists, the action MAY replace it entirely, but the behavior MUST be consistent for the same tool configuration.

### Holistic workflow (normative)

Canonical end-to-end flow:

1. Run `initialize` once per project when `.aib_memory/` does not yet exist.
2. Write your request description into the `## Input` section of `.aib_memory/input.md`.
3. Optionally run `create-analysis` for the active request. If no Active request exists, `create-analysis` auto-creates one from `input.md` content, archives the input, and resets `input.md` with the active request ID as its last step (after all artifacts are written). This generates `analysis.md` and updates `request.md` with Assumptions, Plan, Testing, Documentation, and Questions & Decisions sections as applicable.
4. Run `implement` to execute the request scope and update `implementation.md`. If no Active request exists, `implement` automatically triggers the `create-analysis` flow without asking for user confirmation, then continues with implementation once analysis completes.
5. Run `close-request` to finalize the request when the request scope is completed.

Workflow guardrails:

- `create-request` MUST fail if another request is already `Active`.
- `create-analysis` MUST fail when no request is `Active` and `input.md` is empty; if `input.md` has content, it auto-creates a request.
- `implement` MUST auto-trigger `create-analysis` when no Active request exists, without asking for user confirmation.
- `close-request` SHOULD require that no open work remains for the request being closed.

`input.md` lifecycle:
- The developer writes intent into the `## Input` section of `.aib_memory/input.md`.
- `create-analysis` archives `input.md` to the request folder, then resets `input.md` to the seed template **as the last action** of the run (after all analysis artifacts are fully written). After reset, the `## Active request` line reflects the current active request ID and title (format: `<request_id> — <title>`), not the literal string `No active request`.
- The "No changes — provide answer only" toggle: when checked, `create-analysis` writes exactly one file (`answer-<timestamp>.md` in the request folder) and resets `input.md` with the active request ID. It MUST NOT modify `request.md`, `analysis.md`, or any other file.

## Concepts:

### Overall Concepts

  - AIB shall be defined entirely in a folder called `.aib_brain/` with files and subfolders in it where are defined the prompts, templates, conventions and tools of the framework (generic, non-specific and replaceable part).
   
  - The artifacts in `.aib_brain/` shall be used to seed the folder `.aib_memory/` (if not existing) in the same folder where `.aib_brain/` is located. 
  
  - AIB work will be organized in a series of requests defined in files and file structure as per this document. In the requests are defined the context and specifications needed for AI to build or change the product accordingly the expectation of the human. 
  
  - The AI-produced output (the product) is driven by the functionalities defined in `.aib_brain/` and the information stored in `.aib_memory`. 
  
  - `.aib_brain/` installed in a project folder SHALL NOT be modified by AIB tool scripts. Humans may replace or update `.aib_brain/` explicitly when evolving the framework.

  - The request shall be defined in a single file `request.md` in a dedicated folder under `.aib_memory/requests/`. In addition, a record shall be added for it in a file `.aib_memory/requests_register.md`.

  - During a request, an analysis or plan for implementation could be created. These are optional. `implementation.md` file must be generated during request implementation.

  - `implementation.md` is request-scoped and append-only with dated entries. Minimum entry fields: changes, tests, outcome.

  - The artifacts of AIB shall be separated by their lifecycle. In `.aib_brain/` folder shall be stored reusable framework assets (prompts, conventions, templates, tools). On upgrade this folder shall be replaceable entirely. In `.aib_memory/` shall be stored project specific artifacts - project-specific requests and iteration artifacts

  - For creation of analysis, questionnaire or plan shall exist separate prompts defining the instructions to be followed. These prompts shall be located in a subfolder `.aib_brain/prompts/` in form of markdown files.

  - For creation of new files under `.aib_memory` or plan shall exist a collection of template files to be used for seed. These templates shall be located in a subfolder `.aib_brain/templates/` in form of markdown files.
    
  - All kind of formatting specifications, shared and common definitions, extended context or similar shall be located in `.aib_brain/conventions/` folder in markdown files.
  
  - Scripts to support AIB workflow shall be placed in `.aib_brain/tools/` folder. Python 3.10+ is the prime choice of programming language for the scripts.
  
  - A file `.aib_memory/requests_register.md` shall contain a list with the requests the user has generated. Each request record shall contain the request ID in format "R-<YYYYMMDD>-<HHmi>", request title, relative path to the request folder and states (Active, Closed). Many Closed requests could coexist. Only one Active request shall exist at a time. No new requests shall be created until the current Active one is closed.
  
  - The product knowledge for the workspace is consolidated in `.aib_memory/context.md`, generated and fully replaced by `aib-context.md` on each execution. Developers MAY use `.aib_memory/instructions.md` to flag any additional files that AIB prompts should read or treat with special care.

  - AIB shall be model and vendor agnostic. This means it shall be executable in all environments like VS Code with GitHub copilot, Claude Code, Cursor or similar and with different models like GPT 5.3 Codex, Claude Code 4.6 Opus, Gemini 3.1 or better.

### Lifecycle state model (normative)

Request lifecycle states:
- `Active`: Request is in progress.
- `Closed`: Request is finalized.

Allowed request transitions:
- `Active -> Closed`
- `Closed` is terminal.

Iteration lifecycle states:
- `Active`: Current working iteration for the request.
- `Completed`: Iteration is finished and superseded or finalized.

Allowed iteration transitions:
- `Active -> Completed`
- `Completed` is terminal.

Concurrency rules:
- Multiple requests may exist in `.aib_memory/requests/`.
- At most one request can be in `Active` state in `.aib_memory/requests_register.md`.

    
## Preferences

  - The folder structure to be simple
  - IDs and time stamps to be generated by the scripts, do not expect the human to fulfill
  - Avoid attributes for prioritization - it will be handled outside this structure
  - Avoid attributes for ownership - it will be handled outside this structure

## Implementation details:

### Folder structure

.aib_brain/
  - conventions/
  - prompts/  
  - templates/      
  - tools/
.aib_memory/
  - requests_register.md
  - context.md
  - requests/

### Content of request folder

Inside requests/, each request gets its own folder (example):
.aib_memory/requests/R-20260307-1342-create-backend-layer/
  - request.md
  - analysis.md
  - implementation.md

Folder format is join between request ID and request title: R-<YYYYMMDD>-<HHmi>-<request_title>

What each file means:
  - `request.md`: The canonical specification artifact. Contains Goal, Background, Scope, Out of scope, Constraints, Success criteria (mandatory), plus Assumptions, Plan, Testing, Documentation, and Questions & Decisions sections (optional, added by `create-analysis`).
  
  - `analysis.md`: AIB-generated reasoning and knowledge-capture artifact. NOT an implementation driver. Contains: Executive Summary, Scope Interpretation, Domain Knowledge Essentials, Technical Knowledge & Terms, Impact Assessment, Research Plan and Findings, Risks.
  
  - `implementation.md`: What was actually implemented, technical details, decisions, follow-ups.

### Minimal list of templates

  - .aib_brain/templates/requests_register-template.md
  - .aib_brain/templates/request-template.md

### Content headings per file

  - Request: Goal, Background, Scope, Out of scope, Constraints, Success criteria (mandatory); Assumptions, Plan, Testing, Documentation, Questions & Decisions (optional, added by create-analysis).
  - Analysis: Executive Summary, Scope Interpretation, Domain Knowledge Essentials, Technical Knowledge & Terms, Impact Assessment, Research Plan and Findings, Risks.
  - Implementation: Scope, Changes, Tests, Outcome, Evidence, Notes (Optional).
    
### Minimal prompts to be defined

  - `.aib_brain/prompts/aib-analysis.md` -> creates `analysis.md` and updates `request.md` with implementation-relevant sections (Assumptions, Plan, Testing, Documentation, Questions & Decisions as applicable).
  - `.aib_brain/prompts/aib-implement.md` -> based on `request.md` of the Active request, builds/changes the product, creates/adds and runs tests (if case is software development), works continuously until the work is done and all tests are passed successfully.
  - `.aib_brain/prompts/aib-context.md` -> synthesizes and fully replaces `.aib_memory/context.md` from workspace sources. Also serves as the reverse-engineering entry point when no product-doc content is yet available.
    
### Minimal tools to be defined

  - `.aib_brain/tools/initialize.py` -> creates .aib_memory/ folder and seeds using the canonical schema and default seed rules.
    
  - `.aib_brain/tools/create-request.py` -> registers a new request in `.aib_memory/requests_register.md` with state Active and creates a folder for the request under `.aib_memory/requests`

  - `.aib_brain/tools/close-request.py` -> change the state of the request to Closed

### Minimal conventions to be defined

  - .aib_brain/conventions/requests_register-convention.md
  - .aib_brain/conventions/request-convention.md
  - .aib_brain/conventions/analysis-convention.md
  - .aib_brain/conventions/plan-convention.md
  - .aib_brain/conventions/implementation-convention.md
  - .aib_brain/conventions/context-convention.md

  - A convention file shall exist for the `context.md` product knowledge artefact: `.aib_brain/conventions/context-convention.md`.


## Documentation Domains

The following domain taxonomy defines the knowledge domains used to classify product documentation and drive the `## Domain Summary` section of `context.md`. When performing workspace synthesis or reverse-engineering, map discovered artefacts to these domains.

| Domain | Acronym | Scope summary |
| --- | --- | --- |
| Architecture | ARCH | Defines foundational principles, high-level structural design, key decisions, and strategic direction for data & analytics products. |
| Compute | CMP | Defines and documents reproducible computational procedures and analytical logic (scripts, notebooks, formulas, parameters, performance). |
| Data | DATA | Standards for definition, structure, quality, access, lineage, classification, lifecycle and governance of data assets. |
| Development | DEV | Standards for SDLC: developer setup, code practices, CI/CD, testing, collaboration, maintainability and security. |
| Disaster Recovery | DSR | Plans and procedures to recover data/systems (RPO/RTO, backups, restoration testing). |
| Financial | FNL | Budgeting, forecasting, cost tracking, variance analysis, optimization and cost allocation. |
| Knowledge | KNW | Business/domain knowledge: glossary, data dictionary, processes, use cases, personas, key decisions. |
| Requirements | RQT | Define, prioritize and accept requirements; manage change to requirements. |
| Observability | OBS | Metrics, alerting, logging, and tracing standards. |
| Operations | OPR | Runbooks, SOPs, task inventories, health checks, SLO/SLA expectations. |
| Security | SEC | Confidentiality, integrity, availability: access control, protection, secrets, network security, compliance. |


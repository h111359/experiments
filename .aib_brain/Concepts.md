## Goal: 

AI Builder (AIB) is a minimal but powerful framework for AI specification based development called. AIB serves for software development, documentation creation, data processing and all other activities which can be achieved with AI.

## Objectives:

  - to be able when I ask AIB to analyze the request and to generate an analysis markdown file in the active request folder under `.aib_memory/requests/<request-folder>/`
  
  - to be able when I ask AIB to generate questions to me and these questions to be written as a questionnaire in the active request folder
  
  - to be able to write a plan for action based on the defined changes and fulfilled questionnaires
  
  - to be able to write implementation details when execution is performed

## Invocation contract (normative)

The key words "MUST", "MUST NOT", "SHALL", "SHOULD", and "MAY" in this section are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174).

This section defines the deterministic action contract for user-triggered AIB operations.

### Supported actions

- `initialize`: Initialize AIB memory structures and default artifacts.
- `create-request`: Create and register a new request.
- `create-iteration`: Create and register a new iteration for a request.
- `close-iteration`: Close the active iteration for a request.
- `close-request`: Close the active request.
- `create-analysis`: Generate iteration analysis document.
- `create-questionnaire`: Generate iteration questionnaire document.
- `create-plan`: Generate iteration execution plan document.
- `reverse-engineer`: Reverse engineer the workspace to populate editable documentation based on conventions.
- `implement`: Execute the active request scope and update implementation record.

### Common input resolution rules

- Script-backed actions MUST invoke the corresponding tool scripts in `.aib_brain/tools/`.
- `initialize` MUST invoke `.aib_brain/tools/initialize.py`.
- `create-request` MUST invoke `.aib_brain/tools/create-request.py`.
- `create-iteration` MUST invoke `.aib_brain/tools/create-iteration.py`.
- `close-iteration` MUST invoke `.aib_brain/tools/close-iteration.py`.
- `close-request` MUST invoke `.aib_brain/tools/close-request.py`.
- The invocation MUST resolve `request_id` from explicit user input when provided.
- If `request_id` is not provided, the invocation MUST resolve the single `Active` request from `.aib_memory/requests_register.md`.
- If no `Active` request exists and no explicit `request_id` is provided, execution MUST fail with a validation error and MUST NOT create output files.
- For iteration-scoped actions (`create-analysis`, `create-questionnaire`, `create-plan`), `iteration_id` MUST be resolved from explicit input when provided, otherwise from the `Active` iteration in `iterations.md`.
- If no active iteration exists for an iteration-scoped action, execution MUST fail with a validation error and MUST NOT create output files.

### Action contract matrix

| Action | Required context | Output target | Output rule |
| --- | --- | --- | --- |
| `initialize` | Workspace root with `.aib_brain/` present | `.aib_memory/`, `.aib_memory/requests_register.md`, `.aib_memory/references.md`, `.aib_memory/requests/`, `.aib_memory/docs/` | MUST invoke `.aib_brain/tools/initialize.py` and seed memory using canonical schema and default seed rules. |
| `create-request` | Initialized memory; no other request in `Active` state | `.aib_memory/requests_register.md`, `.aib_memory/requests/<request-folder>/request.md`, `.aib_memory/requests/<request-folder>/iterations.md` | MUST invoke `.aib_brain/tools/create-request.py`, register one new `Active` request, and create default iteration `01` as `Active`. |
| `create-iteration` | Resolved request in `Active` state | `.aib_memory/requests/<request-folder>/iterations.md` | MUST invoke `.aib_brain/tools/create-iteration.py`, create next strictly ascending iteration ID, and enforce single active iteration for the request. |
| `close-iteration` | Resolved request + resolved active iteration | `.aib_memory/requests/<request-folder>/iterations.md` | MUST invoke `.aib_brain/tools/close-iteration.py` and move the active iteration to its terminal non-active state according lifecycle rules. |
| `close-request` | Resolved request in `Active` state | `.aib_memory/requests_register.md` | MUST invoke `.aib_brain/tools/close-request.py` and set request state to `Closed`. |
| `create-analysis` | Resolved request + resolved iteration | `.aib_memory/requests/<request-folder>/<ITERATION_ID>-analysis.md` | MUST generate full file content from prompt/conventions for analysis. Auto-triggers `create-questionnaire` when unresolved questions exist. |
| `create-questionnaire` | Resolved request + resolved iteration | `.aib_memory/requests/<request-folder>/<ITERATION_ID>-questionnaire.md` | MUST generate full file content from prompt/conventions for questionnaire. |
| `create-plan` | Resolved request + resolved iteration + available clarifications | `.aib_memory/requests/<request-folder>/<ITERATION_ID>-plan.md` | MUST generate full file content from prompt/conventions for plan. |
| `reverse-engineer` | Initialized memory + readable workspace sources | `product-doc` files in `.aib_memory/references.md` where `edit_allowed=Y` | MUST read `.aib_memory/references.md`, enforce per-doc convention mapping (fail-closed), and populate target docs with explicit traceability to workspace sources. |
| `implement` | Resolved request | `.aib_memory/requests/<request-folder>/implementation.md` | MUST update implementation record according to implementation prompt and request scope. Auto-triggers `update-documentation` upon completion. |

### Determinism and safety rules

- Each action MUST write only to its target output file(s) and any explicitly required register file(s).
- Each action SHOULD be idempotent with the same resolved inputs (re-running should converge to the same output intent).
- On validation failure, the action MUST return a human-readable error and MUST NOT leave partial writes.
- If a required output file already exists, the action MAY replace it entirely, but the behavior MUST be consistent for the same tool configuration.

### Holistic workflow (normative)

Canonical end-to-end flow:

1. Run `initialize` once per project when `.aib_memory/` does not yet exist.
2. Run `create-request` to open a new `Active` request and create iteration `01` as `Active`.
3. Optionally run any iteration artifact actions for the active iteration in this order as needed:
  - `create-analysis`
  - `create-questionnaire`
  - `create-plan`
4. Run `implement` to execute the request scope and update `implementation.md`.
5. If additional clarifications are needed, run `create-iteration` and repeat step 3 and step 4 for the new active iteration.
6. Run `close-iteration` to finalize the current active iteration when no further iteration work is needed.
7. Run `close-request` to finalize the request when the request scope is completed.

Workflow guardrails:

- `create-request` MUST fail if another request is already `Active`.
- `create-iteration`, `create-analysis`, `create-questionnaire`, `create-plan`, `implement`, and `close-iteration` MUST fail when no request is `Active` unless `request_id` is explicitly provided and valid.
- `close-request` SHOULD require that no iteration remains `Active` for the request being closed.

## Concepts:

### Overall Concepts

  - AIB shall be defined entirely in a folder called `.aib_brain/` with files and subfolders in it where are defined the prompts, templates, conventions and tools of the framework (generic, non-specific and replaceable part).
   
  - The artifacts in `.aib_brain/` shall be used to seed the folder `.aib_memory/` (if not existing) in the same folder where `.aib_brain/` is located. 
  
  - AIB work will be organized in a series of requests defined in files and file structure as per this document. In the requests are defined the context and specifications needed for AI to build or change the product accordingly the expectation of the human. 
  
  - The AI-produced output (the product) is driven by the functionalities defined in `.aib_brain/` and the information stored in `.aib_memory`. 
  
  - `.aib_brain/` installed in a project folder SHALL NOT be modified by AIB tool scripts. Humans may replace or update `.aib_brain/` explicitly when evolving the framework.

  - The request shall be defined in a single file `request.md` in a dedicated folder under `.aib_memory/requests/`. In addition, a record shall be added for it in a file `.aib_memory/requests_register.md`.

  - Request clarification is supposed to be made in iterations. During initiation of the request shall be created default iteration 01. In case of need the user can create more iterations.

  - Iterations shall be registered in a file `iterations.md` in the request subfolder

  - During each iteration could be created an analysis, questionnaire to the user or plan for implementation. None of these are mandatory. The user can decide to generate one of them, two of them, all of them or to skip entirely all of them. `implementation.md` file must be generated during request implementation.

  - `implementation.md` is request-scoped and append-only with dated/iteration-tagged entries. Minimum entry fields: iteration ID, changes, tests, outcome.
  
  - Iteration files (except `implementation.md`) shall be written in the request folder with prefixes - the ID of the iteration
  
  - Questionnaire structure and answer format are governed by `.aib_brain/conventions/questionnaire-convention.md`, which defines the QID-based canonical Question Block format. Refer to that convention for the authoritative schema.
  
  - The user shall edit the questionnaire file by checking the answer they prefer or provide free text answer.

  - It is supposed the iterations to complement each other, but in case of conflict, the iteration with higher ID is considered the truth.

  - The artifacts of AIB shall be separated by their lifecycle. In `.aib_brain/` folder shall be stored reusable framework assets (prompts, conventions, templates, tools). On upgrade this folder shall be replaceable entirely. In `.aib_memory/` shall be stored project specific artifacts - project-specific requests and iteration artifacts

  - For creation of analysis, questionnaire or plan shall exist separate prompts defining the instructions to be followed. These prompts shall be located in a subfolder `.aib_brain/prompts/` in form of markdown files.

  - For creation of new files under `.aib_memory` or plan shall exist a collection of template files to be used for seed. These templates shall be located in a subfolder `.aib_brain/templates/` in form of markdown files.
    
  - All kind of formatting specifications, shared and common definitions, extended context or similar shall be located in `.aib_brain/conventions/` folder in markdown files.
  
  - Scripts to support AIB workflow shall be placed in `.aib_brain/tools/` folder. Python 3.10+ is the prime choice of programming language for the scripts.
  
  - A file `.aib_memory/requests_register.md` shall contain a list with the requests the user has generated. Each request record shall contain the request ID in format "R-<YYYYMMDD>-<HHmi>", request title, relative path to the request folder and states (Active, Closed). Many Closed requests could coexist. Only one Active request shall exist at a time. No new requests shall be created until the current Active one is closed.
  
  - A file `.aib_memory/references.md` shall contain the location of project documentation files as per `Product_Documentation.md`. It also can be complemented by the human other files which AIB shall read or edit. Initially it shall be seeded with a default content with references to the product documentation files, which the user can change on a later stage. Each file record shall have toggle Y/N flag if AIB is allowed to edit the file.
  
  - By default the documentation files are located in subfolders of `.aib_memory/docs/` according to the "Location" attribute of each file in `Product_Documentation.md`. But the user can decide to change the location of the respective documents.

  - AIB shall be model and vendor agnostic. This means it shall be executable in all environments like VS Code with GitHub copilot, Claude Code, Cursor or similar and with different models like GPT 5.3 Codex, Claude Code 4.6 Opus, Gemini 3.1 or better.

### references.md schema (normative)

`references.md` defines what AIB may read and edit.

Required table columns:
- `ref_id`: Stable unique ID (format `REF-0001`, `REF-0002`, ...).
- `title`: Human-readable file name.
- `path`: Workspace-relative path (must not be absolute).
- `type`: One of `product-doc|source-code|domain|other`.
- `edit_allowed`: `Y|N`.
- `source`: `default|user`.
- `notes`: Optional constraints/context.

Default seeding rule:
- On memory initialization, seed all entries from `Product_Documentation.md` locations with:
  - `edit_allowed=Y`
  - `source=default`
- Product documentation resolution for initialization SHALL use `.aib_brain/Product_Documentation.md` as the single canonical location.

#### Seeding mapping rule (normative)

To eliminate interpretation variance, seeding from `Product_Documentation.md` to `.aib_memory/references.md` SHALL follow the rules below.

Input extraction from `Product_Documentation.md`:
- A requirement entry is identified by headings in format `##### <REQUIREMENT_ID> - <TITLE> **[<PRIORITY>]**`.
- `REQUIREMENT_ID` SHALL match regex `^[A-Z]{3}-[0-9]{2}$` (examples: `ARCH-01`, `DATA-09`).
- The requirement `Location` SHALL be read from the nearest `Location: **...**` line in the same requirement block.

Default documentation file mapping:
- One documentation file SHALL be seeded per requirement entry.
- Default documentation file path SHALL be:
  - `.aib_memory/docs/<LocationPath>/<REQUIREMENT_ID>.md`
- `<LocationPath>` is derived from `Location` by:
  - splitting by `/`
  - trimming surrounding whitespace in each segment
  - joining segments with `/` as folder separators
- Each seeded row in `.aib_memory/references.md` SHALL be:
  - `type=product-doc`
  - `edit_allowed=Y`
  - `source=default`
  - `title=<REQUIREMENT_ID> - <TITLE>`

Deterministic row identity rules:
- `ref_id` SHALL be generated as `REF-0001`, `REF-0002`, ... in ascending lexical order of `REQUIREMENT_ID`.
- If the same `REQUIREMENT_ID` appears multiple times, the entry is invalid and MUST be reported as a validation error.
- If two rows resolve to the same `path`, both rows are invalid and MUST be reported as validation errors.

Worked example (`references.md` row):

| ref_id | title | path | type | edit_allowed | source | notes |
| --- | --- | --- | --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | product-doc | Y | default | Seeded from Product_Documentation.md |

Validation rules:
- `ref_id` must be unique.
- `path` must be unique.
- Rows with invalid values are ignored by automation and reported as validation errors.

### Lifecycle state model (normative)

Request lifecycle states:
- `Active`: Request is in progress and can accept new iterations.
- `Closed`: Request is finalized; no new iterations can be created.

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
- At most one iteration can be in `Active` state per request in `iterations.md`.

#### Iteration files naming (normative)

Use `ITERATION_ID` as a two-digit numeric token (`01`, `02`, ...), matching regex `^[0-9]{2}$`.

File names must follow these exact patterns:
- `<ITERATION_ID>-analysis.md`
- `<ITERATION_ID>-questionnaire.md`
- `<ITERATION_ID>-plan.md`

Examples:
- `01-analysis.md`
- `01-questionnaire.md`
- `01-plan.md`

    
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
  - references.md
  - requests/
  - docs/
    - 01 Product Management/
    - 02 Domain/
    - 03 Requirements/
    - 04 Technology/

### Content of request folder

Inside requests/, each request gets its own folder (example):
.aib_memory/requests/R-20260307-1342-create-backend-layer/
  - request.md
  - iterations.md
  - 01-analysis.md
  - 01-questionnaire.md
  - 01-plan.md
  - implementation.md

Folder format is join between request ID and request title: R-<YYYYMMDD>-<HHmi>-<request_title>

What each file means:
  - `request.md`: Your original change description (what you want changed in AIB framework, why, scope, constraints).
  
  - `iterations.md`: A register of the iterations in the course of request processing. Must be a register table with the columns:
    - `iteration_id` (e.g., `01`, `02`)
    - `state` (`Active` | `Completed`)
    - `created_at` (local time)
    - `closed_at` (local time, empty unless `Completed`)
    - `summary` (short purpose/outcome)
   Validation rules:
    - Exactly one `Active` iteration is allowed per request.
    - `closed_at` is required when `state = Completed`.
    - Iteration IDs are strictly ascending and never reused.
  
  - `<ITERATION_ID>-analysis.md`: AIB-generated analysis of impact, assumptions, affected modules, risks. 
  
  - `<ITERATION_ID>-questionnaire.md`: AIB-generated clarifying questions for the user to answer. 
  
  - `<ITERATION_ID>-plan.md`: Step-by-step execution plan based on request + answers. 
  
  - `implementation.md`: What was actually implemented, technical details, decisions, follow-ups.

### Minimal list of templates

  - .aib_brain/templates/requests_register-template.md
  - .aib_brain/templates/references-template.md
  - .aib_brain/templates/request-template.md
  - .aib_brain/templates/iterations-template.md

### Content headings per file

  - Request: Goal, Background, Scope, Out of scope, Constraints, Success criteria.
  - Analysis: Executive Summary, Scope Interpretation, Domain Knowledge Essentials, Technical Knowledge & Terms, Assumptions, Impact Assessment, Research Plan and Findings, Rewrite Proposal, Solution Options, Affected Documentation, Operational & Documentation Implications, Risks, Open Questions & Next Actions.
  - Questionnaire: numbered questions with answer format hints.
  - Plan: MUST follow `.aib_brain/conventions/plan-convention.md` (no Markdown tables). Key sections include Overview, Scope of Work, Decision Gates, WBS, Dependencies & Interfaces, Environment & Configuration, Testing Strategy, Observability & Quality Gates, Documentation Touchpoints, Milestones, Risks & Mitigations, Acceptance & Handover.
  - Implementation: Scope, Changes, Tests, Outcome, Evidence, Notes (Optional).
    
### Minimal prompts to be defined

  - `.aib_brain/prompts/aib-analysis.md` -> creates `<ITERATION_ID>-analysis.md` file according to the convention for analysis.
  - `.aib_brain/prompts/aib-questionnaire.md` -> creates `<ITERATION_ID>-questionnaire.md` file according to the convention for questionnaire.
  - `.aib_brain/prompts/aib-plan.md` -> creates `<ITERATION_ID>-plan.md` file according to the convention for plan (template not required).
  - `.aib_brain/prompts/aib-implement.md` -> based on the files of the Active request, builds/changes the product, creates/adds and runs tests (if case is software development), work continuously until the work is done and all tests are passed successfully.
  - `.aib_brain/prompts/aib-documentation.md` -> based on the files of the Active request, builds/changes the product documentation.
    
### Minimal tools to be defined

  - `.aib_brain/tools/initialize.py` -> creates .aib_memory/ folder and seeds using the canonical schema and default seed rules.
    
  - `.aib_brain/tools/create-request.py` -> registers a new request in `.aib_memory/requests_register.md` with state Active and creates a folder for the request under `.aib_memory/requests`
  
  - `.aib_brain/tools/create-iteration.py` -> registers new iteration in iterations.md and mark it active (mark closed the other if some is not)
  
  - `.aib_brain/tools/close-iteration.py` -> change the state of an iteration to Closed

  - `.aib_brain/tools/close-request.py` -> change the state of the request to Closed

### Minimal conventions to be defined

  - .aib_brain/conventions/requests_register-convention.md
  - .aib_brain/conventions/references-convention.md
  - .aib_brain/conventions/request-convention.md
  - .aib_brain/conventions/iterations-convention.md
  - .aib_brain/conventions/analysis-convention.md
  - .aib_brain/conventions/questionnaire-convention.md
  - .aib_brain/conventions/plan-convention.md
  - .aib_brain/conventions/implementation-convention.md
  
  - A convention file shall exist per each document file from `Product_Documentation.md` defining its format and way for editing. The convention file shall be named like this: <document_id>-convention.md (example: `.aib_brain/conventions/arch-01-convention.md`)




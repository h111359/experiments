Purpose
Define the authoritative format, naming, semantics, and operational rules for the file `request.md` located in every request folder under `.aib_memory/requests/<REQUEST_FOLDER>/`. This convention ensures deterministic parsing by AIB tools, consistent structure across all requests, and unambiguous interpretation of human‑provided specifications.

Scope
- Applies only to the single file `request.md` inside each request folder.  
- Covers: file structure, required headings, allowed content, ID resolution, constraints, and editing rules.  
- Excludes: rules for iterations and iteration artifacts (analysis, questionnaire, plan, implementation).

File Location & Naming (normative)
- MUST be named exactly `request.md`.  
- MUST be placed inside a dedicated folder under `.aib_memory/requests/`.  
- Request folder name MUST follow:  
  `R-<YYYYMMDD>-<HHmi>-<request_title>`  
  where the timestamp is created by tooling, not the human.
- Only one `request.md` may exist per request folder.

Request Identity (normative)
- Request identity is defined by:
  - `request_id` extracted from the folder name:  
    `R-<YYYYMMDD>-<HHmi>`  
  - The request title (slug) forming the suffix of the folder name.  
- Creation of `request.md` MUST occur via the `create-request` action.  
- On creation:
  - The new request MUST be registered in `.aib_memory/requests_register.md`.  
  - The request MUST be set to state `Active`.  
  - Iteration `01` MUST be created automatically.

Document Structure (normative)
The file MUST contain the following top-level sections in the exact order shown below.  
All headings MUST be level‑2 (`##`).  
Each section MUST be present, even if empty.

1. `## Goal`  
   - A concise description of what the human wants changed/created.  
   - MUST be 1–10 sentences.

2. `## Background`  
   - Context explaining why the change is needed.  
   - MAY reference documentation files listed in `references.md`.

3. `## Scope`  
   - Clear definition of what is included in the change.  
   - MUST explicitly list impacted functional areas, components, domains, or documents.  
   - Scope MUST be precise enough for AIB to reason deterministically.
4. `## Out of scope`  
   - Items intentionally excluded from the request.  
   - MUST NOT be empty; include at least one entry (“No exclusions” is allowed).

5. `## Constraints`  
   - All assumptions, limitations, or boundary conditions.  
   - SHOULD include business constraints, technical constraints, and timing restrictions.  
   - MUST avoid ambiguity; if undefined, specify “None”.

6. `## Success criteria`  
   - MUST define measurable outcomes that indicate completion.  
   - SHOULD link criteria to testability or user acceptance conditions.

Formatting Rules (normative)
- Only level‑2 headings (`##`) are allowed for the required sections.  
- Level‑3 headings MAY be used inside sections.  
- No metadata header (Title/Version/Owner/etc.) is allowed.  
- No hyperlinks, references, or footnotes that require external resolution.  
- Markdown lists MUST use `-` or `1.` consistently.  
- Code blocks MAY appear only inside the `Background` or `Scope` section if showing input/output examples.

Content Rules (normative)
- The request MUST describe desired *intent*, not implementation.  
- The request MUST avoid specifying iteration-specific content (iterations are separate entities).  
- The request SHOULD:
  - articulate user expectation with sufficient detail for tooling to generate analysis & questionnaires,  
  - avoid contradictions with documented product requirements in `.aib_memory/docs/` (if contradictions exist, they MUST be resolved via iterations).  
- The request MUST NOT instruct the tools to violate lifecycle rules (e.g., creating multiple active requests). 

Lifecycle & Editing Rules (normative)
- Only one request in the system MAY be `Active` at a time.  
- A request becomes `Closed` via `close-request`; after that:
  - `request.md` becomes read‑only except for human archival comments.  
  - Tools MUST NOT modify the request after closure.  
- Human edits:
  - Allowed only while request is `Active`.  
  - MUST maintain section order and headings.  
  - SHOULD avoid unpredictable changes (rewriting the whole file breaks iteration continuity).  
- Tools:
  - MUST NOT auto-rewrite the content except where explicitly allowed (e.g., minor formatting normalization).  
  - MUST reject the request if mandatory sections are missing.

Validation Rules (normative)
A valid `request.md` MUST satisfy:
- All six required sections exist exactly once.  
- Section order is correct.  
- No undefined or extra top-level sections.  
- Content in each section is non-empty except where explicitly allowed.  
- File path matches the request folder.  
- Folder name matches naming convention and `request_id` is parseable.

Example Minimal Valid Structure (informative)
```
## Goal
Text…

## Background
Text…

## Scope
- Item 1
- Item 2

## Out of scope
- Item not included

## Constraints
- None

## Success criteria
- The system performs X
- Documentation updated
```

Operational Workflow (normative)
- `create-request` initializes `request.md` as an empty template with all mandatory sections.  
- `create-analysis`, `create-questionnaire`, `create-plan` MUST read `request.md` as their primary input.  
- `implement` MUST rely on `request.md` + iteration artifacts; it MUST NOT alter `request.md`.  
- Iterations complement the request; if contradictions arise, higher iteration IDs take precedence. 

Change Control (normative)
- Any updates to this convention MUST be made before generating new `request.md` files.  
- When the convention is updated, existing requests SHOULD NOT be rewritten automatically.  
- New requests MUST always follow the latest convention.
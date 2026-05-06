Purpose
Define the authoritative format, naming, semantics, and operational rules for the file `request.md` located in every request folder under `.aib_memory/requests/<REQUEST_FOLDER>/`. This convention ensures deterministic parsing by AIB tools, consistent structure across all requests, and unambiguous interpretation of human‑provided specifications.

Scope
- Applies only to the single file `request.md` inside each request folder.  
- Covers: file structure, required headings, allowed content, ID resolution, constraints, and editing rules.  
- Excludes: rules for iterations and iteration artifacts (analysis, questionnaire, plan, implementation).

File Location & Naming (normative)
- MUST be named exactly `request.md`.  
- **Two-phase placement rule:**
  1. **Active phase** — while the request is open, `request.md` resides at `.aib_memory/request.md` (workspace root of `.aib_memory/`, NOT inside the request subfolder). It is written here by `aib-analysis.md` and read from here by `aib-implement.md`.
  2. **Archived phase** — upon successful implementation completion, `request.md` is moved by `move-request-artifacts.py` to `.aib_memory/requests/<request-folder>/request.md` before `close-request.py` marks the request Closed.
- Re-runs of `aib-analysis.md` fully replace the active copy at `.aib_memory/request.md` without merging.
- Request folder name MUST follow:  
  `R-<YYYYMMDD>-<HHmi>-<request_title>`  
  where the timestamp is created by tooling, not the human.
- Only one `request.md` may exist per request folder (archived phase).

Request Identity (normative)
- Request identity is defined by:
  - `request_id` extracted from the folder name:  
    `R-<YYYYMMDD>-<HHmi>`  
  - The request title (slug) forming the suffix of the folder name.  
- Creation of `request.md` MUST occur via the `create-request` action.  
- On creation:
  - The new request MUST be registered in `.aib_memory/requests_register.md`.  
  - The request MUST be set to state `Active`.

Document Structure (normative)
The file MUST contain the following top-level sections in the exact order shown below.  
All headings MUST be level‑2 (`##`).  
All sections (1–12) are mandatory and MUST be present, even if empty. 

1. `## Goal`  
   - A concise description of what the human wants changed/created.  
   - MUST be 1–10 sentences.

2. `## Background`  
   - Context explaining why the change is needed.  
   - MAY reference documentation files in the workspace (for example `.aib_memory/context.md`).

3. `## Scope`  
   - Clear definition of what is included in the change.  
   - MUST explicitly list impacted functional areas, components, domains, or documents.  
   - Scope MUST be precise enough for AIB to reason deterministically.
   - Must be written in bullet-list form. Add extra empty line between bullets.
  
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

7. `## Assumptions`  
   - AI-generated list of implementation-affecting assumptions.  
   - Each entry: `- A<n>: <text>` with optional sub-bullet `  - Risk if false: <text>`.  
   - Fully replaced on every analysis re-run.

8. `## Plan`  
   - AI-generated Work Breakdown Structure (WBS) for the active iteration.  
   - Each task uses the following schema:
     ```
     ### Task <N>: <Task Name>
     **Intent:** <single-sentence goal>
     **Inputs:** <files, configs, parameters, data preconditions>
     **Outputs:** <artifacts produced or changed; file paths or product components>
     **External Interfaces:** <systems, data sources, modules consumed or produced>
     **Environment & Configuration:** <environments, config keys, secrets handling notes>
     **Procedure:** <ordered, concise steps>
     **Done Criteria:** <objective pass/fail checks>
     **Dependencies:** <Task IDs or external>
     **Risk Notes:** <if any>
     ```
   - Fully replaced on every analysis re-run.
   - Every plan MUST include: (a) a task defining automated test steps for the request scope (covering all testable Success Criteria); (b) a task to update `.aib_memory/context.md` and any other documentation files affected by the request, reflecting changes made and any discovered discrepancies.

9. `## Documentation`  
    - AI-generated list of documentation files that must be revised because of this request.  
    - Each entry: `- <path> (ref_id: <REF-ID>) — <reason for update>.`
    - If ref_id is unknown: `- <path> (ref_id: N/A) — <reason>`.  
    - Fully replaced on every analysis re-run.

10. `## Questions & Decisions`  
    - AI-generated question blocks requiring user input.  
    - Present only when the analysis identifies unknowns or decision forks that meet the severity threshold defined in `aib-analysis.md`.  
    - Each question block uses the following schema:  
      ```
      **Q<nnn>**: <question text>
      - [ ] Option A: <text>
      - [ ] Option B: <text> *(recommended)*
      - [ ] Other: ___
      > Answer: <free-text answer block — leave blank until answered>
      ```
    - SHOULD include a `*(recommended)*` suffix on the AI's preferred option where one is clearly identifiable. MAY omit the marker if no option is clearly preferable.
    - Re-run preservation rule: A question is "answered" if at least one checkbox is `[x]` OR the `> Answer:` block is non-empty. Answered questions MUST be applied as embedded instructions to the relevant sections of `request.md`, then removed from `## Questions & Decisions`. New unanswered questions are appended.
    - Conflict flagging: Append `> [!NOTE] DECISION REVIEW NEEDED: <reason>` to any answered question whose answer conflicts with an updated analysis context. Do not alter the answer itself.

11. `## Code and Asset Scan for Impacted Components`  
    - AI-generated table of workspace files, modules, pipelines, and assets impacted by this request.  
    - Format: Markdown table with columns `File/Asset`, `Change Type`, `Reason`.  
    - Change types: `Modified`, `Created`, `Deleted`, `Read-only dependency`.  
    - Fully replaced on every analysis re-run.

12. `## Internal Review of Request and Product Docs`  
    - AI-generated factual findings from reading `request.md` and `.aib_memory/context.md` (plus any additional documentation files explicitly listed by the developer in `.aib_memory/instructions.md`).  
    - Documents ambiguities, contradictions, missing information, and cross-reference issues found.  
    - Each finding: `- <finding-type>: <file> — <description>`.  
    - Finding types: `Ambiguity`, `Contradiction`, `Missing info`, `Cross-ref issue`, `OK`.  
    - Fully replaced on every analysis re-run.
    - This section records FACTUAL findings only (what is in the documents). Evaluative opinions belong in `analysis.md`.

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
- The six mandatory sections (Goal, Background, Scope, Out of scope, Constraints, Success criteria) exist exactly once and in order.  
- AI-generated sections (7–14) added by `create-analysis` are allowed after `## Success criteria`; they do not affect mandatory section validation before analysis is run.
- Content in each mandatory section is non-empty except where explicitly allowed.  
- File path matches the request folder.  
- Folder name matches naming convention and `request_id` is parseable.
- `## Amends` section MUST NOT appear in any `request.md`; use `input.md` for amendments.

Operational Workflow (normative)
- `create-request` creates the request folder and register entry. 
- `request.md` is generated by `create-analysis` (or by `aib-analysis.md` auto-request branch) from `input.md` content.  
- `implement` MUST rely on `request.md`; it MUST NOT alter `request.md`.  

Change Control (normative)
- Any updates to this convention MUST be made before generating new `request.md` files.  
- When the convention is updated, existing requests SHOULD NOT be rewritten automatically.  
- New requests MUST always follow the latest convention.
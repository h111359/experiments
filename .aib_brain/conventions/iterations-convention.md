Purpose
Define the canonical format, naming, lifecycle, and validation rules for iteration tracking within an AIB request. This convention ensures deterministic automation, human legibility, and frictionless execution across tools.

Scope
This convention applies to every request folder under `.aib_memory/requests/<request-folder>/` and governs:
- `iterations.md` register file
- Iteration-scoped artifact files:
  - `<ITERATION_ID>-analysis.md`
  - `<ITERATION_ID>-questionnaire.md`
  - `<ITERATION_ID>-plan.md`
It explicitly excludes `implementation.md` (request-scoped, append-only).

Outcomes
- Single source of truth for iteration state and chronology.
- Deterministic file names and table schema enabling scriptable operations.
- Clear human guidance for creating, closing, and referencing iterations.

Normative References
- AIB invocation contract and lifecycle (create/close iteration, artifacts, safety, determinism).
- Iteration file name patterns and ID format.

File Naming (Normative)
- Iteration ID token: `ITERATION_ID` MUST match regex `^[0-9]{2}$` (e.g., `01`, `02`, `03`).
- Artifact file names MUST be exactly:
  - `<ITERATION_ID>-analysis.md`
  - `<ITERATION_ID>-questionnaire.md`
  - `<ITERATION_ID>-plan.md`
- `iterations.md` MUST be the register file name (lowercase), located alongside iteration artifacts within the request folder.

Folder Location (Normative)
All iteration artifacts and `iterations.md` MUST reside in:
```
.aib_memory/requests/<request-folder>/
```
where `<request-folder>` is formatted as:
```
R-<YYYYMMDD>-<HHmi>-<request_title>
```
Whitespace in `<request_title>` is preserved; use hyphens for spaces when convenient, but scripts MUST NOT rely on hyphenization.

Lifecycle & Concurrency (Normative)
- Request states: `Active`, `Closed`. Iterations exist only for `Active` requests.
- Iteration states: `Active`, `Completed`.
- Exactly one `Active` iteration per request at any time.
- Allowed transitions:
  - `Active -> Completed` (terminal).
- New iterations MUST receive the next strictly ascending, unused `ITERATION_ID`. IDs are never reused.

Register Schema: `iterations.md` (Normative)
`iterations.md` MUST contain a single GitHub-Flavored Markdown table with the columns below in the exact order:

| iteration_id | state     | created_at     | closed_at      | summary |
|--------------|-----------|----------------------|----------------------|---------|

Column rules:
- `iteration_id`: REQUIRED. Two-digit string, `^[0-9]{2}$`.
- `state`: REQUIRED. One of `Active`, `Completed`.
- `created_at`: REQUIRED. ISO local timestamp in `YYYY-MM-DD HH:MM:SS ±HHMM` (24h, with seconds and timezone offset) using the operator’s local time when created.
- `closed_at`: REQUIRED iff `state=Completed`, else empty. Same format as `created_at`.
- `summary`: REQUIRED. Short human description (≤ 140 chars) of purpose/outcome.

Register Rules (Normative)
- Exactly one header row and one separator row.
- One data row per iteration, ordered ascending by `iteration_id`.
- At all times, at most one row where `state=Active`.
- When an iteration transitions to `Completed`, `closed_at` MUST be set and immutable thereafter.
- Rows MUST be edited only by AIB tools or intentional human edits following this convention.

Iteration Artifacts (Normative)
Each iteration MAY have zero or more of the following artifacts:
1) Analysis — `<ITERATION_ID>-analysis.md`
   - Purpose: AIB-produced analysis of impact, assumptions, affected modules/areas, risks, dependencies.
   - Recommended headings (H2): `Summary`, `Affected areas`, `Assumptions`, `Risks`, `Dependencies`.
2) Questionnaire — `<ITERATION_ID>-questionnaire.md`
   - Purpose: Clarifying questions for the user.
   - Form: Numbered questions with rationale and answer options formatted as Markdown checklists:
     - Options labeled `A`, `B`, `C`, `D`, plus `Other (free text)`.
     - Indicate recommended option with `(recommended)`.
3) Plan — `<ITERATION_ID>-plan.md`
   - Purpose: Step-by-step execution plan.
   - Recommended headings (H2): `Overview`, `Tasks`, `Summary`.
   - For each task include: `Task Name`, `Task Description`, `Inputs`, `Outputs`, `Done criteria`.

Determinism & Safety (Normative)
- Tools MUST be idempotent given the same inputs.
- On validation failure, tools MUST emit a human-readable error and MUST NOT write partial files.
- Tools MAY replace entire target files, but behavior MUST be consistent for the same configuration.

Creation & Closure Protocol (Normative)
- Creation (`create-iteration`):
  - Preconditions: Request resolved and `Active`.
  - Actions:
    - Determine next `ITERATION_ID` by scanning existing rows; choose highest + 1, left-padded to two digits.
    - Append a new row with:
      - `iteration_id=<new id>`
      - `state=Active`
      - `created_at=<now>`
      - `closed_at=` (empty)
      - `summary=<short intent>`
    - If another iteration is `Active`, set its `state=Completed` and `closed_at=<now>` before adding the new row.
- Closure (`close-iteration`):
  - Preconditions: Exactly one `Active` iteration exists.
  - Actions: Set its `state=Completed` and `closed_at=<now>`.
  - Postconditions: No `Active` iteration remains for the request.

Human Editing Guidance (Informative)
- Keep `summary` crisp and factual (what this iteration aims to achieve).
- Do not reorder rows or change `iteration_id`.
- Only change `summary` to correct clarity; never to reinterpret history.
- If you accidentally create conflicting actives, resolve by completing the older one.

Validation Rules (Normative)
A validator MUST enforce:
1) Table structure present with exact header names and order.
2) `iteration_id` format `^[0-9]{2}$`, strictly ascending with no reuse.
3) At most one `Active` row.
4) `closed_at` non-empty iff `state=Completed`.
5) Timestamp format `^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s[+-]\d{4}$`.
6) Artifact file names (if present) match `<ITERATION_ID>-analysis.md`, `<ITERATION_ID>-questionnaire.md`, `<ITERATION_ID>-plan.md`.
7) Missing artifacts are allowed; presence does not affect validity.
8) On any violation: fail with a precise message and do not write outputs.

Examples (Informative)

A) Minimal `iterations.md` immediately after request creation:
| iteration_id | state  | created_at | closed_at | summary                      |
|--------------|--------|------------------|-----------------|------------------------------|
| 01           | Active | 2026-03-08 21:05 |                 | Bootstrap iteration for setup |

B) After adding iteration 02 (auto-closing 01):
| iteration_id | state     | created_at | closed_at | summary                          |
|--------------|-----------|------------------|-----------------|----------------------------------|
| 01           | Completed | 2026-03-08 21:05 | 2026-03-08 21:22| Bootstrap iteration for setup     |
| 02           | Active    | 2026-03-08 21:22 |                 | Clarify scope and confirm plan    |

C) Valid artifact set for iteration 02:
- `02-analysis.md`
- `02-questionnaire.md`
- `02-plan.md`

Operational Notes (Informative)
- Timestamps use operator local time; UTC is acceptable if consistently applied, but MUST still follow the format and be explicitly stated in surrounding documentation if used globally.
- Scripts SHOULD avoid modifying `.aib_brain/` and operate only in `.aib_memory/`.
- `implementation.md` remains request-scoped, append-only with dated/iteration-tagged entries.

Change Management (Informative)
- When evolving this convention, treat changes as breaking if they affect:
  - Table headers order or names
  - `iteration_id` format
  - File naming patterns
- For breaking changes, provide a migration script and note in release documentation.

Glossary (Informative)
- Request: A scoped unit of work tracked under `.aib_memory/requests/`.
- Iteration: A bounded clarification/execution cycle within a request.
- Artifact: An iteration-scoped document aiding analysis, clarification, or planning.
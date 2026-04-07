Purpose
Define the authoritative format, naming, and operation rules for `.aib_memory/references.md`. This convention ensures deterministic seeding from `Product_Documentation.md`, unambiguous editing rights, and stable identifiers used by AIB tools.

Scope
- Applies to the single file: `.aib_memory/references.md`.
- Covers: file structure (table schema, column order, allowed values), identity/ordering rules, deterministic seeding from `Product_Documentation.md`, validation, and maintenance operations.
- Excludes: request-specific artifacts and any other registers.

File Location & Naming (normative)
- Path MUST be exactly `.aib_memory/references.md`.
- File name MUST be `references.md`.
- The file MUST exist after `initialize` is executed or any operation that seeds memory.
- No versioning fragments or suffixes are allowed in the file name.

File Structure (normative)
- The document is a GitHub-flavored Markdown file containing:
  1) A single top-level heading `# References` (MAY be omitted by tools if they render tables without headings).
  2) One canonical register table with exactly the following columns in the exact order:

     | ref_id | title | path | type | edit_allowed | source | notes |

- Column semantics and allowed values:

  - `ref_id`  
    - Purpose: stable, human-readable, unique row identifier.  
    - Format: `REF-0001`, `REF-0002`, … (4-digit, zero-padded).  
    - Constraints: unique, non-empty.  
    - Generation: assigned deterministically as defined in “Deterministic Identity & Ordering”.

  - `title`  
    - Purpose: human-readable label of the referenced file.  
    - For seeded documentation rows: `"<REQUIREMENT_ID> - <TITLE>"` from `Product_Documentation.md`.  
    - Non-empty UTF‑8 text; SHOULD avoid trailing spaces.

  - `path`  
    - Purpose: workspace-relative path to the referenced file; MUST NOT be absolute.  
    - For seeded documentation rows: `.aib_memory/docs/<LocationPath>/<REQUIREMENT_ID>.md` (see “Seeding Rules”).  
    - MUST be unique across the table.

  - `type`  
    - Allowed values (closed set): `product-doc` | `source-code` | `domain` | `other`.  
    - Seeded rows from `Product_Documentation.md` MUST use `product-doc`.

  - `edit_allowed`  
    - Allowed values (closed set): `Y` | `N`.  
    - Seeded rows from `Product_Documentation.md` MUST be `Y`.  
    - Human MAY later change to `N` if they want to prevent AIB from editing the target file.

  - `source`  
    - Allowed values (closed set): `default` | `user`.  
    - Seeded rows MUST be `default`.  
    - Manually added rows by a human SHOULD be `user`.

  - `notes`  
    - Free text for constraints/context.  
    - Seeded rows SHOULD contain “Seeded from Product_Documentation.md”.

Deterministic Identity & Ordering (normative)
- Canonical sort key for initial seeding is ascending lexical order of `<REQUIREMENT_ID>` (e.g., `ARCH-01`, `DATA-02`, …).
- After sorting, assign `ref_id` in ascending order starting at `REF-0001`, incrementing by 1.
- `ref_id` is immutable once published; if a row is removed, its `ref_id` MUST NOT be reused.
- The table MAY be re-sorted for readability, but `ref_id` values MUST remain attached to their original rows.

Seeding Rules from Product_Documentation (normative)
- Input extraction:
  - Requirement entries are identified by headings that follow the exact pattern:  
    `##### <REQUIREMENT_ID> — <TITLE> **[<PRIORITY>]**`  
    where `<REQUIREMENT_ID>` matches regex `^[A-Z]{3,4}-[0-9]{2}$` (e.g., `ARCH-01`, `DATA-09`, `RQT-02`), and `[<PRIORITY>]` is one of `[C]`, `[H]`, `[R]`.
  - The documentation `Location` is taken from the nearest `Location: **...**` line inside the same requirement block.
- Default mapping from requirement to documentation file:
  - One row per requirement.
  - `<LocationPath>` is derived from `Location` by:
    - splitting by `/`,
    - trimming surrounding whitespace on each segment,
    - joining with `/` without leading `./`.
  - `path` becomes:  
    `.aib_memory/docs/<LocationPath>/<REQUIREMENT_ID>.md`
  - Seeded field values:
    - `type=product-doc`
    - `edit_allowed=Y`
    - `source=default`
    - `title=<REQUIREMENT_ID> - <TITLE>`
    - `notes=Seeded from Product_Documentation.md`
- Deterministic conflict checks during seeding:
  - If the same `<REQUIREMENT_ID>` appears more than once → validation error; no row is created for the duplicates.
  - If two resolved rows produce the same `path` → validation error; both rows are skipped.

Validation Rules (normative)
- The file MUST contain exactly one register table with the required columns in the required order.
- Each row MUST satisfy:
  - `ref_id` unique; regex `^REF-\d{4}$`.
  - `title` non-empty.
  - `path` unique; workspace-relative (no leading drive letter, no URI scheme).
  - `type` ∈ {`product-doc`, `source-code`, `domain`, `other`}.
  - `edit_allowed` ∈ {`Y`, `N`}.
  - `source` ∈ {`default`, `user`}.
- Rows failing validation MUST be ignored by automation and reported as validation errors.
- On any validation failure, tools MUST NOT partially write additional output files.

Editing & Maintenance Rules (normative)
- Human edits:
  - MAY add new rows with `source=user` to reference additional assets (e.g., domain notes, code folders).  
  - MAY change `edit_allowed` from `Y` to `N` to prevent AIB from editing a specific file; SHOULD provide a short rationale in `notes`.
  - SHOULD avoid modifying seeded rows’ `title`/`path` unless the underlying documentation was relocated/renamed.
- Tool behavior:
  - Tools MUST treat `edit_allowed=N` as read-only; no writes to the referenced file.
  - Tools MAY read any referenced file regardless of `edit_allowed` (unless a separate policy denies read).
  - Tools MUST preserve column order and all existing valid rows.
  - Tools MUST maintain `ref_id` stability; never renumber existing rows.
- Deletions/relocations:
  - If a referenced file is relocated, update the `path`; do not change `ref_id`.  
  - If a referenced file is removed, keep the row and set `notes` to include “Target missing since <YYYY-MM-DD>” until cleaned up.

Operational Workflow (normative)
- Initialize:
  - `initialize` creates `.aib_memory/` and seeds `.aib_memory/references.md` from `Product_Documentation.md` using the rules herein.
- Ongoing product work:
  - When new requirements are added to `Product_Documentation.md`, re-run the seeding step (idempotent). New rows are appended with the next `ref_id`. Existing rows are matched by `<REQUIREMENT_ID>` + `path` and MUST NOT be duplicated.
  - When requirements are removed, their rows remain until manually cleaned; automation SHOULD flag them in a validation report.
- Concurrency & safety:
  - All tools writing this file MUST be idempotent with the same inputs.
  - On validation error, tools MUST emit a human-readable error and MUST NOT leave partial writes.

Rendering & Formatting Conventions (normative)
- Use a single Markdown table; avoid multiple tables for the register.
- Keep one header row and a separator row (`---`) followed by data rows.
- No footnotes, hyperlinks, or embedded HTML in table cells; plain text only.
- Paths use `/` as separator on all platforms.

Worked Examples (informative)
- Seeded documentation row:

  | ref_id  | title                                | path                                                           | type        | edit_allowed | source  | notes                               |
  |---------|--------------------------------------|----------------------------------------------------------------|-------------|--------------|---------|-------------------------------------|
  | REF-0001| ARCH-01 - High-level architecture    | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md         | product-doc | Y            | default | Seeded from Product_Documentation.md|

- User-added domain note row:

  | ref_id  | title                          | path                                       | type   | edit_allowed | source | notes                          |
  |---------|--------------------------------|--------------------------------------------|--------|--------------|--------|--------------------------------|
  | REF-0123| Sales domain glossary (draft)  | .aib_memory/docs/02 Domain/Glossary/draft.md| domain | Y            | user   | Allow AIB to normalize terms.  |

Change Control (normative)
- Any structural changes to schema/allowed values MUST be performed by updating this convention file first.
- After changing this convention, re-run initialization or dedicated migration tooling to reconcile `.aib_memory/references.md`.

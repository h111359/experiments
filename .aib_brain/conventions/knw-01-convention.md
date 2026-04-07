## Purpose
Define a precise, lightweight, and machine-verifiable convention for the **Domain Glossary** so AI can read it deterministically and humans can verify/edit it quickly. The glossary captures canonical business terms with exact definitions, examples, ownership, and synonyms to ensure consistent communication across the product and documentation set.

## Scope
This convention applies to the **KNW-01 — Domain glossary** document. It specifies the file naming, section layout, entry schema, allowed value sets, editing and validation rules, and operational behaviors for creation and maintenance.

## File Naming
- **File name:** `KNW-01.md`
- **One file only** for the complete glossary (no per-term files).
- **Character set:** UTF-8, Unix line endings (`\n`).

## Document Structure (Top-Level Sections, Order Is Normative)
1. **Introduction**
2. **How to Use This Glossary**
3. **Term Entries** *(normative register)*
4. **Conventions & Style Rules**
5. **Validation Rules**
6. **Operations (Edit, Review, Publish)**
7. **Change Log**

### 1) Introduction
A short paragraph (≤ 5 sentences) explaining the glossary’s purpose and how it reduces ambiguity. No lists or terms here.

### 2) How to Use This Glossary
Bulleted guidance for readers and editors (≤ 10 bullets), including search tips, linking rules, and how to request new terms.

### 3) Term Entries (Normative Register)
All glossary content lives here as a **single Markdown table** with the following columns in this exact order:

| term_id | term | definition | examples | owner | synonyms | tags | status | version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

**Column semantics (normative):**
- **term_id**: Stable ID, format `TERM-0001`, `TERM-0002`, … (ascending, zero-padded to 4 digits).
- **term**: Canonical business term (Title Case, ASCII preferred; Unicode allowed when required).
- **definition**: Single-paragraph precise description (≤ 600 chars). Must be product-specific when relevant.
- **examples**: Comma-separated short examples or “N/A” if none (≤ 200 chars).
- **owner**: Business role or specific team accountable for correctness (e.g., “RGM Team”, “Finance”).
- **synonyms**: Comma-separated list of recognized aliases; “—” if none.
- **tags**: Comma-separated keywords (e.g., “pricing, RGM, KPI”); optional “—”.
- **status**: One of `Proposed | Approved | Deprecated`.
- **version**: Semantic-like integer `1`, `2`, … incremented on definition change (not on metadata-only edits).

**Normative constraints:**
- Exactly **one** header row and **no extra formatting** inside table cells (no lists, no links, no code fences).
- **Uniqueness:** `term_id` and `term` must be unique case-insensitively.
- **Stability:** `term_id` never changes; `term` may change only via an Approved change request.
- **Minimal row example (illustrative only):**  
  | TERM-0001 | Net Revenue | Revenue after discounts and returns within recognized period. | “$1.2M Q1”, “€500k March” | Finance | Net Sales, Net Rev | finance, revenue | Approved | 1 |

### 4) Conventions & Style Rules
- **Writing style:** Clear, unambiguous, business-first language; avoid jargon unless defined.
- **Definition do’s:** Start with the essence; include boundary conditions (inclusions/exclusions) when material.
- **Definition don’ts:** No forward references to undefined terms; no external links; no placeholders like “TBD”.
- **Term naming:** Singular noun phrase (e.g., “Invoice”, not “Invoices”). Use standard capitalization.
- **Synonyms:** Include only widely used aliases; avoid spelling variants unless materially different.
- **Examples:** Prefer 1–3 short, concrete illustrations or use “N/A”.
- **Tags:** Use to group by domain (e.g., “commercial, finance, supply-chain”).
- **Status transitions:** `Proposed → Approved → (optional) Deprecated`. Skipping states is not allowed.

### 5) Validation Rules
Automations and reviewers MUST enforce:

**Table-level checks**
- File contains **exactly one** glossary table under “Term Entries”.
- Columns match the specified header names and order exactly.
- No duplicate `term_id` or `term` (case-insensitive).
- All rows sorted ascending by `term_id`.

**Field-level checks**
- `term_id`: Matches `^TERM-\d{4}$`; sequence strictly increasing without gaps is recommended but not mandatory.
- `term`: `^[A-Za-z0-9 \-/&()]+$` (Unicode letters allowed; avoid trailing spaces; Title Case).
- `definition`: 1–600 characters; must not contain Markdown links/backticks.
- `examples`: ≤ 200 chars; comma-separated or “N/A”.
- `owner`: Non-empty; short role/team label.
- `synonyms`: Comma-separated list or “—”.
- `tags`: Comma-separated, lowercase tokens (spaces allowed after commas) or “—”.
- `status`: One of `Proposed|Approved|Deprecated`.
- `version`: Integer ≥ 1.

**Change control**
- If `definition` changes, increment `version`.
- If `term` changes, require a recorded rationale in the Change Log and reviewer approval.

### 6) Operations (Edit, Review, Publish)
- **Edit cycle:**  
  1) Propose new/updated rows in a working branch.  
  2) Run validation script (or AI check) locally.  
  3) Submit for review to the designated owner.  
  4) On approval, merge and set `status=Approved`.

- **AI behavior (non-destructive):**  
  - AI MAY add `Proposed` rows; AI MUST NOT modify `Approved` rows without an explicit instruction.  
  - AI MUST preserve table structure, ordering, and column headers.

- **Conflict resolution:**  
  - When conflicting definitions exist, the **higher `version` on an Approved row** wins.  
  - Deprecated rows stay for historical context until explicitly removed.

- **Publishing:**  
  - Treat the merged file as the single source of truth for term definitions across all product docs.

### 7) Change Log
Maintain an append-only Markdown table capturing material edits to `term`, `definition`, `status`, or `owner`.

| date (YYYY-MM-DD) | actor | term_id | field | old_value → new_value | rationale |
| --- | --- | --- | --- | --- | --- |

**Rules:**
- One row per logical change.
- `old_value` and `new_value` should be short (≤ 120 chars). Provide extended rationale if needed outside the table.

## Quality Gates (Pass/Fail)
A pull request or AI-generated update **MUST FAIL** if any of the following are true:
- Table missing or malformed; headers out of order.
- Invalid `status` value or empty required fields.
- Duplicated `term_id` or `term`.
- `definition` exceeds 600 chars or contains links/backticks.
- Unapproved changes to rows with `status=Approved`.

## Minimal Editor Guidance
- Add new terms at the end, then re-sort by `term_id`.
- Prefer improving an existing definition over adding near-duplicates; if merging, deprecate the weaker entry.
- Keep `examples` practical and concise; do not restate the definition.

## Ready-to-Use Boilerplate (Copy/Paste Starters)

### Introduction (template)
This glossary defines canonical business terms for our product. Each entry is precise, concise, and reviewed by accountable owners to avoid ambiguity. Use this as the single source of truth for naming, calculation boundaries, and domain concepts across requirements, analytics, and documentation.

### How to Use This Glossary (template)
- Search for a term before proposing a new one.
- When in doubt, prefer the **Approved** entry.
- If a term is missing, add a `Proposed` row and request review.
- Avoid synonyms proliferation—record aliases in `synonyms`.
- Reference terms exactly as listed under `term`.

### Term Entries (empty table scaffold)
| term_id | term | definition | examples | owner | synonyms | tags | status | version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-0001 |  |  |  |  |  |  | Proposed | 1 |

## Appendix: Deterministic Parsing Hints (For Tools)
- Parse exactly the first Markdown table under “Term Entries”.
- Treat header names as exact match tokens.
- Permit Unicode letters in `term` and `definition`; forbid Markdown links and inline code.
- Normalize spaces around commas in `examples`, `synonyms`, and `tags`.

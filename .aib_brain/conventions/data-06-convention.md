Purpose
Define a deterministic, AI-friendly convention for the **Metrics catalog** document that captures business metrics with unambiguous definitions, traceability to data, and operationalization signals required by AIB. This convention ensures consistent file naming, structure, field semantics, and validation logic across products.

Scope
This convention governs the single documentation file for **DATA-06 — Metrics catalog** under the product documentation tree. It applies to creation, editing, validation, and lifecycle management of the metrics catalog content.

Deterministic File Name (normative)
- File name: `DATA-06.md`
- The file MUST exist as a single file (no sharding into multiple files or folders).

Document Structure (normative)
The document MUST use the following top-level headings in the exact order shown:
1. Overview
2. Catalog
3. Change Log

Section 1 — Overview (normative)
- Purpose: Short paragraph explaining the intent and scope of the catalog for this product.
- Coverage: A bullet list describing which business domains/areas are represented.
- Conventions: Brief notes on formatting rules used in this file (IDs, formulas, units, time zones, rounding).

Section 2 — Catalog (normative)
- The Catalog section MUST contain a **single Markdown table** with the exact columns and semantics defined below.
- The table MUST be the single source of truth for all metrics. No free-form metric definitions outside the table.
- Column order is normative and MUST NOT be changed.

Catalog Table Schema (normative)
Columns (exact names, left-to-right):

1) `metric_id`
   - Purpose: Stable, unique identifier.
   - Format: `MET-0001`, `MET-0002`, … (4 digits, zero-padded).
   - Uniqueness: MUST be unique within this file.

2) `name`
   - Purpose: Human-readable metric name.
   - Constraints: Concise (≤ 8 words), descriptive, no acronyms without expansion.

3) `business_definition_ref`
   - Purpose: Reference ID or canonical link text to enterprise business definition (if available).
   - Format: Plain text reference (e.g., glossary term ID or catalog key). Do not use URLs in this field.

4) `business_owner`
   - Purpose: Accountable role/persona responsible for metric accuracy for this product.
   - Format: `Role - Team` or `Name - Role` (free text). Avoid emails.

5) `calculation_formula`
   - Purpose: Precise product-specific calculation.
   - Syntax Rules:
     - Express as pseudo-DSL using: uppercase function names, column/entity names in backticks, operators `+ - * /`, and explicit aggregation (`SUM`, `AVG`, `COUNT_DISTINCT`, etc.).
     - Time windowing must be explicit (e.g., `FILTER(date BETWEEN {{from}} AND {{to}})`).
     - Dimensional grain MUST be stated at the end in square brackets, e.g., `[grain: day, dims: geography, channel]`.
     - Example pattern: `SUM(\`net_sales\`) / NULLIF(SUM(\`volume_l\`), 0) [grain: month, dims: market]`.

6) `aggregation_rules`
   - Purpose: How the metric aggregates across time/segments (if not fully captured in `calculation_formula`).
   - Examples: `sum_over_time_then_avg_over_entities`, `weighted_avg(volume_l)`.

7) `underlying_sources`
   - Purpose: Comma-separated list of raw/curated data assets used.
   - Format: Workspace-relative logical names (e.g., `src_sap_sales_orders`, `dwh.sales_fact`).

8) `reporting_cadence`
   - Purpose: Expected refresh/reporting frequency.
   - Allowed values: `daily`, `weekly`, `monthly`, `quarterly`, `ad-hoc`.
   - Optional cron-like note permitted in parentheses, e.g., `daily (06:00+02:00)`.

9) `targets`
   - Purpose: Target/threshold values if applicable.
   - Format: Free text with units and condition, e.g., `≥ 97%`, `1–3 days`, `≤ 0.5%`.

10) `business_objectives_links`
    - Purpose: Explicit links (by textual identifier, not URL) to OKRs/strategic goals.
    - Format: Comma-separated identifiers, e.g., `OBJ-2026-01, KRO-3.2`.

11) `units`
    - Purpose: Unit of measure.
    - Examples: `%`, `USD`, `EUR`, `count`, `L`, `cases`.

12) `domain_validations`
    - Purpose: Domain-specific constraints or sanity checks.
    - Examples: `value ∈ [0%, 100%]`, `non-negative`, `monotonic_non_decreasing_monthly`.

13) `data_quality_rules_ref`
    - Purpose: Reference to DQ rules (e.g., `DQ-SET-07`) defined under DATA-07.
    - Format: Comma-separated textual IDs; no hyperlinks.

14) `lineage_ref`
    - Purpose: Reference to lineage artifacts (DATA-03) describing how the metric is produced.
    - Format: Free text IDs of lineage nodes/diagrams.

15) `owner_notes`
    - Purpose: Brief rationale, caveats, or adoption notes (≤ 200 chars).

Validation Rules (normative)
- Table MUST include all columns above, in exact order.
- `metric_id` MUST be unique; MUST follow `MET-\d{4}`.
- No duplicate `name` values.
- `calculation_formula` MUST:
  - Be non-empty, refer only to fields/sources enumerated in `underlying_sources`.
  - State grain/dimensions in trailing bracket `[grain: …, dims: …]`.
  - Avoid ambiguous terms like “latest” without a time window.
- `reporting_cadence` MUST be one of the allowed values.
- `units` MUST be present; `%` requires values scaled 0–100 unless explicitly stated otherwise.
- If `targets` is provided, it MUST specify comparator(s) or range and unit(s).
- If `data_quality_rules_ref` is provided, each referenced ID MUST exist in the DATA-07 documentation set.
- If `business_definition_ref` is omitted, `owner_notes` MUST state why the enterprise definition is not available/applicable.
- Rows violating validation MUST be reported by automation and ignored until corrected.

Expression & Notation Guidelines (normative)
- Use explicit null/zero guards: `NULLIF`, `COALESCE`.
- Disallow implicit casting; specify unit conversions inside the formula (e.g., `SUM(\`volume_ml\`)/1000` for liters).
- Time zone offsets MUST be explicit in cadence notes if time-of-day matters.
- Rounding rules (if needed) MUST be appended to the formula using `{round: HALF_UP, scale: 2}`.

Change Management (normative)
- The Catalog is append-and-amend: new metrics add new rows; modifications edit existing rows.
- Breaking changes (altering `metric_id` meaning, unit change, grain change) REQUIRE an entry in **Section 3 — Change Log** and MUST increment the `rev` note inline in `owner_notes` (e.g., `rev: 2026-03-09`).
- Deprecation:
  - Add `owner_notes: deprecated as of YYYY-MM-DD; replacement: MET-00XX`.
  - Keep deprecated metrics until all downstream consumers migrate.

Section 3 — Change Log (normative)
- Reverse-chronological list of dated entries describing structural schema updates or breaking metric changes.
- Format:
  - `YYYY-MM-DD — <short description> — <impacted metric_ids or "schema">`

Authoring Workflow (normative)
- Create or open `.aib_memory/docs/04 Technology/Analytics/DATA-06.md`.
- Update **Overview** if scope/conventions change.
- Edit the **Catalog** table only through structured additions/edits that pass validation.
- Record any breaking change in **Change Log**.

AI Editing Rules (normative)
- AIB MAY add or edit rows in the Catalog if:
  - All validation rules pass.
  - Added/edited rows contain fully specified formulas and units.
- AIB MUST NOT:
  - Rename or reorder table columns.
  - Remove rows without explicit “deprecated” notation.
  - Insert external hyperlinks anywhere in the file.

Worked Example (informative)
Below is a minimal example row illustrating style and notation (field values are illustrative):

| metric_id | name                    | business_definition_ref | business_owner     | calculation_formula                                                                                 | aggregation_rules                 | underlying_sources                          | reporting_cadence   | targets | business_objectives_links | units | domain_validations          | data_quality_rules_ref | lineage_ref     | owner_notes                    |
|-----------|--------------------------|--------------------------|--------------------|------------------------------------------------------------------------------------------------------|-----------------------------------|----------------------------------------------|---------------------|---------|---------------------------|-------|------------------------------|------------------------|-----------------|-------------------------------|
| MET-0001  | On-shelf Availability % | GLOS-OSA                 | Sales Ops - EMEA   | `100 * (1 - SUM(\`oos_sku_store_days\`) / NULLIF(SUM(\`sku_store_days\`), 0)) [grain: day, dims: market, customer]` {round: HALF_UP, scale: 1} | sum_over_time_then_avg_over_entities | src_retail_oos_daily, dwh.dim_store, dwh.dim_sku | daily (06:00+02:00) | ≥ 97%  | OBJ-2026-01, KRO-3.2      | %     | value ∈ [0%, 100%]          | DQ-SET-07              | LIN-OSA-PIPE-01 | rev: 2026-03-09; product-specific formula |

Quality Gates for Review (informative)
- Does every row have an explicit grain and dimension list?
- Do formulas reference only sources listed in `underlying_sources`?
- Are units consistent with targets and rounding?
- Are domain validations actionable for DQ?
- Are business objectives references populated for key metrics?

End of document.
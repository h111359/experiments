Purpose
Define the canonical format, naming, structure, and operating rules for the “DATA-01 — Source data catalog and data ingestion strategy” document. The goal is to enable AI agents to read, validate, and generate consistent content, and enable humans to quickly verify completeness and correctness.

Scope
This convention applies to a single product documentation file describing all source data systems used by the product and the ingestion strategy for each source. It governs structure, headings, tables, allowed values, and edit rules.

File Naming
- File name: DATA-01.md

Document Structure (normative)
The DATA-01 document MUST follow this exact section order and include all normative sections:

1. Title (H1): DATA-01 — Source data catalog and data ingestion strategy
2. Overview (H2)
3. Catalog (H2)
   3.1 Source Systems Register (H3) — table (normative)
   3.2 Schema Details (H3) — repeated sub-sections per source (normative)
4. Ingestion Strategy (H2)
   4.1 Ingestion Overview (H3)
   4.2 Ingestion Methods & Schedules (H3) — table (normative)
   4.3 Error Handling & Reprocessing (H3)
5. Governance & Classification (H2)
6. Validation & Acceptance Checklist (H2)
7. Change Log (H2)

Section Content Requirements (normative)
1) Title (H1)
- Exact text: “DATA-01 — Source data catalog and data ingestion strategy”.

2) Overview (H2)
- Brief purpose of the document and its intended audience.
- Short summary of how many source systems are in scope.

3) Catalog (H2)
3.1) Source Systems Register (H3)
- A single table with the following columns (exact names, order, and types):
  - source_id (string; unique; pattern: SRC-0001, SRC-0002, …)
  - source_system (string; human-readable name)
  - business_owner (string; “Name, Team/Org”)
  - technical_owner (string; “Name, Team/Org”)
  - data_domain (enum; one of: Sales, Marketing, Finance, SupplyChain, HR, IT, Other)
  - refresh_frequency (enum; one of: real-time, hourly, 4-hourly, daily, weekly, monthly, ad-hoc)
  - data_classification (enum; one of: Public, Internal, Confidential, Restricted)
  - retention_policy (string; free text; e.g., “13 months in bronze; 25 months in silver”)
  - primary_keys (string; comma-separated field names)
  - schema_ref (string; anchor to the schema section id, e.g., #schema-SRC-0001)

- Constraints:
  - source_id MUST be unique.
  - schema_ref MUST point to an existing Schema Details sub-section id.

3.2) Schema Details (H3)
- One sub-section per source system, in ascending order of source_id.
- Heading format: “Schema — SRC-000X (source_system)”
- MUST include the following sub-subsections in order:
  a) Description — brief purpose and scope of the source.
  b) Tables — a table with columns:
     - table_name (string)
     - description (string)
     - grain (string; e.g., “1 row per invoice line”)
     - expected_rowcount_range (string; e.g., “10k–50k/day”)
     - pii_present (enum; Y/N)
     - incremental_field (string; nullable; e.g., “updated_at”)
  c) Fields — one table per listed table_name (repeat). Columns:
     - field_name (string)
     - data_type (string; e.g., string/int64/decimal(18,2)/date/timestamp/boolean/json)
     - nullable (enum; Y/N)
     - primary_key (enum; Y/N)
     - description (string)
     - allowed_values (string; optional; enumeration or pattern)
     - lineage_note (string; optional; free text)
  d) Known Issues & Caveats — bullet list.
  e) Sample Records — optional fenced code block (CSV or JSON), max 10 rows/objects.

4) Ingestion Strategy (H2)
4.1) Ingestion Overview (H3)
- Narrative summary of the overall ingestion approach (batch/streaming/CDC), zones (bronze/silver/gold), and orchestration/tooling.

4.2) Ingestion Methods & Schedules (H3)
- A single table with columns:
  - source_id (string; references Source Systems Register)
  - method (enum; one of: batch, streaming, cdc, file-drop, api-pull, db-replication, other)
  - frequency (enum; real-time, hourly, 4-hourly, daily, weekly, monthly, ad-hoc)
  - latency_target (string; e.g., “< 30 min”, “< 24 h”)
  - format (enum; parquet, csv, json, avro, orc, xml, other)
  - transport (enum; s3, adls, gcs, ftp/sftp, http(s), jdbc/odbc, kafka, kinesis, eventhub, other)
  - error_handling (string; short description; e.g., “retry x3 with backoff; quarantine path …”)
  - reprocessing (string; short description; e.g., “date-partition reruns via parameter”)

- Constraints:
  - Every source_id in this table MUST exist in Source Systems Register.
  - frequency MUST match refresh_frequency for that source_id unless a rationale is provided in a footnote in the same row (keep within the cell text).

4.3) Error Handling & Reprocessing (H3)
- Narrative of common errors, retry strategy, quarantine location, reconciliation controls, and audit evidence.

5) Governance & Classification (H2)
- Classification mapping rules (Public/Internal/Confidential/Restricted).
- Access rules by classification (who can access; masking/anonymization rules).
- Retention & deletion alignment with product-wide policy.
- Compliance references (e.g., GDPR/CCPA), if applicable.

6) Validation & Acceptance Checklist (H2) (normative)
- A markdown checklist the reviewer MUST use. Items:
  - [ ] Source Systems Register table exists and has no empty required cells.
  - [ ] All source_id values are unique and follow pattern SRC-\\d{4}.
  - [ ] Each source has a matching Schema Details section with a valid anchor.
  - [ ] Each table has Fields tables listing PKs and nullability.
  - [ ] Ingestion Methods & Schedules table exists and references valid source_id values.
  - [ ] frequency values in Ingestion Methods & Schedules align with refresh_frequency or include a documented rationale.
  - [ ] Data classification is assigned for every source and matches allowed values.
  - [ ] Retention policy is stated for every source.
  - [ ] Error handling and reprocessing are described for each source or globally.
  - [ ] No PII fields lack classification and handling notes.
  - [ ] All tables/fields have clear descriptions.
  - [ ] Document passes lint rules in this convention.

7) Change Log (H2)
- Reverse-chronological list of dated changes. Format:
  - YYYY-MM-DD — Summary of change — Author initials.

Formatting Rules (normative)
- Language: English.
- Headings: Use exact casing and order specified above.
- Tables: GitHub-flavored Markdown tables; column names EXACT as specified.
- Lists: Use hyphens “- ” for bullets; checklists use “[ ]”.
- Code blocks: Use fenced triple backticks for sample records only; limit to 10 rows/objects.
- IDs and Anchors:
  - source_id: “SRC-0001”, “SRC-0002”, … (strictly 4 digits).
  - Schema Details anchor id format: “schema-SRC-000X” (lowercase id).
- Dates: ISO 8601 (YYYY-MM-DD).
- Numbers: Use SI digits; use thousands separators only in prose if needed, not in numeric fields of tables.

Allowed Values (normative)
- data_domain: Sales | Marketing | Finance | SupplyChain | HR | IT | Other
- refresh_frequency: real-time | hourly | 4-hourly | daily | weekly | monthly | ad-hoc
- data_classification: Public | Internal | Confidential | Restricted
- pii_present: Y | N
- method: batch | streaming | cdc | file-drop | api-pull | db-replication | other
- format: parquet | csv | json | avro | orc | xml | other
- transport: s3 | adls | gcs | ftp/sftp | http(s) | jdbc/odbc | kafka | kinesis | eventhub | other
- boolean fields: Y | N (uppercase)

Validation Rules (normative, machine-checkable)
- Title MUST exactly match required text.
- Required sections MUST exist and appear in the defined order.
- All required tables MUST exist with exact column names and order.
- source_id MUST be unique and match ^SRC-\\d{4}$.
- schema_ref MUST match a present anchor (#schema-SRC-\\d{4}).
- For each row in Source Systems Register:
  - data_domain MUST be in Allowed Values.
  - refresh_frequency MUST be in Allowed Values.
  - data_classification MUST be in Allowed Values.
  - primary_keys MUST be non-empty (comma-separated) unless rationale provided (“none — rationale: …”).
- For each Tables row:
  - grain MUST be present (non-empty).
  - expected_rowcount_range MUST match pattern “<min>–<max>/<period>” or “unknown”.
  - pii_present MUST be Y or N.
- For each Fields row:
  - nullable MUST be Y or N.
  - primary_key MUST be Y or N.
  - data_type MUST be one of the documented types or db-native type; if custom, include parentheses with definition.
- Ingestion Methods & Schedules:
  - source_id MUST exist in Source Systems Register.
  - frequency MUST equal the Register’s refresh_frequency or include an inline rationale within the cell.

Editing Rules (normative)
- Append-only Change Log.
- When adding a new source:
  1) Add a row in Source Systems Register.
  2) Add corresponding Schema Details sub-section with anchor id “schema-SRC-000X”.
  3) Add or update a row in Ingestion Methods & Schedules.
  4) Update counts in Overview.
  5) Update Change Log.
- When deprecating a source:
  - Keep its row, add “(deprecated)” to source_system, note the retirement date and rationale in a new column “notes” (optional column allowed at the end of the table), and update Change Log.
- Do not remove historical rows; maintain lineage in prose as needed.

Minimal Example (illustrative)
Overview
- This document catalogs 2 source systems and defines their ingestion strategy.

Catalog
Source Systems Register

| source_id | source_system | business_owner     | technical_owner    | data_domain  | refresh_frequency | data_classification | retention_policy                          | primary_keys       | schema_ref        |
|---|---|---|---|---|---|---|---|---|---|
| SRC-0001 | ERP Central   | Jane Doe, Finance  | Alex Lee, DataEng  | Finance      | daily            | Confidential        | 13 months bronze; 25 months silver        | company_id, doc_id | #schema-SRC-0001  |
| SRC-0002 | WebTracker    | Mark Sun, Marketing| Priya Rao, DataEng | Marketing    | hourly           | Internal            | 6 months bronze; 12 months silver         | session_id         | #schema-SRC-0002  |

Schema — SRC-0001 (ERP Central) {#schema-SRC-0001}
a) Description
- Financial documents and master data from ERP.

b) Tables

| table_name  | description                  | grain                      | expected_rowcount_range | pii_present | incremental_field |
|---|---|---|---|---|---|
| invoices    | AP/AR invoice lines          | 1 row per invoice line     | 50k–150k/daily          | N          | updated_at        |
| vendors     | Vendor master                 | 1 row per vendor           | 20k–25k/monthly         | Y          | updated_at        |

c) Fields (invoices)

| field_name | data_type       | nullable | primary_key | description                      | allowed_values | lineage_note |
|---|---|---|---|---|---|---|
| company_id | string          | N        | Y           | Legal entity identifier          |                |             |
| doc_id     | string          | N        | Y           | Document id                      |                |             |
| line_no    | int64           | N        | N           | Line number                      |                |             |
| amount     | decimal(18,2)   | N        | N           | Line amount in document currency |                |             |
| updated_at | timestamp       | N        | N           | Last modification ts             |                |             |

Ingestion Strategy
Ingestion Methods & Schedules

| source_id | method  | frequency | latency_target | format  | transport | error_handling                                   | reprocessing                         |
|---|---|---|---|---|---|---|---|
| SRC-0001 | batch   | daily     | < 24 h         | parquet | adls      | retry x3 with exp backoff; quarantine: /quar/... | rerun by date partition (param dt)   |
| SRC-0002 | streaming | hourly | < 30 min       | json    | eventhub  | retry x5 short backoff; dead-letter: /dlq/...    | replay from offset (checkpoint)      |

Governance & Classification
- Confidential data requires masking in non-prod; PII marked Y requires tokenization at bronze.

Validation & Acceptance Checklist
- Use the checklist in the normative section above.

Lint Hints (non-normative)
- Ensure all anchors (#schema-SRC-000X) exist.
- Keep column order exact.
- Prefer precise, measurable ranges and targets.

Operational Notes (non-normative)
- For extremely wide schemas, collapse Fields tables using multiple smaller tables grouped by functional area.
- If schemas are machine-exported, keep the human-written Description and Known Issues concise and review-friendly.
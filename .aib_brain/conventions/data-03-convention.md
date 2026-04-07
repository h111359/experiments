Purpose
Define the deterministic convention for the “DATA‑03 — Data lineage” document so it is unambiguous for AI generation and easy for humans to verify and maintain. The convention specifies file path, naming, audience, required sections, table schemas, allowed values, editing workflow, validation rules, and examples.

Scope
Applies to the product documentation file that captures end‑to‑end data lineage across source systems, transformations, intermediate assets, and targets. The convention governs a single document per product (or per bounded domain if explicitly split).

Target Naming (normative)
- File name: DATA-03.md

Audience and Usage
- Primary readers: architects, data engineers, analytics developers, operations.
- Secondary readers: product managers, governance/QA, security.
- The document MUST enable independent understanding of how any target data element is produced from its sources.

Authoritativeness and Relationships
- This document is authoritative for end‑to‑end lineage description.
- It MUST reference (but not duplicate) identifiers defined in:
  - DATA‑01 Source data catalog
  - DATA‑02 Data models (logical & physical)
  - CMP‑01 Notebook/script catalog
  - CMP‑02 Algorithm specification register
- Where identifiers exist elsewhere, this document MUST link via stable IDs (names/paths) rather than restating full specs.

Document Structure (normative)
Documents MUST use the following top‑level headings in this order:

1. Document Index
   - Purpose: enumerate lineage scopes covered when multiple files exist.
   - Required table columns:
     - doc_id (e.g., DATA-03, DATA-03-Sales)
     - scope (concise description)
     - path (workspace‑relative path)
     - notes

2. Overview
   - Brief intent and coverage boundaries (systems, domains, time horizons).
   - Legend of identifiers used (e.g., SRC_*, TBL_*, JOB_*, DSET_*).

3. Systems and Assets Register
   - Register of all systems and data assets appearing in lineage graphs.
   - Required table columns:
     - asset_id (stable, human‑friendly; MUST be unique within the document)
     - asset_type (one of: source_system | table | view | file | topic | stream | job | notebook | function | model | dashboard | other)
     - platform (e.g., SAP, Snowflake, Databricks, Kafka, S3/ADLS, PowerBI, Excel)
     - location (e.g., <account>/<region>/<db>/<schema>/<name> or URI)
     - owner_role (business_owner | technical_owner)
     - pii_level (none | low | moderate | high)
     - classification (public | internal | confidential | restricted)
     - retention (e.g., 30d, 1y, policy-id)
     - notes

4. Lineage Scopes
   - Each scope describes a cohesive pipeline or subject area from inputs to outputs.
   - For each lineage scope, include subsections 4.x with REQUIRED content:
     4.x.1 Scope Summary
       - scope_id (LS-001, LS-002, …; unique within document)
       - business_purpose (1–3 sentences)
       - primary_targets (list of asset_id for produced datasets/dashboards)
       - freshness_target (e.g., hourly, daily 06:00 EET)
       - owning_team
     4.x.2 Sources
       - Table columns:
         - asset_id (must exist in Systems and Assets Register)
         - interface (batch | streaming | api | cdc | manual)
         - expected_format (parquet | csv | json | avro | delta | other)
         - schedule (cron or natural language)
         - dq_contract (brief rule ids or reference)
     4.x.3 Transformations
       - Table columns:
         - step_id (T-001, T-002… per scope)
         - step_type (join | filter | aggregate | dedupe | enrich | calculate | reshape | ml_inference | other)
         - description (precise operation intent)
         - implementation_ref (JOB_* / notebook path / function name / sql file)
         - params (key=value; multiple via semicolon)
         - input_assets (comma‑separated asset_id or step_id outputs)
         - output_assets (comma‑separated asset_id or temp names)
     4.x.4 Targets
       - Table columns:
         - asset_id (must exist in Systems and Assets Register)
         - schema_ref (DATA-02 entity/table id, if applicable)
         - partitioning (keys or none)
         - distribution/index (if applicable)
         - consumption_paths (sql endpoint, api, report)
         - rls/ols (Y/N or brief ref)
     4.x.5 Data Flow Diagram
       - Include a textual diagram (indented list) AND an embedded image reference placeholder.
       - Textual diagram syntax (normative):
         - Use “ASSET_OR_STEP_A -> ASSET_OR_STEP_B : label”
         - Example lines MUST be indented with four spaces to avoid breaking fences when embedded in other docs.
       - Image reference placeholder format:
         - “Image: ./images/<scope_id>-lineage.png”
     4.x.6 Quality and Monitoring
       - dq_rules (brief list or reference ids)
       - lineage_completeness (what % of assets/edges covered)
       - freshness_slo (target & tolerance)
       - alerting (channel, severity thresholds)

5. Cross‑Scope Dependencies
   - Table columns:
     - from_scope_id
     - to_scope_id
     - dependency_type (data | schedule | compute | security)
     - description

6. Change Log (lightweight)
   - Append‑only bullets capturing material lineage changes (date, editor, summary).
   - No version header; use ISO dates (YYYY‑MM‑DD).

Content Requirements (normative)
- Precision: Each asset and edge MUST be resolvable to a unique artifact path or identifier.
- Minimal duplication: Reuse asset_id and implementation_ref; do not restate full code or schemas.
- Consistency: Names MUST match those in DATA‑01 (sources), DATA‑02 (models), CMP‑01/CMP‑02 (compute) when available.
- Determinism: Re‑generating the document from the same inputs SHOULD converge to the same tables and edges order (lexicographic by id).

Allowed Values and Formats (normative)
- asset_type: {source_system, table, view, file, topic, stream, job, notebook, function, model, dashboard, other}
- interface: {batch, streaming, api, cdc, manual}
- expected_format: {parquet, csv, json, avro, delta, other}
- step_type: {join, filter, aggregate, dedupe, enrich, calculate, reshape, ml_inference, other}
- pii_level: {none, low, moderate, high}
- classification: {public, internal, confidential, restricted}
- schedule: cron (“m h dom mon dow”) or natural text (e.g., “daily 06:00 EET”)
- dates: ISO‑8601 (YYYY‑MM‑DD)
- times: 24h local time with zone (e.g., 06:00 EET)

Editing Workflow (normative)
- Creation: AIB MAY seed this document during initialization of documentation using known sources, models, and compute catalogs.
- Update triggers:
  - New source onboarded or existing schema materially changed.
  - New transformation step introduced or retired.
  - New target dataset/report added or ownership changed.
- Human edits:
  - May add/adjust table rows, but MUST preserve required columns and allowed value sets.
  - MUST update Systems and Assets Register before referencing asset_id in scopes.
- Diagrams:
  - Keep textual diagram up to date first; image can follow (stored under ./images/).
- Splitting/merging:
  - If this file is split by context, update “Document Index” and ensure each file repeats the same structure.

Validation Rules (normative)
- Uniqueness:
  - asset_id MUST be unique within “Systems and Assets Register”.
  - scope_id MUST be unique within the document.
  - step_id MUST be unique within its scope.
- Referential integrity:
  - Every asset_id used in Sources/Targets MUST exist in Systems and Assets Register.
  - implementation_ref MUST resolve to an entry in CMP‑01 or CMP‑02 when such catalogs exist.
- Values:
  - Columns using enumerations MUST use allowed values only.
  - Dates/times MUST follow ISO‑8601 and specified time format.
- Path rules:
  - The document MUST reside at the exact path specified in “Target Path and Naming”.
  - Image references MUST be workspace‑relative and within ./images/.
- Lint outcomes:
  - On violation, automation MUST fail generation and emit human‑readable errors without partial writes.

Quality Gates (recommended)
- Coverage target: ≥ 95% of production datasets and dashboards represented as targets in at least one scope.
- Freshness SLOs documented for all primary_targets.
- DQ linkage: ≥ 80% of scopes list dq_rules or references.

Examples (non‑normative)
- Systems and Assets Register (snippet):
  - asset_id: SRC_SAP_SALES; asset_type: source_system; platform: SAP; location: “ECC/SD”; owner_role: business_owner; pii_level: moderate; classification: restricted; retention: “7y”
  - asset_id: TBL_SALES_ORDER_HDR; asset_type: table; platform: Snowflake; location: “ACCT/REGION/DB/SCHEMA/SALES_ORDER_HDR”
  - asset_id: JOB_SALES_DAILY; asset_type: job; platform: Databricks; location: “/Jobs/Sales/DailyLoad”
- Transformations (snippet):
  - step_id: T-001; step_type: dedupe; description: “Remove duplicate header rows by (ORDER_ID, UPDATED_AT) keep latest”; implementation_ref: JOB_SALES_DAILY; params: “keep=latest”
- Textual diagram (snippet):
    SRC_SAP_SALES -> T-001 : daily extract
    T-001 -> TBL_SALES_ORDER_HDR : load curated
    TBL_SALES_ORDER_HDR -> DASH_SALES_OVERVIEW : BI

Operational Notes
- Security: For restricted assets, ensure classification and pii_level are set; omit sensitive field names unless necessary.
- Observability: If freshness SLOs are documented here, ensure alignment with OBS catalogs and alerting rules.

Change Log
- 2026-03-08: Initial convention created; establishes deterministic structure, validation, and examples.

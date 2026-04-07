Purpose
Define the canonical convention for the “DATA-02 — Data models (logical & physical)” documentation file. This convention standardizes naming, file location, document structure, edit rules, and validation so both AI and humans can create, read, and maintain the document consistently.

Applies To
- Document ID: DATA-02 — Data models (logical & physical)
- Scope: One document per product capturing both logical and physical data models.
- Audience: Data modelers, data engineers, architects, and AI tools generating or validating documentation.

File Naming (Normative)
- File name: DATA-02.md
- The file MUST be Markdown (.md) encoded in UTF-8.

Document Structure (Normative)
The document MUST contain the sections below in the listed order. Headings MUST be top-level unless otherwise specified.

1. Summary
   - Purpose: 2–5 sentences describing the data modeling scope for the product.
   - Model scope: Systems covered, domains, high-level boundaries.
   - Last major change: one line (free text).

2. Logical Model
   2.1 Modeling Approach
       - Notation used (e.g., UML class, Crow’s Foot, Chen).
       - Modeling principles and constraints (keys, cardinalities, normalization/denormalization choices).
   2.2 Entities
       A Markdown table with the following columns:
       - entity_id (stable, SCREAMING_SNAKE_CASE)
       - name (human-readable)
       - description (concise purpose)
       - primary_key (field list)
       - candidate_keys (optional)
       - business_rules (brief bullet list)
       - sensitive_data (Y/N)
   2.3 Attributes
       A Markdown table with the following columns:
       - entity_id
       - attribute_name (snake_case)
       - business_definition
       - data_type (logical; e.g., string, integer, decimal(p,s), date, timestamp, boolean)
       - nullability (NULLABLE / REQUIRED)
       - default (optional)
       - domain_constraints (enumerations, patterns, ranges)
   2.4 Relationships
       A Markdown table with the following columns:
       - relationship_id (REL_0001, REL_0002, …)
       - from_entity_id
       - to_entity_id
       - cardinality (1:1, 1:N, N:M)
       - identifying (Y/N)
       - description
   2.5 Logical ERD Description
       - Textual description of the ERD (components and key relationships).
       - Optionally an ASCII diagram or a link to a model artifact path inside the repo (no external URLs).

3. Physical Model
   3.1 Physical Design Principles
       - Target platforms/engines (e.g., PostgreSQL, Databricks, Fabric, Snowflake—state the actual).
       - Partitioning, indexing, clustering, distribution strategies.
       - Performance considerations and storage formats (e.g., Parquet) if applicable.
   3.2 Schema Inventory
       A Markdown table:
       - schema_id (SCHEMA_01, …) or database name
       - purpose
       - retention_strategy (if applicable)
       - notes
   3.3 Tables/Views
       A Markdown table with:
       - object_id (OBJ_0001, …)
       - object_type (TABLE / VIEW / MATERIALIZED_VIEW)
       - schema (or database.schema)
       - name (snake_case)
       - description
       - primary_key (column list if applicable)
       - cluster/partition (if applicable)
       - indexes (short list)
       - rls/ols (row/object level security notes, if any)
   3.4 Columns
       A Markdown table with:
       - object_id
       - column_name
       - data_type (engine-specific)
       - nullability
       - default
       - semantic_ref (entity_id.attribute_name if mapped)
       - pii_sensitivity (NONE / LOW / HIGH)
   3.5 Physical DDL
       - Provide DDL snippets per object in fenced code blocks.
       - Each snippet MUST be preceded by a comment header with object_id and purpose.

4. Data Dictionary
   - A combined, human-readable dictionary that ties logical attributes to physical columns.
   - Markdown table:
     - term (entity.attribute)
     - business_definition
     - physical_locations (list of schema.object.column)
     - calculation_rules (if derived)
     - data_owner (role/persona)
     - quality_dimension_impact (accuracy/completeness/consistency/timeliness/uniqueness/validity)

5. Lineage and Mappings (Concise)
   - Upstream sources (system, dataset, field).
   - Transformation summary (high-level).
   - Downstream consumers (datasets, reports, APIs).
   - Provide pointers to detailed lineage documents where applicable.

6. Standards & Naming
   - Entity IDs: SCREAMING_SNAKE_CASE, stable across versions.
   - Attribute names: snake_case, concise and descriptive.
   - Physical names: snake_case; prefixes/suffixes only if justified (e.g., dim_, fact_).
   - Keys: name primary/foreign keys deterministically (pk_<table>, fk_<from>__<to>).
   - Enumerations: centralize enumerations and reference them.

7. Governance & Controls
   - Security classification per entity/attribute.
   - Access patterns and constraints (read/write roles).
   - Change control approach (who approves model changes).
   - Compliance tags (e.g., GDPR data subject relevance).

8. Quality Rules (Focused)
   - List critical DQ rules tied to entities/attributes (not full DQ catalog; put details in DATA-07).
   - For each rule: rule_id, target, rule_type, threshold, severity, remediation pointer.

9. Validation Checklist (Normative)
   The document is valid when ALL are true:
   - Sections 1–9 exist in order; no sections empty (except optional notes explicitly marked).
   - Logical tables (Entities, Attributes, Relationships) are present and non-empty for the modeled scope.
   - Physical tables (Tables/Views, Columns) reflect the current implementation or planned target, not stale.
   - DDL snippets exist for all new or changed physical objects, or rationale is stated if generated elsewhere.
   - Data Dictionary maps logical to physical for all business-critical attributes.
   - PII/sensitivity flags are specified where applicable.
   - Naming follows Standards & Naming rules.
   - No external hyperlinks; repository-relative references only.
   - Document passes lint rules in “Automation & AI Rules”.

10. Examples (Illustrative)
   10.1 Entities (excerpt)
   | entity_id         | name          | description                           | primary_key | candidate_keys | business_rules                           | sensitive_data |
   |-------------------|---------------|---------------------------------------|------------|----------------|-------------------------------------------|----------------|
   | CUSTOMER          | Customer      | Party purchasing products              | customer_id| email          | One active status at a time               | Y              |
   | SALES_ORDER       | Sales Order   | Order placed by a customer            | order_id   | order_number   | Order_number unique per legal entity      | N              |

   10.2 Attributes (excerpt)
   | entity_id   | attribute_name  | business_definition                          | data_type | nullability | default | domain_constraints                 |
   |-------------|-----------------|-----------------------------------------------|----------|------------|---------|------------------------------------|
   | CUSTOMER    | customer_id     | Unique customer identifier                    | integer  | REQUIRED   |         | positive                           |
   | CUSTOMER    | email           | Customer contact email                        | string   | NULLABLE   |         | pattern: RFC5322                   |
   | SALES_ORDER | order_status    | Current status of the order                   | string   | REQUIRED   | 'NEW'   | enum: NEW, CONFIRMED, SHIPPED,...  |

   10.3 Relationships (excerpt)
   | relationship_id | from_entity_id | to_entity_id | cardinality | identifying | description                 |
   |-----------------|----------------|--------------|-------------|------------|-----------------------------|
   | REL_0001        | SALES_ORDER    | CUSTOMER     | N:1         | N          | Many orders per customer    |

   10.4 Physical DDL (excerpt)
   ```sql
   -- OBJ_0001: SALES_ORDER table
   CREATE TABLE analytics.sales_order (
     order_id            BIGINT PRIMARY KEY,
     customer_id         BIGINT NOT NULL,
     order_number        TEXT UNIQUE NOT NULL,
     order_status        TEXT NOT NULL DEFAULT 'NEW',
     created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   ```

Automation & AI Rules (Normative)
- Generation:
  - When AIB runs create or update for DATA-02, it MUST populate all required sections with the latest known state.
  - Logical-to-physical mappings MUST be derived from existing schemas/DDL when available; otherwise, clearly marked as “Planned”.
- Editing:
  - AI MAY re-order attributes/columns for readability but MUST preserve semantics.
  - AI MUST NOT remove entities/objects without an explicit “Removed” note and request/iteration reference.
  - AI MUST keep tables sorted by entity_id/object_id unless explicitly specified otherwise.
- Lint Rules (Minimum):
  - entity_id matches ^[A-Z0-9_]+$ and is unique.
  - attribute_name matches ^[a-z0-9_]+$ and is unique within entity.
  - relationship_id matches ^REL_[0-9]{4}$ and is unique.
  - object_id matches ^OBJ_[0-9]{4}$ and is unique.
  - schema and name present for every physical object.
  - primary_key columns exist in Columns table.
  - data_type present and valid for target engine(s).
  - pii_sensitivity in {NONE, LOW, HIGH}.
  - All referenced entity.attribute pairs in semantic_ref exist.

Change Log (Lightweight, Append-Only)
- YYYY-MM-DD — Initial creation aligned to DATA-02 convention.
- YYYY-MM-DD — <short description of change, request_id/iteration_id>

Notes
- Keep prose concise; prefer tables for structure.
- Place extended lineage, DQ catalogs, and analytics details in their dedicated documents; this file references them briefly.
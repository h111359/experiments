## Purpose
Define a deterministic, AI-friendly convention for documenting **Data storage strategy & patterns** for a product. The document ensures consistent structure, unambiguous field semantics, and easy human verification and maintenance.

## Scope
This convention applies to the single documentation file that captures **DATA-04 — Data storage strategy & patterns** for a product. It covers: file identity and location, required sections, mandatory/optional fields, value formats, validation rules, edit workflow, and quality checklist.

## File Identity (Normative)
- **Document ID:** DATA-04
- **Canonical File Name:** `DATA-04.md`
- **Uniqueness Rule:** Exactly one `DATA-04.md` per product. If multiple files exist, automation MUST fail validation.

## Audience & Roles
- **Primary readers:** Solution/Data Architects, Platform Engineers, Data Engineers.
- **Secondary readers:** Product Owners, Security & Compliance, FinOps.
- **Editors:** Architecture or Data Engineering representatives assigned by the product team (as per local governance).

## Authoring Principles
- Keep explanations concise and decision-oriented.
- Prefer enumerations, tables, and matrices over prose.
- State **why** a pattern/technology is chosen (decision rationale) and **when** to use it (applicability).
- For every declared storage, specify **ownership**, **cost impact**, **performance intent**, and **lifecycle**.

## Document Structure (Headings)
The document MUST follow the heading order below. All headings are required unless explicitly marked “Optional”.

1. Strategy Overview
2. Storage Technologies
3. Data Layering
4. Serialization Formats
5. Partitioning & Indexing
6. Performance & Cost Considerations
7. Reliability, Durability & Availability
8. Security & Compliance Guardrails
9. Lifecycle, Retention & Archival
10. Operational Considerations
11. Decision Log (Append-only)
12. Risks & Constraints
13. Change History (Append-only)

---

### 1. Strategy Overview
**Goal:** One concise paragraph (≤ 8 lines) describing the product’s overall approach to storage (e.g., “object storage–first, compute-pushdown via columnar formats, query federation where feasible”).  
**Must include:**
- **Primary paradigm(s):** (object, relational, columnar, key-value, search, time-series)
- **Rationale:** 3–5 bullets connecting choices to product needs (freshness, scale, analytics mode, cost)
- **Scope boundaries:** What is explicitly out of scope (e.g., ML feature store handled elsewhere)

### 2. Storage Technologies
Provide a table enumerating all approved storage technologies used by the product.

| tech_id | technology | purpose | data_domain | environment(s) | classification | tenancy | ownership | notes |
|---|---|---|---|---|---|---|---|---|
| ST-01 | e.g., Object storage (S3/ADLS/GCS) | Raw/landing zone | Source/Raw | Dev/Test/Prod | Internal/Confidential/Restricted | Single/Multi | Team/Owner | Short rationale |

**Rules:**
- `tech_id` MUST be unique (format `ST-NN`).
- `classification` MUST use the product’s standard data classification levels.
- For each technology, provide a link or path to the corresponding **Resource Catalog** entry (if maintained separately) using a relative path reference (no external URLs).

### 3. Data Layering
Describe the layered model and its intent.

| layer_id | layer_name | description | allowed_sources | allowed_sinks | schema_evolution | quality_gate |
|---|---|---|---|---|---|---|
| L-01 | Bronze (Raw) | Immutable landings, minimal transformations | Ingestion jobs | Silver | Disallow schema drop; allow additive columns | Basic validity |
| L-02 | Silver (Refined) | Cleaned & conformed | Bronze | Gold | Controlled evolution w/ contracts | Referential & conformance |
| L-03 | Gold (Curated) | Presentation-ready | Silver | Consumption | Contracted schemas | Business acceptance |

**Rules:**
- Layer names SHOULD align to commonly-used terms (Bronze/Silver/Gold) or the team’s approved equivalents; if different, define mapping.
- Each layer MUST declare its **quality gates** and **schema evolution policy**.

### 4. Serialization Formats
Enumerate approved formats and where they are used.

| format | layer(s) | compression | encoding | intended_use | notes |
|---|---|---|---|---|---|
| Parquet | Silver/Gold | Snappy/ZSTD | Columnar | Analytics & pushdown | Preferred default |
| JSON | Bronze | GZIP | Text | Raw ingestion, semi-structured | Transient—convert downstream |
| Avro | Bronze/Silver | Snappy | Row | Streaming/CDC payloads | Schema registry-backed |

**Rules:**
- Declare **default format per layer**.
- If multiple formats are allowed in a layer, define selection criteria (e.g., streaming vs batch).

### 5. Partitioning & Indexing
Define approaches by layer and access pattern.

| scope | strategy | partition_key(s) | granularity | clustering/indexing | skew_mitigation |
|---|---|---|---|---|---|
| Bronze | Ingestion-date | `ingest_date` | daily | none | Salt keys for hot sources |
| Silver | Query-driven | `business_date`, `entity_id` | daily/monthly | Z-order/cluster by | Repartition thresholds |
| Gold | Consumer SLA | `business_date` | monthly | Materialized views / indexes (DB) | Roll-ups |

**Rules:**
- Partition keys MUST be stable and low-cardinality where possible.
- For each strategy, specify **read/write amplification** trade-offs and **expected query predicates**.

### 6. Performance & Cost Considerations
Provide clear guidance:

- **File sizing targets:** e.g., Parquet 128–512 MB per file; avoid files < 64 MB.
- **Small file mitigation:** compaction jobs and scheduling window.
- **Hot/cold separation:** tiering rules (hot analytics vs archival).
- **Cost levers:** compression choices, partition pruning, caching, serverless vs provisioned.

### 7. Reliability, Durability & Availability
- **Durability tier:** e.g., standard vs reduced redundancy; replication factors or storage-class rules.
- **Availability pattern:** multi-AZ/region stance (if applicable).
- **Write guarantees:** exactly-once vs at-least-once ingestion, idempotency keys.
- **Recovery hooks:** references to DR/backup processes defined elsewhere in product docs.

### 8. Security & Compliance Guardrails
- **Access model:** role-based or attribute-based; data product personas mapped to layers.
- **Encryption:** at-rest and in-transit standards; key ownership and rotation references.
- **PII/PHI handling:** masking/tokenization policies; allowed layers for sensitive data.
- **Auditability:** minimum evidence (e.g., storage ACL snapshots, policy-as-code path).

### 9. Lifecycle, Retention & Archival
For each layer and major dataset, define:
- **Retention targets:** e.g., Raw 90 days, Refined 2 years, Curated 3 years.
- **Archival rules:** move to colder tier after N days; retrieval expectations.
- **Deletion policy:** secure delete, legal hold exceptions.
- **Governance hooks:** who approves changes to retention.

### 10. Operational Considerations
- **Quotas & limits:** expected storage growth, capacity alerts.
- **Monitoring:** freshness SLAs, data lag, failed writes, compaction status.
- **Backfills & reprocessing:** safe patterns for overwrite/merge; late-arriving data policy.
- **Change coordination:** how schema changes propagate (contracts, consumer notifications).

### 11. Decision Log (Append-only)
Capture storage-related decisions that affect architecture or consumers.

| date (YYYY-MM-DD) | decision_id | context | decision | alternatives | rationale | impact |
|---|---|---|---|---|---|---|
| 2026-03-09 | D-001 | Format for Silver layer | Adopt Parquet+ZSTD | Parquet+Snappy; Delta | Better compression; CPU trade-off acceptable | Lower cost |

**Rules:**
- New entries append at the bottom; never edit past entries—use a new row to supersede.

### 12. Risks & Constraints
List known risks (e.g., object store eventual consistency) and product constraints (e.g., region residency). Each risk MUST include **mitigation** and **owner**.

### 13. Change History (Append-only)
| date (YYYY-MM-DD) | description | editor |
|---|---|---|
| 2026-03-09 | Initial version aligned to product documentation standards | <name> |

---

## Validation Rules (Automation)
- **Structure:** All 13 sections present in order. Empty sections MUST contain the placeholder `_TBD_` and fail “ready” checks.
- **Tables:** All required columns present; `tech_id` and `layer_id` values unique.
- **File identity:** Path and name match **File Identity** rules.
- **No external links:** Only relative, workspace paths are allowed.
- **Decision Log:** At least one entry once the document moves beyond draft.
- **Serialization defaults:** At least one **default format per layer** declared.

## Editing & Workflow
- Changes that alter **Security, Retention, or Availability** MUST be referenced in the **Decision Log** and communicated to impacted consumers (per team process).
- When storage technologies are added/removed, update affected catalogs (e.g., Resource and Notebook/Script catalogs) to remain consistent.

## Ready-for-Review Checklist
- [ ] Strategy overview states primary paradigms and rationale.
- [ ] All layers defined with schema evolution and quality gates.
- [ ] Default serialization format per layer declared.
- [ ] Partitioning & indexing aligned to access patterns; trade-offs documented.
- [ ] Security guardrails and classification alignment present.
- [ ] Lifecycle/retention specified with approvers.

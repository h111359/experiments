# Summary

AI Builder (AIB) stores operational state as structured Markdown files under `.aib_memory`. This document describes the logical entities represented by those registers and a practical physical model for deterministic parsing.

Last major change: 2026-03-22 — initial population.

# Logical Model

## Modeling Approach

Lightweight register tables + deterministic file naming. Logical keys are stable ids (request_id, iteration_id, ref_id) in Markdown tables.

## Entities

| entity_id | name | description | primary_key | candidate_keys | business_rules | sensitive_data |
| --- | --- | --- | --- | --- | --- | --- |
| REQUEST | Request | Tracked work unit with lifecycle state | request_id | folder | Exactly one Active request per workspace | N |
| ITERATION | Iteration | Numbered step within a request | request_id, iteration_id | - | Exactly one Active iteration per request | N |
| REFERENCE | Reference | Register row describing a file and edit permissions | ref_id | path | path must be unique | N |
| PRODUCT_DOC | Product Doc | Convention-governed documentation file | path | title | edits only when edit_allowed=Y | N |
| VERSION_LOG | Version Log | Release bookkeeping artifact | version | log_path | one log per bumped version | N |

## Attributes

| entity_id | attribute_name | business_definition | data_type | nullability | default | domain_constraints |
| --- | --- | --- | --- | --- | --- | --- |
| REQUEST | request_id | Stable request identifier | string | REQUIRED |  | pattern: R-YYYYMMDD-HHmi |
| REQUEST | state | Lifecycle state | string | REQUIRED |  | enum: Active, Closed |
| REQUEST | folder | Request folder path | string | REQUIRED |  | workspace-relative |
| ITERATION | iteration_id | Iteration identifier | string | REQUIRED |  | 2-digit ascending |
| ITERATION | state | Iteration state | string | REQUIRED |  | enum: Active, Completed |
| REFERENCE | edit_allowed | Edit permission | string | REQUIRED | N | enum: Y, N |
| VERSION_LOG | version | Version marker name | string | REQUIRED |  | pattern: vMAJOR.MINOR.PATCH |

## Relationships

| relationship_id | from_entity_id | to_entity_id | cardinality | identifying | description |
| --- | --- | --- | --- | --- | --- |
| REL_0001 | REQUEST | ITERATION | 1:N | Y | A request has multiple iterations. |
| REL_0002 | REFERENCE | PRODUCT_DOC | 1:1 | N | A reference row points to a product-doc path. |

## Logical ERD Description

REQUEST owns ITERATIONs. REFERENCE rows describe PRODUCT_DOC files and constrain edits. VERSION_LOG is produced by CI release bookkeeping.

# Physical Model

## Physical Design Principles

- Storage is filesystem + Git.
- Tables are Markdown tables in fixed files.

## Schema Inventory

| schema_id | purpose | retention_strategy | notes |
| --- | --- | --- | --- |
| AIB_MEMORY | Registers and request artifacts | via Git history | Canonical operational state store. |
| AIB_BRAIN | Reusable framework assets | via Git history | Replaceable on upgrade. |

## Tables/Views

| object_id | object_type | schema | name | description | primary_key | cluster/partition | indexes | rls/ols |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OBJ_0001 | TABLE | AIB_MEMORY | requests_register | Request register table in `.aib_memory/requests_register.md` | request_id | none | none | N/A |
| OBJ_0002 | TABLE | AIB_MEMORY | references | References register table in `.aib_memory/references.md` | ref_id | none | none | N/A |
| OBJ_0003 | TABLE | AIB_MEMORY | iterations | Iterations register in `.aib_memory/requests/<request>/iterations.md` | request_id, iteration_id | none | none | N/A |

## Columns

| object_id | column_name | data_type | nullability | default | semantic_ref | pii_sensitivity |
| --- | --- | --- | --- | --- | --- | --- |
| OBJ_0001 | request_id | string | NOT NULL |  | REQUEST.request_id | NONE |
| OBJ_0001 | folder | string | NOT NULL |  | REQUEST.folder | NONE |
| OBJ_0001 | state | string | NOT NULL |  | REQUEST.state | NONE |
| OBJ_0002 | ref_id | string | NOT NULL |  | REFERENCE.ref_id | NONE |
| OBJ_0002 | path | string | NOT NULL |  | PRODUCT_DOC.path | NONE |
| OBJ_0002 | edit_allowed | string | NOT NULL | N | REFERENCE.edit_allowed | NONE |
| OBJ_0003 | iteration_id | string | NOT NULL |  | ITERATION.iteration_id | NONE |
| OBJ_0003 | state | string | NOT NULL |  | ITERATION.state | NONE |

## Physical DDL

```sql
-- OBJ_0001: requests_register
CREATE TABLE aib_memory.requests_register (
	request_id TEXT PRIMARY KEY,
	title TEXT NOT NULL,
	folder TEXT NOT NULL,
	state TEXT NOT NULL,
	created_at TEXT NOT NULL,
	closed_at TEXT
);

-- OBJ_0002: references
CREATE TABLE aib_memory.references (
	ref_id TEXT PRIMARY KEY,
	title TEXT NOT NULL,
	path TEXT NOT NULL UNIQUE,
	type TEXT NOT NULL,
	edit_allowed TEXT NOT NULL,
	source TEXT NOT NULL,
	notes TEXT
);
```

# Data Dictionary

| term (entity.attribute) | business_definition | physical_locations | calculation_rules | data_owner | quality_dimension_impact |
| --- | --- | --- | --- | --- | --- |
| REQUEST.request_id | Stable request identifier | AIB_MEMORY.requests_register.request_id | N/A | Product Team | uniqueness |
| REFERENCE.edit_allowed | Edit permission toggle | AIB_MEMORY.references.edit_allowed | N/A | Product Team | validity |

# Lineage and Mappings (Concise)

- Upstream: workspace filesystem and git.
- Transformations: tool scripts generate/modify Markdown registers.
- Downstream: humans and agents read registers/docs.

# Standards & Naming

- request_id: R-YYYYMMDD-HHmi.
- iteration_id: zero-padded two digits.

# Governance & Controls

- Edit scope enforced via references register.

# Quality Rules (Focused)

- DQ-0001: requests register must have at most one Active request.
- DQ-0002: references paths must be unique.

# Validation Checklist (Normative)

- Sections present in order.
- Tables present and non-empty for modeled scope.
- No external hyperlinks required.

# DATA-01 — Source data catalog and data ingestion strategy

## Overview

This document catalogs the source “data systems” used by AIB and describes how tool scripts ingest repository files into AIB memory artifacts. For this repo, the primary source system is the workspace filesystem.

In scope source systems: 1.

## Catalog

### Source Systems Register

| source_id | source_system | business_owner | technical_owner | data_domain | refresh_frequency | data_classification | retention_policy | primary_keys | schema_ref |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SRC-0001 | Workspace repository filesystem | Repository Maintainers | AIB Maintainers | IT | ad-hoc | Internal | Git history; see DATA-08 | path | #schema-SRC-0001 |

### Schema Details

<a id="schema-SRC-0001"></a>
#### Schema — SRC-0001 (Workspace repository filesystem)

a) Description

Repository filesystem is the canonical store for brain assets, memory artifacts, scripts, and logs. AIB tools read and write a bounded set of Markdown files to track work.

b) Tables

| table_name | description | grain | expected_rowcount_range | pii_present | incremental_field |
| --- | --- | --- | --- | --- | --- |
| files | Workspace file inventory relevant to AIB | 1 row per file path | unknown | N | last_modified |
| requests | Request folders under `.aib_memory/requests/` | 1 row per request folder | <= 100/year | N | created_at |

c) Fields (files)

| field_name | data_type | nullable | primary_key | description | allowed_values | lineage_note |
| --- | --- | --- | --- | --- | --- | --- |
| path | string | N | Y | Workspace-relative file path | relative path | Derived from filesystem walk. |
| size_bytes | int64 | N | N | File size in bytes | non-negative | From filesystem metadata. |
| extension | string | Y | N | File extension (lowercase) | md, py, yml, json, other | Derived from path. |
| last_modified | timestamp | N | N | Last modified timestamp | ISO 8601 | From filesystem metadata. |
| content_text | string | Y | N | Text content for readable files | N/A | Read when needed.

d) Known Issues & Caveats

- Binary files are out of scope for content extraction.
- Large repos require chunked reads.

e) Sample Records

```csv
path,size_bytes,extension,last_modified
.aib_memory/references.md,1234,md,2026-03-22T09:00:00+02:00
scripts/release_bookkeeping.py,5678,py,2026-03-22T09:00:00+02:00
```

## Ingestion Strategy

### Ingestion Overview

AIB “ingestion” is performed by tools and prompts reading workspace files and writing derived artifacts under `.aib_memory`. Mode is on-demand batch reads of Markdown and source files.

### Ingestion Methods & Schedules

| source_id | method | frequency | latency_target | format | transport | error_handling | reprocessing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SRC-0001 | batch | ad-hoc | < 5 min | other | other | fail fast; explicit error; no partial writes | rerun action after fixing invalid state |

### Error Handling & Reprocessing

- On unreadable files: record path and reason; continue for reading.
- On convention enforcement failure: stop before writing product docs.

## Governance & Classification

- Default classification for AIB artifacts: Internal.
- No secrets should be stored in repo artifacts.

## Validation & Acceptance Checklist

- [ ] Source Systems Register table exists and has no empty required cells.
- [ ] source_id values unique and match SRC-\d{4}.
- [ ] Each source has Schema Details anchor.
- [ ] Ingestion Methods & Schedules references valid source_id.
- [ ] Retention policy stated.

## Change Log

- 2026-03-22 — Populated AIB source catalog — AI Agent

## Purpose
Define a strict, AI-friendly convention for the **CMP-01 — Notebook/Script Catalog** document that inventories all executable compute artifacts (e.g., notebooks, scripts) with enough detail to locate, understand, run, and govern them consistently.

## Scope
This convention applies to the single documentation file representing CMP-01 within the product documentation set and to any AI/human that reads or edits it.

## Document Identity
- **Document ID:** CMP-01
- **Type:** product-doc (readable by all; edit gated per references registry)

## File Naming
- File name MUST be exactly: `CMP-01.md`.

## Authoring Principles
- Keep content concise, deterministic, and machine-parseable.
- Prefer tables and normalized field names.
- Use English.
- Avoid external links if a stable, repository-relative path exists.

## Structure (Top-Level Sections)
Sections MUST appear in the following order:

1. `# CMP-01 — Notebook/Script Catalog`
2. `## Instructions (Non-normative)`
3. `## Catalog`
4. `## Conventions & Examples`
5. `## Validation Notes`

No additional top-level sections are allowed.

## Section: "Instructions (Non-normative)"
Provide a brief explanation (≤ 10 lines) of how to add or update catalog rows, noting that fields and rules are normative below. Do NOT duplicate the rules—reference the "Catalog" schema.

## Section: "Catalog"
The catalog MUST be a single GitHub-flavored Markdown table with exactly the following columns and semantics:

| id | name | kind | purpose | source_assets | inputs | outputs | dependencies | env | version_control | edge_cases_and_validation | run_profile | owner | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

**Column definitions (normative):**
- **id**: Stable unique identifier for the compute artifact. Format: `CMP-ART-0001`, `CMP-ART-0002`, … (zero-padded 4 digits).
- **name**: Human-friendly artifact name (≤ 80 chars).
- **kind**: One of: `notebook` | `script` | `pipeline` | `sql` | `udf` | `macro`.
- **purpose**: Short description of what the artifact does (≤ 200 chars).
- **source_assets**: Comma-separated list of *data* assets or repositories used as sources (prefer stable, repo-relative paths or dataset IDs).
- **inputs**: Machine-readable list of parameters and inbound data references. Format: `param:<name>=<default>|<range>; data:<ref_id or path>`.
- **outputs**: Artifacts produced (tables/files/reports). Use repo-relative or dataset IDs. Include retention if relevant.
- **dependencies**: Other compute artifacts this one calls/relies on. List by `id` (preferred) or path.
- **env**: Environment requirements. Format free text ≤ 200 chars; include runtime (e.g., `Python 3.10`), packages, compute profile.
- **version_control**: Repository and path to the executable code (e.g., `repo://<org>/<repo>/<path>` or relative path).
- **edge_cases_and_validation**: Known edge cases and the validation/checks performed (brief; ≤ 300 chars).
- **run_profile**: Expected execution traits, e.g., `schedule=hourly; max_latency=5m; parallelism=4; timeout=30m`.
- **owner**: Accountable owner (role or group name). Avoid personal emails.
- **status**: One of: `draft` | `active` | `deprecated` | `retired`.

### Row Rules
- Each row describes exactly one executable compute artifact.
- `id` MUST be unique and stable across edits.
- Prefer referencing other catalog entries by `id` in `dependencies`.
- Keep all fields single-line; if detail is lengthy, summarize and point to an internal doc path within the repo.
- Empty cells are not allowed except when the field is explicitly optional (none in this table are optional).

## Acceptance Criteria (Alignment with Product Documentation)
The table MUST cover at least the following per artifact:
- Unique identifier, purpose, source data assets, inputs, outputs, dependencies, environment requirements, edge case handling & validation metrics, and a clear link to version-controlled code.
- Execution characteristics suitable for operationalization (captured in `run_profile`).
If any of the required information is unknown, enter `TBD` and open a follow-up task; do not leave cells blank.

## Section: "Conventions & Examples"
Provide 1–3 short, canonical examples. Examples MUST use realistic placeholder values and the exact table schema. For instance:

| id | name | kind | purpose | source_assets | inputs | outputs | dependencies | env | version_control | edge_cases_and_validation | run_profile | owner | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CMP-ART-0001 | Daily Sales Prep | notebook | Prepares daily sales fact table from POS raw zone | ds:raw/pos_v1 | param:date=<<YYYY-MM-DD>>|N/A; data:raw/pos_v1 | table:dw/fct_sales_daily; file:reports/sales_daily.csv | CMP-ART-0003 | Python 3.10; libs:pandas=2.2,polars=1.x | repo://org/product/compute/notebooks/sales_prep.ipynb | Handles missing store_id; validates row counts vs. yesterday ±10% | schedule=daily 03:00; max_latency=20m | DataOps | active |
| CMP-ART-0002 | Price Elasticity Model | script | Trains elasticity model from curated features | ds:silver/feat_pricing | param:train_window=90|30..180; data:silver/feat_pricing | model:ml/elasticity_v2; metrics:ml/elasticity_v2.json | CMP-ART-0004 | Python 3.10; libs:scikit-learn=1.5 | repo://org/product/compute/scripts/elasticity_train.py | Detects zero-variance features; validates R^2≥0.6 | schedule=weekly Sun 02:00; timeout=45m | DS Guild | active |

_Note:_ Use `<<YYYY-MM-DD>>` placeholders for dates where applicable; replace with actual values when running.

## Section: "Validation Notes"
Automations SHOULD validate:
- **Schema**: Table has exactly the mandated columns in the mandated order.
- **Uniqueness**: `id` column values are unique.
- **Enumerations**: `kind`, `status` values are from the allowed sets.
- **Non-emptiness**: No empty required fields; `TBD` is allowed only as a temporary marker.
- **References**: `dependencies` reference existing `id`s (if present).
- **Paths**: `version_control` and dataset/file paths are repository-relative or `repo://` URIs.

## Editing Rules
- Prefer PR-based edits to keep history.
- When deprecating an artifact, change `status` to `deprecated`; after removal from production, set to `retired` but KEEP the row for traceability.
- Do NOT delete `id`s. If an artifact is superseded, reference the successor in `dependencies` or add a note in `edge_cases_and_validation`.

## AI Generation & Update Guidance
- When creating a new row, AI SHOULD infer `dependencies` by scanning code imports/calls in the referenced path.
- AI MUST NOT invent non-existent datasets or paths; use `TBD` and emit a follow-up task when uncertain.
- AI SHOULD normalize package names and versions found in environment files (e.g., `requirements.txt`, `environment.yml`).

## Lifecycle & Governance
- This catalog is **critical** and MUST be maintained as part of release readiness.
- A release is **not** ready until all new/changed compute artifacts are represented here with `status=active`.

## Idempotency & Determinism
- Re-generating the document from the same inputs SHOULD converge to an identical table (ordering by `id` ascending).
- Tools SHOULD preserve the section order and column order exactly as specified.

## Change Log
- No separate change log section is allowed; rely on VCS history and PR descriptions.
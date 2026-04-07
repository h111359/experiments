Purpose
Define the normative convention for the “Algorithm specification register” document required by CMP‑02. The convention ensures deterministic structure, unambiguous field semantics, and frictionless editing by humans and AIs.

Applicability
This convention applies to the CMP‑02 algorithm specification register that documents all computational algorithms used by the product (analytics, transformations, scoring, optimization, etc.). It governs how the file is named, structured, validated, and updated.

## File Naming
- **File name:** `CMP-02.md`
- **One file only** for the complete glossary (no per-term files).
- **Character set:** UTF-8, Unix line endings (`\n`).

Document Format (Target: CMP-02.md)
- Markdown only; English language.
- Top-level organization: one register table + one details section per algorithm.
- Single source of truth: the register table is canonical for inventory and identity; the details sections are canonical for semantics.
- No document-level metadata or version block. Versioning is handled by VCS.
- Deterministic order: rows sorted lexicographically by alg_id; detail sections appear in the same order.

Register Table (Canonical Schema)
Provide one row per algorithm with the exact columns below and no extras:

| alg_id | title | purpose | owner_role | inputs | outputs | code_ref | status | perf_target | accuracy_metric | constraints | last_review |
|---|---|---|---|---|---|---|---|---|---|---|---|

Column definitions and rules:
- alg_id: Stable unique ID; format `ALG-0001`, `ALG-0002`, …; MUST be unique; zero-padded to 4 digits.
- title: Human-readable name (≤ 8 words).
- purpose: Short intent (≤ 200 chars).
- owner_role: Role accountable for business correctness (e.g., “Pricing Manager”, “Risk Lead”). A person name is NOT allowed.
- inputs: Comma-separated identifiers of input data/assets or upstream algorithms; keep concise.
- outputs: Concise description of produced data/artifacts.
- code_ref: Repository or path reference to executable implementation; use workspace-relative paths if local; otherwise a repo locator string (no URLs required).
- status: One of `proposed | active | deprecated`.
- perf_target: Expected performance benchmark (e.g., “p95 ≤ 2m, mem ≤ 8GB”).
- accuracy_metric: Named metric + target if applicable (e.g., “MAPE ≤ 8%”, “F1 ≥ 0.92”, “N/A”).
- constraints: Operational constraints (e.g., “runs nightly”, “GPU required”, “spark 3.5 only”).
- last_review: ISO 8601 date `YYYY-MM-DD`.

Detail Section (Per Algorithm)
For each algorithm listed in the register table, provide a second-level heading with its alg_id and title, and the following subsections in the exact order and headings:

## ALG-XXXX — <Title>
### Business Purpose
Short paragraph explaining business context and value; avoid repetition from the table.

### Inputs
- Data assets (names, schemas or pointers)
- Pre-conditions and assumptions

### Parameters
List parameters in a markdown table with default, type, allowed range, and description.

| name | type | default | allowed | description |
|---|---|---|---|---|

### Business Rules
Explicit rules or domain logic (enumerated list). Each rule is atomic and testable.

### Computational Steps
Numbered list of steps (aggregations, joins, filters, derivations). Reference prior steps where relevant.

### Formulas
Inline math or fenced blocks for mathematical definitions. Prefer unambiguous notation; define symbols before use.

### Outputs
Artifacts produced, schema(s) or shape, and where they are written.

### Performance Benchmarks
Expected execution time, resource usage, scale limits, and data-volume assumptions.

### Accuracy Metrics
Metric definitions, datasets used for evaluation, baseline and current values, acceptance thresholds.

### Operational Constraints
Scheduling, environment requirements, external dependencies, failure/retry expectations, and idempotency notes.

### Reference to Executable Code
Local path or repo locator to the implementation that corresponds to this specification.

### Test Cases (Minimum)
- Positive cases (at least two)
- Edge cases (at least two)
- Failure/guard-rail cases (at least one)
Each test case MUST include: input sketch, expected output/behavior, and acceptance check.

### Change History (Append-Only)
Dated entries for material changes to this algorithm specification. Do not duplicate VCS history; summarize intent and effect.

Validation Rules (Normative)
- The register table MUST exist as the first top-level section after the document title (if any).
- All columns listed in “Register Table (Canonical Schema)” MUST be present in order.
- Each row in the register table MUST have a corresponding details section with matching `## ALG-XXXX — <Title>`.
- All alg_id values MUST be unique and match `^ALG-[0-9]{4}$`.
- Status MUST be one of the allowed enumerations; any other value is invalid.
- last_review MUST match `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` and represent a valid calendar date.
- Parameters table, if present, MUST include the five specified columns in order.
- If accuracy is not applicable, set `accuracy_metric` to “N/A” and include a justification in the “Accuracy Metrics” subsection.
- No external links are required; relative paths or repo locators are sufficient.

Authoring & Editing Rules
- Keep table fields succinct; put depth in the details section.
- Prefer deterministic, mechanical wording; avoid ambiguous qualifiers.
- Do not remove historical detail sections; mark deprecated algorithms via `status=deprecated` and note in Change History.
- When an algorithm is superseded, add a `Superseded by ALG-XXXX` note in both details sections (old and new).
- Update `last_review` whenever any material edit is made to the algorithm’s details or register row.
- Code and spec must remain in sync. If code changes invalidate this document, the request cannot be Closed until the document is updated.

Deterministic Sorting & Anchors
- Sort register rows by `alg_id` ascending.
- Each details section heading MUST include an HTML anchor immediately above the `##` heading in the form `<a id="ALG-XXXX"></a>` to allow stable references.
- Cross-references within the document MUST use these anchors.

Minimal Example (Illustrative)
Register:

| alg_id | title | purpose | owner_role | inputs | outputs | code_ref | status | perf_target | accuracy_metric | constraints | last_review |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALG-0001 | Weekly Uplift | Estimate promo uplift | Pricing Manager | SALES_TXN, PROMO_CAL | uplift_by_sku_week | /code/compute/uplift | active | p95 ≤ 3m | MAPE ≤ 10% | runs Sun 02:00Z | 2026-03-08 |

<a id="ALG-0001"></a>
## ALG-0001 — Weekly Uplift
### Business Purpose
Estimate promotional uplift by SKU and week to guide pricing and trade spend optimization.

### Inputs
- SALES_TXN (facts), PROMO_CAL (calendar)
- Assumes complete transactions; excludes returns after T+7

### Parameters
| name | type | default | allowed | description |
|---|---|---|---|---|
| min_txn | int | 50 | ≥ 0 | Minimum transactions per SKU-week |
| decay | float | 0.7 | 0.0–1.0 | Exponential decay for recency weighting |

### Business Rules
1. Exclude SKUs with incomplete master data.
2. Treat overlapping promos as a single event with max discount.

### Computational Steps
1. Filter by min_txn.
2. Compute baseline using pre-promo weeks.
3. Estimate uplift = observed − baseline.
4. Apply decay weighting.

### Formulas
- baseline_sku_week = median(sales_sku_week over pre-promo window)
- uplift = sales − baseline

### Outputs
- Table: uplift_by_sku_week (sku_id, week, uplift_units, uplift_pct)

### Performance Benchmarks
- p95 runtime ≤ 3 minutes for 10M rows; memory ≤ 8 GB.

### Accuracy Metrics
- MAPE on backtesting windows ≤ 10%.

### Operational Constraints
- Scheduled weekly; requires Spark 3.5 cluster; idempotent by (sku_id, week).

### Reference to Executable Code
- /code/compute/uplift

### Test Cases (Minimum)
- Positive: SKU with clear promo → uplift_pct > 0
- Edge: SKU with min_txn=0 → algorithm still returns baseline
- Failure: Missing PROMO_CAL → fail with explicit message

### Change History (Append-Only)
- 2026-03-08: Initial specification.

Quality Checklist (For Reviewers)
- [ ] Register row exists and matches details section.
- [ ] Inputs/outputs explicitly named and traceable to data catalog.
- [ ] Parameters table present with defaults and allowed ranges.
- [ ] Business rules are atomic and testable.
- [ ] Computational steps are reproducible and unambiguous.
- [ ] Formulas are defined with clear symbols.
- [ ] Performance and accuracy targets are measurable.
- [ ] Operational constraints are explicit and realistic.
- [ ] Code reference resolves to the correct implementation.
- [ ] Change History includes the latest material edit.
## Purpose
Define a strict, minimal, and machine-checkable convention for the "ARCH-03 — Capacity model" document. The convention enables AI-first authoring, deterministic validation, and quick human verification while staying concise and practical.

## Applicability
- Applies to the product documentation artifact that fulfills requirement ID ARCH-03 — Capacity model (Priority [H]).
- Intended audience: solution architects, platform engineers, cost owners, and AI assistants generating or validating the document.
- Location of the resulting product document (default): .aib_memory/docs/04 Technology/Architecture/ARCH-03.md
- This convention document itself lives under: .aib_brain/conventions/arch-03-convention.md

## Outcome
When followed, the product document:
- States environment-level capacity targets and current sizing.
- Specifies CPU, memory, storage, throughput, and latency targets per environment.
- Declares scaling triggers/strategies and cost projections by key drivers.
- Is fully parseable by automation and easy to validate by humans.

## File Naming and Placement Rules (normative)
- Product document file name: ARCH-03.md
- Exactly one file per product. If multiple capacity models exist (e.g., per major sub-system), they MUST be consolidated into a single file with a subsystem column and clearly separated sections.

## Authoring Principles
- Be precise, terse, and unambiguous. Prefer tables over prose.
- Use SI units with explicit unit columns. Avoid implicit units in numbers.
- Prefer ranges and targets over vague qualifiers (e.g., “~500 rps” instead of “many requests”).
- Document assumptions explicitly and reference evidence.
- Keep non-essential narrative brief; the tables are the source of truth.

## Document Structure (top-level headings, in order)
1. Title: “ARCH-03 — Capacity model” (single H1)
2. Summary
3. Scope and Assumptions
4. Environments Matrix
5. Workload Profiles
6. Sizing & Performance Targets
7. Scaling Strategy
8. Cost Model
9. Evidence and Calibration
10. Risks and Limits
11. Change Log

The document MUST contain all sections above. Sections may be empty during inception but MUST include the correct table headers to allow tooling.

## Section Specifications and Table Schemas (normative)

### 2. Summary
- Short paragraph (max 5 sentences) explaining what the capacity model covers and the key headline targets (per environment), e.g., top throughput target and P95 latency.

### 3. Scope and Assumptions
Provide a table capturing the modeling scope and explicit assumptions that drive sizing.

Columns:
- id (A-001 style)
- category (traffic, data, infra, usage, compliance, other)
- statement
- rationale
- confidence (High | Medium | Low)
- evidence_ref (free text ID pointing to “Evidence and Calibration”)

Validation:
- id unique; confidence must be one of the allowed values.

### 4. Environments Matrix
Enumerate all product environments (Dev, Test, Staging, Prod, etc.) with their role and traffic policy.

Columns:
- env (Dev | Test | Staging | Prod | Other)
- purpose
- traffic_profile (synthetic | partial | prod_like | full_prod)
- data_profile (masked | synthetic | subset | full)
- change_frequency (daily | weekly | on_demand | rare)
- notes

Validation:
- env unique; values must be from the allowed sets where specified.

### 5. Workload Profiles
Describe distinct workloads that stress capacity (e.g., API read, batch ingestion, ML scoring, scheduled report generation).

Columns:
- workload_id (WL-001, WL-002…)
- name
- type (api | batch | stream | interactive | background | other)
- peak_window (e.g., 09:00–12:00 UTC)
- key_drivers (e.g., active_users, rps, events_per_sec)
- baseline_rate (with unit)
- peak_rate (with unit)
- burst_factor (x)
- notes

Validation:
- workload_id unique; baseline_rate and peak_rate must include units.

### 6. Sizing & Performance Targets
Capacity and performance targets per environment and workload.

Columns:
- env
- workload_id
- cpu_cores (target)
- memory_gib (target)
- storage_gib (working set or footprint; specify which in notes)
- iops_target
- net_throughput_mbps (ingress or egress; specify in notes)
- target_rps_or_eps (requests per second or events per second)
- latency_p95_ms (target)
- latency_p99_ms (target)
- availability_slo_pct
- headroom_pct (capacity buffer, e.g., 30)
- notes

Validation:
- (env, workload_id) composite key unique.
- Numeric fields MUST be non-negative numbers.
- availability_slo_pct between 90 and 100.
- headroom_pct between 0 and 200.

### 7. Scaling Strategy
How resources change with demand, including triggers and ceilings.

Columns:
- env
- resource (cpu | memory | storage | iops | workers | partitions | replicas | other)
- scale_type (vertical | horizontal | mixed)
- min_capacity (unit-specific)
- max_capacity (unit-specific)
- trigger_metric (e.g., cpu_util_pct, queue_depth, p95_latency_ms)
- scale_out_threshold
- scale_in_threshold
- cool_down_sec
- failover_policy (active_active | active_passive | none)
- notes

Validation:
- scale_in_threshold < scale_out_threshold (hysteresis).
- cool_down_sec >= 0.

### 8. Cost Model
Declarative cost projection by driver and environment (not a billing system; it’s a planning guide).

Columns:
- env
- cost_component (compute | storage | network | license | data_transfer | support | other)
- driver (e.g., avg_cores, storage_gib_month, egress_gb_month)
- unit_cost (currency per unit, incl. currency code, e.g., USD/GB-month)
- baseline_qty
- baseline_monthly_cost
- peak_qty
- peak_monthly_cost
- cost_notes

Validation:
- baseline_monthly_cost = baseline_qty * unit_cost (tooling MAY recompute).
- peak_monthly_cost = peak_qty * unit_cost.

### 9. Evidence and Calibration
Link measurements, benchmarks, or vendor guidance used for calibration.

Columns:
- evidence_id (E-001…)
- source_type (benchmark | prod_metric | load_test | vendor_doc | assumption)
- description
- link_or_location (repo path or URL if allowed in your governance)
- date
- relevance (which ids/sections it supports)
- notes

Validation:
- evidence_id unique.
- date in ISO 8601 (YYYY-MM-DD).

### 10. Risks and Limits
Capacity-related risks, constraints, and known ceilings.

Columns:
- risk_id (R-001…)
- description
- impact (H | M | L)
- likelihood (H | M | L)
- mitigation
- owner_role
- due_date (optional)

Validation:
- impact and likelihood must be H, M, or L.

### 11. Change Log
Append-only record of material updates to the capacity model.

Columns:
- date (ISO 8601, local time allowed with offset)
- author_role (or team)
- change_summary
- related_ids (e.g., A-003; WL-002; E-005)
- reviewer_role (optional)

Validation:
- date must be present and valid.

## Units and Conventions (normative)
- CPU: cores (integer or decimal).
- Memory: GiB.
- Storage: GiB or TiB (prefer GiB for working set; TiB for estates).
- Throughput: rps (requests per second) or eps (events per second) — must be explicit.
- Latency: milliseconds; specify percentile in the column name.
- Network: Mbps for throughput; GB for transfer volumes in cost.
- Time windows: 24-hour clock with timezone or UTC.

## Quality and Consistency Rules
- Every workload present in “Workload Profiles” MUST appear at least once in “Sizing & Performance Targets” for each environment that runs it.
- “Scaling Strategy” MUST reference only resources that exist in the runtime architecture and be coherent with the environment’s purpose.
- Headroom_pct SHOULD reflect business continuity expectations and historical variability; default 30 if unknown.
- “Cost Model” SHOULD include at least compute and storage components for Prod.
- “Evidence and Calibration” MUST include at least one non-assumption source before moving to production.

## Editing and Lifecycle Rules
- The document is owned collectively by Architecture; updates may be proposed by Engineering and reviewed by Architecture.
- Keep narrative brief; prioritize updating the tables.
- Do not embed personally identifiable information, secrets, or internal account numbers.
- When major architecture events occur (e.g., new region, service tier change), update Sections 6–8 and add a Change Log entry on the same day.

## Validation Checklist (for humans and automation)
- Summary exists and states key targets.
- All mandatory sections present with prescribed tables and columns.
- No empty required columns; numeric fields valid.
- Each Prod workload has non-zero targets and SLOs.
- Hysteresis in scaling rules is valid (scale_in < scale_out).
- Costs recompute to within 1% of stated totals.
- Evidence contains at least one non-assumption source for Prod numbers.
- Change Log has an entry for this version if material numbers changed.

## Minimal Worked Example (illustrative)
Note: Values below are placeholders to demonstrate format only.

### Summary
Capacity model targets Prod at 1,200 rps peak with P95 latency ≤ 180 ms; Staging mirrors 60% traffic. Headroom set to 30% to handle seasonal bursts.

### Scope and Assumptions
| id   | category | statement                                  | rationale                         | confidence | evidence_ref |
|------|----------|--------------------------------------------|-----------------------------------|------------|--------------|
| A-001| traffic  | Daily peak 09:00–12:00 UTC                  | Historical usage in similar apps  | Medium     | E-001        |
| A-002| infra    | Baseline CPU 16 cores per API replica       | Prior tuning on same stack        | Low        | E-002        |

### Environments Matrix
| env    | purpose     | traffic_profile | data_profile | change_frequency | notes              |
|--------|-------------|-----------------|--------------|------------------|--------------------|
| Dev    | Build/test  | synthetic       | synthetic    | daily            | Engineers only     |
| Staging| Pre-prod    | prod_like       | masked       | weekly           | Perf testing stage |
| Prod   | Live        | full_prod       | full         | on_demand        | External users     |

### Workload Profiles
| workload_id | name         | type | peak_window   | key_drivers     | baseline_rate | peak_rate | burst_factor | notes             |
|-------------|--------------|------|---------------|-----------------|---------------|-----------|--------------|-------------------|
| WL-001      | Public API   | api  | 09:00–12:00 U | rps, active_user| 400 rps       | 1200 rps  | 2.0          | Mixed read/write  |
| WL-002      | Batch ingest | batch| 01:00–03:00 U | eps, file_count | 5k eps        | 20k eps   | 1.5          | Nightly files     |

### Sizing & Performance Targets
| env  | workload_id | cpu_cores | memory_gib | storage_gib | iops_target | net_throughput_mbps | target_rps_or_eps | latency_p95_ms | latency_p99_ms | availability_slo_pct | headroom_pct | notes                 |
|------|-------------|-----------|------------|-------------|-------------|---------------------|-------------------|----------------|----------------|----------------------|--------------|-----------------------|
| Prod | WL-001      | 64        | 256        | 200         | 8000        | 1200                | 1200 rps          | 180            | 300            | 99.5                 | 30           | 4 replicas, 16c ea   |
| Prod | WL-002      | 32        | 128        | 1000        | 6000        | 800                 | 20k eps           | 500            | 900            | 99.0                 | 30           | Window 2 hours       |

### Scaling Strategy
| env  | resource | scale_type | min_capacity | max_capacity | trigger_metric   | scale_out_threshold | scale_in_threshold | cool_down_sec | failover_policy | notes         |
|------|----------|------------|--------------|--------------|------------------|---------------------|-------------------|---------------|-----------------|---------------|
| Prod | replicas | horizontal | 2            | 8            | cpu_util_pct     | 65                  | 35                | 300           | active_active   | API layer     |
| Prod | storage  | vertical   | 1 TiB        | 5 TiB        | volume_used_pct  | 75                  | 55                | 600           | none            | Hot data tier |

### Cost Model
| env  | cost_component | driver            | unit_cost | baseline_qty | baseline_monthly_cost | peak_qty | peak_monthly_cost | cost_notes           |
|------|----------------|-------------------|----------:|-------------:|----------------------:|---------:|------------------:|----------------------|
| Prod | compute        | avg_cores         | USD/cores-month 25 | 96           | 2400                 | 128      | 3200              | Includes API+batch   |
| Prod | storage        | storage_gib_month | USD/GB-month 0.10  | 1200         | 120                  | 2000     | 200               | Hot block storage    |

### Evidence and Calibration
| evidence_id | source_type | description                   | link_or_location                       | date       | relevance     | notes            |
|-------------|-------------|--------------------------------|----------------------------------------|------------|---------------|------------------|
| E-001       | load_test   | API load test v1.2            | repo://perf/loadtests/api_v1.2         | 2026-03-01 | WL-001, Prod  | 20-min soak      |
| E-002       | vendor_doc  | VM sizing guidance             | https://example.vendor/sizing          | 2026-02-20 | A-002         | N2d equivalent   |

### Risks and Limits
| risk_id | description                     | impact | likelihood | mitigation               | owner_role | due_date   |
|---------|----------------------------------|--------|-----------|--------------------------|------------|------------|
| R-001   | Storage burst exceeds 5 TiB cap | H      | M         | Tier to object storage   | Platform   | 2026-04-15 |

### Change Log
| date       | author_role | change_summary                         | related_ids     | reviewer_role |
|------------|-------------|----------------------------------------|-----------------|---------------|
| 2026-03-08 | Architect   | Initial capacity model skeleton added  | A-001; WL-001   | Eng Lead      |

## Automation Hints (non-normative)
- Tools can diff only the tables to detect material changes.
- Costs can be recomputed by parsing numeric columns; discrepancies >1% should flag warnings.
- SLO, headroom, and scaling triggers can be linted for coherence with “Observability” and “Operations” documents when available.

## Acceptance Criteria (for this convention)
- A file named ARCH-03.md exists in the default folder or a referenced alternate path.
- It contains all mandatory sections and schemas in the order described.
- Numeric fields and enumerations pass validation rules.
- Evidence contains at least one non-assumption source before production use.
- Change Log updated on each material update.
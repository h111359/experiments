# GDATD (Global Data & Analytics Technologies Delivery)

> Consolidated, deduplicated context for the GDATD team (Sofia, Bulgaria). Condensed from all markdown files in this folder; capped for slide/briefing use.

## 1) Executive summary
- **Who we are:** Global Data & Analytics Technologies Delivery team (GDATD), part of the Global Delivery Center (GDC) in Sofia.
- **Mission:** Deliver and run end-to-end Data & Analytics products with strong technical ownership (architecture → engineering → operations/service → continuous improvement).
- **Team size & roles:** ~24 people across D&A architects, data engineers, data analysts, web development, Scrum/PM, and team leadership.
- **Operating model:** DevOps (same team builds + runs + supports).

## 2) Mission, principles, and what we do
### Principles
- Empowerment & ownership
- Inclusion, tolerance, team-first delivery
- Continuous improvement (Kaizen)
- Agile mindset (Scrum adapted for data/analytics)

### Core responsibilities (end-to-end)
- Data acquisition and integration (from multiple ERP/source systems)
- Data quality, validation, governance enablement
- ETL/ELT orchestration, reliability patterns (batching, self-healing), logging/observability
- Data modeling (star schemas, cubes/semantic layers)
- Reporting and visualization (Power BI) + admin/consumer web interfaces
- Technical support (incidents/service requests), maintenance, audits/change support

## 3) DevOps model (Build + Run)
**Same team covers:**
- **Dev:** New features/enhancements aligned to roadmap/backlog
- **Ops:** Maintenance, procedures, deployment automation, CI/CD hygiene
- **Prod Mgmt:** Monitoring, change management, security, reliability
- **Service:** Incidents, technical requests, audit/support cases

**Why it works for us**
- Faster incident resolution through deep system knowledge
- Higher quality incentives (engineers support what they build)
- Dynamic capacity allocation between development and support
- Knowledge retention and faster onboarding through production exposure

## 4) Product portfolio (ownership and contributions)
- **NSR** (Net Sales Revenue) – technical ownership
- **UDP / SSDP** (Self‑Service Data Platform / Unified Data Platform) – ingestion & processing capabilities
- **BEACH → UDP Extract** – migration and support
- **DX** (Data Exchange) – rules engine/orchestration contributions
- **Smart OPEX** (Finance alignment) – technical ownership/support of compute space
- **Coke&GO analytics** – technical ownership
- **CuDa** (Customer Data) – technical ownership and analytics solutions
- **Surveys & apps:** Sodexo Surveys dashboards, Metro Surveys dashboards, Metro Survey app, RED Certification, RED Assessments

## 5) Key products (short descriptions)
### NSR (Net Sales Revenue) platform
- Collects **volume and revenue** data from bottlers; consolidates master data for cross-country/bottler reporting.
- Standardizes ingestion from diverse ERP systems; focuses on completeness/accuracy and maintainability.
- Modernization themes: improved concurrency, data democratization, orchestration engine evolution.

### Metro Surveys / Metro Survey application
- Supports pay-for-performance tracking for the TCCC–Metro agreement across multiple markets/bottlers.
- Captures programs/initiatives, planned vs actual revenue (EUR/local), program status, new buying customers/activated locations, and payment projections.

### RED Certification
- Web-based survey system replacing manual Excel-based surveys for collecting RED performance data.
- Central UI + database + Power BI reporting/analysis; planned go-live in 2025.

## 6) Capabilities (what we’re good at)
- **Discovery & data analysis:** profiling, semantics clarification, source evaluation
- **Solution architecture:** formats/types/constraints, component setup, security, lifecycle, logging
- **ETL/ELT development:** extraction, validation, transformation, integration, enrichment algorithms
- **Analytical modeling:** star schemas, cubes, measures, performance tuning
- **Reporting & visualization:** Power BI dashboards; admin/user experiences
- **Reliability:** batching, self-healing routines, error handling, observability improvements

## 7) Strategy (D&A ideas)
### Products
- Global data products catalogue (discoverability + ownership + access)
- AI-ready documentation (domain + technical, machine-readable)
- Knowledge internalization (decision/control based on internal know-how)

### Teams
- Single technical owner per product
- Team autonomy in way of work (within agreed guardrails)
- DevOps model as default
- Extendable with external resources while staying in control

### Governance & standards
- Data owners per domain (lineage, quality, access, certification)
- Centralized infrastructure ownership for consistent standards/processes
- Aligned product roadmaps with user/stakeholder involvement
- Shared codebase + architecture templates

### Infrastructure
- Azure-first, with an approved tools catalogue
- Sandbox environments for experimentation/ideation

## 8) Organization and team
### Leadership
- **Hristo Hristov** – GDATD Team Leader

### Sub-units
- **Global D&A Engineering** (Lead: Kiril Rusev)
  - Kalina Petrova, Nikol Bratkova, Mariyan Yanakiev, Nikolay Likyov, Neda Kirova, Elena Aleksieva,
    Jordan Kanchev, Alina Todorova, Ivailo Penchev, Milan Billingsley, Chavdar Kostadinov
- **UDP group** (Lead: Hristo Hristov)
  - Viktor Bakayov, Victor Vassilev, Petya Aroyo-Koteva
- **CCL D&A CoE** (Lead: Miroslav Dimitrov)
  - Denislava Metodieva, Ivan Todorov, Mariya Hadzhirhiisteva, Mirela Dimitrova, Monika Slavova

### Additional roles
- **Teodora Atanasova** – Project Manager
- **Radoslav Frenski** – Web Developer

## 9) Technologies and tools
- **Azure services:** Synapse, Storage Accounts, Functions, Logic Apps, Analysis Services, Databricks, Data Factory, SQL DB/SQL Server, Azure DevOps
- **BI:** Power BI
- **Languages:** Python, SQL/T‑SQL, DAX, HTML, JavaScript, C#
- **Tools:** VS Code, GitHub, DAX Studio, Tabular Editor, SSMS, Postman, draw.io, Microsoft Teams, OneNote

## 10) History and achievements (condensed)
### 2018–2019: EMEA BI team
- Team establishment; NSR local configurations/support for EMEA
- EMEA reporting; advanced analytics/data science; initial RGM implementations

### 2020–2021: Becoming global
- NSR ops/support transfer to Dublin; Europe consolidated NSR cube
- CEE Forecast/Suggested Execution; BEACH design contribution

### 2022: NSR transformation + SSDP transition
- Designed SSDP transition architecture and standards; led vendors technically
- Set up collaboration/documentation, Scrum ceremonies, backlog/user stories
- Migrated Databricks/Informatica workloads toward Synapse (Spark notebooks/pipelines)
- NSR core product & Global cube feature development, troubleshooting, optimizations
- Supported Smart OPEX rewiring toward Finance HUB

### 2023: NSR 2.0 go-live + CoE expansion
- NSR Go-Live (April) + stabilization through month/half-year/year-end closes
- Migrated error reporting for Data Governance anomaly detection
- Europe OU model unification; LATAM outlet reporting model
- Introduced Web API → ~80% service request automation; batching → ~60% concurrency
- Took full ownership of NSR Integrated Tracker; improved regional hierarchies
- Migrated BEACH data into SSDP
- Established CCL D&A CoE (hiring, Scrum team, onboarding to 5Ps CDE and Coke&GO; CuDa ownership; surveys support)

### 2024: Automation, self-healing, and new deliveries
- Self-healing for cube and pipeline failures; audit simplification/automation
- EME & Africa mergers completion support
- Web UI migration (deployment expected early 2025)
- Outbound data exchange integrations (e.g., Monster, Brown‑Foreman)
- CI/CD integration workflows for Synapse & WebApp components
- Data Steward Panel for SR automation (sync view, bulk code remap)
- NSR Japan integration kickoff (scope/feasibility, migration plan, post‑Go‑Live WoW)
- CCL D&A CoE: Coke&GO ownership; CuDa Carrefour shopper analytics (ETL + PBI); Sodexo/Metro survey dashboards
- RED Certification infra delivered in UAT; Metro app infra kicked off
- UDP/DX: new GTC ingestion (compass DBs), QA/notifications framework, Gold storage E2E events, DX backend + rule orchestration (logging/error handling/persistence)

### 2025 (in progress / priorities)
- NSR Web migration; NSR Japan migration
- RED Assessments app launch; Metro Survey customer success app launch
- RGM Africa OU PVP template refresh automation
- Expanded DX rule engine contributions

## 11) Sources (merged)
Included from:
- 2022-achievements,md; 2023-achievements.md; 2024-achievements.md; 2025-achievements.md
- DevOPS.md; gdatd-context.md; gdatd-history.md; gdatd-team.md; team-members.md; technologies.md
- strategy.md; nsr.md; metro-surveys.md; red-certification.md; one-page-summary-diagram.md

(Images/SVGs intentionally not merged into this markdown.)

# Product Documentation

### Priority scale

- **[C] Critical** — must exist
- **[H] High** — strongly recommended; document a rationale if omitted
- **[R] Recommended** — optional; include if beneficial

### Domains

| Domain | Acronym | Scope summary |
| --- | --- | --- |
| Architecture | ARCH | Defines foundational principles, high-level structural design, key decisions, and strategic direction for data & analytics products. |
| Compute | CMP | Defines and documents reproducible computational procedures and analytical logic (scripts, notebooks, formulas, parameters, performance). |
| Data | DATA | Standards for definition, structure, quality, access, lineage, classification, lifecycle and governance of data assets. |
| Development | DEV | Standards for SDLC: developer setup, code practices, CI/CD, testing, collaboration, maintainability and security. |
| Disaster Recovery | DSR | Plans and procedures to recover data/systems (RPO/RTO, backups, restoration testing). |
| Financial | FNL | Budgeting, forecasting, cost tracking, variance analysis, optimization and cost allocation. |
| Knowledge | KNW | Business/domain knowledge: glossary, data dictionary, processes, use cases, personas, key decisions. |
| Requirements | RQT | Define, prioritize and accept requirements; manage change to requirements. |
| Observability | OBS | Metrics, alerting, logging, and tracing standards. |
| Operations | OPR | Runbooks, SOPs, task inventories, health checks, SLO/SLA expectations. |
| Security | SEC | Confidentiality, integrity, availability: access control, protection, secrets, network security, compliance. |

### General documentation principles

- Documentation provides enough detail for independent understanding and maintenance of the product it describes without additional knowledge transfer.
- Documentation is in English.

### Standard requirements by domain

#### Architecture (ARCH)

<a id="arch-01"></a>
##### ARCH-01 — High-level architecture **[C]**

High-level architecture description to be included in the documentation with components, data flows, major data sources, target data stores, data processing stages, and key data consumers.

Must include:

- Component name
- Description
- Purpose
- Location
- Group or category
- Component tier (if applicable)
- Connections and dependencies on other components

Location: **04 Technology / Architecture**

<a id="arch-02"></a>
##### ARCH-02 — Topology/network description **[C]**

Topology/network description with environments, ingress/egress, trust zones to be included in the documentation.

Must include:

- Network elements
- Description
- Input connections
- Output connections
- Communication protocols

Location: **04 Technology / Architecture**

<a id="arch-03"></a>
##### ARCH-03 — Capacity model **[H]**

Document the expected resource sizing for various environments.

Must include:

- CPU, memory, storage sizes
- Estimated throughput/latency targets
- Scaling triggers/strategies
- Cost projections based on usage

Location: **04 Technology / Architecture**

<a id="arch-04"></a>
##### ARCH-04 — ADRs repository **[H]**

Architecture Decision Records repository.

Must include:

- Records list
- Architectural principles (e.g., security-by-design, scalability, resilience, cost-effectiveness, observability, extensibility, data sovereignty)

Location: **04 Technology / Architecture**

<a id="arch-06"></a>
##### ARCH-06 — Runtime interaction sequences **[R]**

Document the sequence of actions the system performs during runtime.

Must include:

- Runtime interaction sequences explained via text and sequence diagrams

Location: **04 Technology / Architecture**

<a id="arch-07"></a>
##### ARCH-07 — Resource catalog **[C]**

Resource catalog should be documented.

Must include:

- Unique resource IDs
- Location (e.g., cloud regions/data centers)
- SKU/resource type
- Purpose
- Associated application or functionality

Location: **04 Technology / Inventory**

#### Compute (CMP)

<a id="cmp-01"></a>
##### CMP-01 — Notebook/script catalog **[C]**

Notebook/script catalog.

Must include:

- Unique identifier
- Purpose
- Source data assets
- Inputs (e.g., parameters, data sources)
- Outputs (e.g., generated reports, transformed data)
- Dependencies
- Environment requirements
- Edge case handling and validation metrics
- Clear link to the version-controlled code

Location: **04 Technology / Compute**

<a id="cmp-02"></a>
##### CMP-02 — Algorithm specification register **[H]**

Algorithm specification register.

Must include:

- Unique identifier
- Business owner and purpose
- Input
- Parameters (with defaults and ranges)
- Specific business rules
- Computational steps (e.g., aggregations, joins, filters, derivations), algorithms used
- Underlying mathematical/logical formulas
- Output
- Expected performance benchmarks (e.g., execution time, resource usage)
- Accuracy metrics (if applicable)
- Operational constraints
- Reference to executable code

Location: **04 Technology / Compute**

#### Data (DATA)

<a id="data-01"></a>
##### DATA-01 — Source data catalog and data ingestion strategy **[C]**

Source data catalog should be documented.

Must include:

- Unique identifier
- Source system
- Business owner
- Technical owner
- Data schema (fields, types, nullability, primary keys)
- Refresh frequency
- Data retention policy
- Data classification level
- Ingestion methods (e.g., batch, streaming, CDC)
- Ingestion frequency/latency targets
- Data format expectations
- Error handling/reprocessing mechanisms

Location: **04 Technology / Data Sources**

<a id="data-02"></a>
##### DATA-02 — Data models (logical & physical) **[C]**

Document the logical data model (entities, attributes, relationships, business rules) for independent understanding and the physical data model (tables, columns, data types, indexes, partitioning strategies) for technical implementation.

Must include:

- Logical ERD (e.g., UML, Chen) description
- Physical DDL scripts/schema definitions
- Data dictionary

Location: **04 Technology / Data Models**

<a id="data-03"></a>
##### DATA-03 — Data lineage **[C]**

Data lineage should be documented.

Must include:

- Source systems
- Transformation steps
- Intermediate data assets
- Target data products/reports and associated metadata

Location: **04 Technology / Data Workspace**

<a id="data-04"></a>
##### DATA-04 — Data storage strategy & patterns **[H]**

Define the strategic approach to data storage within the product.

Must include:

- Chosen storage technologies (e.g., object storage, relational DB, columnar DB)
- Data layering (e.g., bronze, silver, gold zones)
- Data serialization formats (e.g., Parquet, Avro, JSON)
- Partitioning/indexing strategies

Location: **04 Technology / Data Workspace**

<a id="data-05"></a>
##### DATA-05 — Data consumption & access patterns **[H]**

Document the approved methods and patterns for consuming data from the product.

Must include:

- User exposed data sets
- Database connections
- Available data APIs (REST, GraphQL)
- Direct query access guidelines
- Subscription models
- Data export capabilities

Location: **04 Technology / Data Workspace**

<a id="data-06"></a>
##### DATA-06 — Metrics catalog **[C]**

Business metrics catalog.

Must include:

- Unique identifier
- Reference to the enterprise business definition (if available)
- Designated business owner (accountable for accuracy)
- Precise calculation formula (including aggregation rules specific to this product)
- Underlying raw data sources
- Reporting cadence
- Target values (if applicable)
- Explicit links to relevant business objectives or strategic goals

Location: **04 Technology / Analytics**

<a id="data-07"></a>
##### DATA-07 — Data quality rules, monitoring & reporting **[H]**

Data quality rules and validation checks.

Must include:

- Rule description
- Data element(s) affected
- Data quality dimension (e.g., accuracy, completeness, consistency, timeliness, uniqueness, validity)
- Severity, trigger conditions
- Remediation workflow
- Data quality checks (cardinality rules, referential integrity checks, format validations, domain value constraints, statistical checks)
- Data quality dashboard/reporting
- Alert configurations for quality breaches
- Escalation paths for data quality issues
- Monitoring mechanisms of data quality

Evidence location: **04 Technology / Data Workspace**

<a id="data-08"></a>
##### DATA-08 — Data archiving & deletion policy **[H]**

Establish clear policies and automated procedures for archiving stale data and securely deleting data that has reached the end of its retention period.

Must include:

- Criteria for archiving/deletion
- Archival destinations
- Secure deletion methods
- Audit trails
- Data subject rights considerations

Location: **04 Technology / Data Workspace**

<a id="data-09"></a>
##### DATA-09 — Dashboard inventory **[C]**

Dashboard inventory. “Dashboard” includes reports, spreadsheets, dashboards and all kinds of data visualizations.

Must include:

- Unique dashboard identifier
- Comprehensive dashboard name
- Business purpose
- Primary audience(s)
- Sources of data
- Creation/last update dates
- Development specifics
- Visualization standards
- Available filters, drill-down paths, parameters, export options, and navigation capabilities
- Link to the actual dashboard URL
- Refresh frequency
- Maximum acceptable data latency
- Performance SLAs
- Testing strategy
- Security (row level/object level)
- CI/CD approach
- Logging and monitoring
- Associated computation and orchestration elements

Location: **04 Technology / Analytics**

#### Knowledge (KNW)

<a id="knw-01"></a>
##### KNW-01 — Domain glossary **[C]**

Domain glossary.

Must include:

- Canonical terms
- Precise business definitions
- Illustrative examples
- Designated business owner
- Relevant synonyms/aliases

Location: **02 Domain / Terms and Concepts**

<a id="knw-02"></a>
##### KNW-02 — Business process catalog **[H]**

Business process catalog.

Must include:

- Business process name
- Description of business processes
- Process steps
- Inputs
- Outputs
- Roles involved
- Dependencies on other processes

Location: **02 Domain / Terms and Concepts**

<a id="knw-03"></a>
##### KNW-03 — Use cases & personas **[H]**

Document key use cases the data product supports and the personas interacting with it.

Must include:

- Use cases list
- Personas list
- Detailed persona descriptions (goals, pain points)
- Persona to use case mapping

Location: **02 Domain / Use Cases and Personas**

#### Requirements (RQT)

<a id="rqt-01"></a>
##### RQT-01 — Product charter **[C]**

Gathering high-level overview of the product.

Must include:

- Product name (preferably no longer than 5 words)
- Product definition (short description, ideally no longer than 5 paragraphs)
- Identify stakeholders affected by the product
- Mandatory roles clarified and assigned to real people with title and contact information:
	- Business owner (budget holder and decision taker)
	- Data owner (if different from the business owner)
	- Product owner
	- Technical owner
	- Technical team
	- Known subject matter experts

Location: **01 Product Management / Product Charter**

<a id="rqt-02"></a>
##### RQT-02 — Requirements document **[C]**

List of functionalities, behaviors, non-functional expectations, and quality attributes the product must satisfy.

Must include:

- Detailed user expectations or functional specifications
- Acceptance criteria for each requirement
- Explicit linkage/reference to scope, objectives, constraints, and success metrics
- Non-functional requirements (performance, scalability, security, reliability, maintainability, usability, cost-efficiency, compliance, etc.)
- Measurement criteria and target values (if applicable)
- Acceptance criteria (if not obvious)

Location: **03 Requirements**

#### Observability (OBS)

<a id="obs-01"></a>
##### OBS-01 — Logging **[C]**

Logging process of system operations and user interactions.

Must include:

- Standardized log levels (e.g., DEBUG, INFO, WARN, ERROR)
- Required log fields (e.g., timestamp, service name, request ID, user ID, event type)
- Structured logging format definition
- Log collection process (e.g., agents, sidecars, direct API calls)
- Log destination(s) and storage solution(s)
- Log retention policies for different log types (e.g., hot, warm, cold storage)
- Logging taxonomy and categories for searching and analysis

Location: **04 Technology / Observability**


#### Security (SEC)

<a id="sec-01"></a>
##### SEC-01 — Access management **[C]**

Define and enforce policies for managing user identities and controlling access to application functionalities, data assets (raw, processed, aggregated), and dashboards.

Must include:

- Role definitions and responsibility boundaries
- Permission assignment strategy
- Multi-factor authentication (MFA) requirements
- Principle of least privilege
- Access review cadence and ownership
- IAM model overview (human users vs service identities)
- Integration with enterprise identity provider (SSO, RBAC)

Location: **04 Technology / Access and Security**

<a id="sec-02"></a>
##### SEC-02 — Infrastructure data protection **[C]**

Ensure data handled by infrastructure is protected from unauthorized access.

Must include:

- Encryption at rest mechanisms
- Encryption in transit mechanisms
- Key management approach (KMS, HSM, ownership)
- Data masking/anonymization techniques
- Data loss prevention (DLP) measures
- Data residency requirements
- Adherence to privacy regulations (e.g., GDPR, CCPA)

Location: **04 Technology / Access and Security**

<a id="sec-03"></a>
##### SEC-03 — Secrets management & rotation policy **[H]**

Secrets rotation policy.

Must include:

- Chosen secrets management solution and storage mechanisms
- Types of secrets managed (API keys, credentials, certificates)
- Access control model for secrets
- Rotation and expiration policies
- Injection mechanism (runtime, pipeline, etc.)
- Requirements for audit evidence

Location: **04 Technology / Access and Security**

<a id="sec-04"></a>
##### SEC-04 — Infrastructure network security **[H]**

Document how infrastructure network access is segmented, controlled, and protected.

Must include:

- Network architecture and segmentation (VPC/VNet, subnets, trust boundaries)
- Ingress/egress controls (firewalls, security groups, NACLs)
- Public vs private exposure strategy
- Network-level encryption (e.g., TLS termination points)

Location: **04 Technology / Access and Security**

---
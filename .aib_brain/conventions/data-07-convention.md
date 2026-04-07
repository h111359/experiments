Purpose
Define a strict, machine-checkable convention for the DATA-07 document that captures data quality rules, monitoring, alerting, and reporting for a product. The convention ensures consistency, AI-friendly editing, and human-verifiable evidence.

Scope (Normative)
This convention applies to a single product’s DATA-07 document that records data quality rules, checks, monitoring, alerts, dashboards, and escalation workflows for all in-scope data assets. It governs naming, structure, allowed values, validation rules, and editing operations.

File Naming (Normative)
- File name: DATA-07.md
- Exactly one DATA-07.md file per product.

Document Audience
- Primary: Data owners, product owners, platform engineers, analytics engineers, operations and observability teams.
- Secondary: Security, compliance, and audit stakeholders.

Definitions (Authoritative)
- Data Quality Rule: A deterministic statement that evaluates one or more data elements against a dimension (accuracy, completeness, consistency, timeliness, uniqueness, validity) and returns pass/fail with severity.
- Check: A concrete implementation of a rule (e.g., SQL query, validator function, pipeline step) with execution cadence and success criteria.
- Breach: A check result that violates its success criteria.
- Severity: Business impact of a breach. Levels: Critical, High, Medium, Low.
- Monitoring Mechanism: The automated process that runs checks and emits metrics, logs, and alerts.
- Escalation Path: Ordered set of notifications and actions when a breach is detected or predicted.

Deterministic Structure (Normative)
The DATA-07.md file MUST follow the exact section order and headings below. Sections marked [*] are optional; all others are required.

1. Summary
   - One paragraph describing the overall DQ scope, the covered datasets/domains, and the monitoring surface.

2. Governance & Roles
   - Table: role, responsibilities, contact, on_call (Y/N).

3. Data Quality Dimensions
   - Fixed list table of in-scope dimensions. Columns: dimension, definition, applicability_notes.
   - Allowed dimensions (exact strings): Accuracy, Completeness, Consistency, Timeliness, Uniqueness, Validity.

4. Rule Register
   - A canonical table of rules. Columns (exact order):
     - rule_id (format: DQ-0001, DQ-0002, …; unique)
     - title (concise)
     - description
     - data_elements (comma-separated entity.attribute or table.column; wildcard allowed with approved pattern)
     - dimension (one of the allowed dimensions)
     - severity (Critical|High|Medium|Low)
     - trigger_condition (plain language; if derived, state predicate)
     - remediation_workflow_id (reference to a workflow defined in Section 6)
     - owner_role (must match a role in Section 2)
     - evidence_type (Metric|Log|RowSample|DashboardScreenshot|Other)
     - status (Active|Deprecated)
     - created_at (YYYY-MM-DD)
     - updated_at (YYYY-MM-DD or empty)

5. Checks Catalog
   - Each rule may have one or more checks. Represent as a table with one row per check:
     - check_id (format: CHK-0001, CHK-0002, …; unique)
     - rule_id (must reference an existing rule_id)
     - implementation_type (SQL|Spark|dbt|Notebook|Python|Airflow|AzureDataFactory|Other)
     - implementation_reference (repo path, job name, or notebook path; workspace-relative)
     - cadence (OnIngest|Hourly|Daily|Weekly|AdHoc)
     - success_criteria (deterministic threshold, e.g., error_rate <= 0.1%)
     - data_scope (table/view name(s), partition filters)
     - environment (Dev|Test|Staging|Prod)
     - ownership (team name or role)
     - last_execution_at (YYYY-MM-DD HH:MM, local time)
     - last_status (Pass|Fail|Warn|Skipped)
     - notes [*]

6. Remediation Workflows
   - Table describing standardized remediation playbooks referenced by rules:
     - remediation_workflow_id (format: RW-001, RW-002, …; unique)
     - name
     - steps (numbered outline, concise)
     - required_tools (e.g., ticketing, SQL client, orchestration UI)
     - rollback_or_quarantine (Yes|No with brief note)
     - verification (what confirms resolution)
     - expected_sla (e.g., 4 business hours for Critical)

7. Monitoring & Reporting
   - Describe monitoring mechanisms (pipelines, schedulers, agents) and the surfaces used for visibility.
   - Dashboards/Reports table:
     - dashboard_id (format: DQD-001, …)
     - name
     - purpose
     - metrics_covered (e.g., null_rate, freshness_lag, referential_violations)
     - url_or_path (workspace-relative; no external hyperlinks in this convention)
     - refresh_frequency
     - ownership
   - Alerting table:
     - alert_id (AL-001, …)
     - source (Check|Metric|Composite)
     - rule_or_check_ref (rule_id or check_id)
     - condition (breach predicate)
     - severity (Critical|High|Medium|Low)
     - channel (Email|Teams|Pager|Webhook|Other)
     - escalation_path_id (ESC-001, …)
     - auto_ticket (Yes|No)

8. Escalation Paths
   - Table:
     - escalation_path_id (ESC-001, …)
     - name
     - sequence (ordered list of contacts or groups)
     - timing (e.g., T+0m notify on-call, T+15m escalate to product owner)
     - handoff_criteria
     - closure_requirements

9. Evidence & Audit
   - Specify the evidence to retain for auditability and acceptance:
     - minimum_evidence_set table with columns: evidence_id, evidence_type, source, retention_policy, sample_location.
   - Note that screenshots and logs must redact sensitive data and follow the security policies.

10. Change Log (Register)
    - Append-only table maintained by automation or human:
      - change_id (CH-0001, …)
      - changed_section (e.g., Rule Register)
      - reason
      - author_role
      - created_at
      - related_request_id (if applicable)

Constraints & Allowed Values (Normative)
- severity: Critical, High, Medium, Low.
- dimension: Accuracy, Completeness, Consistency, Timeliness, Uniqueness, Validity.
- status: Active, Deprecated.
- cadence: OnIngest, Hourly, Daily, Weekly, AdHoc.
- environment: Dev, Test, Staging, Prod.
- IDs: rule_id (DQ-####), check_id (CHK-####), remediation_workflow_id (RW-###), dashboard_id (DQD-###), alert_id (AL-###), escalation_path_id (ESC-###), change_id (CH-####).
- Dates: YYYY-MM-DD; Timestamps: YYYY-MM-DD HH:MM (local time).

Validation Rules (Normative)
- Uniqueness:
  - rule_id, check_id, remediation_workflow_id, dashboard_id, alert_id, escalation_path_id, change_id MUST be unique.
- Referential integrity:
  - Each rule.owner_role MUST exist in Governance & Roles.
  - Each check.rule_id MUST reference an existing rule_id.
  - Each rule.remediation_workflow_id MUST reference an existing remediation_workflow_id.
  - Each alert.rule_or_check_ref MUST reference an existing rule_id or check_id.
  - Each alert.escalation_path_id MUST reference an existing escalation_path_id.
- Allowed values MUST match the enumerations above (case-sensitive).
- Timestamps MUST be valid and not in the future for last_execution_at.
- Status transitions:
  - A Deprecated rule MUST NOT have active alerts referencing it.
- Determinism:
  - For identical inputs, regeneration MUST produce the same IDs and ordering.

Operational Rules (Normative)
- AI and scripts MAY create, update, or deprecate rules and checks; human verification is expected for severity and remediation workflow selection.
- Automation MUST NOT remove historical Change Log entries.
- If a validation error occurs, tools MUST fail with a human-readable error and MUST NOT partially write.

Authoring Guidance (Informative)
- Keep titles short and descriptions precise.
- Prefer measurable success_criteria with explicit thresholds.
- Group related checks under a single rule to simplify reporting and escalation.
- For timeliness, specify both freshness_lag and allowable window by environment.

Seeding & Location Guidance (Normative)
- The DATA-07.md resides under 04 Technology/Data Workspace.
- Initial seeding may create empty sections and sample rows to guide authors; all placeholders MUST be removed before sign-off.

Acceptance Checklist (For Reviewers)
- Summary clearly states scope and monitoring surface.
- All roles and contacts present; on_call identified.
- Dimensions match allowed set; applicability_notes filled.
- Every rule has a dimension, severity, trigger_condition, owner_role, remediation_workflow_id, evidence_type, and status.
- Checks catalog maps each check to a rule, cadence, environment, implementation_reference, and success_criteria.
- Monitoring, dashboards, alerts, and escalation paths are fully cross-referenced and consistent.
- Evidence & Audit section defines retention and sample locations.
- No validation errors detected by automation.
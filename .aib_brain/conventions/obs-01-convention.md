Purpose
Define a strict, portable convention for the “Logging” document. The convention standardizes file naming, content structure, required fields, terminology, and operational rules so that engineers and reviewers can produce and validate a complete logging specification quickly and consistently.

Applicability
This convention applies to the single documentation file that specifies the product’s logging standards and operating rules across all components and environments.

File Name
OBS-01.md

Document Status Keywords
Use the RFC 2119/8174 modal keywords for requirement strength within this file: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY.

Authoring Principles
- Keep content concise, unambiguous, and implementation oriented.
- Prefer enumerated lists and tables over prose where possible.
- Write in English.
- Avoid tool- or vendor-specific features unless a generic equivalent is stated.

Required Top-Level Sections (in order)
1. Overview
2. Log Levels
3. Log Event Schema
4. Structured Logging Format
5. Collection & Transport
6. Destinations & Storage
7. Retention & Lifecycle
8. Taxonomy & Categories
9. Correlation & Tracing
10. Privacy & Security
11. Alerting & Usage Expectations
12. Quality Gates & Validation
13. Operational Procedures
14. Change Control

Section Requirements and Content Rules

1. Overview
- State the logging purpose and scope for the product or service.
- Declare which systems, services, and environments are in scope (e.g., dev, test, prod).
- Summarize the required evidence artifacts (e.g., schema file reference, dashboards, alert definitions).
- Outcomes: A short paragraph and a bullet list of scope items.

2. Log Levels
- Define the standardized levels to be used system-wide: DEBUG, INFO, WARN, ERROR, plus FATAL if applicable.
- For each level provide: intent, typical producers, example conditions, and retention class alignment (hot/warm/cold).
- Constraints:
  - Level names MUST be uppercase.
  - Level usage MUST be consistent across services.
  - Sensitive data MUST NOT be logged at DEBUG or INFO.

3. Log Event Schema
- Define the canonical fields REQUIRED in every log entry. The minimal required set is:
  - timestamp: ISO 8601 with timezone offset; services SHOULD log in UTC.
  - service_name: stable producer identifier.
  - environment: one of dev/test/stage/prod or equivalent.
  - host: node or pod identifier (as applicable).
  - trace_id: end-to-end correlation identifier.
  - span_id: local operation identifier (if tracing is implemented).
  - request_id: externally visible request correlation (if applicable).
  - user_id: pseudonymous subject identifier when relevant; MAY be absent for system events.
  - session_id: client session identifier, when relevant.
  - event_type: controlled vocabulary value describing the event (see Taxonomy & Categories).
  - level: one of the standardized levels.
  - message: concise human-readable description.
  - error_code: structured code for error conditions (when level is ERROR or higher).
  - error_stack: sanitized stack trace details (MUST exclude secrets and personal data).
  - component: logical subsystem (e.g., api-gateway, ingestion, scheduler).
  - resource: optional specific resource reference (e.g., file path, dataset name).
  - tags: key=value array for stable dimensions (e.g., region=eu, shard=1).
  - extras: object for structured, event-specific fields (MUST be JSON-serializable).
- Rules:
  - All required fields MUST exist per event (use null only where explicitly allowed).
  - Keys MUST be lower_snake_case.
  - Data types MUST be stable and documented.
  - Personally identifiable information MUST be avoided or anonymized; if unavoidable, document the lawful basis and masking strategy in Privacy & Security.

4. Structured Logging Format
- All services MUST emit logs in a structured, machine-parseable format.
- Preferred encoding: JSON Lines (one JSON object per line).
- Character encoding: UTF-8.
- Timestamp format: ISO 8601 extended, with Z or offset.
- Large binary payloads MUST NOT be embedded; reference them by ID.

5. Collection & Transport
- Describe log collection mechanisms (agents, sidecars, SDK appenders, direct API ingestion).
- For each mechanism define: deployment pattern, supported platforms, failure handling, backpressure strategy, batching and flush intervals, maximum payload size.
- Network transport MUST use secure channels (e.g., TLS) with certificate validation.
- Offline buffering SHOULD be enabled with bounded queues and loss telemetry.

6. Destinations & Storage
- Enumerate destinations (e.g., hot analytics store, warm searchable store, cold archive).
- For each destination define: purpose, write path, schema mapping, partitioning strategy, index strategy, compaction/merge behavior, cost considerations, RPO/RTO expectations.
- State access patterns (interactive search, dashboarding, forensics) and corresponding SLAs.

7. Retention & Lifecycle
- Define retention classes by level and category (e.g., ERROR and security events retained longer).
- Provide a lifecycle table specifying: storage tier, retention duration, transition triggers, deletion policy, and audit evidence required.
- Deletion MUST be verifiable with audit logs; automatic lifecycle transitions SHOULD be policy-driven.

8. Taxonomy & Categories
- Define controlled vocabularies for event_type and category (e.g., auth, io, network, validation, business_rule, data_quality).
- Provide mapping guidelines from source systems to the taxonomy.
- Prohibit free-text categories in required fields; free text MAY appear in message and extras.

9. Correlation & Tracing
- All request-serving paths SHOULD propagate trace_id and span_id.
- Cross-service calls MUST forward correlation identifiers unchanged.
- Asynchronous workflows MUST maintain logical correlation via parent identifiers.
- When tracing is unavailable, services MUST still emit request_id if present.

10. Privacy & Security
- Secrets MUST NEVER appear in logs (keys, tokens, passwords, private certificates).
- Apply deterministic masking for structured fields known to carry sensitive content.
- For user identifiers, prefer pseudonymous stable IDs; avoid direct personal data.
- Document the lawful basis for any personal data in logs and minimize its use.
- Access to log destinations MUST be role-based with least-privilege principles.

11. Alerting & Usage Expectations
- Define alerting policies based on metrics derived from logs (e.g., error rate, saturation, anomalous spikes).
- For each alert: condition, threshold, severity, business impact, runbook link, notification channel, escalation path, and ownership role.
- Dashboards and saved searches SHOULD be listed with their exact names and purposes.
- Evidence requirements MUST indicate where reviewers can find proof of active alerts and dashboards.

12. Quality Gates & Validation
- Provide a validation checklist for CI/CD and runtime:
  - Schema compliance check for all required fields.
  - Prohibit unknown keys at top level unless whitelisted.
  - Log rate and volume SLOs verified per service.
  - PII/secret scanners configured with allow/deny lists.
  - Sampling configuration documented for DEBUG-level logs in production.
- Define failure behavior (build fail, deployment block, or warning-only) per environment.

13. Operational Procedures
- Document standard procedures:
  - Enabling/disabling loggers and changing levels safely.
  - Rotating sinks and credentials.
  - Handling ingestion backlogs and partial outages.
  - Running forensic queries for recent incidents.
- Include a minimal “first-hour” investigation cookbook with 5–10 canonical queries by symptom.

14. Change Control
- Changes to schema, taxonomy, destinations, or retention MUST undergo review.
- Breaking changes MUST be versioned and announced with deprecation timelines.
- Provide a short change log within this document describing material updates.

Acceptance Criteria (for reviewers)
- The document contains all required sections, in order.
- All MUST/SHOULD rules are addressed with concrete values or rationale.
- Log levels, schema, and taxonomy are complete and consistent.
- Collection, destinations, and retention are fully specified with SLAs.
- Privacy, security, and validation controls are explicit and auditable.
- Alert definitions and operational procedures exist and are actionable.

Glossary (normative, minimum)
- event_type: Controlled vocabulary value describing the nature of the event.
- correlation: The practice of linking events across components via shared identifiers such as trace_id and request_id.
- hot/warm/cold storage: Tiers optimized for speed, balance, and cost respectively.

Appendix A: Minimal Required Field Table
Provide a table enumerating for each required field: key, type, required (Y/N), allowed values or pattern, example. At minimum include all fields listed in “Log Event Schema”.

Appendix B: Prohibited Content
- Secrets (API keys, tokens, passwords).
- Full unmasked personal data (names, emails, phone numbers, national identifiers).
- Raw binary blobs; store externally and reference by ID.

Document Maintenance
- This file is living documentation; keep it aligned with the running system and validated by automated checks where feasible.
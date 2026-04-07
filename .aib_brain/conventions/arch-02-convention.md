Purpose
Define the canonical format and editing rules for the “ARCH-02 — Topology/network description” document. The convention ensures deterministic authoring by AI tools and quick verification by humans.

Scope
This convention applies to the single product documentation file that describes network topology across all environments. It standardizes sections, tables, diagrams, and validation rules.

File Naming and Location (normative)
- File name: ARCH-02.md
- Exactly one file per product. If environment-specific supplements are needed, use anchors within the same file (not separate files).

Audience and Reading Expectations
- Primary: architects, security engineers, platform/network teams, SRE/operations.
- Secondary: developers and auditors.
- Language: English.
- Optimized for: quick scanning, deterministic parsing by automation, AI-supported generation.

Authoring Principles
- Write concise, unambiguous statements.
- Prefer tables and lists over prose.
- Use consistent terminology and units (e.g., Mbps, ms, CIDR).
- Diagrams are required and must be paired with machine-readable tables.

Document Structure (normative)
The file MUST follow the section order below. All sections are mandatory unless marked “(conditional)”.

1. Overview
   - One-paragraph description of the product network topology purpose and scope.
   - Architecture scope boundary statement (what is included/excluded).

2. Environments Inventory
   - List all environments (Dev, Test, Staging, Prod, DR, Sandbox, etc.).
   - Provide a register table with the following columns (exact headers):
     - env_id (Dev|Test|Staging|Prod|DR|Sandbox|Other:<name>)
     - region (e.g., westeurope, us-east-1, on-prem-dc-1)
     - tenancy (single-tenant|multi-tenant|shared)
     - internet_exposure (None|Restricted|Public)
     - notes

3. Trust Zones and Segmentation
   - Define trust zones and segmentation strategy.
   - Provide a register table (exact headers):
     - zone_id (e.g., public, dmz, app, data, mgmt)
     - description
     - allowed_sources (zone_id list or “any” with qualifier)
     - allowed_destinations (zone_id list)
     - isolation_controls (e.g., NSG/SG, firewall, policy)
     - data_classification_allowed (Public|Internal|Confidential|Restricted)

4. Network Elements Catalog
   - Every network-relevant element must be listed (gateways, load balancers, API gateways, app services, databases, message brokers, storage endpoints, jump hosts, bastions, NAT, VPN, private endpoints, service endpoints).
   - Provide a catalog table (exact headers):
     - element_id (stable identifier)
     - type (gateway|lb|api-gw|service|db|queue|topic|storage|bastion|nat|vpn|pe|se|other)
     - env_id
     - zone_id
     - location (region/zone/az)
     - dns_name (FQDN or “n/a”)
     - ip (single IP or CIDR; “private”/“public” allowed as qualifier)
     - high_availability (N|AZ|Region|Global)
     - notes

5. Connectivity Matrix (Ingress/Egress)
   - Define permitted flows between elements (one row per flow).
   - Provide a matrix table (exact headers):
     - src_element_id
     - dst_element_id
     - protocol (tcp|udp|icmp|https|http|amqp|mqtt|grpc|other)
     - src_port (int or “*”)
     - dst_port (int or “*”)
     - encryption (tls12|tls13|ipsec|none)
     - authn (mtls|oauth2|key|basic|none)
     - authz (rbac|abac|scope|none)
     - data_sensitivity (Public|Internal|Confidential|Restricted)
     - purpose (short reason)
     - allowed_times (always|window:<cron/UTC>)
     - control_point (fw|nsg|sg|waf|policy|route|peering)
     - evidence (runbook/test-id or “n/a”)

6. External Dependencies
   - List third-party or corporate external endpoints (SaaS, identity providers, payment, telemetry).
   - Provide a dependencies table (exact headers):
     - dep_id
     - provider
     - endpoint (FQDN or CIDR)
     - protocol
     - purpose
     - data_sensitivity
     - contract/SLA (brief; link text is allowed but avoid external hyperlinks in the file)
     - notes

7. Name Resolution (DNS) and Certificates
   - Describe DNS zones, record types, and certificate strategy (issuers, rotation policy, SANs).
   - Provide a table (exact headers):
     - record_name
     - record_type (A|AAAA|CNAME|TXT|SRV|ALIAS|PTR)
     - scope (env_id)
     - target
     - ttl
     - certificate_ref (if tls-terminated; else “n/a”)

8. Routing, Peering, and Edge
   - Summarize routing domains, peering (VNet/VPC peering, ExpressRoute/DirectConnect), edge/CDN, NAT strategy.
   - Provide a table (exact headers):
     - route_id
     - scope (env_id|global)
     - source_cidr
     - next_hop (gateway|virtual-appliance|internet|vnet-peering|local)
     - notes

9. Security Controls
   - Enumerate applied security layers for network traffic: WAF, firewalls, SG/NSG, NACLs, IDS/IPS, DDoS, private endpoints.
   - Provide a table (exact headers):
     - control_id
     - type (waf|fw|nsg|sg|nacl|ids|ips|ddos|pe|se|policy)
     - scope (env_id|zone_id|element_id|global)
     - rule_ref (pointer to ruleset or policy name)
     - objective (e.g., ingress restriction, egress allowlist)
     - monitoring (on|off|partial)
     - notes

10. Availability, DR, and Failover Paths
   - Document HA strategy, failover, and DR connectivity.
   - Provide a table (exact headers):
     - scenario (component failure|zone outage|region outage|dr test)
     - affected_elements
     - failover_mechanism (active-active|active-passive|manual)
     - rto_target
     - rpo_target
     - validation (playbook/ref)

11. Diagram Set (required)
   - Provide at least one high-level topology diagram and per-environment overlays.
   - Each diagram MUST have an alt-text and a caption.
   - Allowed diagram formats: embedded Markdown image referencing a local relative asset (PNG/SVG) or a fenced code block for text-based diagrams (e.g., Mermaid/PlantUML).
   - Each diagram MUST be referenced from sections 2–10 via element_id/env_id anchors.

12. Operational Evidence Hooks
   - Reference IDs for automated validation (connectivity tests, TLS checks, DNS resolution, security policy checks).
   - Provide a table (exact headers):
     - test_id
     - description
     - scope (env_id|element_id|flow)
     - cadence (on_deploy|daily|weekly|ad-hoc)
     - success_criteria
     - last_result (pass|fail|n/a)
     - notes

13. Assumptions and Constraints
   - Explicitly list assumptions (e.g., shared services availability) and constraints (e.g., org policies, legacy networks).

14. Change Log (append-only)
   - Keep a human-auditable list of material topology changes (date, summary, affected elements). Do not version the file; this section serves as traceability.

Editing Rules (normative)
- Section order is fixed; do not reorder.
- All register tables MUST preserve exact headers and column order.
- Allowed values are constrained to the enumerations stated in each section.
- Long lists SHOULD be split across multiple rows rather than multiline cells.
- Use “n/a” instead of leaving required cells empty.
- Avoid external hyperlinks; reference local assets/anchors only.
- Diagrams must correspond 1:1 to elements and flows listed in the tables (no orphan diagram nodes).

Validation Rules (normative)
- Uniqueness:
  - env_id values must be unique within the file.
  - element_id values must be globally unique within the file.
  - src_element_id and dst_element_id in Connectivity Matrix MUST reference valid element_id values.
- Referential integrity:
  - Every zone_id used by an element MUST exist in Trust Zones and Segmentation.
  - Every diagram node MUST map to an element_id.
- Enumerations:
  - Values must match allowed sets exactly (case-sensitive unless specified).
- Security:
  - No flow with data_sensitivity ∈ {Confidential, Restricted} may declare encryption=none.
  - internet_exposure=Public requires control_point including waf or fw at boundary.
- DR:
  - For env_id=Prod, at least one DR scenario row is required with explicit rto_target and rpo_target.

AI Generation Prompts (advisory)
- When generating this document, first build tables (sections 2–10, 12) from source-of-truth inventories, then render diagrams (section 11).
- Prefer stable identifiers and reuse them consistently.
- Emit warnings when a validation rule would be violated and halt write if critical rules fail.

Examples (illustrative)
- Environments Inventory (snippet):
  ```text
  | env_id  | region       | tenancy      | internet_exposure | notes               |
  |---------|--------------|--------------|-------------------|---------------------|
  | Dev     | westeurope   | shared       | Restricted        | Shared platform VNET|
  | Prod    | northeurope  | single-tenant| Public            | Public API via WAF  |
  ```
- Connectivity Matrix (snippet):
  ```text
  | src_element_id | dst_element_id | protocol | src_port | dst_port | encryption | authn | authz | data_sensitivity | purpose          | allowed_times | control_point | evidence |
  |----------------|----------------|----------|---------:|---------:|-----------|-------|-------|------------------|------------------|--------------|---------------|----------|
  | api-gw         | app-svc        | https    |       *  |     443  | tls13     | mtls  | rbac  | Confidential     | inbound requests | always       | waf           | T-API-01 |
  ```

Diagram Requirements (normative)
- Provide at least:
  - One high-level diagram showing zones and major elements.
  - One per-environment overlay highlighting differences.
- Diagram metadata:
  - Caption format: “Figure <n>: <short title>”
  - Alt-text: 1–2 sentences describing the message of the diagram.
- If using Mermaid, prefer “flowchart” or “graph TD” with element_id as node identifiers.

Quality Checklist (for human verification)
- [ ] All mandatory sections exist and in the prescribed order.
- [ ] All tables present with exact headers and no empty required cells.
- [ ] All IDs (env_id, zone_id, element_id) are unique and cross-referenced correctly.
- [ ] No confidential/restricted flow without encryption and an explicit control point.
- [ ] Diagrams align with tabular data; no orphan nodes/edges.
- [ ] DR section present for Prod with clear RTO/RPO and validation.
- [ ] Change Log updated for any material changes.

Appendix A — Controlled Vocabularies
- env_id: Dev, Test, Staging, Prod, DR, Sandbox, Other:<name>
- internet_exposure: None, Restricted, Public
- zone_id (examples): public, dmz, app, data, mgmt
- element type: gateway, lb, api-gw, service, db, queue, topic, storage, bastion, nat, vpn, pe, se, other
- protocol: tcp, udp, icmp, https, http, amqp, mqtt, grpc, other
- encryption: tls12, tls13, ipsec, none
- authn: mtls, oauth2, key, basic, none
- authz: rbac, abac, scope, none
- data_sensitivity: Public, Internal, Confidential, Restricted
- control_point: fw, nsg, sg, nacl, waf, policy, route, peering
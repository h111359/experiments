# Overview

This file inventories technology resources used by AIB in this repository. AIB does not provision cloud infrastructure here; resources include repository, CI workflow, and core artifact sets.

# Registry

| resource_id | name | cloud | account_subscription | environment | region | resource_group_namespace | service_type_sku | purpose | application_function | criticality | data_classification | dependencies | tags | cost_center | owner_role | operational_sla | backup_recovery | dr_class | monitoring | iac_source | lifecycle_state | created_at | last_changed | decommission_plan | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RES-0001 | AI_Builder repository | other | - | shared | global | - | Git / repository | Store AIB assets and workspace artifacts | orchestration | C2 (high) | Internal | - | repo=AI_Builder,system=aib | - | Repository Maintainers | best-effort | N/A | DR1 (manual) | - | - | active | 2026-03-09 | 2026-03-22 | - | Source-controlled repository. |
| RES-0002 | GitHub Actions workflow | other | - | prod | global | - | GitHub Actions / workflow | Automate patch bump and log creation | operations | C2 (high) | Internal | RES-0001 | ci=github-actions,workflow=release | - | AIB Maintainers | best-effort | Provider-Managed | DR1 (manual) | - | .github/workflows/aib-semver-patch-bump-and-log.yml | active | 2026-03-20 | 2026-03-22 | - | Requires repo Actions permissions. |
| RES-0003 | AIB brain assets | other | - | shared | local-workstation | - | Filesystem / folder | Reusable prompts, conventions, templates, tools | orchestration | C1 (critical) | Internal | RES-0001 | path=.aib_brain | - | AIB Maintainers | best-effort | N/A | DR0 (none) | - | - | active | 2026-03-09 | 2026-03-22 | - | Replaceable asset set. |
| RES-0004 | AIB memory artifacts | other | - | dev | local-workstation | - | Filesystem / folder | Requests, registers, product docs | storage | C2 (high) | Internal | RES-0003 | path=.aib_memory | - | Product Team | best-effort | Scheduled; via git commits | DR0 (none) | - | - | active | 2026-03-09 | 2026-03-22 | - | Backed up via VCS practices. |
| RES-0005 | Release bookkeeping script | other | - | prod | github-actions | - | Python / script | Compute patch bump and write version log | operations | C2 (high) | Internal | RES-0002 | path=scripts/release_bookkeeping.py | - | AIB Maintainers | best-effort | N/A | DR1 (manual) | - | - | active | 2026-03-20 | 2026-03-22 | - | Runs in CI; requires git. |

# Conventions and Allowed Values

- cloud=other because resources are repo/CI/file based.

# Validation Rules

- Registry table appears once with exact headers and order.
- resource_id unique and sorted.

# Operations (Create, Edit, Review)

- Add a row when introducing a new CI workflow or external dependency.
- Review quarterly.

# Quality Checks (Checklist)

- [ ] Single Registry table present.
- [ ] resource_id values unique and sorted.

# Change Log

- 2026-03-22 — Populated initial AIB resource catalog.

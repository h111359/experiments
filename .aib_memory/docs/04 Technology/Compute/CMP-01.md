# CMP-01 — Notebook/Script Catalog

## Instructions (Non-normative)

Add one row per executable script/pipeline used by AIB. Prefer workspace-relative paths in `version_control` and keep fields single-line. Use `TBD` instead of leaving required cells empty.

## Catalog

| id | name | kind | purpose | source_assets | inputs | outputs | dependencies | env | version_control | edge_cases_and_validation | run_profile | owner | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CMP-ART-0001 | Initialize AIB memory | script | Seed `.aib_memory` registers and doc stubs from `.aib_brain` | repo:.aib_brain/templates, repo:.aib_brain/conventions | param:workspace=.|N/A; data:repo filesystem | file:.aib_memory/references.md; file:.aib_memory/requests_register.md; files:.aib_memory/docs/* | .aib_brain/tools/common.py | Python 3.10+; stdlib | .aib_brain/tools/initialize.py | Fail on invalid workspace; avoid partial writes | schedule=ad-hoc; timeout=5m | AIB Maintainers | active |
| CMP-ART-0002 | Create request | script | Create Active request folder and seed request artifacts | repo:.aib_memory/requests_register.md | param:workspace=.|N/A; param:title=TBD|N/A | files:.aib_memory/requests/<request-folder>/*; file:.aib_memory/requests_register.md | CMP-ART-0001; .aib_brain/tools/common.py | Python 3.10+; stdlib | .aib_brain/tools/create-request.py | Must fail if another request is Active | schedule=ad-hoc; timeout=2m | Product Team | active |
| CMP-ART-0003 | Create iteration | script | Append next iteration and set Active | repo:.aib_memory/requests/<request>/iterations.md | param:workspace=.|N/A; param:summary=TBD|N/A | file:.aib_memory/requests/<request>/iterations.md | CMP-ART-0002; .aib_brain/tools/common.py | Python 3.10+; stdlib | .aib_brain/tools/create-iteration.py | Enforce single Active iteration | schedule=ad-hoc; timeout=2m | Product Team | active |
| CMP-ART-0004 | Close iteration | script | Mark Active iteration Completed | repo:.aib_memory/requests/<request>/iterations.md | param:workspace=.|N/A | file:.aib_memory/requests/<request>/iterations.md | CMP-ART-0003; .aib_brain/tools/common.py | Python 3.10+; stdlib | .aib_brain/tools/close-iteration.py | Fail if no Active iteration | schedule=ad-hoc; timeout=2m | Product Team | active |
| CMP-ART-0005 | Close request | script | Mark Active request Closed | repo:.aib_memory/requests_register.md | param:workspace=.|N/A | file:.aib_memory/requests_register.md | CMP-ART-0002; .aib_brain/tools/common.py | Python 3.10+; stdlib | .aib_brain/tools/close-request.py | Fail if invalid lifecycle state; auto-closes active iteration(s) before closing request and prints a notice per iteration | schedule=ad-hoc; timeout=2m | Product Team | active |
| CMP-ART-0006 | AIB command menu | script | Interactive menu for tool scripts with real-time output streaming and per-action logging | repo:.aib_brain/tools | param:workspace=.|N/A | terminal UI; file:logs/aib-action-*.log | CMP-ART-0001..CMP-ART-0005 | Python 3.10+; stdlib | .aib_brain/tools/menu.py | Must surface failures clearly; EXCLUDE_SCRIPTS prevents non-tool scripts from appearing; streams stdout/stderr via Popen tee pattern with encoding="utf-8", errors="replace" to handle non-ASCII output on Windows; streaming thread exceptions caught and logged as [THREAD-ERROR]; writes per-action log files | schedule=ad-hoc; interactive=true | AIB Maintainers | active |
| CMP-ART-0007 | Release bookkeeping | script | Validate marker, bump patch, rotate marker, create version log | repo:.aib_brain/vMAJOR.MINOR.PATCH, repo:git history | param:base_ref=origin/main|N/A | file:logs/version_vX.Y.Z_log.md; file:.aib_brain/vX.Y.Z | git | Python 3.10+; git; stdlib | scripts/release_bookkeeping.py | Fail on invalid markers; idempotent reruns | schedule=on-pr-events; timeout=10m | AIB Maintainers | active |
| CMP-ART-0008 | AIB test suite | script | Automated pytest test suite for all AIB tool scripts | repo:tests/*.py | param:workspace=.|N/A | test results (stdout) | pytest; CMP-ART-0001..CMP-ART-0006; .aib_brain/tools/common.py | Python 3.10+; pytest | tests/ | Verify all test files pass; temp dirs for isolation | schedule=ad-hoc; timeout=60s | AIB Maintainers | active |

## Conventions & Examples

| id | name | kind | purpose | source_assets | inputs | outputs | dependencies | env | version_control | edge_cases_and_validation | run_profile | owner | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CMP-ART-9999 | Example artifact | script | Example description | ds:example | param:x=1|0..9; data:example | file:out.txt | - | Python 3.10+ | scripts/example.py | Validates input range | schedule=ad-hoc | Example Owner | draft |

## Validation Notes

- Keep the exact column order in the Catalog table.
- `kind` and `status` must match allowed enumerations.

# Implementation Log

## Implementation Log

### Entry 2026-04-30 22:07
#### Scope
Remove the `.aib_memory/references.md` register from the AIB framework, hard-wire each prompt to read `.aib_memory/context.md` directly, and add a one-shot upgrade-time warning that surfaces any non-default rows from a legacy `references.md` so the developer can migrate them into `.aib_memory/instructions.md`. Aligned with analysis section "Plan" tasks 1–8.

#### Changes
- Updated `.aib_brain/prompts/aib-analysis.md`, `.aib_brain/prompts/aib-implement.md`, and `.aib_brain/prompts/aib-context.md` to remove every `references.md` mention and add explicit `.aib_memory/context.md` preflight reads.
- Updated `.aib_brain/conventions/request-convention.md`, `.aib_brain/conventions/implementation-convention.md`, and `.aib_brain/Concepts.md` to remove the `references.md` schema, REF-0001/REF-0002 seeding rules, and action-contract matrix entries.
- Deleted `.aib_brain/conventions/references-convention.md`, `.aib_brain/templates/references-template.md`, and the live `.aib_memory/references.md`.
- Removed `references_path()`, `seed_references_from_product_doc()`, `parse_product_documentation_requirements()`, `resolve_product_documentation_path()`, `sanitize_location_to_path()`, `RequirementRef`, `REQ_HEADING_PATTERN`, and `LOCATION_PATTERN` from `.aib_brain/tools/common.py`.
- Updated `.aib_brain/tools/initialize.py` to drop the `references.md` seeding code path and added the `_warn_about_legacy_references(legacy_path)` helper, invoked from `_run_upgrade` between the archive copy and the non-archive deletion steps.
- Removed obsolete `references.md` assertions and the `TestInitializeReferencesSkip` class from `tests/test_initialize.py` and `.aib_brain/tools/test_common.py`; added three new test cases (`test_upgrade_warns_when_legacy_references_has_extra_rows`, `test_upgrade_silent_when_only_default_references_present`, `test_upgrade_handles_unparseable_legacy_references`) plus `test_initialize_does_not_create_references_md` to cover SC-1, SC-7, and SC-9.
- Refreshed `.aib_memory/context.md` to drop every `references.md`/REFERENCE entity/`edit_allowed` mention and document the new upgrade-time warning behaviour.
- Appended curated bullets to `logs/next_version_changes.md` per the workspace `instructions.md` directive.

#### Tests
- unit/integration: `python -m pytest tests/ .aib_brain/tools/test_common.py --ignore=tests/test_semver_workflow_structure.py` — 185 passed.
- The `test_semver_workflow_structure.py` module requires the optional `pyyaml` dependency which is not installed in this environment; it was excluded from the run by the same `--ignore` flag used in the prior baseline. Behaviour of that module is unchanged by this iteration.

#### Outcome
Successful. All Success Criteria SC-1 through SC-9 are met. The `--upgrade` warning is informational only and never alters the upgrade exit code; the helper handles malformed legacy tables with the explicit `WARNING: legacy references.md is not parseable; skipping migration check.` line.

#### Evidence
- Path: `.aib_brain/tools/initialize.py` (helper `_warn_about_legacy_references`, invoked between Step 2 and Step 3 of `_run_upgrade`).
- Path: `tests/test_initialize.py::TestUpgradeLegacyReferencesWarning` (three new test cases).
- Path: `.aib_memory/context.md` (regenerated; no `references.md` register entries; new upgrade-warning paragraph in FR-013).
- Path: `logs/next_version_changes.md` (three new bullets describing the removal and warning).
- Test summary:
  ```text
  ============================ 185 passed in 10.19s =============================
  ```

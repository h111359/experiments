## Goal

Remove `.aib_memory/references.md` from the AI Builder framework and replace its role. Make every AIB prompt explicitly read `.aib_memory/context.md` instead of inferring it from `references.md`. Allow developers to point AIB at additional context files via `.aib_memory/instructions.md`. Make any reference to `.aib_brain/Concepts.md` in prompts strictly optional and remove the reference where it is not required for prompt execution. During the `initialize.py --upgrade` procedure, when an existing `references.md` is encountered in the workspace being upgraded, parse it and emit a console warning listing any rows whose `path` does not point to `.aib_memory/context.md` or `.aib_brain/Concepts.md`, instructing the user to migrate those references into `.aib_memory/instructions.md`.

## Background

The current `references.md` register exists primarily to seed two fixed rows: `REF-0001 .aib_memory/context.md` (product-doc) and `REF-0002 .aib_brain/Concepts.md` (domain). All other rows would have to be added by the developer manually, which never happens in the live workspace. The same outcome — pointing AIB at `context.md` and at any additional file the developer wants surfaced — can be achieved more directly by:

1. Hard-coding an explicit "read `.aib_memory/context.md`" step inside each prompt (`aib-analysis.md`, `aib-implement.md`).

2. Using the already-existing `.aib_memory/instructions.md` as the free-form channel for any extra files the developer wants AIB to read or treat with special care.

The `Concepts.md` reference, currently listed as a prompt input, duplicates information already present in `context.md` and the conventions; the prompt bodies do not actually depend on its content for correct execution.

Removing `references.md` simplifies the workspace (one fewer register to maintain), eliminates the `Product_Documentation.md` seeding code path that is no longer used, and reduces the surface area touched by `initialize.py` and the upgrade procedure.

## Scope

- Stop generating `.aib_memory/references.md` during `initialize.py` (both standard initialization and `--upgrade` paths).

- Delete the existing `.aib_memory/references.md` file from the workspace.

- Add an upgrade-time legacy inspection step in `initialize.py --upgrade`: before deleting the old `references.md` content, read it from the about-to-be-archived workspace memory; identify any rows whose `path` differs from the two known defaults (`.aib_memory/context.md`, `.aib_brain/Concepts.md`); emit a single human-readable console warning block listing each such legacy `path` and instructing the user to migrate it into `.aib_memory/instructions.md`. The warning is informational only and MUST NOT abort the upgrade. Standard `initialize.py` (non-upgrade) does not perform this check, since it does not delete an existing `references.md`.

- Delete the seed template `.aib_brain/templates/references-template.md`.

- Delete the convention `.aib_brain/conventions/references-convention.md`.

- Remove all references to `references.md` from the prompts (`.aib_brain/prompts/aib-analysis.md`, `.aib_brain/prompts/aib-implement.md`, `.aib_brain/prompts/aib-context.md`).

- Add an explicit step to each prompt requiring it to read `.aib_memory/context.md` (and treat absent/empty file as no-op, matching the `instructions.md` pattern). For `aib-context.md` (which produces `context.md`), the explicit-read step does not apply; instead it relies on `instructions.md` for any developer-supplied extra source paths.

- Review every mention of `.aib_brain/Concepts.md` in the prompts. Remove the reference where it is not required for the prompt to execute correctly. Keep it only when removal would demonstrably break the prompt.

- Remove all `references.md` mentions from conventions: `request-convention.md`, `implementation-convention.md`, and any other convention currently citing it.

- Remove the `references.md` schema, action contract matrix entries, and `REF-0001` / `REF-0002` seeding rules from `.aib_brain/Concepts.md`.

- Remove `references_path()`, `seed_references_from_product_doc()`, and any helpers that exist only to support `references.md` (including `parse_product_documentation_requirements`, `resolve_product_documentation_path`, and the `RequirementRef` dataclass if no longer used) from `.aib_brain/tools/common.py`. Update `initialize.py` to drop the `references.md` seeding code path and the related import.

- Update tests under `tests/` (notably `tests/test_initialize.py`) and `.aib_brain/tools/test_common.py` to remove assertions and fixtures that depend on `references.md` / `references-template.md`.

- Re-run `aib-context.md` so `.aib_memory/context.md` no longer documents `references.md` as part of the product structure.

## Out of scope

- No changes to the `requests_register.md` register, request lifecycle, or `aib-implement.md` close/move flows.

- No changes to the `attachments/` channel.

- No introduction of a new register file to replace `references.md`.

- No automated migration of legacy per-workspace `references.md` content; existing rows beyond the two defaults are not preserved (developers can capture any extra paths in `instructions.md` if needed).

- No changes to the version bump CI workflow or `release_bookkeeping.py`.

- No changes to coding-language conventions.

## Constraints

- Tool scripts must remain Python 3.10+ standard-library-only.

- All changes must keep `initialize.py` and the upgrade procedure idempotent.

- No partial writes on validation failure (existing fail-closed contract preserved).

- Deletion of `references.md` from the workspace must not break any active automated test or any other prompt invocation.

- The `instructions.md` mechanism (already in place) is the only sanctioned channel for developer-supplied extra context; no new free-form register is introduced.

- The legacy-references warning emitted by `--upgrade` MUST be informational only (printed to stdout); it MUST NOT block, abort, or alter the upgrade outcome. A malformed legacy `references.md` MUST be tolerated (skipped with a single `WARNING: legacy references.md is not parseable; skipping migration check.` line) rather than failing the upgrade.

- Prompts must continue to be model-agnostic and vendor-agnostic.

## Success criteria

- SC-1: `.aib_memory/references.md` does not exist in the workspace, and `initialize.py` does not recreate it on either standard or `--upgrade` runs.

- SC-2: `.aib_brain/templates/references-template.md` and `.aib_brain/conventions/references-convention.md` no longer exist.

- SC-3: A repository-wide search for the literal string `references.md` returns matches only inside historical archives (e.g., `logs/`, `.aib_memory/archives/`, `.aib_memory/requests/<closed-request>/`) and inside this active request's own artifacts; no matches inside `.aib_brain/prompts/`, `.aib_brain/conventions/`, `.aib_brain/templates/`, `.aib_brain/tools/` (excluding tests removed in this iteration), or `.aib_brain/Concepts.md`.

- SC-4: Each of `.aib_brain/prompts/aib-analysis.md` and `.aib_brain/prompts/aib-implement.md` contains an explicit instruction to read `.aib_memory/context.md` (graceful when absent or empty).

- SC-5: Every remaining mention of `.aib_brain/Concepts.md` in prompt files is justified inline (i.e., the prompt explicitly uses content from `Concepts.md`); unjustified mentions are removed.

- SC-6: The full automated test suite passes (`pytest tests/` and `python -m pytest .aib_brain/tools/test_common.py`).

- SC-7: A fresh `python .aib_brain/tools/initialize.py --workspace <tmp>` on an empty workspace succeeds and does not create `references.md`.

- SC-8: After running `aib-context.md` as the final implementation step, `.aib_memory/context.md` does not list `references.md` as a current artifact and reflects the new prompt-level explicit `context.md` read step.

- SC-9: When `initialize.py --upgrade` is run against a workspace whose `references.md` contains rows beyond the two defaults (`REF-0001` → `.aib_memory/context.md`, `REF-0002` → `.aib_brain/Concepts.md`), the script prints a single warning block listing each extra `path` and telling the user to add it to `.aib_memory/instructions.md`. When `references.md` contains only the two defaults (or is absent), no such warning is printed. In neither case does the warning change the upgrade exit code.

## Assumptions

- A1: No live workspace currently relies on `references.md` rows beyond the two default seeded rows (REF-0001 context.md, REF-0002 Concepts.md). The default register has not been customized.
  - Risk if false: A user-added row would be silently lost on deletion. Mitigation: developers may capture any extra paths in `instructions.md` after the change.

- A2: `.aib_brain/Concepts.md` is not actually consumed by `aib-analysis.md` (listed only as input) and is not strictly required by `aib-implement.md` (lifecycle/safety rules duplicated in tool scripts and Safety section of the prompt).
  - Risk if false: Loss of normative reference. Mitigation: `Concepts.md` itself is not deleted — it remains in `.aib_brain/` and can be re-introduced into prompts on demand.

- A3: The static template-driven seeding path in `seed_references_from_product_doc()` is the only live code path; `Product_Documentation.md` does not exist in the workspace.
  - Risk if false: Removing the parser would break a hidden caller. Mitigation: codebase-wide grep for the helper names before removal.

- A4: Tests in `tests/test_initialize.py` and `.aib_brain/tools/test_common.py` are the only automated tests that assert on `references.md`; no other test depends on the file.
  - Risk if false: Other tests break. Mitigation: full pytest run is part of the plan.

- A5: The legacy `references.md` (when present) is a Markdown table parseable by the existing `parse_markdown_table` helper in `common.py` and exposes a `path` column whose values are workspace-relative file references.
  - Risk if false: The migration warning would be unreliable. Mitigation: wrap the parse in a try/except and emit the explicit `WARNING: legacy references.md is not parseable; skipping migration check.` line instead of aborting the upgrade.

- A6: The two default `path` values that MUST NOT trigger the warning are exactly `.aib_memory/context.md` and `.aib_brain/Concepts.md` (case-sensitive comparison after normalising path separators to forward slashes). Any other value — including `.aib_brain\Concepts.md` with backslash, when normalised — counts as a default; any value that does not normalise to one of the two is considered legacy/extra.
  - Risk if false: A non-default path could be misclassified. Mitigation: the comparison is performed on the normalised forward-slash form to absorb the seed template's `.aib_brain\Concepts.md` representation.

## Plan

### Task 1: Update prompt files
**Intent:** Make `references.md` removal effective in the three prompt files and add explicit `context.md` reads.
**Inputs:** `.aib_brain/prompts/aib-analysis.md`, `.aib_brain/prompts/aib-implement.md`, `.aib_brain/prompts/aib-context.md`.
**Outputs:** Modified prompt files with no `references.md` references and explicit `context.md` read steps.
**External Interfaces:** None (text edits).
**Environment & Configuration:** N/A.
**Procedure:**
1. In `aib-analysis.md`: drop `references.md` and `Concepts.md` from the Inputs list and from the required-read set; add an explicit "Read `.aib_memory/context.md`" preflight step (graceful when absent or empty); rephrase Plan/Documentation rules to refer to `context.md` and `instructions.md` instead of `references.md`; rephrase the Q-block pre-check to refer to `context.md`, convention files, and `instructions.md`.
2. In `aib-implement.md`: remove the `Read .aib_memory/references.md` step and the `edit_allowed=Y` gate; add an explicit "Read `.aib_memory/context.md`" preflight step; collapse the convention preflight to just `context-convention.md`; remove the `Concepts.md` read line.
3. In `aib-context.md`: drop Phase 1 product-doc read set; rewrite Phase 1 to read `context-convention.md` only; treat `instructions.md` as the channel for any developer-supplied extra source paths; remove `references.md` from Non-goals and from the reverse-engineering note.
**Done Criteria:** No occurrences of `references.md` in the three prompt files; explicit `context.md` read present in `aib-analysis.md` and `aib-implement.md`.
**Dependencies:** None.

### Task 2: Update conventions and Concepts.md
**Intent:** Remove `references.md` from all conventions and from the AIB Concepts document.
**Inputs:** `.aib_brain/conventions/request-convention.md`, `.aib_brain/conventions/implementation-convention.md`, `.aib_brain/Concepts.md`.
**Outputs:** Updated conventions and Concepts.md.
**External Interfaces:** None.
**Environment & Configuration:** N/A.
**Procedure:**
1. Remove the `references.md` mentions in `request-convention.md` (Plan rule, Background reference, Internal Review wording).
2. Remove the example `references.md` lines from `implementation-convention.md`.
3. Remove the `references.md schema (normative)` section, REF-0001/REF-0002 seeding rules, and the `references.md` mentions in the action contract matrix and the `initialize` action description from `Concepts.md`.
**Done Criteria:** Grep returns no `references.md` matches in the modified files.
**Dependencies:** None.

### Task 3: Delete obsolete brain assets
**Intent:** Physically delete the convention and template files for `references.md`.
**Inputs:** `.aib_brain/conventions/references-convention.md`, `.aib_brain/templates/references-template.md`.
**Outputs:** Files deleted from the repository.
**External Interfaces:** Filesystem.
**Environment & Configuration:** N/A.
**Procedure:**
1. Delete `.aib_brain/conventions/references-convention.md`.
2. Delete `.aib_brain/templates/references-template.md`.
**Done Criteria:** Both files do not exist; pytest passes.
**Dependencies:** Task 4 (so initialize.py no longer imports the helper that needs the template).

### Task 4: Update tool scripts
**Intent:** Remove `references.md` seeding code path from `initialize.py` and dead helpers from `common.py`; add the upgrade-time legacy-references inspection.
**Inputs:** `.aib_brain/tools/initialize.py`, `.aib_brain/tools/common.py`.
**Outputs:** Updated tool scripts.
**External Interfaces:** None.
**Environment & Configuration:** N/A.
**Procedure:**
1. In `initialize.py`: remove the `seed_references_from_product_doc` import; delete the references-seeding block in `_seed_memory`; update the docstring (`force` no longer pertains to `references.md`); update the upgrade summary print line to drop the `references.md` line.
2. In `common.py`: remove `references_path()`, `seed_references_from_product_doc()`, `parse_product_documentation_requirements()`, `resolve_product_documentation_path()`, `sanitize_location_to_path()`, `RequirementRef`, `REQ_HEADING_PATTERN`, and `LOCATION_PATTERN` if no callers remain (verify with grep).
3. In `initialize.py` `_run_upgrade`, before the Step 3 deletion of non-archive content, add a helper (e.g., `_warn_about_legacy_references`) that: reads `<memory_root>/references.md` if it exists; parses it via `parse_markdown_table` (wrapped in try/except — on failure print `WARNING: legacy references.md is not parseable; skipping migration check.` and return); collects every row whose normalised `path` (forward-slash) is not in `{".aib_memory/context.md", ".aib_brain/Concepts.md"}`; if the resulting list is non-empty, prints a single warning block of the form:

```
WARNING: legacy references.md contains entries beyond the two defaults.
The following references will NOT be migrated automatically:
  - <path-1>
  - <path-2>
If you still need them, add them to .aib_memory/instructions.md.
```

   The helper MUST NOT raise; it is informational only.
**Done Criteria:** `initialize.py --workspace <tmp>` produces no `references.md`; `python -c "import common"` succeeds; pytest passes; an `--upgrade` run against a synthetic workspace whose `references.md` contains an extra row prints the warning block listing that row.
**Dependencies:** None.

### Task 5: Update tests
**Intent:** Align automated tests with the removal and cover the new upgrade-time legacy inspection.
**Inputs:** `tests/test_initialize.py`, `.aib_brain/tools/test_common.py`.
**Outputs:** Updated test files.
**External Interfaces:** pytest.
**Environment & Configuration:** Existing `.venv`.
**Procedure:**
1. In `tests/test_initialize.py`: remove all `references.md` is-file assertions (lines ~87, 138, 333–341, 401, 452); remove the related fixtures or adjust them so the rest of each test still passes.
2. In `.aib_brain/tools/test_common.py`: remove the P28 references.md skip-if-exists test and the `references-template.md` setup helper.
3. Add three new test cases in `tests/test_initialize.py` (or a new `tests/test_legacy_references_warning.py`):
   a. `test_upgrade_warns_when_legacy_references_has_extra_rows`: seed a workspace whose `.aib_memory/references.md` contains the two defaults plus one extra row (e.g., `REF-0003 docs/custom.md`); run `_run_upgrade` (or invoke `initialize.py --upgrade` as subprocess and capture stdout); assert the warning block is present in stdout and lists `docs/custom.md`.
   b. `test_upgrade_silent_when_only_default_references_present`: seed a workspace whose `.aib_memory/references.md` contains only the two defaults; run upgrade; assert the warning block is absent from stdout (no `WARNING: legacy references.md` substring).
   c. `test_upgrade_handles_unparseable_legacy_references`: seed a workspace whose `.aib_memory/references.md` is malformed (not a table); run upgrade; assert stdout contains `WARNING: legacy references.md is not parseable; skipping migration check.` and that the upgrade still completes successfully (exit code 0).
**Done Criteria:** `pytest tests/` and `python -m pytest .aib_brain/tools/test_common.py` both pass, including the three new test cases.
**Dependencies:** Task 4.

### Task 6: Delete the workspace `references.md`
**Intent:** Remove the live register file from `.aib_memory/`.
**Inputs:** `.aib_memory/references.md`.
**Outputs:** File deleted.
**External Interfaces:** Filesystem (git-tracked deletion).
**Environment & Configuration:** N/A.
**Procedure:**
1. Delete `.aib_memory/references.md` from the workspace.
**Done Criteria:** File no longer exists; subsequent `initialize.py` re-runs do not recreate it.
**Dependencies:** Task 1, Task 4.

### Task 7: Automated test execution
**Intent:** Verify all Success Criteria are testable and verified by the suite.
**Inputs:** Updated codebase.
**Outputs:** Green test run.
**External Interfaces:** pytest.
**Environment & Configuration:** `.venv` activated.
**Procedure:**
1. Run `python -m pytest tests/`.
2. Run `python -m pytest .aib_brain/tools/test_common.py`.
3. Run a workspace-wide grep for `references.md` and confirm matches are confined to historical archives and the active request artifacts.
4. Run `python .aib_brain/tools/initialize.py --workspace <tmp_dir>` against a temporary workspace clone (without `.aib_memory/`) and verify `references.md` is not created.
**Done Criteria:** All commands exit 0; grep result matches SC-3 expectation.
**Dependencies:** Tasks 1–6.

### Task 8: Refresh `context.md` and append curated changelog bullets
**Intent:** Regenerate `.aib_memory/context.md` and document user-visible changes.
**Inputs:** `.aib_brain/prompts/aib-context.md` (post-edit), `logs/next_version_changes.md`.
**Outputs:** Updated `.aib_memory/context.md`; appended bullets in `logs/next_version_changes.md`.
**External Interfaces:** None.
**Environment & Configuration:** N/A.
**Procedure:**
1. Execute `aib-context.md` to fully replace `.aib_memory/context.md` (per its Phase 5 contract).
2. Append curated bullets to `logs/next_version_changes.md` per the `instructions.md` directive (e.g., "- Remove `.aib_memory/references.md` register; prompts now read `context.md` directly and `instructions.md` for extras.").
**Done Criteria:** `context.md` contains no `references.md` mentions; `logs/next_version_changes.md` has at least one new bullet.
**Dependencies:** Tasks 1–7.

## Documentation

- .aib_memory/context.md (ref_id: N/A) — Regenerate via `aib-context.md` so the register list, data architecture, and module breakdown drop `references.md`.

- .aib_brain/Concepts.md (ref_id: N/A) — Remove `references.md schema (normative)` section, REF-0001/REF-0002 seeding rules, and the matrix/initialize references.

- .aib_brain/conventions/request-convention.md (ref_id: N/A) — Update Plan rule and Internal Review wording to drop `references.md`.

- .aib_brain/conventions/implementation-convention.md (ref_id: N/A) — Drop `references.md` example mentions.

- logs/next_version_changes.md (ref_id: N/A) — Append curated bullets describing the removal and the new explicit `context.md` reads in prompts.

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| .aib_memory/references.md | Deleted | Register no longer exists. |
| .aib_brain/templates/references-template.md | Deleted | Seed template no longer needed. |
| .aib_brain/conventions/references-convention.md | Deleted | Convention no longer applicable. |
| .aib_brain/tools/initialize.py | Modified | Remove `seed_references_from_product_doc` import, the `references.md` seeding block, and the `--force` documentation referring to it; update the upgrade summary print line. Add `_warn_about_legacy_references(memory_root)` helper invoked from `_run_upgrade` between Step 2 (archive copy) and Step 3 (delete non-archive content) to surface a console warning when the legacy `references.md` contains rows beyond the two defaults; helper is informational and MUST NOT raise. |
| .aib_brain/tools/common.py | Modified | Remove `references_path()`, `seed_references_from_product_doc()`, `parse_product_documentation_requirements()`, `resolve_product_documentation_path()`, `RequirementRef`, `REQ_HEADING_PATTERN`, `LOCATION_PATTERN`, and `sanitize_location_to_path()` if no other callers remain. |
| .aib_brain/tools/test_common.py | Modified | Remove the references.md skip-if-exists test (P28) and any helpers that seed `references-template.md`. |
| .aib_brain/prompts/aib-analysis.md | Modified | Drop `references.md` from inputs/required-read; remove `Concepts.md` from inputs (not actively used); add explicit `context.md` read step; rephrase `## Plan` and `## Documentation` rules to reference `context.md` and `instructions.md` instead of `references.md`. |
| .aib_brain/prompts/aib-implement.md | Modified | Drop `references.md` read step and the `edit_allowed=Y` gate; rephrase product-doc convention preflight to refer directly to `context.md` and `context-convention.md`; add explicit `context.md` read step; remove `Concepts.md` reference if not actively used. |
| .aib_brain/prompts/aib-context.md | Modified | Remove `references.md`-driven Phase 1 product-doc read set; treat `context.md` synthesis as based purely on workspace scan plus `instructions.md`-listed extras (if any). |
| .aib_brain/conventions/request-convention.md | Modified | Replace `references.md` mentions in `## Plan` and `## Documentation` and `## Internal Review` with `context.md` and `instructions.md`. |
| .aib_brain/conventions/implementation-convention.md | Modified | Update example entry blocks to no longer mention `references.md`. |
| .aib_brain/conventions/analysis-convention.md | Read-only dependency | Verify no `references.md` mentions; modify only if found. |
| .aib_brain/conventions/context-convention.md | Read-only dependency | Verify the convention does not depend on `references.md`. |
| .aib_brain/Concepts.md | Modified | Remove `references.md` schema section, REF-0001/REF-0002 seeding rules, and `references.md` mentions in the action contract matrix and initialize action. |
| tests/test_initialize.py | Modified | Remove assertions checking for `references.md` creation in standard, `--upgrade`, and `--force` flows. Add three new test cases covering the upgrade-time legacy `references.md` warning: extra-row warning emitted, default-only run silent, malformed-legacy-table tolerated with explicit warning line. |
| .aib_memory/context.md | Modified | Regenerated by `aib-context.md` final step; removes `references.md` from product structure. |
| logs/next_version_changes.md | Modified | Append curated bullets per the workspace `instructions.md` directive. |

## Internal Review of Request and Product Docs

- OK: `.aib_memory/context.md` — accurately reflects the current `references.md` design; will be regenerated.

- OK: `.aib_brain/Concepts.md` — contains the `references.md` schema in section "references.md schema (normative)" and seeding rules; identified for removal.

- Cross-ref issue: `.aib_brain/prompts/aib-analysis.md` inputs list `.aib_brain/Concepts.md` but the prompt body never reads or branches on its content; safe to remove.

- Cross-ref issue: `.aib_brain/prompts/aib-implement.md` instructs reading `Concepts.md` "for normative lifecycle and safety rules" but the same lifecycle/safety rules are already enforced by `Safety` section of the prompt and by tool scripts (`close-request.py`, `move-request-artifacts.py`); reading `Concepts.md` is not strictly required for correct execution.

- Missing info: `.aib_brain/conventions/references-convention.md` references seeding from `Product_Documentation.md`, but `Product_Documentation.md` does not exist in the workspace; the seeding code falls back to the static template — confirms the register is effectively static and a candidate for removal.

- OK: `.aib_brain/conventions/context-convention.md` — does not require modification beyond removing any incidental `references.md` mention.

## Goal
Rename `.aib_brain/tools/reverse-engineer.py` to a filename that accurately reflects its actual behavior (deterministic workspace file inventory emission), and update all workspace references so behavior remains unchanged.

## Background
The current script name suggests a broad reverse-engineering action, while the implementation outputs a JSON Lines inventory of workspace files. This naming mismatch can create confusion for maintainers and readers of prompts/tests that refer to the helper.

## Scope
- Rename the helper script file under `.aib_brain/tools/` to a more behavior-aligned name.

- Update all direct path/name references to that script in prompts, tests, and context documentation files in this repository.

- Preserve script behavior, CLI arguments, output format, and test intent while adapting references to the new filename.

## Out of scope
- Changing the script's runtime logic, output schema, or command-line interface semantics.
- Introducing new menu actions or changing request lifecycle workflows.

## Constraints
- Keep behavior backward-compatible at functional level; this request is naming/refactoring focused.
- Follow existing repository conventions and deterministic tooling expectations.
- Maintain Python 3.10+ standard-library compatibility.

## Success criteria
- The script exists under a new, behavior-accurate filename in `.aib_brain/tools/`.
- No remaining workspace references point to the old script filename in active source/docs/tests (excluding historical archives/log snapshots).
- Relevant tests referencing the renamed script are updated and pass.

## Assumptions
- A1: The preferred renamed helper filename will be `.aib_brain/tools/file-inventory.py` because it directly describes the script's emitted artifact.
	- Risk if false: Rework may be needed if maintainers choose a different canonical name during implementation.

- A2: Historical archives under `.aib_memory/archives/` are not part of active implementation scope and may retain old-name references.
	- Risk if false: Attempting full historical rewrites will create unnecessary noise and possible audit-history drift.

- A3: The helper script behavior (arguments and JSONL output contract) must remain unchanged.
	- Risk if false: A behavioral change would exceed request scope and may break downstream prompt expectations.

## Plan
### Task 1: Baseline Reference Map
**Intent:** Build a deterministic baseline of active-file references to the old helper filename.
**Outputs:** `tests/test_reverse_engineer.py` and `.aib_brain/prompts/aib-context.md` identified as direct update targets; reference-check output in terminal.
**Procedure:**
1. Run `rg "reverse-engineer.py" .aib_brain tests .aib_memory/context.md` from workspace root; expected output location: terminal stdout list of matching files/lines.
2. Review `.aib_brain/prompts/aib-context.md` and `tests/test_reverse_engineer.py` for exact path literals requiring rename alignment.
3. Review `.aib_memory/context.md` sections that explicitly mention `.aib_brain/tools/reverse-engineer.py` for documentation consistency updates.
**Done Criteria:** A concrete, finite list of active files and exact occurrences to update is produced.
**Dependencies:** External: ripgrep availability (or PowerShell Select-String fallback).
**Risk Notes:** If scan scope accidentally includes archives as active targets, implementation noise can increase.

### Task 2: Apply File Rename And Path Updates
**Intent:** Rename the helper script and update hardcoded references while preserving behavior.
**Outputs:** `.aib_brain/tools/file-inventory.py`, updated `.aib_brain/prompts/aib-context.md`, updated `tests/test_reverse_engineer.py`, and updated `.aib_brain/tools/test_common.py` if filename assertion exists.
**Procedure:**
1. Rename `.aib_brain/tools/reverse-engineer.py` to `.aib_brain/tools/file-inventory.py` using a filesystem move command.
2. Update `.aib_brain/prompts/aib-context.md` path references from the old helper filename to `.aib_brain/tools/file-inventory.py`.
3. Update `tests/test_reverse_engineer.py` import path literal and any filename assertions to the new helper filename.
4. Update `.aib_brain/tools/test_common.py` assertions that include `reverse-engineer.py` where they refer to exclusions or inventory helper naming.
5. Confirm no behavior logic changes were introduced in `.aib_brain/tools/file-inventory.py` beyond filename/path-sensitive text.
**Done Criteria:** New helper filename is in place and all targeted active references are updated consistently.
**Dependencies:** Task 1.
**Risk Notes:** Missing one hardcoded literal will produce late test failures despite an apparently successful rename.

### Task 3: Execute Automated Validation
**Intent:** Validate that rename refactor is behavior-preserving and all success criteria are testable.
**Outputs:** Passing test results in terminal; optional temporary JSONL output file for parity check.
**Procedure:**
1. Run the renamed helper `.aib_brain/tools/file-inventory.py` with `--workspace . --max-files 3 --output .aib_memory/logs/inventory-smoke.jsonl`; expected output location: `.aib_memory/logs/inventory-smoke.jsonl`.
2. Run `pytest tests/test_reverse_engineer.py`; expected output location: terminal pytest report.
3. Run `pytest tests/test_analysis_prompt_structure.py tests/test_instructions_md.py`; expected output location: terminal pytest report.
4. Run `rg "reverse-engineer.py" .aib_brain tests .aib_memory/context.md`; expected output location: terminal stdout confirming intended active-reference cleanup.
**Done Criteria:** Smoke output is produced, all selected tests pass, and old-name matches are cleared from intended active targets.
**Dependencies:** Task 2.
**Risk Notes:** If tests rely on old fixture naming, rename-side test data may require small assertion updates.

### Task 4: Update Context And Documentation Artifacts
**Intent:** Keep active documentation synchronized with the renamed helper to prevent future drift.
**Outputs:** Updated `.aib_memory/context.md` and verified documentation consistency with prompt references.
**Procedure:**
1. In `.aib_memory/context.md`, replace active technical references to `.aib_brain/tools/reverse-engineer.py` with `.aib_brain/tools/file-inventory.py`; acceptance test: no old-name matches remain in `.aib_memory/context.md`.
2. In `.aib_memory/context.md`, update descriptive text where needed to keep wording aligned with "file inventory" terminology; acceptance test: helper description still states deterministic JSONL inventory emission.
3. In `.aib_brain/prompts/aib-context.md`, ensure optional helper guidance references `.aib_brain/tools/file-inventory.py`; acceptance test: prompt contains only new helper path.
4. Re-run a scoped search `rg "reverse-engineer.py" .aib_memory/context.md .aib_brain/prompts/aib-context.md`; expected output location: terminal stdout showing zero matches in those files.
**Done Criteria:** Active documentation files are internally consistent with the new helper filename and behavior description.
**Dependencies:** Task 2.
**Risk Notes:** Partial doc updates can cause future requests to reintroduce old names.

## Documentation
- .aib_memory/context.md — update active product-context references and terminology to the renamed helper path.
- .aib_brain/prompts/aib-context.md — update optional helper invocation path to the renamed script filename.

## Questions & Decisions

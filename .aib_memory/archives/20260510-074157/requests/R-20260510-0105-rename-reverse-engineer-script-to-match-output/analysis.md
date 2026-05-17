## Executive Summary
- Request ID: R-20260510-0105.

- Request title: Rename reverse-engineer script to match output.

- Purpose: align helper script naming with its actual behavior (deterministic JSONL workspace file inventory) to reduce semantic drift between code and documentation.

- Current input asks for reference discovery and a rename decision; the workspace contains direct references in prompt guidance, tests, and context documentation.

- No active attachments were present beyond `.gitkeep`; no binary attachment handling was needed.

- Scope is feasible as a focused refactor (file rename + reference updates) with moderate regression risk centered on hardcoded filename references in tests.

- The selected analysis assumption is to rename `.aib_brain/tools/reverse-engineer.py` to `.aib_brain/tools/file-inventory.py`.

- Key risks: missed path references in context docs/tests, breakage in dynamic imports in `tests/test_reverse_engineer.py`, and stale historical wording in active product context.

- During this run, `request-R-20260510-0105.md` was updated in sections: `## Assumptions`, `## Plan`, and `## Documentation`.

## Domain Knowledge Essentials
- Reverse engineering (in AIB context): extracting factual workspace structure and behavior into machine-readable inventory, not reconstructing architecture intent.

- JSONL (JSON Lines): a line-delimited JSON format where each line is one JSON object; used for deterministic large-file processing.

- Request lifecycle artifact: an active request uses ID-suffixed artifacts at `.aib_memory/` root and is later moved to request folder on closure.

- Impacted personas:
  - Maintainer: needs clear helper naming to reduce onboarding confusion.
  - Contributor: relies on path-stable helper invocation in tests and prompts.
  - Reviewer: validates refactor-only intent without behavior change.

- Business process touched: analysis-to-implementation transition quality. A clearer filename lowers cognitive load and reduces accidental misuse.

- Relevant acceptance impact:
  - Success depends on semantic consistency (name matches behavior), not new functionality.
  - Request acceptance requires no orphan references to the old filename in active source/docs/tests.

## Technical Knowledge & Terms
- `.aib_brain/tools/reverse-engineer.py`: Python helper that walks workspace files, applies exclusion rules, and emits sorted JSONL records.

- `tests/test_reverse_engineer.py`: unit suite using `importlib.util.spec_from_file_location` with a hardcoded script path.

- `.aib_brain/prompts/aib-context.md`: prompt guidance that optionally points to this helper script path.

- `.aib_memory/context.md`: synthesized product context that currently documents the old helper filename.

- Deterministic output: stable sort by `path` and predictable newline-delimited JSON output, required for reproducible context generation.

- Non-functional constraints:
  - Python standard library only.
  - Preserve CLI arguments (`--workspace`, `--output`, `--exclude-dir`, `--max-files`).
  - Keep idempotent behavior under repeated invocation.

- Evidence log:
  - Evidence: helper script docstring and code show pure file inventory output. Implication: current filename can be made more behavior-specific without changing logic.
  - Evidence: grep hits in tests and prompts show hardcoded filename references. Implication: rename requires coordinated path updates to avoid test/runtime failures.
  - Evidence: context artifact includes multiple old-name mentions. Implication: documentation update task is mandatory for consistency.

## Research Results
- Pattern scan findings:
  - Existing AIB scripts usually use behavior-explicit names (`create-request.py`, `close-request.py`, `move-request-artifacts.py`), favoring action/result clarity.
  - Current helper filename is comparatively broad and can be interpreted as a full workflow command rather than a narrow inventory emitter.
  - Previous archived requests repeatedly describe this helper as a JSONL inventory tool, confirming long-standing naming ambiguity.

- Files Read:
  - `.aib_brain/prompts/aib-analysis.md`
  - `.aib_memory/instructions.md`
  - `.aib_memory/requests_register.md`
  - `.aib_memory/input.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_memory/context.md`
  - `.aib_brain/tools/reverse-engineer.py`
  - `.aib_brain/prompts/aib-context.md`
  - `tests/test_reverse_engineer.py`
  - `.aib_brain/tools/test_common.py`

- Risks identified:
  - Missed reference updates could leave hidden failures in path-based tests.
  - Overly aggressive search/replace could mutate historical archives unnecessarily.
  - Name choice might still be interpreted too broadly if not mapped to JSONL semantics in docs.

## External Benchmarking
- Benchmark 1: Python tooling convention in widely used CLIs favors intent-descriptive filenames (for example, `generate-*`, `scan-*`, `list-*`) to match observable behavior.
  - Takeaway: behavior-specific names reduce contributor misinterpretation during maintenance.
  - Applicability: high; this request is exactly a naming-clarity correction.
  - Decision: adopt this pattern by using an output-oriented helper filename.

- Benchmark 2: Documentation-driven engineering workflows commonly separate "inventory collection" from "analysis/synthesis" phases.
  - Takeaway: naming artifacts by pipeline stage improves traceability and easier debugging.
  - Applicability: high; AIB already distinguishes helper scripts from prompts.
  - Decision: adapt by naming the script for inventory production, not reverse-engineering as a broad concept.

- Benchmark 3: Refactor safety practice recommends preserving module behavior and updating all path-bound tests during file renames.
  - Takeaway: automated tests should verify both import resolution and output invariance after rename.
  - Applicability: high; the suite imports by exact filename.
  - Decision: include explicit automated test task and idempotency checks in plan/testing.

## Minimal Spikes and Experiments
- **Spike: Reference surface estimation**
  - Hypothesis: The old filename is referenced in multiple active files and cannot be safely renamed without coordinated edits.
  - Approach: Workspace grep scan for `reverse-engineer.py` across active sources and tests.
  - Outcome: Direct hits found in prompt guidance, tests, helper tests, and active context artifact.
  - Conclusion: Rename is feasible but must be executed as a multi-file consistency update.

- **Spike: Attachment-input impact**
  - Hypothesis: Attachment staging may add hidden request constraints.
  - Approach: Flat scan of `.aib_memory/attachments/`.
  - Outcome: Only `.gitkeep` exists.
  - Conclusion: No additional constraints from attachments.

## AI Copilot Suggestions
- Observation: The request is appropriately narrow, but the exact target filename is not explicitly chosen.
  - Actionable suggestion: Standardize on one behavior-explicit name before implementation and record it as an assumption to avoid partial rename churn.

- Observation: The biggest implementation risk is stale references in tests and active context documentation, not script logic.
  - Actionable suggestion: Treat path-reference updates as first-class outputs and gate completion on grep-based absence checks for the old filename in active files.

- Observation: Historical archives contain many old-name mentions and are not implementation targets.
  - Actionable suggestion: Restrict edits to active code/docs scope to prevent unnecessary large diffs and preserve audit history.

- Observation: The request is slightly smaller than typical refactor requests because runtime behavior remains unchanged and this is largely a consistency update.
  - Actionable suggestion: Keep the implementation slice minimal: rename file, update references, validate tests, and refresh core context documentation.

## Testing
- T1 — File rename existence: Verify old helper path `.aib_brain/tools/reverse-engineer.py` is absent and new helper path exists. Expected outcome: old file missing, new file present.

- T2 — Reference replacement check: Run a scoped search in active source/tests/docs for `reverse-engineer.py`. Expected outcome: no remaining matches in intended active targets; known historical archives may still contain it.

- T3 — Script execution parity: Run the renamed helper with `--max-files 3 --output <temp file>`. Expected outcome: command succeeds and output contains up to three valid JSONL records sorted by `path`.

- T4 — Unit test import path integrity: Run `pytest tests/test_reverse_engineer.py`. Expected outcome: test suite passes using updated filename references.

- T5 — Related regression guard: Run `pytest tests/test_analysis_prompt_structure.py tests/test_instructions_md.py`. Expected outcome: prompt-structure and instruction-preload checks remain passing after reference updates.

- T6 — Success criteria mapping: Verify SC-1 (new filename exists), SC-2 (old-name references removed from active targets), SC-3 (updated tests pass). Expected outcome: all three criteria are objectively satisfied.

- T7 — Re-run idempotency: Re-run the same rename/reference-check workflow without additional edits. Expected outcome: no new diffs are introduced and validation results remain stable.

## Multi-Perspective Stakeholder Review
### Senior Solution Architect
The change is technically low complexity but has non-trivial cross-file coupling because several components use hardcoded filenames. Architectural risk is concentrated in inconsistency, not in runtime logic.

- Feasibility is high because script behavior is self-contained.
- Design integrity improves if naming reflects single responsibility (inventory emission).
- Architectural risk is mostly reference drift across prompt/docs/tests.

### Product Owner
The request provides clear user value by reducing ambiguity in tool naming and does not introduce feature creep. Success criteria are measurable and align with maintainability outcomes.

- Business value: improved clarity for developers and reviewers.
- Scope is crisp if constrained to rename plus reference alignment.
- Acceptance criteria should remain behavior-preserving, not feature-expanding.

### User
For contributors, clearer naming lowers confusion when reading prompts and tests. User-facing behavior should remain unchanged, so friction should be minimal.

- Discoverability improves when filename states actual output purpose.
- No expected workflow interruption if all references are updated.
- Residual friction only appears if old docs remain uncorrected.

### Security Officer
This request does not expand attack surface because it is a rename/refactor with no new external I/O or auth pathways. Security focus is on avoiding accidental broad edits.

- No new credentials, endpoints, or trust boundaries are introduced.
- Ensure no accidental modifications to archival files that could mask audit trails.
- Keep CLI arguments and file-system boundaries unchanged.

### Data Governance Officer
Data semantics remain unchanged: the helper continues to emit file metadata inventory. Governance impact is documentation lineage consistency across active artifacts.

- Data lineage clarity improves when helper naming matches produced data artifact.
- Retention/classification behavior is unchanged.
- Compliance risk is low if context documentation is updated in step with code rename.

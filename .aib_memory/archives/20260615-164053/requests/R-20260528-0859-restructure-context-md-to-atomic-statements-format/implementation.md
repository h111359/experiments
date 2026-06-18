Files considered:
- `.aib_memory/plan-R-20260528-0859.md`
- `.aib_memory/context.md`
- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/prompts/aib-refresh-context.md`
- `.aib_brain/prompts/aib-analyze.md`
- `tests/test_context_formatting_rules.py`

## Implementation Log

### Entry 2026-05-28 09:45

#### Scope

Restructure the AIB knowledge representation model by replacing the prose-based `context.md` format with an atomic statement format, creating supporting CRUD tooling, updating the context convention, and modifying prompts to integrate with the new format.

#### Changes

- Created `.aib_brain/tools/hash-text.py` — tool that computes 8-character truncated SHA-256 hex hashes from input text.
- Created `.aib_brain/tools/edit-context.py` — CRUD tool for atomic statements in `context.md` supporting select, insert, and delete operations with uniqueness validation.
- Rewrote `.aib_brain/conventions/context-convention.md` to define the new 3-section structure (Product Identity, Statements with 22 subsections, Workspace File Inventory) and atomic statement format with 9 type letters and uniqueness invariant.
- Modified `.aib_brain/prompts/aib-refresh-context.md` to add format detection (old vs new), old-to-new conversion logic, atomic statement synthesis, and three enrichment verification passes (analysis decisions, plan results, modified files).
- Modified `.aib_brain/prompts/aib-analyze.md` S09 to include a mandatory context-update task directive in generated plans.
- Rewrote `tests/test_context_formatting_rules.py` to validate the new atomic statement format, 3-section structure, 22 subsections, statement types, and uniqueness invariant.
- Converted `.aib_memory/context.md` from old 12-section prose format to new atomic statement format.
- Updated `.aib_brain/README.md` folder structure to list individual tool scripts including new `hash-text.py` and `edit-context.py`.
- Created `logs/next_version_changes.md` with curated change bullets.

#### Tests

- unit: `tests/test_context_formatting_rules.py` — 13 tests pass (validates convention structure, prompt references, atomic format rules).
- unit: `tests/test_tools_common.py` — all tests pass (no regressions in shared tool utilities).
- unit: `tests/test_semver_workflow_structure.py` — all tests pass (no regressions).
- integration: `python .aib_brain/tools/hash-text.py "The system must download only files that are new."` — outputs `8a86981d` (8-char hex), exit 0.
- integration: `python .aib_brain/tools/hash-text.py` (no args) — prints usage to stderr, exit 1.
- integration: `python .aib_brain/tools/edit-context.py --operation select --area PO --type N --hash 00000000 --workspace .` — correctly reports not found, exit 1.
- regression: 11 pre-existing failures in `test_analysis_prompt_structure.py` confirmed unrelated to this change (test content that was never in `aib-analyze.md`).

#### Outcome

Successful implementation. All 7 plan tasks completed. The atomic statement format is fully operational with tool support, convention definition, and prompt integration. Context.md has been converted to the new format.

#### Evidence

- Path: `.aib_brain/tools/hash-text.py`
- Path: `.aib_brain/tools/edit-context.py`
- Path: `.aib_brain/conventions/context-convention.md`
- Path: `.aib_brain/prompts/aib-refresh-context.md`
- Path: `.aib_brain/prompts/aib-analyze.md`
- Path: `tests/test_context_formatting_rules.py`
- Path: `.aib_memory/context.md`

#### Notes (Optional)

The 11 pre-existing test failures in `test_analysis_prompt_structure.py` test for specific text strings (e.g., "Input Interpretation", "deferred-creation", "Appendix A" references in GC-02) that do not exist in `aib-analyze.md` and were failing before this implementation. These are not regressions from this request.

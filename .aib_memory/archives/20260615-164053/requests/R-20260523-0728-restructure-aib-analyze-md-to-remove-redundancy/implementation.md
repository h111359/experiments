Files taken into consideration:
- `.aib_memory/plan-R-20260523-0728.md` — active plan (authoritative scope source)
- `.aib_memory/context.md` — workspace product context
- `.aib_brain/prompts/aib-analyze.md` — primary target file for restructuring
- `.aib_brain/conventions/analysis-convention.md` — cross-reference update target
- `tests/test_analysis_prompt_structure.py` — test file with stale assertion to remove

## Implementation Log

### Entry 2026-05-23 10:30

#### Scope
Restructured `.aib_brain/prompts/aib-analyze.md` to eliminate content redundancy and enforce separation of concerns. Removed GC-03 and associated "Q-blocks first cycle only" statements, consolidated analysis output rules into step 5.5, consolidated plan output rules into step 5.9, restricted section 6 to Q-block specification (renumbered from 6.3 to direct sub-sections 6.1–6.3), inlined section 7 sub-flows into their invocation steps (5.1 and 5.4), and deleted section 7. Updated cross-references in `analysis-convention.md` and removed a stale test assertion from `tests/test_analysis_prompt_structure.py`. Updated `context.md` to reflect the new prompt structure.

#### Changes
- Removed GC-03 bullet ("Q-blocks in first cycle only") from `aib-analyze.md` section 3.1 Global Constraints.
- Removed "One cycle of Q&A is assumed..." sentence from Q-block Generation sub-section in `aib-analyze.md`.
- Removed "No new Q-blocks are generated when re-running after answers..." sentence from Answer Application Sub-flow step 4 in `aib-analyze.md`.
- Replaced step 5.5 single-line generation rule with inline content: full-replace rule referencing `analysis-convention.md` sections 3 and 4, mandatory section list, and trigger guard.
- Deleted section 6.1 (Analysis Document) from `aib-analyze.md`.
- Expanded step 5.9 body with full plan output rules (Plan section deferral stub, Decisions append rules, `plan-convention.md` reference); removed single-line delegation to "section 6.2".
- Deleted section 6.2 (plan.md Updates) from `aib-analyze.md`.
- Promoted `### 6.3 Q-block Rules` to `## 6. Q-block Rules` (removed `## 6. Output Specifications` container).
- Renamed `#### 6.3.1` → `### 6.1`, `#### 6.3.2` → `### 6.2`, `#### 6.3.3` → `### 6.3` in `aib-analyze.md`.
- Updated all internal cross-references to `section 6.3` (Classification) → `section 6.2` and to `section 6.3` (generation) → `section 6` or `section 6.3` as appropriate.
- Inlined Auto-Request Creation Branch (formerly section 7.1, steps 1–6) into step 5.1 of `aib-analyze.md`.
- Inlined Answer Application Sub-flow (formerly section 7.2, steps 0–4) into step 5.4 of `aib-analyze.md`.
- Deleted `## 7. Sub-flows` (including 7.1, 7.2, 7.3) from `aib-analyze.md`; renumbered Completion Confirmation to `## 7.`.
- Updated GC-02 to reference "Auto-Request Creation Branch in step 1 (finalize-input.py invocation step)".
- Updated GC-07 to reference "the Auto-Request Creation Branch in step 1 (create-request.py and finalize-input.py invocations) and 5.6.2".
- Updated step 5.3.1 reference from "section 7.2" to "the Answer Application Sub-flow in step 4".
- Updated step 5.6 trigger guard to reference "step 1" instead of "section 7.1".
- Updated `analysis-convention.md` section 6 cross-reference from "section 6.3" to "section 6.3 (Q-block Generation)".
- Removed `TestPlanSchemaFieldsInAnalysisPrompt.test_outputs_field_present` from `tests/test_analysis_prompt_structure.py`.
- Updated `context.md` entries for "Analysis workflow structure", "Analysis Q-block rules", and "Answer Application Sub-flow".
- Updated `.aib_brain/README.md` to remove stale "One Q&A cycle" statement (no longer accurate without GC-03).
- Appended implementation change bullets to `logs/next_version_changes.md`.

#### Tests
- Unit: `python -m pytest tests/test_analysis_prompt_structure.py -v` — 52 passed, 0 failed.
- Full suite: `python -m pytest tests/ -v` — 302 passed, 4 subtests passed, 0 failed.

#### Outcome
All tasks completed successfully. All 302 tests pass. The `aib-analyze.md` prompt no longer contains section 7, section 6.1, section 6.2, or GC-03. Section 6 now directly contains Q-block rules (6.1–6.3). Sub-flows are inlined at their invocation points. No test regressions introduced.

#### Evidence
- `python -m pytest tests/test_analysis_prompt_structure.py -v`: 52 passed in 0.23s.
- `python -m pytest tests/ -v`: 302 passed, 4 subtests passed in 47.94s.

#### Notes (Optional)
The `test_overview_referenced_in_prompt` test initially failed after Task 2 because section 6.1's explicit section list (`## Overview`, etc.) was removed. Fixed by adding the explicit section list to step 5.5's mandatory structure bullet.

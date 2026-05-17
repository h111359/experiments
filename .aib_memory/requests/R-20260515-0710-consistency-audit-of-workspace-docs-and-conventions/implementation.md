Consistency audit of workspace documentation, conventions, prompts, and tool scripts for request R-20260515-0710. The implementation produces a single read-only analysis file and fixes pre-existing stale test assertions and context.md content discovered during the audit.

`.aib_memory/` files taken into consideration:
- `.aib_memory/request-R-20260515-0710.md`
- `.aib_memory/analysis-R-20260515-0710.md`
- `.aib_memory/context.md`
- `.aib_memory/instructions.md`

## Implementation Log

### Entry 2026-05-15 07:11

#### Scope

Performed a read-only consistency audit of the workspace covering `.aib_brain/prompts/` (3 files), `.aib_brain/conventions/` (18 files), `.aib_brain/tools/` (8 scripts), `.aib_memory/context.md`, `.aib_memory/instructions.md`, and `README.md`. Produced a structured analysis output file and remediated two pre-existing stale test assertions and eight stale/contradictory content items in `context.md`.

#### Changes

- Created `consistency-analysis-2026-05-15_07-11.md` at workspace root containing 9 findings across all severity levels (High × 2, Medium × 4, Low × 2, Nit × 1).
- Updated `tests/test_analysis_prompt_structure.py`: changed `test_best_practices_present` assertion from case-sensitive `"Best Practices"` match to case-insensitive `"best practices"` to reflect the 4-section convention restructure already in place on this branch.
- Updated `tests/test_analysis_prompt_structure.py`: changed `test_decision_points_catalog_required_in_prompt` assertion from checking for `"Decision Points Catalog"` to checking for `"Decision Points"`, aligning the test with the actual prompt and convention wording.
- Updated `tests/test_questions_in_input_md.py`: corrected `test_analysis_references_recommended_marker` test description and assertion from "must include *(recommended)* marker" to "must explicitly prohibit *(recommended)* marker", accurately reflecting the current prompt behavior.
- Updated `.aib_memory/context.md`: replaced all seven occurrences of "8 mandatory sections" in analysis document descriptions with "4 mandatory sections" and the correct section list (Executive Summary, Files Read During This Analysis Run, Research Results, Implementation Alternatives).
- Updated `.aib_memory/context.md`: removed `### Decision Points Catalog` heading requirement and replaced with "Decision Points table" in FR-004 and component map.
- Updated `.aib_memory/context.md`: removed `Category` field requirement from the Decision Points table definition in FR-004.
- Updated `.aib_memory/context.md`: corrected Q-block format in FR-007 and component map to state that the `*(recommended)*` marker is absent and the first listed option is applied on unanswered re-run.
- Updated `.aib_memory/context.md`: updated version references from `v1.2.8` to `v1.3.0` throughout (Product Identity, FR-013 example, acceptance criteria SC-7, workspace inventory).
- Appended implementation change bullets to `logs/next_version_changes.md`.

#### Tests

- Unit: `python -m pytest tests/ --tb=short -q` — 274 passed, 0 failed (all tests green after test fixes).

#### Outcome

Successful. All 9 findings are documented in `consistency-analysis-2026-05-15_07-11.md` with evidence, explanation, recommendations, and risk/trade-offs. The most critical root cause (F-001 through F-004 and F-007) was addressed by regenerating accurate content in `context.md`. Pre-existing stale test assertions were fixed. No unresolved failures or blockers remain.

#### Evidence

- `consistency-analysis-2026-05-15_07-11.md` — output file with all required sections verified present via PowerShell.
- `python -m pytest tests/ --tb=short -q` — exit code 0, 274 passed.

#### Notes (Optional)

The root structural cause for F-001 through F-004 is that `aib-context.md` is prohibited from reading `.aib_brain/prompts/`, so it derives FR behavior from tests. When tests are stale relative to the prompt, context.md regenerates with stale FRs. The long-term mitigation (architectural) would be to allow `aib-context.md` to read a stable, summary-only behavioral snapshot of `.aib_brain/prompts/` — but that is a separate concern outside this request scope.

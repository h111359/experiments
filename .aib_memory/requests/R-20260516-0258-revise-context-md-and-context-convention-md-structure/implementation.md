Implementation log for request R-20260516-0258: Revise context.md and context-convention.md structure.

Files read during this implementation run:
- `.aib_memory/plan-R-20260516-0258.md`
- `.aib_memory/context.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/prompts/aib-context.md`
- `.aib_brain/prompts/aib-implement.md`
- `.aib_brain/conventions/implementation-convention.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `tests/test_context_formatting_rules.py`
- `.aib_memory/instructions.md`

## Implementation Log

### Entry 2026-05-16 05:30

#### Scope

Restructured `context-convention.md` and `context.md` to the new 12-section mandatory order (Tasks 1–2); added a Phase 6 post-write validation step to `aib-context.md` (Task 3); replaced the redundant Phase 4 formatting block in `aib-context.md` with a single reference to the convention (Task 4); updated `test_context_formatting_rules.py` to match the new prompt structure.

#### Changes

- Updated `.aib_brain/conventions/context-convention.md` mandatory section list to 12-section order: Product Identity, Domain Knowledge, Concepts, Constraints & Assumptions, Requirements, Architecture & Decisions, Technical Design, Data Architecture, Security & Compliance, Operations, Development Practices, Workspace File Inventory.
- Renamed Section 2 from "Business Context" to "Domain Knowledge" in `context-convention.md`; added Glossary absorption guidance (no standalone Glossary section at document level).
- Added new Section 3 "Concepts" content guidance to `context-convention.md` specifying definition-list format (`**Concept name**: one-sentence definition`, sorted alphabetically).
- Added Section 4 "Constraints & Assumptions" content guidance (moved from former Section 10) with added "no conceptual entries" MUST NOT rule.
- Renamed former Section 3 to Section 5 "Requirements" in `context-convention.md`; replaced "MUST NOT reproduce verbatim" with "MUST list all requirements verbatim with full detail — no summarization".
- Renamed former Section 4 to Section 6 "Architecture & Decisions" in `context-convention.md`; replaced "top three to five most impactful" with "all architectural decisions".
- Renumbered former Sections 5–9 to 7–11 in `context-convention.md`.
- Removed standalone Section 11 "Glossary" content guidance from `context-convention.md`.
- Updated Section 1 and Section 5 cross-references from "section 5" to "section 7" in `context-convention.md`.
- Renamed `## Business Context` to `## Domain Knowledge` in `.aib_memory/context.md`.
- Inserted `### Glossary` sub-section at end of Domain Knowledge in `context.md` with all former Glossary entries (re-sorted alphabetically; "Curated Change Log" moved to after "Convention File").
- Added new `## Concepts` section at position 3 in `context.md` with intro sentence and four definition-list entries: Determinism, Fail-closed, File-first, Separation of concerns.
- Moved `## Constraints & Assumptions` section to position 4 in `context.md` (before `## Requirements`).
- Renamed `## Requirements Summary` to `## Requirements` in `context.md`.
- Renamed `## Architecture & Key Decisions` to `## Architecture & Decisions` in `context.md`.
- Removed standalone `## Glossary` section from `context.md`.
- Added `## Phase 6 — Post-write Validation` section to `.aib_brain/prompts/aib-context.md` after Phase 5 with six validation steps.
- Replaced "Formatting requirements (MUST enforce for every section):" block in `aib-context.md` Phase 4 with single reference sentence pointing to `context-convention.md` Formatting Rules section.
- Updated three test methods in `tests/test_context_formatting_rules.py` (`test_no_tables_prohibition_in_prompt`, `test_blank_line_requirement_in_prompt`, `test_sentence_limit_enforcement_in_prompt`) to check for the convention reference text instead of the removed inline rules.
- Appended curated change bullets to `logs/next_version_changes.md`.

#### Tests

- Unit/Integration: `python -m pytest tests/ -v --tb=short` — all 286 tests passed (0 failures, 0 errors).
- Structural: verified context.md has exactly 12 `##`-level headings in the correct order per the new convention.
- Structural: verified Phase 6 is present in aib-context.md and Phase 4 no longer contains the duplicated formatting block.
- Structural: verified "MUST NOT appear anywhere in the document", "blank line", "H3", and "MUST NOT exceed two sentences" are all still present in context-convention.md (formatting rules preserved verbatim).

#### Outcome

All four tasks completed successfully. The new 12-section convention structure is in place in both `context-convention.md` and `context.md`. The aib-context.md prompt now references the convention for formatting rules and performs Phase 6 post-write validation. All 286 tests pass.

#### Evidence

- `python -m pytest tests/ -v --tb=short` → 286 passed, 0 failed.
- `Get-Content .aib_memory\context.md | Where-Object { $_ -match "^## " }` → confirmed 12 sections in correct order.
- `Select-String -Path ".aib_brain\prompts\aib-context.md" -Pattern "Phase 6"` → match found at `## Phase 6 — Post-write Validation`.
- `Select-String -Path ".aib_brain\prompts\aib-context.md" -Pattern "Do NOT use Markdown tables anywhere"` → no match (block successfully removed).

#### Notes (Optional)

Curated Change Log entry in `logs/next_version_changes.md` was appended with 9 bullets covering all logical changes from this implementation run. The Glossary entries in `context.md`'s new `### Glossary` sub-section are now in strict alphabetical order (correcting the prior misplacement of "Curated Change Log" after "instructions.md").

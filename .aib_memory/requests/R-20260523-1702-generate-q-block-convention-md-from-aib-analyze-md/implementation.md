Files taken into consideration from `.aib_memory/`:
- `plan-R-20260523-1702.md`
- `context.md`
- `instructions.md`

## Implementation Log

### Entry 2026-05-24 14:30

#### Scope
Extract Q-block format templates and format-level rules from `aib-analyze.md` section 6.3 into a new authoritative convention file `q-block-convention.md`. Update `aib-analyze.md` to reference the new convention. Redirect two tests to read from the convention file. Update `context.md` and `.aib_brain/README.md` to reflect the new file.

#### Changes
- Created `.aib_brain/conventions/q-block-convention.md` with multiple-choice and free-text Q-block format templates, all format-level rules (QID numbering, `Why this matters` line, `*(recommended)*` marker rules), organized into Purpose, Scope & Normative Language, QID Numbering, Multiple-Choice Format, and Free-Text Format sections.
- Removed Q-block format template blocks and format-level rules from `aib-analyze.md` section 6.3; replaced with reference to `q-block-convention.md`; retained both format selection guidance sentences and all behavioral content unchanged.
- Updated `tests/test_questions_in_input_md.py`: `test_analysis_references_why_this_matters` and `test_analysis_references_recommended_marker` now read `q-block-convention.md` instead of `aib-analyze.md`.
- Updated `.aib_memory/context.md` `Analysis Q-block rules` bullet to note `q-block-convention.md` as the authoritative Q-block format source.
- Updated `.aib_brain/README.md` Q&A section to reference `q-block-convention.md` for format definitions.
- Appended change bullets to `logs/next_version_changes.md`.

#### Tests
- Unit/structural: `pytest tests/ -v` — 302 tests passed, 4 subtests passed, 0 failures.

#### Outcome
Successful. All success criteria met. No unresolved test failures or blockers.

#### Evidence
```
=================== 302 passed, 4 subtests passed in 45.78s ===================
```

#### Notes (Optional)
Format selection guidance ("Multiple-choice is preferred when bounded options exist." and "Use free-text only when the answer space is unbounded...") was intentionally kept in `aib-analyze.md` section 6.3 per the plan constraints.

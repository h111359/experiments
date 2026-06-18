Files considered from .aib_memory/:
- plan-R-20260614-0802.md (moved to request folder)
- context.md

## Implementation Log

### Entry 2026-06-14 10:30

#### Scope
Replaced all 22 two-letter area code identifiers with full English names across the AIB context subsystem. Changes propagated from the authoritative definition in context-convention.md through the two Python tool scripts (verify-context.py, edit-context.py), the content file (context.md), and the two test files (test_verify_context.py, test_context_formatting_rules.py). Also corrected two incorrect statements in context.md claiming Git is an AIB runtime dependency, and fixed two statements that referenced stale "area codes" wording. Three pre-existing test failures in test_context_formatting_rules.py and test_questions_in_input_md.py were resolved with minimal fixes as part of the same run.

#### Changes
- Updated `.aib_brain/conventions/context-convention.md`: replaced `### Valid Area Codes (22)` enumeration with full area names, updated section structure rule to reference full names, updated quality gate rule #3, updated Formatting Rules #9 to use normative MUST NOT language, updated Statement Types section to use a Markdown table, updated Pattern compression rule to use natural-language phrasing.
- Updated `.aib_brain/tools/verify-context.py`: replaced `VALID_AREAS` set of 22 two-letter codes with 22 full area name strings; updated error message example to use full names.
- Updated `.aib_brain/tools/edit-context.py`: replaced `VALID_AREAS` set and `AREA_ORDER` list with full area names; updated `_build_area_heading` docstring; updated `--area` argparse help text and error message to reference full names.
- Updated `.aib_memory/context.md`: renamed all 20 present area H2 headings from two-letter codes (PO, CM, DO, CO, BP, FN, TD, TS, NW, DS, DF, PR, UI, SC, OP, DV, DP, DR, OB, DM) to full English names; removed "and Git" from Product Identity paragraph and Technology Stack statement; updated Concepts statement to remove Git runtime dependency claim; updated Data structures and Documentation statements from "area codes" to "area names".
- Updated `tests/test_verify_context.py`: changed VALID_CONTEXT fixture headings `## FN` → `## Functionality` and `## PO` → `## Project overview`; updated `test_invalid_area_heading` target; updated `test_empty_area_section_fails` to use `## Analytics` instead of `## AN`.
- Updated `tests/test_context_formatting_rules.py`: replaced 22 two-letter codes in `expected_areas` list with full area names.
- Updated `.aib_brain/conventions/q-block-convention.md`: added "MUST mark" normative language to the recommendation rule (pre-existing test fix).
- Appended 3 change bullets to `logs/next_version_changes.md`.
- verify-context.py confirmed: 10/10 checks passed.
- Full pytest suite: 332 passed, 4 subtests passed (exit code 0).

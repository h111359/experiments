Implementation record for request R-20260518-1314: Fix user guide to reflect AIB as a product.

Files read during this implementation run:
- `.aib_memory/plan-R-20260518-1314.md`
- `.aib_memory/context.md`
- `.aib_memory/instructions.md`
- `.aib_brain/user_guide.html`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/coding-html-convention.md`
- `.aib_brain/conventions/coding-python-convention.md`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/implementation-convention.md`
- `.aib_brain/README.md`
- `tests/conftest.py`
- `tests/test_instructions_md.py`

## Implementation Log

### Entry 2026-05-18 15:05
#### Scope
Corrected six product-accuracy errors in `.aib_brain/user_guide.html` that conflated the AI_Builder development project with AIB as a general product. Applied changes to Section 2 (prerequisites), Section 9 (folder tree), and Section 11 (glossary). Created automated test file covering all six success criteria.

#### Changes
- Removed `<li><strong>Git</strong> available on PATH (required for CI release bookkeeping).</li>` from Section 2 Prerequisites in `.aib_brain/user_guide.html`.
- Changed README.md annotation in `.aib_brain/` folder tree from "This guide's source of truth" to "Quick-start overview and workspace guide" in `.aib_brain/user_guide.html`.
- Added `user_guide.html ← Self-contained interactive user guide (browser-viewable)` entry to the `.aib_brain/` folder tree in `.aib_brain/user_guide.html`.
- Changed `.aib_memory/logs/` description from "Version logs and curated change bullets" to "Tool execution and action logs" in `.aib_brain/user_guide.html`.
- Removed ` targeting <code>main</code>` from the CI glossary entry in Section 11 of `.aib_brain/user_guide.html`.
- Changed VCS glossary entry from "Version Control System (Git in this workspace)" to "Version Control System." in `.aib_brain/user_guide.html`.
- Created `tests/test_user_guide_product_accuracy.py` with six test cases (SC-1 through SC-6) asserting all corrections.
- Appended curated change bullets to `logs/next_version_changes.md`.
- Updated timestamp in `.aib_memory/context.md` (context refresh pass; no content changes as workspace documentation was unchanged).

#### Tests
- unit: `test_sc1_no_git_path_prerequisite` in `tests/test_user_guide_product_accuracy.py` — pass
- unit: `test_sc2_user_guide_html_listed_in_section9` in `tests/test_user_guide_product_accuracy.py` — pass
- unit: `test_sc3_readme_annotation_not_source_of_truth` in `tests/test_user_guide_product_accuracy.py` — pass
- unit: `test_sc4_logs_described_as_tool_execution` in `tests/test_user_guide_product_accuracy.py` — pass
- unit: `test_sc5_ci_glossary_no_branch_reference` in `tests/test_user_guide_product_accuracy.py` — pass
- unit: `test_sc6_vcs_glossary_no_workspace_qualifier` in `tests/test_user_guide_product_accuracy.py` — pass
- regression: full test suite (303 tests) — all pass

#### Outcome
Successful. All six identified product-accuracy errors in user_guide.html corrected. All 303 tests pass including the 6 new product-accuracy tests. No unresolved failures or blockers.

#### Evidence
- Test run result: 303 passed, 4 subtests passed in 13.50s
- `.aib_brain/user_guide.html` updated at lines 383, 623–625, 631, 713, 732
- `tests/test_user_guide_product_accuracy.py` created

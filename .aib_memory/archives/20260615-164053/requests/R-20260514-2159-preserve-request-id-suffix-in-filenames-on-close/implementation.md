Files read from `.aib_memory/` during this implementation run:
- `.aib_memory/instructions.md`
- `.aib_memory/requests_register.md`
- `.aib_memory/request-R-20260514-2159.md`
- `.aib_memory/context.md`

## Implementation Log

### Entry 2026-05-14 22:30
#### Scope
Preserve the request ID suffix in archived artifact filenames when closing a request. Previously, `move-request-artifacts.py` renamed `request-<ID>.md`, `analysis-<ID>.md`, and `UAT_scenarios-<ID>.md` to bare names (`request.md`, `analysis.md`, `UAT_scenarios.md`) upon archival. This change removes the bare-name renaming logic so archived artifacts retain their original ID-suffixed filenames. Convention files (`analysis-convention.md`, `request-convention.md`) and all test assertions in `test_artifact_placement.py` are updated to match the new behavior. `context.md` is regenerated to remove stale bare-name references throughout.

#### Changes
- Updated `.aib_brain/tools/move-request-artifacts.py`: removed `bare_name` variable and replaced `dest = dest_folder / bare_name` with `dest = dest_folder / filename`; updated module-level docstring to reference `request-<ID>.md`, `analysis-<ID>.md`, `UAT_scenarios-<ID>.md`; updated function docstring to describe ID-suffix-preserving behavior.
- Updated `tests/test_artifact_placement.py`: replaced all 9 bare-name assertions (`folder / "request.md"`, `folder / "analysis.md"`, `folder / "UAT_scenarios.md"`) with f-string ID-suffixed equivalents (`folder / f"request-{req_id}.md"`, etc.); updated T6 inline comment from "bare names" to "ID-suffixed names".
- Updated `.aib_brain/conventions/analysis-convention.md`: replaced archived-phase destination `analysis.md (bare name in the subfolder)` with `analysis-<request_id>.md (ID suffix preserved)` in section 3.
- Updated `.aib_brain/conventions/request-convention.md`: replaced archived-phase destination `request.md (bare name in the subfolder)` with `request-<request_id>.md (ID suffix preserved)`; replaced "Only one `request.md` may exist per request folder" with "Only one `request-<request_id>.md` may exist per request folder".
- Updated `.aib_memory/context.md`: updated Move Artifacts Script component, Request Artifacts component, `move-request-artifacts.py` module description, SEQ-003 sequence, Data Storage entries, test strategy description, test inventory description, and preamble timestamp.
- Appended 5 bullets to `logs/next_version_changes.md` describing user-visible changes.

#### Tests
- integration: `tests/test_artifact_placement.py` T1–T7 — all pass (verified via `python -m pytest tests/test_artifact_placement.py -v`).
- integration: full suite `python -m pytest tests/ -v` — 271 passed; 2 pre-existing failures in `tests/test_analysis_prompt_structure.py` (unrelated to this scope: missing "Best Practices" section check in `analysis-convention.md` and missing "Decision Points Catalog" in `aib-analysis.md`); no regressions introduced.

#### Outcome
Successful. All in-scope files updated; archived artifact filenames now preserve the request ID suffix going forward. Pre-existing test failures in `test_analysis_prompt_structure.py` are out of scope for this request (assumption A2 confirmed: no external tooling relies on bare archived names).

#### Evidence
- `.aib_brain/tools/move-request-artifacts.py` — `bare_name` variable removed; `dest = dest_folder / filename`.
- `tests/test_artifact_placement.py` — assertions use `f"request-{req_id}.md"`, `f"analysis-{req_id}.md"`, `f"UAT_scenarios-{req_id}.md"` patterns.
- `logs/next_version_changes.md` — 5 new bullets appended.

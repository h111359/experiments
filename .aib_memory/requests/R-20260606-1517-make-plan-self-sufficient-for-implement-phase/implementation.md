Files consulted:
- `.aib_memory/plan-R-20260606-1517.md`
- `.aib_memory/context.md`
- `.aib_brain/conventions/plan-convention.md`
- `.aib_brain/prompts/aib-analyze.md`
- `.aib_brain/prompts/aib-implement.md`
- `.aib_brain/README.md`
- `tests/test_tools_common.py`
- `tests/test_analysis_prompt_structure.py`
- `.aib_brain/conventions/context-convention.md`
- `.aib_brain/conventions/coding-general-convention.md`
- `.aib_brain/conventions/implementation-convention.md`

## Implementation Log

### Entry 2026-06-06 16:30

#### Scope
Made plan artifact self-sufficient for the implement phase. Removed the context.md read step from aib-implement.md, added an explicit prohibition on reading context.md during implementation, and updated plan-convention.md to mandate self-sufficient plan structure. Updated aib-analyze.md Step 9 to require plans that embed all information needed for execution. Removed Risk notes sub-field from plan-convention.md task schema. Updated README.md plan description and context.md atomic statements to reflect the new behavior. Added five regression tests.

#### Changes
- Removed `#### Risk notes` sub-field from task schema in `.aib_brain/conventions/plan-convention.md`.
- Updated `## Goal` definition in `plan-convention.md` to mandate self-sufficiency: full background, impacted components, no external file needed.
- Added prohibition in `plan-convention.md` Operational Workflow: `implement MUST NOT read .aib_memory/context.md`.
- Updated context update task description in `plan-convention.md` Content Rules to require exact `edit-context.py` invocations with literal arguments.
- Removed Step 4 (`Read .aib_memory/context.md`) from `.aib_brain/prompts/aib-implement.md` and renumbered all subsequent steps (now Steps 1–11).
- Added `MUST NOT read .aib_memory/context.md` bullet to Execution requirements in `aib-implement.md` Rules section.
- Replaced S09.1 in `.aib_brain/prompts/aib-analyze.md` to mandate plan self-sufficiency and remove reference to context.md as a source.
- Replaced S09.2 in `aib-analyze.md` with expanded self-sufficiency requirements including exact `edit-context.py` invocations in context update tasks.
- Updated `plan-<id>.md` row in `.aib_brain/README.md` Request Folder Artifacts table to describe self-sufficient specification.
- Deleted stale DF statement "Analysis generates analysis-REQUEST_ID.md and updates plan-REQUEST_ID.md with Plan and Decisions sections." from `.aib_memory/context.md` (statement was already absent; new DF statement inserted instead).
- Inserted new DF statement into `context.md`: plan generation now described as producing a self-sufficient plan-REQUEST_ID.md.
- Replaced PR statement in `context.md` to note that context.md is not read during implementation.
- Replaced FN statement in `context.md`: MUST generate self-sufficient plan with exact file paths and edit-context.py commands; implement MUST NOT read context.md.
- Verified `context.md` format compliance — 10/10 checks passed.
- Removed `#### Risk notes\nNone.` block from `VALID_PLAN_MD` fixture in `tests/test_tools_common.py`.
- Added new test class `TestPlanSelfSufficiencyAndContextMdProhibition` in `tests/test_analysis_prompt_structure.py` with five regression tests.
- Appended change bullets to `logs/next_version_changes.md`.

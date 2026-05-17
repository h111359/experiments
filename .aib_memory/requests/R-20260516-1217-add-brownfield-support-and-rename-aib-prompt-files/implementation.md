Files taken into consideration: `.aib_memory/plan-R-20260516-1217.md`, `.aib_memory/context.md`, `.aib_memory/instructions.md`.

## Implementation Log

### Entry 2026-05-16 14:00

#### Scope

Renamed `.aib_brain/prompts/aib-analysis.md` to `aib-analyze.md` and `.aib_brain/prompts/aib-context.md` to `aib-refresh-context.md` for consistent action-verb naming. Added a brownfield pre-preflight step (section 0) to `aib-analyze.md` that auto-executes `aib-refresh-context.md` when `context.md` is absent or empty. Updated all workspace references to the renamed files across prompt files, tool scripts, test files, and documentation.

#### Changes

- Renamed `.aib_brain/prompts/aib-analysis.md` → `.aib_brain/prompts/aib-analyze.md` via `git mv`.
- Renamed `.aib_brain/prompts/aib-context.md` → `.aib_brain/prompts/aib-refresh-context.md` via `git mv`.
- Inserted `## 0. Brownfield Pre-Preflight` section into `aib-analyze.md` before `## 1. Objective`; step checks for absent/empty `context.md` and invokes `aib-refresh-context.md` to populate it.
- Updated prompt title line in `aib-analyze.md` from `# Prompt: aib-analysis` to `# Prompt: aib-analyze`.
- Updated three internal self-references in `aib-analyze.md` from `aib-analysis.md` to `aib-analyze.md`.
- Updated prompt title line in `aib-refresh-context.md` from `# Prompt: context` to `# Prompt: aib-refresh-context`.
- Updated `.aib_brain/tools/menu.py`: replaced all six `aib-analysis.md` references in `_GUIDANCE_MESSAGES` with `aib-analyze.md`; replaced context-empty advisory line referencing `aib-context.md` with new wording referencing `aib-analyze.md` and auto-execution.
- Updated `.aib_brain/prompts/aib-implement.md`: replaced `aib-context.md` (step 7) with `aib-refresh-context.md`; replaced `aib-analysis.md` (Auto-Analysis Branch, step 2) with `aib-analyze.md`.
- Updated `.aib_brain/README.md`: replaced all `aib-analysis.md` occurrences with `aib-analyze.md` and all `aib-context.md` occurrences with `aib-refresh-context.md`.
- Updated `tests/test_analysis_prompt_structure.py`: changed `ANALYSIS_PROMPT` path constant from `aib-analysis.md` to `aib-analyze.md`; updated all assertion messages and docstrings.
- Updated `tests/test_context_formatting_rules.py`: changed `CONTEXT_PROMPT` path constant from `aib-context.md` to `aib-refresh-context.md`; updated class docstrings and assertion messages.
- Updated `tests/test_instructions_md.py`: changed `PROMPT_FILES` list entries and path constructions from old filenames to new filenames.
- Updated `tests/test_menu.py`: changed assertion `"aib-context.md" in output` to `"aib-analyze.md" in output`.
- Updated `tests/test_questions_in_input_md.py`: changed all `aib-analysis.md` path constructions and assertion messages to `aib-analyze.md`.
- Updated `.aib_memory/context.md`: replaced all `aib-analysis.md` and `aib-context.md` prompt filename references with new names; updated preamble to reflect `aib-refresh-context.md` as generator.
- Appended six curated change bullets to `logs/next_version_changes.md`.

#### Tests

- Unit tests (pytest): ran `python -m pytest tests/ -v --tb=short` — 286 passed, 0 failed.

#### Outcome

All tasks completed successfully. Both prompt files are tracked under their new names in VCS. The brownfield pre-preflight step is present in `aib-analyze.md`. All workspace references updated. Test suite passes with no failures.

#### Evidence

- `git ls-files .aib_brain/prompts/aib-analyze.md` returns `.aib_brain/prompts/aib-analyze.md`.
- `git ls-files .aib_brain/prompts/aib-analysis.md` returns nothing.
- `git ls-files .aib_brain/prompts/aib-refresh-context.md` returns `.aib_brain/prompts/aib-refresh-context.md`.
- `git ls-files .aib_brain/prompts/aib-context.md` returns nothing.
- `python -m pytest tests/ -v --tb=short`: `286 passed, 4 subtests passed in 9.39s`.

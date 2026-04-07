## Version 1.0.10

### Template ↔ Convention Drift Fixes

- **#1** Removed `implementation-template.md` — convention is the sole source for implementation structure (Scope, Changes, Tests, Outcome, Evidence, Notes).
- **#2** Removed `analysis-template.md` — convention is the sole source for analysis structure with all 13 mandatory sections.
- **#3** Removed `questionnaire-template.md` — convention is the sole source for questionnaire structure (QID system, structured question blocks).
- **#4** Aligned iterations convention column names from `created_at_local`/`closed_at_local` to `created_at`/`closed_at`, matching script output and templates.
- **#5** Removed `summary` column from `requests_register` convention, aligning with template and script output (6 columns).

### Script Correctness & Robustness

- **#6** Aligned timestamp format in conventions to ISO standard (`YYYY-MM-DD HH:MM:SS ±HHMM`), matching `now_iso()` output.
- **#7** Updated `requests_register` convention sort order to ascending by `request_id`, matching `create-request.py` behavior.
- **#8** Removed Request ID injection from `request.md` in `create-request.py` — request ID is already implicit from the folder name.
- **#9** Made `initialize.py` idempotent — skips `requests_register.md` overwrite when file already exists.
- **#10** Changed default `edit_allowed` for seeded references to `Y` — updated references convention, Concepts.md, common.py fallback, and template.

### Prompt Design

- **#11 #12** Documented auto-chaining in Concepts.md: `create-analysis` auto-triggers `create-questionnaire`; `implement` auto-triggers `update-documentation`.
- **#13** Added `Concepts.md` to every prompt's input list — ensures normative lifecycle rules are always available.
- **#14** Added context-window management guidance to all prompts — 80% threshold with prioritization fallback.
- **#15** Fixed formatting errors in `aib-create-plan.md` — removed trailing dashes creating broken list items.

### Convention Gaps & Inconsistencies

- **#16** Renumbered analysis convention sections sequentially (was 1,3,4,5,...; now 1,2,3,4,...).

### Organization & Architecture

- **#22** Moved `Product_Documentation.md` to `.aib_brain/` root as single canonical location; removed workspace-root fallback logic.

### Testing & Quality

- **#25** Added 64 unit tests for Python tools covering markdown table parsing, slugification, regex patterns, timestamp formatting, workspace validation, register resolution, and product doc parsing.

### Workflow & Usability

- **#29** Added 6 prompt-based actions to the interactive menu (Create Analysis, Create Questionnaire, Create Plan, Implement, Reverse Engineer, Update Documentation) with copy/paste chat suggestions and GitHub Copilot CLI detection.

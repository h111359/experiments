# Implementation Log

Append-only entries. Add a new section for every execution update.

## Implementation Log

### Entry 2026-04-03 09:06 — Iteration 01

#### Scope
Implement all user-approved proposals from `.aib_memory/requests/R-20260402-1858-issue-31/proposals.md`. Changes span the menu launcher, prompt conventions, tool scripts, unit tests, and documentation.

#### Changes
- **P1** — Fixed duplicate "2." step numbering in `.aib_brain/prompts/aib-update-documentation.md`; steps now numbered 1–8 sequentially.
- **P2** — Replaced vague auto-trigger description with deterministic questionnaire rule in `.aib_brain/prompts/aib-create-analysis.md`; questionnaire is triggered if and only if section 13 contains a User-owned or unresolved item.
- **P4** — Removed inline field list from `.aib_brain/prompts/aib-implement.md`; replaced with a reference to `implementation-convention.md` Entry Block Format.
- **P8** — Replaced A/B/C/D free-text description in `.aib_brain/Concepts.md` with a reference to `questionnaire-convention.md`.
- **P10** — Added required `**Files Read**` bullet sub-section to section 4.7 of `.aib_brain/conventions/analysis-convention.md`.
- **P16 + P18** — Rewrote `.aib_brain/tools/menu.py` from scratch: eliminated `menu_config.json`, replaced static `PROMPT_ACTIONS` constant with `discover_prompt_actions(brain_dir)` that discovers `aib-*.md` files dynamically, replaced manifest loading with `build_script_actions(tools_dir)`, made Copilot CLI detection lazy via `_detect_copilot_cli()`. Deleted `.aib_brain/tools/menu_config.json`.
- **P19** — Added `logs/` preservation rule to §7 deployment procedure and §10 compliance checklist of `docs/Development_and_Deployment_Specification.md`.
- **P21** — Added `validate_request_md(path)` function to `.aib_brain/tools/common.py`; added `REQUIRED_REQUEST_SECTIONS` constant. Called `validate_request_md` in `.aib_brain/tools/create-request.py` after writing `request.md`. Removed validation-failure behavior instruction from `.aib_brain/conventions/request-convention.md` (convention now defines structure only).
- **P24** — Added "When to Create a New Iteration vs a New Request" section to `.aib_brain/README.md` with decision criteria, examples, and a decision-checklist table.
- **P28** — Modified `.aib_brain/tools/initialize.py` to skip overwriting `references.md` when it already exists unless `--force` is passed. Added `--force` argument to `parse_args` in `.aib_brain/tools/common.py`.
- **P29** — Added letter-check validation in `.aib_brain/tools/create-request.py`: title must contain at least one letter; raises `ValidationError` otherwise.
- **P30** — Added `max_length: int = 64` parameter to `slugify` in `.aib_brain/tools/common.py`; slug is truncated to 64 chars with trailing dash stripped. Updated caller in `create-request.py`.
- **Tests** — Added four new test classes to `.aib_brain/tools/test_common.py`: `TestSlugifyMaxLength` (P30), `TestValidateRequestMd` (P21), `TestInitializeReferencesSkip` (P28), `TestCreateRequestLetterCheck` (P29). Updated import list to include `validate_request_md`.

#### Tests
- Unit — `TestSlugifyMaxLength` (5 subtests): long title truncated, default max 64, short title unchanged, no trailing dash, custom max_length — PASS
- Unit — `TestValidateRequestMd` (4 subtests): valid request passes, all six missing-section permutations raise, empty file raises, missing file raises — PASS
- Unit — `TestInitializeReferencesSkip` (3 subtests): skip when exists without force, overwrite when force=True, creates when missing — PASS
- Unit — `TestCreateRequestLetterCheck` (3 subtests): numeric title raises, letters title passes, empty title handled by prior guard — PASS
- Full suite — 79 tests, 6 subtests: all PASS (0 failures, 0 errors)
- Syntax — `py_compile` on `menu.py`, `common.py`, `create-request.py`, `initialize.py`: all OK

#### Outcome
All 13 user-approved proposals implemented successfully. The menu is now fully dynamic (no static JSON config). `validate_request_md` enforces structural integrity at creation time. `slugify` is safe for long titles. `initialize.py` is idempotent with an opt-out `--force` escape hatch. Documentation and conventions are trimmed of embedded behavior instructions. No regressions detected.

#### Evidence
- Test run output: `79 passed, 6 subtests passed in 0.46s`
- Files modified: `menu.py`, `common.py`, `create-request.py`, `initialize.py`, `test_common.py`, `aib-update-documentation.md`, `aib-create-analysis.md`, `aib-implement.md`, `Concepts.md`, `analysis-convention.md`, `request-convention.md`, `Development_and_Deployment_Specification.md`, `README.md`
- File deleted: `.aib_brain/tools/menu_config.json`

#### Notes (Optional)
The `proposals.md` source was the user-curated version under `R-20260402-1858-issue-31`. Proposals P3, P5–P7, P9, P11–P15, P17, P20, P22–P23, P25–P27 were not present in the user-edited file and were not implemented.

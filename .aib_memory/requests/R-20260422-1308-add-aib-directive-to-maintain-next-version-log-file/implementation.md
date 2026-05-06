Implementation log for R-20260422-1308 — Add AIB directive to maintain next version log file.

.aib_memory/ files taken into consideration:
- .aib_memory/requests_register.md
- .aib_memory/references.md
- .aib_memory/instructions.md
- .aib_memory/context.md
- .aib_memory/requests/R-20260422-1308-add-aib-directive-to-maintain-next-version-log-file/request.md

## Implementation Log

### Entry 2026-04-25 12:00
#### Scope
Land the curated change-log lifecycle: add a persistent directive in `.aib_memory/instructions.md` instructing the agent to append bullets to `logs/next_version_changes.md` during implementation, extend `scripts/release_bookkeeping.py` to prefer those curated bullets over commit subjects with safe fallback, wire the new CLI flag into the GitHub Actions workflow, seed an empty curated file in `logs/`, and add tests covering preference, fallback, lifecycle reset, and idempotency. Aligned with analysis sections "AI Copilot Suggestions" and "Testing".

#### Changes
- Added persistent directive to `.aib_memory/instructions.md` defining bullet format, append-only behavior, and CI lifecycle expectations for `logs/next_version_changes.md`.
- Extended `scripts/release_bookkeeping.py` with module docstring, `_read_curated_entries` helper, `_reset_curated_file` helper, new `--next-version-changes-file` CLI argument, source-preference selection (curated first, commit subjects fallback), and post-incorporation reset gated on `changed and used_curated`.
- Updated `.github/workflows/aib-semver-patch-bump-and-log.yml` to pass `--next-version-changes-file logs/next_version_changes.md` to the bookkeeping script.
- Created empty `logs/next_version_changes.md` so CI has a tracked curated source ready for first use.
- Added `tests/test_release_bookkeeping.py` with helper-level and end-to-end coverage (curated parsing, preference, two fallback paths, lifecycle reset, idempotent rerun).
- Updated `tests/test_instructions_md.py` to validate the new non-empty directive content (replacing the prior empty-file assertion from R-20260421-1705).

#### Tests
- unit: `tests/test_release_bookkeeping.py::test_read_curated_entries_*` — pass (3 cases: missing, blank, bullet parsing).
- integration: `tests/test_release_bookkeeping.py::test_curated_source_preferred_over_commit_subjects` — pass.
- integration: `tests/test_release_bookkeeping.py::test_fallback_to_commit_subjects_when_curated_missing` — pass.
- integration: `tests/test_release_bookkeeping.py::test_fallback_to_commit_subjects_when_curated_empty` — pass.
- integration: `tests/test_release_bookkeeping.py::test_fallback_to_commit_subjects_when_curated_file_absent_path_provided` — pass.
- integration: `tests/test_release_bookkeeping.py::test_lifecycle_reset_after_incorporation` — pass.
- integration: `tests/test_release_bookkeeping.py::test_idempotent_rerun_after_reset` — pass.
- regression: full `pytest tests/` suite — 100 passed.

#### Outcome
Success. SC-01 through SC-06 satisfied: directive in place (SC-01); curated source preferred (SC-02); two fallback paths verified (SC-03); lifecycle reset of curated file confirmed (SC-04); `.aib_memory/references.md` left unchanged (SC-05); existing tests pass alongside new ones (SC-06). No residual risks identified; lifecycle reset is gated to avoid resetting on idempotent no-op reruns.

#### Evidence
- Path: `.aib_memory/instructions.md`
- Path: `scripts/release_bookkeeping.py`
- Path: `.github/workflows/aib-semver-patch-bump-and-log.yml`
- Path: `logs/next_version_changes.md`
- Path: `tests/test_release_bookkeeping.py`
- Path: `tests/test_instructions_md.py`
- Test summary: `100 passed in 21.31s`

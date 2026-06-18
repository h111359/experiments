Implementation log for request R-20260516-1425: Fix aib-semver-patch-bump-and-log.yml failures.

Files read during this implementation run:
- `.aib_memory/plan-R-20260516-1425.md` — authoritative scope and plan
- `.aib_memory/context.md` — workspace product context
- `scripts/release_bookkeeping.py` — target script (verified pre-applied changes)
- `.github/workflows/aib-semver-patch-bump-and-log.yml` — target workflow (verified pre-applied name change)
- `tests/test_release_bookkeeping.py` — target test file (verified pre-applied regression tests)
- `logs/next_version_changes.md` — curated change log (verified pre-appended bullets)
- `.aib_brain/conventions/implementation-convention.md` — output format rules
- `.aib_brain/conventions/context-convention.md` — context.md structure rules

## Implementation Log

### Entry 2026-05-16 15:00
#### Scope
Fix the GitHub Actions CI workflow so it no longer fails when a PR branch carries a manually-applied MINOR or MAJOR SemVer marker. The scope covers `scripts/release_bookkeeping.py`, `.github/workflows/aib-semver-patch-bump-and-log.yml`, `tests/test_release_bookkeeping.py`, `logs/next_version_changes.md`, and `.aib_memory/context.md`.

#### Changes
- Verified `@dataclass(frozen=True, order=True)` already present on `Version` class in `scripts/release_bookkeeping.py` — no edit needed.
- Verified version-comparison branching already present in `scripts/release_bookkeeping.py`: `head_version < base_version` → error; `head_version == base_version` → auto PATCH bump; `head_version > base_version` → use head version as-is — no edit needed.
- Verified `.github/workflows/aib-semver-patch-bump-and-log.yml` `name:` field already reads `AIB SemVer bump and log` — no edit needed.
- Verified three regression tests already present in `tests/test_release_bookkeeping.py`: `test_minor_version_pre_bumped_on_branch_accepted`, `test_major_version_pre_bumped_on_branch_accepted`, `test_marker_backwards_from_base_raises_error` — no edit needed.
- Verified four curated change bullets already appended to `logs/next_version_changes.md` for this request — no edit needed.
- Updated `.aib_memory/context.md`: corrected test count from 280 to 291, extended `test_release_bookkeeping.py` description to mention MINOR/MAJOR regression tests, updated preamble timestamp.

#### Tests
- unit/integration: `python -m pytest tests/test_release_bookkeeping.py tests/test_semver_workflow_structure.py -v` — 19 passed, 0 failed
- integration: `python -m pytest -v` (full suite) — 291 passed, 0 failed, 0 errors

#### Outcome
Successful. All 19 targeted tests pass and the full suite (291 tests) passes with zero failures. All plan success criteria met: `order=True` present on `Version` dataclass, mismatch guard replaced with version-comparison branching, workflow display name updated, curated change bullets appended, and context.md updated.

#### Evidence
- `python -m pytest tests/test_release_bookkeeping.py tests/test_semver_workflow_structure.py` → `19 passed in 11.83s`
- `python -m pytest` → `291 passed, 4 subtests passed in 14.42s`
- `scripts/release_bookkeeping.py` line: `@dataclass(frozen=True, order=True)`
- `.github/workflows/aib-semver-patch-bump-and-log.yml` line: `name: AIB SemVer bump and log`

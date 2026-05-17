# Implementation Log

Append-only entries. Add a new section for every execution update.

## Entry Template

### [YYYY-MM-DD HH:mi] Iteration [ID]

#### Implemented changes

#### Technical notes

#### Verification steps

#### Evidences for done

#### End result summary

#### Guidance for human how to verify

### 2026-03-20 22:02 Iteration 01

#### Implemented changes
- None (blocked before implementation).

#### Technical notes
- Request scope requires modifying `.github/workflows/aib-semver-patch-bump-and-log.yml` and `scripts/release_bookkeeping.py` to stop failing when historical per-version logs exist.
- Iteration 01 questionnaire decisions captured:
	- Keep historical per-version logs in `logs/` across versions.
	- Remove the “other version log” guard entirely (current selection), allowing multiple per-version logs to coexist.

#### Verification steps
- Not run (blocked).

#### Evidences for done
- Required-read set completed: all `product-doc` files listed in `.aib_memory/references.md` were read.

#### End result summary
- Blocked: `.aib_memory/references.md` does not list the workflow/script files, but the execution rules allow edits only to files listed there with `edit_allowed=Y`.

#### Guidance for human how to verify
- Remediation needed to unblock implementation:
	1) Add the following paths to `.aib_memory/references.md` with `type=source-code` and `edit_allowed=Y`:
		 - `.github/workflows/aib-semver-patch-bump-and-log.yml`
		 - `scripts/release_bookkeeping.py`
	2) Re-run the implement prompt; after unblocking, expected validation is to run the workflow locally (script dry-run) and/or repo tests.

### 2026-03-20 22:07 Iteration 01

#### Implemented changes
- Updated `scripts/release_bookkeeping.py` to remove the guard that failed the workflow when `logs/` already contained per-version log files for older versions.

#### Technical notes
- This aligns with the iteration questionnaire decisions:
	- Keep historical per-version logs in `logs/`.
	- Allow multiple per-version logs to coexist (removed the “other version logs” precondition).
- Workflow file `.github/workflows/aib-semver-patch-bump-and-log.yml` did not need changes because the failure originated in the script.

#### Verification steps
- Ran local dry-run:
	- `python scripts/release_bookkeeping.py --dry-run --base-ref HEAD --issue 17 --pr-number 0`

#### Evidences for done
- Dry-run output:
	- `Computed new version: v1.0.6`
	- `Log file path: logs/version_v1.0.6_log.md`
- Confirms the script no longer errors when `logs/version_v1.0.5_log.md` exists.

#### End result summary
- The workflow should no longer fail with “Per-version log file precondition failed … found ['v1.0.5']” when bumping from `v1.0.5` to `v1.0.6`.

#### Guidance for human how to verify
- Open/rerun a PR targeting `main` and confirm the `AIB SemVer PATCH bump and log` workflow completes successfully and commits `.aib_brain/vX.Y.Z` + `logs/version_vX.Y.Z_log.md` to the PR branch.

### 2026-03-20 22:15 Iteration 01

#### Implemented changes
- Updated the workflow to remove the hardcoded `--issue 17` argument.
- Updated `scripts/release_bookkeeping.py` so `--issue` is optional; when not provided, the generated per-version log omits the Issue section.

#### Technical notes
- Workflow now attempts to derive an issue number from the PR title/body if it contains `Fixes #123`, `Closes #123`, or `Resolves #123` (case-insensitive on the verb).
- If no issue is detected, the script is invoked without `--issue`.

#### Verification steps
- Local dry-run without issue:
	- `python scripts/release_bookkeeping.py --dry-run --base-ref HEAD --pr-number 0`
- Local dry-run with explicit issue:
	- `python scripts/release_bookkeeping.py --dry-run --base-ref HEAD --issue 17 --pr-number 0`

#### Evidences for done
- Both dry-runs computed `v1.0.6` and planned `logs/version_v1.0.6_log.md`.

#### End result summary
- The workflow no longer hardcodes Issue 17, avoiding misleading release notes as the automation is reused for other work.

#### Guidance for human how to verify
- In a PR description, include a line like `Fixes #17` (or another issue) and rerun the workflow; confirm the created log includes the correct Issue number.

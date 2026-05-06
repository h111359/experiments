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

### [2026-03-20 16:52] Iteration 03

#### Implemented changes
- Added a single GitHub Actions workflow to bump PATCH and create a per-version log file for PRs targeting `main` (pre-merge model: commits back to PR branch).
- Added a repo script (stdlib-only Python) that validates SemVer marker preconditions, computes next PATCH version from the base branch marker, rotates the `.aib_brain/` marker file, and creates `logs/version_<version>_log.md`.
- Updated `README.md` with setup requirements, behavior, and troubleshooting guidance.
- Reconciled iteration-03 questionnaire trigger selection to match the chosen pre-merge model.

#### Technical notes
- Workflow is restricted to PRs originating from the same repository (not forks).
- Loop prevention: the workflow skips events triggered by `github-actions[bot]`.
- The script fails fast with explicit errors for invalid marker state (zero/multiple/malformed).

#### Verification steps
- `python -m compileall scripts/release_bookkeeping.py`
- `python scripts/release_bookkeeping.py --base-ref main --dry-run`

#### Evidences for done
- New workflow file exists under `.github/workflows/`.
- Script computes next version and log filename deterministically in dry-run.

#### End result summary
Request deliverables are implemented in-repo (workflow + script + README guidance). Ready for PR review.

#### Guidance for human how to verify
1) Open a PR targeting `main` from a branch in the same repo.
2) Observe the workflow run creating a commit on the PR branch.
3) Confirm `.aib_brain/vX.Y.Z` rotated to `vX.Y.(Z+1)` and a new `logs/version_vX.Y.(Z+1)_log.md` file exists, while `logs/versions_log.md` remains unchanged.

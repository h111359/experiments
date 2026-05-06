# Iteration Analysis

## Summary
- Request: `R-20260321-0638` (workflow-bug-fix).

- Iteration: `03` (Active).

- Observed failure mechanism is deterministic: the workflow writes an untracked file `.aib_pr_commit_subjects.txt` into the repository worktree and never removes it, so the final step “Ensure clean working tree” fails when it runs `git status --porcelain`.

- The workflow currently creates the file in the “Collect PR commit subjects” step and then passes it into `scripts/release_bookkeeping.py` via `--commit-subjects-file .aib_pr_commit_subjects.txt`.

- Iteration goal: select and implement a workflow-safe policy for temporary artifacts that preserves the “clean working tree” guardrail and keeps the bookkeeping step behavior unchanged.

- Recommendation (preferred): store the commit-subjects file outside the repo worktree (use `$RUNNER_TEMP` or `${{ runner.temp }}`) and pass that absolute path to `scripts/release_bookkeeping.py`. Optionally add a defensive cleanup step with `if: always()`.

- Key decision needed: whether to (A) write outside the worktree (recommended) vs (B) write in-worktree but delete before the cleanliness check.

## Affected areas
- `.github/workflows/aib-semver-patch-bump-and-log.yml` (update where the commit-subjects file is written and how its path is passed into the bookkeeping step).

- GitHub Actions runner environment variables / filesystem (`RUNNER_TEMP` or `${{ runner.temp }}`) used for transient artifacts.

- `scripts/release_bookkeeping.py` (expected to accept a path to a readable commit-subjects file; no functional change required if it already reads from the provided path).

## Assumptions
- A1: The file `.aib_pr_commit_subjects.txt` is a transient artifact and should not persist in the repository worktree after the workflow completes.

- A2: Using `$RUNNER_TEMP` (or `${{ runner.temp }}`) is available on the workflow runner (`ubuntu-latest`) and is appropriate for transient files.

- A3: The final “Ensure clean working tree” step is intended to remain strict and meaningful (i.e., it should still fail on other unintended worktree changes).

- A4: `scripts/release_bookkeeping.py` will continue to function correctly if `--commit-subjects-file` is changed from a relative path in the repo root to an absolute path in the runner temp directory.

## Risks
- R1: Temp-path portability/quoting issues (e.g., empty env var, spaces) could cause the bookkeeping step to fail to read the file.

- R2: A cleanup-only approach (delete from worktree right before the cleanliness check) still allows transient files to exist inside the worktree mid-run, which can confuse debugging and can re-break if the step order changes.

- R3: Over-broad ignore-based mitigations (e.g., `.gitignore`) would reduce the signal of the cleanliness check and could mask other unintended artifacts.

## Dependencies
- GitHub-hosted runner provides a writable temp directory via `$RUNNER_TEMP` or `${{ runner.temp }}`.

- Workflow must preserve its current permissions and behavior (it currently checks out the PR branch, runs bookkeeping, optionally commits/pushes `.aib_brain` and `logs`, then enforces cleanliness).

- The bookkeeping step must keep receiving commit subjects content consistent with `git log --pretty=format:%s origin/${{ github.base_ref }}..HEAD`.

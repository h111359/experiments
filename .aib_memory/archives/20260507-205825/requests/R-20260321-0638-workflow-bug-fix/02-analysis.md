# Analysis - Iteration 02

## Executive Summary
- This analysis covers request `R-20260321-0638`: a GitHub Actions workflow failure reporting a dirty working tree with an untracked file `?? .aib_pr_commit_subjects.txt`.
- Root cause is concrete and local to the workflow `.github/workflows/aib-semver-patch-bump-and-log.yml`: it creates `.aib_pr_commit_subjects.txt` via `git log ... > .aib_pr_commit_subjects.txt` but never cleans it up, so the final “Ensure clean working tree” step fails.
- Iteration goal: define and implement a permanent policy for workflow-generated temporary artifacts so the workflow ends with a clean worktree.
- Key decision: preferred mitigation approach (ignore via `.gitignore` vs delete in-workflow vs write outside the repository worktree).
- Recommendation: write the commit-subjects file under `$RUNNER_TEMP` (or equivalent) and/or add an explicit cleanup step with `if: always()`; avoid relying solely on `.gitignore` because it can mask other cleanliness issues.

## Request Context Snapshot
- Request ID: `R-20260321-0638`
- Request title (from folder): `workflow-bug-fix`
- Iteration ID: `02` (Active; created 2026-03-21 07:00:53 +0200)
- High-level purpose (from `request.md`):
  - Find the root cause of the workflow error.
  - Fix it permanently.
  - Explain why it happened.
- Background facts (from `request.md`):
  - Workflow failed with:
    - `Working tree is not clean after workflow run:`
    - `?? .aib_pr_commit_subjects.txt`
- Constraints/scope/success criteria:
  - `request.md` contains the required sections, but `Scope`, `Out of scope`, `Constraints`, and `Success criteria` are currently empty (insufficient specificity).

## Scope Interpretation
- In scope:
  - Identify why `.aib_pr_commit_subjects.txt` exists after the workflow run.
  - Update `.github/workflows/aib-semver-patch-bump-and-log.yml` to ensure the job ends with a clean working tree.
  - Preserve the workflow’s functional behavior (collect commit subjects, run `scripts/release_bookkeeping.py`, optionally commit/push changes).
  - Provide a clear explanation of the failure mechanism.
- Out of scope:
  - No explicit out-of-scope items provided in `request.md`.
- Implicitly in scope (implicit rule - AIB framework):
  - Keep CI runs deterministic and idempotent where possible.
  - Avoid introducing persistent repository artifacts that are not part of the intended versioning/logging outputs.

## Background Knowledge (Domain + Technical)
- GitHub Actions workflow: an automated CI pipeline defined in `.github/workflows/*.yml` running on GitHub-hosted runners.
- Worktree cleanliness: `git status --porcelain` reports modified/untracked files in the checked-out repository directory.
- Untracked file: a file present on disk but not tracked by git and not ignored (shown as `?? <file>` by `git status --porcelain`).
- `$RUNNER_TEMP`: a per-job temporary directory on GitHub-hosted runners intended for transient files (not inside the repository working directory).
- Why this matters here:
  - The workflow intentionally fails if the worktree is dirty at the end, to prevent accidental leftover artifacts from polluting future runs or hiding bugs.

## Assumptions
- Assumption A1: It is acceptable to change `.github/workflows/aib-semver-patch-bump-and-log.yml` to address the failure.
  - Rationale: The failure is caused by workflow steps and the request is explicitly about a workflow failure.
  - Risk if false: the only remaining options would be repo-wide ignore rules or script changes, which may not align with the intended scope.
  - Falsification method: confirm whether workflow YAML changes are allowed for this request/PR.
----------------
- Assumption A2: `.aib_pr_commit_subjects.txt` is intended to be a temporary workflow artifact and should not remain in the repo worktree.
  - Rationale: The file is created only as an intermediate to feed `--commit-subjects-file` and is not added/committed.
  - Risk if false: if the file is intended to be kept for audit/debugging, cleanup would remove expected evidence.
  - Falsification method: check repo conventions/docs for expected CI artifacts; confirm with maintainers.
----------------
- Assumption A3: Keeping the “Ensure clean working tree” step is desired (it is a safeguard, not the problem).
  - Rationale: The check is correctly detecting an unintended leftover file.
  - Risk if false: removing the check could allow other real issues to slip through.
  - Falsification method: confirm whether the project wants strict cleanliness enforcement at job end.
----------------
- Assumption A4: Using `$RUNNER_TEMP` is available and reliable on `ubuntu-latest` runners.
  - Rationale: `$RUNNER_TEMP` is a standard GitHub Actions environment variable on hosted runners.
  - Risk if false: path issues could break `scripts/release_bookkeeping.py` input reading.
  - Falsification method: verify `$RUNNER_TEMP` exists in the runner environment or use a fallback path.
----------------

## Impact Assessment
- Affected Areas
  - `.github/workflows/aib-semver-patch-bump-and-log.yml` (workflow step that writes commit subjects + cleanup/policy)
  - Potentially `.gitignore` (only if choosing the ignore-based option)
- Change Type & Dependencies
  - Workflow change type: modify
  - Dependencies: bash shell, `git`, `python3`, GitHub runner environment variables (`GITHUB_OUTPUT`, `RUNNER_TEMP`)
  - Downstream: `scripts/release_bookkeeping.py` continues to receive a readable commit-subjects file.
- Domain Impacts
  - DOMAIN (DEV): Yes — CI reliability and correctness of PR automation.
  - DOMAIN (OPR): Yes — release-related automation should remain deterministic and non-fragile.
  - DOMAIN (OBS): Minor — the workflow logs/outputs remain the main trace; no need for a committed artifact file.
  - DOMAIN (SEC): No new secrets or credentials; no impact expected.
  - DOMAIN (ARCH/CMP/DATA/KNW/RQT): No direct impact detected for this change.
- Constraints
  - The workflow currently enforces cleanliness via `git status --porcelain` and fails if any changes (including untracked files) remain.
  - The workflow also commits and pushes changes only for `.aib_brain` and `logs`; unrelated changes should not be introduced.
- Required Documentation Updates
  - None strictly required for this change (behavior is a CI hygiene fix). If any internal process documentation exists for release automation, consider a short note that transient files must be stored in temp dirs.
- Estimated Complexity
  - Low
  - Rationale: localized workflow change; no cross-module refactor required.

## Research Summary
- Methodology
  - Read request context (`request.md`, `iterations.md`).
  - Locate references to `.aib_pr_commit_subjects.txt` in the repository.
  - Inspect `.github/workflows/aib-semver-patch-bump-and-log.yml` and `scripts/release_bookkeeping.py`.
- Evidence → Implication
  - Evidence: workflow step “Collect PR commit subjects” runs `git log ... > .aib_pr_commit_subjects.txt`.
    - Implication: the workflow creates an untracked file inside the repo worktree.
  - Evidence: workflow step “Ensure clean working tree” fails when `git status --porcelain` is non-empty.
    - Implication: any leftover untracked file will hard-fail the job.
  - Evidence: `.aib_pr_commit_subjects.txt` is not added to git and not removed.
    - Implication: the job ends dirty and fails deterministically.
- Gaps / unknowns
  - Whether maintainers prefer ignore-based fixes (`.gitignore`) or strict cleanup.
  - Whether the commit-subjects content is needed post-run for debugging/audit.

## Rewrite Proposal of the Request
Update the GitHub Actions workflow `.github/workflows/aib-semver-patch-bump-and-log.yml` so that the workflow-generated commit-subjects artifact does not leave the repository working directory dirty and the workflow completes successfully.

Acceptance criteria:
- The workflow no longer fails with `Working tree is not clean after workflow run: ?? .aib_pr_commit_subjects.txt`.
- The final cleanliness check remains meaningful: the job still fails if other unintended changes are present.
- The bookkeeping step still receives commit subjects and continues to work as before.
- Reruns of the workflow on the same PR do not accumulate persistent temporary artifacts in the repo worktree.

Explicit out of scope:
- Changing SemVer bump semantics or the content of the generated version logs.
- Adding new release artifacts beyond existing `.aib_brain` marker rotation and `logs/` updates.

## Solution Options (A/B; C optional)
- Option A: Add `.aib_pr_commit_subjects.txt` to `.gitignore`
  - Overview: ignore the file so `git status --porcelain` does not report it.
  - Benefits: simple; no workflow changes needed to clean up.
  - Trade-offs: weakens the cleanliness check by hiding this specific file; if the file name changes, the problem returns.
  - Risks: can mask cases where the workflow unexpectedly writes other ignored artifacts.
  - Effort: very low.
- Option B: Delete the file before the final cleanliness check
  - Overview: add a step `rm -f .aib_pr_commit_subjects.txt` (ideally `if: always()`) so the worktree is clean.
  - Benefits: keeps the cleanliness check strict; minimal behavior change.
  - Trade-offs: still writes transient data into the repo worktree during the run.
  - Risks: if later steps rely on the file, ordering mistakes could break the workflow.
  - Effort: very low.
- Option C (recommended): Write the file outside the repo worktree (e.g., `$RUNNER_TEMP`) and optionally clean up
  - Overview: redirect `git log` output to `$RUNNER_TEMP/aib_pr_commit_subjects.txt` and pass that path to `scripts/release_bookkeeping.py`.
  - Benefits: avoids polluting the repo worktree entirely; preserves strict cleanliness enforcement; most robust long-term.
  - Trade-offs: requires passing a different path through workflow steps.
  - Risks: path/env var assumptions; needs a small amount of careful quoting.
  - Effort: low.

Recommendation: Option C (store transient artifacts under `$RUNNER_TEMP`), optionally combined with a cleanup step using `if: always()`.

## Implementation & Testing Approach
- Implementation outline
  - Update `.github/workflows/aib-semver-patch-bump-and-log.yml`:
    - Write commit subjects into `$RUNNER_TEMP` (or a safe temp path) instead of the repository root.
    - Pass that temp path to `--commit-subjects-file`.
    - Add an `if: always()` cleanup step (optional but defensive) that removes the temp file.
  - Keep the final “Ensure clean working tree” step unchanged.
- Testing approach (CI-focused)
  - Open/update a PR targeting `main` and confirm the workflow completes successfully.
  - Confirm the “Show planned changes” and “Ensure clean working tree” steps show no untracked `.aib_pr_commit_subjects.txt`.
  - Confirm the workflow still produces the expected changes under `.aib_brain/` and `logs/` (when applicable) and can push them.
  - Re-run via a new commit (`synchronize`) and confirm idempotent behavior (no accumulating artifacts).

## Risks
- Risk R1: The workflow writes the temp file to a path not accessible by the Python step (path/permissions issue).
  - Probability: Low
  - Impact: Medium
  - Mitigation: use `$RUNNER_TEMP` on `ubuntu-latest`; add a fallback to `${{ runner.temp }}` or `mktemp` if needed; add a debug echo of the chosen path.
  - Owner (role): CI owner
--------------
- Risk R2: Ignore-based approach (Option A) reduces the signal of the “Ensure clean working tree” check.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: prefer Option C/B; if Option A is chosen, keep the ignore narrowly scoped to this single filename.
  - Owner (role): Repo maintainer
--------------

## Dependencies / Externalities
- GitHub-hosted runner environment variables must include a usable temp directory (`RUNNER_TEMP` or equivalent).
- The workflow must continue to have the permissions it currently uses (`contents: write` for push operations).

## Open Questions & Next Actions
1. (Owner: Repo maintainer) Confirm the preferred policy for temporary artifacts in workflows: ignore vs cleanup vs write outside worktree. Trigger: before implementing the chosen option.
2. (Owner: CI owner) Decide whether to add a defensive cleanup step with `if: always()` to guarantee cleanup even when earlier steps fail. Trigger: during workflow edit.

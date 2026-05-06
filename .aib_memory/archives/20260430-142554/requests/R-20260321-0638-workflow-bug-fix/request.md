# Request

## Goal

Update the GitHub Actions workflow `.github/workflows/aib-semver-patch-bump-and-log.yml` so that the workflow-generated commit-subjects artifact does not leave the repository working directory dirty and the workflow completes successfully.

Acceptance criteria:
- The workflow no longer fails with `Working tree is not clean after workflow run: ?? .aib_pr_commit_subjects.txt`.
- The final cleanliness check remains meaningful: the job still fails if other unintended changes are present.
- The bookkeeping step still receives commit subjects and continues to work as before.
- Reruns of the workflow on the same PR do not accumulate persistent temporary artifacts in the repo worktree.

Explicit out of scope:
- Changing SemVer bump semantics or the content of the generated version logs.
- Adding new release artifacts beyond existing `.aib_brain` marker rotation and `logs/` updates.

## Background

The github workflow failed with the following error:

Run set -euo pipefail
Working tree is not clean after workflow run:
?? .aib_pr_commit_subjects.txt
Error: Process completed with exit code 1.

## Scope

## Out of scope

## Constraints

## Success criteria

Request ID: `R-20260321-0638`

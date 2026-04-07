# AI Builder

## Overview

AI Builder (AIB) is a minimal, model-agnostic framework for specification-driven development.

See `.aib_brain/Concepts.md` for the complete definition of goals, concepts, objectives, requirements, and implementation details.

## Installation

Copy folder `.aib_brain/` from main branch in your project and 
- For Windows run in terminal `.\.aib_brain\run.bat`
- For Linux execute `.aib_brain/run.sh`

Follow the user guide in `.aib_brain/README.md`

## Automated version bump & release log (Issue #17)

This repository includes a GitHub Actions workflow that automates release bookkeeping for pull requests targeting `main`.

### What it does

On eligible PR events, the workflow:
- Validates that there is exactly one SemVer marker file under `.aib_brain/` named `vMAJOR.MINOR.PATCH`.
- Computes a new version by incrementing `PATCH` by 1.
- Rotates the marker file by deleting the old marker and creating a new empty marker file with the bumped version name.
- Creates a new per-version log file under `logs/` named `version_<version>_log.md` where `<version>` is the marker filename (includes the leading `v`).
	- Example: `logs/version_v1.0.5_log.md`
- Populates the log file with Issue #17 and the PR commit subjects.

Important constraints:
- The workflow never modifies existing files under `logs/` (it only creates a new file).
- If SemVer marker preconditions are invalid (zero/multiple markers, malformed marker name), the workflow fails with an explicit error.

### When it runs

The workflow triggers for pull requests targeting `main` on: opened, reopened, and synchronize events.

This implementation uses a **pre-merge** write model:
- It commits the marker rotation + new version log file back to the PR branch.
- Then you merge the PR normally to land the changes on `main`.

To prevent infinite loops, the workflow skips runs triggered by `github-actions[bot]`.

### Repository setup requirements

In your GitHub repository settings:
- Enable GitHub Actions.
- Set **Workflow permissions** for `GITHUB_TOKEN` to **Read and write permissions**.

Notes:
- For security, the workflow is restricted to PRs whose source branch is in the same repository (not forks). Forked PRs will be skipped.

### Operational behavior and troubleshooting

- If the workflow fails due to marker validation, ensure `.aib_brain/` contains exactly one file matching `vMAJOR.MINOR.PATCH`.
- If the workflow cannot push to the PR branch, check the repo’s Actions permissions and any branch protection rules that may prevent Actions from pushing to the branch.
- If the workflow fails because a per-version log file already exists for a different version, reset/rebase the PR branch to remove the stale per-version log file, then rerun.

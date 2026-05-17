# Request

Request ID: `R-20260320-0925`

## Goal

Create in the repo a GitHub actions workflow which should be executed when PR to main is executed. It should:

increases the PATCH number in the name of the semver file in .aib_brain folder

Adds the commit messages under a new file for the version (see the current files format) in `logs\` folder

Describe this functionality and instruction how to setup GutHub repo in README.md file

Implement automated release bookkeeping by adding a GitHub Actions workflow that executes for pull requests targeting main and performs the following actions when the selected trigger condition is satisfied: 
(1) detect exactly one SemVer marker file in .aib_brain matching vMAJOR.MINOR.PATCH, 
(2) compute a new version with PATCH incremented by one, 
(3) replace the prior marker file with a new empty marker file named with the updated version, 
(4) create a new file in `logs/` named version_<version>_log.md using the semver file name as version and keeping the existing files style and containing the issue reference and collected commit messages, and 

As an additional requiremet update repository README.md (once, not part of the workflow) with setup instructions covering workflow permissions, branch-policy prerequisites, and operational behavior. 

The workflow must fail with explicit errors if SemVer preconditions are invalid (zero or multiple marker files, malformed version filename), must preserve all existing content in logs/ without modification, and must keep changes traceable to the triggering PR. Acceptance criteria: one new workflow file under .github/workflows; marker file transitions from vX.Y.Z to vX.Y.(Z+1); new version log block is appended only; README includes configuration and usage guidance; and repository checks pass for the workflow path.

## Background

## Scope

## Out of scope

## Constraints

Do not change the existing log files in `logs\`. Add additional file append only

## Success criteria

added workflow in .github folder
after the execution of the workflow there should be no uncommitted changes left
the branch should be ready for merge


# Request

## Goal

Fix the issue with the workflow `.github\workflows\aib-semver-patch-bump-and-log.yml`

## Background

Bug:
0s
Run set -euo pipefail
ERROR: Per-version log file precondition failed: PR branch already contains per-version log file(s) for a different version. Computed target is 'v1.0.6', but found: ['v1.0.5']. Refusing to create additional log files. Rebase/reset the PR branch to remove the stale per-version log file(s) and rerun.
Error: Process completed with exit code 2.

## Scope

## Out of scope

## Constraints

## Success criteria

Request ID: `R-20260320-2120`

# Analysis - Iteration 01

## Executive Summary
- This analysis covers the request `R-20260320-2120`: fix the failing workflow `.github/workflows/aib-semver-patch-bump-and-log.yml` that bumps the SemVer PATCH marker and writes a per-version log.
- The observed failure is deterministic: the release bookkeeping script fails if `logs/` already contains a per-version log for any version other than the computed target (for example, target `v1.0.6` but `logs/version_v1.0.5_log.md` exists).
- The workflow currently runs `scripts/release_bookkeeping.py` on every PR sync, so once the repository has a historical per-version log, future PATCH bumps will fail.
- This iteration should clarify the intended policy for per-version logs: keep historical logs in-repo (recommended) vs treat them as transient PR artifacts.
- Primary decision required: choose the desired behavior when `logs/` contains older per-version log files (A: allow historical logs; B: only guard against logs newly added by the PR; C: auto-clean stale PR-added logs).
- Recommendation: update `scripts/release_bookkeeping.py` to only guard against per-version log files that are newly introduced on the PR branch compared to `--base-ref`, and allow historical logs that already exist on base.
- Expected outcome if accepted: the workflow becomes idempotent and continues to work as the repo accumulates `logs/version_v*_log.md` history.

## Request Context Snapshot
- Request ID: R-20260320-2120
- Request title (from folder): version-bump-workflow-bugfix
- Iteration ID: 01 (Active; created 2026-03-20 21:20:45 +0200)
- High-level purpose: fix the GitHub Actions workflow that performs SemVer PATCH bump bookkeeping and per-version log creation.
- Background facts (from request): the workflow fails with `Per-version log file precondition failed... Computed target is 'v1.0.6', but found: ['v1.0.5']`.
- Constraints from request.md: none explicitly provided (sections exist but are empty).
- Scope delta since prior iteration: none (no prior iterations).

## Scope Interpretation
- In scope:
  - Fix the failure mode of `.github/workflows/aib-semver-patch-bump-and-log.yml` when it runs on PRs to `main`.
  - Fix the underlying guard logic in `scripts/release_bookkeeping.py` if that is the root cause of the workflow failure.
  - Preserve deterministic SemVer computation: base marker at `--base-ref` + 1 PATCH.
- Out of scope:
  - Changing the overall versioning strategy (MAJOR/MINOR rules) beyond PATCH bump.
  - Changing unrelated CI workflows.
  - Rewriting historical logs unless required to restore workflow correctness.
- Implicitly in scope (implicit rule - AIB framework):
  - Updating any directly affected product docs in `.aib_memory/docs/` if they are used as authoritative catalogs for scripts/workflows.

## Domain Knowledge Essentials
- SemVer marker: a file named `vMAJOR.MINOR.PATCH` under `.aib_brain/` used as the canonical version indicator.
- Per-version log: a file under `logs/` named `version_vMAJOR.MINOR.PATCH_log.md` recording release notes for a specific version.
- Impacted role: repo maintainers/release owners who rely on PR automation to bump the version and produce a release log.
- Business/product acceptance impact: the repo should be able to continue releasing new patch versions without PR automation becoming permanently blocked once a historical log exists.

## Technical Knowledge & Terms
- GitHub Actions workflow: `.github/workflows/aib-semver-patch-bump-and-log.yml`, running on `pull_request` events (opened/reopened/synchronize) targeting `main`.
- `--base-ref`: git ref fetched in the workflow (for example `origin/main`) used to compute the next patch version deterministically.
- Worktree vs base tree:
  - Base tree: files as they exist at `--base-ref`.
  - Worktree/HEAD: files currently checked out on the PR branch.
- Release bookkeeping script: `scripts/release_bookkeeping.py`, invoked by the workflow to:
  - read base marker from `git ls-tree` on base ref,
  - validate exactly one marker file on base and on the worktree,
  - compute target marker (base + 1 PATCH),
  - write `logs/version_<target>_log.md` and rotate `.aib_brain/<marker>`.

## Assumptions
- Assumption A1: The repository is intended to keep historical per-version log files under `logs/` across versions (not just a single “latest” log).
  - Rationale: `logs/` currently contains a versioned log file and a cumulative `versions_log.md`.
  - Risk if false: if logs are meant to be transient, allowing historical logs may conflict with repo policy.
  - Falsification method: confirm intended log retention policy in repo docs or maintainer guidance.
- Assumption A2: The workflow should be idempotent on repeated PR `synchronize` events (reruns should not fail or create conflicting artifacts).
  - Rationale: the workflow triggers on `synchronize` and also commits to the PR branch; idempotency is required to avoid endless failures.
  - Risk if false: if non-idempotent runs are acceptable, a simpler fix might be preferred.
  - Falsification method: confirm expected behavior for reruns and rebases in CI.
- Assumption A3: It is acceptable to change `scripts/release_bookkeeping.py` (even though the request names the workflow) because it is part of the workflow’s functional surface.
  - Rationale: the failure is raised by the script and cannot be fixed solely by YAML without changing behavior.
  - Risk if false: fixes would be constrained to wrapper steps (cleaning, renaming, or changing inputs) and may be brittle.
  - Falsification method: confirm whether script changes are in scope for this request.
- Assumption A4: The correct “guard” behavior is to only consider per-version log files that are newly introduced by the PR branch compared to `--base-ref`.
  - Rationale: historical version logs already present on base should not block creating a new one.
  - Risk if false: the guard could allow undesirable multiple version logs in a single PR.
  - Falsification method: reproduce the failure locally and validate expectations with maintainers.
- Assumption A5: The marker rotation behavior (delete old marker, create new marker file) is correct and should remain.
  - Rationale: marker state is validated to be either base marker or target marker.
  - Risk if false: version bumps could become inconsistent with release notes.
  - Falsification method: confirm SemVer marker file contract in `.aib_brain/`.

## Impact Assessment

### Affected Components / Areas
- GitHub Actions workflow: `.github/workflows/aib-semver-patch-bump-and-log.yml`
- Release bookkeeping logic: `scripts/release_bookkeeping.py`
- Version marker file under `.aib_brain/` (for example `v1.0.5` -> `v1.0.6`)
- Per-version log files under `logs/` (for example `logs/version_v1.0.6_log.md`)

### Change Type and Dependencies
- `.github/workflows/aib-semver-patch-bump-and-log.yml`
  - Change type: modify (optional)
  - Dependencies: GitHub Actions runner (`ubuntu-latest`), checkout/fetch operations, Python available as `python3`.
  - Sequencing: must fetch base branch before running bookkeeping; must commit only if files changed.
- `scripts/release_bookkeeping.py`
  - Change type: modify
  - Dependencies: `git` CLI available on runner; stable base ref resolution.
  - Sequencing: compute base marker and target marker first; then determine whether any PR-introduced per-version logs conflict; then write log/rotate marker.

### Domain Impacts
- DOMAIN (ARCH): No impact detected.
- DOMAIN (CMP): Minor impact (release bookkeeping script behavior changes).
- DOMAIN (DATA): No impact detected.
- DOMAIN (DEV): Minor impact (CI workflow reliability for PRs).
- DOMAIN (DSR): No impact detected.
- DOMAIN (FNL): No impact detected.
- DOMAIN (KNW): No impact detected.
- DOMAIN (RQT): No impact detected.
- DOMAIN (OBS): Minor impact (release/log artifacts produced by automation).
- DOMAIN (OPR): Minor impact (release operational process; PR auto-commits).
- DOMAIN (SEC): No impact detected (no new secrets; uses existing GHA token).

### Constraints
- No explicit constraints are stated in the request.
- Technical constraints observed from the current workflow:
  - Must run on `ubuntu-latest` with `bash` and `python3`.
  - Must remain deterministic with respect to `--base-ref` (no “guessing” versions).
  - Must avoid leaving a dirty worktree at the end of the workflow.

### Required Documentation Updates
- CMP-01 - Notebook/script catalog
  Required update? MAYBE
  Reason: If this catalog is maintained, `scripts/release_bookkeeping.py` behavior/purpose changes should be reflected.
- OBS-01 - Logging
  Required update? MAYBE
  Reason: Release logging artifacts and expectations may be documented here.
- All other `product-doc` references
  Required update? NO (no documented requirements/IDs currently present; files are seeded placeholders).

### Decision Points
- Decision D1: How to interpret “stale per-version logs” on a PR branch?
  - Option 1: Remove the guard entirely (always allow multiple historical logs).
    - Implication: simplest; avoids failures; but may allow a PR to accumulate multiple per-version logs across reruns.
  - Option 2: Guard only against PR-introduced logs by comparing the worktree `logs/` to `--base-ref` (recommended).
    - Implication: allows historical logs; still prevents creating multiple new version logs in one PR unless explicitly intended.
  - Option 3: Auto-delete/rename PR-introduced logs that don’t match the newly computed target.
    - Implication: keeps PR tidy and idempotent; but has higher risk of deleting something a human intentionally added.
  - Recommended option: Option 2 (guard only against PR-introduced logs; do not touch base history).

### Estimated Implementation Complexity
- Complexity: Low
  - Rationale: change is localized to the guard clause in `scripts/release_bookkeeping.py` and optionally minor workflow tweaks.
  - Confidence: Medium (depends on the exact desired policy for multiple version logs per PR).

## Research Plan and Findings
- Methodology
  - Read request inputs (`request.md`, `iterations.md`).
  - Read required product docs from `.aib_memory/references.md` (all `product-doc` entries).
  - Scan workflow and script for the error source.
  - Inspect existing `logs/` artifacts to validate the failure scenario.
- Findings
  - Evidence: `.github/workflows/aib-semver-patch-bump-and-log.yml` runs `python3 scripts/release_bookkeeping.py` and commits `.aib_brain` and `logs` if changed.
    - Implication: the workflow’s correctness depends primarily on `scripts/release_bookkeeping.py` behavior.
  - Evidence: `scripts/release_bookkeeping.py` currently fails if `logs/` contains any `version_<marker>_log.md` where `<marker> != target_marker`.
    - Implication: once the repo contains a historical per-version log (for example `logs/version_v1.0.5_log.md`), the next PATCH bump to `v1.0.6` will fail deterministically.
  - Evidence: the repository currently contains `logs/version_v1.0.5_log.md`.
    - Implication: the guard will trigger for target versions other than `v1.0.5` even if the file is part of base history.
- Gaps / unknowns
  - Whether per-version logs are intended to be cumulative history under `logs/` (retain all versions) or ephemeral per-PR artifacts.
  - Whether the workflow should ever allow a single PR to create more than one per-version log across reruns.
- Proposed validation actions
  - Reproduce locally by running `scripts/release_bookkeeping.py --dry-run` with a base ref that already contains at least one historical `logs/version_v*_log.md`.
  - Confirm desired retention policy with maintainers (or via existing project docs if present elsewhere).

## Rewrite Proposal of the Request
Update the GitHub Actions workflow `.github/workflows/aib-semver-patch-bump-and-log.yml` and/or the invoked script `scripts/release_bookkeeping.py` so that PR automation can bump the SemVer PATCH marker under `.aib_brain/` and create the new per-version log `logs/version_<target>_log.md` without failing when `logs/` already contains historical per-version logs from prior releases.

Acceptance criteria:
- On a PR to `main`, the workflow computes the target version as `(base marker at origin/main) + 1 PATCH`.
- The workflow succeeds when `logs/` already contains one or more older `logs/version_v*_log.md` files that exist on the base branch.
- Re-running the workflow on the same PR is idempotent:
  - it does not create duplicate per-version logs for the same target version,
  - it does not fail due to prior workflow-created artifacts.
- The workflow either (a) prevents or (b) deterministically resolves cases where the PR branch introduces multiple new per-version logs (policy must be explicit).

Out of scope:
- Changing the naming scheme of marker files or per-version log files.
- Adding MAJOR/MINOR bump logic.

## Solution Options
- Option A: Remove the “other version log” guard entirely
  - Overview: delete the check that fails when `logs/version_*_log.md` exists for versions other than the computed target.
  - Benefits: simplest; immediately unblocks workflow.
  - Trade-offs: a single PR could accumulate multiple new version logs across reruns if the base ref changes.
  - Constraints: none beyond deterministic version compute.
  - Risks: repository noise; confusing release notes if multiple logs are created in one PR.
  - Expected effort: very low.
  - Acceptance-test ideas: run workflow twice with base unchanged; ensure only one new log is created.

- Option B: Compare against base ref and only guard PR-introduced per-version logs (recommended)
  - Overview: compute which per-version logs exist on `--base-ref` (via `git ls-tree`) and ignore those; only consider logs present in the PR worktree but not on base.
  - Benefits: preserves historical logs; prevents the current deterministic failure; maintains the intent of guarding against multi-log PR artifacts.
  - Trade-offs: requires a bit more git plumbing; still needs a policy decision for what to do if PR already introduced a different version log.
  - Constraints: requires `git ls-tree <base-ref>:logs` (or equivalent) to be available.
  - Risks: edge cases if `logs/` didn’t exist on base; must handle empty tree safely.
  - Expected effort: low.
  - Acceptance-test ideas: simulate a PR where base has `version_v1.0.5_log.md` and target is `v1.0.6` and verify no failure.

- Option C: Auto-clean PR-introduced stale per-version logs
  - Overview: if PR worktree contains new per-version logs that are not the current target marker, delete (or rename) them before writing the new target log.
  - Benefits: strongest idempotency guarantee across rebase/base-advance scenarios.
  - Trade-offs: higher risk of deleting a file that a human intentionally added.
  - Constraints: should only delete files confidently identified as workflow-generated artifacts.
  - Risks: unintended data loss; trust boundary concerns.
  - Expected effort: low-medium.
  - Acceptance-test ideas: add a non-workflow log file and ensure it is not removed.

Recommendation: Option B, optionally combined with a conservative variant of Option C that only cleans logs that are both (1) PR-introduced and (2) clearly workflow-generated.

## Suggested Implementation Approach
- Update `scripts/release_bookkeeping.py` to compute “base-known per-version logs” from `--base-ref` and exclude them from the “other version log” precondition.
- Define policy for PR-introduced conflicting logs:
  - If PR-introduced logs exist for a different marker, either fail with a clearer message OR auto-clean only if they match strict “workflow-generated” criteria.
- Keep existing idempotency rules:
  - If `logs/version_<target>_log.md` exists and the marker is already bumped, treat as no-op.
- If needed, minimally adjust `.github/workflows/aib-semver-patch-bump-and-log.yml` to make the error messaging visible and/or to pass additional context (for example the base ref already fetched).
- Record concrete implementation steps in `01-plan.md` (expected next artifact).

## Suggested Testing Approach
- Local script checks
  - Run `python scripts/release_bookkeeping.py --dry-run --base-ref origin/main` and verify it computes the expected target and does not error when historical logs exist.
  - Create a temporary git scenario (or use a throwaway branch) where `logs/` contains historical logs on base and validate behavior.
- Workflow-level checks
  - Open a PR and ensure the workflow succeeds on `opened` and on a subsequent `synchronize`.
  - Verify the workflow commits exactly the expected files (`.aib_brain/<new marker>` and `logs/version_<target>_log.md`) and ends with a clean worktree.
- Negative-path checks
  - Introduce an extra per-version log file on the PR branch that does not exist on base and confirm the chosen policy (fail vs clean) works deterministically.

## Affected Documentation
| ref_id | document_title | path | reason_for_inclusion |
| --- | --- | --- | --- |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | Release bookkeeping script behavior is part of the script catalog (if maintained). |
| REF-0021 | OBS-01 - Logging | .aib_memory/docs/04 Technology/Observability/OBS-01.md | Release/per-version log artifacts are a logging/observability concern (if maintained). |

## Operational & Documentation Implications
- Operational
  - The workflow commits to PR branches; this can create PR noise and requires `contents: write` permission (already present).
  - If the base branch advances during the PR, the computed target version changes; the workflow should remain deterministic and handle reruns without failing.
- Documentation
  - If `.aib_memory/docs/` catalogs are maintained beyond placeholders, update CMP/OBS docs to reflect the intended behavior and guard policy.

## Risks
- Risk R1: The new logic accidentally allows a single PR to create multiple per-version logs (for different versions) when base advances.
  - Probability: Medium
  - Impact: Medium
  - Mitigation: implement Option B guard (PR-introduced only) and explicitly fail or clean based on a defined policy.
  - Owner (role): Repo maintainer
- Risk R2: If implementing auto-clean, the script could delete a human-authored log file.
  - Probability: Low
  - Impact: High
  - Mitigation: only delete logs that are both PR-introduced vs base and match strict “workflow-generated” signatures; otherwise fail with instructions.
  - Owner (role): Repo maintainer
- Risk R3: Edge cases where `logs/` does not exist on base or base ref fetch is shallow could cause `git ls-tree` lookups to fail.
  - Probability: Low
  - Impact: Medium
  - Mitigation: handle missing `logs/` tree gracefully and keep base fetch consistent (already fetched in workflow).
  - Owner (role): CI owner

## Dependencies / Externalities
- GitHub Actions runner must have `git` and `python3` available.
- The workflow must have permission to push to the PR branch (`contents: write`).
- Maintainer decision on per-version log retention and multi-log policy per PR.

## Open Questions & Next Actions
1. (Owner: Repo maintainer) Define the intended retention policy for `logs/version_v*_log.md` (historical vs transient). Due: before implementing the guard change.
2. (Owner: Repo maintainer) Decide the policy when the PR branch introduces a per-version log for a different marker than the newly computed target (fail vs clean). Due: before implementation.
3. (Owner: CI owner) Confirm whether any documentation in `.aib_memory/docs/` is expected to be updated as part of this change (CMP/OBS). Trigger: after implementation.

## Appendices
- Observed error message (from request background):
  - `Per-version log file precondition failed: ... Computed target is 'v1.0.6', but found: ['v1.0.5'] ...`
- Key code location
  - The guard that raises this error is in `scripts/release_bookkeeping.py` under the comment `# Guard against producing multiple per-version log files on the same PR branch.`

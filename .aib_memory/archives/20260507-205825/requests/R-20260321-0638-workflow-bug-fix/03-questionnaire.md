# Iteration Questionnaire — R-20260321-0638 / Iteration 03

## Business & Functional Questions

### QID-BF-001 — Persist commit-subjects output for audit/debug
**Intent:** Decide whether the PR commit-subjects text should be retained after the workflow run for audit/debugging.

**Rationale:** Retaining the file changes the safety posture: keeping it in-repo breaks cleanliness checks, while keeping it as an artifact requires explicit upload behavior. The answer determines whether we should only treat the commit-subjects file as transient input to bookkeeping or as a user-visible output.

**Impact Areas:** Scope, Operations, Timeline

**Answer Type:** single-select

**Options:**
- [x] A) Transient only; do not retain after run (recommended) — simplest and keeps worktree cleanliness strict
- [ ] B) Retain as a workflow artifact (uploaded) — keeps evidence without polluting the repo
- [ ] C) Retain in-repo (tracked file) — changes repo contents and review surface
- [ ] Other — (describe below)

**Constraints & Guards:** If C is chosen, define file location and review/retention expectations; otherwise prefer A/B.


## Architecture & Technical Questions

### QID-AT-001 — Fix strategy for `.aib_pr_commit_subjects.txt`
**Intent:** Choose the concrete mitigation strategy to prevent the workflow from leaving the repository worktree dirty.

**Rationale:** The workflow currently writes `.aib_pr_commit_subjects.txt` into the repository root and never deletes it, causing the final `git status --porcelain` check to fail. The chosen strategy must preserve the bookkeeping step’s ability to read commit subjects and keep the final cleanliness check meaningful.

**Impact Areas:** Requirements, Architecture, Operations, Timeline

**Answer Type:** single-select

**Options:**
- [x] A) Write outside worktree (e.g., `$RUNNER_TEMP/...`) and pass absolute path (recommended) — avoids worktree pollution entirely
- [ ] B) Keep writing in worktree, but delete before final cleanliness check — minimal diff, but still pollutes mid-run
- [ ] C) Add to `.gitignore` — fastest, but weakens cleanliness signal for this filename
- [ ] Other — (describe below)

**Constraints & Guards:** Option C should be avoided unless you accept reduced cleanliness signal.


### QID-AT-002 — Add defensive cleanup with `if: always()`
**Intent:** Decide whether to add a cleanup step that runs even if earlier steps fail.

**Rationale:** A cleanup step guarded with `if: always()` ensures transient files do not persist across partial/failed runs and prevents reruns from accumulating artifacts. It also reduces future regressions if step ordering changes.

**Impact Areas:** Operations, Timeline

**Answer Type:** single-select

**Options:**
- [x] A) Yes; add cleanup with `if: always()` (recommended) — more robust and future-proof
- [ ] B) No; rely on writing to temp only — acceptable if we never write inside the repo
- [ ] Other — (describe below)

**Constraints & Guards:** If you select B, confirm we will not write any transient files inside the repo worktree.


### QID-AT-003 — Preferred temp directory mechanism
**Intent:** Decide which runner temp directory mechanism to standardize on for transient files.

**Rationale:** GitHub Actions supports both `$RUNNER_TEMP` and `${{ runner.temp }}` patterns; choosing one consistently reduces quoting/path bugs and makes the workflow easier to maintain.

**Impact Areas:** Architecture, Operations

**Answer Type:** single-select

**Options:**
- [x] A) Use `$RUNNER_TEMP` in bash steps (recommended) — standard env var on hosted runners
- [ ] B) Use `${{ runner.temp }}` (YAML expression) — explicit runner context
- [ ] Other — (describe below)

**Constraints & Guards:** Ensure the chosen value is available in all steps that need the path.


## Appendix — Answer Encoding Rules
- Checkbox format:
  - Unchecked: `- [ ]`
  - Checked: `- [x]` or `- [X]`

- Single-select questions:
  - Exactly one option must be checked.
  - `Other` counts as an option if checked.

- If `Other` is checked:
  - Provide the explanation immediately under the `Other` line.

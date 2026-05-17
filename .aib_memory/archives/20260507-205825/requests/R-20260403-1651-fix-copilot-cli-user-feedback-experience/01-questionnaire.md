# Questionnaire - Iteration 01

## Business & Functional Questions

### QID-BF-001
**Intent:** Decide whether execution log files should be excluded from version control.
**Rationale:** Execution logs are transient operational artifacts generated on every action invocation. Committing them to the repository would create noise in pull requests and inflate the repository size. However, some teams prefer to commit logs for audit traceability. This decision affects `.gitignore` rules and the developer workflow.
**Impact Areas:** Operations, Observability, User Experience
**Answer Type:** single-select
**Options:**
- [x] A) Yes — add `logs/aib-action-*.log` to `.gitignore` (recommended) — keeps repo clean; logs remain local for developer reference
- [ ] B) No — commit execution logs to the repository — preserves audit trail in VCS but adds noise to diffs and PR reviews
- [ ] C) Conditional — gitignore by default, with a manual command to commit selected logs — balances cleanliness and traceability but adds workflow complexity
- [ ] Other — (describe here):
**Constraints & Guards:** If option B is selected, a log retention/cleanup mechanism should be considered to prevent unbounded repository growth.

### QID-BF-002
**Intent:** Decide the preferred directory location for execution log files.
**Rationale:** The log file location affects discoverability, separation of concerns, and `.gitignore` management. The `logs/` directory already exists and contains release version logs. Mixing execution logs with release logs may cause confusion. A subdirectory or a separate location under `.aib_memory/` would provide clearer separation but adds a new path convention.
**Impact Areas:** Operations, Observability, Architecture
**Answer Type:** single-select
**Options:**
- [x] A) `logs/` — same top-level directory as release logs (recommended) — simple; reuses existing directory; differentiated by filename prefix `aib-action-*` vs `version_*`
- [ ] B) `logs/sessions/` — dedicated subdirectory under `logs/` — clear separation from release logs; slightly deeper path
- [ ] C) `.aib_memory/logs/` — under the memory folder — keeps operational artifacts with other memory artifacts; may clutter `.aib_memory/`
- [ ] D) A configurable path via an environment variable or menu config — maximum flexibility but adds configuration complexity
- [ ] Other — (describe here):
**Constraints & Guards:** If option C is selected, `.aib_memory/logs/` must be added to the memory folder initialization logic. If option D is selected, a default path must still be defined.

### QID-BF-003
**Intent:** Decide the log retention policy for execution log files.
**Rationale:** Without a retention policy, log files accumulate indefinitely on the developer's workstation. For typical usage (a few actions per day), this is unlikely to be a problem for months. However, heavy usage or long-lived workspaces could accumulate hundreds of log files. The chosen policy affects whether cleanup automation is needed in this iteration or can be deferred.
**Impact Areas:** Operations, Observability, Cost
**Answer Type:** single-select
**Options:**
- [x] A) Unbounded — no automatic cleanup; developer manages manually (recommended) — simplest; appropriate for typical usage patterns; cleanup can be added in a future request if needed
- [ ] B) Count-based — keep last N log files (e.g., 50); delete oldest on new creation — predictable disk footprint; requires cleanup logic in this iteration
- [ ] C) Time-based — delete logs older than N days (e.g., 30) — aligns with common retention practices; requires cleanup logic and a scheduler or on-startup check
- [ ] D) Session-based — keep only logs from the current menu session; delete previous session logs on startup — minimal disk usage; loses historical context
- [ ] Other — (describe here):
**Constraints & Guards:** If option B, C, or D is selected, the cleanup logic must be implemented as part of this request's scope, increasing implementation effort. If option A is selected, a follow-up request may be created later for cleanup automation.

## Architecture & Technical Questions

No architecture or technical questions require user input at this time. Technical decisions (Popen tee pattern, threading for dual-stream, stdin inheritance) are covered in the analysis Solution Options section and do not require user arbitration.

## Appendix — Answer Encoding Rules

- Unchecked: `- [ ]`
- Checked: `- [x]` (lowercase x or uppercase X)
- Single-select: exactly one option must be checked; `Other` counts as a valid selection if checked.
- If `Other` is selected, provide a description in place of `(describe here):`.

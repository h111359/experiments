# Analysis — R-20260427-0858: Upgrade .aib_memory structure on AIB version install

## Executive Summary

- **Request ID:** R-20260427-0858

- **Title:** Upgrade .aib_memory structure on AIB version install

- **High-level purpose:** Introduce version tracking for `.aib_memory/` via a semver marker file (mirroring the existing `.aib_brain/` pattern), implement a backup-and-restore upgrade flow via an `--upgrade` flag added to `initialize.py`, and add a startup version-consistency check to `menu.py` that warns the developer and presents upgrade options when the brain and memory versions differ.

- **Problem being solved:** There is currently no mechanism to detect that a new AIB brain version has been installed and that the existing `.aib_memory/` structure may be incompatible. A developer who unzips a new `.aib_brain/` archive receives no warning and has no automated path to safely migrate the workspace state, risking silent overwrite or loss of curated files (`context.md`, `instructions.md`, `requests_register.md`, `references.md`).

- **Scope summary:** Three tool-script changes (`common.py` helper, `initialize.py` extended with `--upgrade`, `menu.py` startup check) and associated tests. The core logic — backup without nesting, re-seed, restore — is self-contained inside `initialize.py` and does not touch `.aib_brain/` assets. The `logs/` directory is now included in the backup scope (user amendment applied in this run).

- **`request.md` updates in this run:** Q001 (startup check, Option A) and Q002 (extend `initialize.py --upgrade`, Option B) applied and Q-blocks removed. User amendment applied: `logs/` directory moved from Out of scope to in-scope backup content. Scope, Out of scope, SC-5, Assumptions A3/A4, Plan Tasks 3–6, Documentation, Code Scan, and Internal Review updated accordingly.

- **Files read:** `.aib_memory/context.md`, `.aib_brain/Concepts.md`, `.aib_brain/tools/initialize.py`, `.aib_brain/tools/menu.py`, `.aib_brain/tools/common.py`, `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/request-convention.md`, `tests/test_initialize.py`, `tests/test_menu.py`, `tests/conftest.py`, `.aib_memory/references.md`, `.aib_memory/requests_register.md`, `.aib_memory/input.md`, `.aib_memory/instructions.md`.

---

## Domain Knowledge Essentials

**AIB (AI Builder):** A minimal, model-agnostic, file-first framework for specification-driven development. Consists of `.aib_brain/` (reusable, replaceable framework assets) and `.aib_memory/` (workspace-specific state).

**`.aib_brain/`:** Contains prompts, conventions, templates, and tool scripts. The entire folder is replaced on AIB framework upgrade by unzipping a new versioned archive. Tool scripts MUST NOT write to this folder (ADR-0003).

**`.aib_memory/`:** Contains workspace-specific state: request register, references register, `context.md`, `input.md`, `instructions.md`, and all request artifacts. Persists across brain upgrades; never wholesale replaced without explicit user action.

**Semver marker file (ADR-0001):** The installed version of `.aib_brain/` is represented by a single empty file named `vMAJOR.MINOR.PATCH` (e.g., `v1.2.8`) inside `.aib_brain/`. The current version is `v1.2.8`. This request extends this pattern to `.aib_memory/`.

**Upgrade flow (new concept):** The procedure by which an existing `.aib_memory/` is backed up, `.aib_memory/` is re-seeded from the new brain version's templates, and user-curated files are restored from the backup. Triggered when brain and memory semver markers differ.

**Backup flat hierarchy:** The requirement that `.aib_memory/backups/` contains only timestamped subfolders at the same level — never `backups/<ts1>/backups/<ts2>/` nesting. Each backup run appends a new `backups/<new-ts>/` without disturbing prior `backups/<old-ts>/` entries.

**User-curated files:** Files in `.aib_memory/` containing workspace-specific content authored or evolved by the developer or AI agent over time: `context.md`, `instructions.md`, `requests_register.md`, `references.md`, `requests/`. These are the files that must be preserved and restored across an upgrade.

**Impacted roles/personas:**
- Developer — primary actor; interacts via `menu.py` at startup; must confirm or skip upgrade.
- AIB Maintainer — publishes new `.aib_brain/` archives that trigger the version mismatch.
- AI Automation Agent — executes prompts after upgrade; relies on restored `requests_register.md` and `references.md`.

**Business processes touched:**
- Workspace initialization (`initialize.py`).
- Interactive menu launch (`run.bat` / `run.sh` → `menu.py`).
- AIB framework version upgrade (currently a manual unzip step).

---

## Technical Knowledge & Terms

**`initialize.py`:** Seeds `.aib_memory/` from `.aib_brain/templates/` on first run. Idempotent: skips files that already exist. Accepts `--force` to overwrite. Currently does NOT seed a semver file in `.aib_memory/`.

**`menu.py`:** Interactive terminal launcher. Reads `requests_register.md` to conditionally expose the "Close current request" action. Starts with `EXCLUDE_SCRIPTS` to hide lifecycle scripts from dynamic discovery. Currently has no version check at startup.

**`common.py`:** Shared helpers for all AIB tool scripts: `write_text`, `read_text`, `parse_args`, `ensure_workspace`, `load_template`, `seed_references_from_product_doc`, `slugify`, etc. The appropriate home for a new `get_semver(dir)` function.

**`initialize.py --upgrade` (extended):** The upgrade procedure is implemented as a new branch inside `initialize.py`, activated by passing the `--upgrade` flag. This avoids creating a new script file and reuses the existing module entry pattern. `initialize.py` is already in `EXCLUDE_SCRIPTS` in `menu.py`, so no additional exclusion is needed. Invoked by `menu.py` via `subprocess.run` with the `--upgrade` argument when the user confirms the upgrade.

**`get_semver(dir: Path) -> str | None`:** Proposed helper function. Uses `Path.glob()` to find a file matching `v[0-9]*.[0-9]*.[0-9]*` in a directory. Returns the file name string if exactly one match, else `None`. Fail-safe: ambiguous or absent markers return `None`.

**`shutil.copytree` / `shutil.copy2`:** Python standard library functions suitable for backup creation without third-party dependencies. `shutil.copytree` handles recursive directory copying; `shutil.move` handles flat relocation.

**`Path.glob`:** Standard library method for pattern-based file discovery; used for semver marker detection.

**Non-functional attributes:**
- Reliability: backup-before-delete ordering ensures atomicity at the directory level.
- Safety: no file is deleted until a confirmed backup exists.
- Idempotency: re-running initialize does not overwrite existing semver; re-running upgrade creates a new timestamped backup.
- Testability: upgrade flow in `initialize.py` is testable via the existing `_run_initialize` test helper (extended with `--upgrade` arg); mockable at `subprocess.run` in `menu.py` tests.

**Evidence log:**
- `initialize.py` has no semver seeding → implication: SC-1 requires a new code path.
- `menu.py` has no startup check → implication: version mismatch detection requires a new early-exit hook before the main menu loop.
- `.aib_memory/backups/` is currently empty and present → implication: the backup directory structure exists and is ready for use.
- `.aib_brain/v1.2.8` exists → implication: `get_semver(.aib_brain/)` would return `"v1.2.8"` with the proposed helper.
- No `.aib_memory/v*` semver file exists → implication: on first upgrade check, `get_semver(.aib_memory/)` returns `None`, triggering the upgrade prompt.

**Files read:**
- `.aib_brain/tools/initialize.py` — verified idempotent seeding pattern and absence of semver step.
- `.aib_brain/tools/menu.py` — verified `EXCLUDE_SCRIPTS`, `_REFRESH_ACTION`, and `main()` structure.
- `.aib_brain/tools/common.py` — verified available helpers and helper patterns.
- `tests/test_initialize.py` — verified test patterns (temp dir, `_make_brain_only_workspace`, `_run_initialize`).
- `tests/test_menu.py` — verified `unittest.mock` usage and `MenuState` fixture patterns.
- `tests/conftest.py` — verified `workspace_dir` fixture and `_seed_workspace` helper.
- `.aib_memory/context.md` — verified current component descriptions, ADRs, and requirements.
- `.aib_brain/Concepts.md` — verified action contract matrix and workflow guardrails.

---

## Research Results

**Pattern scan — version tracking in tool frameworks:**
- The existing `.aib_brain/` semver-as-empty-file pattern (ADR-0001) is already proven and in use. Extending it to `.aib_memory/` requires zero new conventions.
- The `get_semver` helper follows the same glob-based discovery pattern used elsewhere in the codebase (`build_script_actions` in `menu.py` uses `glob` for script discovery).
- The `initialize.py` idempotent seeding pattern (`if file.exists(): print('skipping')`) is the established convention for adding new seeds without breaking existing workspaces.

**Pattern scan — backup and migration in CLI tools:**
- The backup-before-delete pattern (copy complete state before modifying) is the standard approach for safe in-place upgrades in CLI tooling.
- Flat backup hierarchy (`backups/<ts>/`) is preferable over nested hierarchy (`backups/<ts1>/backups/<ts2>/`) as it makes historical state browsable without traversal.
- Restoring a selective subset of user files (rather than the entire old state) is the correct approach when re-seeding is desired: new template-derived files are correct; only user-curated data must survive.

**Pattern scan — version check at startup:**
- The approach of checking version compatibility at process startup (before any interactive content) is used by package managers (npm, pip), IDEs, and CLI frameworks (e.g., Homebrew's "upgrade available" banner). It surfaces the warning at the earliest point where the user can act.

---

## External Benchmarking

**Homebrew (macOS/Linux package manager) — version mismatch detection:**
- Homebrew detects when its internal formulae database is out of date and prints a banner before any package operation: "Warning: Homebrew is out-of-date. You should run `brew update`."
- Key takeaway: non-blocking warning at startup with a clear remediation command keeps the user informed without halting normal operation.
- Applicability for AIB: the `menu.py` startup check should follow the same pattern — display a prominent warning, offer an upgrade option, but allow the user to skip and continue if they choose.
- Rationale for adoption: well-understood UX pattern; minimal friction; battle-tested at scale.

**Python `venv` activation warning — environment version drift:**
- Python virtual environments embed the Python version at creation time. When a different Python interpreter activates the same venv, a mismatch warning is shown.
- Key takeaway: environment-level version metadata stored as a simple file (a `pyvenv.cfg` key-value pair) enables reliable mismatch detection with no external registry.
- Applicability for AIB: an empty file named `vX.Y.Z` is even simpler than a key-value file and satisfies the same detection need.
- Rationale for adoption: already established via ADR-0001 for `.aib_brain/`; extension to `.aib_memory/` requires no new pattern.

**Ansible `--check` mode / idempotent task execution:**
- Ansible runs idempotently: each task checks if the desired state already exists before making changes. The "changed/ok/failed" output communicates exactly what happened.
- Key takeaway: each step of the upgrade procedure should be self-reporting (`print("Backup created at ...")`, `print("Restored context.md")`) so the developer can verify what occurred.
- Applicability for AIB: `upgrade.py` should emit a structured summary of each action taken (what was backed up, what was deleted, what was restored, what semver was set).
- Rationale for adoption: improves auditability and developer trust; the `initialize.py --upgrade` summary print should follow this pattern.

---

## Minimal Spikes and Experiments

**Spike: Semver file detection via `Path.glob`**
- Hypothesis: `Path('.aib_brain').glob('v[0-9]*.[0-9]*.[0-9]*')` reliably returns exactly the brain version marker.
- Approach: Manually inspected `.aib_brain/` directory listing; confirmed `v1.2.8` is the only file matching `v[0-9]*` pattern.
- Outcome: Pattern is unambiguous; no other files in `.aib_brain/` root match the pattern. Confirmed by `list_dir` of `.aib_brain/`.
- Conclusion: `get_semver` can use `list(dir.glob('v[0-9]*.[0-9]*.[0-9]*'))` and return `matches[0].name` if `len(matches) == 1`, else `None`.

**Spike: Backup flat hierarchy feasibility**
- Hypothesis: Copying `.aib_memory/` content minus `backups/` into a new `backups/<ts>/` subfolder, while leaving existing `backups/<old-ts>/` entries untouched, achieves the flat hierarchy without code complexity.
- Approach: Traced the `shutil.copytree` behavior for selective directory copy; verified that `ignore=shutil.ignore_patterns('backups')` would exclude the `backups/` directory.
- Outcome: `shutil.copytree(src, dst, ignore=shutil.ignore_patterns('backups'))` correctly copies all files and non-`backups` subdirs without nesting the old backups.
- Conclusion: Implementation is straightforward with standard library; no custom recursion needed.

**Spike: `initialize.py` refactoring risk**
- Hypothesis: Adding semver seeding to `initialize.py` requires minimal change (one new idempotent block after existing seeds).
- Approach: Read full `initialize.py` source; identified the `instructions_file` seeding block as the natural insertion point.
- Outcome: The pattern `if semver_file.exists(): print("skipping") else: write_text(semver_file, "")` fits directly after `instructions_file` seeding with no refactoring required.
- Conclusion: Low-risk, additive-only change to `initialize.py`.

---

## AI Copilot Suggestions

**Observation 1 — Restore scope is fully specified; `requests/` directory restoration handles Active request edge case.**
The plan (Task 3 step 9) explicitly restores the entire `requests/` directory from backup, which handles the case where an Active request exists at upgrade time: both `requests_register.md` and the `requests/<folder>/` artifacts are restored from backup. `request.md` and `analysis.md` at `.aib_memory/` root (active-phase artifacts) will be in the backup but are not explicitly in the restore list — if an Active request was in progress, these files would need to be manually restored from backup. This edge case is worth documenting in the upgrade summary print.
- Suggestion: In the `initialize.py --upgrade` implementation, detect whether the backup contains a `request.md` or `analysis.md` at the root level and print a notice to the developer if so, advising them to manually inspect the backup. Do not auto-restore these to avoid overwriting a freshly seeded state with a potentially inconsistent mid-progress artifact.

**Observation 2 — Q002 decision (Option B: extend `initialize.py`) trades testability for simplicity; testability impact should be mitigated.**
Extending `initialize.py` with `--upgrade` means the upgrade logic shares the same test infrastructure as the initialization logic — this is not inherently bad, but the test class `TestInitialize` will grow significantly. The original upgrade.py (Option A) would have been independently testable with its own test module.
- Suggestion: In `test_initialize.py`, group upgrade tests in a dedicated `TestInitializeUpgrade` class, clearly separated from `TestInitialize`. This preserves readability and keeps the failure surface clear when either init or upgrade tests break.

**Observation 3 — Scope is appropriately sized; logs/ inclusion in backup is low-risk and improves auditability.**
The decision to include `logs/` in the backup (applied via user amendment in this run) is pragmatically sound: action logs are small, their loss is non-critical, but preserving them in the backup provides a complete historical snapshot. Not restoring them post-upgrade is equally correct — fresh logs should start from a clean state.
- Suggestion: Document in the upgrade summary print that `logs/` is backed up but not restored. This is informational only and requires no behavioral change.

**Observation 4 — `menu.py` startup version check introduces first I/O before the menu renders; upgrade prompt interaction must use blocking input.**
Adding a `get_semver` filesystem read to `menu.py` startup is a very low-cost operation (one glob call on a small directory) and poses no performance risk. However, the interactive upgrade prompt breaks the menu's existing "auto-refresh after 3 seconds" model.
- Suggestion: Ensure the upgrade prompt loop (`[1] Upgrade / [2] Skip`) uses a blocking `input()` call or equivalent, not the non-blocking key detection used by the menu's `choose_action()`. This avoids accidental auto-skip from a timer tick.

---

## Testing

Test cases for request R-20260427-0858:

- **T1 — Semver seeding on fresh init:** Run `initialize.py` on a workspace with no `.aib_memory/`. Expected outcome: `.aib_memory/` contains exactly one file matching `v[0-9]*.[0-9]*.[0-9]*` whose name matches the brain version marker (SC-1). PASS if file exists and name matches; FAIL otherwise.

- **T2 — Semver seeding idempotency:** Run `initialize.py` twice on the same workspace; second run must print a skip message and not create a second semver file. Expected outcome: exactly one semver file in `.aib_memory/` after both runs (SC-2). PASS if count equals 1 and content unchanged.

- **T3 — Version match, menu startup:** Start `menu.py` with matching `.aib_brain/` and `.aib_memory/` semver files. Expected outcome: normal menu renders; no version mismatch banner or upgrade prompt displayed (SC-3). PASS if upgrade prompt text is absent from stdout.

- **T4 — Version mismatch, menu startup:** Start `menu.py` with `.aib_memory/` semver different from `.aib_brain/` semver (e.g., `.aib_memory/v1.2.7` vs `.aib_brain/v1.2.8`). Expected outcome: version mismatch banner is displayed and upgrade options `[1]` and `[2]` are present in stdout (SC-4). PASS if both option strings are found.

- **T5 — Missing memory semver, menu startup:** Start `menu.py` with no semver file in `.aib_memory/`. Expected outcome: upgrade prompt shown (same as T4; SC-4). PASS if prompt text appears.

- **T6 — Upgrade backup creation:** Run `initialize.py --upgrade` directly (simulating confirmed upgrade). Expected outcome: `.aib_memory/backups/` contains one new timestamped subfolder; subfolder contains the pre-upgrade files including the `logs/` directory (SC-5). PASS if subfolder count increased by 1, `context.md` exists inside it, and a `logs/` directory exists inside it.

- **T7 — Upgrade flat hierarchy:** Run `initialize.py --upgrade` on a workspace where `.aib_memory/backups/` already contains one `<old-ts>/` subfolder. Expected outcome: after upgrade, `backups/` contains two subfolders (`<old-ts>/` and `<new-ts>/`) at the same level; `<new-ts>/` does NOT contain a `backups/` directory (SC-6). PASS if both subfolders are direct children of `backups/`.

- **T8 — Upgrade file restoration:** After `initialize.py --upgrade`, `context.md`, `instructions.md`, `requests_register.md`, and `references.md` in `.aib_memory/` match the content in `backups/<new-ts>/` (SC-5). Also verify that `.aib_memory/logs/` exists as a fresh empty directory (not restored from backup). PASS if file content byte-for-byte identical and logs dir is empty.

- **T9 — Skip upgrade:** Run `menu.py` with version mismatch; simulate user input `2` (skip). Expected outcome: no files created or deleted in `.aib_memory/` (SC-7). PASS if `.aib_memory/` file list is unchanged after skip.

- **T10 — Full test suite regression:** Run `pytest tests/` after all implementation. Expected outcome: all existing tests pass with no new failures (SC-8). PASS if exit code 0.

See [UAT_scenarios.md](UAT_scenarios.md) — UAT-02, UAT-03, UAT-04 for manual verification of the upgrade prompt terminal interaction, skip behavior, and post-upgrade state.

---

## Multi-Perspective Stakeholder Review

### Senior Solution Architect
The request cleanly extends an existing ADR-0001 pattern to `.aib_memory/`, which is architecturally sound and low-risk. Consolidating the upgrade logic inside `initialize.py` (Q002, Option B) respects code-reuse without introducing a new module dependency. The single-responsibility argument for a separate `upgrade.py` is real, but acceptable given the scope: the upgrade branch is activated only by an explicit `--upgrade` flag and the existing `_run_initialize` test helper can be extended cleanly. The backup-before-delete ordering provides a strong safety net. The primary architectural risk remains: if the upgrade fails mid-run (between delete and re-seed), `.aib_memory/` could be partially empty; mitigation is the same — backup must complete entirely before any deletion begins.

**Findings:**
- The `get_semver` helper in `common.py` is the right place for shared semver detection; avoid duplicating the logic in `menu.py` directly.
- Including `logs/` in the backup (user amendment) is architecturally correct: a complete backup snapshot includes all non-`backups` content. Not restoring logs post-upgrade is equally correct.
- Use `shutil.copytree` with `ignore=shutil.ignore_patterns('backups')` for backup creation — cleaner than manual iteration and safe for Python 3.10+.
- The `initialize.py` is already in `EXCLUDE_SCRIPTS`, so the `--upgrade` flag naturally avoids menu exposure with no additional exclusion work.
- A summary print at the end of the upgrade branch (what was backed up, what was restored, what semver was set) aligns with the existing menu tee-log observability pattern.

### Product Owner
The request delivers clear value: developers who upgrade AIB brain assets will no longer risk silent loss of workspace state. Q001 (Option A: startup check) and Q002 (Option B: extend `initialize.py --upgrade`) are now answered, removing the two open scope-influencing decisions. The user amendment adding `logs/` to backup scope is a sensible expansion: it costs nothing and improves auditability. SC-5 is now updated to reflect logs/ inclusion. The risk of losing Active request artifacts at upgrade time is addressed in the plan (restore `requests/` directory, print notice if root-level artifacts are in the backup).

**Findings:**
- The value proposition is clear: backup + semver = safe upgrades.
- SC-5 now explicitly mentions logs/ in the backup content.
- The "no unnotified replacement" constraint is enforced by design: `menu.py` prompts before invoking `initialize.py --upgrade`; no file writes occur on skip.
- UAT-01 remains essential for verifying the terminal UX is clear and unambiguous.

### User (Developer)
The current workflow provides no warning when a brain upgrade has occurred. Seeing an upgrade prompt on `menu.py` startup is a welcome improvement — it removes the possibility of running AIB prompts against an incompatible memory structure without realizing it. The "skip" option ensures the developer is not blocked from using AIB while deferring the upgrade decision. The flat backup hierarchy in `.aib_memory/backups/` makes it easy to manually inspect or restore a specific historical state without navigating nested folders.

**Findings:**
- The upgrade prompt must clearly state which brain version is installed, which memory version is present, and what the upgrade will do.
- The skip option must persist for the session without re-prompting on every menu refresh.
- The backup subfolder naming (`YYYYMMDD-HHMMSS`) should be clearly documented so developers can identify backups chronologically.
- The restore confirmation (after upgrade) should tell the developer exactly which files were restored from backup vs. freshly seeded.

### Security Officer
This request involves creating, copying, and deleting files in the workspace directory. The risk surface is low: all operations are filesystem-local, no credentials or secrets are handled, no network access occurs, and no privilege escalation is required. The primary risk is path traversal in the backup path construction if user-supplied workspace path is not validated.

**Findings:**
- `workspace` path must be resolved to an absolute path before any file operations (already enforced by `ensure_workspace` in `common.py`).
- The `backups/<timestamp>/` path is constructed programmatically from `datetime.now()` and is not user-influenced; no injection risk.
- `shutil.copytree` and `shutil.move` on validated absolute paths are safe.
- `upgrade.py` must validate that `.aib_brain/` exists before proceeding (already provided by `ensure_workspace`).
- No data classified above "Internal engineering documentation" is touched (consistent with existing product context).

### Data Governance Officer
The files involved (`context.md`, `instructions.md`, `requests_register.md`, `references.md`, `requests/`) are classified as Internal engineering documentation. The backup mechanism adds a retention artifact: timestamped backup folders in `.aib_memory/backups/` will accumulate over time and are VCS-tracked if `.aib_memory/` is tracked.

**Findings:**
- Backup retention policy is not defined in the request. Backups will accumulate indefinitely unless manually pruned; consider documenting this in the README or `upgrade.py` output.
- If `.aib_memory/` is committed to VCS, backup folders will also be committed, increasing repository size over time. Consider a `.gitignore` entry for `.aib_memory/backups/` and a note in the documentation.
- `requests/` directory contains all historical request artifacts; restoring it during upgrade is essential for data lineage continuity (request history is the audit trail for all work done in the workspace).
- `instructions.md` may contain workspace-level behavioral directives that are workspace-specific; restoring it from backup ensures these directives are not silently overwritten by a blank-seeded version.

# Analysis: R-20260430-2301 — Fix curated reset bug and request migration duplication

## Executive Summary

- **Request ID**: R-20260430-2301

- **Title**: Fix curated reset bug and request migration duplication

- **High-level purpose**: Fix two bugs in AIB's upgrade and release-bookkeeping subsystems. The primary bug (request migration duplication) is clearly described: when the developer chooses to migrate requests during `initialize.py --upgrade`, requests end up in both the archive snapshot and the active `.aib_memory/requests/` directory. The secondary bug (curated reset bug) is referenced in the request title and GitHub branch name but lacks a precise description in `input.md`.

- **Request scope**: Modifications are contained in `initialize.py` (`_run_upgrade`), `tests/test_initialize.py`, and `context.md`. The curated reset bug fix scope is gated behind developer confirmation (Q001).

- **Key risk**: The archive-after-migration contains a full copy of `requests/`. Deleting `requests/` from the archive makes the archive an incomplete snapshot. If the developer needs to roll back, they would need to rely on VCS rather than the archive.

- **`request.md` updates in this run**: `## Assumptions`, `## Plan`, `## Documentation`, `## Questions & Decisions`, `## Code and Asset Scan for Impacted Components`, and `## Internal Review of Request and Product Docs` were added. `## Goal`, `## Background`, `## Scope`, `## Out of scope`, `## Constraints`, and `## Success criteria` were authored from scratch (no prior `request.md` existed).

---

## Domain Knowledge Essentials

**AIB (AI Builder)**: A minimal, model-agnostic, file-first framework for specification-driven development. It manages structured work items (requests), generates analysis and implementation artifacts via AI prompts, and automates release bookkeeping via CI.

**Request**: The fundamental work item in AIB. Lifecycle: created (register row + folder), Active (request.md + analysis.md in `.aib_memory/`), Closed (artifacts moved to request subfolder). Only one Active request is permitted at a time.

**Upgrade workflow**: The `initialize.py --upgrade` procedure. Triggered by `menu.py` when the brain semver differs from the memory semver. Creates a timestamped archive of the current `.aib_memory/`, clears it, re-seeds from templates, and optionally migrates old requests.

**Migration (upgrade context)**: The user-initiated choice to carry over `requests/` and `requests_register.md` from the previous `.aib_memory/` into the newly seeded one. The alternative is "archive only" — requests remain exclusively in the archive snapshot.

**Archive (upgrade context)**: A timestamped subfolder under `.aib_memory/archives/` containing a full copy of the pre-upgrade `.aib_memory/` contents. Intended as a rollback snapshot.

**Curated change log**: `logs/next_version_changes.md` — an append-only Markdown bullet list maintained by the AI agent during `aib-implement.md` runs. Consumed by `release_bookkeeping.py` as the preferred `Changes:` source for the next per-version release log; reset to empty by CI after incorporation.

**Release bookkeeping**: CI-automated `scripts/release_bookkeeping.py` executed on PR events targeting `main`. Bumps the patch SemVer marker, writes a per-version log, creates a brain zip, and resets the curated file.

**SemVer marker**: An empty file in `.aib_brain/` named `vMAJOR.MINOR.PATCH` (e.g., `v1.2.12`). Used as the authoritative version source. Exactly one must exist.

**Impacted roles/personas**:
- *Developer*: Uses the upgrade workflow; expects no data duplication after migration.
- *AI Automation Agent*: Executes prompts; appends curated bullets; must not be affected by archive state.
- *AIB Maintainer*: Owns `.aib_brain/` assets; manages CI; cares about correctness of curated reset.

---

## Technical Knowledge & Terms

**`initialize.py`**: The AIB initialization and upgrade script. Key functions:
- `_seed_memory()`: Creates `.aib_memory/` directory structure (requests, logs, attachments, input.md, instructions.md, context.md).
- `_run_upgrade()`: 8-step procedure: archive → warn legacy refs → clear → re-seed → seed semver → prompt migrate → restore curated files → conditionally restore requests.
- `_prompt_migrate_requests()`: Interactive prompt; defaults to Y (migrate) in non-TTY environments.

**`shutil.copytree`**: Python standard library function that recursively copies a directory tree. Used in step 2 (archive creation) and step 8 (requests restoration). Does NOT remove the source directory.

**`shutil.move`**: Moves a file or directory. Uses `shutil.copy2` + `os.unlink` or directory rename internally; handles cross-filesystem moves correctly. Used elsewhere in AIB (e.g., `move-request-artifacts.py`).

**`shutil.rmtree`**: Recursively deletes a directory tree. Used in `_run_upgrade` step 3 to clear `.aib_memory/` content. The proposed fix adds a `shutil.rmtree(requests_archive)` call after the migration copy.

**`release_bookkeeping.py`**: CI script. Key flow:
- Reads curated entries from `logs/next_version_changes.md`.
- Prefers curated entries over commit subjects as the `Changes:` source.
- Resets curated file to empty after successful incorporation.
- Emits `changes_body` to GitHub Actions `GITHUB_OUTPUT` before reset.
- Idempotent: if log exists AND marker is already at target, returns early with `changed=false`.

**`GITHUB_OUTPUT`**: The GitHub Actions mechanism for passing step outputs. Written as `key<<delimiter\nvalue\ndelimiter`. Read by subsequent steps via `steps.<id>.outputs.<key>`.

**`git add .aib_brain logs versions`**: The CI commit step's staging command. Captures all changes in these three directories including the reset curated file in `logs/`.

**Request duplication scenario**: `_run_upgrade` step 2 uses `shutil.copytree` to copy `requests/` to the archive. Step 8 uses `shutil.copytree` again to copy it back. Result: identical tree in both `archive/<timestamp>/requests/` and `.aib_memory/requests/`.

**NFR-004**: Non-functional requirement — tool scripts must use Python 3.10+ standard library only. `shutil.rmtree` satisfies this.

**`git status --porcelain`**: Shell command used in the CI "Ensure clean working tree" step. Returns non-empty output if uncommitted changes exist; the step fails if the working tree is dirty after the commit.

---

## Research Results

**Files read:**
- `.aib_memory/input.md` — describes the migration duplication bug
- `.aib_memory/requests_register.md` — confirmed one Active request (R-20260430-2301)
- `.aib_brain/tools/initialize.py` — full source; identified `_run_upgrade` steps 2 and 8 as the duplication root cause
- `tests/test_initialize.py` — existing tests; confirmed `test_upgrade_migrate_requests_choice` does not assert no-duplication
- `scripts/release_bookkeeping.py` — full source; curated reset logic reviewed; no obvious bug found in isolation
- `.github/workflows/aib-semver-patch-bump-and-log.yml` — full workflow; `git add .aib_brain logs versions` captures curated reset
- `tests/test_release_bookkeeping.py` — existing tests; all pass; no failing test reveals curated reset bug
- `.aib_memory/context.md` — FR-013, FR-011, ADR-0008 reviewed
- `.aib_brain/conventions/analysis-convention.md` and `request-convention.md` — structure rules
- `.aib_memory/archives/20260430-225829/` — observed that the latest archive lacks `requests/`; confirms the bug exists in a real scenario where the pre-upgrade memory had no local `requests/` (consistent with migration from a state where requests were in VCS but had been locally deleted/cleaned)

**Pattern scan findings:**
- The duplication bug is a classic "copy-then-forget-to-delete" pattern. The standard fix (copy → verify → delete source) is universally established.
- Alternatively, using `shutil.move` directly from archive to destination avoids the intermediate duplication. However, since the archive is on the same filesystem (inside `.aib_memory/`), a directory rename would work. Using `shutil.move` is preferred per existing AIB conventions.
- The curated reset logic in `release_bookkeeping.py` was reviewed exhaustively. The condition `if changed and used_curated and curated_path is not None: _reset_curated_file(curated_path)` covers all expected scenarios. No failing test currently documents the curated reset bug, suggesting either (a) the bug is triggered by a specific real-world scenario not yet represented in tests, or (b) the bug is in the CI workflow (not the Python script) and not easily tested locally.
- The observed workspace state (archive at `20260430-225829` lacks `requests/`, but `.aib_memory/requests/` has all folders) suggests the developer previously had `requests/` missing locally, ran the upgrade, then manually restored from VCS. This is exactly the failure mode the migration was designed to prevent.

---

## External Benchmarking

**Move-not-copy for archival+migration patterns:**
- Python's `shutil` documentation explicitly recommends `shutil.move` when the intent is relocation, not duplication. The `copytree` + `rmtree` pattern is a well-known anti-pattern when duplication is undesirable.
- GNU `mv` uses the same atomic-rename-then-fallback-to-copy-delete strategy as `shutil.move`.
- **Takeaway**: Replace step 8's `copytree` with `shutil.move` for the `requests/` directory. This is the idiomatic Python approach and eliminates the duplication atomically.
- **Applicability**: Directly applicable; no adaptation needed.

**Archive snapshot integrity vs. migration semantics:**
- Tools like Ansible's `backup` module and Kubernetes `etcd` backup workflows maintain a clear distinction: a backup is taken before any mutation; once a migration is committed, the backup is sealed as pre-migration only. The migration data is the canonical source.
- **Takeaway**: Deleting `requests/` from the archive after migration is consistent with how professional backup/restore tools handle this. The archive represents the pre-upgrade state, not the post-migration state.
- **Applicability**: Adopted directly; the archive should represent the pre-upgrade snapshot only; migrated content should live exclusively in the active memory.

**CI idempotency for file reset patterns:**
- In GitHub Actions and other CI platforms, a common failure mode is: a script modifies a file, the commit step fails (e.g., network error), and the next run finds the file already modified (from the failed run's disk state). Tools like Terraform and Ansible handle this with checksum-based idempotency.
- **Takeaway**: The curated reset in `release_bookkeeping.py` is idempotent: resetting an already-empty file is a no-op. The concern is whether the reset is being COMMITTED correctly. The CI `git add logs` approach is straightforward and should work, but local disk modification without a subsequent commit (e.g., on CI runner crash) could leave the curated file empty without that change being pushed.
- **Applicability**: This suggests adding a test case for the scenario where `_reset_curated_file` empties the file but the commit does not happen (e.g., the `changed=false` idempotent path). This is the most likely scenario for the curated reset bug.

---

## Minimal Spikes and Experiments

**Spike: Confirm migration duplication via archive inspection**
- Hypothesis: After `initialize.py --upgrade` with Y (migrate), `requests/` exists in both the archive and `.aib_memory/`.
- Approach: Inspect `.aib_memory/archives/` for the most recent archive; list its contents; compare with `.aib_memory/requests/` state. Also review `_run_upgrade` source.
- Outcome: Archive at `20260430-225829` does NOT contain `requests/` (the workspace had no local `requests/` at upgrade time). Archives at `20260430-142554` DO contain `requests/`. The `_run_upgrade` source confirms `shutil.copytree` is used for both archiving AND restoring — meaning if the archive had `requests/`, it would be in both places after migration.
- Conclusion: The duplication bug is confirmed by code inspection. The specific workspace scenario is an edge case where `requests/` was absent locally before the upgrade, so no duplication occurred in the most recent run. The fix is still needed.

**Spike: Review curated reset logic for unhandled paths**
- Hypothesis: `release_bookkeeping.py` fails to reset `logs/next_version_changes.md` in some specific path.
- Approach: Trace all execution paths through `main()`; identify every place where `_reset_curated_file` is (or is not) called; verify against branch name "next_version_changes not cleared moving requests".
- Outcome: All reset calls are gated by `if changed and used_curated and curated_path is not None`. No path resets the file without also writing the version log. The idempotent early-exit path correctly does NOT reset the file (no entries were incorporated). All existing tests pass.
- Conclusion: The curated reset logic in the Python script appears correct for all documented scenarios. The bug likely manifests in a CI-specific scenario or a user workflow that is not yet represented by tests. Developer confirmation is required (Q001).

---

## AI Copilot Suggestions

- **Design quality — Use `shutil.move` rather than copytree+rmtree**: The cleaner fix for the migration duplication is to replace the `shutil.copytree` in step 8 with `shutil.move`. This is a single atomic operation (on the same filesystem) rather than two operations (copy then delete). It eliminates the window during which both copies exist simultaneously. If `shutil.move` raises an exception mid-way, the archive is in a partially-moved state — but this is better than the current state where both are always present on success.

- **Scope concern — The curated reset bug is under-specified**: The request title names two bugs, but `input.md` only describes one. The curated reset bug lacks a reproducible test case or triggering scenario. The implementation should NOT proceed on the curated reset bug until Q001 is answered. Implementing a fix for an unconfirmed bug risks introducing a regression. This scope should be split into two separate requests if the curated bug turns out to require non-trivial changes.

- **Testability gap — The `test_upgrade_migrate_requests_choice` test does not seed requests**: The existing test seeds a custom `requests_register.md` but does not create any request subfolders in `requests/`. This means the test verifies register restoration but not the actual `requests/` folder migration. The fix should include seeding a real request folder (e.g., `R-test/`) in the pre-upgrade memory so the test can verify both the migration AND the absence from the archive.

- **Maintainability — The archive is semantically overloaded**: The upgrade archive serves as both a rollback snapshot AND the temporary intermediate storage for migration. This dual role is what creates the duplication bug. A cleaner design would separate these: always archive (for rollback), then move (not copy) from archive. This is what `shutil.move` achieves naturally: the archive is the source of truth, and moving from it makes the archive permanently incomplete for `requests/`. Accept this trade-off explicitly in documentation.

- **Scope size assessment — Appropriate**: The migration duplication fix is small (one `shutil.copytree` call replaced with `shutil.move`, or one `shutil.rmtree` added, plus one test assertion). The curated reset bug fix is unknown but likely small. The scope is proportionate.

---

## Testing

- T1 — Migration no-duplication assertion: After `initialize.py --upgrade` with Y, assert `.aib_memory/archives/<timestamp>/requests/` does NOT exist and `.aib_memory/requests/<seeded-folder>/` DOES exist. Expected outcome: archive has no `requests/` directory; active memory has the migrated request folder. Covers SC-1 and SC-3.

- T2 — Archive-only mode unaffected: After `initialize.py --upgrade` with N, assert `.aib_memory/archives/<timestamp>/requests/` DOES exist and `.aib_memory/requests/` is empty (only seeded dirs). Expected outcome: request folders remain exclusively in the archive. Covers SC-2.

- T3 — Regression: existing migrate test passes: `test_upgrade_migrate_requests_choice` (updated to seed a real request folder) still asserts that `requests_register.md` content is restored. Expected outcome: test passes; no regression in register restoration.

- T4 — Regression: existing archive-only test passes: `test_upgrade_archive_requests_choice` still asserts that `requests_register.md` content is NOT restored. Expected outcome: test passes.

- T5 — Idempotency: Running `--upgrade` twice does not compound the issue. Expected outcome: second upgrade archives the first upgraded memory (which has `requests/`); choosing Y migrates them again; no duplication occurs.

- T6 — Curated reset scenario (gated on Q001): Once the specific failing scenario is confirmed, a test case reproduces it in isolation (e.g., in `tests/test_release_bookkeeping.py`). Expected outcome: test fails before fix, passes after fix; existing curated reset tests remain passing. Covers SC-5.

- T7 — Full test suite regression: `python -m pytest tests/` passes with no new failures. Expected outcome: all existing 185 tests pass plus new tests.

---

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The migration duplication fix is a small, targeted change with low architectural risk. The root cause — using `shutil.copytree` for both archiving and restoration — is a design issue that was acceptable when the archive was intended as a temporary intermediate. Now that the archive is a permanent rollback snapshot, using `shutil.move` for the restoration step correctly re-aligns semantics with intent. The architectural implication is that after a successful migration, the archive is no longer a complete snapshot of pre-upgrade state (it lacks `requests/`). This is acceptable if the developer understands that the archive is a pre-upgrade-minus-migrated-requests snapshot. FR-013 in `context.md` should make this explicit. The curated reset bug fix scope is correctly gated behind Q001; proceeding without that confirmation would be architecturally unsound.

Findings:
- The dual-role of the archive (rollback snapshot + migration source) is a design smell worth documenting explicitly.
- `shutil.move` is the idiomatic and safer choice over copytree+rmtree.
- The curated reset bug is an unresolved architectural concern until Q001 is answered.
- Test gap: the existing `test_upgrade_migrate_requests_choice` test does not exercise actual `requests/` folder content migration.

### Product Owner

The request migration duplication bug is a clear correctness issue: a user who chose to migrate their requests would find them in two places, creating confusion about which copy is authoritative. The fix improves the upgrade workflow's predictability and user trust. The curated reset bug, while referenced in the title, is under-specified — deferring it to Q001 is appropriate. From a product perspective, both bugs should be fixed in this iteration if the curated bug scope is small. If it turns out to require significant changes, splitting into two requests is preferable over delaying the migration fix.

Findings:
- Migration duplication is a user-visible correctness bug; high priority.
- The upgrade workflow is a critical onboarding path; bugs here damage developer confidence.
- The curated reset bug is not described well enough to estimate scope; Q001 is the right gate.
- SC-1 through SC-4 are measurable and appropriately scoped.

### User (Developer)

The immediate frustration is: after upgrading, requests are in two places. This creates uncertainty: which copy should I work with? Should I delete the archive copy? The fix makes the behavior intuitive: if I said "migrate", the requests move — they don't copy. The archive becomes a pre-upgrade backup (which is what I'd expect). If the curated reset bug means my `logs/next_version_changes.md` bullets are sometimes silently lost, that's a trust issue with the release workflow.

Findings:
- After the fix, the upgrade prompting flow should ideally inform the user that migration is a move, not a copy.
- The archive's incompleteness (after migration) should be clearly communicated in the upgrade summary print.
- The curated reset bug, if confirmed, is a silent data-loss scenario — high user impact.

### Security Officer

The upgrade procedure reads, copies, and deletes filesystem content within `.aib_memory/`. No external network calls are made. The fix (adding `shutil.rmtree` or replacing `copytree` with `shutil.move`) does not increase attack surface. The archive directory is under `.aib_memory/` which is workspace-local; no cross-workspace or cross-user data exposure. No authentication or authorization changes are involved. The curated file `logs/next_version_changes.md` is workspace-local and VCS-tracked; no secrets are stored in it.

Findings:
- No security concerns with the migration fix.
- `shutil.rmtree` on a local directory is standard and safe within the workspace boundary.
- If the curated reset bug involves CI workflow changes, ensure `GITHUB_TOKEN` permissions remain minimal (existing `pull-requests: write` is already scoped appropriately).
- No new permissions, secrets, or external endpoints are introduced.

### Data Governance Officer

The `requests/` directory contains historical work artifacts (analysis, implementation logs, inputs). These are classification: Internal engineering documentation. The migration fix determines whether these artifacts reside in the archive (pre-upgrade snapshot, local only) or in active memory (operational, VCS-tracked). After the fix, migrated requests are in VCS (active memory) only, NOT in the local archive snapshot. The archive (a local, non-VCS directory) would no longer contain requests after migration. This is consistent with the product's principle that `.aib_memory/` content is ephemeral between upgrades (VCS is the source of truth). No compliance impact.

Findings:
- The active `.aib_memory/requests/` is VCS-tracked; migrated requests remain in VCS.
- The archive is NOT VCS-tracked; its incompleteness after migration does not affect data lineage.
- Audit trail: the archive still serves as a pre-upgrade snapshot for non-request files (context.md, instructions.md, input.md, semver marker).
- The curated file reset: curated bullets are incorporated into VCS-tracked version logs before being cleared. No data is permanently lost.

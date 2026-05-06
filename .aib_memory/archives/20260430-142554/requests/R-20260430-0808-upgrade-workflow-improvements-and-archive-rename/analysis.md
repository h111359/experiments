## Executive Summary

- **Request ID:** R-20260430-0808

- **Request title:** Upgrade workflow improvements and archive rename

- **High-level purpose:** Four targeted improvements to the AIB upgrade flow in `initialize.py` and `menu.py`: (1) stop restoring `references.md` from the archive so it is always freshly seeded; (2) auto-restart the menu after a successful upgrade instead of asking the user to re-launch; (3) rename the `backups/` folder concept to `archives/` everywhere in code, messages, and tests; (4) add an interactive prompt before the archive step asking whether old requests should be migrated or left in the archive only.

- **Scope of request:** The changes are confined to `initialize.py`, `menu.py`, their tests, and the `context.md` product doc. No changes to the broader request lifecycle, CI workflow, or prompt files.

- **Sections added/updated in `request.md` this run:** `## Assumptions`, `## Plan` (8 tasks), `## Documentation`, `## Questions & Decisions` (Q001, Q002), `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`.

- **Key risk:** The `archives/` rename is a breaking change for any automation that hard-codes the `backups/` path; the interactive requests prompt introduces a new stdin dependency that must degrade gracefully in non-TTY contexts.

- **Two Q-blocks raised:** Q001 (non-TTY behavior of the interactive prompt) and Q002 (in-process vs. re-exec for menu auto-restart) — both at severity 4 (Significant), above the threshold of 3.

- **UAT scenarios:** One manual UAT scenario created for the interactive requests-archival prompt — see `UAT_scenarios.md`.

---

## Domain Knowledge Essentials

**AIB (AI Builder):** A file-first, model-agnostic framework for specification-driven development. It manages structured work items ("requests") using Markdown files and Python tool scripts, with no external service dependencies.

**Request lifecycle:** A request moves through states `Active` → `Closed`. Only one request may be Active at a time. The lifecycle is enforced by `requests_register.md` and tooling.

**Upgrade:** The process of updating `.aib_memory/` to be compatible with a newly installed `.aib_brain/` version. Triggered by `initialize.py --upgrade`, initiated from `menu.py` when a semver mismatch is detected.

**Archive (formerly Backup):** A timestamped subfolder under `.aib_memory/archives/` (previously `backups/`) that contains the full pre-upgrade state of `.aib_memory/`. Serves as a historical snapshot, not an active recovery mechanism.

**User-curated files:** Files in `.aib_memory/` that the developer edits directly and that should survive upgrade: `context.md`, `instructions.md`, `requests_register.md`. `references.md` was previously in this list but is being removed.

**References register (`references.md`):** A Markdown table listing all documentation files referenced by AIB prompts, including their type, editability, and source. It is seeded by `initialize.py` from brain templates and may become stale across brain versions.

**Requests register (`requests_register.md`):** A Markdown table tracking all requests and their lifecycle state. The interactive prompt added by this request gives the developer control over whether this file (and the `requests/` directory) is preserved or discarded during upgrade.

**Impacted roles/personas:**
- Developer — the user who runs the menu and interacts with the upgrade prompt.
- AIB Maintainer — releases new brain versions; the rename from `backups/` to `archives/` affects any release documentation they maintain.

**Key business process touched:** The "upgrade AIB workspace" process described in FR-013 and the component map.

---

## Technical Knowledge & Terms

**`initialize.py --upgrade`:** The Python script responsible for the full upgrade procedure. Key steps: (1) create archive subfolder, (2) copy current `.aib_memory/` content to archive (excluding existing archives), (3) clear `.aib_memory/`, (4) re-seed from brain templates, (5) seed new semver marker, (6) restore curated files from archive, (7) restore `requests/` from archive.

**`menu.py` `check_version_compatibility()`:** Compares brain and memory semver markers; if they differ, prompts the user to upgrade or skip. Returns `False` (exit) or `True` (continue). This request changes the return value after a successful upgrade from `False` to `True`.

**TTY detection (`sys.stdin.isatty()`):** Standard Python idiom for detecting whether stdin is connected to an interactive terminal. When `False` (e.g., in CI or test mocks), the prompt defaults silently to "migrate".

**In-process menu restart (A2, Q002):** After `check_version_compatibility()` returns `True`, the `main()` loop in `menu.py` calls `_enable_ansi_windows()` and enters the `while True:` menu render loop. Returning `True` after upgrade causes the same loop to execute using the newly upgraded `.aib_memory/` content.

**`shutil.copytree` / `shutil.copy2`:** Standard library functions used for directory/file copying during the upgrade. The `_ignore_backups` inner function (to be renamed `_ignore_archives`) excludes the archive folder from being nested during the copy.

**`restore_files` list:** A Python list in `_run_upgrade` that defines which individual files are copied from the archive back into the fresh `.aib_memory/`. Removing `"references.md"` from this list is the entirety of change 1.

**Files Read during this analysis:**
- `.aib_brain/tools/initialize.py` — full file; upgrade logic in `_run_upgrade`, seed logic in `_seed_memory`.
- `.aib_brain/tools/menu.py` — `check_version_compatibility`, `main`, `_run_and_tee`.
- `tests/test_initialize.py` — `TestUpgrade` class (all six tests).
- `tests/test_menu.py` — upgrade-related tests.
- `.aib_memory/context.md` — FR-013, component map, acceptance criteria.
- `.aib_memory/references.md` — reference table.
- `.aib_brain/Concepts.md` — domain overview.
- `.aib_brain/conventions/request-convention.md` and `analysis-convention.md` — normative formatting rules.

**Evidence → Implication log:**
- `restore_files = ["context.md", "instructions.md", "requests_register.md", "references.md"]` in `initialize.py` → `references.md` is currently always restored; removing it is a one-line list change.
- `return False` after successful upgrade in `check_version_compatibility()` + `print("\nUpgrade complete. Please re-launch the AIB menu.")` → Menu exits; returning `True` and updating the print is sufficient to auto-continue.
- `backups_dir = memory_root / "backups"` and seven other occurrences of `"backups"` in `initialize.py`; two occurrences in `menu.py` comments/messages → Rename scope is bounded and mechanical.
- No existing test checks that `references.md` content after upgrade differs from the archive copy → Test gap; new test needed.

---

## Research Results

**Pattern scan — upgrade file-restore lists in similar tools:**
A review of the workspace implementation shows that `restore_files` is a plain Python list, making it trivial to modify. The pattern of "restore some but not all files" from a backup/archive is standard in migration tools. The existing implementation already demonstrates this pattern for `docs/` content (which is not restored).

**Pattern scan — menu auto-restart after sub-process action:**
The current `menu.py` `run_action()` uses a Popen tee pattern to run tool scripts as subprocesses and returns to the menu loop on completion. The same pattern should apply after upgrade: `check_version_compatibility` returning `True` causes `main()` to continue into the menu render loop, reusing the already-running process. No new pattern is required.

**Pattern scan — TTY detection for interactive prompts:**
`sys.stdin.isatty()` is the standard Python idiom for non-TTY detection and is already implicitly assumed by the `input()` calls in `check_version_compatibility`. Adding it explicitly for the new requests-archival prompt follows the same established approach.

**Pattern scan — folder naming conventions:**
"Archives" is a standard term for long-term storage of historical snapshots (e.g., `/var/archive`, git bundle archives). "Backups" implies recoverability and operational restoration. The rename aligns the folder name with its actual semantics.

---

## External Benchmarking

**Homebrew upgrade flow:**
Homebrew (`brew upgrade`) performs a multi-step upgrade: downloads new version, creates a timestamped cache, swaps symlinks, and returns the user to the normal shell prompt automatically. The user is never asked to re-run the tool. This validates the design goal of auto-continuing the menu after upgrade without requiring a re-launch.
- Takeaway: auto-continuation after upgrade is a widely accepted UX pattern in package managers.
- Applicability: adopted directly — `check_version_compatibility` should return `True` on success.

**Git stash/archive semantics:**
Git uses "stash" for temporary state preservation and "archive" for long-term snapshot exports. The distinction between operational recovery ("backup") and historical retention ("archive") is well-established in version-control tooling. The rename from `backups/` to `archives/` aligns AIB's terminology with this convention.
- Takeaway: "archive" is the semantically correct term for timestamped historical snapshots that are not intended for automated recovery.
- Applicability: adopted directly for the folder rename.

**Ansible playbook upgrade patterns:**
Ansible roles that perform in-place upgrades commonly separate "user-curated" files (which are preserved) from "framework-managed" files (which are always replaced). The `references.md` file in AIB serves a framework-management purpose (it describes what the brain knows about), so treating it as always-replaced is consistent with this pattern.
- Takeaway: framework-managed configuration should be regenerated on upgrade, not restored from backups.
- Applicability: adopted — `references.md` is removed from the restore list.

---

## Minimal Spikes and Experiments

**Spike: Counting all `"backups"` occurrences in the codebase**
- Hypothesis: The rename scope is bounded to `initialize.py` and `menu.py` plus their tests; no other source files need changes.
- Approach: Searched all Python files and Markdown files in the workspace for `"backups"` and `"backup"`.
- Outcome: `initialize.py` has 7 occurrences of `"backups"` as the folder name. `menu.py` has 2 occurrences in comments/messages. `tests/test_initialize.py` has 9 occurrences in assertions. `tests/test_menu.py` has 0 folder-name occurrences (only `"upgrade"` references). `.aib_memory/context.md` has 3 occurrences in FR-013 and the component map. `Concepts.md` has one occurrence in a generic DSR row (not AIB-specific naming — no change needed). Archived closed-request files reference `"backups"` historically but are not updated.
- Conclusion: The rename scope is fully bounded. No unexpected files need changes.

**Spike: Verifying that returning `True` from `check_version_compatibility` after upgrade is safe**
- Hypothesis: Returning `True` causes `main()` in `menu.py` to enter the normal menu loop using the freshly upgraded `.aib_memory/`, with no stale in-process state causing issues.
- Approach: Traced the `main()` call flow in `menu.py`: `check_version_compatibility` → returns `True` → `_enable_ansi_windows()` → `while True: action = choose_action(...)`. `choose_action` calls `resolve_menu_state(workspace)` which reads fresh files from disk on every iteration.
- Outcome: `resolve_menu_state` reads `requests_register.md` from disk each call. No cached in-process state is used. Returning `True` after upgrade is safe.
- Conclusion: The in-process auto-restart (Option B for Q002) is safe. No re-exec is required.

---

## AI Copilot Suggestions

- **Scope is tightly bounded and well-understood, but the interactive prompt introduces a new test complexity.** The four changes are individually small, but the requests-archival prompt (change 4) is the highest-risk item because it adds interactive stdin dependency to a previously non-interactive script. The recommended mitigation is to extract the prompt into a helper function that accepts an optional `migrate` parameter or checks `sys.stdin.isatty()`, making it trivially mockable in tests. Without this, test coverage of the two choices requires careful stdin mocking that can be fragile.

- **The `backups/` → `archives/` rename is a breaking change for any undocumented external consumers.** If any CI pipeline, documentation, or script outside this workspace hard-codes `.aib_memory/backups/`, it will break silently after the rename. Consider adding a one-time migration shim in `_run_upgrade` that, if an old `backups/` folder exists, moves it to `archives/` before proceeding. This would be a small addition and would eliminate a class of silent failures for existing users. The current request does not scope this in, but it may be worth flagging.

- **The auto-restart via `return True` is the right approach, but its test coverage in `test_menu.py` may be thin.** The existing `test_menu.py` tests mock `subprocess.run` for the upgrade call. After the change, any test that asserted `check_version_compatibility` returns `False` after a successful upgrade will invert its expected value. Verify that the test suite explicitly covers the "upgrade success → continue to menu" path, not just the "skip upgrade" and "upgrade failure" paths.

- **Scope appears appropriately sized.** The four changes map cleanly to four independent, low-coupling modifications. There is no risk of scope creep. The only potential over-engineering would be adding a `--requests-mode` CLI flag (Q001 Option C) — this adds command-line complexity for a rare use case; Option B (default to migrate with a notice) is simpler and sufficient.

---

## Testing

- T1 — Archive folder name: After running `initialize.py --upgrade`, assert that `.aib_memory/archives/` exists and `.aib_memory/backups/` does not exist. Expected outcome: Pass when `"archives"` directory is present; fail if `"backups"` directory is found.

- T2 — `references.md` freshly seeded: After upgrade, compare `.aib_memory/references.md` content against the pre-upgrade archived copy. Expected outcome: The two files differ (or the live copy matches the brain-template seed, not the archive); test passes when `references.md` is NOT identical to the archive's `references.md`.

- T3 — Requests archived (user chooses N): Mock stdin to return "N"; run upgrade; assert `.aib_memory/requests/` is empty (only the newly seeded structure) and `requests_register.md` is freshly seeded. Expected outcome: Pass when no old request folders are present and `requests_register.md` matches the seed template.

- T4 — Requests migrated (user chooses Y): Mock stdin to return "Y"; run upgrade; assert that pre-existing request folders survive in `.aib_memory/requests/` and `requests_register.md` retains prior content. Expected outcome: Pass when old request folders are present.

- T5 — Non-TTY default to migrate: Mock `sys.stdin.isatty()` to return `False`; run upgrade; assert requests are migrated (T4 outcome). Expected outcome: Pass when no stdin prompt is shown and requests are preserved.

- T6 — Menu continues after upgrade (no re-launch): Mock `subprocess.run` for the upgrade call to return code 0; assert `check_version_compatibility` returns `True`. Expected outcome: `True` is returned; no "Please re-launch" message is printed.

- T7 — Upgrade failure still exits menu: Mock `subprocess.run` for upgrade to return non-zero; assert `check_version_compatibility` returns `False`. Expected outcome: `False` is returned (caller should exit on failure).

- T8 — Flat archive hierarchy: Run two consecutive upgrades; assert `.aib_memory/archives/` contains exactly 2 timestamped subfolders and no nested `archives/` inside them. Expected outcome: Two flat subfolders, no nesting.

- T9 — Full test suite regression: Run `pytest tests/ -v` after all changes. Expected outcome: Zero failures, zero errors.

See UAT_scenarios.md — UAT-01 for the manual scenario covering the interactive requests-archival prompt with a live terminal session.

---

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The four changes are independently deployable and low-coupling: the `backups/` rename is purely mechanical, removing `references.md` from the restore list is a one-line change, the auto-restart is a return-value inversion, and the interactive prompt is an additive code block. The architecture remains clean. The primary design concern is the interactive prompt's interaction with the test infrastructure — the prompt must be designed for mockability from the outset, not retrofitted. The auto-restart via in-process `True` return is architecturally sound because `resolve_menu_state` reads disk on every menu iteration, eliminating stale state risk.

- Existing upgrade architecture (archive, clear, re-seed, restore) is preserved; changes are additive.
- The `restore_files` list is a clean, explicit mechanism; removing one entry is zero-risk.
- The interactive prompt must not block or hang in non-TTY contexts — TTY detection is the correct guard.
- No architectural rework is needed; the changes fit cleanly into the existing design.

### Product Owner

These changes address real friction points reported by users of the upgrade workflow. The auto-restart eliminates a manual step that had no obvious purpose from the user's perspective. The rename from "backups" to "archives" improves terminology consistency. The requests-archival choice gives developers control over a significant decision (history retention vs. clean slate) that was previously made for them. The scope is appropriately minimal — no feature drift is evident.

- All four changes have clear, testable acceptance criteria.
- The interactive prompt for requests adds the highest business value: developers upgrading across major workflow changes may want a clean slate.
- The "migrate" default preserves backward compatibility for existing users.
- The rename does not affect the end-user's experience directly; it is an internal consistency improvement.

### User (Developer)

The auto-restart improvement is immediately tangible: after upgrading, the tool is ready to use without a second manual invocation. The requests-archival prompt is a welcome addition — but the phrasing of the prompt must be unambiguous (the options "Y=migrate" and "N=archive only" should be clearly explained in the prompt text). The rename from "backups" to "archives" has no visible impact unless the user inspects the `.aib_memory/` folder directly.

- The auto-restart reduces cognitive load; users no longer need to remember to re-run the launcher.
- The interactive prompt text must clearly explain the consequences of each choice (especially "N = old requests stay in the archive, new .aib_memory/ starts empty").
- If the user accidentally selects "N", their request history is not lost (it is in the archive), but recovering it requires a manual copy — this should be stated in the prompt.
- The `references.md` change is invisible to the user unless they have manually customized it (see Constraints).

### Security Officer

No new attack surface is introduced. The changes are confined to local filesystem operations. The `sys.stdin.isatty()` check does not introduce any injection risk. The interactive prompt reads from stdin using `input()`, which is the standard Python mechanism and does not execute arbitrary input. No credentials, tokens, or network operations are involved.

- No OWASP Top 10 concerns identified for these changes.
- The archive folder's content (pre-upgrade `.aib_memory/`) may contain sensitive workspace context; it is stored locally in the workspace and subject to the same access controls as `.aib_memory/` itself.
- No change to authentication, authorization, or data transmission.

### Data Governance Officer

`references.md` not being restored from the archive is a governance-relevant change: if a developer had added custom entries to `references.md` (e.g., pointing to internal policy documents), those entries would be lost silently during upgrade. This is accepted per the request scope but should be communicated in the upgrade summary output so developers are aware. The archive folder retains the pre-upgrade `references.md` for inspection.

- The pre-upgrade state of all files (including `references.md`) is always preserved in the timestamped archive subfolder — no data is permanently deleted.
- `requests/` retention depends on user choice at the interactive prompt; the default (migrate) preserves all request history.
- No external data flows are affected; all data is workspace-local.
- The archive folder should be excluded from `.gitignore` review — if users have `.gitignore` patterns excluding `.aib_memory/backups/`, those patterns will need updating to `.aib_memory/archives/`.

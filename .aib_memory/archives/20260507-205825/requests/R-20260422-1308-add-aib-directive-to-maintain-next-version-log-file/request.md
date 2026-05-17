## Goal

Add a persistent AIB behavioral directive to `.aib_memory/instructions.md` that instructs the AI agent to maintain a `logs/next_version_changes.md` file during implementation. Update `scripts/release_bookkeeping.py` so generated version logs prefer curated entries from `logs/next_version_changes.md` and fall back to git commit subjects when curated content is unavailable.

## Background

The GitHub Actions workflow (`aib-semver-patch-bump-and-log.yml`) triggers `scripts/release_bookkeeping.py` on every PR targeting `main`. The script currently generates a per-version log file (`logs/version_vX.Y.Z_log.md`) using only raw git commit subjects collected from the PR branch. These commit subjects are often terse and inconsistent, and may not reflect user-visible changes.

The `instructions.md` file (`.aib_memory/instructions.md`) is the persistent workspace-level directive channel read by all AIB prompts before execution. It is currently empty.

The current input explicitly prohibits adding `logs/next_version_changes.md` to `.aib_memory/references.md`. This request iteration therefore focuses on directive + script/workflow behavior and keeps references unchanged.

## Scope

- Add an AIB behavioral directive to `.aib_memory/instructions.md` instructing the AI agent to append curated change descriptions to `logs/next_version_changes.md` during each implementation run.

- Modify `scripts/release_bookkeeping.py` to detect and read `logs/next_version_changes.md` when present and non-empty, prefer those entries in generated version logs, and fall back to git commit subjects otherwise.

- Apply the resolved lifecycle policy: after CI incorporates curated entries, clear `logs/next_version_changes.md` to empty and commit the reset.

- Keep `.aib_memory/references.md` unchanged for this request.

- Add or update automated tests for source preference, fallback, lifecycle reset, and idempotency.

## Out of scope

- Adding `logs/next_version_changes.md` to `.aib_memory/references.md`.
- Modifying `.aib_brain/` assets (prompts, conventions, templates, tools).
- Introducing third-party changelog tooling or non-standard-library dependencies.
- Changing SemVer bump logic or `.aib_brain` archive creation behavior.

## Constraints

- `scripts/release_bookkeeping.py` must remain Python 3.10+ standard-library-only.
- The modified script must remain idempotent on reruns.
- `.aib_brain/` must not be modified.
- `logs/next_version_changes.md` must remain VCS-tracked so CI can read it.
- If `logs/next_version_changes.md` is absent or empty, fallback to commit subjects must happen without error.
- `.aib_memory/references.md` must remain unchanged in this request iteration.

## Success criteria

- SC-01: `.aib_memory/instructions.md` contains a clear directive for append-style curated change entries in `logs/next_version_changes.md`.
- SC-02: `scripts/release_bookkeeping.py` prefers non-empty curated entries from `logs/next_version_changes.md` as the `Changes:` source.
- SC-03: If curated entries are absent/empty, `scripts/release_bookkeeping.py` falls back to commit subjects without error.
- SC-04: After CI incorporates curated entries, `logs/next_version_changes.md` is reset to empty and committed.
- SC-05: `.aib_memory/references.md` remains unchanged (no `next_version_changes.md` row is added).
- SC-06: Existing automated tests pass after implementation updates.

## Assumptions

- A1: `logs/next_version_changes.md` exists and is tracked in branches where CI bookkeeping runs.
  - Risk if false: curated source is unavailable and logs rely only on fallback subjects.

- A2: The implementation directive in `.aib_memory/instructions.md` is explicit enough to produce consistent append behavior.
  - Risk if false: entries may be overwritten or malformed.

- A3: GitHub Actions can continue committing changes under `logs/` in PR branches.
  - Risk if false: lifecycle reset cannot be persisted.

- A4: Existing commit-subject collection remains intact in the workflow for fallback support.
  - Risk if false: fallback behavior can degrade to sentinel-only output.

- A5: The input prohibition against references updates is authoritative for this request iteration.
  - Risk if false: reruns may reintroduce conflicting requirements.

## Plan

### Task 1: Add persistent implementation directive
**Intent:** Add deterministic directive text in `.aib_memory/instructions.md` for maintaining `logs/next_version_changes.md`.
**Inputs:** `.aib_memory/instructions.md`; this request.
**Outputs:** Updated `.aib_memory/instructions.md`.
**External Interfaces:** None.
**Environment & Configuration:** Workspace root.
**Procedure:**
1. Open `.aib_memory/instructions.md`.
2. Add directive text requiring append-only bullet entries.
3. Specify entry format and file-creation behavior.
4. Note CI reset expectation.
**Done Criteria:** Directive is present, actionable, and unambiguous.
**Dependencies:** None.
**Risk Notes:** Ambiguous directive wording may reduce implementation consistency.

### Task 2: Extend release bookkeeping source selection
**Intent:** Prefer curated entries while preserving fallback and idempotency.
**Inputs:** `scripts/release_bookkeeping.py`; existing behavior.
**Outputs:** Updated `scripts/release_bookkeeping.py`.
**External Interfaces:** Filesystem reads/writes in repository.
**Environment & Configuration:** Python 3.10+ standard library.
**Procedure:**
1. Add helper to read and normalize curated entries.
2. Add optional CLI argument for curated-file path.
3. Select `Changes:` source (curated first, fallback to commit subjects).
4. Apply lifecycle reset behavior to clear curated file after incorporation.
5. Keep idempotency behavior stable.
**Done Criteria:** Script behavior satisfies SC-02 to SC-04.
**Dependencies:** Task 1.
**Risk Notes:** Reset timing must not conflict with idempotent no-op path.

### Task 3: Update workflow invocation
**Intent:** Pass curated-file path to bookkeeping script in CI.
**Inputs:** `.github/workflows/aib-semver-patch-bump-and-log.yml`.
**Outputs:** Updated workflow args.
**External Interfaces:** GitHub Actions runner.
**Environment & Configuration:** Bash workflow step.
**Procedure:**
1. Add `--next-version-changes-file logs/next_version_changes.md` to args.
2. Preserve existing issue and commit-subject handling.
3. Validate YAML syntax and quoting.
**Done Criteria:** CI invokes bookkeeping with curated-file argument and remains backward-safe.
**Dependencies:** Task 2.
**Risk Notes:** Arg quoting issues can break workflow execution.

### Task 4: Add automated verification
**Intent:** Validate source preference, fallback, lifecycle reset, and idempotency.
**Inputs:** `tests/`; updated bookkeeping script.
**Outputs:** New/updated tests.
**External Interfaces:** `pytest`.
**Environment & Configuration:** Local test environment.
**Procedure:**
1. Add test for non-empty curated file preference.
2. Add tests for missing and empty curated file fallback.
3. Add test for lifecycle reset after incorporation.
4. Run full `pytest tests/` suite.
**Done Criteria:** Automated tests cover SC-02 to SC-06 and pass.
**Dependencies:** Tasks 2 and 3.
**Risk Notes:** Tests must isolate filesystem state.

### Task 5: Update context and editable product docs
**Intent:** Ensure product documentation reflects implemented behavior and constraints.
**Inputs:** `.aib_memory/context.md`; `.aib_memory/references.md`; implementation outputs.
**Outputs:** Updated `.aib_memory/context.md` if drift is detected.
**External Interfaces:** None.
**Environment & Configuration:** Workspace root.
**Procedure:**
1. Execute `Execute .aib_brain/prompts/aib-context.md` after implementation.
2. Verify context reflects curated-source and fallback behavior.
3. Verify `.aib_memory/references.md` remained unchanged.
**Done Criteria:** Context aligns with implementation and SC-05 remains true.
**Dependencies:** Tasks 1-4.
**Risk Notes:** Skipping this step can leave product docs inconsistent.

## Documentation

- `.aib_memory/instructions.md` (ref_id: N/A) — Add persistent directive for curated entry format and append behavior.
- `.aib_memory/context.md` (ref_id: REF-0001) — Regenerate after implementation to reflect updated release-bookkeeping behavior.

## Questions & Decisions

All decision points are currently resolved for this iteration.

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_memory/instructions.md` | Modified | Add persistent directive for curated change entry maintenance. |
| `scripts/release_bookkeeping.py` | Modified | Prefer curated entries, preserve fallback, enforce lifecycle reset. |
| `.github/workflows/aib-semver-patch-bump-and-log.yml` | Modified | Pass curated-file path to bookkeeping script. |
| `tests/` bookkeeping tests | Modified | Validate preference, fallback, lifecycle reset, and idempotency. |
| `.aib_memory/context.md` | Modified | Keep behavior documentation synchronized after implementation. |
| `.aib_memory/references.md` | Read-only dependency | Verified unchanged per explicit input constraint. |

## Internal Review of Request and Product Docs

- OK: Active request resolution is consistent (single Active request in register).
- OK: Input toggles do not route to no-change or skip-analysis branches.
- Cross-ref issue resolved: prior references-update requirement conflicted with current input; request now aligned with input prohibition.
- OK: Answered lifecycle/source decisions were applied and removed from open question flow.
- Missing info: exact final directive text in `.aib_memory/instructions.md` remains implementation work.
- OK: No `.aib_brain/` modification is required by this request.

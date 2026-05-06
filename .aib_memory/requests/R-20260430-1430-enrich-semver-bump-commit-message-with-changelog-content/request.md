## Goal

Enhance the commit message produced by the GitHub Actions release bookkeeping workflow (`.github/workflows/aib-semver-patch-bump-and-log.yml`) so that it includes the curated changelog content from `logs/next_version_changes.md` instead of the current short, uninformative `"chore: bump ..."` message. The enriched commit message must be useful as a notification body for recipients who receive commit-triggered emails from GitHub.

## Background

During every pull request event targeting `main`, the `aib-semver-patch-bump-and-log.yml` workflow executes `release_bookkeeping.py`, which:
1. Reads curated change bullets from `logs/next_version_changes.md`.
2. Incorporates them into the version log (`logs/version_vX.Y.Z_log.md`).
3. Resets `logs/next_version_changes.md` to empty.
4. Then the workflow commits the resulting changes (new version log, updated SemVer marker, zip archive) back to the PR branch using the commit message: `"chore: bump to <version> (PR #<number>)"`.

The GitHub commit notification email includes the commit message as its body. Recipients currently see only the terse `"chore: bump ..."` text, which does not communicate what changed. The curated bullets in `logs/next_version_changes.md` (maintained by the AI agent via `instructions.md`) contain precisely the user-visible changes relevant to the release — this content should appear in the commit message so that notification emails are self-explanatory.

## Scope

- Modify the commit message construction in the "Commit and push" step of `.github/workflows/aib-semver-patch-bump-and-log.yml` to include the curated changelog content as the message body.

- Ensure the curated content is captured before `release_bookkeeping.py` resets `logs/next_version_changes.md` to empty, since by the time the commit step runs the file has already been cleared.

- The enriched commit message must preserve the existing subject line (`chore: bump to <version> (PR #<number>)`) and add the changelog bullets as the commit body, separated from the subject by a blank line per Git convention.

- If `logs/next_version_changes.md` is empty or absent at workflow runtime, the commit message falls back to the current subject-only message with no body.

## Out of scope

- Changing the logic in `release_bookkeeping.py` that selects between curated entries and commit-subjects fallback for the version log.
- Changing the content format or schema of `logs/next_version_changes.md` or `logs/version_vX.Y.Z_log.md`.
- Adding new email notification integrations, webhooks, or external communication channels.
- Changing workflow triggers, concurrency settings, checkout steps, or any steps other than the commit message construction.
- Modifying how curated bullets are authored or appended during `aib-implement.md` runs.

## Constraints

- The GitHub Actions workflow must remain compatible with Ubuntu runners and standard Bash.
- All new shell code must comply with `set -euo pipefail`; no unbound variable references or pipeline failures may be introduced.
- The existing `if: steps.bookkeeping.outputs.changed == 'true'` gate on the commit step must be preserved unchanged.
- No new GitHub Actions third-party actions or external dependencies may be introduced; only standard bash, `git`, and existing workflow/script infrastructure may be used.
- The implementation must be idempotent: re-running the workflow on the same PR (e.g., after a synchronize event) produces a consistent commit message structure.
- The commit message subject line format (`chore: bump to <version> (PR #<number>)`) must remain unchanged so that tooling that parses commit subjects is not affected.

## Success criteria

- SC-1: After the workflow runs on a PR where `logs/next_version_changes.md` had non-empty curated content, the CI commit message subject matches `chore: bump to <version> (PR #<number>)`.
- SC-2: After the workflow runs on a PR where `logs/next_version_changes.md` had non-empty curated content, the CI commit message body contains those curated bullet lines.
- SC-3: After the workflow runs on a PR where `logs/next_version_changes.md` was empty, the CI commit message contains only the subject line (no body).
- SC-4: The existing `steps.bookkeeping.outputs.changed == 'true'` gate is preserved; no commit is made when there are no changed files.
- SC-5: The workflow runs to completion without errors under `set -euo pipefail`; no unbound variable or pipeline failures are introduced by the commit message changes.

## Assumptions

- A1: The GitHub Actions Ubuntu runner's bash handles heredoc output to `GITHUB_OUTPUT` correctly for content containing Markdown bullet characters, newlines, and typical ASCII text (hyphens, parentheses, version numbers).
  - Risk if false: Multi-line output truncation or escaping failure causing workflow error on the bookkeeping step.
- A2: If the chosen approach extends `release_bookkeeping.py` with a `changes_body` output key, the existing output parsing logic for `changed` and `new_version` in the workflow is unaffected by adding a new key.
  - Risk if false: Only the new output would be missing; existing behaviour degrades gracefully.
- A3: GitHub's commit notification email renders the full commit message body (not just the subject line) for recipients.
  - Risk if false: The enrichment would be functionally correct but invisible in the email notification, defeating the purpose.
- A4: The curated bullet content written by the AI agent via `instructions.md` consists of plain ASCII text lines without Git-special characters that would break commit message parsing.
  - Risk if false: Edge-case bullets with characters like backticks or leading `From ` could be misinterpreted by some email clients; very low probability given controlled authorship.

## Plan

### Task 1: Capture curated changelog content for commit message
**Intent:** Make the curated `next_version_changes.md` content available to the commit step after the bookkeeping script has already reset the file.
**Inputs:** `.github/workflows/aib-semver-patch-bump-and-log.yml`; `scripts/release_bookkeeping.py` (if Option B chosen from Q001); `logs/next_version_changes.md` (runtime source).
**Outputs:** Modified `release_bookkeeping.py` emitting `changes_body` as a GitHub Actions output (Option B), OR a new "Capture curated changes" step in the workflow reading the file before the bookkeeping step (Option A).
**External Interfaces:** GitHub Actions `GITHUB_OUTPUT` mechanism.
**Environment & Configuration:** Ubuntu runner; bash; no secrets.
**Procedure:**
1. If Option B (recommended): Add a `changes_body` output write in `release_bookkeeping.py` in `main()`, before `_reset_curated_file()` is called. Use the `GITHUB_OUTPUT` heredoc pattern with a non-colliding delimiter (e.g., `AIB_CHANGES_BODY_EOF`).
2. If Option A: Add a bash step in the workflow before "Run release bookkeeping" that reads `logs/next_version_changes.md` (if non-empty) and writes its content to `GITHUB_OUTPUT` as `changes_body`.
3. Verify the output value is accessible in a subsequent step.
**Done Criteria:** A subsequent workflow step can reference `${{ steps.bookkeeping.outputs.changes_body }}` (Option B) or `${{ steps.capture_changes.outputs.changes_body }}` (Option A) and receive the pre-reset bullet content.
**Dependencies:** Q001 resolution.
**Risk Notes:** Multi-line heredoc delimiter collision risk — use a unique, unlikely-to-appear delimiter string.

### Task 2: Modify the "Commit and push" step to use the enriched commit message
**Intent:** Replace the hardcoded single-line `git commit -m "..."` with a message constructed from subject + changelog body, with graceful fallback when the body is empty.
**Inputs:** `.github/workflows/aib-semver-patch-bump-and-log.yml`; `${{ steps.bookkeeping.outputs.changes_body }}` (or analogous output from Task 1).
**Outputs:** Modified "Commit and push" step with multi-line commit message support.
**External Interfaces:** `git commit --file` or `git commit -m ... -m ...`; GitHub Actions expression context.
**Environment & Configuration:** Ubuntu runner; bash; `set -euo pipefail`.
**Procedure:**
1. In the commit step's bash block, assign `changes_body` from the step output to a local variable, defaulting to empty string.
2. If `changes_body` is non-empty, write the full commit message (subject line + blank line + body) to a temporary file and invoke `git commit --file "$msg_file"`.
3. If `changes_body` is empty, invoke the original `git commit -m "chore: bump to ... (PR #...)"` unchanged.
4. Clean up the temporary file after the commit.
**Done Criteria:** `git log --format=%B -n 1` on the committed SHA shows the subject line and, when applicable, the body with curated bullets.
**Dependencies:** Task 1.
**Risk Notes:** Must initialize the variable with `:-""` default to avoid unbound variable error under `set -euo pipefail`.

### Task 3: Run automated test suite
**Intent:** Verify that existing tests still pass and that the modified files satisfy static quality checks.
**Inputs:** All modified files; test suite under `tests/`.
**Outputs:** Test run results.
**External Interfaces:** Python test runner (pytest); `.venv`.
**Environment & Configuration:** Local Python 3.10+ with `.venv` active.
**Procedure:**
1. Activate `.venv`.
2. Run `pytest tests/` and confirm all tests pass.
3. Check that `scripts/release_bookkeeping.py` is syntactically valid (`python -m py_compile`).
**Done Criteria:** All tests exit with code 0; no new failures introduced.
**Dependencies:** Tasks 1–2.
**Risk Notes:** No test currently validates the commit message format; T1–T6 from analysis require a live PR run for full validation.

### Task 4: Update context.md and documentation
**Intent:** Reflect the new commit message enrichment behavior in the workspace context document and any other editable references.
**Inputs:** `.aib_memory/context.md`; `.aib_memory/references.md`.
**Outputs:** Updated `.aib_memory/context.md` (FR-011, ADR-0008, component description of the GitHub Actions Workflow).
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Open `.aib_memory/context.md` and update FR-011 to reference the enriched commit message behavior.
2. Update ADR-0008 Consequences to note that the curated content now also flows into the CI commit message body.
3. Update the GitHub Actions Workflow component description in the Component Map.
4. Append a bullet to `logs/next_version_changes.md` describing the change (per `instructions.md` directive).
**Done Criteria:** `context.md` accurately describes the enriched commit message behavior; `logs/next_version_changes.md` has a new bullet for this change.
**Dependencies:** Tasks 1–2.
**Risk Notes:** None.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — Update FR-011 and ADR-0008 to reflect the new enriched CI commit message behavior; update the GitHub Actions Workflow component description in the Component Map.

## Questions & Decisions

**Q001**: Where should the curated `next_version_changes.md` content be captured for use in the commit message, given that `release_bookkeeping.py` resets the file before the commit step runs?
- [ ] Option A: Add a new workflow step BEFORE "Run release bookkeeping" that reads `logs/next_version_changes.md` and writes the content to `GITHUB_OUTPUT`; no Python script changes needed.
- [x] Option B: Extend `release_bookkeeping.py` to emit a `changes_body` GitHub Actions output key (using heredoc format) alongside the existing `changed` and `new_version` outputs, before resetting the curated file. *(recommended)*
- [ ] Other: ___
> Answer: 

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.github/workflows/aib-semver-patch-bump-and-log.yml` | Modified | Commit step must construct a multi-line commit message using the curated changelog content captured from the bookkeeping step output. |
| `scripts/release_bookkeeping.py` | Modified | (Option B) Add `changes_body` GitHub Actions output emission before resetting the curated file; no logic change — data capture only. |
| `.aib_memory/context.md` | Modified | Update FR-011 and ADR-0008 to reflect the new enriched commit message behavior. |
| `logs/next_version_changes.md` | Read-only dependency | Runtime source of curated changelog content for the enriched commit message; already consumed by `release_bookkeeping.py`. |

## Internal Review of Request and Product Docs

- OK: `context.md` FR-011 describes CI automated patch bump behavior and curated change log lifecycle; the request is an additive improvement consistent with this requirement.
- OK: `context.md` ADR-0008 describes the curated change-log source for version logs; the request extends this data flow to also populate the commit message body — no contradiction.
- OK: `context.md` ADR-0004 (pre-merge CI write model) is unaffected; the commit step remains the same step, only its message changes.
- Missing info: `context.md` does not document the current commit message format in the workflow, nor does it document the intended enriched format after this change; the Component Map entry for the GitHub Actions Workflow should be updated.
- Cross-ref issue: `context.md` ADR-0008 Consequences state "lifecycle reset must be gated to skip the script's idempotent no-op early-exit branches" — this confirms that capturing `changes_body` must occur before `_reset_curated_file()` is called in `release_bookkeeping.py`, which is already accounted for in the plan.

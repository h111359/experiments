## Goal

Fix a set of bugs and behavioral gaps in AIB prompts and the CI release workflow:

1. The "No changes — provide answer only" toggle must produce exactly two file changes: (1) write `<request-folder>/answer-<timestamp>.md`, and (2) reset `input.md` to the seed template with the current active request ID and title in `## Active request`. It MUST NOT modify any other file (`request.md`, `analysis.md`, or any other file).
2. `input.md` must not be reset until ALL operations in the current analysis/implement run are complete.
3. After `input.md` is reset to the seed template, the `## Active request` line must reflect the current active request ID and title instead of the literal text "No active request".
4. The auto-request creation branch in `aib-analysis.md` must generate `request.md` with all 6 mandatory sections (Goal, Background, Scope, Out of scope, Constraints, Success criteria) populated and non-empty; auditing the prompt and convention for any gap.
5. `aib-implement.md` must auto-create a request without asking for user permission when no Active request exists; the prompt wording must be unambiguous on this point.
6. Concepts.md, context.md, and README.md must be reviewed and updated to reflect any behavioral changes made in items 1–5.
7. The CI GitHub Actions workflow must include `versions/` in its `git add` command so that the `aib_brain_vX.Y.Z.zip` archive produced by `release_bookkeeping.py` is committed and pushed.

## Background

AIB is an AI-driven specification-and-implementation framework operating in a local Git repository. Its workflows are governed by prompt files in `.aib_brain/prompts/` and convention files in `.aib_brain/conventions/`.

Several behavioral bugs have been observed in production use:

- The "No changes" toggle is intended to produce a read-only answer without side-effects, but it currently modifies `input.md` (a file outside the request folder), violating the "no changes" contract.
- `input.md` is being reset before the analysis or implementation run is fully complete, causing loss of user context if the run fails mid-way.
- After reset, `input.md` displays "No active request" even when a request was just created, confusing the developer about workspace state.
- Some auto-generated `request.md` files lack one or more of the 6 mandatory sections, causing downstream analysis failures.
- When `aib-implement.md` detects no Active request, the executing agent interprets the prompt ambiguously and asks the user for permission to create one, adding unnecessary friction.
- The CI workflow's `git add` command does not include the `versions/` directory, so the `.aib_brain/` zip archive is generated locally by `release_bookkeeping.py` but never committed or pushed to the PR branch.

## Scope

- Modify `aib-analysis.md` prompt to:

  - Enforce that the "No changes" toggle writes ONLY to `<request-folder>/answer-<timestamp>.md` and resets `input.md` with the current active request ID in `## Active request`. It MUST NOT modify `request.md`, `analysis.md`, or any other file.

  - Move the `input.md` reset step to the very last action of the run (after all files are written and confirmed).

  - After the reset, append the active request ID and title to the `## Active request` line in the newly-seeded `input.md`.

  - Audit the auto-request creation branch for completeness of all 6 mandatory sections and fix any gaps found against `request-convention.md`.

- Modify `aib-implement.md` prompt to make the auto-request-creation branch unconditionally proceed (no user confirmation step).

- Update `Concepts.md` to reflect corrected "No changes" behavior and `input.md` lifecycle.

- Update `context.md` (via `aib-context.md`) to reflect any changes.

- Update `README.md` to document the corrected "No changes" behavior and updated `input.md` lifecycle.

- Modify `.github/workflows/aib-semver-patch-bump-and-log.yml` to add `versions` to the `git add` command in the "Commit and push" step.

## Out of scope

- Changes to `release_bookkeeping.py` logic (zip creation logic is correct; only the workflow's `git add` is missing).
- Changes to `close-request.py`, `create-request.py`, `initialize.py`, or `menu.py`.
- Changes to any convention file other than updates required to close a gap found in the request.md generation audit.
- Multi-request or multi-workspace scenarios.

## Constraints

- All prompt modifications must remain model-agnostic and vendor-agnostic (NFR-001).
- `input.md` reset must remain idempotent; seed template content is fixed.
- `.aib_brain/` assets must NOT be modified by tool scripts; only prompt files and the workflow YAML are changed.
- Python tool scripts must not be changed unless explicitly required by items 1–5.
- No new Python dependencies may be introduced.
- The CI workflow must remain idempotent on reruns.

## Success criteria

- SC-1: When the "No changes" toggle is checked and an Active request exists, the agent writes exactly one file (`answer-<timestamp>.md` in the request folder) and no other files are modified.
- SC-2: `input.md` is reset only after all other outputs of the current analysis run are fully written.
- SC-3: After `input.md` is reset, `## Active request` contains the current active request ID and title (e.g., `R-20260417-1554 — AIB prompt and workflow improvements`), not the literal string "No active request".
- SC-4: The auto-generated `request.md` contains all 6 mandatory sections with non-empty content.
- SC-5: Running `aib-implement.md` with no Active request results in the agent creating a request and proceeding without asking for permission.
- SC-6: Concepts.md, context.md, and README.md accurately reflect the corrected behaviors.
- SC-7: After a PR targeting `main` is processed by CI, `versions/aib_brain_vX.Y.Z.zip` is committed and present on the PR branch.

## Assumptions

- A1: The `initialize.py` seed template for `input.md` uses the literal string `No active request` as the placeholder in `## Active request`. The prompt must write the active request ID dynamically at reset time (in the "No changes" branch, the Auto-Request Branch, and the standard flow reset); `initialize.py` is unchanged.
  - Risk if false: The ID substitution logic would need to target a different sentinel string, causing silent failure.

- A2: The "No changes" mode is only valid when an Active request exists. When no Active request is present and the toggle is set, the existing `ERROR` message behavior is preserved and no file modification is made.
  - Risk if false: Additional branching logic may be needed.

- A3: The `aib-context.md` prompt will be executed after implementation to update `context.md` (as required by `aib-implement.md`). Direct changes to `context.md` in this request are out of scope.
  - Risk if false: Context drift — implement would need to also update `context.md` manually.

- A4: Concepts.md is updated by this request directly. `edit_allowed=N` for REF-0002 (Concepts.md) is overridden by the explicit request scope authorization. The implement run must honor this override.
  - Risk if false: If the implement prompt fails-closed on `edit_allowed=N` without checking request scope, Concepts.md will not be updated.

- A5: The README in scope is `.aib_brain/README.md` (the operational README within the brain). The root `README.md` describes installation only and does not document toggle behaviors.
  - Risk if false: Both READMEs may need updating.

- A6: The standard analysis flow (Active request, no toggles) must reset `input.md` as its final step, unless it was triggered from `aib-implement.md`. No context signal currently distinguishes a direct invocation from an implement-triggered one; the analysis prompt must document this as a caller convention — when triggered from implement, the analysis run MUST NOT reset `input.md`.
  - Risk if false: Double-reset or lost context if implement and analysis both try to reset `input.md` in the same chain.

## Plan

### Task 1: Clarify "No changes" toggle — retain input.md reset, enumerate all prohibited writes; add standard-flow reset
**Intent:** Modify `aib-analysis.md` so that (a) the "No changes" branch explicitly permits only two file writes and prohibits all others, and (b) the standard analysis flow resets `input.md` as its final step.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` (step 4 "No changes" sub-branch; end of standard flow)
**Outputs:** Modified `.aib_brain/prompts/aib-analysis.md`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Open `aib-analysis.md` step 4 "No changes" sub-branch.
2. Replace the existing prohibition list with an explicit enumeration: the branch produces exactly two writes — (1) `answer-<timestamp>.md` in the request folder, (2) reset `input.md` to the seed template. MUST NOT modify `request.md`, `analysis.md`, or any other file.
3. Add instruction: after writing the reset, replace `No active request` in `## Active request` with the current active request ID and title (resolved from the preflight step).
4. Confirm the "Stop here" instruction remains at the end of the branch.
5. At the end of the standard analysis flow steps (after all Part 1 and Part 2 outputs are written), add a final step: "Reset `input.md` to the seed template and replace `No active request` in `## Active request` with the current active request ID and title. MUST NOT perform this reset if the current analysis run was triggered from `aib-implement.md`."
**Done Criteria:** The "No changes" sub-branch explicitly lists both permitted writes, prohibits all others by name, and includes the active-request-ID substitution. The standard flow has a final reset step conditioned on not being triggered from implement.
**Dependencies:** None
**Risk Notes:** The "unless triggered from implement" condition is a caller convention — the analysis prompt must document it clearly; implement must not reset input.md itself when it triggers analysis.

### Task 2: Move input.md reset to last step of Auto-Request Creation Branch
**Intent:** Reorder the Auto-Request Creation Branch so that `input.md` is reset only after all analysis artifacts are fully written.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` (Auto-Request Creation Branch, steps 7–8)
**Outputs:** Modified `.aib_brain/prompts/aib-analysis.md`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Locate step 7 ("Reset `input.md` to the seed template") and step 8 ("Proceed with the standard analysis flow") in the Auto-Request Creation Branch.
2. Move the reset instruction to after step 8 (i.e., make it the new final step, step 9).
3. Also add the step: "After reset, read `.aib_memory/requests_register.md`, find the Active request row, and replace `No active request` in the `## Active request` section with `<request_id> — <title>`."
**Done Criteria:** Step 8 (analysis generation) precedes the reset step in the prompt. The reset step includes the active-request-ID substitution instruction.
**Dependencies:** None
**Risk Notes:** None.

### Task 3: Strengthen request.md section generation in Auto-Request Creation Branch
**Intent:** Enumerate all 14 mandatory section headings explicitly in step 5 of the Auto-Request Creation Branch to prevent incomplete generation.
**Inputs:** `.aib_brain/prompts/aib-analysis.md` step 5 (Auto-Request Creation Branch)
**Outputs:** Modified `.aib_brain/prompts/aib-analysis.md`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Locate step 5 of the Auto-Request Creation Branch.
2. Replace the existing 6-section list with an explicit enumeration of all 14 mandatory headings in order: `## Goal`, `## Background`, `## Scope`, `## Out of scope`, `## Constraints`, `## Success criteria`, `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`, `## Questions & Decisions`, `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`, `## Multi-Perspective Stakeholder Review`.
3. Specify: sections 1–6 MUST be non-empty with content derived from `input.md`'s `## Input` section; sections 7–14 may be empty (they are populated by the analysis continuation in step 8).
4. Add a verification instruction: "Before writing `request.md`, confirm all 14 headings are present and sections 1–6 are non-empty."
**Done Criteria:** Step 5 of Auto-Request Branch explicitly enumerates all 14 headings; sections 1–6 require non-empty content; verification instruction is present.
**Dependencies:** None
**Risk Notes:** None.

### Task 4: Fix aib-implement.md auto-analysis branch — remove permission seeking
**Intent:** Make the Auto-Analysis Branch in `aib-implement.md` unconditionally proceed without user confirmation.
**Inputs:** `.aib_brain/prompts/aib-implement.md` (Input resolution section, zero-Active-row branch, line ~8)
**Outputs:** Modified `.aib_brain/prompts/aib-implement.md`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Locate the zero-Active-rows branch instruction in `aib-implement.md`.
2. Append: "Do NOT ask the user for permission or confirmation before creating the request or running analysis; proceed autonomously."
**Done Criteria:** The zero-Active-rows branch instruction explicitly prohibits asking for user confirmation.
**Dependencies:** None
**Risk Notes:** None.

### Task 5: Fix CI workflow — add versions/ to git add
**Intent:** Ensure the `aib_brain_vX.Y.Z.zip` produced by `release_bookkeeping.py` is staged and committed by the CI workflow.
**Inputs:** `.github/workflows/aib-semver-patch-bump-and-log.yml` ("Commit and push" step)
**Outputs:** Modified `.github/workflows/aib-semver-patch-bump-and-log.yml`
**External Interfaces:** GitHub Actions, git
**Environment & Configuration:** None
**Procedure:**
1. Locate the `git add .aib_brain logs` command in the "Commit and push" step.
2. Change it to `git add .aib_brain logs versions`.
**Done Criteria:** The `git add` command includes `versions`. On CI run, `versions/aib_brain_vX.Y.Z.zip` appears in `git status --porcelain` output and is committed.
**Dependencies:** None
**Risk Notes:** If the `versions/` directory is `.gitignore`d, adding it to `git add` will have no effect. Verify that `versions/` is tracked by VCS.

### Task 6: Update .aib_brain/README.md
**Intent:** Update the README to reflect corrected "No changes" behavior and input.md lifecycle.
**Inputs:** `.aib_brain/README.md`; behaviors from Tasks 1–4
**Outputs:** Modified `.aib_brain/README.md`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Update the "Typical Daily Flow" to reflect that the developer writes intent to `input.md` and runs `aib-analysis.md` (auto-request creation is automatic; no separate "Open a request" step with `create-request.py`).
2. Add a note about the "No changes" toggle: it produces only `answer-<timestamp>.md` and leaves all other files unchanged.
3. Update the `aib-analysis.md` description to mention the Auto-Request Creation Branch and the corrected reset timing.
**Done Criteria:** README accurately describes the corrected behavior for all 3 fixed scenarios.
**Dependencies:** Tasks 1, 2, 4
**Risk Notes:** None.

### Task 7: Update Concepts.md
**Intent:** Update the Invocation contract section and overall concepts to reflect corrected behaviors.
**Inputs:** `.aib_brain/Concepts.md`; corrected behaviors from Tasks 1–4; A4 assumption (edit_allowed=N for Concepts.md)
**Outputs:** Modified `.aib_brain/Concepts.md`
**External Interfaces:** None
**Environment & Configuration:** None
**Procedure:**
1. Note: Concepts.md has `edit_allowed=N` in `references.md`. However, the request explicitly requires updating Concepts.md. Treat this as an explicit override instruction.
2. Update the `input.md` lifecycle description to reflect: (a) reset happens after all artifacts are written; (b) after reset, active request ID is shown.
3. Update the `create-analysis` action description to reflect "No changes" writes only to request folder.
4. Update the `implement` action description to reflect it auto-creates a request without asking for permission.
**Done Criteria:** Concepts.md lifecycle descriptions are accurate for all corrected behaviors.
**Dependencies:** Tasks 1–4
**Risk Notes:** `edit_allowed=N` requires explicit user authorization; the request scope is the authorization.

### Task 8: Run tests and verify
**Intent:** Execute the existing test suite and confirm no regressions from the prompt and workflow changes.
**Inputs:** `tests/` folder; `.venv` environment
**Outputs:** Test run output in terminal
**External Interfaces:** pytest
**Environment & Configuration:** Python venv at `.venv/`
**Procedure:**
1. Run `pytest tests/ -v` in the activated venv.
2. Review results; all tests must pass.
**Done Criteria:** All tests pass with zero failures.
**Dependencies:** Tasks 1–7
**Risk Notes:** Tests may not cover prompt-content correctness; manual review of prompt file diffs is also required.

## Testing

- T1 — "No changes" toggle writes only answer file and resets input.md: With "No changes" toggle set and an Active request present, verify that after running `aib-analysis.md`, only `answer-<timestamp>.md` is created in the request folder and `input.md` is reset. Expected outcome: `request.md` and `analysis.md` are unchanged; `input.md` is reset to seed template with active request ID; one answer file exists.

- T2 — "No changes" toggle does not modify request.md or analysis.md: With "No changes" toggle set, verify `request.md` content is byte-for-byte identical before and after the run. Expected outcome: `request.md` and `analysis.md` unchanged; no extra files created outside the request folder and `input.md`.

- T3 — input.md reset occurs after analysis artifacts are written: Simulate an Auto-Request Creation Branch run. After the run, verify `analysis.md` and updated `request.md` sections exist in the request folder AND `input.md` has been reset. Expected outcome: both analysis artifacts and reset `input.md` are present; neither is missing.

- T4 — Active request ID in reset input.md: After any run that resets `input.md` (Auto-Request Branch or "No changes" branch), read the reset `input.md` and verify `## Active request` contains the real request ID and title. Expected outcome: `## Active request` contains the format `R-<ID> — <title>`; literal `No active request` is NOT present.

- T5 — request.md has all 14 mandatory sections: After auto-request creation, read the generated `request.md` and verify all 14 headings are present and sections 1–6 (`## Goal`, `## Background`, `## Scope`, `## Out of scope`, `## Constraints`, `## Success criteria`) are non-empty. Expected outcome: all 14 headings found; each of sections 1–6 has at least one non-empty line of content.

- T6 — aib-implement.md no-active-request branch does not ask for permission: (Manual test) Run `aib-implement.md` with no Active request and non-empty `input.md`. Verify the agent proceeds to create a request and run analysis without prompting the user for confirmation. Expected outcome: agent creates request, runs analysis, and continues to implementation without a confirmation question.

- T7 — CI zip committed after workflow run: Inspect CI run output on a test PR. Verify that `versions/aib_brain_vX.Y.Z.zip` appears in the commit made by the workflow. Expected outcome: `git log --name-only` shows the zip file in the CI commit.

- T8 — Test suite passes: Run `pytest tests/ -v`. Expected outcome: all tests pass with exit code 0.

- T9 — Re-run idempotency: Run `aib-analysis.md` a second time on the same Active request. Expected outcome: `analysis.md` and `request.md` optional sections are fully replaced; no duplicate sections; `input.md` remains in the reset state from the first run.

- T10 — Standard flow resets input.md: Run `aib-analysis.md` directly (not from implement) with an Active request and no toggles. After the run, verify `input.md` has been reset to the seed template with the active request ID and title in `## Active request`. Expected outcome: `input.md` is reset; `## Active request` contains `R-<ID> — <title>`; all other files written correctly.

## Documentation

- `.aib_brain/README.md` (ref_id: N/A) — Update Typical Daily Flow (remove manual "Open a request" step, describe input.md workflow), document the "No changes" toggle, and update use-case scenarios 1 and 2.
- `.aib_brain/Concepts.md` (ref_id: REF-0002) — Add "No changes" toggle documentation to invocation contract; update input.md lifecycle in the Holistic workflow section to reflect reset-last behavior and active-request-ID display; update implement description to reflect no-confirmation auto-analysis.
- `.aib_memory/context.md` (ref_id: REF-0001) — Regenerate via `aib-context.md` at end of implement run to reflect FR-003, FR-006, FR-007 corrections.

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/prompts/aib-analysis.md` | Modified | Fix "No changes" reset, move input.md reset to last step, add active request ID to seed, strengthen section enumeration |
| `.aib_brain/prompts/aib-implement.md` | Modified | Add explicit no-permission-seeking language to Auto-Analysis Branch |
| `.github/workflows/aib-semver-patch-bump-and-log.yml` | Modified | Add `versions` to `git add` in "Commit and push" step |
| `.aib_brain/README.md` | Modified | Reflect corrected behaviors in user-facing documentation |
| `.aib_brain/Concepts.md` | Modified | Update lifecycle and action descriptions |
| `.aib_memory/context.md` | Modified | Regenerated by `aib-context.md` at end of implement run |
| `scripts/release_bookkeeping.py` | Read-only dependency | Read for analysis; no changes needed |
| `.aib_memory/input.md` | Read-only dependency | Read during analysis; modified during implement reset step |
| `.aib_memory/requests_register.md` | Read-only dependency | Read for active request resolution |

## Internal Review of Request and Product Docs

- OK: `request.md` — All 6 mandatory user-written sections present with non-empty content. Scope is bullet-list form. Success criteria are measurable and linked to testability.
- Ambiguity: `request.md` — A4 assumption notes that Concepts.md has `edit_allowed=N` in `references.md`, but the request explicitly requires updating it. The intent is clear (explicit override), but the implement prompt must be aware of this to avoid a fail-closed block.
- Cross-ref issue: `context.md` FR-003 — "The `aib-analysis.md` prompt archives `input.md` content and resets the file." This is accurate for the Auto-Request Branch but incomplete: the standard flow also resets `input.md` (after the fix). Context.md must be regenerated post-implement to reflect the corrected full lifecycle.
- Cross-ref issue: `context.md` FR-007 — "No changes" toggle: "writes timestamped answer.md, skips analysis/impl". Does not mention `input.md` reset or the prohibition on other writes. After fix, must state that it resets `input.md` with active request ID and prohibits all other writes.
- Ambiguity: `Concepts.md` — Invocation contract for `create-analysis` does not describe the "No changes" toggle behavior. README does not mention the toggle at all. Both gaps must be filled.
- Missing info: `.aib_brain/README.md` — The "Typical Daily Flow" still describes a manual "Open a request" step using `create-request.py`, which contradicts the auto-request creation design (ADR-0005).
- OK: `.github/workflows/aib-semver-patch-bump-and-log.yml` — All other steps are correct; only the `git add` line is defective.
- Missing info: `aib-analysis.md` — The standard analysis flow (Active request, no toggles) has no `input.md` reset step. This is a gap against the expected lifecycle and the request's Goal item 2. Fix: Task 1 adds a final reset step to the standard flow.
- Contradiction: `aib-analysis.md` Auto-Request Creation Branch step 5 vs `request-convention.md` — Step 5 cites 6 mandatory sections; the convention requires 14. Fix: Task 3 updates step 5 to enumerate all 14.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect
The nine defects are all localized and non-structural: two prompt-text fixes, one prompt-ordering fix, one prompt-wording fix, one new reset-step addition (standard flow), one section-enumeration fix (14 vs 6), one YAML one-liner fix, and two documentation updates. There are no architectural changes required. Moving `input.md` reset to "last step" and adding it to the standard flow aligns with standard workflow safety patterns (commit state only after success). The CI `git add` omission is a classic staging oversight. Risk is low; impact is high for developer experience.

- All fixes are backward-compatible — no API or schema changes.
- Prompt-file changes are behavioral, not structural; existing convention files remain valid.
- The `edit_allowed=N` flag on Concepts.md is a process gate, not a technical constraint; explicit request scope is sufficient authorization.
- No new dependencies are introduced.
- CI idempotency is preserved: `zip_path.exists()` check in `_create_brain_zip` prevents duplicate zip creation on reruns.
- The "unless triggered from implement" condition for the standard-flow reset must be expressed with precision to avoid ambiguity across models.

### Product Owner
This request addresses real friction points that degrade developer trust in the tooling. The "No changes" bug and premature reset are the highest-priority items. Two newly identified gaps (missing standard-flow reset and 6 vs 14 section count) are equally important: the first means every standard analysis run leaves `input.md` in a stale state; the second means auto-created `request.md` files may be structurally incomplete. The CI zip omission means that every version published so far may be missing the zip in `versions/`, which is a gap against acceptance criterion 6 (FR-011).

- All success criteria are measurable and testable.
- The README update (Task 6) should also correct the outdated "Typical Daily Flow" — this is a low-effort high-value improvement already scoped.
- The documentation gap (Concepts.md has `edit_allowed=N`) is a minor process friction that should be addressed during implement.
- Post-fix, the end-to-end experience from writing to `input.md` to seeing a confirmed zip in `versions/` will match the documented intent.

### User
The "No changes" toggle is broken — it currently modifies `input.md` silently. This is the most disorienting bug because the user explicitly opted out of changes. The premature reset is also frustrating: if the analysis run fails mid-way, the user loses their input permanently. The "No active request" string in the reset `input.md` is a minor but confusing UI issue.

- After fix: "No changes" mode is truly read-only outside the request folder.
- After fix: failed analysis runs no longer destroy user input.
- After fix: the developer can immediately see which request is active by glancing at `input.md`.
- The implement permission prompt is a friction point that will be removed.

### Security Officer
All changes are local filesystem writes within a controlled repository. No new network endpoints, credentials, or data exfiltration paths are introduced. The CI workflow change (`git add versions`) is additive only — it stages additional files in an already-authorized commit operation. The `GITHUB_TOKEN` scope (contents: write) already covers this. No attack surface changes.

- Zip archives in `versions/` contain only `.aib_brain/` framework files (prompts, conventions, scripts); no secrets or PII are expected.
- No input validation changes; no authentication/authorization changes.
- No OWASP Top 10 exposure introduced.

### Data Governance Officer
The `inputs/input-archive-*.md` files are the audit trail for user input. The fix (moving reset to last step) strengthens the audit trail by ensuring the archive is written before the original is cleared. The "No changes" fix ensures no archive is written for read-only queries (correct — read-only answers should not produce audit artifacts in the request folder if there was no intent change).

- Data lineage for `input.md` → `request.md` → `analysis.md` → `implementation.md` is preserved and strengthened.
- No retention policy changes.
- All artifacts remain classified as Internal.
- Zip archives in `versions/` are now correctly committed; data lineage for releases is complete.


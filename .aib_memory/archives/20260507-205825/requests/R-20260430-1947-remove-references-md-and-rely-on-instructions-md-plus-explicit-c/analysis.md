# Analysis — R-20260430-1947

## Executive Summary

- Request ID: R-20260430-1947

- Title: Remove references.md and rely on instructions.md plus explicit context.md reads.

- Purpose: Eliminate the `.aib_memory/references.md` register, hard-wire each prompt to read `.aib_memory/context.md` directly, let developers list any extra context paths in `.aib_memory/instructions.md`, and surface a console warning during `initialize.py --upgrade` when an old `references.md` contains rows beyond the two default seeded references.

- The active `request.md` defines all 12 mandatory sections and now lists 8 implementation tasks covering prompts, conventions, tools (with the new legacy-references warning helper), tests (with three new upgrade-warning test cases), file deletion, validation, and `context.md` regeneration.

- Run delta vs the previous analysis: an `input.md` amendment extended Goal, Scope, Constraints, Success criteria, Assumptions, Plan (Task 4 + Task 5), and the Code & Asset Scan to cover an upgrade-time inspection that informs the user of any non-default rows that need to be migrated to `instructions.md`.

- Sections refreshed in `request.md` during this run: `## Goal`, `## Scope`, `## Constraints`, `## Success criteria`, `## Assumptions` (added A5, A6), `## Plan` (rewrote Task 4 and Task 5), `## Code and Asset Scan for Impacted Components` (refined `initialize.py` and `tests/test_initialize.py` rows).

- No `## Questions & Decisions` block is created in this run — every decision point introduced by the amendment falls below the configured threshold (3) on the 5-Level Severity Scale and is resolved autonomously and documented inline in `request.md`.

## Domain Knowledge Essentials

- **AIB workspace registers**: Two long-lived markdown registers historically governed AIB state — `requests_register.md` (lifecycle of work units) and `references.md` (catalog of files AIB may read or edit). Only the former remains business-critical after this iteration.

- **Active personas**:
  - Developer — writes intent into `input.md`, reads generated artifacts, edits `instructions.md` to give the agent persistent guidance, runs `initialize.py --upgrade` after pulling a newer `.aib_brain/`.
  - AI Automation Agent — executes prompts and tool scripts.
  - AIB Maintainer — owns `.aib_brain/` assets and conventions.

- **Business processes touched**:
  - Workspace initialization and **upgrade** (newly emits a legacy-references warning).
  - Active-request analysis and implementation.
  - Context synthesis (`aib-context.md`).
  - Release bookkeeping (unaffected).

- **Acceptance impact**: After removal, AIB still operates with one Active request at a time, still produces `request.md`/`analysis.md`/`implementation.md`, still updates `context.md` and the curated changelog. The `--upgrade` path is now slightly more informative: any custom rows a developer historically added to `references.md` are surfaced for manual migration into `instructions.md` instead of being silently dropped.

## Technical Knowledge & Terms

- **`.aib_memory/references.md`** — Legacy Markdown table seeded by `initialize.py` from `.aib_brain/templates/references-template.md` via `seed_references_from_product_doc()`. Being deleted in this iteration.

- **`.aib_memory/context.md`** — Auto-generated unified product knowledge synthesized by `aib-context.md`; the only file historically tagged `product-doc` in the live workspace.

- **`.aib_memory/instructions.md`** — Free-form Markdown file read by every AIB prompt as its first step; persistent workspace-level directives. Already present and idempotently seeded by `initialize.py`. Becomes the sole sanctioned channel for developer-supplied extra-context paths.

- **`.aib_brain/Concepts.md`** — Domain document describing AIB conceptual model and lifecycle rules. Referenced as input by `aib-analysis.md` (passive listing) and as a read step by `aib-implement.md`.

- **`seed_references_from_product_doc()`** — Helper in `.aib_brain/tools/common.py` synthesizing the references table from either a static template or `Product_Documentation.md`. Only the static-template branch is exercised in the live repo; entire helper is being removed.

- **`_run_upgrade(workspace, brain_dir, memory_root)`** — Internal `initialize.py` routine that archives the current `.aib_memory/`, clears non-archive content, re-seeds, and conditionally restores `context.md`, `instructions.md`, and `requests_register.md`/`requests/`. The new `_warn_about_legacy_references(memory_root)` helper is invoked between Step 2 (archive copy) and Step 3 (delete non-archive content), so the live legacy file is still readable when the helper runs.

- **`parse_markdown_table(text)`** — Existing helper in `common.py` returning a list of dict rows from a GitHub-flavoured Markdown table. Used by the new helper to extract `path` values.

- **Default `path` values that MUST NOT trigger the warning** — `.aib_memory/context.md` and `.aib_brain/Concepts.md`. Comparison is performed after normalising backslashes to forward slashes (the seed template stores `Concepts.md` as `.aib_brain\Concepts.md`).

- **Files Read (evidence log)**:
  - `.aib_memory/instructions.md` — directive on `logs/next_version_changes.md` curation; observed → carried forward into Plan Task 8.
  - `.aib_memory/input.md` — amendment scope source; implication → drives the new Goal/Scope/SC-9 additions.
  - `.aib_memory/references.md` — current schema and live rows (REF-0001, REF-0002 only); implication → live workspace would not trigger the new warning, but `initialize.py --upgrade` could trigger it on third-party clones.
  - `.aib_memory/context.md` — current product context; implication → identifies impacted module/data/storage descriptions to refresh.
  - `.aib_memory/requests_register.md` — confirmed exactly one Active request before run; standard analysis flow.
  - `.aib_memory/request.md` — current request body; implication → exact insertion points for amendment.
  - `.aib_brain/prompts/aib-analysis.md`, `aib-implement.md`, `aib-context.md` — current prompt bodies; unchanged scope of edits.
  - `.aib_brain/conventions/analysis-convention.md`, `request-convention.md` — section ordering and Q-block rules.
  - `.aib_brain/tools/initialize.py` — confirmed `_run_upgrade` step ordering and identified the safe insertion point for `_warn_about_legacy_references`.
  - `.aib_brain/tools/common.py` — verified `parse_markdown_table` is the natural parser to reuse.

## Research Results

- Pattern scan against the existing AIB codebase shows that `references.md` reads are universally followed by either a no-op (e.g., `aib-analysis.md` builds an empty product-doc set in practice) or a single-file branch that always resolves to `.aib_memory/context.md`. Replacing the register with an explicit `context.md` read removes one indirection layer with no loss of behavior.

- Pattern scan for `Concepts.md` consumers shows zero call sites in tool scripts; only two textual mentions in prompt files. Removing the prompt mentions does not break any executable path.

- Pattern scan for `seed_references_from_product_doc()` callers shows exactly one caller (`initialize.py`); `parse_product_documentation_requirements()` and `resolve_product_documentation_path()` are only used by that helper. Confirms safe removal of the entire seeding code path.

- Pattern scan against `_run_upgrade` confirms a single archive-then-clear sequence; injecting an informational helper between Step 2 (archive copy) and Step 3 (delete non-archive content) preserves access to the live legacy `references.md` without coupling to the archive layout.

## External Benchmarking

- **Specification-driven and prompt-engineering frameworks (industry pattern)**: Modern lightweight prompt frameworks (e.g., Cursor `.cursorrules`, Continue.dev YAML, AGENTS.md / `copilot-instructions.md` conventions) favor a single free-form persistent-directives file for "what the agent should always know" over a structured register of file paths. Takeaway: collapsing `references.md` into `instructions.md` aligns AIB with the dominant industry pattern and reduces ceremony. Adoption: applied directly. Reinforced by the upgrade-time warning that nudges users toward `instructions.md`.

- **Twelve-Factor / "explicit dependencies" principle (general software architecture)**: Explicit, in-source declaration of inputs is preferred over indirection through configuration tables, particularly when the table is effectively static. Takeaway: hard-coding the `context.md` read inside each prompt makes the dependency visible at the call site and removes a register that most users never modify. Adoption: applied directly.

- **Schema-migration warning patterns (e.g., Django `RemovedInNextVersionWarning`, Rails `DEPRECATION WARNING`)**: When deleting a configuration file, mature frameworks emit a one-shot informational warning during the upgrade tool that lists the user-customised entries that will not be migrated, then continue without aborting. Takeaway: aligns exactly with the new `_warn_about_legacy_references` design — print, do not raise. Adoption: applied directly.

## Minimal Spikes and Experiments

- **Spike: Verify `references.md` consumers are static**
  - Hypothesis: `references.md` is consumed only by the three AIB prompts, `initialize.py`, and a handful of tests.
  - Approach: Workspace-wide grep across `.aib_brain/`, `.aib_brain/tools/`, `.aib_brain/conventions/`, `tests/` for `references.md`.
  - Outcome: 16 matches confirmed in the expected files only — three prompts, two conventions, `Concepts.md`, `initialize.py`, `common.py`, two test modules.
  - Conclusion: Removal scope is bounded; no hidden consumers.

- **Spike: Verify the static template branch is the live path**
  - Hypothesis: `seed_references_from_product_doc()` always uses the static template because `Product_Documentation.md` is absent.
  - Approach: Filesystem check for `.aib_brain/Product_Documentation.md` and code reading of the helper.
  - Outcome: File absent; helper falls through to template-based seeding.
  - Conclusion: Removing both the template and the helper is safe; the `Product_Documentation.md` parser path is dead code.

- **Spike: Identify safe insertion point in `_run_upgrade` for the legacy-references warning**
  - Hypothesis: The warning helper can read the live legacy `references.md` from `<memory_root>/references.md` if invoked between archive copy (Step 2) and non-archive deletion (Step 3).
  - Approach: Read `.aib_brain/tools/initialize.py` `_run_upgrade` function and trace each step.
  - Outcome: Step 2 finishes the archive copy via `shutil.copy2`/`copytree`; Step 3 then iterates and deletes. Inserting the helper between them keeps the live file readable and avoids coupling to the timestamped archive folder.
  - Conclusion: Insertion point is between Step 2 and Step 3 in `_run_upgrade`. The helper accepts only `memory_root` and reads `<memory_root>/references.md`.

## AI Copilot Suggestions

- **Subtractive change is still the right shape.** The amendment adds one tightly-scoped, informational step to a deletion-only iteration. Keep the helper purely informational — never raise, never alter the upgrade outcome.

- **Default-path comparison must be normalised.** The seed template historically stored `Concepts.md` as `.aib_brain\Concepts.md` (backslash). The default-set membership check MUST normalise backslashes to forward slashes before comparing, otherwise the live workspace would falsely emit the warning on every upgrade. Worth a one-line dedicated unit test.

- **Avoid swallowing real bugs.** Wrap only the parse step in `try/except`, not the whole helper. If `parse_markdown_table` raises, print the explicit `WARNING: legacy references.md is not parseable; skipping migration check.` line and return. Do not silence unrelated exceptions (filesystem permission, encoding) — let them propagate so they get surfaced.

- **Test coverage proportional to the change.** Three new test cases (extra row → warning, default-only → silent, malformed → fallback warning) exactly mirror the three behavioural paths. No additional tests are needed.

- **Scope verdict.** The amendment is the correct size: it adds exactly one helper, one Plan task expansion, three test cases, and one Success Criterion. Resist the temptation to also auto-migrate the extra rows into `instructions.md` programmatically — that would be additive scope creep and is better left to the developer.

- **Document the warning shape in user-facing docs.** Briefly mention the warning in the curated `logs/next_version_changes.md` bullet so that users encountering it on first upgrade understand it is expected behaviour, not an error.

## Testing

- T1 — Initialize does not create references.md: Run `python .aib_brain/tools/initialize.py --workspace <tmp>` against an empty workspace; confirm `<tmp>/.aib_memory/references.md` is absent. Expected outcome: Pass — file absent, exit code 0. (Covers SC-1, SC-7.)

- T2 — Brain assets removed: Assert `.aib_brain/templates/references-template.md` and `.aib_brain/conventions/references-convention.md` do not exist. Expected outcome: Pass — both `Path.exists()` return False. (Covers SC-2.)

- T3 — Live workspace file removed: Assert `.aib_memory/references.md` does not exist. Expected outcome: Pass — `Path.exists()` returns False. (Covers SC-1.)

- T4 — No `references.md` mentions in active brain code: Workspace-wide grep for `references.md` excluding `logs/`, `.aib_memory/archives/`, closed-request folders, and the active request artifacts; assert zero matches inside `.aib_brain/prompts/`, `.aib_brain/conventions/`, `.aib_brain/templates/`, `.aib_brain/tools/` (excluding deleted tests), and `.aib_brain/Concepts.md`. Expected outcome: Pass — zero matches. (Covers SC-3.)

- T5 — Prompts contain explicit `context.md` read: Assert each of `.aib_brain/prompts/aib-analysis.md` and `.aib_brain/prompts/aib-implement.md` contains the literal string `.aib_memory/context.md` in a "Read" instruction step. Expected outcome: Pass — string present. (Covers SC-4.)

- T6 — `Concepts.md` mentions justified or removed: Grep for `Concepts.md` in `.aib_brain/prompts/`; assert zero matches OR each match is on a line beginning with normative usage of the file's content. Expected outcome: Pass — zero matches under the autonomous decision recorded in the prior run. (Covers SC-5.)

- T7 — Existing test suite passes: Run `python -m pytest tests/` and `python -m pytest .aib_brain/tools/test_common.py`. Expected outcome: Pass — exit code 0; no test failures. (Covers SC-6.)

- T8 — Re-run idempotency: Re-run `initialize.py` on the same workspace twice; second run prints "already exists — skipping" lines for `requests_register.md`, `context.md`, `input.md`, `instructions.md`; does not create `references.md`. Expected outcome: Pass — no diff between first and second runs. (Covers SC-1, SC-7.)

- T9 — Context regeneration removes `references.md`: Run `aib-context.md`; assert generated `.aib_memory/context.md` contains zero occurrences of the literal string `references.md`. Expected outcome: Pass — zero matches. (Covers SC-8.)

- T10 — Upgrade emits warning when legacy `references.md` has extra rows: Seed a synthetic workspace with `.aib_memory/references.md` containing rows for `REF-0001` (`.aib_memory/context.md`), `REF-0002` (`.aib_brain\Concepts.md`), and `REF-0003` (`docs/custom-extra.md`); invoke `initialize.py --upgrade` (or `_run_upgrade` directly) and capture stdout; assert stdout contains the literal string `WARNING: legacy references.md contains entries beyond the two defaults` and the line `  - docs/custom-extra.md`; assert exit code 0. Expected outcome: Pass. (Covers SC-9, default-with-extra path.)

- T11 — Upgrade silent when only default `references.md` rows present: Seed a synthetic workspace with `.aib_memory/references.md` containing only the two default rows; invoke `initialize.py --upgrade` and capture stdout; assert stdout does NOT contain the substring `WARNING: legacy references.md`; assert exit code 0. Expected outcome: Pass. (Covers SC-9, defaults-only path.)

- T12 — Upgrade tolerates malformed legacy `references.md`: Seed a synthetic workspace with `.aib_memory/references.md` set to non-table garbage (e.g., a single line of free text); invoke `initialize.py --upgrade`; assert stdout contains `WARNING: legacy references.md is not parseable; skipping migration check.`; assert exit code 0 and that the rest of the upgrade procedure completes (semver marker present, `instructions.md` restored). Expected outcome: Pass. (Covers SC-9, malformed-fallback path.)

All test cases are expressible as automated assertions. No `UAT_scenarios.md` is required for this iteration.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

The amendment preserves the architecturally sound subtractive shape of the iteration and adds exactly one informational helper at the right insertion point in `_run_upgrade`. It does not introduce a new abstraction, does not couple to the archive folder layout, and does not change exit codes. The fail-soft handling of malformed legacy tables avoids the worst failure mode (a one-shot upgrade tool that aborts on a junk file in user space).

- Bounded blast radius — touches one helper inside one function in one tool script.

- Insertion point chosen so the live legacy file is still readable.

- Fail-soft on parse error — never aborts the upgrade.

- No new persistent state introduced; warning is one-shot stdout only.

### Product Owner

The new behaviour delivers measurable user value: any developer who customised `references.md` in a previous AIB version is now told exactly which rows to migrate, instead of silently losing them. Acceptance criterion SC-9 is one-to-one testable across three behavioural paths, each backed by a dedicated test case (T10, T11, T12).

- Each Success Criterion (including new SC-9) is testable and tied to a Plan task.

- Communication: the warning text itself doubles as user-facing documentation.

- Risk of churn: minimal — only users on AIB versions that pre-date this iteration will encounter the warning, and only on their first `--upgrade`.

- Scope discipline preserved — the amendment does not auto-migrate, only informs.

### User

The first-time upgrade experience improves. A developer who customised `references.md` previously would have lost those rows silently; now they see a clear, actionable message pointing at `instructions.md`. The default-only and absent-file paths emit no extra noise, so the typical developer sees no change in upgrade output.

- Custom rows are no longer silently dropped.

- Default-only upgrades stay quiet — no spurious warnings.

- Single, copy-pasteable target file (`instructions.md`) for the manual migration.

- Malformed legacy file does not break the upgrade.

### Security Officer

The change is neutral on attack surface: the helper reads a file that the `_run_upgrade` procedure was already about to delete, performs string comparisons, and writes only to stdout. No new IO paths, no new permissions, no new external calls. The warning text contains workspace-relative file paths only — no secret material is at risk of being printed.

- Read-only access to a file already owned by the workspace user.

- No new external calls or network IO.

- Warning text is bounded to workspace-relative paths.

- Fail-soft branch does not swallow non-parse exceptions, preserving signal on real bugs.

### Data Governance Officer

Data lineage is improved by the explicit migration nudge: developer-customised rows have a documented exit path into `instructions.md` instead of disappearing silently. The historical `references.md` snapshot is still preserved in `.aib_memory/archives/<timestamp>/`, so audit trails remain intact. Classification (Internal) is unchanged; no PII concerns.

- Cleaner lineage chain with no silent data loss for custom rows.

- Historical archives retain prior snapshots verbatim.

- Classification and retention unchanged.

- Curated changelog note ensures the schema change and migration nudge are auditable in version logs.

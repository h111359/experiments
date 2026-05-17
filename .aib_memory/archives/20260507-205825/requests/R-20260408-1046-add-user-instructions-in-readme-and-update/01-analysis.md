# Analysis - Iteration 01

## Executive Summary

- **Request ID**: R-20260408-1046

- **Request title**: add-user-instructions-in-readme-and-update

- **Iteration ID**: 01 (Active; initial iteration, no predecessors)

- **High-level purpose**: Update `.aib_brain/README.md` to correct stale prompt file names, add user-facing workflow scenarios, and include copy-paste VS Code chat invocations; and regenerate `.aib_memory/context.md` to be comprehensive enough that a developer could rebuild the AIB application from it alone.

- **Trigger**: The AIB application underwent significant structural changes in requests R-20260404-0823 through R-20260404-2326 (prompt file renames, addition of `aib-context.md`, removal of GitHub Copilot CLI integration) but `.aib_brain/README.md` was never updated. Users following the README cannot invoke prompts because five of six listed file names no longer exist.

- **context.md status**: Last auto-generated 2026-04-04 18:35; manually patched afterwards per R-20260404-2326 to remove stale references. A full regeneration via `aib-context.md` is needed to ensure completeness and a current workspace inventory.

- No earlier iterations exist for this request.

- No conflicts with prior iterations.


## Scope Interpretation

- **Explicitly in scope**:

  - Update `.aib_brain/README.md` — full rewrite to correct prompt file names, add use case scenarios, add VS Code chat copy-paste invocations, and remove stale `copilot -sp` CLI references.

  - Update `.aib_memory/context.md` — full regeneration by executing `.aib_brain/prompts/aib-context.md` prompt, producing a comprehensive rebuild-ready description.

- **Explicitly out of scope**:

  - Any changes to application code (tool scripts, Python files, conventions, templates, prompts other than the README).

  - Root-level `README.md` (not mentioned in request scope).

  - Changes to `references.md` or any product-doc files other than `context.md`.

- **Implicitly in scope (implicit rule - AIB framework)**:

  - Reading all product-doc files from `references.md` before making documentation changes.

  - Following `context-convention.md` when regenerating `context.md`.


## Domain Knowledge Essentials

- **AIB (AI Builder)**: A minimal, model-agnostic, specification-driven development framework stored in a repository workspace. Organizes work as *requests* and *iterations*, and uses *prompts* to instruct AI agents to perform analysis, planning, implementation, and documentation.

- **Request**: A user-defined unit of work tracked in `.aib_memory/`. Contains a `request.md` specification and one or more *iterations*.

- **Iteration**: A numbered working step within a request. Per-iteration artifacts: analysis, questionnaire, plan, and implementation log.

- **Prompts (AIB sense)**: Markdown files in `.aib_brain/prompts/` defining instructions for AI agents. Users invoke them by telling the AI chat to "Execute" the file by path.

- **VS Code chat**: The GitHub Copilot chat interface inside VS Code where developers invoke AIB prompts interactively.

- **Brain assets** (`.aib_brain/`): Reusable prompts, conventions, templates, and tool scripts. Replaceable on upgrade. Not touched by AIB tool scripts.

- **Memory artifacts** (`.aib_memory/`): Project-specific registers, docs, requests, and context. Changed by AIB tool scripts and prompts.

- **context.md**: Auto-generated synthesis document of all product knowledge. Must have 12 mandatory sections per `context-convention.md`. Fully replaced on each execution of `aib-context.md`.

- **Impacted personas**: Developer / AIB User (primary README audience), AIB Maintainer.


## Technical Knowledge & Terms

- **`.aib_brain/prompts/`** — Seven prompt files exist as of v1.0.11:
  - `aib-analysis.md` — generates iteration analysis document
  - `aib-questionnaire.md` — generates clarifying questionnaire
  - `aib-plan.md` — generates iteration execution plan
  - `aib-implement.md` — executes the request scope and updates `implementation.md`
  - `aib-documentation.md` — updates product documentation; triggers `aib-context.md` upon completion
  - `aib-context.md` — regenerates `.aib_memory/context.md` from all product-doc files
  - `aib-reverse-engineer.md` — reverse-engineers workspace artifacts into product docs

- **Prompt renames (R-20260404-2326)**: Four prompts were renamed to vendor-neutral names: `aib-create-analysis.md` → `aib-analysis.md`; `aib-create-plan.md` → `aib-plan.md`; `aib-create-questionnaire.md` → `aib-questionnaire.md`; `aib-update-documentation.md` → `aib-documentation.md`. The README was NOT updated when these renames happened.

- **`aib-context.md` prompt**: Added in R-20260404-0823. Synthesizes all product-doc files into `context.md`. Entirely absent from the current README.

- **GitHub Copilot CLI removed (R-20260404-2326)**: The `copilot -sp "..."` CLI invocation syntax and all supporting code (`_detect_copilot_cli()`, `discover_prompt_actions()`, `run_prompt_action()`) were removed. The README still shows `copilot -sp` examples, which no longer work.

- **Menu system** (`run.bat` / `run.sh` → `menu.py`): Interactive terminal menu that surfaces only tool scripts, not prompt files. Prompts must be invoked manually from AI chat.

- **SemVer marker**: Empty file `vMAJOR.MINOR.PATCH` in `.aib_brain/`. Current version: `v1.0.11`.

- **context-convention.md**: Normative file defining 12 mandatory sections, formatting rules, preamble format, stub notice format, and 11 quality gates for `context.md`.


## Assumptions

- Assumption A1: The user-facing README referred to in the request is `.aib_brain/README.md`, not the root `README.md`.
  - Rationale: The request `## Scope` explicitly states "Update `.aib_brain\README.md`".
  - Risk if false: Wrong file is updated; root README may need separate update.
  - Falsification method: Re-read the request scope section.

- Assumption A2: The VS Code chat invocation format should remain `Execute .aib_brain/prompts/<name>.md` — unchanged from the current README's "How to run a prompt" instructions.
  - Rationale: This format is already established, functional, and aligns with the request's phrasing "sample prompts ready for copy/paste in VSC chat".
  - Risk if false: Wrong invocation format is documented; prompts fail to execute.
  - Falsification method: Test an invocation in VS Code Copilot chat.

- Assumption A3: context.md must be regenerated by executing `.aib_brain/prompts/aib-context.md`, not via manual editing.
  - Rationale: `context-convention.md` Section "Document Identity" says "Auto-generated by `aib-context.md` prompt. Human edits are not permitted; the file is fully replaced on each execution."
  - Risk if false: Manual edits drift from convention; future regenerations overwrite them.
  - Falsification method: Check `context-convention.md` "Document Identity" section.

- Assumption A4: The six use case scenarios listed in the request are examples, not an exhaustive mandatory list; additional relevant scenarios should be included.
  - Rationale: The request uses "like:" before the list, implying non-exclusive enumeration.
  - Risk if false: Key scenarios might be over-included or under-included.
  - Falsification method: User confirmation.

- Assumption A5: The `copilot -sp "..."` CLI invocation section in the README should be removed entirely.
  - Rationale: GitHub Copilot CLI integration was removed in R-20260404-2326; these commands no longer work.
  - Risk if false: Stale instructions remain and users encounter errors.
  - Falsification method: Verify `copilot` CLI support has been removed from `menu.py` (confirmed in R-20260404-2326 implementation log).


## Impact Assessment

### Affected Components / Areas

- `.aib_brain/README.md` — primary change target; full content revision required.

- `.aib_memory/context.md` — primary change target; full regeneration via `aib-context.md` prompt required.

- No code, tool script, convention, or runtime component is affected.

### Change Type and Dependencies

- `.aib_brain/README.md`: **modify** (full rewrite).
  - Dependency: `.aib_brain/prompts/` directory listing — confirmed 7 files exit.
  - Dependency: AIB holistic workflow steps from `Concepts.md` — confirmed 7-step canonical flow.
  - No downstream dependencies blocked by README content changes.

- `.aib_memory/context.md`: **modify** (full replacement via prompt execution).
  - Dependency: All product-doc files listed in `references.md` (type=product-doc, REF-0001 through REF-0027).
  - Dependency: `context-convention.md` governs output structure (12 mandatory sections, 11 quality gates).

### Domain Impacts

- DOMAIN (KNW): Medium impact. README and context.md are user-facing knowledge artifacts. Correcting prompt names and adding use case scenarios directly improves domain usability.
  - Relevant requirement IDs: KNW-01 (domain glossary), KNW-03 (use cases & personas).

- DOMAIN (RQT): Low impact. No requirements change; documentation accuracy improves to match implemented state.
  - Relevant requirement IDs: RQT-01 (product charter), RQT-02 (requirements document).

- DOMAIN (ARCH): Low informational impact. Architecture description in context.md may gain completeness after full regeneration.
  - Relevant requirement IDs: ARCH-01.

- DOMAIN (CMP): Low informational impact. Prompt inventory in README now matches CMP-01 current state.
  - Relevant requirement IDs: CMP-01.

- DOMAIN (DATA): No impact detected.

- DOMAIN (OBS): No impact detected.

- DOMAIN (OPR): No impact detected.

- DOMAIN (SEC): No impact detected.

### Constraints

- README must remain user-focused; no framework internals, convention details, or Python source excerpts.

- README must list only prompts that physically exist in `.aib_brain/prompts/`.

- `context.md` must follow `context-convention.md` structure exactly (12 mandatory sections in specified order).

- `context.md` is auto-generated; must be produced by running `aib-context.md` prompt, not by manual editing.

- No application code changes permitted.

### Required Documentation Updates

- `.aib_brain/README.md`
  - Required update? YES
  - Reason: Wrong prompt file names (5 of 6); missing `aib-context.md`; stale `copilot -sp` CLI references; missing use case scenarios and VS Code copy-paste prompts.

- `.aib_memory/context.md`
  - Required update? YES
  - Reason: Last auto-generated 2026-04-04 18:35; manually patched after that without full regeneration; workspace file inventory is outdated; timestamp in preamble is stale.

### Decision Points

- **D1: README approach — surgical patch vs. full rewrite**:
  - Option 1 (surgical patch): Fix only the wrong file names and add missing sections. Lower risk of accidental omission of existing content.
  - Option 2 (full rewrite): Rewrite README from scratch with correct, complete user-focused structure.
  - **DECISION: Full rewrite** — the existing README has compounding inaccuracies (5 wrong names, stale CLI section, missing prompt, outdated examples). A clean rewrite avoids residual inconsistencies and produces better user experience. Risk of omission is mitigated by cataloging all current sections before rewriting.

- **D2: context.md approach — manual edit vs. prompt execution**:
  - Option 1 (manual edit): Faster but risks drift from convention and future overwrite.
  - Option 2 (execute `aib-context.md`): Canonical approach; follows convention; produces deterministic output.
  - **DECISION: Execute `aib-context.md`** — convention mandates auto-generation; manual edits are explicitly prohibited.


## Research Plan and Findings

**Methodology**: Internal document scan — read all relevant AIB framework files and compared current README with actual workspace file state.

**Evidence summary**:

- `.aib_brain/prompts/` contains exactly 7 files: `aib-analysis.md`, `aib-context.md`, `aib-documentation.md`, `aib-implement.md`, `aib-plan.md`, `aib-questionnaire.md`, `aib-reverse-engineer.md`.

- Current `.aib_brain/README.md` "Available prompt files" section lists 6 files with 5 wrong names: `aib-create-analysis.md` (incorrect), `aib-create-questionnaire.md` (incorrect), `aib-create-plan.md` (incorrect), `aib-reverse-engineer.md` (correct), `aib-implement.md` (correct), `aib-update-documentation.md` (incorrect). `aib-context.md` is entirely absent.

- The "Optional CLI-style invocation example" section uses `copilot -sp "..."` syntax — removed in R-20260404-2326. This section should be replaced with VS Code chat instructions.

- `context.md` preamble timestamp is 2026-04-04 18:35. R-20260404-2326 implementation log confirms context.md was manually patched (not regenerated) to remove Copilot CLI references. A full regeneration has not been run since then.

- `Concepts.md` holistic workflow defines 7 canonical steps: initialize → create-request → create-analysis / create-questionnaire / create-plan → implement → create-iteration (if needed) → close-iteration → close-request.

- `context-convention.md` mandates 12 sections, 11 quality gates, preamble format with timestamp, and stub notices for empty sections.

- All product-doc files from `references.md` (REF-0001 through REF-0027) are in `.aib_memory/docs/`; many are seeded stubs.

**Gaps and unknowns**:

- Whether the manual patches to `context.md` are complete cannot be verified without running `aib-context.md` prompt and comparing outputs.

- Whether other changes between April 4 and April 8 need to be captured in `context.md` — none found in requests_register.md (no request closed after R-20260404-2326).

**Proposed validation actions**:

- After README update: verify each listed prompt file exists in `.aib_brain/prompts/` (directory listing).
- After context.md regeneration: verify all 12 mandatory sections present per `context-convention.md`.

**Files Read**:

- `.aib_brain/prompts/` (directory listing) — confirmed 7 actual prompt files vs. 6 wrong names in README.
- `.aib_brain/README.md` — current state with 5 wrong prompt names, missing `aib-context.md`, stale `copilot -sp` section.
- `.aib_memory/context.md` — last auto-generated 2026-04-04 18:35; manually patched after that; workspace inventory outdated.
- `.aib_brain/Concepts.md` — holistic workflow (7 steps), supported actions list, all AIB concepts.
- `.aib_brain/conventions/analysis-convention.md` — analysis format rules and Canonical Disambiguation Questionnaire.
- `.aib_brain/conventions/request-convention.md` — request.md format rules for rewrite proposal.
- `.aib_brain/conventions/context-convention.md` — 12-section structure, 11 quality gates, formatting rules.
- `.aib_memory/references.md` — all 29 references including 27 product-docs and context.md.
- `.aib_memory/requests_register.md` — request history; confirmed R-20260404-2326 as last closed request before current active.
- `.aib_memory/requests/R-20260404-2326-remove-github-cli-integration/implementation.md` — confirmed 4 prompt renames and that README was NOT updated.
- `.aib_memory/requests/R-20260408-1046-add-user-instructions-in-readme-and-update/request.md` — active request.
- `.aib_memory/requests/R-20260408-1046-add-user-instructions-in-readme-and-update/iterations.md` — active iteration 01.
- `.aib_memory/docs/03 Requirements/RQT-02.md` — FR and NFR content; confirmed FR-008 description.
- `.aib_memory/docs/01 Product Management/Product Charter/RQT-01.md` — seeded stub; no content.
- [SKIPPED — domain out of scope] ARCH-02, ARCH-03, ARCH-06, ARCH-07, CMP-02, DATA-01 through DATA-09, OBS-01, SEC-01 through SEC-04 — not relevant to a documentation-only README/context update request.


## Rewrite Proposal of the Request

---

## Goal

Update `.aib_brain/README.md` and `.aib_memory/context.md` to accurately reflect the current state of the AIB application (v1.0.11).

`.aib_brain/README.md` must be fully rewritten to:
- list all 7 prompt files in `.aib_brain/prompts/` with their correct names (`aib-analysis.md`, `aib-questionnaire.md`, `aib-plan.md`, `aib-implement.md`, `aib-documentation.md`, `aib-context.md`, `aib-reverse-engineer.md`).
- include at minimum 6 end-to-end use case scenarios mapping user intent to AIB actions, covering: basic analysis → plan → implement flow; analysis with open questions and re-iteration; direct implement → close flow; refactor scenario; documentation update scenario; context regeneration scenario.
- include copy-paste VS Code chat invocation prompts for each of the 7 prompt files using the format `Execute .aib_brain/prompts/<name>.md`.
- remove the stale `copilot -sp` CLI invocation section (GitHub Copilot CLI integration was removed in R-20260404-2326).
- remain user-focused: no convention internals, no Python source code, no `.aib_brain/` framework implementation details.

`.aib_memory/context.md` must be fully replaced by executing `.aib_brain/prompts/aib-context.md`, producing output that passes all 11 quality gates in `context-convention.md`. After regeneration, a developer unfamiliar with AIB must be able to understand and rebuild the application from `context.md` alone.

## Background

The AIB application underwent significant changes in requests R-20260404-0823 through R-20260404-2326:
- Four prompt files were renamed to vendor-neutral names (removed `create-` and `update-` prefixes).
- A new `aib-context.md` prompt was added.
- GitHub Copilot CLI integration was fully removed from the menu system.
- `context.md` was manually patched rather than fully regenerated after these changes.

None of these changes were reflected in `.aib_brain/README.md`. Users following the README will encounter file-not-found errors for 5 of 6 listed prompts and encounter broken `copilot -sp` CLI commands.

## Scope

- Full rewrite of `.aib_brain/README.md` with all correct prompt names, use case scenarios, and VS Code copy-paste invocations.
- Full regeneration of `.aib_memory/context.md` via execution of `.aib_brain/prompts/aib-context.md`.

## Out of scope

- Application code changes (tool scripts, Python files, conventions, templates, or any other `.aib_brain/` prompt files).
- Root `README.md` changes.
- Any `references.md` changes.
- Any product-doc files under `.aib_memory/docs/` other than `context.md`.

## Constraints

- Follow `.aib_brain/conventions/context-convention.md` strictly for `context.md` structure (12 mandatory sections, 11 quality gates).
- README must list only prompt files that physically exist in `.aib_brain/prompts/` at the time of writing.
- README must remain user-focused; do not include framework internals, convention file paths, or Python code.
- VS Code chat invocations must use the format `Execute .aib_brain/prompts/<name>.md`.
- `context.md` must be auto-generated by executing the `aib-context.md` prompt, not manually edited.

## Success criteria

- `.aib_brain/README.md` lists exactly 7 prompt files with correct names matching files in `.aib_brain/prompts/`.
- `.aib_brain/README.md` includes 6 or more end-to-end workflow scenarios.
- `.aib_brain/README.md` contains copy-paste VS Code chat prompts for all 7 prompt files.
- `.aib_brain/README.md` contains no `copilot -sp` references.
- `.aib_memory/context.md` contains all 12 mandatory sections per `context-convention.md`.
- `.aib_memory/context.md` preamble timestamp is current (post April 8, 2026).
- A new AIB user can understand installation and all major usage patterns from `.aib_brain/README.md` alone.
- A developer unfamiliar with AIB can understand and rebuild the application from `.aib_memory/context.md` alone.

---

## Solution Options

**Option A: Targeted Surgical Patch of README + Execute aib-context.md**

- Overview: Precisely correct the 5 wrong prompt file names in the README, add the missing `aib-context.md` entry, add use case sections, add VS Code chat invocations, and remove the `copilot -sp` block. Run `aib-context.md` for context.md.
- Benefits: Minimal disruption to existing README structure; faster to implement.
- Trade-offs: Existing README structure may not integrate the new content cleanly; error-prone when correcting many scattered references.
- Constraints: Must verify every changed line against actual state.
- Risks: Residual inconsistencies if not all stale references are found.
- Expected effort: Low for README; low for context.md.
- Acceptance: All 7 prompt names correct; scenarios present; VS Code prompts present; no `copilot -sp`.

**Option B: Full Rewrite of README + Execute aib-context.md** *(Recommended)*

- Overview: Rewrite `.aib_brain/README.md` from scratch with correct, complete user-focused content structured around use case scenarios. Run `aib-context.md` for context.md.
- Benefits: Clean structure with no residual inaccuracies; best readability for end users; surfaces all current capabilities coherently.
- Trade-offs: More writing effort; risk of omitting useful content from current README.
- Constraints: Must catalog all current useful README sections before rewriting (prerequisites, quick start, tool commands, troubleshooting, iteration vs. request guide) to ensure none are lost.
- Risks: Accidental omission of the "When to Create a New Iteration vs a New Request" decision guide or troubleshooting tips.
- Expected effort: Medium for README; low for context.md.
- Acceptance: All 7 prompt names correct; at least 6 scenarios present; VS Code chat prompts for all 7 prompts; no stale references; all useful existing sections preserved.

**Recommendation**: Option B — full rewrite of the README. The compounding inaccuracies (5 wrong names + stale CLI section + missing prompt) make a surgical patch error-prone. A clean rewrite mitigates residual inconsistencies and improves the user experience. Risk of omission is mitigated by cataloging existing sections first.


## Affected Documentation

| ref_id | document_title | path | reason_for_inclusion |
|--------|----------------|------|----------------------|
| REF-0029 | AIB Context | .aib_memory/context.md | Primary change target — full regeneration required via `aib-context.md` prompt |
| — | AIB README | .aib_brain/README.md | Primary change target — full rewrite required (not registered in references.md; user-granted explicit permission via request scope) |


## Operational & Documentation Implications

- No runtime or operational impact — this is a documentation-only change.

- After README update: users will be able to correctly invoke all 7 prompts from VS Code chat. Before update, following the README would produce file-not-found errors for 5 of 6 listed prompts.

- After context.md regeneration: the file will have a current timestamp, a current workspace file inventory, and a complete machine-regenerated description of the AIB application.

- No runbooks, SLAs, monitoring, alerting, or data quality rules are affected.


## Risks

- Risk R1: README rewrite accidentally omits the "When to Create a New Iteration vs a New Request" decision guide or troubleshooting section.
  - Probability: Medium
  - Impact: Medium (users lose useful guidance for common decisions)
  - Mitigation: Catalog all sections of existing README before rewriting and explicitly carry over each valuable section.
  - Owner (role): AI Automation Agent

- Risk R2: context.md regeneration via `aib-context.md` produces stubs for many product-doc sections because most product-doc files are seeded stubs.
  - Probability: High (confirmed: most product-doc files remain as "seeded by AIB initialize" stubs)
  - Impact: Low (`context-convention.md` mandates stub notices; this is expected behavior and does not block quality gates)
  - Mitigation: Convention mandates stub notices for empty sections; quality gates verified after generation.
  - Owner (role): AI Automation Agent

- Risk R3: After regeneration, context.md omits the description of `aib-context.md` prompt itself (self-referential gap).
  - Probability: Low (`aib-context.md` prompt reads product-doc files where this is described)
  - Impact: Low (minor incompleteness)
  - Mitigation: Manually verify context.md mentions all 7 prompt files after regeneration.
  - Owner (role): AI Automation Agent

- Risk R4: The new README use case scenarios are written at a level too technical or too abstract for new AIB users.
  - Probability: Low
  - Impact: Medium (reduced user onboarding effectiveness)
  - Mitigation: Write scenarios as step-by-step user actions using plain language and concrete copy-paste prompts.
  - Owner (role): AI Automation Agent


## Disambiguation Questionnaire

**Question:** What is the minimal shippable outcome for this iteration (MSI) and what is explicitly excluded?
**Chosen Answer / Value:** MSI — `.aib_brain/README.md` with 7 correct prompt names, 6+ use case scenarios, VS Code chat prompts, no stale CLI references; and `.aib_memory/context.md` regenerated via `aib-context.md`. Excluded: any code changes, root README changes, product-doc file changes.
**Rationale:** Stated explicitly in request scope and success criteria.
**Evidence / Reference:** request.md `## Scope`, `## Out of scope`, `## Success criteria`.
**Impact if changed:** Narrower → some use cases or prompts omitted; broader → code changes violate out-of-scope constraint.

**Question:** Which user-visible changes MUST be demonstrable at iteration end?
**Chosen Answer / Value:** 1) Opening `.aib_brain/README.md` shows all 7 correct prompt file names. 2) All VS Code chat invocation strings in README correspond to files that exist. 3) `context.md` preamble timestamp is after 2026-04-08.
**Rationale:** These are the observable acceptance conditions derived from success criteria.
**Evidence / Reference:** request.md `## Success criteria`.
**Impact if changed:** N/A for this iteration.

**Question:** What are the non-functional targets applicable to this iteration?
**Chosen Answer / Value:** No latency, throughput, or availability requirements apply — this is a documentation-only change. README file size should remain reasonable (< 5 KB is informational target to keep it user-focused).
**Rationale:** Documentation-only change; no runtime performance targets apply.
**Evidence / Reference:** request.md `## Constraints`.
**Impact if changed:** N/A.

- Q4, Q5, Q6 (Data & Contracts): N/A — no data sources, schemas, serialization formats, or error handling rules apply to a documentation-only change. | Chosen Answer / Value: N/A | Rationale: No data assets involved. | Evidence / Reference: request.md `## Out of scope`. | Impact if changed: N/A.

- Q7, Q8, Q9 (Compute & Algorithms): N/A — no algorithms, quality thresholds, or compute constraints apply. | Chosen Answer / Value: N/A | Rationale: Documentation-only change. | Evidence / Reference: request.md `## Scope`. | Impact if changed: N/A.

- Q10, Q11 (Interfaces & Integration): N/A — no APIs, message topics, or compatibility requirements apply. | Chosen Answer / Value: N/A | Rationale: No integration surfaces changed. | Evidence / Reference: Confirmed by scope. | Impact if changed: N/A.

- Q12, Q13, Q14 (Security, Privacy, Compliance): N/A — no new access-controlled assets, no PII, no secrets. | Chosen Answer / Value: N/A | Rationale: Documentation-only change; all artifacts classified Internal with no sensitive data. | Evidence / Reference: context.md Security section. | Impact if changed: N/A.

- Q15, Q16 (Observability & Operations): N/A — no metrics, logs, or alerts required. | Chosen Answer / Value: N/A | Rationale: Documentation update; no observable operational change. | Evidence / Reference: Confirmed by scope. | Impact if changed: N/A.

**Question:** What runbook/SOP updates are required, if any?
**Chosen Answer / Value:** None. The README itself is the SOP for users; updating it is the scope item, not a downstream runbook.
**Rationale:** README is the primary user guide; no separate runbooks exist for AIB prompt invocation.
**Evidence / Reference:** `.aib_brain/README.md` existing structure.
**Impact if changed:** N/A.

**Question:** Which product docs must be created or updated (paths), and is editing permitted?
**Chosen Answer / Value:** `.aib_brain/README.md` — edit permitted (explicit user scope grant); `.aib_memory/context.md` — auto-generated (not directly edited; regenerated by prompt; REF-0029 has edit_allowed=N for automation tool scripts but `aib-context.md` prompt is the canonical generator).
**Rationale:** Both files are primary targets per request scope.
**Evidence / Reference:** request.md `## Scope`; `context-convention.md` "Document Identity"; `references.md` REF-0029.
**Impact if changed:** N/A.

**Question:** What acceptance evidence will be recorded and where?
**Chosen Answer / Value:** Evidence recorded in `implementation.md` for this request. Evidence items: directory listing of `.aib_brain/prompts/` confirming 7 files; section listing of rewritten README; confirmation of 6+ scenarios present; confirmation of `context.md` preamble timestamp.
**Rationale:** Per AIB implementation convention; `implementation.md` is the append-only record.
**Evidence / Reference:** `Concepts.md` implementation.md definition; implementation-convention.md.
**Impact if changed:** N/A.

**Question:** What is the rollback strategy if acceptance fails?
**Chosen Answer / Value:** Git revert to previous commit of `.aib_brain/README.md` and `.aib_memory/context.md`. Both files are tracked in version control.
**Rationale:** Both files are Markdown tracked in the Git repository; revert is deterministic.
**Evidence / Reference:** context.md development practices section; `.gitignore` (confirms neither file is ignored).
**Impact if changed:** N/A.


## Open Questions & Next Actions

No open questions requiring user input identified. All required information was resolved from internal workspace sources.

**Next actions (owner: AI Automation Agent)**:

1. Catalog all current sections of `.aib_brain/README.md` to ensure no valuable content is omitted in the rewrite.
2. Rewrite `.aib_brain/README.md` in full: correct all 7 prompt names, add 6+ use case scenarios, add VS Code chat copy-paste prompts for all 7 prompts, remove `copilot -sp` section, preserve all valuable existing sections.
3. Execute `.aib_brain/prompts/aib-context.md` to regenerate `.aib_memory/context.md`.
4. Verify all 7 prompt file names in the rewritten README match actual files in `.aib_brain/prompts/`.
5. Verify context.md contains all 12 mandatory sections per `context-convention.md`.
6. Record outcome in `implementation.md`.

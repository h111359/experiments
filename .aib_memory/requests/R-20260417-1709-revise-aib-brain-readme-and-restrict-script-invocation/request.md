## Goal

Update `.aib_brain/README.md` to reflect that users must not invoke Python scripts in `.aib_brain/tools/` directly. Script invocations are the exclusive responsibility of AIB prompts (the AI agent). The README must be revised to remove or reframe instructions that suggest direct script invocation by the user, while preserving a clear guide for prompt-based and interactive-menu-based workflows.

## Background

The current `.aib_brain/README.md` contains a "Common Commands" section with explicit Windows and Linux/macOS examples showing users how to run `initialize.py`, `create-request.py`, and `close-request.py` directly from the terminal. The "Typical Daily Flow" also references these scripts by name in a way that implies users are expected to invoke them. This contradicts the intended AIB workflow (see ADR-0003 in `context.md`) where all script execution is delegated to AIB prompts (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`). Direct user invocation of tool scripts bypasses the prompt-governed workflow, risks state inconsistencies, and can undermine the single-Active-request invariant (FR-001, ALG-0002).

## Scope

- Update `.aib_brain/README.md`:

  - Remove or reframe the "Common Commands" section so it is explicit that these scripts are NOT intended for direct user invocation.

  - Revise the "Typical Daily Flow" to remove any step that implies direct user script execution.

  - Add a prominent note or warning clearly stating that users must not run scripts in `.aib_brain/tools/` directly — AIB prompts invoke them automatically.

  - Preserve the Quick Start section (interactive menu via `run.bat`/`run.sh`) and all prompt invocation instructions as the recommended workflows.

## Out of scope

- Changes to any tool scripts in `.aib_brain/tools/`.

- Changes to prompt files in `.aib_brain/prompts/`.

- Changes to conventions or templates.

- Changes to `.aib_memory/` artifacts beyond those updated by this analysis run (Assumptions, Plan, Testing, Documentation, Questions & Decisions sections in `request.md`).

## Constraints

- Only `.aib_brain/README.md` is a content-change target for the implementation.

- The README must remain accurate with respect to current product capabilities.

- Must not introduce external links.

- Changes must be minimal and targeted — do not restructure sections that are unrelated to script invocation.

## Success criteria

- `.aib_brain/README.md` contains no instructions or code examples that encourage users to invoke `.aib_brain/tools/*.py` scripts directly.

- A clear and prominent note is present in the README informing users that tool scripts are invoked by prompts only, not by the user.

- The interactive menu (`run.bat`/`run.sh`) remains the documented entry point for interactive use.

- The prompt invocation guide remains fully intact and unaltered in intent.

- All steps in the daily flow refer only to prompt execution or interactive menu launch actions.

## Assumptions

- A1: `.aib_brain/README.md` is not listed in `references.md` with `edit_allowed=Y`. Its modification is explicitly authorized by this request under human governance.
  - Risk if false: Automation cannot flag this file for edit; the change remains manual (AI-authored directly via prompt), which is acceptable for a brain-asset doc.

- A2: `initialize.py` is the one script a user may still invoke directly — specifically as a one-time first-time setup step before any `input.md` content or Active request exists. All other scripts (`create-request.py`, `close-request.py`) are exclusively prompt-invoked.
  - Risk if false: If `initialize.py` must also be fully hidden, the README would provide no guidance for first-time workspace setup, leaving new users without an entry point.

- A3: Removing the "Common Commands" direct script invocation examples does not break any existing functionality; the interactive menu and prompt invocations are fully adequate for the user workflow.
  - Risk if false: An undocumented edge case requiring direct script invocation exists. In that case the scripts can still be called by a developer who reads the source, but the README would not document this path.

## Plan

### Task 1: Revise `.aib_brain/README.md`
**Intent:** Remove direct lifecycle script invocation examples from the README and add a prominent note prohibiting users from running `.aib_brain/tools/*.py` scripts directly.
**Inputs:** `.aib_brain/README.md` (current content), `request.md` success criteria.
**Outputs:** Updated `.aib_brain/README.md`.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Remove the "Common Commands" section's Windows and Linux/macOS examples for `create-request.py` and `close-request.py`.
2. Add a prominent blockquote or bold warning near the top of the README (after the Purpose section or just before Quick Start) stating that scripts in `.aib_brain/tools/` are invoked by AIB prompts automatically and must not be run directly by users.
3. Revise the "Typical Daily Flow" to remove any step that names a `.py` script as a user action; replace with the corresponding prompt invocation or menu action. Preserve `initialize.py` as the one-time first-time setup action.
4. Verify no remaining `python .aib_brain\tools\create-request.py` or `python .aib_brain\tools\close-request.py` command examples exist.
5. Confirm all prompt invocation instructions remain intact.
**Done Criteria:**
- No copyable `create-request.py` or `close-request.py` command examples remain in the README.
- A visible warning note is present prohibiting direct script invocation.
- Prompt invocation section is unchanged.
- Quick Start (run.bat/run.sh) section is unchanged.
**Dependencies:** None.
**Risk Notes:** None.

## Testing

- T1 — No lifecycle script examples: Search `.aib_brain/README.md` for `create-request.py` and `close-request.py` as copyable terminal commands. Expected outcome: Zero command-block occurrences referencing these scripts.

- T2 — Warning note present: Open `.aib_brain/README.md` and confirm a prominent note warns against direct script invocation by users. Expected outcome: Note is present, clearly visible, and unambiguous.

- T3 — Prompt invocations intact: Verify all three prompt invocations (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) are present and unchanged in the README. Expected outcome: All three invocations are present in the copy-paste section.

- T4 — Quick Start intact: Verify the Quick Start section (`run.bat`/`run.sh` commands) is present and unmodified. Expected outcome: Section is present with correct Windows and Linux/macOS commands.

- T5 — Re-run idempotency: Re-running `aib-implement.md` for this request produces the same README content without further modification. Expected outcome: No content drift on second implementation run.

## Documentation

- `.aib_brain/README.md` (ref_id: N/A) — Primary target: reframe to prohibit direct script invocation and align with the prompt-driven workflow design.

## Questions & Decisions

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_brain/README.md` | Modified | Remove direct lifecycle script invocation examples; add prohibition note; revise daily flow. |
| `.aib_memory/requests/R-20260417-1709-revise-aib-brain-readme-and-restrict-script-invocation/request.md` | Modified | AI-generated sections (Assumptions, Plan, Testing, Documentation, Code Scan, Internal Review, Stakeholder Review) populated during analysis. |
| `.aib_memory/requests/R-20260417-1709-revise-aib-brain-readme-and-restrict-script-invocation/analysis.md` | Created | Analysis artifact for this request. |
| `.aib_memory/requests/R-20260417-1709-revise-aib-brain-readme-and-restrict-script-invocation/inputs/input-archive-2026-04-17_17-11-02.md` | Created | Archive of `input.md` content before reset. |
| `.aib_memory/input.md` | Modified | Reset to seed template with active request ID after analysis completes. |

## Internal Review of Request and Product Docs

- OK: `request.md` Goal, Background, Scope, and Success criteria are consistent with `context.md` (FR-001, FR-003, ADR-0003, FR-010).

- Contradiction: `.aib_brain/README.md` "Common Commands" section shows `create-request.py` and `close-request.py` as direct user commands. This contradicts FR-010 (menu does not expose lifecycle commands) and the `EXCLUDE_SCRIPTS` design in `menu.py`. This request resolves the contradiction.

- Cross-ref issue: `.aib_brain/README.md` is not listed in `references.md` with `edit_allowed=Y`. The file is a `.aib_brain/` brain asset. Its modification is explicitly authorized by this request's scope; however, it is not automatable via the register-based edit-gating mechanism. This is an acceptable exception for a documentation-only change under human-governed requests.

- OK: Scope is single-file, minimal, and directly traceable to the input intent.

- OK: Success criteria are measurable and testable (T1–T5).

- OK: No missing information; the current README content, design docs, and conventions provide sufficient context for implementation.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

This is a low-risk, editorial change to a single Markdown file with no code, script, or state mutations. The architectural intent (ADR-0003 — separation of brain and memory, prompt-governed invocation model) is already enforced by all scripts and prompts; the README was simply lagging behind. Fixing the documentation is necessary for coherent architectural documentation and to prevent workflow divergence caused by developers following outdated README examples. No design trade-offs are required.

- Aligns README with ADR-0003 and the `EXCLUDE_SCRIPTS` design decision.
- No breaking changes; the scripts remain callable if ever needed by a developer who reads the source.
- Preserves `initialize.py` as the documented first-time setup action, which is architecturally correct.
- Risk: minimal; scope is a single Markdown file.
- Recommend: implementation is straightforward; no spike required.

### Product Owner

The request addresses a real developer friction point: users who follow the README literally may call lifecycle scripts directly, causing hard-to-diagnose state errors (e.g., creating a duplicate Active request). The business value is clear — fewer workflow errors, cleaner developer experience, and documentation that matches the actual product design. Success criteria are measurable and test coverage (T1–T5) is adequate.

- Business value is clear and directly tied to developer experience.
- Scope is well-bounded and delivers a self-contained, verifiable change.
- Acceptance criteria are testable without ambiguity.
- Priority: appropriate for immediate implementation.
- No user-visible product behavior changes.

### User

The change reduces the surface area of confusion. New users who read the README and instinctively copy-paste Python commands will no longer find lifecycle script examples to copy. The interactive menu and prompt invocations remain fully documented. The one potential friction point is that `initialize.py` must remain accessible — its documentation should remain explicit because it is the mandatory first step before any prompt workflow is possible.

- Positive: Removes misleading examples that could cause errors.
- Positive: The interactive menu path and prompt invocations remain clear.
- Neutral: `initialize.py` remains documented; no first-time user is left without guidance.
- Recommendation: The warning note should be clear enough that even a first-time reader understands why scripts are not to be invoked directly.

### Security Officer

No security implications. This is a documentation change only. No credentials, no network access, no secrets handling changes. The change marginally improves security hygiene by discouraging undocumented script invocation patterns that bypass the prompt-governed safety guards (state validation, invariant enforcement). No new attack surface is introduced or removed.

- No OWASP Top 10 concerns.
- No authentication or authorization changes.
- No data exposure risk.
- Positive: Reduces the likelihood of misuse of lifecycle scripts outside the intended workflow.

### Data Governance Officer

No data lineage, retention, classification, or compliance impacts. All artifacts are internal engineering documentation. The change does not affect any data flow, data storage, or data access pattern. No regulatory considerations apply.

- No data governance concerns.
- All artifacts remain classified as internal engineering documentation.
- No cross-border data transfer or PII handling involved.

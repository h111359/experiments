## Executive Summary

- Request ID: `R-20260510-0744`; title: **Archive input.md on standard-flow reset**.

- Purpose: clarify lifecycle semantics so standard-flow analysis preserves human-entered `input.md` content before reset, while skipping archival for pristine seed-state input.

- Scope focus: prompt behavior in `.aib_brain/prompts/aib-analysis.md`, with test and context alignment.

- Risk profile: medium, because lifecycle wording changes can unintentionally alter toggle branches (`No changes`, `Skip analysis`) and reset ordering guarantees.

- Request updates produced by this analysis run: regenerated `## Assumptions`, `## Plan`, and `## Documentation` in `.aib_memory/request-R-20260510-0744.md`.

## Domain Knowledge Essentials

- **Standard analysis flow**: `aib-analysis.md` run with exactly one Active request already present.

- **Non-stub reset event**: reset of `.aib_memory/input.md` after processing meaningful user content (not the untouched seed template).

- **Input archive**: immutable snapshot in `<request-folder>/inputs/input-archive-<timestamp>.md` used for traceability.

- **Lifecycle consistency**: both auto-request and standard-flow paths should preserve materially relevant operator input before destructive overwrite.

- **Impacted roles**:
  - Developer/operator: needs confidence that submitted amendment text is not lost.
  - AIB maintainer: needs deterministic wording that is testable and branch-safe.
  - Reviewer/auditor: needs an explainable evidence trail for request evolution.

- **Business process impact**:
  - Amendment loops remain auditable.
  - Re-runs stay predictable across branches and avoid noisy archives for untouched template state.

## Technical Knowledge & Terms

- **Key assets**:
  - Prompt spec: `.aib_brain/prompts/aib-analysis.md`.
  - Active request artifact: `.aib_memory/request-R-20260510-0744.md`.
  - Active analysis artifact: `.aib_memory/analysis-R-20260510-0744.md`.
  - Product context baseline: `.aib_memory/context.md`.

- **Runtime constraints**:
  - Exactly one Active request.
  - `No changes` branch remains exactly two file writes and stop.
  - Direct standard-flow runs still perform reset as the last action.

- **Quality attributes**:
  - Reliability: no loss of substantive user input during reset.
  - Determinism: explicit rule for when to archive and when not to archive.
  - Maintainability: assertions in prompt-structure tests prevent drift.

- **Evidence -> implication**:
  - Existing prompt text already archives in auto-request branch -> standard flow needs equally explicit conditional archive wording.
  - Current request scope explicitly asks for pre-reset archival semantics -> updates should avoid broader lifecycle refactors.
  - Context text should match final prompt semantics -> context update task must be present in plan.

- **Files Read**:
  - `.aib_memory/instructions.md`
  - `.aib_memory/requests_register.md`
  - `.aib_memory/request-R-20260510-0744.md`
  - `.aib_memory/input.md`
  - `.aib_memory/context.md`
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_brain/prompts/aib-analysis.md`

## Research Results

- Repository convention pattern: lifecycle-critical behavior is defined in prompt MUST-language and locked by text-assertion tests.

- Existing branch pattern: `No changes` has strict side-effect boundaries; new archive semantics must stay explicitly outside that branch.

- Documentation pattern: `.aib_memory/context.md` is the authoritative behavioral summary; prompt updates without context sync create drift risk.

- Implication: implement as a narrow prompt-spec clarification plus regression tests and context synchronization.

## External Benchmarking

- **Write-ahead safety pattern (transactional systems)**
  - Persist user intent before destructive mutation.
  - Applicability: reset is destructive to prior `input.md` content.
  - Decision: adopt archive-before-reset ordering for substantive standard-flow input.

- **CI/CD artifact retention pattern**
  - Preserve pre-transform inputs to support post-change traceability.
  - Applicability: request amendments are operational inputs affecting downstream artifacts.
  - Decision: retain substantive snapshots per run and avoid over-retention of seed-state stubs.

- **Idempotent tooling pattern**
  - Avoid low-value duplicate artifacts when state is effectively unchanged.
  - Applicability: untouched seed template should not trigger archive writes.
  - Decision: use conditional archive trigger tied to non-stub state.

## Minimal Spikes and Experiments

- **Spike: branch-collision feasibility**
  - Hypothesis: standard-flow archive wording can be added without violating `No changes` branch write limits.
  - Approach: compare toggle branch constraints and final-step reset rules in `.aib_brain/prompts/aib-analysis.md`.
  - Outcome: branch boundaries are explicit enough to add scoped wording safely.
  - Conclusion: feasible with precise branch-scoped language.

- **Spike: test strategy fit**
  - Hypothesis: prompt-structure assertions are sufficient to prevent regression for this change type.
  - Approach: inspect existing test organization and lifecycle assertion style in the workspace tests.
  - Outcome: current repository already uses stable text-assertion guardrails for prompt semantics.
  - Conclusion: extend those assertions rather than introducing new runtime harnesses.

## AI Copilot Suggestions

- Finding: "non-stub" is the most ambiguity-prone phrase in the request.
  - Actionable suggestion: define it concretely in prompt text (for example, seed-template-equivalent vs meaningful deviation) so assertions remain deterministic.

- Finding: the request is appropriately narrow and does not require tool-script changes.
  - Actionable suggestion: keep implementation constrained to prompt text, tests, and context updates; avoid touching unrelated lifecycle scripts.

- Finding: branch safety is the highest regression risk, not implementation complexity.
  - Actionable suggestion: add explicit regression assertions that `No changes` still enforces exactly two writes and does not inherit standard-flow archive behavior.

- Finding: scope sizing is right-sized for the goal.
  - Actionable suggestion: resist adding extra lifecycle redesign items in this iteration.

## Testing

- T1 — Standard-flow archive requirement present: Validate `.aib_brain/prompts/aib-analysis.md` explicitly states that non-stub standard-flow resets archive prior `input.md` content before reset. Expected outcome: deterministic, branch-scoped wording exists.

- T2 — Auto-request path remains intact: Validate `.aib_brain/prompts/aib-analysis.md` still archives `input.md` and moves attachments in the Auto-Request Creation Branch. Expected outcome: existing branch semantics remain unchanged.

- T3 — No-changes side-effect boundary preserved: Validate `.aib_brain/prompts/aib-analysis.md` still enforces exactly two writes in `No changes` and then stops. Expected outcome: no extra writes are implied.

- T4 — Prompt-structure regression suite: Run `c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe -m pytest tests/test_analysis_prompt_structure.py`. Expected outcome: all assertions pass, including new standard-flow archive semantics.

- T5 — Related lifecycle regression suite: Run `c:/Hristo/projects/AI_Builder/.venv/Scripts/python.exe -m pytest tests/test_questions_in_input_md.py tests/test_artifact_placement.py`. Expected outcome: Q&A and artifact-placement behavior remains stable.

- T6 — Re-run idempotency check: Re-run T4 immediately without further edits. Expected outcome: unchanged pass outcome and no additional file changes required.

## Multi-Perspective Stakeholder Review

### Senior Solution Architect
The requested change is technically straightforward but lifecycle-sensitive. The architecture is best served by explicit, branch-scoped prompt language and assertion-backed guarantees, rather than introducing new runtime scripts.

- The change should remain text-level in prompt spec plus tests.
- Archive-before-reset improves durability of human input.
- Branch scoping is mandatory to avoid `No changes` regressions.

### Product Owner
The request delivers clear business value by preventing silent loss of submitted amendment content while keeping process noise low. Success criteria are specific and measurable, which supports fast acceptance.

- The objective is user-trust and traceability, not feature expansion.
- Scope is clear and bounded.
- Context documentation must be synchronized to avoid future ambiguity.

### User
For operators, expected behavior is intuitive: meaningful input should be preserved before reset, while untouched template state should not generate archive clutter. This lowers friction during repeated analysis cycles.

- Improves confidence during re-runs.
- Keeps request history cleaner by avoiding low-value archives.
- Makes archive behavior easier to reason about.

### Security Officer
No new network or auth surfaces are introduced; this is a local lifecycle semantics update. The primary concern is controlled retention of archived input, which is improved by conditional archival rather than unconditional writes.

- No expansion of attack surface.
- Conditional archival supports data minimization.
- Existing repo access controls remain the protection boundary.

### Data Governance Officer
The change strengthens data lineage by ensuring substantive human input is retained when it affects request evolution. Consistent semantics across lifecycle branches improves auditability and interpretation quality.

- Better provenance for amendment-driven changes.
- Reduced ambiguity across request histories.
- Requires context updates to maintain documentation integrity.

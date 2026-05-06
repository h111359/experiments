## Executive Summary

- **Request ID:** R-20260420-1727

- **Title:** Analysis prompt and workflow improvements

- **Purpose:** Address one confirmed bug and three usability/quality enhancements across the AIB analysis prompt (`aib-analysis.md`), the implement prompt (`aib-implement.md`), and supporting assets (`initialize.py`, `request-convention.md`).

- **Bug (item 1):** After `aib-implement.md` closes a request via `close-request.py`, `input.md` is not reset — its `## Active request` line continues to show the now-Closed request ID. This leaves the workspace in a deceptive state: subsequent menu display or accidental analysis execution may behave unexpectedly.

- **Enhancement (item 2):** The Question threshold row in `input.md` options carries no scale-direction labels. Adding `(all)` after value 1 and `(mandatory only)` after value 5 immediately communicates the scale semantics.

- **Enhancement (item 3):** Q-blocks offer multiple options but provide no guidance on which the AI considers most appropriate. A recommended-answer marker improves decision quality.

- **Enhancement (item 4):** The analysis prompt has no explicit instruction to identify ambiguous or underspecified parts of a request that would lead to materially different implementation paths. Adding this instruction closes a quality gap.

- **`request.md` updates performed this run:** Assumptions, Plan, Documentation, Questions & Decisions, Code and Asset Scan for Impacted Components, Internal Review of Request and Product Docs sections have been written or updated.

---

## Domain Knowledge Essentials

- **AIB (AI Builder):** Minimal, model-agnostic framework for specification-driven development. Operates through Markdown prompt files, convention files, and Python tool scripts under `.aib_brain/`; workspace artifacts are stored in `.aib_memory/`.

- **Request:** A structured work item defined in `request.md` inside a dedicated folder under `.aib_memory/requests/`; tracked in `requests_register.md` with lifecycle states Active and Closed.

- **input.md:** The primary ephemeral communication file between the developer and the AI. Contains three sections: `## Active request` (display only, shows the current Active request ID or "No active request"), `## Options` (toggles and threshold selector), and `## Input` (developer's free-text intent). It is seeded by `initialize.py` and reset by `aib-analysis.md` as its final step.

- **Seed template:** The canonical initial string content for `input.md`; currently hardcoded in both `initialize.py` and `aib-analysis.md`. Both must stay in sync.

- **Question threshold:** A 1–5 integer scale embedded in `input.md ## Options`. Controls when Q-blocks are surfaced to the developer vs. resolved autonomously by the AI. Lower values raise more questions; higher values raise fewer. Value 3 is the default.

- **Q-block:** A structured multiple-choice question block written into `request.md ## Questions & Decisions` when a decision point meets or exceeds the threshold. Format is defined in both `aib-analysis.md` and `request-convention.md`.

- **Recommended marker:** A textual annotation on one option within a Q-block indicating the AI's preferred resolution given the analysis context.

- **Ambiguity detection:** The analytical practice of identifying underspecified or multiply-interpretable parts of a request that would lead to different implementation or design choices if left unresolved.

- **Impacted roles/personas:** Developer (reads and answers Q-blocks, acts on reset `input.md`); AIB Maintainer (owns `.aib_brain/` files); AI Automation Agent (executes prompts, applies instructions).

---

## Technical Knowledge & Terms

- **`aib-analysis.md`:** The analysis prompt. On a standard run it: (1) auto-creates a request if none is Active, (2) generates `analysis.md`, (3) updates `request.md` optional sections, and (4) resets `input.md` to the seed template as its **last step**. The seed template string is embedded inline in the prompt text.

- **`aib-implement.md`:** The implement prompt. Its final step is invoking `close-request.py`. It does **not** currently include any step to reset `input.md`. This is the source of the bug.

- **`close-request.py`:** A Python script that marks the Active request Closed in `requests_register.md`. It has no knowledge of `input.md` and performs no file writes to it.

- **`initialize.py`:** Seeds the `.aib_memory/` structure. The `input.md` seed is a hardcoded multi-line string constant inside the script. Any format change to the threshold row must be reflected here.

- **`request-convention.md`:** Normative document defining the required structure and schema for `request.md`, including the Q-block format definition.

- **Seed string consistency invariant:** The `input.md` seed string appears in two places: `initialize.py` (initial seeding) and `aib-analysis.md` (reset after each run). If these diverge, the workspace state varies depending on which code path was used to create/reset `input.md`.

- **Files read for this analysis:**
  - `.aib_memory/context.md` (REF-0001, product-doc)
  - `.aib_brain/Concepts.md` (REF-0002, domain)
  - `.aib_brain/conventions/analysis-convention.md`
  - `.aib_brain/conventions/request-convention.md`
  - `.aib_brain/prompts/aib-analysis.md`
  - `.aib_brain/prompts/aib-implement.md`
  - `.aib_brain/tools/initialize.py`
  - `.aib_brain/tools/close-request.py`
  - `.aib_memory/references.md`
  - `.aib_memory/requests_register.md`
  - `.aib_memory/input.md`

---

## Research Results

### Bug root cause: stale `input.md` after implement

`aib-implement.md` execution flow (final steps):
1. Confirm all implementation work and tests pass.
2. Execute `aib-context.md`.
3. Invoke `python .aib_brain/tools/close-request.py --workspace .` — **this is the final step**.

`close-request.py` only modifies `requests_register.md`. It does not touch `input.md`.

`aib-analysis.md` resets `input.md` as its last step after all artifacts are written. But `aib-implement.md` does not invoke `aib-analysis.md` at the end; it invokes it only at the start if no Active request exists.

Result: after implement + close-request.py, `input.md ## Active request` still shows the former request ID.

### Threshold row format: no external labels

The threshold row currently reads:

```
- Question threshold: [ ] 1  [ ] 2  [x] 3  [ ] 4  [ ] 5
```

There is no indication of what low vs. high values mean. The scale direction (1 = all questions, 5 = only mandatory) is documented only in `aib-analysis.md`'s 5-Level Severity Scale table, which developers typically don't read every run.

### Q-block format: no recommended marker

Current Q-block schema (from both `aib-analysis.md` and `request-convention.md`):

```
**Q<nnn>**: <question text>
- [ ] Option A: <text>
- [ ] Option B: <text>
- [ ] Other: ___
> Answer:
```

No field or annotation indicates which option the AI recommends. Developers must infer preference from the question phrasing alone.

### Ambiguity detection: not instructed

The `## Questions & Decisions` generation block in `aib-analysis.md` instructs the AI to:
- Apply the 5-level severity scale
- Check whether the answer is determinable from existing workspace docs
- Raise Q-blocks at or above the threshold

It does **not** explicitly instruct the AI to proactively scan for ambiguities in the request text that could lead to diverging implementation outcomes. This means ambiguities may be silently resolved with an assumption rather than surfaced as Q-blocks.

---

## External Benchmarking

- **GitHub Issues / Jira — recommended option pattern:** Many issue-tracking and decision-logging tools support a "default" or "suggested" label on options in multi-choice fields. The pattern is ubiquitous and consistently improves decision throughput by anchoring the reviewer to the most likely correct choice. Applicability: **adopt** the inline `*(recommended)*` annotation as it requires no schema extension.

- **MADR (Markdown Architecture Decision Records) — decision outcome field:** MADR convention includes a `Status` field and a `Decision Outcome` block with a clearly labeled chosen option. The recommended-answer concept in AIB Q-blocks parallels the MADR "proposed decision" field. Takeaway: keeping the recommendation inline (adjacent to the option) rather than in a separate section is preferred for scanability. Applicability: **adopt** inline placement; **reject** separate-section approach (adds visual noise in short Q-blocks).

- **RFC 2119 / BCP 14 — normative threshold language:** Using directional plain-English labels in option selectors is consistent with the BCP 14 practice of expressing intent concisely. Applicability: **adopt** the `(all)` / `(mandatory only)` shorthand as unambiguous and minimal.

- **Conventional Commits / Semantic Versioning — ephemeral state reset patterns:** Several CLI tools that maintain ephemeral state files (e.g., `COMMIT_EDITMSG`, `MERGE_MSG`) reset them automatically after the corresponding workflow step completes. This is precisely what AIB's `input.md` should do after the implement workflow closes a request. Applicability: **adopt** the post-close reset as a standard hygiene step.

---

## Minimal Spikes and Experiments

**Spike: locate all occurrences of the input.md seed template string**
- Hypothesis: The seed template string is embedded in exactly two places: `initialize.py` and `aib-analysis.md`.
- Approach: Read both files and search for the literal `Question threshold:` substring.
- Outcome: Confirmed — `initialize.py` line 62 and `aib-analysis.md` (multiple reset references) each embed the full seed string. No other file contains the string.
- Conclusion: Both locations must be updated atomically to maintain the consistency invariant.

**Spike: confirm that close-request.py has no input.md interaction**
- Hypothesis: `close-request.py` does not read or write `input.md`.
- Approach: Read the full source of `close-request.py`.
- Outcome: Confirmed — the script operates only on `requests_register.md` and optionally `iterations.md`. No reference to `input.md`.
- Conclusion: The input.md reset must be added either in `aib-implement.md` (prompt) or in `close-request.py` (script). Both are viable; Q001 defers to the developer.

---

## AI Copilot Suggestions

- **Scope is right-sized but carries coupling risk.** All four items are genuinely related (they all touch the `input.md` lifecycle and the Q-block schema), and bundling them is efficient. However, the bug fix (item 1) is independent of the enhancements (items 2–4) and could be delivered alone without risk. If the Q001 decision is delayed, item 1 could block the whole request unnecessarily. Consider splitting into two requests if Q001 is not answered promptly.

- **The recommended-marker enhancement is under-specified without Q002.** The two proposed formats (inline suffix vs. separate line) have different implications for automated parsing. If AIB ever needs to parse Q-blocks programmatically (e.g., to auto-apply recommendations), a separate `> Recommended:` line would be far more machine-readable than an inline annotation. The current request treats this as a purely cosmetic change, but the decision has latent architectural weight. The developer should be aware of this before answering Q002.

- **The ambiguity-detection instruction in item 4 is well-framed but should be placed precisely.** The instruction fits naturally before the threshold check in the `## Questions & Decisions` generation block — not after, because the threshold check governs whether to raise a Q-block at all. If placed after the threshold logic, an ambiguity identified below the threshold would be silently dropped. The instruction should trigger identification first, then severity rating, then threshold filtering.

- **Seed template duplication is a maintenance liability.** The `input.md` seed string now appears in two files (`initialize.py` and `aib-analysis.md`). This request adds a third content-bearing change to both (the scale labels). A longer-term simplification would be to define the seed in a single location (e.g., a `common.py` constant or a template file) and have both callers import or read it. This is out of scope for this request but should be recorded as a future improvement.

---

## Testing

- T1 — Inspect implement prompt for reset step (SC-01, partial): Read `.aib_brain/prompts/aib-implement.md`; verify it contains an instruction to reset `input.md` to the seed template after `close-request.py` succeeds. Expected outcome: The file contains a line/paragraph that explicitly resets `input.md` with "No active request" as the last step. See UAT_scenarios.md — UAT-01 for end-to-end validation.

- T2 — Inspect `initialize.py` threshold row (SC-02): Read `.aib_brain/tools/initialize.py`; verify the `input_seed` string contains `[ ] 1 (all)` and `[ ] 5 (mandatory only)` in the threshold row. Expected outcome: Both label strings are present in the seed constant.

- T3 — Inspect `aib-analysis.md` threshold row in seed string (SC-03): Read `.aib_brain/prompts/aib-analysis.md`; verify every occurrence of the seed template reset string contains `[ ] 1 (all)` and `[ ] 5 (mandatory only)` in the threshold row. Expected outcome: All seed string occurrences are updated.

- T4 — Inspect `aib-analysis.md` Q-block format for recommended marker (SC-04, partial): Read `.aib_brain/prompts/aib-analysis.md`; verify the Q-block format schema includes the recommended-answer marker. Expected outcome: The Q-block format example contains the agreed marker format. See UAT_scenarios.md — UAT-02 for live execution validation.

- T5 — Inspect `aib-analysis.md` for ambiguity-detection instruction (SC-05, partial): Read `.aib_brain/prompts/aib-analysis.md`; verify the `## Questions & Decisions` generation block contains an instruction matching the intent of "Identify ambiguous or underspecified parts of the active request". Expected outcome: The instruction is present before the threshold-check logic. See UAT_scenarios.md — UAT-03 for live execution validation.

- T6 — Cross-check Q-block format between `aib-analysis.md` and `request-convention.md` (SC-06): Read both files; compare the Q-block format schema in each. Expected outcome: Both files show an identical Q-block format including the recommended-answer marker.

- T7 — Re-run idempotency: Re-run `aib-analysis.md` on this same request (R-20260420-1727) after implementation; verify that `request.md` optional sections are replaced (not duplicated) and `analysis.md` is fully replaced. Expected outcome: Exactly one `## Assumptions`, `## Plan`, etc. section exists in `request.md`; `analysis.md` is a single complete file.

---

## Multi-Perspective Stakeholder Review

### Senior Solution Architect

This request targets four distinct change points that all stem from the same design gap: incomplete lifecycle coverage of the `input.md` reset step. The bug fix (item 1) is architecturally the most important — a stateful file left in a misleading state after a workflow completes is a reliability violation. The enhancement items are low-risk text changes to prompt and convention files. The main architectural risk is the duplication of the seed template string; this request will add a third synchronized edit to both locations without eliminating the duplication, which increases future maintenance burden.

- The choice between Option A (prompt change) and Option B (script change) for the bug fix has different failure-mode characteristics; both are valid but the decision should be deliberate.
- The recommended-marker format choice (Q002) has latent machine-readability implications that should be considered now even if not acted on.
- No structural changes to `.aib_brain/` tool scripts are required unless Q001 selects Option B.
- Risk: If the seed strings in `initialize.py` and `aib-analysis.md` diverge post-implementation, the workspace behavior becomes inconsistent depending on which code path was used.

### Product Owner

All four items deliver clear developer experience improvements. The bug fix eliminates a confusing workspace state after every implement run. The scale labels reduce cognitive load for any developer not already familiar with the threshold scale. The recommended marker reduces decision friction on Q-blocks. The ambiguity detection instruction addresses a documented quality gap in the analysis output. The scope is well-bounded and the success criteria are measurable.

- Business value is moderate-to-high: reduces friction and error risk in a workflow that runs multiple times per workday.
- SC-01 through SC-06 are all verifiable; UAT scenarios are appropriate for the prompt-execution cases.
- No acceptance criteria gaps identified.
- Risk: Low. All changes are additive or corrective; no behavioral regressions expected.

### User

The bug fix is the most immediately impactful change: seeing an old request ID in `input.md ## Active request` after implement completes causes confusion — is the request still open? Did something go wrong? Eliminating this ambiguity is a clear win. The scale labels remove a lookup step that was previously required. The recommended marker on Q-blocks will make decisions faster — developers can simply accept the recommendation rather than weighing all options from scratch.

- The ambiguity-detection instruction is invisible to the user as a prompt change, but will produce higher-quality Q-blocks on future requests.
- The scale label format should be brief; `(all)` and `(mandatory only)` are appropriately concise.
- Risk: If the recommended marker is placed in a visually noisy or easily overlooked position, it may not be noticed. The inline suffix approach is harder to miss.

### Security Officer

This request involves no changes to authentication, authorization, data access controls, or sensitive data handling. All modifications are to prompt files, a Python script, and convention documents. No secrets or credentials are introduced or exposed.

- The `input.md` file is a local workspace file with no network exposure.
- Resetting `input.md` after implement actually reduces a mild information disclosure risk: a stale active-request reference could mislead a developer into acting on an already-closed request.
- No attack surface changes; no security recommendations.

### Data Governance Officer

All artifacts involved (`input.md`, prompt files, convention files, `initialize.py`) are classified as internal engineering documentation with no regulatory sensitivity. The `input.md` archive files created per request are retained locally in the request folder and committed to VCS — this behavior is unchanged by this request.

- No new data lineage paths are introduced.
- No personally identifiable information is involved.
- No compliance impact.
- The archival behavior of `input.md` (archived before reset) remains intact; this request does not alter when or how archives are created.

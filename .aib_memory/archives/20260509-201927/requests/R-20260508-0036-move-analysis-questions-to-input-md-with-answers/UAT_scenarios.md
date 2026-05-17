# UAT Scenarios — R-20260508-0036

## UAT-01 — Q&A round-trip in `input.md`

**Scenario:** Developer triggers `aib-analysis.md` with a new request that contains genuine implementation ambiguity. The analysis generates a `## Questions` section in `input.md` with one or more Q-blocks. The developer answers a question by marking a checkbox `[x]` and re-runs the analysis prompt.

**Pre-conditions:**
- Active request exists with ambiguous scope.
- `input.md` is at the seed state (no `## Questions` section).

**Steps:**
1. Observe `input.md` after analysis run — verify `## Questions` section is present with Q-blocks.
2. Each Q-block must show: question text, `> **Why this matters:** ...` explanation, checkbox options with one marked `*(recommended)*`, and an empty `> Answer:` line.
3. Developer selects one option (`[x]`) in a Q-block.
4. Developer re-runs `Execute .aib_brain/prompts/aib-analysis.md`.
5. Observe `request.md` — the relevant section (Goal/Scope/Constraints/etc.) must reflect the chosen option.
6. Observe `input.md` — the `## Questions` section must be absent; file reset to seed state with active request ID.

**Expected outcome:** Pass — all steps complete without error; `request.md` is correctly updated; `input.md` is clean.


## UAT-02 — Unanswered questions use recommended default

**Scenario:** Developer triggers analysis, receives `## Questions` in `input.md`, but makes no selection (leaves all checkboxes unchecked, `> Answer:` empty), and re-runs analysis.

**Pre-conditions:**
- Active request with Q-blocks in `input.md`, all unanswered.

**Steps:**
1. Re-run `Execute .aib_brain/prompts/aib-analysis.md` without selecting any option.
2. Observe `request.md` — sections updated as if the `*(recommended)*` option had been selected for each unanswered question.
3. Observe `input.md` — `## Questions` section absent; file reset to seed state.

**Expected outcome:** Pass — recommended options applied silently; no error raised; `input.md` clean.

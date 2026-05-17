# UAT Scenarios: R-20260508-1400 — Refactor menu: remove clutter, add state-aware guidance

## UAT-01 — Visual layout of the rendered menu with state-aware guidance block

**Type:** Manual visual inspection  
**Linked to:** Testing section in `analysis.md` (T1–T15 are automated; UAT-01 through UAT-03 cover visual layout fidelity)  
**Scope:** Verify the complete rendered menu looks correct in a real terminal session for each of the five guidance states.

**Preconditions:**
- AIB workspace initialized (`.aib_memory/` exists).
- Implementation of Tasks 1–3 complete.
- Terminal supports ANSI escape sequences (any modern terminal on Windows / macOS / Linux).

**Steps:**

1. **State: No task in progress**
   - Ensure `.aib_memory/input.md ## Input` section is empty (seed template only).
   - Ensure no Active request in `.aib_memory/requests_register.md`.
   - Launch the menu (`run.bat` or `run.sh`).
   - **Verify:** The guidance block displays below the "Active request: No active request" line and reads approximately: *"No task in progress. Add your description to .aib_memory/input.md, then run: Execute \`.aib_brain/prompts/aib-analysis.md\`"*
   - **Verify:** No "── AIB Prompts ──" block is visible.
   - **Verify:** No numbered "Refresh" item is present.
   - **Verify:** Action list contains "Reverse Engineer" but NOT "Move Request Artifacts".

2. **State: Input ready**
   - Write any non-empty, non-whitespace content into `input.md ## Input`.
   - Ensure no Active request.
   - Wait for the auto-refresh (≤ 3 seconds) or relaunch the menu.
   - **Verify:** Guidance text changes to approximately: *"Input ready. Execute analysis to create a request: Execute \`.aib_brain/prompts/aib-analysis.md\`"*

3. **State: Active request, no analysis**
   - Run `python .aib_brain/tools/create-request.py --workspace . --title "Test request"` to create a request without running analysis (so `request.md` is absent at `.aib_memory/request.md`).
   - **Verify:** Guidance text reads approximately: *"Request active — no analysis yet. Run: Execute \`.aib_brain/prompts/aib-analysis.md\`"*
   - **Verify:** "Close current request" action is visible.

4. **State: Active request, analysis done**
   - With the same active request, create a placeholder `request.md` at `.aib_memory/request.md` (or run `aib-analysis.md` to produce it).
   - **Verify:** Guidance text reads approximately: *"Request analysed and ready. Run: Execute \`.aib_brain/prompts/aib-implement.md\`"*

5. **State: Active request, questions pending**
   - With an active request and `request.md` present at `.aib_memory/request.md`, add a `## Questions` section to `.aib_memory/input.md` with at least one Q-block (e.g., `**Q001**: Should X or Y be used?`).
   - Wait for the auto-refresh (≤ 3 seconds).
   - **Verify:** Guidance text changes to two lines: line 1 references answering questions and re-running analysis; line 2 references running implement directly with recommended options applied.
   - **Verify:** The state switches back to the `active_with_analysis` two-line guidance after clearing the `## Questions` section from `input.md` and waiting for auto-refresh.

**Pass criteria:**
- Each of the five states displays the correct guidance text.
- The guidance text appears between the "Active request:" line and the numbered action list.
- Two-line guidance messages (states 2, 4, 5) are visually distinct and readable without line-wrapping on a standard 120-column terminal.

---

## UAT-02 — Two-line layout readability: `input_ready` state

**Type:** Manual visual inspection  
**Linked to:** SC-06, T6  
**Scope:** Verify the `input_ready` two-line guidance is readable and accurately describes both paths.

**Preconditions:** No active request; `input.md ## Input` has non-empty content.

**Steps:**
1. Launch the menu.
2. Observe the two-line guidance block.

**Pass criteria:**
- Line 1 references `aib-analysis.md` with wording about creating a request or running analysis.
- Line 2 references `aib-implement.md` with wording indicating analysis runs automatically (not "skip").
- Both lines are distinct and do not merge into a single long line.
- Neither line contains the word "skip" or "bypass".

---

## UAT-03 — Two-line layout readability: `active_with_questions` state

**Type:** Manual visual inspection  
**Linked to:** SC-12, T11, T12  
**Scope:** Verify the `active_with_questions` two-line guidance is readable and accurately describes both resolution paths.

**Preconditions:** Active request; `request.md` present; `input.md` contains non-empty `## Questions` section.

**Steps:**
1. Launch the menu.
2. Observe the two-line guidance block.

**Pass criteria:**
- Line 1 references `aib-analysis.md` with wording about pending questions and re-running analysis.
- Line 2 references `aib-implement.md` with wording that recommended options will be applied automatically.
- Both lines are distinct and clearly present two separate options.
- Neither line is truncated or wrapped on a standard 120-column terminal.
- No ANSI escape sequence artifacts (stray escape characters) are visible.
- The menu continues to auto-refresh every ~3 seconds without keypress.
- Terminal layout is clean: no overlapping lines, no residual content from previous renders.

**Fail criteria:**
- Wrong guidance text for a given state.
- Guidance block is absent from the rendered menu.
- Stray "── AIB Prompts ──" or "Refresh" items visible.
- `Move Request Artifacts` action visible in the menu.
- ANSI escape artifacts visible in the terminal.

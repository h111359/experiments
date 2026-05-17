# UAT Scenarios: R-20260510-2056 — Restructure analysis prompt and output format

## UAT-01 — Full analysis run produces correct section structure

**Description:** Run `aib-analysis.md` on a new active request after the implementation is complete. Verify that the generated `analysis-<request_id>.md` contains the new section structure.

**Pre-conditions:**
- Implementation of R-20260510-2056 is complete.
- A new request exists in Active state.
- `input.md` has non-empty content in `## Input`.

**Steps:**
1. Execute `aib-analysis.md` in the AI coding interface.
2. Open the generated `analysis-<request_id>.md`.
3. Verify the section structure matches the new convention.

**Expected outcomes:**
- The analysis file does NOT contain sections: "Domain Knowledge Essentials", "Technical Knowledge & Terms", "Testing", "Multi-Perspective Stakeholder Review".
- The analysis file DOES contain sections: "Best Practices", "Implementation Alternatives".
- The "Executive Summary" section contains only Request ID, Title, and Purpose.
- "Files read during this analysis run" appears as a heading (not a plain bullet in a section body).
- "Research Results" section does not contain an "Evidence log" sub-section.
- All headings use markdown heading syntax (`##`, `###`) instead of bold labels (`**...**`).
- Empty lines are present between items for readability.

## UAT-02 — Q-blocks derived from Implementation Alternatives

**Description:** Verify that the analysis generates Q-blocks corresponding to the identified implementation alternatives.

**Pre-conditions:** Same as UAT-01, but the request has at least two materially different implementation approaches.

**Steps:**
1. Execute `aib-analysis.md`.
2. Open `input.md`.
3. Verify `## Questions` section is present and contains Q-blocks.
4. Verify each Q-block maps to an alternative listed in the "Implementation Alternatives" section of the analysis.

**Expected outcomes:**
- Every alternative in "Implementation Alternatives" with a materially different outcome has a corresponding Q-block in `input.md ## Questions`.
- No Q-block refers to an alternative not listed in "Implementation Alternatives".

## UAT-03 — Minimum-questions option visible in input.md

**Description:** After a fresh initialization or request close, verify the minimum-questions option appears in `input.md`.

**Steps:**
1. Run `initialize.py` or `close-request.py` on a workspace.
2. Open `.aib_memory/input.md`.
3. Verify the minimum-questions option is present in `## Options`.

**Expected outcomes:**
- `## Options` section contains a minimum-questions option with a default value of 0.
- The option is clearly labeled so a developer understands it controls the floor for Q-block generation.

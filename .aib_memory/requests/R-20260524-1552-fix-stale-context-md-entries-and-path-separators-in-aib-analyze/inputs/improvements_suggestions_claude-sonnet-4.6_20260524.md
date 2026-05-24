# Consistency Analysis

## Timestamp

2026-05-24 (local time, Europe/Sofia)

## Scope

Entire workspace, including:

- `.aib_brain/` — prompts, conventions, tool scripts, README, version marker, user guide
- `.aib_memory/` — context.md, input.md, instructions.md, requests_register.md
- `docs/` — Development_and_Deployment_Specification.md, Analyze_AIB.prompt.md
- `logs/` — next_version_changes.md, per-version log files
- `tests/` — all test files
- `scripts/` — release_bookkeeping.py
- `README.md` (root)
- `.github/workflows/aib-semver-patch-bump-and-log.yml`
- `versions/` — archived zip files (binary; content not inspected)
- `recordings/` — WebM video files (binary; content not inspected)

## Coverage & Gaps

| Folder / File | Files Discovered | Readable | Notes |
| --- | --- | --- | --- |
| `.aib_brain/prompts/` | 3 | 3 | aib-analyze.md, aib-implement.md, aib-refresh-context.md |
| `.aib_brain/conventions/` | 20 | 20 | All convention files read |
| `.aib_brain/tools/` | 6 | 5 | close-request.py, finalize-input.py, initialize.py, create-request.py, move-request-artifacts.py, common.py |
| `.aib_brain/` root | 4 | 2 | README.md, user_guide.html (HTML not fully parsed), v1.3.4 (empty marker), run.bat/run.sh |
| `.aib_memory/` root | 5 | 5 | context.md, input.md, instructions.md, requests_register.md, v1.3.4 |
| `.aib_memory/requests/` | 42 request folders | Sampled | Individual request artifacts not read (GC-04 equivalent; closed) |
| `.aib_memory/attachments/` | 1 | 1 | .gitkeep only |
| `docs/` | 2 | 2 | Both files read |
| `logs/` | Multiple | 2 | next_version_changes.md and one version log read; others not read (repeating pattern) |
| `tests/` | 19 | 8 | conftest.py + 7 test files deeply read; remainder scanned for structure |
| `scripts/` | 1 | 1 | release_bookkeeping.py (structure scanned) |
| `README.md` | 1 | 1 | Root README read |
| `.github/workflows/` | 1 | 1 | CI workflow file read |
| `versions/` | 26 | 0 | Binary zip archives; not inspected |
| `recordings/` | 8 | 0 | Binary WebM files; not inspected |

**Gaps:** Coding convention files (coding-python-convention.md, coding-csharp-convention.md, etc.) were not deeply read, as they are not relevant to the primary consistency audit of the AIB framework itself. Individual closed-request artifacts were not read per the scope boundary.

---

## Findings (Prioritized)

---

### F-001

**Severity:** High

**Title:** GC-06 referenced in failure table but never defined

**Evidence:**

- `.aib_brain/prompts/aib-analyze.md`, line 69 (Failure Handling table):
  > `Any write attempted to a file outside .aib_memory not covered by GC-06 exceptions`

- `.aib_brain/prompts/aib-analyze.md`, Section 3.1 (Global Constraints): only GC-01 through GC-05 are defined. GC-06 is absent.

**Why it matters:** The failure handling table instructs the agent to allow writes "not covered by GC-06 exceptions," but GC-06 does not exist. An agent reading this will fail to locate the referenced constraint, creating ambiguity about which writes are permitted. The actual exceptions are defined in GC-05 (the `No implementation writes` constraint), making this a wrong GC reference.

**Recommendation:** In the Failure Handling table row, replace `GC-06 exceptions` with `GC-05 exceptions`. No other changes required.

**Risk/Tradeoffs:** Low risk; straightforward label correction. Regression test `test_gc06_no_closed_request_reads_present` in `tests/test_analysis_prompt_structure.py` searches only for the string `"GC-06"` (which still appears in the table row), so the test continues to pass without changes. However, the test description is also misleading — see F-008.

---

### F-002

**Severity:** High

**Title:** GC-05 contains two stale cross-references: non-existent Appendix A step A.5 and non-existent section 5.6.2

**Evidence:**

- `.aib_brain/prompts/aib-analyze.md`, line 57 (GC-05):
  > `except for the tool script invocations explicitly authorized in **Appendix A — Auto-Request Creation Branch** (steps A.3 and A.5) and 5.6.2`

- Appendix A in the same file defines only steps A.1, A.2, A.3, and A.4. Step A.5 does not exist.

- Section 5.6.2 does not exist in the current document structure; that numbering referred to the old sub-section layout where Archive Input and Reset was section 5.6. The current document uses step identifiers S07.1, S07.2, etc.

**Why it matters:** GC-05 is a safety constraint that limits unauthorized file writes. Citing non-existent steps makes the exception boundary undefined. An agent trying to verify whether a tool invocation is authorized cannot follow the reference.

**Recommendation:**

- Remove "`(steps A.3 and A.5)`" and replace with "`(steps A.3 and A.4)`" if A.4 is the intended invocation, OR add a missing step A.5 to Appendix A if another tool invocation is authorized there.
- Remove "`and 5.6.2`" from GC-05, as this section no longer exists. If a specific step in S07 is meant (e.g., the finalize-input.py invocation), replace with "`and S07.1`".

**Risk/Tradeoffs:** Medium effort; requires determining whether a step A.5 was intentionally omitted or is a genuine missing step. Changing GC-05 wording may require a test update if any test asserts the exact GC-05 text.

---

### F-003

**Severity:** High

**Title:** context.md step order for analysis workflow contradicts aib-analyze.md

**Evidence:**

- `.aib_memory/context.md`, line 27 (Domain Knowledge, Analysis workflow structure bullet):
  > `(5) Generate Analysis, (6) Archive Input and Reset, (7) Quality Check, (8) Q-block Generation`

- `.aib_brain/prompts/aib-analyze.md`, Execution Model Summary:
  > `6. **Quality Check** … 7. **Archive Input and Reset** …`

- `.aib_brain/prompts/aib-analyze.md`, actual steps: S06 = Quality Check; S07 = Archive Input and Reset.

**Why it matters:** context.md is the shared product memory read by every AIB prompt. An agent or human reading context.md will believe Archive runs before Quality Check, but the actual prompt executes Quality Check first. This is not a trivial ordering difference — running Quality Check before Archive ensures the gate evaluation is included in the analysis document before it is archived. Swapping the order in context.md leads to an incorrect mental model of the workflow.

**Recommendation:** In `.aib_memory/context.md`, update the step-number descriptions in the "Analysis workflow structure" bullet to read:
> `(5) Generate Analysis, (6) Quality Check, (7) Archive Input and Reset, (8) Q-block Generation, (9) Plan Generation, (10) Completion Confirmation`

Note: context.md is auto-generated by `aib-refresh-context.md`. The root fix is to ensure the next execution of `aib-refresh-context.md` picks up the correct order from the source file. No direct manual fix of context.md is strictly necessary, but an immediate correction prevents misleading agents that read context.md before the next refresh.

**Risk/Tradeoffs:** Low risk. The context.md is fully replaced on refresh; the correction will persist only until the next refresh run unless `aib-refresh-context.md` synthesizes incorrectly again.

---

### F-004

**Severity:** High

**Title:** context.md states "GC-03 was removed" but GC-03 exists in aib-analyze.md

**Evidence:**

- `.aib_memory/context.md`, line 27:
  > `The prompt includes an ## Execution Model Summary chapter, a ## Global Constraints section (GC-01, GC-02, GC-04 through GC-07; GC-03 was removed)`

- `.aib_brain/prompts/aib-analyze.md`, line 53:
  > `- **GC-03 — No partial writes on halt:** When execution halts due to any error condition, MUST NOT write any output files.`

**Why it matters:** context.md explicitly tells readers (and AI agents) that GC-03 does not exist. An agent reading context.md for orientation and then scanning aib-analyze.md for global constraints will receive contradictory information. The intended removal was of the old GC-03 ("Q-blocks first cycle only"), which was replaced by the current GC-03 ("No partial writes on halt"). context.md was not updated to reflect the reassignment.

**Recommendation:** Update the "Analysis workflow structure" bullet in `.aib_memory/context.md` to read:
> `a ## Global Constraints section (GC-01 through GC-05)`

Remove the claim "GC-03 was removed" and the reference to GC-06 and GC-07, neither of which currently exist.

**Risk/Tradeoffs:** Low risk. context.md is auto-generated; the fix should be applied at the next `aib-refresh-context.md` run and also verified that the source prompt synthesizes accurately.

---

### F-005

**Severity:** High

**Title:** context.md claims GC-04 through GC-07 exist, but only GC-04 and GC-05 are defined

**Evidence:**

- `.aib_memory/context.md`, line 27:
  > `(GC-01, GC-02, GC-04 through GC-07; GC-03 was removed)`

- `.aib_brain/prompts/aib-analyze.md`, Section 3.1: only GC-01 through GC-05 are defined. GC-06 and GC-07 are absent.

**Why it matters:** An agent reading context.md will believe GC-06 and GC-07 are valid constraint identifiers it should look up. Finding only GC-05 defined creates confusion and undermines trust in the documentation.

**Recommendation:** Update context.md to reflect only the constraints that actually exist: GC-01 through GC-05. Remove the "GC-04 through GC-07" range claim and "GC-03 was removed" claim together (overlap with F-004).

**Risk/Tradeoffs:** Same as F-004 — low risk, auto-generated file.

---

### F-006

**Severity:** High

**Title:** aib-implement.md Rules section names wrong completion phrase

**Evidence:**

- `.aib_brain/prompts/aib-implement.md`, Step 14:
  > `MUST confirm at the very end of the conversation with the text "--- I am done with the implementation  of \`<request_id>\` ---"`

- `.aib_brain/prompts/aib-implement.md`, Rules section (line 50):
  > `Do not add additional text after "--- I am done with the analysis of \`<request_id>\` ---" line.`

**Why it matters:** Step 14 defines the correct message (implementation), but the accompanying rule quotes the wrong message (analysis). An agent following the Rules section literally would emit the analyze-phase phrase at the end of an implement run, making it impossible to detect which prompt completed. Also contains the typo "somenting" instead of "something" in the same line.

**Recommendation:**

- In the Rules section of `.aib_brain/prompts/aib-implement.md`, replace:
  > `"--- I am done with the analysis of \`<request_id>\` ---"`
  with:
  > `"--- I am done with the implementation of \`<request_id>\` ---"`

- Fix typo: replace `somenting` with `something`.

- Fix double space in Step 14: `"--- I am done with the implementation  of"` → `"--- I am done with the implementation of"` (remove extra space).

**Risk/Tradeoffs:** Low risk. The Rules section is referenced by the agent during execution; fixing it brings it into alignment with Step 14 and prevents prompt confusion.

---

### F-007

**Severity:** Medium

**Title:** context.md references stale "section 5.6" sub-section structure (5.6.1, 5.6.2, 5.6.3)

**Evidence:**

- `.aib_memory/context.md`, line 29:
  > `Step 6 (Archive Input and Reset, section 5.6) is split into three sub-sections: 5.6.1 Eligibility Check, 5.6.2 Finalize Script Invocation, and 5.6.3 Post-conditions.`

- `.aib_brain/prompts/aib-analyze.md`, current structure: Archive Input and Reset is now S07 (a top-level step), with sub-steps S07.1 and S07.2 only. No 5.6 section hierarchy exists. The Eligibility Check and Post-conditions sub-steps are absent.

**Why it matters:** context.md directs agents to look for sub-sections (5.6.1, 5.6.2, 5.6.3) that do not exist. An agent parsing this will spend time searching for non-existent structure.

**Recommendation:** Update context.md to describe step S07 accurately:
> `Step 7 (Archive Input and Reset, S07) invokes finalize-input.py (S07.1) and emits a step-completion note (S07.2).`

Remove all references to section 5.6 numbering.

**Risk/Tradeoffs:** Low risk. Auto-generated file; fix by correcting `aib-refresh-context.md`'s synthesis.

---

### F-008

**Severity:** Medium

**Title:** Test `test_gc06_no_closed_request_reads_present` has wrong description — it asserts GC-06 but GC-06 is not "no-closed-request-reads"

**Evidence:**

- `tests/test_analysis_prompt_structure.py`, line 177:
  > `"""GC-06 no-closed-request-reads constraint must be present in aib-analyze.md."""`

- `tests/test_analysis_prompt_structure.py`, line 179–182:
  ```python
  assert "GC-06" in content, (
      "aib-analyze.md must contain 'GC-06' in the Global Constraints section — "
      "this constraint prohibits reading files inside Closed request subfolders."
  )
  ```

- `.aib_brain/prompts/aib-analyze.md`, actual GC-04 (not GC-06) is the "No closed-request reads" constraint.

**Why it matters:** The test passes (because "GC-06" appears in the failure table row) but is validating the wrong thing. The description says it protects the "no-closed-request-reads" constraint, which is GC-04, not GC-06. If GC-04 were accidentally renamed or removed, this test would not catch it. The test provides false assurance.

**Recommendation:**

- Change the test method name and docstring to reference GC-04:
  ```python
  def test_gc04_no_closed_request_reads_present(self) -> None:
      """GC-04 no-closed-request-reads constraint must be present in aib-analyze.md."""
      ...
      assert "GC-04" in content, (
          "aib-analyze.md must contain 'GC-04' in the Global Constraints section — "
          "this constraint prohibits reading files inside Closed request subfolders."
      )
  ```

- Add a separate test for GC-05 if desired.

**Risk/Tradeoffs:** Low risk. Rename + content fix. The GC-06 string still appears in the failure table, so the renamed test for GC-04 will correctly assert GC-04 presence.

---

### F-009

**Severity:** Medium

**Title:** aib-analyze.md uses backslash path separators inconsistently alongside forward slashes

**Evidence:**

- `.aib_brain/prompts/aib-analyze.md`, line 187 (S05.2):
  > `.aib_memory\input.md`, `.aib_memory\attachments`, `.aib_memory\context.md`

- Same line: `.aib_memory/analysis-<request_id>.md` (forward slash)

- Line 225 (S08.2):
  > `.aib_brain\conventions\q-block-convention.md`

- Line 235 (S09.1):
  > `.aib_memory\context.md`, `.aib_brain\conventions\plan-convention.md`, but `.aib_memory/plan-<request_id>.md` (forward slash)

- `logs/next_version_changes.md` change bullet: `Replace backslash path separators with forward slashes in instructions.md.` — indicating the convention is forward slashes.

**Why it matters:** Mixed path separators inside a single step create confusion. On non-Windows agents, backslash paths may fail if passed to shell commands. Since AIB is cross-platform (run.sh for Linux/macOS), all paths in prompts should use forward slashes.

**Recommendation:** In `.aib_brain/prompts/aib-analyze.md`, replace all backslash path separators with forward slashes in S05.2, S08.2, and S09.1:

- `'.aib_memory\input.md'` → `'.aib_memory/input.md'`
- `'.aib_memory\attachments'` → `'.aib_memory/attachments'`
- `'.aib_memory\context.md'` → `'.aib_memory/context.md'`
- `'.aib_brain\conventions\q-block-convention.md'` → `'.aib_brain/conventions/q-block-convention.md'`
- `'.aib_brain\conventions\plan-convention.md'` → `'.aib_brain/conventions/plan-convention.md'`

**Risk/Tradeoffs:** Low risk. Text replacements. No test currently asserts these paths.

---

### F-010

**Severity:** Medium

**Title:** Two typos in aib-analyze.md: "Qurestions" in S05.2 and "and and" in S09.1

**Evidence:**

- `.aib_brain/prompts/aib-analyze.md`, line 187 (S05.2):
  > `(Input or Qurestions sections)`

- `.aib_brain/prompts/aib-analyze.md`, line 235 (S09.1):
  > `based on .aib_memory/analysis-<request_id>.md and and project memory`

**Why it matters:** Typos in prompt instructions can cause agents to miss the intended meaning or produce unexpected behavior.

**Recommendation:**

- Fix `Qurestions` → `Questions` in S05.2.
- Fix `and and` → `and` in S09.1.

**Risk/Tradeoffs:** Trivial fix. No test asserts these specific strings.

---

### F-011

**Severity:** Medium

**Title:** context.md references stale "## 7. Completion Confirmation" section heading in Appendix A location description

**Evidence:**

- `.aib_memory/context.md`, line 27:
  > `The Auto-Request Creation Branch is defined in **Appendix A** (after \`## 7. Completion Confirmation\`)`

- `.aib_brain/prompts/aib-analyze.md`: the current structure does not have a heading `## 7. Completion Confirmation`. Completion Confirmation is now step S10 within Section 5 (Execution Procedure). Appendix A appears after the entire `## 5. Execution Procedure` section.

**Why it matters:** An agent searching for Appendix A by locating "## 7. Completion Confirmation" will not find it, because that heading doesn't exist. This makes the context.md location hint actively misleading.

**Recommendation:** Update context.md to accurately describe Appendix A's location:
> `The Auto-Request Creation Branch is defined in **Appendix A** (after the Execution Procedure section S10)`

**Risk/Tradeoffs:** Low risk. Auto-generated; fix at next refresh.

---

### F-012

**Severity:** Medium

**Title:** context.md preamble timestamp format violates context-convention.md

**Evidence:**

- `.aib_memory/context.md`, preamble (line 2):
  > `> **Auto-generated** by \`aib-refresh-context.md\` on 2026-05-23 local time.`

- `.aib_brain/conventions/context-convention.md`, Preamble Format (normative):
  > `> **Auto-generated** by \`aib-refresh-context.md\` on <YYYY-MM-DD HH:MM timezone>.`

**Why it matters:** The convention requires `HH:MM timezone` (e.g., `2026-05-23 14:35 UTC+3`). The actual file omits the time and uses "local time" as the timezone identifier, which is non-deterministic and un-parseable by tooling.

**Recommendation:** When `aib-refresh-context.md` generates the preamble, insert the full timestamp including hours, minutes, and the timezone offset (e.g., `UTC+3` or `EET`). Alternatively, update the preamble format in context-convention.md if the simpler date-only format is intentional; but the current convention text is unambiguous.

**Risk/Tradeoffs:** Low risk; the timestamp is cosmetic. However, if tooling later parses this timestamp for versioning or diffing purposes, the incomplete format will cause failures.

---

### F-013

**Severity:** Medium

**Title:** context.md Requirements section missing MoSCoW classification, which is mandatory per context-convention.md

**Evidence:**

- `.aib_brain/conventions/context-convention.md`, Section 5 (Requirements), MUST include:
  > `Known requirement priorities or MoSCoW classification for the top capabilities.`

- `.aib_memory/context.md`, Requirements section: lists FR-001 through FR-009 and NFR-001 through NFR-002 with no MoSCoW or priority labels.

**Why it matters:** MoSCoW classification is a mandatory element per the convention. Its absence means developers cannot quickly identify which requirements are critical vs. optional, leading to implementation decisions without proper priority context.

**Recommendation:** Add MoSCoW labels (Must Have / Should Have / Could Have / Won't Have) to each requirement in context.md's Requirements section, or add a sentence above the list indicating that all listed requirements are classified as Must Have. Update `aib-refresh-context.md` synthesis logic to include this classification.

**Risk/Tradeoffs:** Medium effort for the synthesis prompt. Adding labels to all FR/NFR items in context.md is straightforward since all requirements are currently active must-haves.

---

### F-014

**Severity:** Medium

**Title:** ADR-003 in context.md is stale — describes Q-block rules as co-located with output specs in aib-analyze.md section 6.3, but they are now in q-block-convention.md

**Evidence:**

- `.aib_memory/context.md`, Architecture & Decisions, ADR-003:
  > `ADR-003: Co-locate Q-block generation rules with output specifications (section 6.3 of \`aib-analyze.md\`) to reduce navigation distance between generation instructions and classification rules.`

- `logs/next_version_changes.md` records:
  > `Extract Q-block format templates and format-level rules from aib-analyze.md section 6.3 into new .aib_brain/conventions/q-block-convention.md.`
  > `Update aib-analyze.md section 6.3 to reference q-block-convention.md for format specification.`

- `.aib_brain/prompts/aib-analyze.md`, S08.2: references `.aib_brain/conventions/q-block-convention.md` as the authoritative source.

**Why it matters:** ADR-003 records the opposite of what is now true. The Q-block format rules were deliberately extracted to a separate convention file. Any developer reading ADR-003 will look in aib-analyze.md section 6.3 for format rules that are now in q-block-convention.md.

**Recommendation:** Update ADR-003 in context.md to reflect the current architecture:
> `ADR-003: Q-block format templates and format-level rules are defined in \`.aib_brain/conventions/q-block-convention.md\` (authoritative source); \`aib-analyze.md\` section 6.3 references that convention for format specification and retains format selection guidance.`

**Risk/Tradeoffs:** Low risk. ADR updates in context.md are auto-generated; fix at next refresh.

---

### F-015

**Severity:** Medium

**Title:** Development_and_Deployment_Specification.md branch naming convention not followed by the current active branch

**Evidence:**

- `docs/Development_and_Deployment_Specification.md`, Section 5 (Git and GitHub Workflow):
  > `Branches MUST be organized by issue and named using issue number (example: \`issue/123\`).`
  > `Do not use \`feature/\`, \`fix/\`, or \`breaking/\` prefixes.`

- Repository attachment (workspace context): current branch is `111-analysis-content-duplication`.

**Why it matters:** The spec mandates `issue/123` format, but the current active branch uses `111-<slug>` format (no `issue/` prefix). This is a direct spec violation visible in the active working branch.

**Recommendation:** Either rename the current branch to `issue/111` to comply with the spec, or update the spec to allow `<issue-number>-<slug>` as an alternative format if that is the intended convention. The spec must match actual practice to be credible.

**Risk/Tradeoffs:** Branch rename mid-work has moderate risk (requires updating PR references). Alternatively, updating the spec document is low risk but requires a decision on the canonical format.

---

### F-016

**Severity:** Low

**Title:** instructions.md exception for `.aib_brain/README.md` is communicated only via instructions.md, not in aib-implement.md safety rules

**Evidence:**

- `.aib_memory/instructions.md`, README maintenance section:
  > `Modification of \`.aib_brain/README.md\` is allowed exception from the rule no \`.aib_brain\` files to be changed.`

- `.aib_brain/prompts/aib-implement.md`, Safety requirements:
  > `Do not modify \`.aib_brain/\` assets during implementation work.`

**Why it matters:** The safety rule in aib-implement.md is absolute. The exception is only discoverable through instructions.md (which is read first). A developer reading only aib-implement.md would believe `.aib_brain/README.md` is immutable. The exception is technically correct (instructions.md is always read first), but the asymmetry between the hard rule in the prompt and the exception in instructions.md creates confusion and is fragile — if instructions.md is cleared during re-initialization, the exception disappears silently.

**Recommendation:** Add a parenthetical note to the safety rule in `aib-implement.md`:
> `Do not modify \`.aib_brain/\` assets during implementation work (except \`.aib_brain/README.md\` when the active request explicitly requires it, per instructions.md).`

**Risk/Tradeoffs:** Low risk. Makes an existing implicit exception explicit. The exception is still governed by instructions.md content.

---

### F-017

**Severity:** Low

**Title:** context.md Domain Knowledge bullet on "Analysis workflow structure" is a single very long run-on bullet violating Rule 16 of context-convention.md

**Evidence:**

- `.aib_memory/context.md`, line 27: a single bullet (`- **Analysis workflow structure**:`) that spans over 250 words across multiple complex sentences.

- `.aib_brain/conventions/context-convention.md`, Formatting Rule 16:
  > `Each bullet or list item MUST NOT exceed two sentences. If the content of an entry requires more than two sentences to express, it MUST be split into two or more separate bullet items.`

**Why it matters:** The rule exists to keep context.md readable for AI agents consuming it under token constraints. Long bullets are harder to parse and may be truncated in limited-context situations.

**Recommendation:** Split the "Analysis workflow structure" bullet into multiple sub-bullets, each covering one aspect (step sequence, GC constraints, Appendix A, Answer Application Sub-flow, step-completion notes, State transitions). This also applies to the "Analysis Q-block rules" bullet and the "Analysis Decision Points requirement" bullet, which are similarly long.

**Risk/Tradeoffs:** Medium effort for the synthesis prompt. Low risk to overall correctness.

---

### F-018

**Severity:** Nit

**Title:** aib-analyze.md Execution Model Summary lists Quality Check at step 6 and Archive at step 7 but the summary text describes them in old order

**Evidence:**

- `.aib_brain/prompts/aib-analyze.md`, Execution Model Summary:
  ```
  6. **Quality Check** — Evaluate every checklist item...
  7. **Archive Input and Reset** — Invoke finalize-input.py...
  ```

This is consistent with the actual steps S06 and S07. This is NOT an error in the prompt itself — the Execution Model Summary is correct. The error is only in context.md (already covered by F-003). No action required on aib-analyze.md for this finding.

---

### F-019

**Severity:** Nit

**Title:** aib-implement.md "Must not read the Analysis" rule uses inconsistent capitalisation

**Evidence:**

- `.aib_brain/prompts/aib-implement.md`, Rules / Execution requirements, line 56:
  > `- Must not read the Analysis`

- All other rules in the same section use `MUST NOT` (uppercase normative language per RFC 2119 / BCP 14).

**Why it matters:** Inconsistent capitalisation of normative keywords makes the rule appear non-normative, potentially causing it to be treated as advisory rather than mandatory.

**Recommendation:** Change to `MUST NOT read the Analysis document (analysis-<request_id>.md).`

**Risk/Tradeoffs:** Trivial.

---

## Cross-Reference Check Summary

### Broken references

| Reference | Location | Issue |
| --- | --- | --- |
| `GC-06 exceptions` | `.aib_brain/prompts/aib-analyze.md`, Failure Handling table | GC-06 is not defined; should be GC-05 |
| `(steps A.3 and A.5)` | `.aib_brain/prompts/aib-analyze.md`, GC-05 | Step A.5 does not exist in Appendix A |
| `and 5.6.2` | `.aib_brain/prompts/aib-analyze.md`, GC-05 | Section 5.6.2 does not exist; the archive step is now S07.1 |
| `## 7. Completion Confirmation` | `.aib_memory/context.md` | That heading no longer exists; completion is now step S10 within Section 5 |
| `section 5.6` (with 5.6.1, 5.6.2, 5.6.3) | `.aib_memory/context.md` | That section structure was removed; current step is S07 with sub-steps |
| `GC-03 was removed` | `.aib_memory/context.md` | GC-03 exists in the current file as "No partial writes on halt" |
| `GC-04 through GC-07` | `.aib_memory/context.md` | GC-06 and GC-07 are not defined; only GC-01 through GC-05 exist |

### Suspicious references (may be correct but should be verified)

| Reference | Location | Note |
| --- | --- | --- |
| `analysis-convention.md section 3` | `.aib_memory/context.md`, "Answer Application Sub-flow" bullet | Verify that section 3 of analysis-convention.md is still titled "File Naming, Location & Write Behavior (Normative)" — it was as of last read |
| `aib-analyze.md section 6.3` | `.aib_memory/context.md`, "Analysis Q-block rules" bullet | Verify section 6.3 still exists with that title in the current aib-analyze.md |
| `section 5.6.1 Eligibility Check` | `.aib_memory/context.md` | This sub-step does not exist in the current file; the archive step is S07 without an eligibility check sub-step |

---

## Redundancy & Source-of-Truth Map

### Key concept ownership

| Concept | Authoritative source | Secondary sources (potential redundancy) |
| --- | --- | --- |
| Q-block format templates | `.aib_brain/conventions/q-block-convention.md` | `aib-analyze.md` S08 (references convention correctly); `.aib_brain/README.md` (summary reference); `context.md` (summary reference) |
| Analysis document structure | `.aib_brain/conventions/analysis-convention.md` | `context.md` (summary) |
| Plan document structure | `.aib_brain/conventions/plan-convention.md` | `context.md` (summary) |
| context.md structure | `.aib_brain/conventions/context-convention.md` | `aib-refresh-context.md` (references convention correctly) |
| GC constraint definitions | `.aib_brain/prompts/aib-analyze.md` | `context.md` (summary — currently stale, see F-003 through F-005) |
| Analysis step order | `.aib_brain/prompts/aib-analyze.md` | `context.md` (summary — currently incorrect, see F-003) |
| Branch naming convention | `docs/Development_and_Deployment_Specification.md` | `context.md` Development Practices (general description) |
| SemVer versioning rules | `docs/Development_and_Deployment_Specification.md` | `context.md` Operations section |
| Implementation completion phrase | `.aib_brain/prompts/aib-implement.md` Step 14 | Rules section of same file (currently contradictory, see F-006) |

### Conflicts between sources

- `context.md` vs `aib-analyze.md`: step order (F-003), GC-03 existence (F-004), GC numbering (F-005), section 5.6 structure (F-007), Appendix A location (F-011), ADR-003 (F-014).
- `aib-implement.md` Step 14 vs its own Rules section: completion phrase (F-006).
- `aib-analyze.md` GC-05 vs Appendix A: step A.5 not defined (F-002).
- `test_analysis_prompt_structure.py` test description vs aib-analyze.md GC numbering: GC-06 described as "no-closed-request-reads" but that is GC-04 (F-008).

---

## Suggested Next Actions

- [ ] **Fix GC-06 reference in failure table** (F-001): In aib-analyze.md Failure Handling, replace `GC-06 exceptions` with `GC-05 exceptions`.
- [ ] **Resolve GC-05 stale cross-references** (F-002): Remove or correct references to Appendix A step A.5 and section 5.6.2.
- [ ] **Fix aib-implement.md completion phrase and typos** (F-006): Correct the Rules section phrase from "analysis" to "implementation"; fix "somenting" → "something"; remove double space.
- [ ] **Fix backslash path separators in aib-analyze.md** (F-009): Replace all backslash separators with forward slashes in S05.2, S08.2, S09.1.
- [ ] **Fix typos in aib-analyze.md** (F-010): Fix "Qurestions" → "Questions" in S05.2; fix "and and" → "and" in S09.1.
- [ ] **Refresh context.md** via `aib-refresh-context.md`: This will address F-003, F-004, F-005, F-007, F-011, F-012, F-013, F-014, F-017 in one run, provided the synthesis correctly reads the current aib-analyze.md structure.
- [ ] **Fix test description in test_analysis_prompt_structure.py** (F-008): Rename `test_gc06_no_closed_request_reads_present` to reference GC-04 and assert the correct GC identifier.
- [ ] **Resolve branch naming** (F-015): Decide on the canonical branch naming format (issue/NNN vs NNN-slug) and update either the spec or the branch.
- [ ] **Improve instructions.md exception visibility** (F-016): Add a parenthetical note to aib-implement.md Safety requirements.
- [ ] **Update ADR-003 in context.md** (F-014): Reflect q-block-convention.md as the authoritative Q-block format source (resolved at next context refresh).

---

## Ideas for Improvement Beyond Fixing Issues

### New functionality

- **Status dashboard command**: Add a `show-status` tool script that outputs a human-readable summary of the active request state, pending Q-blocks, and last context refresh date. This would reduce the need to open multiple files to understand workspace state.

- **Validate-workspace command**: A `validate.py` tool script that checks all cross-references (GC identifiers, Appendix A step numbers, section numbers) in prompts and context.md against actual file content, outputting a report of stale references. This would prevent the class of issues found in F-001, F-002, and F-007.

- **Changelog diff preview**: Before `aib-implement.md` appends to `logs/next_version_changes.md`, emit a preview of what will be written so the developer can review before committing.

### Developer experience improvements

- **context.md staleness indicator**: Add a mechanism (e.g., a timestamp comparison in `menu.py`) to warn the developer when context.md was last generated more than N days ago, prompting a refresh before running analysis.

- **Prompt linting step in CI**: Add a CI step that runs a simple linter on `.aib_brain/prompts/*.md` to check for common errors: undefined GC references, backslash path separators, and duplicate words. This would catch F-001, F-002, F-009, and F-010 automatically.

- **Clearer Q-block halting behavior**: Add a visual separator or status line in `input.md` when questions are present, so developers immediately see the Q&A state without reading the whole file. Currently, the `State: questions_generated` line conveys this, but it requires knowing to look for it.

### Robustness and safety improvements

- **Step A.5 in Appendix A**: Formally define what step A.5 of the Auto-Request Creation Branch should be (likely "Resume at Step 2" or similar), resolving F-002 and making GC-05 exceptions complete.

- **GC constraint numbering stability**: Adopt a policy of never reusing a removed GC identifier. When GC-03 was removed, the next new constraint should have been GC-06, not GC-03. This prevents the confusion documented in F-004. Document this policy in the AIB framework conventions.

- **Convention cross-reference registry**: Maintain a simple table in a shared conventions index listing every named identifier (GC-NN, FR-NNN, ADR-NNN) with a canonical location. This would make broken cross-references (F-001, F-002, F-005) immediately visible.

### Documentation quality improvements

- **context-convention.md completeness test**: Add a test in the test suite that reads context.md and validates each of the 12 mandatory sections is present and non-empty (or contains the stub notice). Currently only formatting rules are tested.

- **context.md preamble timestamp test**: Add a test that asserts the preamble timestamp in context.md matches the required format `YYYY-MM-DD HH:MM timezone` (F-012).

- **analysis-convention.md "implement MUST NOT read" enforcement test**: Add a test that reads aib-implement.md and asserts it does not reference any analysis artifact file path pattern, reinforcing the separation of concerns.

### Maintainability improvements

- **Separate context.md synthesis from aib-refresh-context.md prompt logic**: The current synthesis approach relies on the AI agent correctly summarizing the aib-analyze.md step structure. Given the frequency of stale context.md entries found in this audit, consider maintaining a small machine-readable metadata file (e.g., `.aib_brain/metadata.json`) with structured entries (step order, GC list, appendix names) that `aib-refresh-context.md` reads directly rather than inferring from free text.

- **Prompts version annotation**: Add a comment block at the top of each prompt file noting the last significant structural change (e.g., `<!-- Last restructured: R-20260521-1709 -->`). This makes it easier to correlate context.md stale entries with the request that introduced the structural change.

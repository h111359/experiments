# UAT Scenarios — R-20260430-1550

## UAT-01: Attachment file acknowledgement in analysis output

**Scenario:** Verify that when the developer places a text file in `.aib_memory/attachments/` before running `aib-analysis.md`, the AI agent reads and acknowledges the file's content as part of the analysis input.

**Preconditions:**
- `.aib_memory/attachments/` exists and is empty.
- A text file (e.g., `sample-spec.txt`) is placed in `.aib_memory/attachments/`.
- `input.md` contains a non-empty `## Input` section.
- No Active request exists in the register.

**Steps:**
1. Write a descriptive request text in `.aib_memory/input.md ## Input`.
2. Place a text file named `sample-spec.txt` with distinguishable content (e.g., "ATTACHMENT_MARKER_12345") in `.aib_memory/attachments/`.
3. Execute `aib-analysis.md`.
4. After execution completes, inspect `analysis.md` or `request.md` for evidence that the attachment was read (e.g., the distinguishable content or the file name is referenced).
5. Verify that `.aib_memory/attachments/` is empty after execution.
6. Verify that `sample-spec.txt` is present in `<request-folder>/inputs/`.

**Expected outcome:**
- The AI agent's analysis references the attachment file by name or content.
- `.aib_memory/attachments/` is empty.
- `sample-spec.txt` resides in `<request-folder>/inputs/sample-spec.txt`.

**Pass/Fail criteria:**
- PASS: Evidence of attachment reading in analysis artifacts AND staging folder is empty AND file is in request inputs.
- FAIL: No reference to attachment in analysis output OR staging folder retains files OR file is missing from request folder.

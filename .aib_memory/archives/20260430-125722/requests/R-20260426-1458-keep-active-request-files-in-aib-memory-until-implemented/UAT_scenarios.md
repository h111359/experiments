# UAT Scenarios — R-20260426-1458

## UAT-01 — Active-request files appear at .aib_memory root after analysis

**Trigger:** The updated `aib-analysis.md` is run with a non-empty `input.md` and no prior Active request.

**Preconditions:**
- No Active request in `requests_register.md`.
- `input.md` contains non-empty `## Input` content.
- Both `aib-analysis.md` and `aib-implement.md` have been updated per request scope.

**Steps:**
1. Write a short test intent into `.aib_memory/input.md`'s `## Input` section.
2. Execute `aib-analysis.md` from the AI coding interface.
3. After the prompt confirms completion, open `.aib_memory/` in a file explorer or IDE file tree.

**Expected outcome:**
- `.aib_memory/request.md` is visible at root level of `.aib_memory/`.
- `.aib_memory/analysis.md` is visible at root level of `.aib_memory/`.
- The request subfolder exists under `.aib_memory/requests/` but does NOT contain `request.md` or `analysis.md`.
- The developer can open and read `request.md` without navigating into a subfolder.

**Pass criteria:** All three bullets above are true simultaneously.

---

## UAT-02 — Active-request files are moved to request subfolder after implement

**Trigger:** The updated `aib-implement.md` is run after an Active request exists with files at `.aib_memory/` root.

**Preconditions:**
- An Active request is present (result of UAT-01 or equivalent).
- `.aib_memory/request.md` and `.aib_memory/analysis.md` exist.

**Steps:**
1. Execute `aib-implement.md` (or simulate the move step manually if a full implementation run is too costly).
2. After the prompt confirms completion, verify `.aib_memory/` in the file tree.

**Expected outcome:**
- `.aib_memory/request.md` no longer exists at root level.
- `.aib_memory/analysis.md` no longer exists at root level.
- `.aib_memory/requests/<request-folder>/request.md` exists.
- `.aib_memory/requests/<request-folder>/analysis.md` exists.
- The request state in `requests_register.md` is `Closed`.

**Pass criteria:** All five bullets above are true simultaneously.

---

## UAT-03 — Direct close (without implement) moves artifacts to request subfolder

**Trigger:** The menu "Close current request" action (or direct `close-request.py` invocation) is used while Active-request artifact files exist at `.aib_memory/` root.

**Preconditions:**
- An Active request is present.
- `.aib_memory/request.md` and `.aib_memory/analysis.md` exist (artifacts from a prior analysis run).
- `aib-implement.md` has NOT been run (simulating a close-without-implement scenario).

**Steps:**
1. Confirm `.aib_memory/request.md` and `.aib_memory/analysis.md` exist.
2. Run `python .aib_brain/tools/close-request.py --workspace .` (or trigger via menu).
3. After the script completes, check `.aib_memory/` and the request subfolder.

**Expected outcome:**
- `.aib_memory/request.md` no longer exists at root level.
- `.aib_memory/analysis.md` no longer exists at root level.
- `.aib_memory/requests/<request-folder>/request.md` exists.
- `.aib_memory/requests/<request-folder>/analysis.md` exists.
- The request state in `requests_register.md` is `Closed`.
- `input.md` is reset to seed template with `No active request`.

**Pass criteria:** All six bullets above are true simultaneously.

---

## UAT-04 — Developer ergonomics: reduced navigation friction

**Trigger:** Manual observation during active development using the updated AIB.

**Preconditions:** UAT-01 has been completed successfully.

**Steps:**
1. With an Active request running and files at `.aib_memory/` root, attempt to open `request.md` from the file tree.
2. Compare the number of folder navigations required with the old behavior (navigating into the request subfolder).

**Expected outcome:**
- `request.md` is accessible with one fewer folder-level navigation step compared to the old behavior.
- The developer can edit `request.md` without confusion about which copy is authoritative.

**Pass criteria:** Developer confirms the file is immediately accessible from `.aib_memory/` root without subfolder navigation.

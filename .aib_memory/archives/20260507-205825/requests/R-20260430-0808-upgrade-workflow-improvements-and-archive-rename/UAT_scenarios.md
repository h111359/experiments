# UAT Scenarios

Request: R-20260430-0808 — Upgrade workflow improvements and archive rename

---

## UAT-01 — Interactive requests-archival prompt: "archive old requests" choice

**Description:** Verify that when the user selects "N" (archive old requests) at the interactive prompt during `initialize.py --upgrade`, the old requests are NOT migrated into the new `.aib_memory/` and `requests_register.md` is freshly seeded.

**Preconditions:**
1. A workspace with `.aib_brain/` (with a new semver marker) and an existing `.aib_memory/` (with the old semver marker) is available.
2. `.aib_memory/requests/` contains at least one request subfolder.
3. `.aib_memory/requests_register.md` contains at least one request row.
4. The upgrade is triggered from a live interactive terminal session (stdin is a TTY).

**Steps:**
1. Launch `menu.py` from the workspace.
2. When the version mismatch banner appears, select `[1] Upgrade .aib_memory/ now`.
3. When the requests-archival prompt appears (e.g., "Migrate old requests to new .aib_memory/? [Y=migrate / N=archive only] (Y):"), enter `N`.
4. Allow the upgrade to complete.
5. Inspect `.aib_memory/requests/`.
6. Inspect `.aib_memory/requests_register.md`.
7. Inspect `.aib_memory/archives/<timestamp>/requests/` (the archive).

**Expected outcome:**
- `.aib_memory/requests/` contains no old request subfolders (only the freshly seeded empty directory).
- `.aib_memory/requests_register.md` contains only the seed header row with no data rows.
- `.aib_memory/archives/<timestamp>/requests/` contains the original request subfolders (data preserved in archive).
- The upgrade summary output includes a note indicating that old requests were archived and not migrated.
- The AIB menu is displayed automatically after upgrade completes (no "Please re-launch" message).

# UAT Scenarios — R-20260427-0858

Request: Upgrade .aib_memory structure on AIB version install

---

## UAT-01 — Menu starts normally when versions are consistent

**Precondition:** `.aib_brain/vX.Y.Z` and `.aib_memory/vX.Y.Z` carry the same version string (versions are in sync).

**Steps:**
1. Open a terminal and navigate to the workspace root.
2. Run `run.bat` (Windows) or `run.sh` (Unix).

**Expected outcome:** The AIB menu renders immediately with the standard action list. No upgrade prompt or version-mismatch message appears. The user can interact with menu actions normally.

---

## UAT-02 — Upgrade prompt appears on version mismatch

**Precondition:** `.aib_brain/vX.Y.Z` (e.g., `v1.2.9`) and `.aib_memory/vX.Y.Z-OLD` (e.g., `v1.2.8`) carry different version strings — or `.aib_memory/` has no version marker file at all.

**Steps:**
1. Open a terminal and navigate to the workspace root.
2. Run `run.bat` (Windows) or `run.sh` (Unix).

**Expected outcome:** Before the standard menu is shown, a message describing the version mismatch is displayed (e.g., "Brain version: v1.2.9 | Memory version: v1.2.8"). At least two options are presented: "Upgrade now" and "Skip". The user is not automatically upgraded without interaction.

---

## UAT-03 — "Skip" leaves `.aib_memory/` unchanged

**Precondition:** Same as UAT-02 (version mismatch detected; upgrade prompt shown).

**Steps:**
1. Open a terminal and run `run.bat` / `run.sh`.
2. At the upgrade prompt, select "Skip" (or equivalent).

**Expected outcome:** `.aib_memory/` directory is unmodified — its version marker still shows the old version, no backup archive has been created, and no files were added or changed. The standard menu is displayed after the user selects Skip.

---

## UAT-04 — "Upgrade now" invokes upgrade, creates backup, continues to menu

**Precondition:** Same as UAT-02 (version mismatch detected; upgrade prompt shown).

**Steps:**
1. Open a terminal and run `run.bat` / `run.sh`.
2. At the upgrade prompt, select "Upgrade now" (or equivalent).
3. Observe the output.
4. After the upgrade completes, inspect the backup location and `.aib_memory/`.

**Expected outcome:**
- The upgrade script output is displayed in the terminal (including confirmation that a backup was created and its path).
- A backup archive exists at the path shown in the output.
- `.aib_memory/` now contains the new version marker (matching `.aib_brain/`); the old marker is removed.
- Pre-existing files (`instructions.md`, `requests_register.md`, `references.md`) are intact and unmodified.
- The standard AIB menu then renders normally.
- Re-running the menu shows no upgrade prompt (SC-06 confirmed).

## Business & Functional Questions

### QID-BF-001 — Active context display format
**Intent:** Choose what the menu should display as the “active request” and “active iteration”.

**Rationale:** The request requires a concise active-status display; the exact identifiers affect UX and implementation (what to parse and how to present it).

**Impact Areas:** User Experience, Operations, Scope

**Answer Type:** single-select

**Options:**
- [x] A) Display request ID only (e.g., `R-20260321-2314`) + iteration ID (e.g., `02`) (recommended) — Most concise, stable.
- [ ] B) Display request folder name + iteration ID — More context, less concise.
- [ ] C) Display request title (from register) + IDs — Requires parsing title.
- [ ] D) Display all of the above — More verbose, higher UI clutter.
- [ ] Other — (describe below)

**Constraints & Guards:** Single-select; if “Other” is selected, specify exact format.


### QID-BF-002 — Instruction blocks fidelity in README
**Intent:** Confirm whether the two instruction blocks must appear verbatim in `.aib_brain/README.md`.

**Rationale:** The request provides exact strings and says they should be described in README; “verbatim vs equivalent” affects acceptance and prevents accidental wording drift.

**Impact Areas:** Requirements, User Experience

**Answer Type:** single-select

**Options:**
- [ ] A) Must be verbatim (exact lines/spaces) (recommended) — Minimizes interpretation risk.
- [ ] B) Equivalent meaning is fine, wording may change — Allows simplification.
- [x] C) Keep them in README but reorganize into bullets/sections — Improves readability.
- [ ] D) Keep only a short link/reference in README — Minimal doc footprint.
- [ ] Other — (describe below)

**Constraints & Guards:** If not verbatim, specify acceptable edits (e.g., punctuation changes).


## Architecture & Technical Questions

### QID-AT-001 — Definition of “initialized” for auto-init
**Intent:** Decide what condition triggers initialization on startup.

**Rationale:** `initialize.py` overwrites seed registries; to satisfy “otherwise don’t change it”, the guard must be precisely defined.

**Impact Areas:** Operations, Scope, Timeline

**Answer Type:** single-select

**Options:**
- [x] A) Folder-only: if `.aib_memory/` exists, do nothing (recommended) — Strictest “no change”.
- [ ] B) Key-file repair: if folder exists but seed files missing, create missing only — More robust.
- [ ] C) Integrity check: validate registries; repair if invalid — Most robust, most complex.
- [ ] D) Always initialize (overwrite) — Not compatible with stated constraint.
- [ ] Other — (describe below)

**Constraints & Guards:** If B/C, explicitly list which files are allowed to be written when folder exists.


### QID-AT-002 — Where to implement the auto-init check
**Intent:** Choose where the auto-initialization guard should live.

**Rationale:** The request mentions `run.bat`, but `run.sh` also exists; placement affects cross-platform parity and maintenance.

**Impact Areas:** Architecture, Operations, Timeline

**Answer Type:** single-select

**Options:**
- [x] A) In `.aib_brain/tools/menu.py` (recommended) — Single source of truth across launchers.
- [ ] B) In `.aib_brain/run.bat` only — Windows-only change.
- [ ] C) In both `.aib_brain/run.bat` and `.aib_brain/run.sh` — Duplicated logic across shells.
- [ ] D) In `initialize.py` itself (make it safe to run always) — Requires changing initializer semantics.
- [ ] Other — (describe below)

**Constraints & Guards:** If not A, specify how Linux/macOS parity should be handled.


### QID-AT-003 — Dynamic visibility scope
**Intent:** Decide which actions must be dynamically hidden/shown.

**Rationale:** The request explicitly calls out lifecycle actions; extending gating to auto-discovered scripts may be desirable but adds rules/schema.

**Impact Areas:** Scope, User Experience, Timeline

**Answer Type:** single-select

**Options:**
- [x] A) Only lifecycle actions (create/close request, create/close iteration) (recommended) — Matches request examples.
- [ ] B) Lifecycle actions + any action that requires an active request/iteration — Requires tagging rules.
- [ ] C) All actions become conditional via config metadata — More scalable, more complex.
- [ ] D) No dynamic gating; keep static menu — Not compatible with request.
- [ ] Other — (describe below)

**Constraints & Guards:** If B/C, specify how auto-discovered actions are classified.


### QID-AT-004 — Menu numbering stability expectation
**Intent:** Decide whether action numbers must remain stable across states.

**Rationale:** `menu.py` currently normalizes action IDs and relies on numeric shortcuts; filtering actions will likely change numbering.

**Impact Areas:** User Experience, Operations

**Answer Type:** single-select

**Options:**
- [x] A) Numbers may change; only visible actions must be numbered 1..N (recommended) — Simple and consistent.
- [ ] B) Numbers must remain stable across states — Requires non-contiguous numbering or mapping.
- [ ] C) Remove numeric shortcuts and rely on arrows/enter — UX regression risk.
- [ ] D) Keep stable numbers for the first 5 lifecycle actions only — Hybrid approach.
- [ ] Other — (describe below)

**Constraints & Guards:** If B/D, define the stable mapping explicitly.


## Appendix — Answer Encoding Rules
- For single-select questions: exactly one checkbox must be selected (`- [x]`).
- For “Other”: if selected, provide a short free-text clarification in the same section.
- Unchecked boxes use `- [ ]`.
- Checked boxes use `- [x]` (or `- [X]`).

# 1. Business & Functional Questions

---

### QID-BF-001 — Remove All Verbose Labels from Menu Lines

**Intent:**  
Decide which text to remove from each menu item line in the rendered terminal menu.

**Rationale:**  
`render_menu()` currently appends `[script_name]` to Script action lines and `[prompt_file]` to Prompt action lines. The request asks to remove "unnecessary information". The question is whether descriptions (the subtitle after the ` — ` separator) should also be removed, or only the bracketed path suffixes.

**Impact Areas:** User Experience, Scope

**Assumptions:**
- Currently each Script action line reads: `> 1) Create request - Create a new active request with initial iteration [create-request.py]`
- Currently each Prompt action line reads: `> 5) Create Analysis - Generate iteration analysis document [.aib_brain/prompts/aib-create-analysis.md]`

**Answer Type:** single-select

**Options:**
- [ ] A) Remove only the `[script]` and `[prompt_file]` bracketed suffixes; keep descriptions — e.g.: `> 1) Create request - Create a new active request with initial iteration` *(recommended)*
- [ ] B) Remove both the bracketed suffixes and all inline descriptions — e.g.: `> 1) Create request`
- [ ] C) Remove only from Prompt actions; keep the script name suffix on Script actions
- [ ] Other — (describe below)

```
Other answer:
```

---

### QID-BF-002 — Informational Prompt List Layout When CLI Is Absent

**Intent:**  
Define exactly how prompt actions are presented when GitHub Copilot CLI is not detected.

**Rationale:**  
The request states that when CLI is absent the menu should "list in minimalistic way the invocation strings for all possible prompts, without giving option for execution". The analysis assumes a static text block printed below the Script actions section. Alternative layouts are possible (separate screen, sub-menu, etc.). The choice affects how `render_menu()` and `choose_action()` are structured.

**Impact Areas:** User Experience, Architecture

**Assumptions:**
- CLI detection result is available before rendering.
- The navigable cursor (UP/DOWN/ENTER) should only cover Script action rows when CLI is absent.

**Answer Type:** single-select

**Options:**
- [ ] A) Show a static, non-navigable block in the same menu screen below Script actions, listing each prompt as: `  • Create Analysis  →  gh copilot suggest "Execute the prompt defined in .aib_brain/prompts/aib-create-analysis.md"` *(recommended)*
- [ ] B) Show a collapsed `[Prompt actions — Copilot CLI not detected]` label only; user presses a key to expand the full list as a read-only sub-screen
- [ ] C) Do not show any prompt-related information when CLI is absent
- [ ] D) Show prompt titles and file paths only (no invocation strings)
- [ ] Other — (describe below)

```
Other answer:
```

---

### QID-BF-003 — Auto-Close Iteration When Closing a Request: Feedback Style

**Intent:**  
Decide whether auto-closing an active iteration during `close-request` should print a notice, require confirmation, or proceed silently.

**Rationale:**  
Currently `close-request.py` blocks with an error if an active iteration exists. The new behavior will close the iteration automatically. The question is how transparent this side effect should be to the user. A printed notice is transparent but not intrusive; a confirmation prompt adds a safety check but slows the flow.

**Impact Areas:** User Experience, Scope, Requirements

**Answer Type:** single-select

**Options:**
- [ ] A) Print a notice `"Auto-closed iteration 01 before closing request."` and proceed without confirmation *(recommended)*
- [ ] B) Show a confirmation prompt `"Active iteration 01 will be auto-closed. Continue? [y/N]"` before proceeding
- [ ] C) Proceed silently — no notice, no confirmation
- [ ] Other — (describe below)

```
Other answer:
```

---

# 2. Architecture & Technical Questions

---

### QID-AT-001 — Exclusion Mechanism for Non-Tool Scripts in the Menu

**Intent:**  
Choose how `reverse-engineer.py` and `test_common.py` are excluded from the Script actions menu section.

**Rationale:**  
`build_script_actions()` auto-discovers all `.py` files in `tools/` not listed in `EXCLUDE_SCRIPTS`. Both `reverse-engineer.py` (a file-inventory helper for the reverse-engineer prompt) and `test_common.py` (a pytest test file) are currently auto-discovered and shown as menu entries. The simplest fix is extending `EXCLUDE_SCRIPTS`; a more robust fix is adopting an explicit allowlist. The choice has long-term maintenance implications as the tools directory grows.

**Impact Areas:** Architecture, Scope

**Assumptions:**
- `reverse-engineer.py` is a support helper for the `aib-reverse-engineer.md` prompt, not a direct user tool.
- `test_common.py` is a test file and should never appear in the interactive menu.

**Answer Type:** single-select

**Options:**
- [ ] A) Extend `EXCLUDE_SCRIPTS` constant with `reverse-engineer.py` and `test_common.py` — minimal change, consistent with existing pattern *(recommended)*
- [ ] B) Replace `EXCLUDE_SCRIPTS` with an explicit `INCLUDED_SCRIPTS` allowlist containing only `create-request.py`, `close-request.py`, `create-iteration.py`, `close-iteration.py` — safer for future growth
- [ ] C) Add a filename pattern rule: exclude all files matching `test_*.py` (auto-excludes current and future test files); `reverse-engineer.py` still added to `EXCLUDE_SCRIPTS` explicitly
- [ ] Other — (describe below)

```
Other answer:
```

---

### QID-AT-002 — Parameter Collection UX: Keep or Simplify

**Intent:**  
Decide whether the `collect_parameters()` function's banner, hints, and prompts should also be simplified or left as-is.

**Rationale:**  
The request says "no unnecessary texts or confirmation". `collect_parameters()` currently prints "Parameter input" / "---------------" header and per-field hint lines (`Hint: Root folder containing .aib_brain`). The request's focus appears to be on the menu rendering and the "Running command:" line, but the parameter collection flow is also verbose. This question ensures the scope is explicitly agreed before implementation.

**Impact Areas:** User Experience, Scope

**Answer Type:** single-select

**Options:**
- [ ] A) Leave `collect_parameters()` unchanged — only remove `[script]`/`[prompt_file]` suffixes and the `Running command:` line *(recommended)*
- [ ] B) Remove the "Parameter input / ------" banner but keep per-field hints
- [ ] C) Remove both the banner and per-field hints from `collect_parameters()`
- [ ] Other — (describe below)

```
Other answer:
```

---

# 3. Appendix — Answer Encoding Rules

## Checkbox Syntax

| State | Markdown |
| --- | --- |
| Unchecked | `- [ ]` |
| Checked | `- [x]` (lowercase x accepted; uppercase X also accepted) |

## Single-Select Rule

Exactly **one** checkbox must be checked per question block (including `Other`).  
Checking more than one option for a `single-select` question is invalid.

## Multi-Select Rule

Any number of checkboxes may be checked (zero = unanswered).

## Free-Text / Other Rule

If `Other` is checked (`- [x] Other — (describe below)`), the fenced `Other answer:` block below it **MUST** contain non-empty text.

## Recommended Option

The word `(recommended)` at the end of an option label indicates the AI's suggested default.  
You may override it freely; it is not a constraint.

## Completion Check

A question is considered **answered** when:
- Its selection state is valid (single-select: exactly one checked; multi-select: at least one checked or explicitly left blank with a comment).
- Any `Other answer:` block is filled in if `Other` is checked.

# 1. Business & Functional Questions

---

### QID-BF-001 — GitHub Copilot CLI Invocation Binary

**Intent:**  
Confirm whether prompt actions should be executed via `gh copilot suggest "..."` (GitHub CLI extension) or via a different `copilot` binary.

**Rationale:**  
The request.md Goal section items 2 and 3 reference `copilot --version` for detection and `subprocess.run(["copilot", "Execute the prompt defined in <path>"])` for execution — without the `gh` prefix and without the `suggest` subcommand. The existing `_detect_copilot_cli()` function in `menu.py` already uses `["gh", "copilot", "--version"]`, and the iteration 01 Section 8 rewrite proposal explicitly used `["gh", "copilot", "suggest", ...]`. These forms are incompatible: the former targets a standalone `copilot` binary while the latter targets the GitHub CLI extension. Choosing the wrong one means CLI detection always returns False (silently falls back to static informational mode), making prompt-action execution unreachable.

**Impact Areas:** Scope, Architecture, User Experience

**Assumptions:**
- `gh copilot suggest "<prompt>"` is the standard GitHub Copilot CLI invocation on machines with the GitHub CLI installed.
- The standalone `copilot` binary (if it exists) would use a different invocation format.

**Answer Type:** single-select

**Options:**

- [ ] A) Use `["gh", "copilot", "--version"]` for detection and `["gh", "copilot", "suggest", "Execute the prompt defined in <path>"]` for execution — consistent with the existing code, GitHub CLI ecosystem conventions, and the iteration 01 rewrite proposal. *(recommended)*

- [x] B) Use `["copilot", "--version"]` for detection and `["copilot", "Execute the prompt defined in <path>"]` for execution — literal interpretation of request.md Goal items 2 and 3.

- [ ] C) Use `["copilot", "--version"]` for detection and `["copilot", "suggest", "Execute the prompt defined in <path>"]` for execution — bare `copilot` binary with the `suggest` subcommand.

- [x] Other — (describe below)

```
Other answer: If copilot is installed, the cmd command for running it is `copilot`
```

---

# 2. Architecture & Technical Questions

No architecture or technical questions remain after full-doc review. All other design decisions from the 01-questionnaire (QID-BF-001 through QID-AT-002) have been definitively resolved by the updated request.md Goal section.

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

## Free-Text / Other Rule

If `Other` is checked (`- [x] Other — (describe below)`), the fenced `Other answer:` block below it **MUST** contain non-empty text.

## Recommended Option

The word `(recommended)` at the end of an option label indicates the AI's suggested default.  
You may override it freely; it is not a constraint.

## Completion Check

A question is considered **answered** when:
- Its selection state is valid (single-select: exactly one checked).
- Any `Other answer:` block is filled in if `Other` is checked.

# Consistency Analysis

## Timestamp

2026-05-15 07:11 (local, UTC+0300)

## Scope

This audit covers the following files and folders:

- `.aib_brain/prompts/` — 3 files: `aib-analysis.md`, `aib-context.md`, `aib-implement.md`
- `.aib_brain/conventions/` — 18 files: `analysis-convention.md`, `request-convention.md`, `implementation-convention.md`, `context-convention.md`, `requests_register-convention.md`, and 13 `coding-*-convention.md` files
- `.aib_brain/tools/` — 8 Python scripts: `common.py`, `create-request.py`, `close-request.py`, `finalize-input.py`, `initialize.py`, `menu.py`, `move-request-artifacts.py`, `file-inventory.py`
- `.aib_memory/context.md`
- `.aib_memory/instructions.md`
- `README.md` (workspace root)

Note: The original `input.md` that generated this request did not contain an explicit `### Scope` section. The scope above was inferred from the audit instructions ("documentation, conventions, templates, and prompts"). See Coverage & Gaps.

## Coverage & Gaps

| Area | Files Discovered | Files Read | Skipped / Unreadable |
| --- | --- | --- | --- |
| `.aib_brain/prompts/` | 3 | 3 (full) | 0 |
| `.aib_brain/conventions/` — operational | 5 | 5 (full) | 0 |
| `.aib_brain/conventions/` — coding | 13 | 1 full (`coding-general-convention.md`), 12 skimmed | 0 |
| `.aib_brain/tools/` | 8 | 6 full + 2 partial (`initialize.py`, `menu.py`) | 0 |
| `.aib_memory/context.md` | 1 | 1 (full) | 0 |
| `.aib_memory/instructions.md` | 1 | 1 (full) | 0 |
| `README.md` (root) | 1 | 1 (full) | 0 |
| `.aib_brain/README.md` | 1 | 1 (full) | 0 |

**Coverage gaps:**

- Coding conventions (`coding-css-convention.md`, `coding-dax-convention.md`, etc.) were skimmed for structural alignment only due to their volume and lower priority relative to operational conventions. Deep consistency analysis of coding conventions against each other is not performed in this audit.
- `menu.py` and `initialize.py` were read partially (first 80–100 lines each); behavioral correctness was not fully verified.

---

## Findings (Prioritized)

---

### F-001 — High

**Title:** `context.md` describes 8 mandatory analysis sections; the actual convention and prompt define only 4

**Evidence:**

`analysis-convention.md` section 4 (mandatory structure):

> "Each analysis file **must** contain the following sections in the exact order:
> 1. Executive Summary [REQ]
> 2. Files Read During This Analysis Run [REQ]
> 3. Research Results [REQ]
> 4. Implementation Alternatives [REQ]"

`.aib_memory/context.md` FR-004 and component map entry for `aib-analysis.md`:

> "The `analysis-<request_id>.md` artifact contains 8 mandatory sections: Executive Summary, Files Read During This Analysis Run, Research Results, Best Practices, External Benchmarking, Minimal Spikes and Experiments, Implementation Alternatives, and AI Copilot Suggestions."

`aib-analysis.md` section 6.2 defines generation instructions for exactly those same 4 sections listed in `analysis-convention.md`. No generation guidance exists for Best Practices, External Benchmarking, Minimal Spikes and Experiments, or AI Copilot Suggestions.

**Why it matters:** An AI agent reads `context.md` as a preflight step in both `aib-analysis.md` and `aib-implement.md`. The stale 8-section description in `context.md` causes ambiguity: an agent applying `context.md` as a quality gate would reject a correctly structured 4-section analysis document, or an agent writing analysis would generate 4 extra unsupported sections, producing artifacts that do not match the convention.

**Recommendation:** Regenerate `context.md` via `aib-context.md`. The regenerated document should derive its FR-004 behavioral claims from the test suite and workspace sources that accurately reflect the current 4-section structure. If the tests themselves assert 8 sections, update the tests first (separate request).

**Risk/Trade-offs:** Low risk to fix — regenerating `context.md` is a routine operation. Risk if not fixed: agent behavior inconsistency across implementations.

---

### F-002 — High

**Title:** Q-block `*(recommended)*` marker: `context.md` requires it; `aib-analysis.md` explicitly forbids it

**Evidence:**

`.aib_memory/context.md` FR-007:

> "Each Q-block includes a `> **Why this matters:**` impact line, mutually exclusive options with a `*(recommended)*` marker, and a `> Answer:` field."

`.aib_memory/context.md` component map entry for `aib-analysis.md`:

> "Each Q-block includes a `> **Why this matters:**` impact line, mutually exclusive options, a `*(recommended)*` marker on the preferred choice, and a `> Answer:` field."

`aib-analysis.md` section 7.5.3 Q-block format:

> "Do NOT include a `*(recommended)*` marker on any option — the developer chooses without AI steering."

**Why it matters:** This is a direct binary contradiction. Both `aib-analysis.md` and `aib-implement.md` read `context.md` as context. An agent that applies `context.md` as the normative source for Q-block format will produce Q-blocks with a `*(recommended)*` marker, violating the explicit prohibition in the prompt. Conversely, an agent reading only the prompt will produce Q-blocks without a marker, which `context.md` describes as non-compliant. This ambiguity could confuse agents into steering developers toward a "preferred" option, which the prompt architecture explicitly wants to prevent.

**Recommendation:** Regenerate `context.md` to remove the `*(recommended)*` marker references from FR-007 and the component map. The authoritative source is `aib-analysis.md` section 7.5.3.

**Risk/Trade-offs:** No implementation risk. Regenerating `context.md` will resolve this once the test suite no longer asserts the recommended marker behavior.

---

### F-003 — Medium

**Title:** `context.md` requires `### Decision Points Catalog` subsection heading; prompt and convention use no specific heading

**Evidence:**

`.aib_memory/context.md` FR-004:

> "MUST contain a `### Decision Points Catalog` subsection enumerating all decision forks and tagging each as `ask` or `resolve-autonomously`; the `Category` field MUST be one of..."

`aib-analysis.md` section 7 (section `## Implementation Alternatives`):

> "Produce a **Decision Points table** with columns `Decision Fork`, `Tag`, `Rationale / Resolution` covering every identified fork..."

`analysis-convention.md` section 4.4:

> "A **Decision Points table** with columns `Decision Fork`, `Tag`, `Rationale / Resolution`."

Neither the prompt nor the convention names this table with the heading `### Decision Points Catalog`. They reference it as an inline table under `## Implementation Alternatives`.

**Why it matters:** An agent enforcing `context.md` as the quality gate for analysis documents would require a `### Decision Points Catalog` level-3 heading, which is not in the convention. This creates format drift and unpredictable document structure.

**Recommendation:** Regenerate `context.md`. The Decision Points table does not require a named subsection heading per the current convention and prompt.

**Risk/Trade-offs:** Low. Only affects the analysis document heading structure. Agents that have previously generated a `### Decision Points Catalog` heading have not violated anything; it is a superset of what is required.

---

### F-004 — Medium

**Title:** `context.md` requires a `Category` field in the Decision Points table; prompt and convention do not

**Evidence:**

`.aib_memory/context.md` FR-004:

> "The `Category` field MUST be one of `Architecture`, `Data Model`, `UX/UI`, `Integration`, `Performance`, `Testing`, or `Documentation`."

`aib-analysis.md` section 7 Decision Points table definition: columns are `Decision Fork`, `Tag`, `Rationale / Resolution` only.

`analysis-convention.md` section 4.4 Decision Points table: same 3 columns with no `Category`.

**Why it matters:** Same pattern as F-003 — `context.md` imposes an additional validation requirement on analysis documents that neither the prompt nor the convention supports. An agent or human reviewer using `context.md` as a quality gate would incorrectly reject valid analysis documents.

**Recommendation:** Regenerate `context.md` to remove the `Category` field requirement from FR-004.

**Risk/Trade-offs:** Low. Only affects analysis document validation.

---

### F-005 — Medium

**Title:** `requests_register-convention.md` timestamp format: normative text and worked example are inconsistent

**Evidence:**

`requests_register-convention.md` line 38 (normative spec):

> "`created_at` — ISO local timestamp when the request was created, format `YYYY-MM-DD HH:MM:SS ±HHMM` (24h, with seconds and timezone offset)."

`requests_register-convention.md` line 52 (Table Skeleton example):

> `| R-YYYYMMDD-HHmi   | <title> | ... | Active  | YYYY-MM-DD HH:MI  |`

The example uses `YYYY-MM-DD HH:MI` (no seconds, no timezone), which directly contradicts the normative text and the Validation Rules section (line 104) which correctly repeats `YYYY-MM-DD HH:MM:SS ±HHMM`.

**Why it matters:** Worked examples in convention files carry high cognitive weight. A developer or agent reading the example will likely produce timestamps without seconds and timezone, causing validation failures against the normative rule (line 104). This is a classic specification-by-example inconsistency.

**Recommendation:** Update the Table Skeleton example in `requests_register-convention.md` to use `YYYY-MM-DD HH:MM:SS ±HHMM` format, consistent with the normative text. Also update the Worked Example Rows (around line 58) to use the full format.

**Risk/Trade-offs:** Change is confined to the convention file; no tool scripts need updating. Risk if not fixed: new contributors generate non-conformant timestamp values.

---

### F-006 — Medium

**Title:** `aib-analysis.md` section 6.1 note is ambiguous about whether the analysis document is generated when triggered from `aib-implement.md`

**Evidence:**

`aib-analysis.md` section 6.1:

> "Always generated unless triggered from `aib-implement.md` (see Standard Flow Final Step note in section 8)."

The Standard Flow Final Step (section 8) restricts the `finalize-input.py` invocation, not the analysis document generation. If taken literally, section 6.1 says the analysis document is *not* generated when `aib-analysis.md` is triggered from `aib-implement.md` — but this would leave the Plan in `request.md` empty and `aib-implement.md` without an execution scope.

`aib-analysis.md` section 4.7 (Auto-Request Creation Branch) step 7: "Resume the standard analysis flow at Preflight step 6... The request.md file that was just created is to be analyzed." This step clearly implies analysis generation should proceed.

**Why it matters:** If an agent reads section 6.1 literally, it will skip writing `analysis-<request_id>.md` when triggered from `aib-implement.md`. This would leave the request with a populated `request.md` but no supporting analysis, and more critically, the Plan section of `request.md` might not be generated, leaving implement with no execution scope.

**Recommendation:** Rewrite section 6.1 to remove the ambiguous "unless triggered from `aib-implement.md`" clause, or clarify that the restriction applies only to the Standard Flow Final Step (the `finalize-input.py` call in section 8), not to analysis document generation itself. Suggested replacement:

> "Always generated. When `aib-analysis.md` is triggered from `aib-implement.md`, section 8 (Standard Flow Final Step) is suppressed — the analysis document itself is still written."

**Risk/Trade-offs:** Low risk. Only affects the prompt clarity; no tool script or convention changes needed.

---

### F-007 — Low

**Title:** Scope of "implement MUST NOT read analysis document" is narrower in `context.md` than in the convention and prompt

**Evidence:**

`context.md` component map entry for `aib-analysis.md`:

> "`analysis-<request_id>.md` artifact... AI Copilot Suggestions (reasoning-only, MUST NOT be read or acted on by `implement`)."

`analysis-convention.md` section 1:

> "The analysis document is NOT an implementation driver. `implement` MUST NOT read the analysis document."

`aib-analysis.md` section 5:

> "The analysis document is a reasoning artifact only; it is NOT an implementation driver... `implement` MUST NOT read or act on it."

`context.md` says only the AI Copilot Suggestions section is off-limits for implement; the convention and prompt restrict the entire document.

**Why it matters:** An agent reading `context.md` as the authority would believe it is permitted to read the analysis document (minus one section). This contradicts the convention and prompt intent of keeping implement strictly scoped to `request.md`.

**Recommendation:** Regenerate `context.md` to clarify that the entire analysis document is off-limits to implement, not just one section.

**Risk/Trade-offs:** Low. The restriction is more permissive in context.md than in the authoritative sources, so existing analysis documents are not at risk.

---

### F-008 — Low

**Title:** `context.md` Product Identity version string is stale

**Evidence:**

`.aib_memory/context.md` Product Identity section:

> "Current version: **v1.2.8** (active request R-20260514-2159 in progress; next release pending)."

`requests_register.md`: request R-20260514-2159 is in `Closed` state. Multiple additional requests have been closed since then (R-20260515-0629 and R-20260515-0710).

**Why it matters:** `context.md` is auto-generated and expected to be refreshed regularly. Stale version and request state references do not directly cause agent failures (agents do not make implementation decisions based on the version string), but they reduce trust in `context.md` as an accurate product snapshot.

**Recommendation:** Run `aib-context.md` to regenerate `context.md`. This is already recommended by F-001–F-004 and F-007; a single regeneration run will resolve all five context.md findings.

**Risk/Trade-offs:** None. Standard maintenance operation.

---

### F-009 — Nit

**Title:** `input.md` used to generate this request had no explicit `### Scope` section, requiring scope inference

**Evidence:**

The `## Input` section of the input.md that generated request R-20260515-0710 contained the instruction:

> "You will review ONLY the files and folders listed under **Scope** below."

However, no `### Scope` section followed. The audit scope was inferred from the input body.

**Why it matters:** The missing scope section introduces ambiguity about what the developer intended to include. The inferred scope may not match the intended scope exactly.

**Recommendation:** When preparing future consistency audit inputs, include an explicit `### Scope` section enumerating the target folders and files. This is informational only; no file change is needed.

**Risk/Trade-offs:** None. Developer-process guidance only.

---

## Cross-Reference Check Summary

### Broken References

None found. All file paths referenced in the in-scope prompts and conventions resolve to existing files:

- `aib-analysis.md` → `.aib_brain/conventions/analysis-convention.md` ✓
- `aib-analysis.md` → `.aib_brain/conventions/request-convention.md` ✓
- `aib-implement.md` → `.aib_brain/conventions/implementation-convention.md` ✓
- `aib-context.md` → `.aib_brain/conventions/context-convention.md` ✓
- `README.md` → `.aib_brain/README.md` ✓
- Tool script imports (`from common import ...`) → all referenced symbols exist in `common.py` ✓

### Suspicious References

- `context.md` references `analysis-<request_id>.md` with 8 sections and a `### Decision Points Catalog` subsection — these are references to a structure that no longer matches the current convention. See F-001, F-003.
- `requests_register-convention.md` Table Skeleton example uses `YYYY-MM-DD HH:MI` for timestamps while the normative text requires `YYYY-MM-DD HH:MM:SS ±HHMM`. See F-005.

---

## Redundancy & Source-of-Truth Map

| Key Concept | Authoritative Source | Secondary / Derived Sources | Conflict? |
| --- | --- | --- | --- |
| Analysis document section structure | `analysis-convention.md` section 4 | `aib-analysis.md` section 6.2, `context.md` FR-004 | Yes — `context.md` describes 8 sections vs convention's 4 (F-001) |
| Q-block format | `aib-analysis.md` section 7.5.3 | `context.md` FR-007 | Yes — recommended marker conflict (F-002) |
| Decision Points table structure | `aib-analysis.md` section 7, `analysis-convention.md` section 4.4 | `context.md` FR-004 | Yes — Category field and heading name (F-003, F-004) |
| Register timestamp format | `requests_register-convention.md` (normative text) | Convention worked example | Yes — example shows shorter format (F-005) |
| Active request resolution | `requests_register.md` (single source of truth) | `common.py` | No conflict |
| Artifact placement (active vs archived) | `request-convention.md`, `analysis-convention.md` | `context.md`, `move-request-artifacts.py` | No conflict |
| implement may not read analysis | `analysis-convention.md` section 1, `aib-analysis.md` section 5 | `context.md` component map | Partial — `context.md` restricts only AI Copilot Suggestions section (F-007) |
| Workspace instructions | `.aib_memory/instructions.md` | None (single source) | No conflict |

---

## Suggested Next Actions

- [ ] **Regenerate `context.md`** via `aib-context.md`. A single run will resolve F-001, F-002, F-003, F-004, F-007, and F-008 — provided the test suite and workspace sources accurately reflect the current 4-section analysis structure and the no-recommended-marker Q-block format.
- [ ] **Update `requests_register-convention.md` worked examples** (Table Skeleton around line 52, Worked Example Rows around line 58) to use the full `YYYY-MM-DD HH:MM:SS ±HHMM` timestamp format, resolving F-005. This is a quick, low-risk edit.
- [ ] **Clarify `aib-analysis.md` section 6.1 note** about analysis generation when triggered from `aib-implement.md`, resolving F-006. Replace the ambiguous "unless triggered from aib-implement.md" with explicit text stating that only the Standard Flow Final Step (section 8) is suppressed.
- [ ] **Verify test suite** (`tests/`) for any tests that assert 8 analysis sections, a `*(recommended)*` marker in Q-blocks, or a `### Decision Points Catalog` heading. If such tests exist, update them before regenerating `context.md`, or `context.md` will regenerate with the same stale claims.
- [ ] **Add explicit `### Scope` section** to future audit input.md entries to avoid scope inference (F-009, developer-process guidance).

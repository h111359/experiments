# Consistency Analysis

## Timestamp

2026-05-22 local time

## Scope

The entire workspace: `c:\Hristo\repos\coca-cola\AI_Builder`

## Coverage & Gaps

| Folder / Area | Files Discovered | Skipped/Unreadable |
| --- | --- | --- |
| Root | 2 (`README.md`, `write_analysis.py`) | None |
| `.aib_brain/` | 1 README + 3 prompts + 19 conventions + 7 tools + 1 version marker + 2 launchers + 1 user guide | `user_guide.html` (binary HTML, not deeply analyzed for content correctness) |
| `.aib_memory/` | `context.md`, `input.md`, `instructions.md`, `requests_register.md`, 35 closed request folders, `attachments/`, `logs/`, `archives/` | Closed request subfolders not deeply read (per GC-06 spirit); `archives/` only spot-checked for stale references |
| `docs/` | 4 files | None |
| `logs/` | 38 version logs + `next_version_changes.md` | Individual version logs not read (repetitive pattern) |
| `recordings/` | 8 `.webm` files | Binary video files — acknowledged by name only |
| `scripts/` | 1 file (`release_bookkeeping.py`) | None |
| `tests/` | 17 files | Read `conftest.py`; other test files noted by name |
| `versions/` | 28 `.zip` archives | Binary archives — acknowledged by name only |
| `.github/workflows/` | 1 file | None |

**Coverage notes:**
- All current (non-archived) documentation, prompts, conventions, and tool scripts were read in full.
- The `.aib_memory/archives/` folder contains legacy context snapshots from a prior AIB version; these were spot-checked for stale reference propagation but not fully analyzed.

---

## Findings (Prioritized)

### F-001

**Severity:** Critical  
**Title:** `analysis-convention.md` section 6 directs Q-blocks to the wrong target

**Evidence:**
- `.aib_brain/conventions/analysis-convention.md` lines 182–183:
  > If request ambiguity exists that cannot be resolved internally, create a `Q<nnn>` question block in `plan-<request_id>.md` -> `## Decisions` instead of making assumptions.
- `.aib_brain/prompts/aib-analyze.md` section 6.3.3 (Q-block generation target):
  > Q-blocks are written to a `## Questions` section appended to `input.md` (`.aib_memory/input.md`).

**Why it matters:** The convention file is authoritative for the analysis document structure. An AI agent reading the convention after reading the prompt encounters a direct contradiction about where Q-blocks are placed. This can cause Q-blocks to be written to `plan.md ## Decisions` instead of `input.md ## Questions`, breaking the entire Q&A workflow.

**Recommendation:** Replace the bullet in `analysis-convention.md` section 6 (Determinism Rules) with:
```
* If request ambiguity exists that cannot be resolved internally, generate a Q-block in `input.md ## Questions` per the rules in `aib-analyze.md` section 6.3.
```

**Risk/Tradeoffs:** Low risk — this is a documentation correction aligning the convention with the implemented behavior.

---

### F-002 - Skipped

---

### F-003 - skip

---

### F-004 - skip

---

### F-005

**Severity:** Medium  
**Title:** `write_analysis.py` contains hardcoded stale path

**Evidence:**
- `write_analysis.py` lines 3–5:
  ```python
  new_content = pathlib.Path(r'c:\Hristo\projects\AI_Builder\analysis_new.md').read_text(encoding='utf-8')
  pathlib.Path(r'c:\Hristo\projects\AI_Builder\.aib_memory\analysis.md').write_text(new_content, encoding='utf-8', newline='\n')
  ```

**Why it matters:** The paths reference `c:\Hristo\projects\AI_Builder\` which does not match the current workspace (`c:\Hristo\repos\coca-cola\AI_Builder`). The script also references `analysis.md` without a request ID suffix, which is the obsolete naming convention. This script would fail if executed and could confuse contributors about the current artifact naming pattern.

**Recommendation:** Either remove this file (it appears to be a one-off utility that is no longer needed) or update it to use relative paths and the current `analysis-<request_id>.md` naming convention.

**Risk/Tradeoffs:** Low risk — the script is clearly a legacy utility. Removing it eliminates confusion.

---

### F-006

**Severity:** Medium  
**Title:** Duplicate quality-check instructions in `aib-analyze.md`

**Evidence:**
- `aib-analyze.md` section 5.7 (Step 7 — Quality Check, line ~207):
  > After generating the analysis (step 5), evaluate every mandatory checklist item from `requirements-analysis-convention.md`...
- `aib-analyze.md` section 6.1 (Analysis Document, line ~238):
  > After reading `requirements-analysis-convention.md` (step 3.6), evaluate every mandatory checklist item...

Both passages contain nearly identical instructions for the requirements gate evaluation.

**Why it matters:** Duplicate instructions increase the risk of divergence over time and create ambiguity about which is authoritative. An agent may execute the evaluation twice or become confused about when it should occur.

**Recommendation:** Keep the instruction in section 5.7 (Step 7) as the authoritative execution point. In section 6.1, replace the duplicated paragraph with a cross-reference:
```
See Step 7 (section 5.7) for the mandatory requirements gate evaluation procedure.
```

**Risk/Tradeoffs:** Low risk — consolidation improves clarity without changing behavior.

---

### F-007 Skipped


---

### F-008

**Severity:** Medium  
**Title:** `aib-refresh-context.md` instructs using `file-inventory.py` but also excludes `.aib_brain/` from scan

**Evidence:**
- `.aib_brain/prompts/aib-refresh-context.md` line 71:
  > Use `.aib_brain/tools/file-inventory.py` to emit a JSONL inventory
- Same file, line 17:
  > Do not explore or read `.aib_brain/` folder contents except `.aib_brain/conventions/context-convention.md`.

**Why it matters:** Running `.aib_brain/tools/file-inventory.py` requires reading a file from `.aib_brain/`. This creates a logical inconsistency — the prompt tells the agent to use a tool it's forbidden from reading. In practice, AI agents invoke tool scripts without "reading" them (they execute them), but the constraint language is ambiguous enough to cause confusion.

**Recommendation:** Add an explicit exception: "Do not explore or read `.aib_brain/` folder contents except `.aib_brain/conventions/context-convention.md` and tool script invocations listed in this prompt."

**Risk/Tradeoffs:** Low risk — clarification only.

---

### F-009

**Severity:** Medium  
**Title:** `.aib_brain/README.md` says "AI specification based development called" (grammatically broken)

**Evidence:**
- `.aib_brain/README.md` line 4:
  > AI Builder (AIB) is a minimal but powerful framework for AI specification based development called. AIB serves for software development...

**Why it matters:** The sentence is grammatically malformed ("called" is a dangling word), making the product introduction unclear to new users.

**Recommendation:** Rewrite as:
```
AI Builder (AIB) is a minimal but powerful framework for AI specification-driven development. AIB serves for software development...
```

**Risk/Tradeoffs:** None — pure grammar fix.

---

### F-010

**Severity:** Low  
**Title:** `context.md` preamble uses date-only format instead of full timestamp

**Evidence:**
- `.aib_memory/context.md` line 3:
  > `> **Auto-generated** by `aib-refresh-context.md` on 2026-05-22 local time.`
- `context-convention.md` Preamble Format specifies:
  > `on <YYYY-MM-DD HH:MM timezone>`

**Why it matters:** The preamble is missing the time component (`HH:MM`) and the timezone identifier. While "local time" conveys the idea, it doesn't match the specified format.

**Recommendation:** Next `aib-refresh-context.md` execution will naturally fix this. No manual action needed unless the prompt has a bug preventing full timestamp generation.

**Risk/Tradeoffs:** None — will self-correct on next execution.

---

### F-011

**Severity:** Low  
**Title:** `context.md` has a duplicate `logs/` directory entry

**Evidence:**
- `.aib_memory/context.md` contains two separate bullets for `logs/`:
  > `- `logs/` — Contains per-version release log files and the curated change log; individual version logs follow the pattern `version_vX.Y.Z_log.md`.`
  > `- `logs/` — Contains 38 per-version release log files following the pattern `version_vX.Y.Z_log.md`; individual items are not listed.`

**Why it matters:** Duplicate entries violate the uniqueness expectation of the file inventory section and could confuse agents about what `logs/` contains.

**Recommendation:** Merge into a single entry. Will self-correct on next `aib-refresh-context.md` execution.

**Risk/Tradeoffs:** None.

---

### F-012 skipped

---

### F-013

**Severity:** Low  
**Title:** `aib-implement.md` "Auto-Analysis Branch" uses stale terminology

**Evidence:**
- `.aib_brain/prompts/aib-implement.md` Input resolution Step 2:
  > Auto-Analysis Branch — trigger the `aib-analyze.md` flow (read and execute `.aib_brain/prompts/aib-analyze.md`)

The prompt says "aib-analyze.md flow" but references it by the full correct path. No actual inconsistency, but this phrasing pattern differs from other references.

**Why it matters:** Minor; consistency of reference style. All other prompt cross-references use the full path.

**Recommendation:** No action needed — this is a nit.

**Risk/Tradeoffs:** None.

---

### F-014

**Severity:** Nit  
**Title:** Path separator inconsistency in `instructions.md`

**Evidence:**
- `.aib_memory/instructions.md` README maintenance section:
  > `.aib_brain\prompts\aib-implement.md`
  > `.aib_brain\README.md`
  > `.aib_memory\context.md`

All other AIB documentation consistently uses forward slashes (`/`) for workspace-relative paths.

**Why it matters:** While Windows tolerates both separators, POSIX systems do not. The repository conventions (and the `requests_register-convention.md`) explicitly require forward slashes for portability.

**Recommendation:** Replace backslashes with forward slashes in `instructions.md`.

**Risk/Tradeoffs:** None.

---

### F-015

**Severity:** Nit  
**Title:** `analysis-convention.md` section 2 references location as `.aib_memory/requests/<request-folder>/` but section 3 correctly describes the two-phase placement

**Evidence:**
- Section 2 (Scope & Normative Language):
  > Location: `.aib_memory/requests/<request-folder>/`
- Section 3 (File Naming, Location & Write Behavior):
  > Active phase — resides at `.aib_memory/analysis-<request_id>.md`

**Why it matters:** Section 2 only mentions the archived location without noting the active-phase placement. While section 3 corrects this, an agent reading section 2 in isolation could conclude the file should always be inside the request folder.

**Recommendation:** Update section 2 to:
```
* Location: `.aib_memory/` (active phase) or `.aib_memory/requests/<request-folder>/` (archived phase)
```

**Risk/Tradeoffs:** None — documentation alignment.

---

## Cross-Reference Check Summary

### Broken References

| Source File | Reference | Status |
| --- | --- | --- |
| `docs/Copilot_Issue_Assignment_Rules.md` | `logs\versions_log.md` | **BROKEN** — file does not exist |
| `write_analysis.py` | `c:\Hristo\projects\AI_Builder\analysis_new.md` | **BROKEN** — stale absolute path, non-existent file |
| `write_analysis.py` | `c:\Hristo\projects\AI_Builder\.aib_memory\analysis.md` | **BROKEN** — stale path and obsolete filename pattern |

### Suspicious References (should be verified)

| Source File | Reference | Concern |
| --- | --- | --- |
| `analysis-convention.md` section 6 | `plan-<request_id>.md` -> `## Decisions` (for Q-blocks) | **INCORRECT** — contradicts the actual Q-block target (`input.md ## Questions`) |
| `docs/aib-refresh-context-AIB_version.md` | "Explore especially `.aib_brain/`" | **CONTRADICTS** canonical prompt's non-goal rule |
| `aib-refresh-context.md` line 71 | `.aib_brain/tools/file-inventory.py` | May conflict with the "do not read .aib_brain/" non-goal |

---

## Redundancy & Source-of-Truth Map

| Concept | Authoritative Source | Other Locations | Conflict? |
| --- | --- | --- | --- |
| Analysis document structure | `analysis-convention.md` section 4 | `aib-analyze.md` section 6.1 | No conflict — prompt defers to convention |
| Q-block target location | `aib-analyze.md` section 6.3.3 | `analysis-convention.md` section 6 | **YES** — convention says `plan.md ## Decisions`, prompt says `input.md ## Questions` |
| Plan structure | `plan-convention.md` | `aib-analyze.md` section 6.2 | No conflict — consistent |
| Requirements gate evaluation | `requirements-analysis-convention.md` | `aib-analyze.md` sections 5.7 AND 6.1 | Redundant — same instruction duplicated in two sections |
| Context.md structure | `context-convention.md` | `aib-refresh-context.md` | No conflict — prompt defers to convention |
| Version bump procedure | `Development_and_Deployment_Specification.md` + `release_bookkeeping.py` | `Copilot_Issue_Assignment_Rules.md` | **YES** — obsolete manual procedure in Copilot rules |
| Branch naming | `Development_and_Deployment_Specification.md` | Actual practice | **YES** — `issue/N` convention not followed |
| `.aib_brain/` exploration rules | `aib-refresh-context.md` (canonical) | `docs/aib-refresh-context-AIB_version.md` | **YES** — opposite instructions (by design, but undocumented) |

---



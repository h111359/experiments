# Analysis — R-20260416-1053-readme-improve

## Executive Summary

- **Request ID:** R-20260416-1053

- **Request title:** readme-improve

- **High-level purpose:** Review `.aib_brain/README.md` for obsolete content, and restructure it to be more readable and memorable — providing a clear, concise explanation of AIB functionality to new and existing users.

- **Source:** The request goal was provided directly in `request.md`; Background, Scope, Out of scope, Constraints, and Success criteria sections were empty at analysis time and have been inferred and populated from the stated goal.

- **Key findings from research:** The README is largely accurate for current tool paths and prompt file paths. The primary issues are structural: the Typical Daily Flow omits the `create-analysis` step, Scenarios 3 and 4 are functionally redundant, and the Quick Start section repeats menu output text blocks unnecessarily.

- **Risk profile:** Low. The target is documentation-only. No tool scripts, registers, or logic are changed.

- **`request.md` sections updated during this run:** Background, Scope, Out of scope, Constraints, Success criteria (inferred from goal); Assumptions, Plan, Testing, Documentation appended. No Questions & Decisions raised.

---

## Domain Knowledge Essentials

**AIB (AI Builder):** A minimal, file-first framework for specification-driven development in a repository. It organises work as *requests* and uses convention-governed Markdown artifacts stored in `.aib_memory/`.

**Request:** A tracked work unit with a lifecycle (Active → Closed). Represents a single goal described in `request.md`. At most one request is Active at a time.

**`.aib_brain/`:** The framework asset layer — prompts, conventions, templates, and tool scripts. Replaceable on upgrade. Never modified by tool scripts.

**`.aib_memory/`:** The project-specific memory layer — request folders, registers, and `context.md`. Persists workspace state.

**Prompt action:** A Markdown file in `.aib_brain/prompts/` that defines a deterministic instruction set for an AI coding agent. Invoked via the AI chat interface (e.g., VS Code Copilot Chat).

**Tool script:** A Python 3.10+ script in `.aib_brain/tools/` that performs a deterministic filesystem operation (initialize, create-request, close-request, etc.).

**Interactive menu:** The terminal UI launcher (`run.bat` / `run.sh`) that lists and runs tool scripts with real-time output streaming.

**Impacted roles:**
- Developer — primary reader of the README; runs tool scripts via menu or direct invocation.
- AIB Maintainer — keeps `.aib_brain/` assets accurate and up to date.

**Business processes touched:**
- BP-0001 Initialize AIB workspace
- BP-0002 Create request
- BP-0004 Execute implement workflow

**Acceptance impact:** Improved README reduces onboarding friction and the chance of developers following a stale workflow.

---

## Technical Knowledge & Terms

**Canonical workflow (5 steps per context.md):**
1. `initialize` — seeds `.aib_memory/` once.
2. `create-request` — opens a new Active request.
3. `create-analysis` *(optional)* — generates `analysis.md` and updates `request.md`.
4. `implement` — executes the request scope.
5. `close-request` — finalises the request.

The current README Typical Daily Flow only shows steps 1, 2, and 5 — the `create-analysis` and `implement` steps are absent from the flow summary even though they are described elsewhere in the document.

**Deprecated tools:** `create-iteration.py` and `close-iteration.py` were deprecated as of R-20260414-1421. Neither appears in the current README — no action needed there.

**`reverse-engineer.py`:** A tool script present under `.aib_brain/tools/` that walks the workspace filesystem and produces a file inventory. Not listed in the README's Common Commands section, but covered indirectly by Scenario 5 (which uses `aib-context.md` as the entry point). No critical gap.

**Non-functional attributes:**
- Readability: The README is ~180 lines. Consolidation of redundant scenarios and removal of duplicate Quick Start text blocks would reduce it to ~130–140 lines without losing content.
- Determinism: README content is static documentation; no algorithmic determinism concerns.
- Security: No credentials, secrets, or sensitive paths involved.

**Files read during this analysis:**
- `.aib_memory/requests/R-20260416-1053-readme-improve/request.md` — active request
- `.aib_memory/references.md` — reference register
- `.aib_memory/context.md` — unified product knowledge (REF-0001)
- `.aib_brain/Concepts.md` — domain knowledge (REF-0002)
- `.aib_brain/conventions/analysis-convention.md` — analysis format rules
- `.aib_brain/conventions/request-convention.md` — request format rules
- `.aib_brain/README.md` — the target file under review
- `README.md` (workspace root) — cross-reference for scope confirmation
- `.aib_brain/prompts/` directory listing — to verify listed prompt files are current
- `.aib_brain/tools/` directory listing — to verify listed tools are current

---

## Research Results

### 1. Internal review of `request.md` and referenced docs

The goal is clear: review `.aib_brain/README.md` for obsolete content and improve readability. The mandatory sections (Background through Success criteria) were empty; all were inferred from the goal. The canonical workflow described in `context.md` (5-step holistic workflow per Concepts.md) is the authoritative reference for what the README flow should describe.

### 2. Code and asset scan for impacted components

- `.aib_brain/prompts/` contains exactly three files: `aib-analysis.md`, `aib-context.md`, `aib-implement.md`. All three are listed correctly in the README. No stale prompt references.
- `.aib_brain/tools/` contains: `close-request.py`, `common.py`, `create-request.py`, `initialize.py`, `menu.py`, `reverse-engineer.py`, `test_common.py`. The README correctly lists `initialize.py`, `create-request.py`, and `close-request.py` under Common Commands. `reverse-engineer.py` is present but not listed as a direct command (acceptable since it is exposed via the menu).
- `run.bat` and `run.sh` exist and are correctly referenced.
- No references to `create-iteration.py` or `close-iteration.py` were found in the README.

### 3. Pattern scan and structural findings

**Finding F-001 — Typical Daily Flow is incomplete.**
The README flow section shows only 3 steps: initialize → create-request → close-request. It omits the `create-analysis` (optional) and `implement` steps, which are the primary value actions of AIB. This does not match the canonical 5-step flow.

**Finding F-002 — Quick Start has redundant text blocks.**
Two code blocks under Quick Start show menu help text that is essentially the same content repeated with minor labelling differences. One block is sufficient.

**Finding F-003 — Scenarios 3 and 4 are functionally equivalent.**
Both Scenario 3 ("Regenerate workspace context after code changes") and Scenario 4 ("Regenerate workspace context") describe running `Execute .aib_brain/prompts/aib-context.md`. Scenario 3 adds the note that `aib-implement.md` calls it automatically. These can be combined into a single scenario with a note about automatic invocation.

**Finding F-004 — `create-analysis` missing from Scenarios.**
The scenarios do not include a standalone analysis re-run scenario, even though `aib-analysis.md` is an independent prompt that can be re-run multiple times on the same request.

**Finding F-005 — The document explains *what* to run but not *why* the flow exists.**
A short framing paragraph at the top of each major section would improve memorability for new users.

### 4. External benchmarking

Developer guides for small toolkits follow the pattern: 1-sentence purpose → quick start → annotated workflow → reference. The current README has these elements but the workflow section is incomplete (F-001) and contains redundancy (F-002, F-003). Consolidation would improve first-read retention.

### 5. Spikes / experiments

Not applicable — this is a documentation review with deterministic findings from file inspection.

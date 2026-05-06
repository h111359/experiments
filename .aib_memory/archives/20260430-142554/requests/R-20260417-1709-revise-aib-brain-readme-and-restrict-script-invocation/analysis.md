## Executive Summary

- **Request ID:** R-20260417-1709

- **Request title:** Revise aib_brain README and restrict script invocation

- **High-level purpose:** `.aib_brain/README.md` currently exposes direct Python script invocations (`initialize.py`, `create-request.py`, `close-request.py`) as user-facing commands. The request removes or reframes those instructions so it is unambiguous that `.aib_brain/tools/*.py` scripts are invoked by AIB prompts only — not by users. Users interact with AIB exclusively via the interactive menu (`run.bat`/`run.sh`) and AI prompt invocations.

- **Trigger branch:** Auto-Request Creation Branch — no Active request existed at invocation time; `input.md` contained the user intent; request R-20260417-1709 was created automatically.

- **`request.md` updates this run:** `request.md` was created from scratch (all 14 sections). Sections 1–6 (Goal through Success criteria) were populated from `input.md` content. Sections populated in Part 2 (this analysis run): `## Assumptions`, `## Plan`, `## Testing`, `## Documentation`, `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`, `## Multi-Perspective Stakeholder Review`.

- **Risk level:** Low. Scope is a single Markdown file; no code, scripts, or runtime state is affected.

- **Files read during this analysis:** `.aib_memory/input.md` (archived), `.aib_memory/references.md`, `.aib_memory/context.md` (REF-0001), `.aib_brain/Concepts.md` (REF-0002), `.aib_brain/README.md`, `.aib_brain/conventions/analysis-convention.md`, `.aib_brain/conventions/request-convention.md`, `.aib_memory/requests_register.md`.


---

## Domain Knowledge Essentials

- **AIB (AI Builder):** A minimal, model-agnostic framework for specification-driven development in a repository workspace. It provides deterministic, file-first workflows for managing requests, maintaining documentation, and automating release bookkeeping.

- **AIB Brain (`.aib_brain/`):** The reusable, replaceable framework-assets folder containing prompts, conventions, templates, and tool scripts. Never modified by tool scripts; replaced by AIB Maintainers on framework upgrade (ADR-0003).

- **AIB Memory (`.aib_memory/`):** Workspace-specific artifacts: requests, registers, `context.md`, `input.md`. Persists across framework upgrades.

- **AIB Prompts:** Markdown files in `.aib_brain/prompts/` invoked in an AI coding interface (e.g., VS Code Copilot). They contain the full workflow logic including all script invocations, state validation, and artifact writes.

- **AIB Tool Scripts (`.aib_brain/tools/*.py`):** Python automation scripts that execute deterministic AIB actions. They are implementation internals of the prompt workflow and are not intended for direct user invocation.

- **Interactive Menu (`run.bat`/`run.sh`):** A terminal UI that displays copy-paste-ready prompt invocations and surfaces non-excluded tool scripts. Lifecycle scripts (`create-request.py`, `close-request.py`) and internal helpers are excluded from the menu (`EXCLUDE_SCRIPTS` constant in `menu.py`).

- **Request:** A structured work item tracked in `.aib_memory/requests_register.md`. Lifecycle states: `Active` → `Closed`.

- **Single-Active-Request invariant:** At most one request may be `Active` at a time (FR-001). Direct script invocation by users can violate this invariant if preconditions are not validated.

- **Impacted personas:** Developer (primary reader of README), AI Automation Agent (reads prompts and invokes scripts), AIB Maintainer (maintains `.aib_brain/` assets).

- **Business process touched:** Developer onboarding and daily workflow guidance.


---

## Technical Knowledge & Terms

- **`.aib_brain/README.md`:** The human-facing guide to the AIB workflow. Located inside `.aib_brain/` and currently not listed in `references.md`. Contains Quick Start, Common Commands, Typical Daily Flow, and prompt invocation sections.

- **`edit_allowed` flag:** In `references.md`, `Y` means automation may modify the file. `.aib_brain/README.md` is not registered in `references.md`; its modification in this request is explicitly authorized by the request scope under human governance.

- **ADR-0003 — Separation of brain and memory:** Architecture decision establishing that `.aib_brain/` contains reusable framework assets never written by tool scripts. All workspace-specific writes go to `.aib_memory/`.

- **`EXCLUDE_SCRIPTS` constant in `menu.py`:** A list of script filenames that are hidden from the interactive menu. Lifecycle scripts (`create-request.py`, `close-request.py`) and internal helpers (`reverse-engineer.py`) are excluded — meaning the menu already enforces the "user does not invoke these directly" principle. The README was not aligned with this design.

- **FR-010:** The interactive menu "does NOT expose lifecycle commands (Create request, Close request)." The current README contradicts this by showing these commands as direct Python invocations.

- **Prompt-driven invocation model:** All `.py` script calls originate from prompt files that validate workspace state, enforce invariants, and handle errors. Direct user invocation of scripts bypasses these safety wrappers.

- **Evidence log:**

  | Evidence | Implication |
  | --- | --- |
  | `EXCLUDE_SCRIPTS` in `menu.py` hides `create-request.py` and `close-request.py` | Design intent: users should not invoke lifecycle scripts directly |
  | FR-010: menu does not expose lifecycle commands | README "Common Commands" section contradicts this requirement |
  | ADR-0003: `.aib_brain/` assets never written by tool scripts | README (a `.aib_brain/` asset) lags behind the architectural intent |
  | `aib-analysis.md` auto-creates requests from `input.md` | Users do not need to call `create-request.py` directly |

- **Files read:** As listed in Executive Summary.


---

## Research Results

- **Pattern scan — README vs. design intent contradiction:** The `menu.py` `EXCLUDE_SCRIPTS` constant and FR-010 both establish that lifecycle commands (`create-request.py`, `close-request.py`) should not be directly accessible to users. The README "Common Commands" section presents these as normal user commands, creating a contradiction between the product design and its documentation.

- **Pattern scan — `initialize.py` special status:** `initialize.py` is the sole script that runs before any Active request or `input.md` content exists. It is a prerequisite for the entire AIB workflow and must remain documented as a user-facing action — but specifically as the first-time setup step, not as a routine command.

- **Pattern scan — Daily flow over-specification:** The "Typical Daily Flow" in the current README names raw Python scripts in steps 1 and 5. The equivalent prompt-level flow (write to `input.md` → execute `aib-analysis.md` → execute `aib-implement.md`) is already documented below those steps but is not positioned as the primary path.

- **Pattern scan — No safety net for direct invocations:** `create-request.py` validates that no Active request exists before creating one, but a user who calls it directly while an Active request exists receives a CLI error without the context provided by the prompt workflow. The README implicitly encourages this path.


---

## External Benchmarking

- **Framework documentation for CLI tools (Nx, Turborepo, Angular CLI):** These tools distinguish between user-facing commands (e.g., `nx generate`, `ng serve`) and internal build scripts. Internal scripts are documented only in `CONTRIBUTING.md` or architecture guides, never in the end-user `README.md`.
  - Key takeaway: End-user READMEs should expose only the abstracted entry points; internal scripts belong in developer/contributor-level documentation.
  - Applicability: Directly applicable. `.aib_brain/README.md` should surface only the interactive menu and prompt invocations, not the internal `.py` scripts (except `initialize.py` as a first-time setup prerequisite).
  - Decision: Adopt this pattern — move script-level examples out of the end-user README.

- **Task-runner conventions (Make, just, Task):** Projects using task runners document only task names in user-facing docs, never the underlying shell commands. The abstraction is the contract; the implementation is hidden.
  - Key takeaway: User-facing documentation should reference the task/prompt abstraction, not the underlying command.
  - Applicability: Applicable. The AIB interactive menu (`run.bat`/`run.sh`) is the "task runner"; the README should point users to it and to prompt invocations, not to individual `.py` files.
  - Decision: Adopt this pattern — the interactive menu and prompt files are the documented user interface.


---

## Minimal Spikes and Experiments

No spike was required for this request.

- **Hypothesis: None to test** — The scope is confined to a single Markdown file (`README.md`). The change type is entirely editorial: content removal and addition of a warning note. There are no runtime dependencies, no state mutations, and no integration risks that require experimental validation. The feasibility and correctness of the change are self-evident from reading the file alongside `context.md` and `Concepts.md`.

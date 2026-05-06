## Goal

Create `.aib_memory/instructions.md` — a persistent, workspace-level instructions file for AIB that is read by every prompt in `.aib_brain/prompts/` independently of which prompt is executed. The file serves as workspace-specific behavioral directives that the AI must always observe, analogous to GitHub Copilot's `.github/copilot-instructions.md` but without requiring GitHub Copilot binding or any external dependency.

## Background

Currently, AIB has no mechanism for workspace-specific persistent instructions that apply across all prompt executions. Each prompt in `.aib_brain/prompts/` is self-contained and has no shared, always-loaded workspace context beyond the standard product docs in `references.md`.

GitHub Copilot's `.github/copilot-instructions.md` pattern demonstrates the value of a persistent instruction file: it allows teams to encode project-specific conventions, behavioral constraints, and directives that the AI must always respect — regardless of the specific task or prompt being executed.

AIB's architecture already separates framework assets (`.aib_brain/`) from workspace state (`.aib_memory/`), making `.aib_memory/instructions.md` the natural home for workspace-level directives. Users want these instructions to propagate automatically without needing to manually include them in each prompt invocation.

## Scope

- Create `.aib_memory/instructions.md` as an empty file — no preliminary content or template structure.

- Update every prompt in `.aib_brain/prompts/` (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) to include a mandatory pre-read step for `instructions.md` before executing the prompt's main logic. The step must be graceful: if the file is absent or empty, the prompt continues normally.

- Update `initialize.py` to seed `instructions.md` on workspace initialization if not already present (idempotent), conditional on resolution of Q001.

- Update `.aib_brain/README.md` to document `.aib_memory/instructions.md` — its purpose, location, and how users can populate it with workspace-specific directives.

- Update `.aib_memory/context.md` to document the new artifact and its role in the AIB lifecycle.

## Out of scope

- Integration with or dependency on GitHub Copilot's `.github/copilot-instructions.md`.

- Registering `.aib_memory/instructions.md` in `.aib_memory/references.md` — the file is intentionally excluded from the references registry.

- Creating a convention file for `instructions.md` (the file is intentionally free-form markdown; no schema enforcement is required).

- Modifying any `.aib_brain/conventions/` files.

- Multi-workspace coordination or cloud-based instruction management.

- Adding validation logic that enforces a specific structure within `instructions.md`.

## Constraints

- ADR-0003 applies: `.aib_brain/` MUST NOT be modified by tool scripts. Changes to `.aib_brain/prompts/` files are manual edits (performed by the AI agent acting in the developer role, not via tool scripts).

- The mechanism MUST NOT require GitHub Copilot binding or any external runtime dependency.

- `instructions.md` MUST reside in `.aib_memory/` (workspace-specific state), not in `.aib_brain/`.

- If `instructions.md` is absent or empty, all prompts MUST continue executing normally — no error, no halt.

- NFR-004: Any changes to tool scripts (`initialize.py`) must use Python 3.10+ standard library only.

- The file MUST be editable by users without requiring any tool invocation.

## Success criteria

1. `.aib_memory/instructions.md` exists after implementation as an empty file with no pre-populated content.

2. Every prompt file in `.aib_brain/prompts/` (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) contains a mandatory step to read `.aib_memory/instructions.md` and apply its content throughout the prompt's execution.

3. When `instructions.md` is absent or empty, no prompt produces an error — execution continues normally.

4. `initialize.py` seeds `instructions.md` on workspace initialization if not already present; re-running does not overwrite a manually populated file (conditional on Q001 resolution).

5. `.aib_memory/context.md` documents `instructions.md` in the Component Map and reflects its lifecycle role.

6. `.aib_brain/README.md` contains a section documenting `.aib_memory/instructions.md` — its purpose, location, and guidance on how to populate it.

## Assumptions

- A1: `instructions.md` is free-form Markdown with no enforced schema. Any content is valid; an empty file is treated as "no instructions."
  - Risk if false: If a schema is required, implementation must include a convention file and validation logic.

- A2: `initialize.py` should seed `instructions.md` only if it does not already exist (idempotent seeding). This assumption is pending confirmation via Q001.
  - Risk if false: Overwriting a user-populated file on re-initialization would cause data loss.

- A3: When `instructions.md` is absent or empty, prompts treat it as a no-op and continue executing normally without raising an error or halting.
  - Risk if false: Prompts would need explicit fallback error handling, adding complexity.

- A4: The modifications to `.aib_brain/prompts/` files are performed by the AI agent acting in the developer role (manual edits to framework asset files), not via tool scripts — consistent with ADR-0003.
  - Risk if false: Any tool-script modification of `.aib_brain/` would violate ADR-0003 and corrupt the upgrade boundary.

- A5: `instructions.md` is excluded from `references.md` by user directive. All prompts read it by explicit hardcoded path (`.aib_memory/instructions.md`), not via registry lookup.
  - Risk if false: If registry-gated access is required, a `references.md` row must be added and the read mechanism must change.

## Plan

### Task 1: Create `.aib_memory/instructions.md`
**Intent:** Create `instructions.md` as an empty file in `.aib_memory/` — no pre-populated content or template structure.
**Inputs:** None (new file).
**Outputs:** `.aib_memory/instructions.md`
**External Interfaces:** None.
**Environment & Configuration:** Standard file write.
**Procedure:**
1. Create `.aib_memory/instructions.md` as an empty file.
**Done Criteria:** `.aib_memory/instructions.md` exists and is empty (zero bytes or whitespace only).
**Dependencies:** None.
**Risk Notes:** None.

### Task 2: Update each prompt in `.aib_brain/prompts/` to include mandatory `instructions.md` pre-read
**Intent:** Ensure every prompt reads and applies `instructions.md` before executing its main logic.
**Inputs:** `.aib_brain/prompts/aib-analysis.md`, `.aib_brain/prompts/aib-implement.md`, `.aib_brain/prompts/aib-context.md`
**Outputs:** Updated prompt files.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. In each prompt file, immediately after the opening Goal/Input section (before the first execution step), insert a mandatory pre-read instruction: "Read `.aib_memory/instructions.md`. If the file exists and is non-empty, treat its content as persistent workspace-level instructions that MUST be observed throughout this prompt's execution. If the file is absent or empty, proceed normally."
2. Verify the inserted step does not alter any other logic in the prompt.
**Done Criteria:** All three prompt files contain the `instructions.md` pre-read step and the string `instructions.md` appears in each file.
**Dependencies:** Task 1.
**Risk Notes:** Edits to `.aib_brain/` files are manual developer-role changes — ADR-0003 applies.

### Task 3: Update `.aib_brain/README.md` to document `instructions.md`
**Intent:** Add a dedicated section in the README explaining the purpose of `.aib_memory/instructions.md`, how to use it, and best practices.
**Inputs:** `.aib_brain/README.md`
**Outputs:** `.aib_brain/README.md` (updated)
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Add a new section (e.g., `## Workspace Instructions`) to `.aib_brain/README.md` that covers: the file location (`.aib_memory/instructions.md`), its purpose (persistent workspace-level directives read by all prompts), examples of useful directive categories (coding conventions, naming rules, always/never behaviors), and an explicit warning not to store secrets or PII.
2. Confirm the section fits the existing README structure and tone.
**Done Criteria:** `.aib_brain/README.md` contains a section documenting `instructions.md` with purpose, usage guidance, and a security note.
**Dependencies:** Task 1.
**Risk Notes:** Edits to `.aib_brain/` files are manual developer-role changes — ADR-0003 applies.

### Task 4: Update `initialize.py` to seed `instructions.md` (conditional on Q001)
**Intent:** Seed an empty `instructions.md` during workspace initialization if not already present.
**Inputs:** `.aib_brain/tools/initialize.py`
**Outputs:** Updated `initialize.py`.
**External Interfaces:** Filesystem.
**Environment & Configuration:** Python 3.10+ standard library.
**Procedure:**
1. In `initialize.py`, add a block after existing file seeding logic: if `.aib_memory/instructions.md` does not exist, write it as an empty file.
2. Ensure the block uses an existence check (`Path.exists()`) to preserve idempotency.
**Done Criteria:** Running `initialize.py` on a fresh workspace creates an empty `instructions.md`; re-running on an existing workspace leaves the file unchanged.
**Dependencies:** Task 1; Q001 must be answered "Yes".
**Risk Notes:** If Q001 is answered "No", this task is skipped.

### Task 5: Write and run automated tests
**Intent:** Verify all testable Success Criteria with automated assertions.
**Inputs:** All files modified in Tasks 1–4; `tests/` directory.
**Outputs:** Passing test suite; updated `tests/` if new test cases are added.
**External Interfaces:** `pytest`.
**Environment & Configuration:** Python 3.10+, `.venv` active.
**Procedure:**
1. Assert `.aib_memory/instructions.md` exists and is empty (SC-1).
2. Assert each prompt file contains the string `instructions.md` in a mandatory-read context (SC-2).
3. If Task 4 executed: run `initialize.py` on a temp directory and assert `instructions.md` is created as an empty file; re-run and assert content unchanged (SC-4).
4. Assert `.aib_brain/README.md` contains a reference to `instructions.md` (SC-6).
5. Run `pytest tests/` and confirm zero failures.
**Done Criteria:** All assertions pass; `pytest` exits with code 0.
**Dependencies:** Tasks 1–4.
**Risk Notes:** None.

### Task 6: Update `context.md` and documentation
**Intent:** Reflect the new `instructions.md` artifact in `context.md` to ensure workspace documentation is current.
**Inputs:** `.aib_memory/context.md`, `.aib_memory/references.md`.
**Outputs:** Updated `.aib_memory/context.md`.
**External Interfaces:** None.
**Environment & Configuration:** None.
**Procedure:**
1. Execute `aib-context.md` prompt to fully replace `context.md` with updated content, reflecting `instructions.md` in the Component Map, Architecture sections, and functional requirements.
2. Verify the resulting `context.md` references `instructions.md` in the Component Map and AIB lifecycle description.
**Done Criteria:** `context.md` documents `.aib_memory/instructions.md` as a named component; the lifecycle description reflects the persistent instructions mechanism.
**Dependencies:** Tasks 1–4.
**Risk Notes:** None.

## Documentation

- `.aib_memory/context.md` (ref_id: REF-0001) — update Component Map to document `.aib_memory/instructions.md`; update lifecycle description to reflect the persistent instructions mechanism; update FR list to include the new behavior.

- `.aib_brain/README.md` (ref_id: N/A) — add section documenting `instructions.md` purpose, usage, and security guidance.

## Questions & Decisions

**Q001**: Should `initialize.py` be updated to seed `.aib_memory/instructions.md` on workspace initialization?
- [ ] Option A: Yes — `initialize.py` seeds `instructions.md` if not already present (idempotent; does not overwrite existing content). *(recommended)*
- [ ] Option B: No — `instructions.md` is created only as a one-time implementation artifact; `initialize.py` is not modified.
- [ ] Other: ___
> Answer: 

## Code and Asset Scan for Impacted Components

| File/Asset | Change Type | Reason |
| --- | --- | --- |
| `.aib_memory/instructions.md` | Created | New persistent workspace instructions file — the primary deliverable of this request. Empty on creation. |
| `.aib_brain/prompts/aib-analysis.md` | Modified | Add mandatory pre-read step for `instructions.md`. |
| `.aib_brain/prompts/aib-implement.md` | Modified | Add mandatory pre-read step for `instructions.md`. |
| `.aib_brain/prompts/aib-context.md` | Modified | Add mandatory pre-read step for `instructions.md`. |
| `.aib_brain/README.md` | Modified | Add section documenting `instructions.md` purpose, usage, and security guidance. |
| `.aib_brain/tools/initialize.py` | Modified | Add idempotent seeding of empty `instructions.md` (conditional on Q001). |
| `.aib_memory/context.md` | Modified | Update Component Map and lifecycle description to reflect `instructions.md`. |
| `tests/` | Modified | Add automated assertions for Success Criteria 1–6. |

## Internal Review of Request and Product Docs

- OK: `request.md` — All 12 mandatory sections are present and sections 1–6 are non-empty. Section order matches the convention.

- OK: `references.md` — Current schema is valid. REF-0001 and REF-0002 are well-formed. `instructions.md` is explicitly excluded from this registry by user directive; no new row is needed.

- OK: `context.md` — Does not yet reference `instructions.md`; this is expected since the file does not exist yet. The update is planned in Task 6.

- Missing info: `context.md` FR list — The functional requirements section does not yet include a requirement for the persistent workspace instructions mechanism. Task 6 (context update) will address this.

- OK: ADR-0003 — All planned changes to `.aib_brain/` files are manual developer-role edits, not tool script changes. No violation.

- OK: ADR-0005 — `input.md` is the ephemeral communication channel; `instructions.md` is the persistent complement. The two concepts are architecturally complementary and non-conflicting.

- OK: NFR-004 — `initialize.py` change (Task 4) uses standard library only (`pathlib.Path.exists()`, standard file write). No new dependencies.

- RESOLVED: User directive excludes `instructions.md` from `references.md` — applied to Scope, Out of scope, Success criteria, Plan, and Code and Asset Scan sections.

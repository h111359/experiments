# Analysis — R-20260421-1705: Add instructions.md for persistent AIB directives

## Executive Summary

- **Request ID:** R-20260421-1705

- **Title:** Add instructions.md for persistent AIB directives

- **Purpose:** Introduce `.aib_memory/instructions.md` as a persistent, workspace-level instruction file that is read by every AIB prompt before executing its main logic, enabling teams to encode project-specific behavioral directives that are always observed — regardless of which prompt is invoked.

- **Motivation:** AIB currently has no mechanism for workspace-global persistent instructions. Each prompt is self-contained. The GitHub Copilot `.github/copilot-instructions.md` pattern demonstrates how powerful this capability is: a single file whose content is unconditionally injected into every AI interaction. This request brings an equivalent pattern to AIB without any external dependency.

- **Amendments applied in this run:** Three user-provided directives from `input.md` were incorporated as scope amendments: (1) `instructions.md` MUST NOT be registered in `references.md`; (2) `instructions.md` MUST be seeded as an empty file with no preliminary content; (3) `.aib_brain/README.md` must be updated to document how `instructions.md` is used.

- **Scope summary (updated):** Create an empty `instructions.md` in `.aib_memory/`; add a mandatory pre-read step to all three prompts in `.aib_brain/prompts/`; update `.aib_brain/README.md` to document the file's purpose and usage; conditionally seed via `initialize.py`; update `context.md`.

- **`request.md` sections added/updated in this run:** `## Scope`, `## Out of scope`, `## Success criteria`, `## Assumptions`, `## Plan`, `## Documentation`, `## Questions & Decisions`, `## Code and Asset Scan for Impacted Components`, `## Internal Review of Request and Product Docs`.

- **Open questions:** Q001 (whether `initialize.py` should seed `instructions.md`) remains open for user decision. All other decision points resolved autonomously (below threshold or deterministic).

- **Risk posture:** Low. The change is additive and purely file-based. Prompts degrade gracefully when the file is absent or empty.


## Domain Knowledge Essentials

**Workspace-level instructions:** Custom, persistent behavioral guidelines that an AI agent applies unconditionally across all interactions within a defined scope (e.g., a repository workspace). These instructions encode project-specific conventions, team standards, and mandatory behavioral constraints.

**AIB (AI Builder):** A minimal, model-agnostic framework for specification-driven development. AIB organizes work as structured requests, uses convention files to enforce document quality, and exposes prompt files that drive AI agent behavior.

**AIB Prompt:** A Markdown file in `.aib_brain/prompts/` that defines a specific AIB action (e.g., `aib-analysis.md`, `aib-implement.md`, `aib-context.md`). Prompts are invoked directly in an AI coding interface and contain deterministic execution instructions.

**`.aib_brain/`:** The framework assets folder. Contains reusable prompts, conventions, templates, and tool scripts. Must never be modified by tool scripts (ADR-0003). AIB Maintainers replace it on framework upgrade.

**`.aib_memory/`:** The workspace-specific state folder. Contains all persistent artifacts: requests, `context.md`, `input.md`, `references.md`, and all request folders. Persists across framework upgrades.

**`references.md`:** A registry table in `.aib_memory/` that lists all files referenced by AIB, their types, and whether automation is permitted to edit them (`edit_allowed`). `instructions.md` is explicitly excluded from this registry by user directive; prompts access it by hardcoded path.

**`initialize.py`:** The tool script that seeds `.aib_memory/` on first workspace setup. Currently creates: `requests_register.md`, `references.md`, `context.md`, `input.md`, and the `requests/` and `logs/` subdirectories.

**Impacted roles:**

- Developer — writes workspace instructions into `instructions.md`; benefits from consistent AI behavior across all prompts.

- AI Automation Agent — reads and applies `instructions.md` at the start of every prompt execution.

- AIB Maintainer — may document the instructions mechanism in `.aib_brain/` conventions on framework upgrade.

**Business process touched:** Communicate user intent (the developer sets persistent context before invoking any prompt). Augments the existing `input.md` ephemeral channel with a persistent complement.

**Acceptance impact:** Increases consistency of AI behavior across prompt invocations without adding user ceremony; the file is read-once per prompt run with graceful fallback on absence.


## Technical Knowledge & Terms

**`copilot-instructions.md`:** A file placed at `.github/copilot-instructions.md` that GitHub Copilot injects as persistent context into every chat interaction in the repository. It is model-aware and automatically applied, requiring no per-prompt configuration. This is the direct architectural analogue for `instructions.md` in AIB.

**`.cursorrules`:** A workspace-level rules file used by the Cursor AI editor to inject persistent behavioral directives into all AI interactions. Same pattern; different vendor.

**Graceful degradation:** A design property ensuring that the system continues functioning correctly when an optional resource (here, `instructions.md`) is absent or empty. Required for this feature to remain non-breaking.

**Idempotent seeding:** Writing a file during initialization only if it does not already exist, ensuring re-running `initialize.py` does not overwrite user content.

**Pre-read step:** An explicit instruction in a prompt directing the AI to read a specific file before proceeding with the main logic. The content of the read file is then treated as persistent context for the entire prompt execution.

**Hardcoded path access:** Reading a file by its fixed workspace-relative path (`.aib_memory/instructions.md`) rather than by a registry lookup. Since `instructions.md` is excluded from `references.md`, all prompts must reference it by explicit path. This is a stable, low-risk coupling given the file's fixed location.

**Empty-file seed:** A seeding strategy where the initial file contains no content. The user is expected to populate it based on their needs. This maximizes freedom but reduces in-file discoverability. The AIB README becomes the primary documentation surface.

**Files read during analysis:**

- `.aib_memory/input.md` — source of request amendments and intent.
- `.aib_memory/requests_register.md` — active request resolution.
- `.aib_memory/references.md` — product-doc registry.
- `.aib_memory/context.md` — unified workspace context (REF-0001).
- `.aib_brain/Concepts.md` — AIB domain concepts (REF-0002).
- `.aib_brain/conventions/analysis-convention.md` — analysis structure convention.
- `.aib_brain/conventions/request-convention.md` — request structure convention.
- `.aib_brain/prompts/aib-analysis.md`, `aib-implement.md`, `aib-context.md` — prompt files to be modified.
- `.aib_brain/README.md` — user-facing workspace guide to be updated.
- `.aib_brain/tools/initialize.py` — seeding script examined for pattern consistency.

**Non-functional implications:**

- Reliability: Graceful fallback on absent/empty file ensures no regression to existing workflows.
- Security: `instructions.md` is a local Markdown file. No secrets should be stored in it; it is visible in VCS. No attack surface increase beyond existing workspace access. Excluding from `references.md` (no `edit_allowed = Y`) means no automation path writes to the file.
- Performance: One additional file read per prompt invocation — negligible.
- Operations: Standard workspace file; no deployment or configuration changes required.

**Evidence log:**

| Evidence | Implication |
| --- | --- |
| `initialize.py` uses `Path.exists()` guards for all seeded files | Adding empty `instructions.md` seeding follows the identical idempotent pattern |
| ADR-0003: `.aib_brain/` must not be modified by tool scripts | Prompt file edits are manual developer-role changes, not tool script changes |
| User directive: `instructions.md` MUST NOT be in `references.md` | No register row is created; all prompts read the file by explicit path only |
| User directive: empty file seed | No template structure is needed; README becomes the primary usage guide |
| Context.md documents `input.md` as ephemeral | `instructions.md` is the persistent complement; documented distinction is important |
| `.aib_brain/README.md` has no workspace customization section | New `## Workspace Instructions` section is the appropriate addition |


## Research Results

**Pattern scan — existing AIB prompts:**

- All three prompts (`aib-analysis.md`, `aib-implement.md`, `aib-context.md`) have distinct "Inputs" or "Input resolution" sections at the top.

- None currently reference a shared persistent instruction source.

- The addition of a mandatory pre-read step for `instructions.md` is structurally uniform and does not conflict with any existing logic in any of the three prompts.

- `aib-context.md` has an explicit non-goal: "Do not add entries to `.aib_memory/references.md`." The `instructions.md` pre-read step only reads the file — no registry entry is added. No conflict.

**Pattern scan — `initialize.py` seeding logic:**

- Currently seeds: `requests_register.md`, `references.md`, `context.md`, `input.md`, `requests/` folder, `logs/` folder.

- Uses `exist_ok=True` for directories and conditional write guards for files (does not overwrite if already present — idempotent pattern).

- Adding empty `instructions.md` seeding follows the identical idempotent pattern with no new dependencies.

**Pattern scan — `references.md` schema:**

- Current entries: REF-0001 (`context.md`, `product-doc`, `edit_allowed = Y`) and REF-0002 (`Concepts.md`, `domain`, `edit_allowed = N`).

- By user directive, `instructions.md` is excluded from this registry. No new row is needed. Prompts access the file by explicit hardcoded path.

**Pattern scan — `.aib_brain/README.md`:**

- The README covers Quick Start, Typical Daily Flow, Use Case Scenarios, and Troubleshooting. It has no section for workspace customization or persistent instructions.

- A new section (e.g., `## Workspace Instructions`) documenting `instructions.md`, its purpose, and how to use it would follow the existing structural and tone pattern of the README.


## External Benchmarking

**Benchmark 1 — GitHub Copilot `copilot-instructions.md`**

- Pattern: A single Markdown file at `.github/copilot-instructions.md` that GitHub Copilot automatically reads and applies as persistent context for every chat interaction in the repository.

- Key takeaways:
  - Free-form Markdown content is sufficient; no schema enforcement is needed.
  - The file is loaded unconditionally by the AI tool, not by user action.
  - The pattern is universally applicable: instructions survive across sessions, teammates, and task types.
  - GitHub's documentation (not the file itself) is the primary source of user guidance on what to write — the file starts empty; discovery is documentation-driven.

- Applicability: High. AIB's `instructions.md` mirrors this pattern at the prompt level. The empty-file-with-README-documentation approach exactly matches the Copilot pattern.

- Adoption decision: Adapt — use the same free-form Markdown format and the "read unconditionally at prompt start" behavior. Empty initial state matches the Copilot pattern exactly. Reject the platform-binding aspect; AIB's approach is vendor-agnostic.

**Benchmark 2 — Cursor AI `.cursorrules`**

- Pattern: A workspace-root file (`.cursorrules`) that the Cursor editor injects as persistent behavioral context into all AI completions and chat interactions within the workspace.

- Key takeaways:
  - Teams use it for coding standards, naming conventions, language preferences, and safety constraints.
  - The file is typically short (< 100 lines) and written in plain prose or bullet lists.
  - Cursor's documentation (not the file itself) explains what to put in it — documentation-driven adoption, not template-driven.

- Applicability: High for the concept; the empty-file-with-documentation approach aligns with Cursor's established pattern.

- Adoption decision: Adapt the concept (free-form persistent workspace rules); README documentation replaces any template.

**Benchmark 3 — OpenAI Custom Instructions (ChatGPT)**

- Pattern: Per-user persistent instructions stored in ChatGPT settings and injected into every conversation. Covers "what should ChatGPT know about you" and "how should ChatGPT respond."

- Key takeaways:
  - Persistent instructions dramatically improve consistency across sessions.
  - User-editable, not schema-enforced.
  - Instructions are surfaced through UI guidance, not a built-in template — documentation-driven adoption is the established pattern for this type of feature.

- Applicability: Medium. The per-user scope differs from AIB's per-workspace scope, but confirms that documentation-driven adoption (not template-driven) is the right approach. No direct adoption required.


## Minimal Spikes and Experiments

No spike was conducted. The mechanism (add a mandatory pre-read step to each prompt file) is a simple, well-understood file-injection pattern with no technical uncertainty. The feasibility is confirmed by the existing structure of all three prompt files, which already contain explicit "Inputs" and "Input resolution" sections where the additional step fits naturally. Graceful fallback on absence is a standard prompt instruction pattern — no experiment needed to validate it. The empty-file seeding pattern is already established in `initialize.py` (e.g., `context.md` is seeded as a minimal stub). No novel uncertainty exists.


## AI Copilot Suggestions

**Observation 1 — Discoverability risk of an empty seed file**

The user has explicitly chosen an empty file (no template or placeholder content). While this maximizes freedom, it creates a discoverability gap: a developer encountering `.aib_memory/instructions.md` for the first time has no in-file guidance about what to write. The README update (now in scope) becomes the sole documentation surface, making its quality critical for adoption.

- Suggestion: Ensure the README section for `instructions.md` is comprehensive — cover purpose, format (free-form Markdown), concrete examples of useful directive categories (coding conventions, naming rules, always/never behaviors, response format preferences), and an explicit warning against storing secrets or PII. The README section quality directly determines how quickly and correctly developers adopt the feature.

**Observation 2 — Prompt modification consistency risk**

Adding a pre-read step to three separate prompt files creates a maintenance surface: if a fourth prompt is added to `.aib_brain/prompts/` in the future, it may not include the `instructions.md` step, silently breaking the "always observed" guarantee. The request does not address this forward-compatibility risk.

- Suggestion: Add a normative rule to `Concepts.md` or a convention file stating that all future prompts MUST include a mandatory `instructions.md` pre-read step. This converts a local implementation detail into a durable framework convention, reducing the risk of accidental omission.

**Observation 3 — Exclusion from `references.md` creates an implicit read contract**

By excluding `instructions.md` from `references.md`, prompts access it outside the standard registry-gated mechanism. This is intentional (user directive), but it means the constraint "prompts only read it, never write it" is enforced only by convention — no `edit_allowed` gate applies.

- Suggestion: Document explicitly in the README and in the prompts' pre-read step that `instructions.md` is a read-only input for all AIB prompts — it is populated only by the developer, never overwritten by automation. This makes the implicit contract explicit and durable.

**Observation 4 — Scope note**

The scope is appropriately sized for the stated goal. The three amendments applied in this run (exclude from `references.md`, empty file, README update) are internally consistent and produce a simpler, cleaner design than the previous iteration. The `initialize.py` seeding question (Q001) remains the only open variable. There is no scope creep risk.


## Testing

- T1 — File existence: Verify `.aib_memory/instructions.md` exists after implementation. Expected outcome: file is present at the expected path.

- T2 — Empty seed state: Verify `.aib_memory/instructions.md` is empty or contains only whitespace after initial seeding (no pre-populated content). Expected outcome: file content is empty or whitespace-only.

- T3 — Prompt inclusion (analysis): Verify `.aib_brain/prompts/aib-analysis.md` contains a reference to `.aib_memory/instructions.md` in a mandatory-read context. Expected outcome: the string `instructions.md` appears in the file with a mandatory-read instruction.

- T4 — Prompt inclusion (implement): Verify `.aib_brain/prompts/aib-implement.md` contains a reference to `.aib_memory/instructions.md` in a mandatory-read context. Expected outcome: the string `instructions.md` appears in the file.

- T5 — Prompt inclusion (context): Verify `.aib_brain/prompts/aib-context.md` contains a reference to `.aib_memory/instructions.md` in a mandatory-read context. Expected outcome: the string `instructions.md` appears in the file.

- T6 — README documentation: Verify `.aib_brain/README.md` contains a section documenting `instructions.md` — its purpose, location, and how to use it. Expected outcome: the string `instructions.md` appears in a dedicated section of the README.

- T7 — Not registered in references.md: Verify `.aib_memory/references.md` does NOT contain a row for `instructions.md`. Expected outcome: no row with path `.aib_memory/instructions.md` exists in the table.

- T8 — Graceful degradation: Rename or remove `instructions.md` and trigger a prompt execution. Expected outcome: no error is raised; prompt executes normally. (See UAT_scenarios.md — UAT-01)

- T9 — Initialize seeding (conditional on Q001): Run `initialize.py` on a fresh workspace (without `instructions.md`). Expected outcome: `instructions.md` is created as an empty file.

- T10 — Initialize idempotency (conditional on Q001): Run `initialize.py` again on the same workspace with manually modified `instructions.md`. Expected outcome: file content is unchanged; no overwrite occurs.

- T11 — Re-run idempotency: Execute the implementation tasks again with unchanged inputs. Expected outcome: all files converge to the same content; no duplicate entries or formatting regressions.

- T12 — Test suite: Run `pytest tests/` after implementation. Expected outcome: all existing tests pass with zero failures.


## Multi-Perspective Stakeholder Review

### Senior Solution Architect

This request introduces a well-established pattern (persistent workspace instructions) in a way that is architecturally consistent with AIB's existing design. The separation between `.aib_brain/` (framework) and `.aib_memory/` (workspace state) is preserved; `instructions.md` correctly belongs in `.aib_memory/`. The graceful degradation requirement eliminates backward-compatibility risk. The decision to exclude `instructions.md` from `references.md` simplifies the registry but creates an implicit read contract — prompts access the file by hardcoded path — that must be consistently implemented across all three prompt files. This coupling is acceptable given the file's stable, well-defined location. The README update correctly provides the missing documentation surface.

- The additive, file-read-only mechanism has zero impact on existing prompt behavior when `instructions.md` is absent.
- Excluding from `references.md` simplifies the registry; the hardcoded path is a stable, low-risk coupling.
- Prompt modification consistency risk is the most significant long-term architectural concern; a normative rule in `Concepts.md` would mitigate it permanently.
- No inter-component protocol changes, API surface changes, or data model changes are required.

### Product Owner

This feature delivers direct value to developer users: workspace-specific AI behavioral constraints that persist across all prompt invocations without any per-invocation ceremony. The decision to use an empty seed file shifts the documentation burden to the README, which is now in scope — this is an appropriate trade-off that avoids prescribing structure. The acceptance criteria are clear and testable.

- Business value is high relative to implementation effort: three prompt file edits, one new empty file, one README section, and optionally one script update.
- The acceptance criteria cover all significant behaviors and are verifiable.
- The Q001 question (initialize seeding) should be resolved before implementation to avoid a follow-up request.
- No risk to existing product behavior; the change is purely additive.

### User

From the developer's perspective, this feature eliminates a friction point: the need to manually remind the AI of project-specific conventions at the start of each prompt invocation. The empty-file approach gives full freedom to structure the content as needed. The README becomes the primary discovery surface — its quality determines how quickly developers understand and adopt the feature. The absence of an in-file template is offset by the README documentation.

- The file is easy to find (in `.aib_memory/`, alongside other familiar artifacts).
- No new command or workflow step is required to activate the feature — it is always on.
- Graceful degradation means there is no risk of breaking existing workflows if the file is accidentally deleted.
- The README section must be comprehensive; without it, the feature is invisible to new users.

### Security Officer

The `instructions.md` file is a local Markdown file read during prompt execution. It introduces no new network communication, authentication surface, or external dependency. Excluding it from `references.md` (no `edit_allowed = Y`) means no automation path writes to the file — this is actually a security improvement over the previous design iteration. The file is part of the repository and visible to anyone with repository read access.

- No attack surface increase beyond existing file-read operations.
- No authentication or authorization changes required.
- The file is not executed — it is read and its content is treated as text context. No code injection risk.
- Excluding from `references.md` means no automation path writes to the file — minimizes risk of automated content tampering.
- The README section must include an explicit warning against storing secrets or credentials in `instructions.md`.

### Data Governance Officer

`instructions.md` contains free-form text authored by the developer. It is classified as Internal engineering documentation (same classification as all `.aib_memory/` artifacts). It is committed to the repository and subject to standard VCS retention and access controls. No personally identifiable information (PII) is expected or should be stored in this file.

- Data classification: Internal engineering documentation. No change to existing classification framework.
- Retention: governed by repository VCS retention policy (same as all `.aib_brain/` and `.aib_memory/` artifacts).
- Lineage: authored by the developer; read by AI prompts; not transmitted to external systems.
- Compliance: no regulatory impact identified. No data processing, transformation, or external transfer occurs.
- Recommendation: README section should discourage storage of PII, secrets, or sensitive configuration data in `instructions.md`.

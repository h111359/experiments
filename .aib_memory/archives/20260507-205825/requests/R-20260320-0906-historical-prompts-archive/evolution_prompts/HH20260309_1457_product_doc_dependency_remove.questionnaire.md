# Questionnaire for HH20260309_1457_product_doc_dependency_remove.md

Analyze `evolution_prompts/HH20260309_1457_product_doc_dependency_remove.md` and provide clarifying questions/options for implementation choices.

---

## Q1 — Desired runtime behavior when Product_Documentation.md exists
- Explanation: Decide whether `Product_Documentation.md` should ever influence runtime, or only the new seeded `references-template.md`.
- Options:
- [x] A: Always ignore `Product_Documentation.md` at runtime (never read it).
- [ ] B: Use `references-template.md` as the default but allow `Product_Documentation.md` to override when present. (Recommended)
- [ ] C: Only consult `Product_Documentation.md` in interactive/diagnostic sessions, not in normal execution.

## Q2 — Where to store the default document locations
- Explanation: Determine the authoritative place for default file locations used for seeding.
- Options:
- [x] A: Embed default locations directly inside `.aib_brain/templates/references-template.md` (as requested in the objective). (Recommended)
- [ ] B: Keep defaults in a separate config file (e.g., `.aib_brain/config/defaults.yaml|json`) and have the template read that config.
- [ ] C: Define defaults as code constants in `.aib_brain/tools/*` and generate the template at init time.

## Q3 — Path format for default locations
- Explanation: Decide how paths should be expressed so they work reliably across environments.
- Options:
- [x] A: Repository-relative paths (recommended: use `pathlib`/POSIX-style internally and resolve at runtime). (Recommended)
- [ ] B: Absolute filesystem paths.
- [ ] C: URIs (e.g., `file://` or `http://`) for remote-hosted documents.

## Q4 — When and how to seed `references-template.md`
- Explanation: Choose the timing and mechanism for writing/updating the template with defaults.
- Options:
- [ ] A: Seed once during initialization (first-run of `.aib_brain/tools/initialize.py`). (Recommended)
- [ ] B: Ensure seeding happens whenever the template is missing or empty (idempotent on startup).
- [ ] C: Provide an explicit CLI/subcommand to regenerate the template (manual control).
- [x] Other: Generate now and let AIB human developers to change it manually

## Q5 — Fallback and override strategy
- Explanation: Define what happens if the expected documents are missing and whether overrides are allowed.
- Options:
- [ ] A: If a referenced document is missing, log a warning and continue with defaults/empty placeholders. (Recommended)
- [ ] B: Treat missing documents as errors and abort execution.
- [ ] C: Allow an environment variable or runtime flag to enable strict mode (error) vs permissive mode (warn).
- [x] D: The template will be used only diring initialization. During initialization all the docs will be created. No need of verificaiton

## Q6 — Backward compatibility and migration
- Explanation: Decide whether to provide an automated migration to remove dynamic dependencies and update templates in existing repos.
- Options:
- [ ] A: Add a migration script that updates `references-template.md` and adjusts code to stop dynamic loading (safe, automated). (Recommended)
- [x] B: Provide manual migration instructions in the README and let maintainers opt-in.
- [ ] C: Make the change only in new installations without migration for existing repos.

## Q7 — Scope of code changes to remove dependency
- Explanation: Confirm which files must be updated and whether to run a wider search for other dependencies.
- Options:
- [ ] A: Update `.aib_brain/tools/initialize.py`, `.aib_brain/tools/common.py`, and `.aib_brain/templates/references-template.md` only.
- [x] B: Update the above and perform a repository-wide search for any other modules that read `Product_Documentation.md`, updating them too. (Recommended)
- [ ] C: Keep changes minimal to the two files and add warnings elsewhere without modifying other modules.

## Q8 — Tests and CI validation
- Explanation: Define testing strategy to ensure `Product_Documentation.md` is not required for execution.
- Options:
- [x] A: Add unit tests asserting that initialization and common operations succeed without `Product_Documentation.md`. (Recommended)
- [ ] B: Add integration tests that simulate missing docs and validate fallback behavior.
- [ ] C: Rely on manual QA and code review only.

## Q9 — Cross-platform path handling
- Explanation: Ensure path handling works across Windows, Linux, and macOS.
- Options:
- [x] A: Use Python `pathlib` exclusively for path operations and normalization. (Recommended)
- [ ] B: Use manual string-based paths with `os.path` and platform checks.
- [ ] C: Hardcode platform-specific paths where necessary.

## Q10 — Logging and user feedback
- Explanation: Choose the verbosity and user-visible notifications when the system falls back to defaults.
- Options:
- [ ] A: Emit clear warnings in logs and continue (non-fatal). (Recommended)
- [ ] B: Emit informational logs only (no warnings), to avoid noise.
- [ ] C: Raise exceptions for any fallback to force attention.
- [x] D: The initialization should be strigh forward, no need of that

## Q11 — Removal vs retention of `Product_Documentation.md` file in repo
- Explanation: Decide whether to delete, archive, or keep the file in the repository after the change.
- Options:
- [x] A: Keep the file in the repo but stop reading it (retained for historical/reference). (Recommended)
- [ ] B: Remove the file from new templates/boilerplate to avoid confusion.
- [ ] C: Move it to an `archive/` location and update docs accordingly.

## Q12 — Approval to proceed with implementation changes and PR
- Explanation: Confirm whether you want me to implement the change (code edits, tests, migration script) and open a PR.
- Options:
- [ ] A: Yes — implement the changes, run tests, and prepare a PR. (If chosen, please confirm branch naming preference.)
- [x] B: Yes — but only generate a patch and instructions, not a PR.
- [ ] C: No — I will provide implementation guidance only.

---

If you confirm answers (check options), I'll proceed to: search the repo for any other usages of `Product_Documentation.md`, update the `initialize.py` and `common.py` to stop dynamic loads, seed `references-template.md` with the chosen defaults, add tests, and prepare a migration script/PR as agreed.

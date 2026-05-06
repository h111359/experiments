# Analysis: R-20260416-1322 — Simplify Root README

## Executive Summary

- **Request ID:** R-20260416-1322

- **Title:** readme-in-root

- **High-level purpose:** The root `README.md` currently mixes two concerns — a simple onboarding entry point (overview, installation) and detailed technical CI/release-bookkeeping documentation. The request asks to strip technical details from the root file, leaving only a minimal orientation document, and confirms that the removed content already belongs in `.aib_memory/context.md` and `.aib_brain/Concepts.md`.

- **Scope of the analysis run:** The root `README.md` content was reviewed and classified into "keep" and "remove" buckets. `context.md` was checked to confirm the CI workflow details are already synthesized there. The edit-allowed status of all affected files was verified against `references.md`. A1 (CI details already in `context.md`) has been verified true and is no longer an open assumption.

- **A1 verification result:** Confirmed. `context.md` contains the Release Bookkeeping Script component, GitHub Actions Workflow component, ADR-0004 (pre-merge CI write model), ALG-0001 (SemVer patch bump algorithm), SEQ-003 (CI release bookkeeping sequence), Operations > Deployment (Actions permissions setup), and Security > Access Control (GITHUB_TOKEN permissions). No information loss occurs from removing the CI section in `README.md`.

- **Impact on `request.md` this run:** Preamble note above `## Goal` removed (A1 is now confirmed). Assumptions section updated (A1 removed as confirmed; A2 retained). Plan, Testing, and Documentation sections fully replaced with refined content.

---

## Domain Knowledge Essentials

**Business terminology:**

- **Root README.md** — the top-level file displayed by GitHub on the repository landing page; conventionally the first document a new contributor reads. Its primary audience is an onboarding developer, not an advanced operator.

- **AIB (AI Builder)** — a minimal, model-agnostic framework for specification-driven development living in `.aib_brain/`. It orchestrates request lifecycles, analysis, implementation, and release bookkeeping via AI prompt workflows.

- **`.aib_brain/README.md`** — the operator's field guide for daily AIB use: workflow steps, prompt invocation examples, command-line instructions, troubleshooting tips.

- **`.aib_brain/Concepts.md`** — authoritative domain reference defining AIB goals, objectives, concepts, invocation contracts, and lifecycle rules. Owned by the AIB Maintainer; `edit_allowed = N`.

- **`.aib_memory/context.md`** — auto-generated product-knowledge synthesis, fully replaced by `aib-context.md` on each execution. Acts as the AI's working memory for the workspace. `edit_allowed = Y`.

**Impacted roles/personas:**

- Developer (onboarding) — currently confronted with detailed CI workflow documentation in the root README, which is not relevant at the start.

- AIB Maintainer — owns `Concepts.md` and will not receive a request to edit it through this workflow (edit_allowed = N).

**Business processes touched:**

- Developer onboarding — improved by a leaner README.

- Documentation maintenance — fewer places to keep CI workflow content in sync.

**Acceptance impact:** A reader arriving at the repository should be able to install AIB and be pointed to further reading in three conceptual steps: what is it, how to install, where to read more.

---

## Technical Knowledge & Terms

**Technologies and components:**

- **GitHub Markdown rendering** — GitHub renders the root `README.md` automatically on the repository landing page. Only standard GitHub Markdown is supported; no HTML or embedded diagrams.

- **GitHub Actions CI workflow** (`.github/workflows/aib-semver-patch-bump-and-log.yml`) — automates patch-version bumping and per-version log creation on PR events targeting `main`. This is the technical subject of the section currently in `README.md`.

- **SemVer marker file** — a single empty file in `.aib_brain/` named `vMAJOR.MINOR.PATCH` that encodes the current version without a package manager.

- **`references.md`** — the AIB edit-permission register. Files with `edit_allowed = N` MUST NOT be written by the implement workflow.

- **`context.md` synthesis** — `aib-context.md` reads all workspace sources (including the GitHub Actions workflow YAML, `release_bookkeeping.py`, and `Concepts.md`) and synthesizes them into `context.md`. CI operational details are therefore already captured there without manual duplication.

**Data and runtime constraints:**

- `context.md` is fully replaced on each `aib-context.md` execution; any manually inserted content would be overwritten.

- `Concepts.md` is `edit_allowed = N`; the implement workflow cannot write to it.

- Root `README.md` is not listed in `references.md`. Editing it is not gated by the register but is explicitly requested by the user.

**Non-functional attributes:**

- Reliability: removing one of two copies of CI workflow documentation eliminates a documentation drift risk.

- Maintainability: a shorter root README has a smaller maintenance surface.

**Evidence log:**

| Evidence | Implication |
| --- | --- |
| `README.md` contains a 50+ line "Automated version bump & release log (Issue #17)" section | This is the content to remove |
| `context.md` Architecture section includes Release Bookkeeping Script, GitHub Actions Workflow, and ADR-0004 | CI workflow details are already preserved in the auto-generated knowledge base |
| `references.md` lists `Concepts.md` as `edit_allowed = N` | The implement workflow cannot add content to `Concepts.md` |
| `references.md` does not list root `README.md` | No explicit edit-permission entry; user request serves as explicit authorisation |
| `.aib_brain/README.md` covers daily workflow, prompt invocations, and troubleshooting | Sufficient "where to read more" destination for the root README pointer |

**Files read:**

- `.aib_memory/requests/R-20260416-1322-readme-in-root/request.md`
- `.aib_memory/references.md`
- `.aib_memory/context.md`
- `.aib_brain/Concepts.md`
- `.aib_brain/README.md`
- `README.md`
- `.aib_brain/conventions/analysis-convention.md`
- `.aib_brain/conventions/request-convention.md`

---

## Research Results

### 1. Internal review of request and referenced docs

The request goal is clear: simplify the root `README.md` by removing technical content and keeping only installation orientation with a pointer to `.aib_brain/README.md`.

**A1 verification — CI workflow details in `context.md`:**

The following content from the `README.md` "Automated version bump & release log" section is confirmed present in `context.md`:

| README.md content | Equivalent in `context.md` |
| --- | --- |
| What the workflow does (validate marker, bump PATCH, rotate file, create log) | ALG-0001 — SemVer Patch Bump; Component Map rows for Release Bookkeeping Script and GitHub Actions Workflow |
| When it runs (PR events: opened, reopened, synchronize) | SEQ-003 — Release bookkeeping in CI |
| Pre-merge write model (commits back to PR branch before merge) | ADR-0004 — Pre-merge CI write model for release bookkeeping |
| Repository setup requirements (enable Actions; Read/Write GITHUB_TOKEN) | Operations > Deployment; Security > Access Control |
| Operational behavior (marker validation failure handling, push failure, log-file conflict) | ALG-0001 idempotency clause; ADR-0004 consequences |
| Fork PR exclusion for security | ADR-0004 consequences; Security > Access Control |

**Conclusion:** A1 is confirmed true. No information is lost by removing the CI section from `README.md`.

### 2. Code and asset scan for impacted components

| File | Current state | Action |
| --- | --- | --- |
| `README.md` (root) | Contains Overview, Installation, and "Automated version bump & release log" sections | Remove CI workflow section; keep Overview and Installation |
| `.aib_memory/context.md` | CI workflow details already synthesized | No edit required |
| `.aib_brain/Concepts.md` | Does not contain GitHub Actions operational guidance; `edit_allowed = N` | No edit performed |
| `.aib_brain/README.md` | Operator field guide; no CI workflow setup instructions | No edit required |

The "Automated version bump & release log" section in `README.md` covers: what the workflow does, when it runs, repository setup requirements, operational behaviour, and troubleshooting. All architectural aspects are already in `context.md`. Operational setup requirements (GitHub Actions permissions) are not duplicated elsewhere, but they are primarily relevant to the AIB Maintainer setting up the repository, not to a developer onboarding via the root README.

### 3. Pattern scan against standards

A concise root README following the pattern: what-is-it → how-to-install → where-to-learn-more is the standard open-source convention. The current root README deviates from this by embedding operational runbook content.

### 4. External benchmarking

Standard practice for framework repositories is to keep the root README as a "landing page" document (2–3 short sections) and link out to dedicated documentation for operational details.

### 5. Risks

- **R1 — Loss of operational guidance discoverability:** The GitHub Actions setup requirements (enabling Actions, setting Read/Write permissions) are currently only in `README.md`. After removal, a maintainer setting up the repository for the first time would need to find this in `context.md` or the YAML file. Mitigation: the content is already in `context.md`; acceptable for the maintainer audience.

- **R2 — README.md not in references.md:** The root `README.md` is not registered in `references.md`. The implement workflow relies on `references.md` for file-edit permission. Since the user explicitly requested the edit, this is acceptable, but the implement workflow should be aware it is operating outside the registered set.

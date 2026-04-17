# Analysis Document Convention

**Scope:** Normative  
**Applies to:** All files named `analysis.md` generated under `.aib_memory/requests/<request-folder>/`.

## 1. Purpose

The **Analysis document** is a **reasoning and knowledge-capture artifact** only. It records the AI's structured thinking about the user request ΓÇö research findings, scope interpretation, domain and technical context, impact awareness, and risk identification.

**The analysis document is NOT an implementation driver.**

- `implement` MUST NOT read the analysis document.
- All implementation-relevant content (assumptions, plan, testing, documentation touchpoints, open questions) is written into `request.md` by the `create-analysis` action.
- Human stakeholders read the analysis for auditability and context; they do not use it as an execution specification.

***

## 2. Scope & Normative Language

This convention applies only to analysis artifacts for a single request:

*   Target files: `analysis.md`
*   Location: `.aib_memory/requests/<request-folder>/`
*   Out of scope: plan, questionnaire, and implementation records (defined by their own conventions or removed)

Normative keywords **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, and **MAY** are interpreted per BCP 14 (RFC 2119 / RFC 8174).

***

## 3. File Naming & Location (Normative)

*   File name **must** be exactly: `analysis.md`

*   File **must** be placed in the respective request folder: `.aib_memory/requests/<request-folder>/analysis.md`

*   Exactly one analysis file per request **MAY** exist at a time.

*   Regeneration **must** replace the same file path atomically.

*   Version metadata (for example: version/author/status headers) **must not** be embedded in the analysis file. Versioning is handled by VCS.

***

## 4. Mandatory Structure

Each analysis file **must** contain the following sections in the exact order:

1.  **Executive Summary** **[REQ]**
2.  **Domain Knowledge Essentials** **[REQ]**
3.  **Technical Knowledge & Terms** **[REQ]**
4.  **Research Results** **[REQ]**
5.  **External Benchmarking** **[REQ]**
6.  **Minimal Spikes and Experiments** **[REQ]**

***

### 4.1 Executive Summary

A concise overview in 5-10 bullets or sentences answering:

*   Request ID

*   Request title

*   High-level purpose

The summary must reference:

*   The `request.md` content

*   A brief note on which sections were added/updated in `request.md` during this analysis run (forward reference to section 8)

After each bullet keep an empty line for readability.


***

### 4.2 Domain Knowledge Essentials

Describe the minimum domain context required for correct decisions.

Include:

*   Business terminology and one-line definitions

*   Impacted roles/personas

*   Business processes touched

*   Relevant metrics/KPIs and IDs (if defined)

*   Acceptance impact from a business/product perspective

***

### 4.3 Technical Knowledge & Terms

Describe the minimum technical context required for correct decisions.

Include:

*   Technologies, components, modules, and environments involved

*   Data models/assets and runtime constraints

*   Non-functional attributes (reliability, performance, security, operations)

*   One-line definition for each key term/acronym on first use



Rules:

*   Summarize findings and implications; do not embed external links.

*   If live web research was used, mention outcomes only, not URLs.

*   Include a concise evidence log mapping `evidence -> implication`.

*   The Files Read bullet list is required; omitting it is a convention violation.

### 4.4. Research Results

This section lists pattern-based research findings:

1.  Pattern scan against organizational standards and prior similar solutions.


## 5. External Benchmarking **[REQ]**

This section MUST be present and substantive. It documents research-based context from outside the workspace.

**Mandatory content:**

- Comparable solutions, frameworks, or patterns found in industry literature or open-source ecosystems relevant to the request scope.
- Key takeaways and applicability assessment for each benchmark reference.
- Explicit rationale for adoption, adaptation, or rejection of each benchmarked approach.
- At minimum two external references must be documented per analysis. If no applicable external material exists, explicitly state why and document the absence.

**Rules:**

- Summarize findings and implications; do not embed external links.
- Organize as a bulleted list with one sub-bullet per takeaway.
- MUST NOT be empty or contain only a stub notice.


## 6. Minimal Spikes and Experiments **[REQ]**

This section documents the outcome of brief feasibility experiments or uncertainty-resolution spikes conducted as part of this analysis.

**Mandatory content:**

- For each spike or experiment: a one-sentence hypothesis, the approach taken, the observed outcome, and the conclusion drawn.
- If no spike was conducted: a brief justification explaining why uncertainty was low enough not to require one.

**Format per spike:**

- **Spike: <topic>**
  - Hypothesis: <what was tested>
  - Approach: <how it was tested>
  - Outcome: <what was observed>
  - Conclusion: <what is now known>

**Rules:**

- MUST NOT be empty; use the "no spike needed" form when applicable.
- Each spike MUST be independently reproducible from the described approach.


## 7. Maintenance Rules (Normative)

*   Idempotence: same memory state and same request should converge to same analysis intent.
*   Change drivers: update analysis when scope changes, new evidence appears, or risk state changes.
*   Closure: once a request is closed in `requests_register.md`, analysis remains unchanged except factual corrections.

## 8. Formatting Requirements

*   All headings must use `##` or `###` consistent with this convention.
*   Bullet lists must use `- `.
*   Tables must use standard GitHub Markdown table syntax.
*   No HTML is allowed.
*   No images, diagrams, embeds, or external hyperlinks.
*   The document must be deterministic (same inputs -> same output intent).
*   Separate chapters, bullets with empty lines for readability

***

## 9. Determinism Rules (Normative)

*   Given the same memory state and request input, analysis output intent must be identical.
*   AI must not guess beyond request scope.
*   If request ambiguity exists that cannot be resolved internally, create a `Q<nnn>` question block in `request.md` -> `## Questions & Decisions` instead of making assumptions.

***

## 10. Prohibited Content

*   Secrets, private keys, credentials, tokens, or sensitive PII.
*   External hyperlinks.
*   Embedded images or diagrams.
*   In-file version/author/status metadata headers.

***



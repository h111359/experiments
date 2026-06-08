# Analysis Document Convention
$RID=request_id | $AM=.aib_memory/ | $ARQ=.aib_memory/requests/<request-folder>/ | $AD=analysis doc | $DP=Decision Point
Scope: Normative | Applies to: analysis-$RID.md in $AM (active) + $ARQ (archived)

## 1. Purpose
$AD = reasoning+knowledge-capture artifact only; NOT impl driver.
Records AI structured thinking: research findings, scope interpretation, domain+technical context, impact awareness, risk identification.
implement MUST NOT read $AD.
impl-relevant content (assumptions, plan, testing, doc touchpoints, open questions) -> plan-$RID.md via aib-analyze.md.
NO: [use $AD as exec spec]

## 2. Scope & Normative Lang
Applies to: analysis-$RID.md only.
Target: analysis.md | Location: $AM (active) or $ARQ (archived)
Out of scope: plan, questionnaire, impl records (own conventions or removed).
Keywords MUST/MUST NOT/SHALL/SHOULD/MAY per BCP 14 (RFC 2119/8174).

## 3. File Naming, Location & Write Behavior
Name pattern: analysis-$RID.md (e.g. analysis-R-20260509-2313.md)
Placement:
  active: $AM/analysis-$RID.md (root of $AM; NOT inside request subfolder)
  archived: move-request-artifacts.py moves -> $ARQ/analysis-$RID.md (ID preserved) before close-request.py marks Closed
Max 1 analysis file per req.
Re-run aib-analyze.md -> fully replace (overwrite) active copy at $AM/analysis-$RID.md.
NO: [append | prepend | partial edit]; prior content discarded; output = complete self-contained doc always.
NO: [version/author/status headers in file]; versioning via VCS.

## 4. Mandatory Structure
Sections in exact order:
1. Overview [REQ]
2. Files Read During This Analysis Run [REQ]
3. Input Interpretation [REQ]
4. Research Results [REQ]
5. Decision Register [REQ]

### 4.1 Overview
For human review+auditability only; implement MUST NOT read/act on it. Fully replace each re-run.
Required:
- Request ID
- Request title
- ### Background: context explaining why change needed, sourced from developer's ## Input
- ### Scope: what's included; impacted functional areas, components, domains, docs
- ### Out of scope: intentionally excluded items
Rules: each subsection (### Background | ### Scope | ### Out of scope) >= 1 sentence | fully replace on re-run.

### 4.2 Files Read During This Analysis Run [REQ]
List every workspace file read in this run.
Each entry: workspace-relative file path.
Includes: preflight, convention loading, analysis drafting files.
MUST NOT be empty.

### 4.3 Input Interpretation [REQ]
AI-generated spec-grade interpretation of developer's ## Input. Rewrites intent using correct product terminology (@context.md) + relevant external domain knowledge. Third-person spec prose.
Primary purpose: authoritative source for Answer Application Sub-flow when creating request-$RID.md on re-run without archived input.md (GC-01 compliance).
Sub-sections:
  ### User Original Inputs: original + all subsequent inputs
  ### AI interpretation: copilot interpretation (updated)
Rules: present in every run (first+re-run) | faithfully represent dev intent (enrich, not replace) | MUST NOT be empty.

### 4.4 Research Results [REQ]
Primary AI reasoning artifact. Documents full analytical thinking.
Required:
- Workspace pattern-scan: impacted components, cross-ref issues, relevant prior solutions
- Industry knowledge: best practices+external benchmarking; min 3 findings from established frameworks/OSS communities/industry lit; each with applicability assessment
- AI Agent critique: bullet-list review of ALL issues in req itself + every file read this run; not limited to current scope; each issue = 1 bullet regardless of scope relation
  Issue types: [misalignment | inconsistencies | logical errors | redundancies | misplaced content | unclear wording | broken cross-refs | format drift | other quality concerns]
NO: [empty | stub notices only]
implement MUST NOT read/act on this section.

### 4.5 Decision Register [REQ]
Captures pivotal decisions shaping solution. Each entry = $DP.
$DP state: resolved autonomously by AI | raised as question for user | already resolved by user.
Required per $DP:
- Identify specific task/step where decision applies + why alternatives exist
- Named alternative approaches, each with:
  - one-sentence description
  - key trade-offs (benefits + drawbacks)
  - expected codebase impact
- Resolution classification:
  - resolve-autonomously: ONLY when developer's input.md ## Input OR named specific section of workspace convention file explicitly+unambiguously resolves it; rationale MUST quote/cite exact source text+file path
    NO: [external benchmarking | industry best practices | AI judgment as justification]
  - ask: Q-block raised for dev input; AI MUST NOT express preference or steer toward any option; present choices neutrally
  - resolved-by-user: user already decided
- Resolution outcome: retain only chosen alternative; discard non-chosen from final doc
Structure:
  ### Decision Points
  #### Decision Point: <name> (one per $DP)
    - Tag
    - Rationale/Resolution
[no $DPs identified] -> single entry documenting that fact.
Rules: >= 1 alternative per $DP | [doubt resolve-autonomously vs ask] -> always ask | resolve-autonomously MUST cite concrete source (exact text+file path) | update resolution after human answer | MUST NOT be empty | fully replaced each re-run.

## 5. Formatting
- Headings: ## or ### consistent with this convention
- Bullets: -
- [2+ discrete items] -> list; unordered when order !matter; ordered when order matters
- Parallel phrasing + consistent punctuation; items concise
- [enumerated parts in single item] -> sublist
- Tables: standard GitHub Markdown syntax
NO: [HTML | non-deterministic output]
Doc must be deterministic (same inputs -> same output intent).
Separate chapters+bullets with empty lines for readability.

## 6. Prohibited
NO: [secrets | private keys | credentials | tokens | sensitive PII | in-file version/author/status metadata headers]



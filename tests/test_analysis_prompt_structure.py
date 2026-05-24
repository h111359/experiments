"""
test_analysis_prompt_structure.py: Regression tests asserting the simplified
plan.md section schema in aib-analyze.md and plan-convention.md.

Part of the AIB test suite. Covers SC-1, SC-2, SC-3, SC-3b, SC-4, and SC-5
from request R-20260507-2209.

Responsibilities:
- Assert removed section headings are absent from both source files.
- Assert #### Outputs appears as a level-4 heading in the Plan schema.
- Assert removed standalone field labels (Inputs, External Interfaces,
  Environment & Configuration) are absent from the Plan schema blocks.
- Assert **Intent:** bold label is absent from both source files.
- Assert the 4-section mandatory list is referenced in aib-analysze.md.
"""

from __future__ import annotations

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_PROMPT = WORKSPACE_ROOT / ".aib_brain" / "prompts" / "aib-analyze.md"
PLAN_CONVENTION = WORKSPACE_ROOT / ".aib_brain" / "conventions" / "plan-convention.md"


class TestRemovedSectionsAbsentFromAnalysisPrompt:
    """SC-1: Removed section headings must not appear in aib-analyze.md generation rules."""

    def test_code_scan_section_absent(self) -> None:
        """## Code and Asset Scan for Impacted Components must not appear."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Code and Asset Scan for Impacted Components" not in content, (
            "aib-analyze.md must not reference 'Code and Asset Scan for Impacted "
            "Components' — this section has been removed from the request.md schema."
        )

    def test_internal_review_section_absent(self) -> None:
        """## Internal Review of Request and Product Docs must not appear."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Internal Review of Request and Product Docs" not in content, (
            "aib-analyze.md must not reference 'Internal Review of Request and "
            "Product Docs' — this section has been removed from the request.md schema."
        )


class TestRemovedSectionsAbsentFromPlanConvention:
    """SC-2: Removed section headings must not appear in plan-convention.md."""

    def test_code_scan_section_absent(self) -> None:
        """## Code and Asset Scan for Impacted Components must not appear."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "Code and Asset Scan for Impacted Components" not in content, (
            "plan-convention.md must not define 'Code and Asset Scan for Impacted "
            "Components' — this section has been removed from the plan.md schema."
        )

    def test_internal_review_section_absent(self) -> None:
        """## Internal Review of Request and Product Docs must not appear."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "Internal Review of Request and Product Docs" not in content, (
            "plan-convention.md must not define 'Internal Review of Request and "
            "Product Docs' — this section has been removed from the plan.md schema."
        )


class TestPlanSchemaFieldsInAnalysisPrompt:
    """SC-3: Plan schema must use #### headings and remove embedded metadata fields."""

    def test_intent_bold_label_absent(self) -> None:
        """**Intent:** bold label must not appear in the Plan schema."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "**Intent:**" not in content, (
            "aib-analyze.md Plan schema must not contain '**Intent:**' — "
            "level-4 headings are now used for plan task sub-fields."
        )

    def test_inputs_field_absent(self) -> None:
        """**Inputs:** must not appear as a standalone plan-schema field."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        # The top-level 'Inputs:' label in the prompt header is allowed;
        # the schema field '**Inputs:**' must be gone.
        assert "**Inputs:**" not in content, (
            "aib-analyze.md Plan schema must not contain '**Inputs:**' as a "
            "standalone labeled field — this metadata is now embedded in Procedure steps."
        )

    def test_external_interfaces_field_absent(self) -> None:
        """**External Interfaces:** must not appear as a standalone plan-schema field."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "**External Interfaces:**" not in content, (
            "aib-analyze.md Plan schema must not contain '**External Interfaces:**' "
            "— this metadata is now embedded in Procedure steps."
        )

    def test_environment_configuration_field_absent(self) -> None:
        """**Environment & Configuration:** must not appear as a standalone plan-schema field."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "**Environment & Configuration:**" not in content, (
            "aib-analyze.md Plan schema must not contain '**Environment & "
            "Configuration:**' — this metadata is now embedded in Procedure steps."
        )


class TestPlanSchemaFieldsInPlanConvention:
    """SC-3: Plan schema in plan-convention.md must use #### headings and remove others."""

    def test_outputs_field_present(self) -> None:
        """#### Outputs must appear as a level-4 heading in the Plan schema."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "#### Outputs" in content, (
            "plan-convention.md Plan schema must use '#### Outputs' as a level-4 heading."
        )

    def test_intent_bold_label_absent(self) -> None:
        """**Intent:** bold label must not appear in the Plan schema."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "**Intent:**" not in content, (
            "plan-convention.md Plan schema must not contain '**Intent:**' — "
            "level-4 headings are now used for plan task sub-fields."
        )

    def test_inputs_field_absent(self) -> None:
        """**Inputs:** must not appear as a standalone plan-schema field."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "**Inputs:**" not in content, (
            "plan-convention.md Plan schema must not contain '**Inputs:**' as a "
            "standalone labeled field."
        )

    def test_external_interfaces_field_absent(self) -> None:
        """**External Interfaces:** must not appear as a standalone plan-schema field."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "**External Interfaces:**" not in content, (
            "plan-convention.md Plan schema must not contain '**External Interfaces:**'."
        )

    def test_environment_configuration_field_absent(self) -> None:
        """**Environment & Configuration:** must not appear as a standalone plan-schema field."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "**Environment & Configuration:**" not in content, (
            "plan-convention.md Plan schema must not contain '**Environment & Configuration:**'."
        )


class TestNewStructuralSections:
    """Regression tests for structural sections added in R-20260514-0427.

    Guards against accidental removal of the three new top-level sections
    introduced to reduce cognitive load in aib-analyze.md.
    """

    def test_execution_model_summary_present(self) -> None:
        """## Execution Model Summary heading must be present in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Execution Model Summary" in content, (
            "aib-analyze.md must contain 'Execution Model Summary' — "
            "this section was added to orient the agent before execution begins."
        )

    def test_global_constraints_present(self) -> None:
        """## Global Constraints heading must be present in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Global Constraints" in content, (
            "aib-analyze.md must contain 'Global Constraints' — "
            "this section consolidates cross-cutting constraints by GC identifier."
        )

    def test_failure_handling_present(self) -> None:
        """## Failure Handling heading must be present in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Failure Handling" in content, (
            "aib-analyze.md must contain 'Failure Handling' — "
            "this section specifies halt-with-error behavior for missing files and script failures."
        )

    def test_gc04_no_closed_request_reads_present(self) -> None:
        """GC-04 no-closed-request-reads constraint must be present in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "GC-04" in content, (
            "aib-analyze.md must contain 'GC-04' in the Global Constraints section — "
            "this constraint prohibits reading files inside Closed request subfolders."
        )


class TestAttachmentsScanLanguage:
    """SC-1, SC-2, SC-3: aib-analyze.md must use recursive-walk language for attachments."""

    def test_flat_scan_absent_from_attachments_steps(self) -> None:
        """'flat scan' must not appear anywhere in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "flat scan" not in content, (
            "aib-analyze.md must not contain 'flat scan' — the attachments steps "
            "must specify recursive-walk semantics."
        )

    def test_ignore_subdirectories_absent_from_attachments_steps(self) -> None:
        """'ignore subdirectories' must not appear anywhere in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "ignore subdirectories" not in content, (
            "aib-analyze.md must not contain 'ignore subdirectories' — the attachments "
            "steps must specify recursive-walk semantics."
        )

    def test_recursive_language_present(self) -> None:
        """'Recursively' or 'recursively' must appear in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "ecursively" in content, (
            "aib-analyze.md must contain recursive-walk language ('Recursively' or "
            "'recursively') in the attachments steps."
        )


class TestFourSectionMandatoryListInAnalysisPrompt:
    """SC-5: aib-analyze.md auto-creation branch must validate 4 mandatory sections."""

    def test_four_mandatory_sections_referenced(self) -> None:
        """Auto-creation branch must reference 4 (not 10) mandatory sections."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "All 4 mandatory sections" in content, (
            "aib-analyze.md auto-request creation branch must reference '4 mandatory "
            "sections', not 10."
        )


class TestBrownfieldCheckRelocation:
    """Regression tests guarding the brownfield check relocation from Section 0 into Phase 4.

    Guards against re-introduction of the old Section 0 position and accidental
    deletion of the brownfield check logic after R-20260516-1343.
    """

    def test_section_0_brownfield_heading_absent(self) -> None:
        """## 0. Brownfield Pre-Preflight must not appear as a level-2 heading."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "## 0. Brownfield Pre-Preflight" not in content, (
            "aib-analyze.md must not contain '## 0. Brownfield Pre-Preflight' as a "
            "level-2 heading — the brownfield check was relocated into Phase 4."
        )

    def test_refresh_context_referenced_in_analyze(self) -> None:
        """aib-refresh-context.md must still be referenced in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "aib-refresh-context.md" in content, (
            "aib-analyze.md must still reference 'aib-refresh-context.md' "
            "— the brownfield context check invokes this prompt."
        )

    def test_ten_mandatory_sections_absent(self) -> None:
        """The old 10-section reference must be gone from the auto-creation branch."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "All 10 mandatory sections" not in content, (
            "aib-analyze.md must not reference '10 mandatory sections' — the schema "
            "was reduced to 4 sections."
        )


class TestFourSectionMandatoryListInPlanConvention:
    """SC-2: plan-convention.md Document Structure must declare 4 mandatory sections."""

    def test_four_section_declaration_present(self) -> None:
        """Document Structure header must declare 4 mandatory sections."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "1\u20134" in content or "1-4" in content, (
            "plan-convention.md must declare sections 1\u20134 as mandatory, "
            "not 1\u201310."
        )

    def test_ten_section_declaration_absent(self) -> None:
        """Document Structure header must not declare 10 mandatory sections."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "1\u201310" not in content and "1-10" not in content, (
            "plan-convention.md must not reference sections 1\u201310 — the schema "
            "was reduced to 4 sections."
        )


class TestStandardFlowInputArchivingSemantics:
    """SC: Standard-flow reset must conditionally archive input.md before reset."""

    def test_non_stub_definition_present(self) -> None:
        """Standard flow final step must define non-stub input deterministically."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "`.aib_memory/input.md` is in a non-stub state" in content, (
            "aib-analyze.md must define when standard-flow input is treated as non-stub."
        )

    def test_archive_before_reset_rule_present(self) -> None:
        """Non-stub standard flow must archive input.md before reset."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "archive the pre-reset `input.md` content" in content, (
            "aib-analyze.md must require archive-before-reset for non-stub standard flow."
        )

    def test_stub_equivalent_skip_archive_rule_present(self) -> None:
        """Stub-equivalent standard flow must skip archive creation."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "If stub-equivalent: skip archive creation for this standard-flow reset." in content, (
            "aib-analyze.md must require archive skip when input.md is seed-template-equivalent."
        )


ANALYSIS_CONVENTION = WORKSPACE_ROOT / ".aib_brain" / "conventions" / "analysis-convention.md"
INITIALIZE_PY = WORKSPACE_ROOT / ".aib_brain" / "tools" / "initialize.py"
CLOSE_REQUEST_PY = WORKSPACE_ROOT / ".aib_brain" / "tools" / "close-request.py"


class TestAnalysisConventionSectionStructure:
    """Regression tests asserting the restructured analysis-convention.md section content."""

    def test_domain_knowledge_absent(self) -> None:
        """Domain Knowledge Essentials must not appear in analysis-convention.md."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "Domain Knowledge Essentials" not in content, (
            "analysis-convention.md must not reference 'Domain Knowledge Essentials' — "
            "this section has been removed."
        )

    def test_technical_knowledge_absent(self) -> None:
        """Technical Knowledge & Terms must not appear in analysis-convention.md."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "Technical Knowledge" not in content, (
            "analysis-convention.md must not reference 'Technical Knowledge' — "
            "this section has been removed."
        )

    def test_testing_section_absent(self) -> None:
        """Testing must not appear as a [REQ] mandatory section heading."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "**Testing** **[REQ]**" not in content, (
            "analysis-convention.md must not list 'Testing' as a [REQ] mandatory section."
        )

    def test_multi_perspective_absent(self) -> None:
        """Multi-Perspective Stakeholder Review must not appear in analysis-convention.md."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "Multi-Perspective Stakeholder Review" not in content, (
            "analysis-convention.md must not reference 'Multi-Perspective Stakeholder Review' — "
            "this section has been removed."
        )

    def test_best_practices_present(self) -> None:
        """Best-practices content must appear in analysis-convention.md (within Research Results)."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "best practices" in content.lower(), (
            "analysis-convention.md must reference best-practices guidance "
            "(now covered within Research Results, not as a standalone section)."
        )

    def test_decision_register_present(self) -> None:
        """Decision Register must appear in analysis-convention.md."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "Decision Register" in content, (
            "analysis-convention.md must define 'Decision Register' as a mandatory section."
        )

    def test_minimum_questions_in_initialize_seed(self) -> None:
        """initialize.py input_seed must contain 'Minimum questions'."""
        content = INITIALIZE_PY.read_text(encoding="utf-8")
        assert "Minimum questions" in content, (
            "initialize.py input_seed must contain 'Minimum questions' option."
        )

    def test_minimum_questions_in_close_request_seed(self) -> None:
        """close-request.py input_seed must contain 'Minimum questions'."""
        content = CLOSE_REQUEST_PY.read_text(encoding="utf-8")
        assert "Minimum questions" in content, (
            "close-request.py input_seed must contain 'Minimum questions' option."
        )


class TestDecisionsSectionRename:
    """Regression tests asserting ## Decisions section presence and Decision Points structure requirements."""

    def test_questions_and_decisions_absent_from_prompt(self) -> None:
        """## Questions & Decisions must not appear as a section heading in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "## Questions & Decisions" not in content, (
            "aib-analyze.md must not reference '## Questions & Decisions' as a section heading "
            "— the section has been renamed to '## Decisions'."
        )

    def test_questions_and_decisions_absent_from_plan_convention(self) -> None:
        """## Questions & Decisions must not appear in plan-convention.md."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "## Questions & Decisions" not in content, (
            "plan-convention.md must not reference '## Questions & Decisions' "
            "— the section has been removed from the plan schema."
        )

    def test_plan_section_present_in_plan_convention(self) -> None:
        """## Plan must appear in plan-convention.md as the 4th mandatory section."""
        content = PLAN_CONVENTION.read_text(encoding="utf-8")
        assert "## Plan" in content, (
            "plan-convention.md must define '## Plan' as the 4th mandatory section."
        )

    def test_decision_points_catalog_required_in_prompt(self) -> None:
        """Decision Points section must be required in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Decision Points" in content, (
            "aib-analyze.md must require a 'Decision Points' section "
            "within ## Decision Register."
        )


class TestRequirementsConventionReference:
    """SC-1, SC-2, SC-3: requirements-analysis-convention.md must be referenced
    in aib-analyze.md External Dependencies, Preflight step 8, and Section 5."""

    def test_requirements_convention_in_external_dependencies(self) -> None:
        """SC-1: requirements-analysis-convention.md must appear in section 2.2 table."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "requirements-analysis-convention.md" in content, (
            "aib-analyze.md section 2.2 must list 'requirements-analysis-convention.md' "
            "as an external dependency."
        )

    def test_requirements_convention_in_preflight_step_8(self) -> None:
        """SC-2: step 8 in aib-analyze.md must name requirements-analysis-convention.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "all three convention files" in content, (
            "aib-analyze.md Preflight step 8 must read 'all three convention files', "
            "including requirements-analysis-convention.md."
        )

    def test_requirements_gate_application_instruction_present(self) -> None:
        """SC-3: aib-analyze.md must contain a gate application instruction."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Requirements Gate Evaluation" in content, (
            "aib-analyze.md Section 5 must contain a 'Requirements Gate Evaluation' "
            "instruction specifying how gate results are surfaced in the analysis output."
        )


class TestInputInterpretationSection:
    """Regression tests asserting the ## Input Interpretation section and deferred-creation rule.

    Added in request R-20260515-1107 to guard against removal of the new mandatory section
    and the deferred request.md creation logic introduced in aib-analyze.md.
    """

    def test_input_interpretation_in_analysis_prompt(self) -> None:
        """aib-analyze.md must reference 'Input Interpretation' as a mandatory section."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Input Interpretation" in content, (
            "aib-analyze.md must reference 'Input Interpretation' — this section was "
            "added as a mandatory section in the analysis document."
        )

    def test_input_interpretation_in_analysis_convention(self) -> None:
        """analysis-convention.md must define 'Input Interpretation' as a mandatory section."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "Input Interpretation" in content, (
            "analysis-convention.md must define 'Input Interpretation' as a mandatory section."
        )

    def test_deferred_creation_rule_in_analysis_prompt(self) -> None:
        """aib-analyze.md must contain deferred-creation state handling language."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "deferred-creation" in content, (
            "aib-analyze.md must contain deferred-creation state handling language — "
            "request.md MUST NOT be written in the first pass when Q-blocks are generated."
        )


class TestOverviewSectionIntroduced:
    """Regression tests asserting the new ## Overview section and removed ## Executive Summary."""

    def test_executive_summary_absent_from_convention(self) -> None:
        """Executive Summary must not appear in the section-4 mandatory list of analysis-convention.md."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "**Executive Summary** **[REQ]**" not in content, (
            "analysis-convention.md must not list '**Executive Summary** **[REQ]**' as a "
            "mandatory section — it has been replaced by Overview."
        )

    def test_overview_present_in_convention(self) -> None:
        """Overview must appear in analysis-convention.md as a mandatory section."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "Overview" in content, (
            "analysis-convention.md must define 'Overview' as a mandatory section."
        )

    def test_ai_agent_critique_present_in_convention(self) -> None:
        """AI Agent critique must appear in analysis-convention.md Research Results content."""
        content = ANALYSIS_CONVENTION.read_text(encoding="utf-8")
        assert "AI Agent critique" in content, (
            "analysis-convention.md must reference 'AI Agent critique' in the Research Results "
            "mandatory content — it replaces Feasibility notes and Expert observations."
        )

    def test_decision_points_table_phrase_absent_from_prompt(self) -> None:
        """The phrase 'Decision Points table' must not appear in aib-analyze.md."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Decision Points table" not in content, (
            "aib-analyze.md must not contain the phrase 'Decision Points table' — "
            "the format has been replaced by a heading/sub-heading list."
        )

    def test_overview_referenced_in_prompt(self) -> None:
        """Overview must be referenced in aib-analyze.md section list."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Overview" in content, (
            "aib-analyze.md must reference 'Overview' as a mandatory analysis section."
        )


class TestAppendixAStructure:
    """Regression tests asserting the Appendix A refactor from R-20260524-0734.

    Guards against removal of Appendix A and re-inlining of the Auto-Request
    Creation Branch procedure into Step 1 of aib-analyze.md.
    """

    def test_appendix_a_section_exists(self) -> None:
        """## Appendix A — Auto-Request Creation Branch must be present after ## 7."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "## Appendix A — Auto-Request Creation Branch" in content, (
            "aib-analyze.md must contain '## Appendix A — Auto-Request Creation Branch' "
            "as a top-level section at the end of the file."
        )

    def test_step1_zero_active_rows_no_inline_substeps(self) -> None:
        """The inline 6-sub-step procedure must not appear in Step 1; only in Appendix A."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        appendix_start = content.find("## Appendix A")
        assert appendix_start != -1, "Appendix A section not found."
        step1_region = content[:appendix_start]
        assert "Resume the standard analysis flow at step 2 (Context Check)" not in step1_region, (
            "aib-analyze.md Step 1 must not contain the inline 'Resume the standard analysis "
            "flow at step 2' instruction — it belongs exclusively in Appendix A."
        )

    def test_gc02_references_appendix_a(self) -> None:
        """GC-02 must reference Appendix A instead of 'Auto-Request Creation Branch in step 1'."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Appendix A" in content[content.find("GC-02"):content.find("GC-03")], (
            "aib-analyze.md GC-02 must reference 'Appendix A' for the input-reset rule."
        )

    def test_gc06_references_appendix_a(self) -> None:
        """GC-06 must reference Appendix A instead of 'Auto-Request Creation Branch in step 1'."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "Appendix A" in content[content.find("GC-06"):content.find("GC-06") + 300], (
            "aib-analyze.md GC-06 must reference 'Appendix A' for the authorized tool-script "
            "invocations exception."
        )

    def test_step1_trigger_line_references_appendix_a(self) -> None:
        """Step 1 Zero-Active-rows trigger line must reference Appendix A."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        assert "execute **Appendix A — Auto-Request Creation Branch**" in content, (
            "aib-analyze.md Step 1 'Zero Active rows' branch must contain the trigger line "
            "'execute **Appendix A — Auto-Request Creation Branch**'."
        )

    def test_step6_trigger_guard_references_appendix_a(self) -> None:
        """Step 6 trigger guard must reference Appendix A."""
        content = ANALYSIS_PROMPT.read_text(encoding="utf-8")
        step6_start = content.find("### 5.6 Step 6")
        step7_start = content.find("### 5.7 Step 7")
        step6_region = content[step6_start:step7_start]
        assert "Appendix A" in step6_region, (
            "aib-analyze.md Step 6 trigger guard must reference 'Appendix A' instead of "
            "'Auto-Request Creation Branch (step 1)'."
        )

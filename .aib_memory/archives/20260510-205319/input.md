## Active request
No active request

## Options
- [ ] No changes — provide answer only
- [ ] Skip analysis document generation

## Input

What:

change the formatting of the whole file. Instead of bold titles - make markdown headings. Add empty lines for readability.
Reduce "## Executive Summary" - leave only Request ID:, Title:, Purpose:
Make "Files read during this analysis run:" a separate header
Remove sections "## Domain Knowledge Essentials", "## Technical Knowledge & Terms"
Keep "Research Results", just remove Evidence log: section
Add section "Best practices" with result of found in Internet best practices related to the request
Keep "External Benchmarking" and "Minimal Spikes and Experiments" sections from analysis.md
"Testing" steps should be included in the request.md or in UAT_scenarios.md files - remove it from the analysis
Remove section "## Multi-Perspective Stakeholder Review"
Eliminate "analysis.md" - no generation anymore. Only request.md remains the file generated and considered in implementation phase
Add section "Implementation alternatives" - list here the moments where the request could be executed in several significant different ways. Use these alternatives to generate the questions to the user which option is preferred.
Make sure this analysis is created before the plan in request.md is generated and the plan is aligned with the findings and entries in the analysis
Questions specific:

Ensure the analysis prompt has a step for identification of multiple different implementation variants/approaches
Ensure for each identified multi-choice topic is generated a question
Ensure all questions are asked and no need of second round of questions to be asked
Add in input.md an option the user to provide the minimum number of questions which to be asked (by default should be 0)
The system should provide the user to make choices for alternatives which makes significant difference in the result. Also the questions provide sort of feedback, opportunity for learning and more transparency for the user
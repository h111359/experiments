# Development and Deployment Specification

## 1) Purpose

This specification defines the lifecycle for evolving `.aib_brain/`, with version visibility managed through a single SemVer file placed directly in `.aib_brain/`.

## 2) Canonical Version Rule

- The active AIB version MUST be represented by exactly one empty file in `.aib_brain/`.
- Filename format MUST be: `vMAJOR.MINOR.PATCH`.
- Example: `.aib_brain/v1.0.0`.
- The filename is the canonical version indicator.

## 3) Semantic Versioning Policy

AIB versioning MUST follow [Semantic Versioning 2.0.0](https://semver.org/).

- MAJOR (`X` in `vX.Y.Z`): Increment for breaking structural changes in `.aib_brain/`.
  - Examples: incompatible folder/file layout changes, prompt contract changes requiring migration, required field renames in templates.
- MINOR (`Y`): Increment for backward-compatible feature additions.
  - Examples: new optional prompts, additional conventions, non-breaking workflow enhancements.
- PATCH (`Z`): Increment for backward-compatible fixes.
  - Examples: typo corrections, bug fixes in scripts/prompts/templates that do not break compatibility.

## 4) Version Bump Workflow

When changing version:

1. Determine the correct bump type (MAJOR/MINOR/PATCH) per Section 3.
2. Remove the existing version marker file in `.aib_brain/`.
3. Create the new empty marker file with the updated name.
4. Include a short note in the pull request describing:
   - previous version,
   - new version,
   - bump rationale,
   - migration impact (if any).
5. Before merge, verify there is exactly one version marker file in `.aib_brain/` whose name follows `vMAJOR.MINOR.PATCH` (for example, `v1.2.3`) and that this marker file is empty.

## 5) Git and GitHub Workflow

- Branch naming convention:
  - Branches MUST be organized by issue and named using issue number (example: `issue/123`).
  - Do not use `feature/`, `fix/`, or `breaking/` prefixes.
- Pull requests MUST include:
  - clear summary of `.aib_brain/` changes,
  - explicit SemVer bump justification,
  - migration notes when required.
- Squash merge is recommended for a clean change history per version transition.

## 6) Developer Workflow Across Versions

For each request/iteration that modifies `.aib_brain/`:

1. Read current marker file in `.aib_brain/` to identify active version.
2. Implement changes in an issue branch named with the issue number (for example, `issue/123`).
3. Validate scripts/prompts/templates still function for expected workflows.
4. Apply SemVer bump only when the change scope is finalized.
5. Submit PR with version rationale and migration guidance.

## 7) Deployment Procedure

Deployment here means releasing `.aib_brain/` for consumption in workspaces.

1. Merge approved PR containing the updated version marker file.
2. Publish/propagate updated `.aib_brain/` to target repositories/workspaces.
3. Post-release verification:
   - `.aib_brain/` contains exactly one semver marker file,
   - marker filename matches release notes,
   - core commands (`run.sh`, `run.bat`, and tools scripts) remain operational.
4. The `logs/` directory at workspace root MUST be preserved across `.aib_brain/` upgrades and MUST NOT be deleted or modified during the upgrade procedure.

## 8) Expected Agent Behavior on Version Changes

Agents and automation working with AIB SHOULD:

1. Detect the current version by finding the marker file in `.aib_brain/` whose filename matches `vMAJOR.MINOR.PATCH`.
2. Refuse to infer version from any other source when this file is present.
3. Treat MAJOR changes as potentially incompatible and request/perform migration checks.
4. Treat MINOR/PATCH changes as compatible unless specific migration notes state otherwise.
5. If no marker file is found, stop and report a configuration error that requires maintainer action.
6. If more than one marker file is found, stop and report an invalid state; do not guess a version.

## 9) Migration Rules for Incompatible Updates

For MAJOR version changes:

- A migration note is REQUIRED in the PR describing:
  - what changed incompatibly,
  - which files/paths/prompts/tools are affected,
  - upgrade steps,
  - rollback strategy.
- Keep a compatibility window only if explicitly documented.
- If no compatibility window is provided, consumers MUST update immediately to the documented new structure/behavior.

## 10) Compliance Checklist

- [ ] Exactly one empty version marker file exists in `.aib_brain/`.
- [ ] Marker uses `vMAJOR.MINOR.PATCH` format.
- [ ] Version bump type matches SemVer policy.
- [ ] PR includes rationale and migration detail (when applicable).
- [ ] `logs/` directory preserved and not modified by the upgrade.

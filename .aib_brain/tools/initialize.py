#!/usr/bin/env python3
"""
initialize.py: Initialize AIB memory structures and default artifacts.
Part of the AIB core tooling layer.
Responsibilities: seed .aib_memory/ from .aib_brain/ templates, create required
directories and files, create aib-setup.yaml setup file, run upgrade procedure
when --upgrade is given.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from common import (
    ValidationError,
    _INPUT_SEED_TEMPLATE,
    ensure_workspace,
    get_semver,
    get_setup_option,
    set_setup_option,
    print_error_and_exit,
    parse_args,
    write_text,
)


# Default value written to default_questions_number in a freshly seeded aib-setup.yaml.
_DEFAULT_QUESTIONS_NUMBER: int = 5

_CONTEXT_DATA_MODEL_EMPTY = (
    "# Context Data Model\n\n"
    "No data models are currently documented.\n"
)

_MANAGED_REFERENCES = (
    "## References\n\n"
    "### Context Data Model\n"
    "Location: .aib_memory/context-data-model.md\n"
    "Summary: Logical, physical, and analytical schemas, entities, and relationships discovered in the workspace.\n"
    "Convention: .aib_brain/conventions/context-data-model-convention.md\n"
    "Prompt: .aib_brain/prompts/aib-refresh-context-data-model.md\n"
    "Read: no\n"
    "Update: yes\n"
)


def _build_input_seed(minimum_questions: int) -> str:
    """Return the input.md seed content with *minimum_questions* substituted.

    Replaces the hardcoded fallback value in ``_INPUT_SEED_TEMPLATE`` with the
    given integer so the seeded file reflects workspace-level configuration.

    Args:
        minimum_questions: The value to write as minimum_questions in the
            YAML frontmatter.

    Returns:
        Full input.md seed content string.
    """
    return _INPUT_SEED_TEMPLATE.replace(
        "  minimum_questions: 5\n",
        f"  minimum_questions: {minimum_questions}\n",
    )


def _write_setup_file(path: Path, memory_version: str, default_questions_number: int) -> None:
    """Write a fresh aib-setup.yaml file with the given values.

    Overwrites the file if it already exists.

    Args:
        path: Target file path.
        memory_version: Version string to store as memory_version.
        default_questions_number: Value to store as default_questions_number.
    """
    content = (
        f"memory_version: {memory_version}\n"
        f"default_questions_number: {default_questions_number}\n"
        f"memory_version_compatibility: compatible\n"
    )
    write_text(path, content)


def _update_memory_version_in_setup(setup_path: Path, brain_semver: str) -> None:
    """Overwrite only the memory_version key in an existing aib-setup.yaml.

    Preserves all other key-value pairs.  Appends memory_version as a new line
    when it is absent from the file.

    Args:
        setup_path: Path to the existing aib-setup.yaml file.
        brain_semver: The new version string to set as memory_version.
    """
    content = setup_path.read_text(encoding="utf-8")
    updated_lines = []
    found = False
    for line in content.splitlines(keepends=True):
        if line.startswith("memory_version:"):
            updated_lines.append(f"memory_version: {brain_semver}\n")
            found = True
        else:
            updated_lines.append(line)
    if not found:
        updated_lines.append(f"memory_version: {brain_semver}\n")
    write_text(setup_path, "".join(updated_lines))


def _seed_memory(workspace: Path, brain_dir: Path, memory_root: Path, force: bool = False) -> None:
    """Seed the standard .aib_memory/ artifacts from .aib_brain/ templates.

    Creates required directories and seeds every default file. Existing files
    are skipped on idempotent re-runs.  Reads default_questions_number from
    aib-setup.yaml when available to configure the seeded input.md.

    Args:
        workspace: Resolved workspace root path.
        brain_dir: Path to the .aib_brain/ directory.
        memory_root: Path to the .aib_memory/ directory to seed.
        force: Reserved for future per-file overwrite behaviour.
    """
    (memory_root / "requests").mkdir(parents=True, exist_ok=True)

    # Scratch is the only AIB-managed repository location for short-lived helpers.
    # Idempotent seeding preserves any content already present during normal setup.
    scratch_dir = memory_root / "scratch"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    scratch_gitkeep = scratch_dir / ".gitkeep"
    if not scratch_gitkeep.exists():
        scratch_gitkeep.touch()
        print("Created scratch directory.")

    # Create the attachments staging folder used by aib-analyze.md as an
    # enriched input channel. A .gitkeep placeholder ensures the empty directory
    # is committed to VCS and available immediately after a fresh clone.
    attachments_dir = memory_root / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = attachments_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        print("Created attachments directory.")

    context_file = memory_root / "context.md"
    if context_file.exists():
        print("context.md already exists — skipping overwrite.")
    else:
        write_text(context_file, _generate_initial_context())

    data_model_file = memory_root / "context-data-model.md"
    if data_model_file.exists():
        print("context-data-model.md already exists — skipping overwrite.")
    else:
        write_text(data_model_file, _CONTEXT_DATA_MODEL_EMPTY)

    input_file = memory_root / "input.md"
    if input_file.exists():
        print("input.md already exists — skipping overwrite.")
    else:
        # Read default_questions_number from aib-setup.yaml when available so the
        # seeded input.md reflects workspace-level configuration.
        default_q = get_setup_option(memory_root, "default_questions_number")
        try:
            minimum_questions = int(default_q) if default_q is not None else _DEFAULT_QUESTIONS_NUMBER
        except ValueError:
            minimum_questions = _DEFAULT_QUESTIONS_NUMBER
        write_text(input_file, _build_input_seed(minimum_questions))

    # Seed instructions.md as the workspace-level persistent instructions file.
    # Idempotent: does not overwrite a file that already exists.
    instructions_file = memory_root / "instructions.md"
    if instructions_file.exists():
        print("instructions.md already exists — skipping overwrite.")
    else:
        write_text(instructions_file, "")


def _seed_setup(brain_dir: Path, memory_root: Path, force: bool = False) -> "str | None":
    """Seed aib-setup.yaml in *memory_root* with brain version and default settings.

    Skips seeding when the file already exists and force is False (idempotency).
    Removes any stale ``v*.*.*`` empty marker files from *memory_root* as part of
    legacy workspace cleanup.

    Args:
        brain_dir: Path to the .aib_brain/ directory.
        memory_root: Path to the .aib_memory/ directory.
        force: When True, overwrite any existing aib-setup.yaml.

    Returns:
        The brain semver string (e.g. ``"v1.2.8"``), or ``None`` when no brain
        semver marker was found.
    """
    brain_semver = get_semver(brain_dir)
    if not brain_semver:
        print("WARNING: No semver marker found in .aib_brain/ — skipping setup file seeding.")
        return None

    # Remove any stale empty version marker files left from older workspaces.
    for old_marker in memory_root.glob("v[0-9]*.[0-9]*.[0-9]*"):
        if old_marker.is_file():
            old_marker.unlink()

    setup_file = memory_root / "aib-setup.yaml"
    if setup_file.exists() and not force:
        print("aib-setup.yaml already exists in .aib_memory/ — skipping overwrite.")
        return brain_semver

    _write_setup_file(setup_file, brain_semver, _DEFAULT_QUESTIONS_NUMBER)
    return brain_semver


def _generate_context_placeholder() -> str:
    """Return a valid minimal context.md string that passes verify-context.py after upgrade.

    Generates a placeholder containing all five mandatory sections so that the
    upgraded workspace starts in a format-compliant state. The developer must
    replace this placeholder by running ``aib-modify.md`` with the migration
    instructions pre-loaded in ``input.md``.

    Returns:
        A conforming context.md string with title line, all five mandatory
        sections, and one placeholder bullet or line per section.
    """
    return (
        "# Product Context\n\n"
        "## Product\n\n"
        "- Migration in progress — run aib-modify.md with the migration instructions "
        "in input.md to reconstruct the workspace context.\n\n"
        "## Concepts\n\n"
        "- Migration in progress — concepts to be populated after running aib-modify.md "
        "with migration instructions.\n\n"
        "## Requirements\n\n"
        "- MUST: Execute aib-modify.md using the migration instructions in input.md to "
        "reconstruct the workspace context from archived legacy memory files before normal "
        "AIB workflows are used.\n\n"
        "## Solution\n\n"
        "- Migration in progress — solution statements to be populated after running "
        "aib-modify.md with migration instructions.\n\n"
        "## File Structure\n\n"
        ".aib_memory/\n"
        "  scratch/ — managed task-specific helpers swept during input finalization\n"
        "Migration in progress — remaining file structure to be populated after running "
        "aib-modify.md with migration instructions.\n\n"
        + _MANAGED_REFERENCES
    )


def _generate_initial_context() -> str:
    """Return a valid fresh-workspace context with the managed registry.

    Returns:
        A minimal context document that passes verify-context.py and directs the
        developer to run the context refresh prompt.
    """
    return (
        "# Product Context\n\n"
        "## Product\n\n"
        "- Workspace context awaits discovery through aib-refresh-context.md.\n\n"
        "## Concepts\n\n"
        "- Context extensions provide convention-managed supplementary workspace knowledge.\n\n"
        "## Requirements\n\n"
        "- MUST: Run aib-refresh-context.md to populate current workspace context before analysis.\n\n"
        "## Solution\n\n"
        "- AIB initializes context.md with a managed context extension registry.\n\n"
        "## File Structure\n\n"
        ".aib_memory/\n"
        "  context.md — workspace product context\n"
        "  context-data-model.md — managed data-model context extension\n"
        "  scratch/ — managed task-specific helpers swept during input finalization\n\n"
        + _MANAGED_REFERENCES
    )


def _generate_migration_input(archive_path: Path, memory_root: Path) -> str:
    """Generate a complete input.md string with a minimal migration activation paragraph.

    Builds on the standard input.md seed template and appends a single prose paragraph
    to ``## Input`` directing execution of ``aib-context-migration.md`` with the
    workspace-relative path to the archived legacy ``context.md``.

    When ``context.md`` is absent from the archive, references ``aib-refresh-context.md``
    instead so the developer can reconstruct context from the current workspace.

    Args:
        archive_path: Path to the timestamped archive folder containing the full
            pre-upgrade .aib_memory/ content.
        memory_root: Path to the new (post-upgrade) .aib_memory/ directory.

    Returns:
        Full input.md content string with idle YAML header and a single prose
        activation paragraph under ## Input (no sub-headings).
    """
    # Read default_questions_number from the already-seeded aib-setup.yaml.
    default_q = get_setup_option(memory_root, "default_questions_number")
    try:
        minimum_questions = int(default_q) if default_q is not None else _DEFAULT_QUESTIONS_NUMBER
    except ValueError:
        minimum_questions = _DEFAULT_QUESTIONS_NUMBER
    seed = _build_input_seed(minimum_questions)

    # Compute workspace-relative archive path with forward slashes.
    workspace_root = memory_root.parent
    relative_archive = archive_path.relative_to(workspace_root).as_posix()

    # Build a single prose paragraph based on whether the legacy context.md is present.
    if (archive_path / "context.md").is_file():
        migration_body = (
            f"Execute `.aib_brain/prompts/aib-context-migration.md` to reconstruct "
            f"`context.md` from the legacy archive. "
            f"[legacy context]: `{relative_archive}/context.md`. The migration also "
            "reconciles the managed Context Data Model registry and extension."
        )
    else:
        # context.md absent from archive: direct developer to refresh from workspace instead.
        migration_body = (
            f"`context.md` was not found in the legacy archive at `{relative_archive}/`. "
            "Execute `.aib_brain/prompts/aib-refresh-context.md` to create `context.md` "
            "from workspace inspection instead."
        )

    # Append the activation paragraph to the seed (seed ends with "## Input\n\n").
    return seed + migration_body + "\n"


def _run_upgrade(workspace: Path, brain_dir: Path, memory_root: Path) -> None:
    """Execute the full .aib_memory/ upgrade procedure.

    Archives the full current .aib_memory/ state (excluding any existing
    archive/ folder) to a timestamped ``legacy_YYYYMMDD-HHMMSS`` subfolder,
    seeds a fresh conforming memory structure, copies ``instructions.md``
    unchanged from the archive, generates a valid placeholder ``context.md``
    with all five mandatory sections, and generates migration-ready ``input.md``
    pre-loaded with structured migration instructions.

    Requests are never automatically restored to active memory; they remain
    exclusively in the timestamped archive for developer reference.

    Args:
        workspace: Resolved workspace root path.
        brain_dir: Path to the .aib_brain/ directory.
        memory_root: Path to the .aib_memory/ directory to upgrade.

    Raises:
        ValidationError: When no brain semver marker is found.
    """
    brain_semver = get_semver(brain_dir)
    if not brain_semver:
        raise ValidationError(
            "Cannot upgrade: no semver marker found in .aib_brain/. "
            "Ensure the brain directory contains a file named vMAJOR.MINOR.PATCH."
        )

    # Step 1 — Create timestamped archive directory.
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_dir = memory_root / "archives"
    archive_path = archive_dir / f"legacy_{timestamp}"
    # Ensure uniqueness when two upgrades happen within the same second.
    counter = 1
    while archive_path.exists():
        archive_path = archive_dir / f"legacy_{timestamp}-{counter}"
        counter += 1
    archive_path.mkdir(parents=True, exist_ok=True)

    # Step 2 — Copy all .aib_memory/ content (excluding archives/) into the archive.
    # Prevents the archives/ directory from being nested inside itself.
    for item in memory_root.iterdir():
        if item.name == "archives":
            # Existing archives stay at their current level — never nest them.
            continue
        dest = archive_path / item.name
        if item.is_dir():
            shutil.copytree(str(item), str(dest))
        else:
            shutil.copy2(str(item), str(dest))

    print(f"Archive created: {archive_path}")

    # Step 3 — Delete all non-archive content from .aib_memory/.
    for item in memory_root.iterdir():
        if item.name == "archives":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print("Cleared non-archive content from .aib_memory/")

    # Step 4 — Seed setup file using merge-restore strategy.
    # Must run before _seed_memory so input.md seeding can read default_questions_number.
    # When an archived aib-setup.yaml exists, restore it and update only
    # memory_version so user-configured values (e.g. default_questions_number) are preserved.
    archived_setup = archive_path / "aib-setup.yaml"
    if archived_setup.is_file():
        shutil.copy2(str(archived_setup), str(memory_root / "aib-setup.yaml"))
        _update_memory_version_in_setup(memory_root / "aib-setup.yaml", brain_semver)
    else:
        # No archived setup file; generate fresh defaults.
        _seed_setup(brain_dir, memory_root, force=True)

    # Step 5 — Re-seed .aib_memory/ from brain templates.
    _seed_memory(workspace, brain_dir, memory_root, force=False)

    # Step 6 — Restore instructions and scratch content from the archive.
    src_instructions = archive_path / "instructions.md"
    if src_instructions.exists():
        shutil.copy2(str(src_instructions), str(memory_root / "instructions.md"))

    archived_scratch = archive_path / "scratch"
    if archived_scratch.is_dir():
        # Upgrade re-seeding recreates scratch first; merge the archived tree so no
        # task-specific content is lost merely because the framework was upgraded.
        shutil.copytree(
            str(archived_scratch),
            str(memory_root / "scratch"),
            dirs_exist_ok=True,
        )

    # Step 7 — Generate placeholder context.md and migration-ready input.md.
    write_text(memory_root / "context.md", _generate_context_placeholder())
    write_text(memory_root / "input.md", _generate_migration_input(archive_path, memory_root))

    print("\nUpgrade summary:")
    print(f"  Brain version   : {brain_semver}")
    print(f"  Archive location: {archive_path}")
    print(f"  Restored files  : instructions.md and scratch/")
    print(f"  Requests        : archived in {archive_path}")
    print("\n.aib_memory/ upgrade complete.")
    set_setup_option(memory_root, "memory_version_compatibility", "initialized-not-populated")


def main() -> None:
    """Entry point for the initialize script.

    Parses arguments and either runs the upgrade procedure (--upgrade) or the
    standard idempotent seeding procedure. Exits with a non-zero code on error.
    """
    args = parse_args("Initialize AIB memory structure")
    workspace = Path(args.workspace).resolve()

    try:
        ensure_workspace(workspace)

        memory_root = workspace / ".aib_memory"
        brain_dir = workspace / ".aib_brain"

        if args.upgrade:
            # Upgrade path: back up, clean, re-seed, restore.
            memory_root.mkdir(parents=True, exist_ok=True)
            _run_upgrade(workspace, brain_dir, memory_root)
        else:
            # Standard idempotent initialization path.
            memory_root.mkdir(parents=True, exist_ok=True)
            # Seed the setup file first so _seed_memory can read default_questions_number.
            _seed_setup(brain_dir, memory_root, force=args.force)
            _seed_memory(workspace, brain_dir, memory_root, force=args.force)
            print("Initialized .aib_memory structure successfully.")

    except ValidationError as exc:
        print_error_and_exit(str(exc))


if __name__ == "__main__":
    main()

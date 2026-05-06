#!/usr/bin/env python3
"""
move-request-artifacts.py: Move active-request artifacts from .aib_memory/ root
to the active request's subfolder.
Part of the AIB tool scripts. Invoked by aib-implement.md (pre-close) and
close-request.py (safety net).
Responsibilities: locate the active request folder, move request.md, analysis.md,
and UAT_scenarios.md from .aib_memory/ to the request subfolder; idempotent.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from common import (
    ValidationError,
    ensure_workspace,
    parse_args,
    read_text,
    parse_markdown_table,
    requests_register_path,
    ACTIVE,
)

# Names of the artifact files that live at .aib_memory/ root while a request is active.
_ARTIFACT_NAMES = ("request.md", "analysis.md", "UAT_scenarios.md")


def move_artifacts(workspace: Path) -> None:
    """Move active-request artifacts from .aib_memory/ root to the active request subfolder.

    Reads requests_register.md to resolve the active request folder.
    For each artifact (request.md, analysis.md, UAT_scenarios.md):
      - If the source exists at .aib_memory/<artifact>, moves it to the request subfolder.
      - If the source does not exist, skips silently (idempotent).
    Calling this function a second time is safe: no sources remain at root after
    the first successful move, so the second call is a no-op.

    Args:
        workspace: Resolved absolute path to the workspace root.

    Raises:
        ValidationError: If the workspace is invalid, the register is missing,
                         or no active request is found.
    """
    ensure_workspace(workspace)

    register = requests_register_path(workspace)
    if not register.exists():
        raise ValidationError("Missing requests_register.md; run initialize first")

    header, rows = parse_markdown_table(read_text(register))
    if not header:
        raise ValidationError("requests_register.md has no valid table")

    col = {name: idx for idx, name in enumerate(header)}
    active = [r for r in rows if r[col["state"]] == ACTIVE]
    if len(active) == 0:
        raise ValidationError("No active request found; cannot move artifacts")
    if len(active) > 1:
        raise ValidationError("Multiple active requests found; resolve register inconsistency")

    folder_rel = active[0][col["folder"]]
    dest_folder = workspace / folder_rel
    dest_folder.mkdir(parents=True, exist_ok=True)

    aib_memory = workspace / ".aib_memory"

    for artifact in _ARTIFACT_NAMES:
        source = aib_memory / artifact
        dest = dest_folder / artifact
        if source.exists():
            # shutil.move handles cross-filesystem moves unlike os.rename
            shutil.move(str(source), str(dest))
            print(f"Moved: {source.relative_to(workspace)} -> {dest.relative_to(workspace)}")
        else:
            print(f"Skipped (not found): .aib_memory/{artifact}")


def main() -> None:
    """Entry point: resolve workspace, run move_artifacts, exit cleanly."""
    args = parse_args("Move active-request artifacts to request subfolder")
    workspace = Path(args.workspace).resolve()

    try:
        move_artifacts(workspace)
    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

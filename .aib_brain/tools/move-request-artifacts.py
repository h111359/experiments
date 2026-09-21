#!/usr/bin/env python3
"""
move-request-artifacts.py: Move active-request artifacts from .aib_memory/ root
to the active request's subfolder and archive shared audit streams.
Part of the AIB tool scripts. Invoked by aib-implement.md (pre-close) and
close-request.py (safety net).
Responsibilities: locate the active request folder; move plan-<ID>.md and
analysis-<ID>.md from .aib_memory/ to the request subfolder; rename-to-staging
then binary-append the shared runtime log and clarification history into
request-scoped archives with fsync-before-cleanup durability.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path

from common import (
    ValidationError,
    artifact_name,
    ensure_workspace,
    parse_args,
    read_input_header,
    slugify,
)

# Artifact types that live at .aib_memory/ root while a request is active.
# The actual filenames are constructed dynamically using artifact_name() so
# that each file carries the request ID, preventing merge conflicts across branches.
_ARTIFACT_TYPES = ("plan", "analysis")

# Fixed filename of the shared active runtime log at .aib_memory/ root.
_ACTIVE_LOG_FILENAME = "log.md"

# Chunk size used for streaming the staged snapshot into the archive.
_ARCHIVE_CHUNK_BYTES = 64 * 1024


class SharedArchiveError(ValidationError):
    """Base failure for an audit stream whose archival must block closure."""

    label = "shared-archive"


class LogArchiveError(SharedArchiveError):
    """Raised when the shared-log archival transaction cannot proceed safely."""

    label = "log-archive"


class ClarificationArchiveError(SharedArchiveError):
    """Raised when clarification-history archival cannot proceed safely."""

    label = "clarification-history-archive"


def _require_regular_file(path: Path) -> None:
    """Ensure *path* is a regular non-symlink file or does not exist.

    Args:
        path: Path to verify.

    Raises:
        SharedArchiveError: If *path* exists but is a symlink, directory, or other
            special file type.
    """
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink():
        raise SharedArchiveError(f"archive path is a symlink and cannot be archived: {path}")
    st = os.stat(path, follow_symlinks=False)
    if not stat.S_ISREG(st.st_mode):
        raise SharedArchiveError(f"archive path is not a regular file: {path}")


def _archive_needs_separator(archive_path: Path) -> bool:
    """Return True when the existing archive is non-empty and lacks a trailing newline.

    Args:
        archive_path: Destination archive file path.

    Returns:
        True when a single newline separator must be written before appending
        the next snapshot; False otherwise.
    """
    if not archive_path.exists():
        return False
    size = archive_path.stat().st_size
    if size == 0:
        return False
    with archive_path.open("rb") as fh:
        fh.seek(-1, os.SEEK_END)
        return fh.read(1) != b"\n"


def _append_snapshot(staging_path: Path, archive_path: Path) -> None:
    """Append the staged snapshot to the archive with durability guarantees.

    Streams *staging_path* into *archive_path* in binary mode using a bounded
    chunk buffer, inserts a single newline separator only when both files are
    non-empty and the archive lacks a trailing newline, fsyncs the archive, and
    removes the staging file only after fsync succeeds.

    Args:
        staging_path: Rename-to-staging snapshot of the shared audit stream.
        archive_path: Destination archive file inside the request subfolder.
    """
    staging_size = staging_path.stat().st_size
    needs_separator = staging_size > 0 and _archive_needs_separator(archive_path)

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("ab") as archive_fh:
        if needs_separator:
            archive_fh.write(b"\n")
        with staging_path.open("rb") as staging_fh:
            while True:
                chunk = staging_fh.read(_ARCHIVE_CHUNK_BYTES)
                if not chunk:
                    break
                archive_fh.write(chunk)
        archive_fh.flush()
        os.fsync(archive_fh.fileno())

    # Only remove the staging file after fsync succeeded to preserve
    # at-least-once delivery semantics across crashes.
    staging_path.unlink()


def _archive_shared_stream(
    workspace: Path,
    request_id: str,
    dest_folder: Path,
    stream_name: str,
    error_type: type[SharedArchiveError],
) -> None:
    """Rotate an audit stream, preserving staged bytes until the archive is durable.

    Args:
        workspace: Resolved workspace root path.
        request_id: Active request identifier.
        dest_folder: Destination request subfolder for the archive.
        stream_name: Filename stem shared by active, staged, and archived files.
        error_type: Stream-specific exception used for all archival failures.

    Raises:
        SharedArchiveError: On unexpected path types or I/O failures. Staged
            content is retained for at-least-once recovery on the next call.
    """
    aib_memory = workspace / ".aib_memory"
    root_stream = aib_memory / f"{stream_name}.md"
    staging_stream = aib_memory / f"{stream_name}-staging-{request_id}.md"
    archive_stream = dest_folder / f"{stream_name}_{request_id}.md"

    try:
        for path in (root_stream, staging_stream, archive_stream):
            _require_regular_file(path)

        # Recover earlier bytes before rotating newer entries to preserve order.
        if staging_stream.exists():
            _append_snapshot(staging_stream, archive_stream)

        if root_stream.exists():
            os.replace(root_stream, staging_stream)
            root_stream.touch()
            _append_snapshot(staging_stream, archive_stream)
        else:
            archive_stream.parent.mkdir(parents=True, exist_ok=True)
            archive_stream.touch(exist_ok=True)
            root_stream.touch()
    except (OSError, SharedArchiveError) as exc:
        # I/O failures must never reach close-request's warn-and-continue path.
        raise error_type(f"{root_stream}: {exc}") from exc


def _archive_shared_log(workspace: Path, request_id: str, dest_folder: Path) -> None:
    """Archive the runtime log using the shared durable rotation transaction."""
    _archive_shared_stream(workspace, request_id, dest_folder, "log", LogArchiveError)


def move_artifacts(workspace: Path) -> None:
    """Move active-request artifacts and archive both shared audit streams.

    Reads the input.md YAML header to resolve the active request folder and
    request ID. For each artifact type (plan, analysis) moves the ID-suffixed
    file from .aib_memory/ to the request subfolder when present. Archives the
    runtime log and clarification history via the same rename-to-staging
    transaction before moving any plan or analysis files.

    Args:
        workspace: Resolved absolute path to the workspace root.

    Raises:
        ValidationError: When the workspace is invalid, the input.md header is
            missing, or no active request is found.
        SharedArchiveError: When either audit-stream archival transaction fails.
    """
    ensure_workspace(workspace)

    # Read active request state from input.md YAML header.
    header = read_input_header(workspace)
    if header["state"]["status"] == "idle":
        raise ValidationError("No active request found; cannot move artifacts")

    request_id = header["state"]["request_id"].strip()
    title = header["state"]["title"]
    # Derive folder path using the same slugify convention as create-request.py.
    folder_name = f"{request_id}-{slugify(title)}"
    folder_rel = f".aib_memory/requests/{folder_name}"
    dest_folder = workspace / folder_rel
    aib_memory = workspace / ".aib_memory"

    # Archive the shared runtime log FIRST so a failure in the fail-closed
    # log-archive transaction aborts before any other artifact is moved.
    _archive_shared_log(workspace, request_id, dest_folder)
    print(
        f"Archived: .aib_memory/{_ACTIVE_LOG_FILENAME} -> "
        f"{(dest_folder / f'log_{request_id}.md').relative_to(workspace)}"
    )

    _archive_shared_stream(
        workspace, request_id, dest_folder, "clarification_questions", ClarificationArchiveError
    )
    print(
        "Archived: .aib_memory/clarification_questions.md -> "
        f"{(dest_folder / f'clarification_questions_{request_id}.md').relative_to(workspace)}"
    )

    for artifact_type in _ARTIFACT_TYPES:
        # Construct the ID-suffixed filename (e.g. "plan-R-20260509-2313.md").
        filename = artifact_name(artifact_type, request_id)
        source = aib_memory / filename
        # Archived artifacts keep their ID-suffixed names inside the subfolder.
        dest = dest_folder / filename
        if source.exists():
            # shutil.move handles cross-filesystem moves unlike os.rename
            shutil.move(str(source), str(dest))
            print(f"Moved: {source.relative_to(workspace)} -> {dest.relative_to(workspace)}")
        else:
            print(f"Skipped (not found): .aib_memory/{filename}")


def main() -> None:
    """Entry point: resolve workspace, run move_artifacts, exit cleanly."""
    args = parse_args("Move active-request artifacts to request subfolder")
    workspace = Path(args.workspace).resolve()

    try:
        move_artifacts(workspace)
    except SharedArchiveError as exc:
        print(f"ERROR: {exc.label}: {exc}", file=sys.stderr)
        raise SystemExit(2)
    except ValidationError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

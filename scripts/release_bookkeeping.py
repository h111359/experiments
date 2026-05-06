#!/usr/bin/env python3
"""
release_bookkeeping.py: AIB CI release bookkeeping tool.

Validates the SemVer marker in `.aib_brain/`, computes the next PATCH version,
rotates the marker file, writes `logs/version_vX.Y.Z_log.md`, and creates a
versioned zip of `.aib_brain/` under `versions/`. The `Changes:` section of the
generated log prefers curated entries from `logs/next_version_changes.md` when
present and non-empty; otherwise it falls back to git commit subjects.

Part of the AIB release automation invoked by
`.github/workflows/aib-semver-patch-bump-and-log.yml`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_MARKER_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


class ReleaseBookkeepingError(RuntimeError):
    pass


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse_marker(cls, marker: str) -> "Version":
        match = _MARKER_RE.match(marker)
        if not match:
            raise ReleaseBookkeepingError(
                f"Malformed SemVer marker filename '{marker}'. Expected format 'vMAJOR.MINOR.PATCH'."
            )
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
        )

    def bump_patch(self) -> "Version":
        return Version(self.major, self.minor, self.patch + 1)

    def to_marker(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def to_heading(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def _run_git(args: list[str], *, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return completed.stdout
    except FileNotFoundError as exc:
        raise ReleaseBookkeepingError("git is required but was not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise ReleaseBookkeepingError(f"git command failed: git {' '.join(args)}\n{stderr}") from exc


def _markers_from_ls_tree(ref: str, brain_dir: str) -> list[str]:
    out = _run_git(["ls-tree", "--name-only", f"{ref}:{brain_dir}"])
    candidates = [line.strip() for line in out.splitlines() if line.strip()]
    markers = [name for name in candidates if _MARKER_RE.match(name)]
    return sorted(markers)


def _markers_from_worktree(brain_path: Path) -> list[str]:
    if not brain_path.exists():
        raise ReleaseBookkeepingError(f"Expected '{brain_path.as_posix()}' to exist.")
    if not brain_path.is_dir():
        raise ReleaseBookkeepingError(f"Expected '{brain_path.as_posix()}' to be a directory.")

    markers: list[str] = []
    for child in brain_path.iterdir():
        if child.is_file() and _MARKER_RE.match(child.name):
            markers.append(child.name)

    return sorted(markers)


def _require_single_marker(markers: list[str], *, where: str) -> str:
    if len(markers) == 0:
        raise ReleaseBookkeepingError(
            f"SemVer marker precondition failed: expected exactly 1 marker file in {where}, found 0."
        )
    if len(markers) != 1:
        raise ReleaseBookkeepingError(
            f"SemVer marker precondition failed: expected exactly 1 marker file in {where}, found {len(markers)}: {markers}"
        )
    return markers[0]


def _normalize_subjects(lines: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    for raw in lines:
        text = " ".join(raw.strip().split())
        if text:
            normalized.append(text)
    return normalized


def _read_commit_subjects(path: Path | None) -> list[str]:
    if path is None:
        return []
    if not path.exists():
        raise ReleaseBookkeepingError(f"Commit subjects file not found: {path.as_posix()}")
    return _normalize_subjects(path.read_text(encoding="utf-8").splitlines())


def _read_curated_entries(path: Path | None) -> list[str]:
    """Read curated change bullets from `logs/next_version_changes.md`.

    Args:
        path: Path to the curated change log file, or None if not provided.

    Returns:
        A list of normalized bullet text lines (the leading `- ` marker is
        stripped). Returns an empty list when the path is None, the file does
        not exist, or the file contains no bullet entries. A missing file is
        treated as an empty curated source so callers can fall back to commit
        subjects without error.
    """
    if path is None:
        return []
    # Absent file is a valid empty curated source (fallback path expected).
    if not path.exists():
        return []

    entries: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        # Accept only Markdown bullet lines per the instructions.md directive.
        if stripped.startswith("- "):
            text = stripped[2:].strip()
        elif stripped.startswith("-"):
            text = stripped[1:].strip()
        else:
            # Non-bullet content is ignored to keep the curated source strict.
            continue
        # Collapse internal whitespace for stable, idempotent output.
        text = " ".join(text.split())
        if text:
            entries.append(text)
    return entries


def _reset_curated_file(path: Path) -> None:
    """Clear the curated change log file to empty content.

    Used as the lifecycle reset after curated entries have been incorporated
    into the per-version log. Keeps the file VCS-tracked (created if missing)
    so subsequent implementation runs can append again.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def _write_version_log(
    *,
    log_path: Path,
    version_heading: str,
    issue: str | None,
    pr_number: str | None,
    commit_subjects: list[str],
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    now_utc = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines.append(f"## Version {version_heading}")
    lines.append("")
    if issue:
        lines.append(f"### Issue #{issue}")
        lines.append("")
    if pr_number:
        lines.append(f"PR #{pr_number}")
        lines.append("")

    lines.append(f"Generated by GitHub Actions on {now_utc}.")
    lines.append("")

    if commit_subjects:
        lines.append("Changes:")
        for subject in commit_subjects:
            lines.append(f"- {subject}")
    else:
        lines.append("Changes:")
        lines.append("- (no commit subjects detected)")

    lines.append("")

    log_path.write_text("\n".join(lines), encoding="utf-8")


def _rotate_marker(brain_path: Path, old_marker: str, new_marker: str) -> None:
    old_path = brain_path / old_marker
    new_path = brain_path / new_marker

    if new_path.exists():
        return

    if not old_path.exists():
        raise ReleaseBookkeepingError(
            f"Expected marker file '{old_path.as_posix()}' to exist before rotation, but it does not."
        )

    old_path.unlink()
    new_path.write_text("", encoding="utf-8")


def _create_brain_zip(brain_path: Path, versions_dir: Path, version_marker: str) -> Path:
    """Create a versioned zip archive of brain_path in versions_dir.

    The archive is named ``aib_brain_<version_marker>.zip`` and is placed in
    ``versions_dir``.  If the target zip already exists, creation is skipped
    (idempotent).

    Returns the path to the zip file (whether created or pre-existing).
    """
    versions_dir.mkdir(parents=True, exist_ok=True)
    zip_path = versions_dir / f"aib_brain_{version_marker}.zip"

    # Idempotency: skip if already created for this version.
    if zip_path.exists():
        return zip_path

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(brain_path.rglob("*")):
            if file_path.is_file():
                # Archive relative to the parent of brain_path so the zip
                # contains a .aib_brain/ top-level folder.
                arcname = file_path.relative_to(brain_path.parent)
                zf.write(file_path, arcname)

    return zip_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Automated release bookkeeping: validates SemVer marker, bumps PATCH, rotates marker file, "
            "creates a per-version log file under logs/, and archives .aib_brain/ to versions/."
        )
    )
    parser.add_argument(
        "--base-ref",
        required=True,
        help="Git ref for the base branch (e.g. origin/main). Used to compute the next version deterministically.",
    )
    parser.add_argument("--brain-dir", default=".aib_brain", help="Path to .aib_brain directory.")
    parser.add_argument("--log-dir", default="logs", help="Path to logs directory.")
    parser.add_argument(
        "--issue",
        default=None,
        help=(
            "Optional issue number to record in the version log (e.g., 17). "
            "If omitted, no Issue section is written."
        ),
    )
    parser.add_argument("--pr-number", default=None, help="PR number for traceability.")
    parser.add_argument(
        "--commit-subjects-file",
        default=None,
        help="Text file with one commit subject per line (will be normalized).",
    )
    parser.add_argument(
        "--next-version-changes-file",
        default=None,
        help=(
            "Curated change log file (e.g. logs/next_version_changes.md). When present "
            "and non-empty, its Markdown bullets are preferred over commit subjects as "
            "the Changes: source. After successful incorporation the file is reset to empty."
        ),
    )
    parser.add_argument(
        "--github-output",
        default=None,
        help="If set, append step outputs in GitHub Actions GITHUB_OUTPUT format.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and compute outputs without writing any files.",
    )

    args = parser.parse_args(argv)

    brain_path = Path(args.brain_dir)
    log_dir = Path(args.log_dir)
    commit_subjects = _read_commit_subjects(Path(args.commit_subjects_file) if args.commit_subjects_file else None)
    curated_path = Path(args.next_version_changes_file) if args.next_version_changes_file else None
    curated_entries = _read_curated_entries(curated_path)
    # Source preference: curated entries first; commit subjects as fallback.
    if curated_entries:
        change_entries = curated_entries
        used_curated = True
    else:
        change_entries = commit_subjects
        used_curated = False
    # Reconstruct the curated body as Markdown bullet lines for the commit message.
    # Captured here (before any lifecycle reset) so it is available for GITHUB_OUTPUT.
    changes_body = "\n".join(f"- {e}" for e in curated_entries)
    issue_value = (str(args.issue).strip() if args.issue is not None else None) or None

    base_markers = _markers_from_ls_tree(args.base_ref, args.brain_dir)
    base_marker = _require_single_marker(base_markers, where=f"{args.base_ref}:{args.brain_dir}")

    head_markers = _markers_from_worktree(brain_path)
    head_marker = _require_single_marker(head_markers, where=brain_path.as_posix())

    base_version = Version.parse_marker(base_marker)
    target_version = base_version.bump_patch()
    target_marker = target_version.to_marker()

    # Ensure the PR branch marker state is consistent.
    if head_marker not in (base_marker, target_marker):
        raise ReleaseBookkeepingError(
            "SemVer marker state mismatch between base and PR branch. "
            f"Base marker is '{base_marker}', but PR branch marker is '{head_marker}'. "
            "Rebase the PR branch onto the latest base branch and rerun."
        )

    log_path = log_dir / f"version_{target_marker}_log.md"

    # NOTE: Intentionally allow multiple per-version logs to coexist in logs/.
    # The repository is expected to keep historical logs, and workflow reruns/base advances
    # may legitimately result in multiple version_v*_log.md files being present.

    if args.dry_run:
        print(f"Computed new version: {target_marker}")
        print(f"Log file path: {log_path.as_posix()}")
        if args.github_output:
            with Path(args.github_output).open("a", encoding="utf-8") as fp:
                fp.write(
                    f"new_version={target_marker}\nlog_path={log_path.as_posix()}\nchanged=false\n"
                    f"changes_body<<AIB_CHANGES_BODY_EOF\n{changes_body}\nAIB_CHANGES_BODY_EOF\n"
                )
        return 0

    # Idempotency for pre-merge workflow runs: if log already exists AND marker already bumped, treat as done.
    if log_path.exists() and head_marker == target_marker:
        print("No changes needed; target log and marker already present.")
        if args.github_output:
            with Path(args.github_output).open("a", encoding="utf-8") as fp:
                fp.write(
                    f"new_version={target_marker}\nlog_path={log_path.as_posix()}\nchanged=false\n"
                    f"changes_body<<AIB_CHANGES_BODY_EOF\n{changes_body}\nAIB_CHANGES_BODY_EOF\n"
                )
        return 0

    if log_path.exists() and head_marker == base_marker:
        raise ReleaseBookkeepingError(
            f"Target log file already exists but marker was not bumped: '{log_path.as_posix()}'. "
            "Refusing to bump marker to avoid inconsistent state."
        )

    if head_marker == base_marker:
        _write_version_log(
            log_path=log_path,
            version_heading=target_version.to_heading(),
            issue=issue_value,
            pr_number=str(args.pr_number) if args.pr_number else None,
            commit_subjects=change_entries,
        )
        _rotate_marker(brain_path, base_marker, target_marker)
        zip_path = _create_brain_zip(brain_path, log_dir.parent / "versions", target_marker)
        print(f"Created brain archive: {zip_path.as_posix()}")
        changed = True
    else:
        # Marker already bumped to target_marker; ensure log and zip exist.
        _write_version_log(
            log_path=log_path,
            version_heading=target_version.to_heading(),
            issue=issue_value,
            pr_number=str(args.pr_number) if args.pr_number else None,
            commit_subjects=change_entries,
        )
        zip_path = _create_brain_zip(brain_path, log_dir.parent / "versions", target_marker)
        print(f"Created brain archive: {zip_path.as_posix()}")
        changed = True

    # Lifecycle reset: only after curated entries were incorporated into the log.
    # Skipped on the idempotent no-op early-exit branches above so reruns stay stable.
    if changed and used_curated and curated_path is not None:
        _reset_curated_file(curated_path)
        print(f"Reset curated change log: {curated_path.as_posix()}")

    print(f"Computed new version: {target_marker}")
    print(f"Log file path: {log_path.as_posix()}")

    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as fp:
            fp.write(
                f"new_version={target_marker}\nlog_path={log_path.as_posix()}\nchanged={'true' if changed else 'false'}\n"
                f"changes_body<<AIB_CHANGES_BODY_EOF\n{changes_body}\nAIB_CHANGES_BODY_EOF\n"
            )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ReleaseBookkeepingError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)

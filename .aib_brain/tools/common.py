#!/usr/bin/env python3
"""Shared helpers for AIB tool scripts."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import List, Sequence

ACTIVE = "Active"
CLOSED = "Closed"

REQ_ID_PATTERN = re.compile(r"^R-\d{8}-\d{4}$")


class ValidationError(RuntimeError):
    """Raised on deterministic validation failures."""


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--workspace", default=".", help="Workspace root path")
    parser.add_argument("--request-id", default=None, help="Explicit request ID")
    parser.add_argument("--title", default=None, help="Request title (create-request only)")
    parser.add_argument("--summary", default="", help="Short summary text")
    parser.add_argument("--force", action="store_true", default=False, help="Force overwrite of existing files (initialize only)")
    parser.add_argument("--upgrade", action="store_true", default=False, help="Upgrade .aib_memory/ structure from .aib_brain/ templates (initialize only)")
    return parser.parse_args()


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def now_compact_request_id(now: dt.datetime | None = None) -> str:
    value = now or now_local()
    return f"R-{value.strftime('%Y%m%d-%H%M')}"


def now_iso(now: dt.datetime | None = None) -> str:
    value = now or now_local()
    return value.strftime("%Y-%m-%d %H:%M:%S %z")


def slugify(text: str, max_length: int = 64) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    lowered = lowered[:max_length].rstrip("-")
    return lowered or "request"


def get_semver(directory: Path) -> "str | None":
    """Return the semver marker file name found in *directory*, or None.

    Scans *directory* for files matching the ``vMAJOR.MINOR.PATCH`` pattern.
    Returns the file name (e.g. ``"v1.2.8"``) when exactly one match is found.
    Returns ``None`` when zero or multiple matches are found (fail-safe).

    Args:
        directory: Filesystem path of the directory to scan.

    Returns:
        The semver marker file name, or None if not found or ambiguous.
    """
    if not directory.is_dir():
        return None
    matches = list(directory.glob("v[0-9]*.[0-9]*.[0-9]*"))
    # Only consider plain files, not subdirectories; require exactly one match.
    file_matches = [m for m in matches if m.is_file()]
    if len(file_matches) == 1:
        return file_matches[0].name
    return None


def ensure_workspace(workspace: Path) -> None:
    if not workspace.exists() or not workspace.is_dir():
        raise ValidationError(f"Workspace does not exist: {workspace}")
    if not (workspace / ".aib_brain").exists():
        raise ValidationError("Missing .aib_brain/ folder in workspace")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def requests_root(workspace: Path) -> Path:
    return workspace / ".aib_memory" / "requests"


def _yaml_quote(value: str) -> str:
    """Return *value* single-quoted when it contains YAML special characters.

    Plain values (null marker ``~`` and values with no YAML-special characters)
    are returned as-is.  All other strings are wrapped in single quotes with
    embedded single-quote characters escaped as ``''`` (YAML 1.2 convention).

    Args:
        value: The string value to quote.

    Returns:
        The value unchanged or wrapped in single quotes.
    """
    if value == "~":
        return "~"
    _YAML_SPECIAL = set(":#{}[]|>&*!,'`\"")
    if any(c in value for c in _YAML_SPECIAL):
        return "'" + value.replace("'", "''") + "'"
    return value


def parse_input_header(content: str) -> "dict | None":
    """Parse YAML frontmatter block from *content* (input.md text).

    Supports the fixed AIB header schema only: four top-level keys
    (``request_id``, ``title``, ``state``) plus one nested dict
    (``options.minimum_questions``).  No external YAML library required.

    Args:
        content: Full text of input.md.

    Returns:
        Dict with keys ``request_id``, ``title``, ``state``, and
        ``options`` (a nested dict with key ``minimum_questions``).
        Returns ``None`` when no valid ``---`` frontmatter block is found.
    """
    import re as _re

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return None

    header: dict = {
        "request_id": "~",
        "title": "~",
        "state": "idle",
        "options": {"minimum_questions": 0},
    }
    in_options = False
    for line in lines[1:end_idx]:
        if line.rstrip() == "options:":
            in_options = True
            continue
        if in_options:
            m = _re.match(r"^\s+minimum_questions:\s*(\S+)", line)
            if m:
                try:
                    header["options"]["minimum_questions"] = int(m.group(1))
                except ValueError:
                    header["options"]["minimum_questions"] = 0
            continue
        m = _re.match(r"^(\w+):\s*(.*)", line)
        if m:
            key, raw = m.group(1), m.group(2).strip()
            # Strip surrounding single or double quotes.
            if len(raw) >= 2:
                if (raw[0] == "'" and raw[-1] == "'") or (raw[0] == '"' and raw[-1] == '"'):
                    raw = raw[1:-1].replace("''", "'")
            header[key] = raw
    return header


def write_input_header(content: str, header: dict) -> str:
    """Replace the YAML frontmatter block in *content* with *header* and return the result.

    The body of input.md (everything after the closing ``---`` delimiter) is
    preserved unchanged.  When no frontmatter block exists the new block is
    prepended to the existing content.

    Args:
        content: Current full text of input.md.
        header: Dict with keys ``request_id``, ``title``, ``state``, and
                ``options`` (nested dict with key ``minimum_questions``).

    Returns:
        Updated input.md text with the frontmatter block replaced.
    """
    lines = content.splitlines(keepends=True)
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break
    body = "".join(lines[body_start:])

    req_id = _yaml_quote(str(header.get("request_id", "~")))
    title = _yaml_quote(str(header.get("title", "~")))
    state = str(header.get("state", "idle"))
    min_q = int(header.get("options", {}).get("minimum_questions", 0))

    frontmatter = (
        "---\n"
        f"request_id: {req_id}\n"
        f"title: {title}\n"
        f"state: {state}\n"
        "options:\n"
        f"  minimum_questions: {min_q}\n"
        "---\n"
    )
    return frontmatter + body


def read_input_header(workspace: Path) -> dict:
    """Read and parse the YAML frontmatter header from input.md in *workspace*.

    Args:
        workspace: Resolved absolute path to the workspace root.

    Returns:
        Parsed header dict (see ``parse_input_header``).

    Raises:
        ValidationError: When input.md is missing or has no valid YAML header.
    """
    input_path = workspace / ".aib_memory" / "input.md"
    if not input_path.exists():
        raise ValidationError("input.md not found; run initialize first")
    content = read_text(input_path)
    header = parse_input_header(content)
    if header is None:
        raise ValidationError("input.md does not contain a valid YAML frontmatter header")
    return header


REQUIRED_PLAN_SECTIONS = [
    "## Goal",
    "## Constraints",
    "## Success criteria",
    "## Plan",
]


def validate_plan_md(path: Path) -> None:
    """Raise ValidationError if ``plan.md`` is missing any required section."""
    content = read_text(path)
    if not content:
        raise ValidationError(f"plan.md is empty or missing: {path}")
    for heading in REQUIRED_PLAN_SECTIONS:
        # Match heading at the start of a line, case-insensitive
        if not re.search(r"^" + re.escape(heading), content, re.IGNORECASE | re.MULTILINE):
            raise ValidationError(
                f"plan.md missing required section '{heading}': {path}"
            )


def artifact_name(artifact_type: str, request_id: str) -> str:
    """Construct the active-phase artifact filename for a given artifact type and request ID.

    Active-phase artifacts reside at ``.aib_memory/<artifact_type>-<request_id>.md``
    while the request is open. This helper centralises filename construction to avoid
    scattered string literals across tool scripts and prompts.

    Args:
        artifact_type: Artifact category; one of ``"plan"``, ``"analysis"``,
            or ``"UAT_scenarios"``.
        request_id: The request identifier, which must match the pattern
            ``R-YYYYMMDD-HHmi`` (e.g. ``"R-20260509-2313"``).

    Returns:
        The filename string, e.g. ``"plan-R-20260509-2313.md"``.

    Raises:
        ValueError: If ``request_id`` does not match the expected pattern, to
            prevent path traversal via malformed identifiers.
    """
    if not REQ_ID_PATTERN.match(request_id):
        raise ValueError(
            f"Invalid request_id '{request_id}'; expected pattern R-YYYYMMDD-HHmi"
        )
    return f"{artifact_type}-{request_id}.md"


def print_error_and_exit(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

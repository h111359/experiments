#!/usr/bin/env python3
"""Shared helpers for AIB tool scripts."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

ACTIVE = "Active"
CLOSED = "Closed"
COMPLETED = "Completed"

REQ_ID_PATTERN = re.compile(r"^R-\d{8}-\d{4}$")
ITER_ID_PATTERN = re.compile(r"^\d{2}$")
REQ_HEADING_PATTERN = re.compile(
    r"^\s*#{5}\s+([A-Z]{3,4}-\d{2})\s+[\-\u2012\u2013\u2014\u2015]\s+(.+?)\s+\*\*\[[CHR]\]\*\*\s*$"
)
LOCATION_PATTERN = re.compile(r"^\s*(?:Location|Evidence\s+location):\s+\*\*(.+?)\*\*\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class RequirementRef:
    req_id: str
    title: str
    location: str


class ValidationError(RuntimeError):
    """Raised on deterministic validation failures."""


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--workspace", default=".", help="Workspace root path")
    parser.add_argument("--request-id", default=None, help="Explicit request ID")
    parser.add_argument("--title", default=None, help="Request title (create-request only)")
    parser.add_argument("--summary", default="", help="Short summary text")
    parser.add_argument("--iteration-id", default=None, help="Explicit iteration ID")
    parser.add_argument("--force", action="store_true", default=False, help="Force overwrite of existing files (initialize only)")
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


def parse_markdown_table(content: str) -> Tuple[List[str], List[List[str]]]:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]
    if len(table_lines) < 2:
        return [], []

    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows: List[List[str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        rows.append(cells[: len(header)])
    return header, rows


def format_markdown_table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    sep = ["---"] * len(header)
    out = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows:
        vals = [str(v).replace("\n", " ").strip() for v in row]
        if len(vals) < len(header):
            vals += [""] * (len(header) - len(vals))
        out.append("| " + " | ".join(vals[: len(header)]) + " |")
    return "\n".join(out) + "\n"


def load_template(brain_dir: Path, name: str) -> str:
    path = brain_dir / "templates" / name
    if not path.exists():
        raise ValidationError(f"Missing template: {path}")
    return path.read_text(encoding="utf-8")


def requests_register_path(workspace: Path) -> Path:
    return workspace / ".aib_memory" / "requests_register.md"


def references_path(workspace: Path) -> Path:
    return workspace / ".aib_memory" / "references.md"


def requests_root(workspace: Path) -> Path:
    return workspace / ".aib_memory" / "requests"


def resolve_active_request_or_explicit(workspace: Path, request_id: str | None) -> List[str]:
    register = requests_register_path(workspace)
    if not register.exists():
        raise ValidationError("Missing .aib_memory/requests_register.md; run initialize first")

    header, rows = parse_markdown_table(read_text(register))
    if not header:
        raise ValidationError("requests_register.md has no valid table")

    col = {name: idx for idx, name in enumerate(header)}
    for required in ["request_id", "title", "folder", "state", "created_at", "closed_at"]:
        if required not in col:
            raise ValidationError(f"requests_register.md missing column: {required}")

    if request_id:
        matches = [r for r in rows if r[col["request_id"]] == request_id]
        if not matches:
            raise ValidationError(f"Request ID not found: {request_id}")
        return matches[0]

    active = [r for r in rows if r[col["state"]] == ACTIVE]
    if len(active) == 0:
        raise ValidationError("No active request found; provide --request-id explicitly")
    if len(active) > 1:
        raise ValidationError("Multiple active requests found; resolve register inconsistency")
    return active[0]


def update_requests_register(workspace: Path, rows: Sequence[Sequence[str]]) -> None:
    header = ["request_id", "title", "folder", "state", "created_at", "closed_at"]
    text = "# Requests Register\n\n" + format_markdown_table(header, rows)
    write_text(requests_register_path(workspace), text)


def sanitize_location_to_path(location: str) -> str:
    parts = [segment.strip() for segment in location.split("/")]
    parts = [p for p in parts if p]
    return "/".join(parts)


def parse_product_documentation_requirements(product_doc_path: Path) -> List[RequirementRef]:
    if not product_doc_path.exists():
        raise ValidationError(f"Missing Product_Documentation.md: {product_doc_path}")

    lines = product_doc_path.read_text(encoding="utf-8").splitlines()
    results: List[RequirementRef] = []
    seen_ids = set()
    last_location_by_prefix: dict[str, str] = {}

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        m = REQ_HEADING_PATTERN.match(line)
        if not m:
            i += 1
            continue

        req_id = m.group(1).strip()
        title = m.group(2).strip()
        req_prefix = req_id.split("-", 1)[0]
        if req_id in seen_ids:
            raise ValidationError(f"Duplicate requirement ID in Product_Documentation.md: {req_id}")
        seen_ids.add(req_id)

        location = None
        j = i + 1
        while j < len(lines):
            nxt = lines[j].rstrip()
            if REQ_HEADING_PATTERN.match(nxt):
                break
            loc_m = LOCATION_PATTERN.match(nxt)
            if loc_m:
                location = loc_m.group(1).strip()
                break
            j += 1

        if not location:
            location = last_location_by_prefix.get(req_prefix)
        if not location:
            raise ValidationError(f"Missing Location for requirement: {req_id}")

        last_location_by_prefix[req_prefix] = location

        results.append(RequirementRef(req_id=req_id, title=title, location=location))
        i = j

    if not results:
        raise ValidationError("No requirement headings found in Product_Documentation.md")

    return sorted(results, key=lambda x: x.req_id)


def resolve_product_documentation_path(workspace: Path) -> Path:
    canonical_path = workspace / ".aib_brain" / "Product_Documentation.md"
    if canonical_path.exists():
        return canonical_path

    raise ValidationError(
        f"Missing Product_Documentation.md: expected {canonical_path}"
    )


def seed_references_from_product_doc(workspace: Path) -> Tuple[str, List[RequirementRef]]:
    # Prefer a static references template bundled with the brain. This
    # removes a hard dependency on Product_Documentation.md during runtime.
    brain_dir = workspace / ".aib_brain"
    template_path = brain_dir / "templates" / "references-template.md"
    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        header, table_rows = parse_markdown_table(content)
        if header and table_rows:
            # Try to construct RequirementRef objects from the template rows.
            col = {name: idx for idx, name in enumerate(header)}
            requirements: List[RequirementRef] = []
            for row in table_rows:
                try:
                    title_cell = row[col["title"]]
                    path_cell = row[col["path"]]
                except KeyError:
                    raise ValidationError("references-template.md missing required columns")

                if " - " in title_cell:
                    req_id, req_title = [s.strip() for s in title_cell.split(" - ", 1)]
                else:
                    # Fallback req id generation when template doesn't include one
                    req_id = f"REQ-{len(requirements) + 1:04d}"
                    req_title = title_cell.strip()

                # Expect path like: .aib_memory/docs/<location>/<REQ_ID>.md
                prefix = ".aib_memory/docs/"
                location = ""
                if path_cell.startswith(prefix):
                    rel = path_cell[len(prefix) :]
                    parts = rel.split("/")
                    if len(parts) >= 2:
                        location = "/".join(parts[:-1])
                    else:
                        location = ""
                else:
                    p = Path(path_cell)
                    parts = list(p.parts)
                    if ".aib_memory" in parts and "docs" in parts:
                        try:
                            docs_idx = parts.index("docs")
                            location = "/".join(parts[docs_idx + 1 : -1])
                        except ValueError:
                            location = ""

                requirements.append(RequirementRef(req_id=req_id, title=req_title, location=location))

            # Return the template content unmodified and the parsed requirements
            return content, requirements

    # Fallback to legacy behavior: parse Product_Documentation.md
    requirements = parse_product_documentation_requirements(resolve_product_documentation_path(workspace))

    rows = []
    paths_seen = set()
    for idx, req in enumerate(requirements, start=1):
        location_path = sanitize_location_to_path(req.location)
        rel_path = f".aib_memory/docs/{location_path}/{req.req_id}.md"
        if rel_path in paths_seen:
            raise ValidationError(f"Duplicate seeded path resolved: {rel_path}")
        paths_seen.add(rel_path)

        rows.append(
            [
                f"REF-{idx:04d}",
                f"{req.req_id} - {req.title}",
                rel_path,
                "product-doc",
                "Y",
                "default",
                "Seeded from Product_Documentation.md",
            ]
        )

    text = "# References\n\n" + format_markdown_table(
        ["ref_id", "title", "path", "type", "edit_allowed", "source", "notes"], rows
    )
    return text, requirements


def ensure_doc_seed_files(workspace: Path, requirements: Sequence[RequirementRef]) -> None:
    for req in requirements:
        location_path = sanitize_location_to_path(req.location)
        path = workspace / ".aib_memory" / "docs" / Path(location_path) / f"{req.req_id}.md"
        if path.exists():
            continue
        content = (
            f"# {req.req_id} - {req.title}\n\n"
            f"Source location: `{req.location}`\n\n"
            "## Content\n\n"
            "_This file is seeded by AIB initialize. Fill with project-specific content._\n"
        )
        write_text(path, content)


REQUIRED_REQUEST_SECTIONS = [
    "## Goal",
    "## Background",
    "## Scope",
    "## Out of scope",
    "## Constraints",
    "## Success criteria",
]


def validate_request_md(path: Path) -> None:
    """Raise ValidationError if ``request.md`` is missing any required section."""
    content = read_text(path)
    if not content:
        raise ValidationError(f"request.md is empty or missing: {path}")
    for heading in REQUIRED_REQUEST_SECTIONS:
        # Match heading at the start of a line, case-insensitive
        if not re.search(r"^" + re.escape(heading), content, re.IGNORECASE | re.MULTILINE):
            raise ValidationError(
                f"request.md missing required section '{heading}': {path}"
            )


def print_error_and_exit(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

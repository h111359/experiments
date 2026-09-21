"""
verify-context-data-model.py: Validate a managed data-model context extension.
Part of the AIB context-extension tooling for request R-20260718-0809.
Responsibilities: enforce structure, empty-state, model identity, entity, relation,
object, and formatting rules without third-party dependencies.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DOCUMENT_TITLE = "# Context Data Model"
EMPTY_NOTICE = "No data models are currently documented."
REQUIRED_SECTIONS = ("Type", "Location", "Description", "Entities")
OPTIONAL_SECTIONS = ("Relations", "Other Objects")
VALID_SECTIONS = set(REQUIRED_SECTIONS + OPTIONAL_SECTIONS)
VALID_TYPES = {"logical", "physical", "analytical"}
VALID_CARDINALITIES = {"1:1", "M:1", "M:M"}
VALID_CONSTRAINTS = {
    "Key",
    "Not Null",
    "Unique",
    "Foreign Key",
    "Min Length",
    "Max Length",
    "Check",
}
HEADING_PATTERN = re.compile(r"^(#{1,})\s+(.+)$")
HTML_PATTERN = re.compile(r"<[a-zA-Z/][^>]*>")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def _parse_args() -> argparse.Namespace:
    """Parse workspace and target path arguments."""
    parser = argparse.ArgumentParser(
        description="Validate a managed context data-model Markdown extension."
    )
    parser.add_argument("--workspace", default=".", help="Workspace root path.")
    parser.add_argument(
        "--path",
        default=".aib_memory/context-data-model.md",
        help="Workspace-relative data-model extension path.",
    )
    return parser.parse_args()


def _resolve_target(workspace: Path, relative_path: str) -> tuple[Path | None, str]:
    """Resolve a target path while preventing workspace traversal."""
    root = workspace.resolve()
    target = (root / relative_path).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None, "Target path escapes the workspace root."
    return target, ""


def _heading(line: str) -> tuple[int, str] | None:
    """Return a Markdown heading level and text for a line, when present."""
    match = HEADING_PATTERN.match(line.strip())
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def _model_ranges(lines: list[str]) -> list[tuple[str, int, int]]:
    """Return model names and zero-based content ranges for all H2 headings."""
    positions = []
    for index, line in enumerate(lines):
        heading = _heading(line)
        if heading and heading[0] == 2:
            positions.append((heading[1], index))
    ranges = []
    for offset, (name, start) in enumerate(positions):
        end = positions[offset + 1][1] if offset + 1 < len(positions) else len(lines)
        ranges.append((name, start, end))
    return ranges


def _section_ranges(lines: list[str], start: int, end: int) -> dict[str, tuple[int, int]]:
    """Return H3 section content ranges inside one model range."""
    positions = []
    for index in range(start + 1, end):
        heading = _heading(lines[index])
        if heading and heading[0] == 3:
            positions.append((heading[1], index))
    ranges = {}
    for offset, (name, position) in enumerate(positions):
        section_end = positions[offset + 1][1] if offset + 1 < len(positions) else end
        ranges[name] = (position, section_end)
    return ranges


def _first_value(lines: list[str], start: int, end: int) -> str:
    """Return the first non-blank non-heading value in a range."""
    for line in lines[start + 1:end]:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped.removeprefix("- ").strip()
    return ""


def _h4_blocks(lines: list[str], start: int, end: int) -> list[tuple[str, int, int]]:
    """Return H4 names and content ranges in an H3 section."""
    positions = []
    for index in range(start + 1, end):
        heading = _heading(lines[index])
        if heading and heading[0] == 4:
            positions.append((heading[1], index))
    blocks = []
    for offset, (name, position) in enumerate(positions):
        block_end = positions[offset + 1][1] if offset + 1 < len(positions) else end
        blocks.append((name, position, block_end))
    return blocks


def _field_map(lines: list[str], start: int, end: int) -> dict[str, list[str]]:
    """Collect colon-delimited Markdown fields from a block."""
    fields: dict[str, list[str]] = {}
    for line in lines[start + 1:end]:
        stripped = line.strip().removeprefix("- ").strip()
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        fields.setdefault(key.strip(), []).append(value.strip())
    return fields


def check_file_readable_and_title(content: str | None, error: str) -> tuple[bool, str]:
    """Check file readability and the exact document title."""
    if error:
        return False, error
    lines = content.splitlines() if content is not None else []
    if not lines or lines[0] != DOCUMENT_TITLE:
        return False, f"Document must start with '{DOCUMENT_TITLE}'."
    return True, ""


def check_heading_hierarchy(content: str | None, _error: str) -> tuple[bool, str]:
    """Check model and section heading levels and permitted names."""
    if content is None:
        return False, "Content is unavailable."
    active_h3 = None
    for index, line in enumerate(content.splitlines(), start=1):
        heading = _heading(line)
        if not heading:
            continue
        level, text = heading
        if level > 4 or (level == 1 and (index != 1 or text != "Context Data Model")):
            return False, f"Invalid heading at line {index}: {line.strip()}"
        if level == 3:
            active_h3 = text
            if text not in VALID_SECTIONS:
                return False, f"Unsupported H3 section '{text}' at line {index}."
        if level == 4 and active_h3 not in {"Entities", "Relations", "Other Objects"}:
            return False, f"H4 heading at line {index} is outside a supported object section."
    return True, ""


def check_empty_state_exclusive(content: str | None, _error: str) -> tuple[bool, str]:
    """Check canonical empty state or mutually exclusive model state."""
    if content is None:
        return False, "Content is unavailable."
    normalized = content.rstrip("\r\n")
    canonical = f"{DOCUMENT_TITLE}\n\n{EMPTY_NOTICE}"
    models = _model_ranges(content.splitlines())
    if EMPTY_NOTICE in content:
        if normalized != canonical or models:
            return False, "No-model notice must use the exact canonical document and no H2 models."
        return True, ""
    if not models:
        return False, "Model state requires at least one H2 model."
    return True, ""


def check_required_model_sections(content: str | None, _error: str) -> tuple[bool, str]:
    """Check required model sections and scalar values."""
    if content is None or EMPTY_NOTICE in content:
        return (content is not None), "" if content is not None else "Content is unavailable."
    lines = content.splitlines()
    for model, start, end in _model_ranges(lines):
        sections = _section_ranges(lines, start, end)
        if set(sections) - VALID_SECTIONS:
            return False, f"Model '{model}' has unsupported or duplicate sections."
        if any(name not in sections for name in REQUIRED_SECTIONS):
            return False, f"Model '{model}' is missing a required section."
        model_type = _first_value(lines, *sections["Type"]).lower()
        if model_type not in VALID_TYPES:
            return False, f"Model '{model}' has invalid Type '{model_type}'."
        for name in ("Location", "Description"):
            if not _first_value(lines, *sections[name]):
                return False, f"Model '{model}' has an empty {name} section."
    return True, ""


def check_model_identity_and_order(content: str | None, _error: str) -> tuple[bool, str]:
    """Check composite identity uniqueness and deterministic ordering."""
    if content is None or EMPTY_NOTICE in content:
        return (content is not None), "" if content is not None else "Content is unavailable."
    lines = content.splitlines()
    identities = []
    for model, start, end in _model_ranges(lines):
        sections = _section_ranges(lines, start, end)
        location = _first_value(lines, *sections.get("Location", (start, start))).casefold()
        identities.append((model.casefold(), location))
    if len(identities) != len(set(identities)):
        return False, "Duplicate business-name-plus-Location model identity found."
    if identities != sorted(identities):
        return False, "Models must be ordered by business name and then Location."
    return True, ""


def _attributes_complete(lines: list[str], start: int, end: int) -> bool:
    """Return whether an entity block contains complete Name/Type attributes."""
    attributes = []
    current: dict[str, str] | None = None
    for line in lines[start + 1:end]:
        stripped = line.strip()
        if stripped.startswith("- Name:"):
            current = {"Name": stripped.split(":", 1)[1].strip()}
            attributes.append(current)
        elif current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.removeprefix("- ").strip()] = value.strip()
    return bool(attributes) and all(item.get("Name") and item.get("Type") for item in attributes)


def check_entities_and_attributes(content: str | None, _error: str) -> tuple[bool, str]:
    """Check unique entities and complete attribute definitions."""
    if content is None or EMPTY_NOTICE in content:
        return (content is not None), "" if content is not None else "Content is unavailable."
    lines = content.splitlines()
    for model, start, end in _model_ranges(lines):
        sections = _section_ranges(lines, start, end)
        blocks = _h4_blocks(lines, *sections["Entities"])
        names = [name.casefold() for name, _start, _end in blocks]
        if not blocks or len(names) != len(set(names)):
            return False, f"Model '{model}' needs one or more uniquely named entities."
        for entity, entity_start, entity_end in blocks:
            if not _attributes_complete(lines, entity_start, entity_end):
                return False, f"Entity '{entity}' requires at least one Name and Type attribute."
    return True, ""


def _constraints_valid(values: list[str]) -> bool:
    """Return whether comma-delimited constraint values use supported names."""
    for value in values:
        for token in (part.strip() for part in value.split(",")):
            base = token.split("(", 1)[0].strip()
            if base not in VALID_CONSTRAINTS:
                return False
            if base in {"Check", "Foreign Key"} and "(" not in token:
                return False
    return True


def check_relations_and_objects(content: str | None, _error: str) -> tuple[bool, str]:
    """Check optional relation, object, and constraint fields."""
    if content is None or EMPTY_NOTICE in content:
        return (content is not None), "" if content is not None else "Content is unavailable."
    lines = content.splitlines()
    for model, start, end in _model_ranges(lines):
        sections = _section_ranges(lines, start, end)
        for name, required in (
            ("Relations", {"Left Side Entity", "Right Side Entity", "Relationship Cardinality"}),
            ("Other Objects", {"Name", "Type", "Description"}),
        ):
            if name not in sections:
                continue
            for item, item_start, item_end in _h4_blocks(lines, *sections[name]):
                fields = _field_map(lines, item_start, item_end)
                if not required.issubset(fields) or any(not fields[key][0] for key in required):
                    return False, f"{name} item '{item}' is missing required fields."
                if name == "Relations" and fields["Relationship Cardinality"][0] not in VALID_CARDINALITIES:
                    return False, f"Relation '{item}' has invalid cardinality."
        for _entity, entity_start, entity_end in _h4_blocks(lines, *sections["Entities"]):
            constraints = _field_map(lines, entity_start, entity_end).get("Constraints", [])
            if not _constraints_valid(constraints):
                return False, f"Model '{model}' has an invalid attribute constraint."
    return True, ""


def check_formatting_and_duplicates(content: str | None, _error: str) -> tuple[bool, str]:
    """Check prohibited Markdown and duplicate object headings."""
    if content is None:
        return False, "Content is unavailable."
    if HTML_PATTERN.search(content) or IMAGE_PATTERN.search(content):
        return False, "HTML and Markdown images are prohibited."
    if any(line.lstrip().startswith("|") for line in content.splitlines()):
        return False, "Markdown tables are prohibited."
    lines = content.splitlines()
    for model, start, end in _model_ranges(lines):
        sections = _section_ranges(lines, start, end)
        for section_name in ("Entities", "Relations", "Other Objects"):
            if section_name not in sections:
                continue
            names = [name.casefold() for name, _start, _end in _h4_blocks(lines, *sections[section_name])]
            if len(names) != len(set(names)):
                return False, f"Model '{model}' has duplicate names in {section_name}."
    return True, ""


ALL_CHECKS = [
    ("check_file_readable_and_title", check_file_readable_and_title),
    ("check_heading_hierarchy", check_heading_hierarchy),
    ("check_empty_state_exclusive", check_empty_state_exclusive),
    ("check_required_model_sections", check_required_model_sections),
    ("check_model_identity_and_order", check_model_identity_and_order),
    ("check_entities_and_attributes", check_entities_and_attributes),
    ("check_relations_and_objects", check_relations_and_objects),
    ("check_formatting_and_duplicates", check_formatting_and_duplicates),
]


def main() -> int:
    """Run all eight data-model checks and return a process exit code."""
    args = _parse_args()
    target, error = _resolve_target(Path(args.workspace), args.path)
    content = None
    if target is not None:
        try:
            content = target.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError, UnicodeError) as exc:
            error = f"Cannot read data-model extension: {exc}"

    passed = 0
    for name, check in ALL_CHECKS:
        ok, message = check(content, error)
        if ok:
            print(f"[OK] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name}: {message}")

    print(f"Results: {passed}/{len(ALL_CHECKS)} checks passed.")
    return 0 if passed == len(ALL_CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())

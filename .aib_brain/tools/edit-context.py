"""
edit-context.py: CRUD operations for atomic statements in .aib_memory/context.md.
Part of the AIB tools suite.
Responsibilities: Select, insert, and delete atomic statements by area section using
text-based line matching. Statement format: - TYPE: text (no hash, no area prefix).
"""

import argparse
import re
import sys
from pathlib import Path

# Valid two-letter area codes
VALID_AREAS = {
    "PO", "CM", "DO", "CO", "BP", "FN", "TD", "TS", "NW",
    "DS", "DF", "PR", "AN", "UI", "SC", "PF", "OP", "DV",
    "DP", "DR", "OB", "DM",
}

# Ordered area list for consistent section insertion order
AREA_ORDER = [
    "PO", "CM", "DO", "CO", "BP", "FN", "TD", "TS", "NW",
    "DS", "DF", "PR", "AN", "UI", "SC", "PF", "OP", "DV",
    "DP", "DR", "OB", "DM",
]

# Valid statement type letters
VALID_TYPES = {"N", "R", "C", "E", "L", "U", "A", "D", "I"}

# Pattern matching an atomic statement line: "- TYPE: text" or "- TYPE-N: text"
STATEMENT_PATTERN = re.compile(r"^- ([A-Z])(?:-\d+)?: (.+)$")

# Pattern matching H2 headings
H2_PATTERN = re.compile(r"^## .+$")


def _build_area_heading(area: str) -> str:
    """
    Return the H2 heading string for the given area code.

    Args:
        area: Two-letter area code (e.g. 'FN').

    Returns:
        The heading string (e.g. '## FN').
    """
    return f"## {area}"


def _find_area_range(lines: list[str], area: str) -> tuple[int, int]:
    """
    Find the start and end line indices for a given area section.

    Args:
        lines: All lines of context.md.
        area: The two-letter area code (e.g. 'FN').

    Returns:
        Tuple (start, end) where start is the heading line index and end is the
        line index of the next H2 or end of file. Returns (-1, -1) if not found.
    """
    target_heading = _build_area_heading(area)
    start = -1
    for i, line in enumerate(lines):
        if line.rstrip() == target_heading:
            start = i
            break

    if start == -1:
        return (-1, -1)

    # Find end: next H2 heading or end of file
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if H2_PATTERN.match(lines[i].rstrip()):
            end = i
            break

    return (start, end)


def _find_statement_by_text(lines: list[str], area: str, text_substring: str) -> int:
    """
    Find the line index of the first statement in the area section that contains
    the given text substring (case-insensitive).

    Args:
        lines: All lines of context.md.
        area: Two-letter area code.
        text_substring: Substring to search for in statement text.

    Returns:
        Line index of the matching statement, or -1 if not found.
    """
    start, end = _find_area_range(lines, area)
    if start == -1:
        return -1

    needle = text_substring.lower()
    matches = []
    for i in range(start + 1, end):
        match = STATEMENT_PATTERN.match(lines[i].rstrip())
        if match and needle in match.group(2).lower():
            matches.append(i)

    if len(matches) > 1:
        sys.stderr.write(
            f"Warning: Ambiguous match — {len(matches)} statements in '{area}' "
            f"contain '{text_substring}'. Using first match at line {matches[0] + 1}.\n"
        )

    return matches[0] if matches else -1


def _insert_area_section(lines: list[str], area: str) -> list[str]:
    """
    Insert a new area section heading in the correct order within the document.

    Area sections are ordered according to AREA_ORDER. The new section is inserted
    after the last existing area section that precedes it in the order, or before
    the ## Files section if no preceding area section exists.

    Args:
        lines: All lines of context.md.
        area: The two-letter area code to insert.

    Returns:
        Modified lines with the new area heading inserted.
    """
    target_order = AREA_ORDER.index(area) if area in AREA_ORDER else len(AREA_ORDER)

    # Find the insertion point: after the last preceding area section's content
    insert_at = len(lines)  # default: end of file

    # Look for ## Files or end of file as the upper bound
    files_line = -1
    for i, line in enumerate(lines):
        if line.rstrip() == "## Files":
            files_line = i
            break

    if files_line != -1:
        insert_at = files_line

    # Walk backwards from insert_at to find the last area section that should precede this one
    last_preceding_end = -1
    for idx, other_area in enumerate(AREA_ORDER):
        if idx >= target_order:
            break
        start, end = _find_area_range(lines, other_area)
        if start != -1:
            last_preceding_end = end

    if last_preceding_end != -1:
        insert_at = last_preceding_end

    # Build insertion: ensure blank line separation
    new_section_lines = []
    if insert_at > 0 and lines[insert_at - 1].strip() != "":
        new_section_lines.append("\n")
    new_section_lines.append(f"{_build_area_heading(area)}\n")
    new_section_lines.append("\n")

    return lines[:insert_at] + new_section_lines + lines[insert_at:]


def _validate_uniqueness_in_area(lines: list[str], area: str, new_text: str) -> bool:
    """
    Check that no existing statement in the area section has identical text (case-insensitive).

    Args:
        lines: All lines of context.md.
        area: Two-letter area code.
        new_text: The text of the statement being inserted.

    Returns:
        True if the text is unique, False if a duplicate exists.
    """
    start, end = _find_area_range(lines, area)
    if start == -1:
        return True  # Section doesn't exist yet, no duplicates possible

    needle = new_text.strip().lower()
    for i in range(start + 1, end):
        match = STATEMENT_PATTERN.match(lines[i].rstrip())
        if match and match.group(2).strip().lower() == needle:
            sys.stderr.write(
                f"Error: Duplicate statement text in '{area}': '{new_text}'\n"
            )
            return False

    return True


def operation_select(lines: list[str], area: str, text_substring: str) -> int:
    """
    Find and print the statement matching the given text substring in the area section.

    Args:
        lines: All lines of context.md.
        area: Two-letter area code.
        text_substring: Substring to search for in statement text.

    Returns:
        0 if found, 1 if not found.
    """
    line_idx = _find_statement_by_text(lines, area, text_substring)
    if line_idx == -1:
        sys.stderr.write(
            f"Error: No statement in '{area}' containing '{text_substring}'.\n"
        )
        return 1

    match = STATEMENT_PATTERN.match(lines[line_idx].rstrip())
    if match:
        print(f"- {match.group(1)}: {match.group(2)}")
    return 0


def operation_insert(
    lines: list[str],
    area: str,
    type_letter: str,
    text: str,
) -> tuple[list[str], int]:
    """
    Insert a new atomic statement in the appropriate area section.

    Args:
        lines: All lines of context.md.
        area: Two-letter area code.
        type_letter: Single-letter statement type.
        text: Statement text content.

    Returns:
        Tuple of (modified lines, exit code). Exit code 0 on success, 1 on failure.
    """
    # Validate uniqueness before inserting
    if not _validate_uniqueness_in_area(lines, area, text):
        return (lines, 1)

    # Find or create the area section
    start, end = _find_area_range(lines, area)
    if start == -1:
        lines = _insert_area_section(lines, area)
        start, end = _find_area_range(lines, area)
        if start == -1:
            sys.stderr.write(f"Error: Failed to create section for area '{area}'.\n")
            return (lines, 1)

    # Build the statement line
    statement = f"- {type_letter}: {text}\n"

    # Insert at the end of the section (before the next heading)
    insert_at = end
    # Skip backwards over trailing blank lines to insert right before them
    while insert_at > start + 1 and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    new_lines = lines[:insert_at]
    new_lines.append(statement)
    new_lines.extend(lines[insert_at:])

    return (new_lines, 0)


def operation_delete(lines: list[str], area: str, text_substring: str) -> tuple[list[str], int]:
    """
    Remove the atomic statement matching the text substring in the area section.

    Args:
        lines: All lines of context.md.
        area: Two-letter area code.
        text_substring: Substring to search for in statement text.

    Returns:
        Tuple of (modified lines, exit code). Exit code 0 on success, 1 if not found.
    """
    line_idx = _find_statement_by_text(lines, area, text_substring)
    if line_idx == -1:
        sys.stderr.write(
            f"Error: No statement in '{area}' containing '{text_substring}'. Nothing deleted.\n"
        )
        return (lines, 1)

    new_lines = [line for i, line in enumerate(lines) if i != line_idx]
    return (new_lines, 0)


def main() -> int:
    """
    Entry point for the edit-context tool.

    Parses arguments and dispatches to the appropriate CRUD operation on
    atomic statements in .aib_memory/context.md.

    Returns:
        0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="CRUD operations for atomic statements in .aib_memory/context.md."
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=["select", "insert", "delete"],
        help="Operation to perform: select, insert, or delete.",
    )
    parser.add_argument(
        "--area",
        required=True,
        help="Two-letter area code (e.g. PO, CM, FN).",
    )
    parser.add_argument(
        "--type",
        default=None,
        dest="type_letter",
        help="Single-letter statement type (N, R, C, E, L, U, A, D, I). Required for insert.",
    )
    parser.add_argument(
        "--text",
        default=None,
        help="Statement text (required for insert and as search substring for select/delete).",
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root path (default: current directory).",
    )

    args = parser.parse_args()

    # Validate area code
    if args.area not in VALID_AREAS:
        sys.stderr.write(
            f"Error: Invalid area code '{args.area}'. "
            f"Valid codes: {', '.join(sorted(VALID_AREAS))}.\n"
        )
        return 1

    # Validate text is provided (required for all operations)
    if not args.text:
        sys.stderr.write("Error: --text is required for all operations.\n")
        return 1

    # Validate type letter for insert
    if args.operation == "insert":
        if not args.type_letter:
            sys.stderr.write("Error: --type is required for insert operation.\n")
            return 1
        if args.type_letter not in VALID_TYPES:
            sys.stderr.write(
                f"Error: Invalid type letter '{args.type_letter}'. "
                f"Valid types: {', '.join(sorted(VALID_TYPES))}.\n"
            )
            return 1

    # Locate context.md
    context_path = Path(args.workspace) / ".aib_memory" / "context.md"
    if not context_path.exists():
        sys.stderr.write(f"Error: context.md not found at '{context_path}'.\n")
        return 1

    # Read context.md
    lines = context_path.read_text(encoding="utf-8").splitlines(keepends=True)

    if args.operation == "select":
        return operation_select(lines, args.area, args.text)

    elif args.operation == "insert":
        new_lines, exit_code = operation_insert(
            lines, args.area, args.type_letter, args.text
        )
        if exit_code == 0:
            context_path.write_text("".join(new_lines), encoding="utf-8")
        return exit_code

    elif args.operation == "delete":
        new_lines, exit_code = operation_delete(lines, args.area, args.text)
        if exit_code == 0:
            context_path.write_text("".join(new_lines), encoding="utf-8")
        return exit_code

    return 1


if __name__ == "__main__":
    sys.exit(main())

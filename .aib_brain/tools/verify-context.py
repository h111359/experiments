"""
verify-context.py: Validate .aib_memory/context.md against context-convention.md rules.
Part of the AIB tools suite.
Responsibilities: Run structural and format checks on context.md, report pass/fail per check,
exit with code 0 if all pass or 1 if any fail.
"""

import argparse
import re
import sys
from pathlib import Path

# Valid two-letter area codes (must match context-convention.md)
VALID_AREAS = {
    "PO", "CM", "DO", "CO", "BP", "FN", "TD", "TS", "NW",
    "DS", "DF", "PR", "AN", "UI", "SC", "PF", "OP", "DV",
    "DP", "DR", "OB", "DM",
}

# Valid single-letter statement type identifiers
VALID_TYPES = {"N", "R", "C", "E", "L", "U", "A", "D", "I"}

# Pattern matching an atomic statement line: "- TYPE: text" or "- TYPE-N: text"
STATEMENT_PATTERN = re.compile(r"^- ([A-Z])(?:-\d+)?: (.+)$")

# Pattern matching H2 headings
H2_PATTERN = re.compile(r"^## .+$")

# Pattern matching H3 headings
H3_PATTERN = re.compile(r"^### .+$")

# Pattern detecting HTML tags
HTML_TAG_PATTERN = re.compile(r"<[a-zA-Z/][^>]*>")

# Pattern detecting URLs
URL_PATTERN = re.compile(r"https?://")

# Pattern detecting Markdown table rows (lines starting with |)
TABLE_PATTERN = re.compile(r"^\|")


def _parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the verification script.

    Returns:
        Parsed namespace with workspace path.
    """
    parser = argparse.ArgumentParser(
        description="Validate .aib_memory/context.md against context-convention.md rules."
    )
    parser.add_argument(
        "--workspace", default=".", help="Workspace root path (default: current directory)"
    )
    return parser.parse_args()


def _read_context(workspace: Path) -> str:
    """
    Read the context.md file from the workspace.

    Args:
        workspace: Path to workspace root.

    Returns:
        Full text content of context.md.

    Raises:
        FileNotFoundError: If context.md does not exist.
    """
    context_path = workspace / ".aib_memory" / "context.md"
    return context_path.read_text(encoding="utf-8")


def _get_area_sections(lines: list[str]) -> list[tuple[str, int, int]]:
    """
    Extract all valid area sections from the document.

    Args:
        lines: All lines of context.md.

    Returns:
        List of (area_code, heading_line_index, end_line_index) tuples.
        end_line_index is the index of the next H2 or end of file.
    """
    sections: list[tuple[str, int, int]] = []

    # Collect all H2 heading positions
    h2_positions: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if H2_PATTERN.match(stripped) and not stripped.startswith("### "):
            heading_text = stripped[3:].strip()  # Remove "## "
            h2_positions.append((heading_text, i))

    for idx, (heading_text, pos) in enumerate(h2_positions):
        # Determine end: next H2 or end of file
        end = h2_positions[idx + 1][1] if idx + 1 < len(h2_positions) else len(lines)

        # Skip reserved headings
        if heading_text in ("1. Product Identity", "Files"):
            continue
        # Check if it's a valid two-letter area code
        if heading_text in VALID_AREAS:
            sections.append((heading_text, pos, end))

    return sections


def check_title_and_product_identity(content: str) -> tuple[bool, str]:
    """
    Verify document starts with # Product Context and ## 1. Product Identity is present.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "# Product Context":
        return False, "Document does not start with '# Product Context'."

    if not any(line.strip() == "## 1. Product Identity" for line in lines):
        return False, "Section '## 1. Product Identity' not found."

    return True, ""


def check_area_headings_valid(content: str) -> tuple[bool, str]:
    """
    Verify every H2 heading is ## 1. Product Identity, ## Files, or ## VALID_AREA.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    invalid_headings = []

    for line in lines:
        stripped = line.strip()
        if H2_PATTERN.match(stripped):
            heading_text = stripped[3:].strip()
            if heading_text not in ("1. Product Identity", "Files") and heading_text not in VALID_AREAS:
                invalid_headings.append(stripped)

    if invalid_headings:
        return False, f"Invalid H2 headings found: {invalid_headings[:5]}."

    return True, ""


def check_at_least_one_area_section(content: str) -> tuple[bool, str]:
    """
    Verify at least one valid area section (## VALID_AREA) is present.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        if H2_PATTERN.match(stripped):
            heading_text = stripped[3:].strip()
            if heading_text in VALID_AREAS:
                return True, ""

    return False, "No valid area section (e.g., ## FN, ## PO) found in the document."


def check_area_sections_non_empty(content: str) -> tuple[bool, str]:
    """
    Verify every area section heading has at least one atomic statement line.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    area_sections = _get_area_sections(lines)

    empty_areas = []
    for area_code, start, end in area_sections:
        has_statement = False
        for i in range(start + 1, end):
            stripped = lines[i].strip()
            if stripped.startswith("- ") and STATEMENT_PATTERN.match(stripped):
                has_statement = True
                break
        if not has_statement:
            empty_areas.append(area_code)

    if empty_areas:
        return False, f"Area sections with no atomic statements: {empty_areas}."

    return True, ""


def check_statement_format(content: str) -> tuple[bool, str]:
    """
    Verify every bullet line in area sections matches the atomic statement pattern.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    area_sections = _get_area_sections(lines)

    invalid_lines = []
    for _area_code, start, end in area_sections:
        for i in range(start + 1, end):
            stripped = lines[i].strip()
            # Skip empty lines and headings
            if not stripped or H3_PATTERN.match(stripped):
                continue
            # Lines starting with '- ' are statement candidates
            if stripped.startswith("- "):
                match = STATEMENT_PATTERN.match(stripped)
                if not match:
                    invalid_lines.append(f"Line {i + 1}: {stripped[:80]}")
                else:
                    stype = match.group(1)
                    if stype not in VALID_TYPES:
                        invalid_lines.append(
                            f"Line {i + 1}: invalid type letter '{stype}'."
                        )

    if invalid_lines:
        report = invalid_lines[:5]
        suffix = f" (and {len(invalid_lines) - 5} more)" if len(invalid_lines) > 5 else ""
        return False, f"Invalid statement lines: {report}{suffix}."

    return True, ""


def check_statement_uniqueness(content: str) -> tuple[bool, str]:
    """
    Verify no duplicate statement text within each area section (case-insensitive).

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    area_sections = _get_area_sections(lines)

    duplicates = []
    for area_code, start, end in area_sections:
        seen_texts: dict[str, int] = {}
        for i in range(start + 1, end):
            match = STATEMENT_PATTERN.match(lines[i].strip())
            if match:
                text = match.group(2).strip().lower()
                if text in seen_texts:
                    duplicates.append(
                        f"'{area_code}' area: duplicate text on lines {seen_texts[text]} and {i + 1}"
                    )
                else:
                    seen_texts[text] = i + 1

    if duplicates:
        return False, f"Duplicate statement texts: {duplicates[:5]}."

    return True, ""


def check_no_external_hyperlinks(content: str) -> tuple[bool, str]:
    """
    Verify no http:// or https:// strings appear in the file.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    offending = []
    for i, line in enumerate(lines):
        if URL_PATTERN.search(line):
            offending.append(i + 1)

    if offending:
        return False, f"External URLs found on lines: {offending[:5]}."

    return True, ""


def check_no_html_tags(content: str) -> tuple[bool, str]:
    """
    Verify no HTML tags appear in the file, excluding template placeholders in backticks.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    # Pattern to strip inline code spans before checking for HTML
    inline_code_pattern = re.compile(r"`[^`]+`")
    offending = []
    for i, line in enumerate(lines):
        cleaned = inline_code_pattern.sub("", line)
        if HTML_TAG_PATTERN.search(cleaned):
            offending.append(i + 1)

    if offending:
        return False, f"HTML tags found on lines: {offending[:5]}."

    return True, ""


def check_no_tables(content: str) -> tuple[bool, str]:
    """
    Verify no Markdown table syntax appears in the file.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()
    offending = []
    for i, line in enumerate(lines):
        if TABLE_PATTERN.match(line.strip()):
            offending.append(i + 1)

    if offending:
        return False, f"Table syntax (|) found on lines: {offending[:5]}."

    return True, ""


def check_product_identity_non_empty(content: str) -> tuple[bool, str]:
    """
    Verify Section 1 (Product Identity) has substantive prose content.

    Args:
        content: Full text of context.md.

    Returns:
        Tuple of (passed, message).
    """
    lines = content.splitlines()

    section1_start = None
    section1_end = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## 1. Product Identity":
            section1_start = i
        elif section1_start is not None and H2_PATTERN.match(stripped):
            section1_end = i
            break

    if section1_start is None:
        return False, "Section '## 1. Product Identity' not found."

    if section1_end is None:
        section1_end = len(lines)

    # Count non-empty, non-heading lines in Product Identity
    content_lines = 0
    for i in range(section1_start + 1, section1_end):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#"):
            content_lines += 1

    MIN_CONTENT_LINES = 3
    if content_lines < MIN_CONTENT_LINES:
        return False, (
            f"Product Identity has only {content_lines} content lines "
            f"(minimum {MIN_CONTENT_LINES} required)."
        )

    return True, ""


# All checks in execution order (10 checks total)
ALL_CHECKS = [
    ("check_title_and_product_identity", check_title_and_product_identity),
    ("check_area_headings_valid", check_area_headings_valid),
    ("check_at_least_one_area_section", check_at_least_one_area_section),
    ("check_area_sections_non_empty", check_area_sections_non_empty),
    ("check_statement_format", check_statement_format),
    ("check_statement_uniqueness", check_statement_uniqueness),
    ("check_no_external_hyperlinks", check_no_external_hyperlinks),
    ("check_no_html_tags", check_no_html_tags),
    ("check_no_tables", check_no_tables),
    ("check_product_identity_non_empty", check_product_identity_non_empty),
]


def main() -> int:
    """
    Entry point for the context.md verification tool.

    Runs all checks sequentially, prints structured results, and returns
    exit code 0 if all pass or 1 if any fail.

    Returns:
        0 on all checks passing, 1 on any failure.
    """
    args = _parse_args()
    workspace = Path(args.workspace)

    try:
        content = _read_context(workspace)
    except FileNotFoundError:
        print("[FAIL] file_exists: .aib_memory/context.md not found.")
        print("Results: 0/1 checks passed.")
        return 1

    passed = 0
    failed = 0

    for name, check_fn in ALL_CHECKS:
        ok, message = check_fn(content)
        if ok:
            print(f"[OK] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name}: {message}")
            failed += 1

    total = passed + failed
    print(f"Results: {passed}/{total} checks passed.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

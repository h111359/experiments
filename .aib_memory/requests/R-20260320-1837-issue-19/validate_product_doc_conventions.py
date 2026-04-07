"""Validate deterministic product-doc -> convention mapping.

Checks:
- Every `product-doc` row in `.aib_memory/references.md` has a resolvable convention path
  `.aib_brain/conventions/<requirement-id-lower>-convention.md`.
- The convention file exists.
- `.aib_brain/conventions/product-documentation-convention.md` contains a mapping row
  for the doc title and the resolved convention path.

Stdlib-only; intended to be run from the repository root.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
REFERENCES_PATH = REPO_ROOT / ".aib_memory" / "references.md"
MAPPING_PATH = REPO_ROOT / ".aib_brain" / "conventions" / "product-documentation-convention.md"
CONVENTIONS_DIR = REPO_ROOT / ".aib_brain" / "conventions"


@dataclass(frozen=True)
class ProductDocRef:
    ref_id: str
    title: str
    path: str

    @property
    def requirement_id(self) -> str:
        return Path(self.path).stem

    @property
    def convention_relpath(self) -> str:
        return f".aib_brain/conventions/{self.requirement_id.lower()}-convention.md"


def _normalize_slashes(text: str) -> str:
    return text.replace("\\", "/")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_product_docs_from_references(md_text: str) -> list[ProductDocRef]:
    lines = [line.rstrip("\n") for line in md_text.splitlines()]

    # Find the markdown table header delimiter line (---) and parse subsequent rows.
    # Table columns: ref_id | title | path | type | edit_allowed | source | notes
    product_docs: list[ProductDocRef] = []

    in_table = False
    for line in lines:
        if not in_table:
            if re.match(r"^\|\s*ref_id\s*\|", line, flags=re.IGNORECASE):
                in_table = True
            continue

        # Skip separator row
        if re.match(r"^\|\s*-+\s*\|", line):
            continue

        if not line.startswith("|"):
            break

        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 7:
            continue

        ref_id, title, path, ref_type, *_rest = cells
        if ref_type != "product-doc":
            continue

        product_docs.append(ProductDocRef(ref_id=ref_id, title=title, path=path))

    return product_docs


def parse_mapping_pairs(md_text: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    # Expected list line format:
    #   - `TITLE` with defining convention file `.aib_brain/conventions/<file>.md`
    pattern = re.compile(
        r"^\s*-\s*`(?P<title>[^`]+)`\s+with\s+defining\s+convention\s+file\s+`(?P<path>[^`]+)`\s*$"
    )

    for raw_line in md_text.splitlines():
        line = _normalize_slashes(raw_line.strip())
        match = pattern.match(line)
        if not match:
            continue

        title = match.group("title").strip()
        path = match.group("path").strip()
        pairs.add((title, path))

    return pairs


def main() -> int:
    if not REFERENCES_PATH.exists():
        print(f"ERROR: Missing {REFERENCES_PATH}")
        return 2
    if not MAPPING_PATH.exists():
        print(f"ERROR: Missing {MAPPING_PATH}")
        return 2

    refs_text = _read_text(REFERENCES_PATH)
    mapping_text = _read_text(MAPPING_PATH)

    product_docs = parse_product_docs_from_references(refs_text)
    mapping_pairs = parse_mapping_pairs(mapping_text)

    errors: list[str] = []

    for ref in product_docs:
        # Validate requirement id shape (best-effort, deterministic extraction)
        if not re.match(r"^[A-Z]{3,4}-\d{2}$", ref.requirement_id):
            errors.append(
                f"{ref.ref_id}: requirement_id '{ref.requirement_id}' is unexpected (from path '{ref.path}')"
            )

        convention_file = CONVENTIONS_DIR / f"{ref.requirement_id.lower()}-convention.md"
        if not convention_file.exists():
            errors.append(
                f"{ref.ref_id}: missing convention file '{ref.convention_relpath}' (expected at '{convention_file.as_posix()}')"
            )

        expected_pair = (ref.title, ref.convention_relpath)
        if expected_pair not in mapping_pairs:
            errors.append(
                f"{ref.ref_id}: mapping missing for title '{ref.title}' -> '{ref.convention_relpath}'"
            )

    if errors:
        print("FAIL: product-doc convention mapping validation failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: validated {len(product_docs)} product-doc entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Product Documentation

This convention defines the files (if enabled) which define the product.
The exact location of the files is in `.aib_memory/references.md`.

## Authoritative Mapping and Deterministic Resolution

- This file is the authoritative, reviewable mapping between each `product-doc` title and its per-document convention file.
- Canonical path separator for paths in this repository documentation is `/`.
- Deterministic convention resolution rule (used by prompts):
  - Requirement ID is derived from the product-doc filename (e.g., `.../ARCH-01.md` -> `ARCH-01`).
  - Convention path MUST be `.aib_brain/conventions/<requirement-id-lower>-convention.md`.
  - Example: `ARCH-01` -> `.aib_brain/conventions/arch-01-convention.md`.
- If the deterministic convention path does not exist OR the mapping row is missing from this file, editing that product-doc MUST fail-closed.

## Documents Lists Format

Format of list row: " - `<title>`  with defining convention file `<convention-path>`"
<title> = same attribute in `.aib_memory\references.md`
<convention-path> = path to the file with definition of the convention of the <title>

## Business & Functional Documents

  - `KNW-01 - Domain glossary` with defining convention file `.aib_brain/conventions/knw-01-convention.md`
  - `KNW-02 - Business process catalog` with defining convention file `.aib_brain/conventions/knw-02-convention.md`
  - `KNW-03 - Use cases & personas` with defining convention file `.aib_brain/conventions/knw-03-convention.md`
  - `RQT-01 - Product charter` with defining convention file `.aib_brain/conventions/rqt-01-convention.md`
  - `RQT-02 - Requirements document` with defining convention file `.aib_brain/conventions/rqt-02-convention.md`

## Architecture & Technical Documents

  - `ARCH-01 - High-level architecture` with defining convention file `.aib_brain/conventions/arch-01-convention.md`
  - `ARCH-02 - Topology/network description` with defining convention file `.aib_brain/conventions/arch-02-convention.md`
  - `ARCH-03 - Capacity model` with defining convention file `.aib_brain/conventions/arch-03-convention.md`
  - `ARCH-04 - ADRs repository` with defining convention file `.aib_brain/conventions/arch-04-convention.md`
  - `ARCH-06 - Runtime interaction sequences` with defining convention file `.aib_brain/conventions/arch-06-convention.md`
  - `ARCH-07 - Resource catalog` with defining convention file `.aib_brain/conventions/arch-07-convention.md`
  - `CMP-01 - Notebook/script catalog` with defining convention file `.aib_brain/conventions/cmp-01-convention.md`
  - `CMP-02 - Algorithm specification register` with defining convention file `.aib_brain/conventions/cmp-02-convention.md`
  - `DATA-01 - Source data catalog and data ingestion strategy` with defining convention file `.aib_brain/conventions/data-01-convention.md`
  - `DATA-02 - Data models (logical & physical)` with defining convention file `.aib_brain/conventions/data-02-convention.md`
  - `DATA-03 - Data lineage` with defining convention file `.aib_brain/conventions/data-03-convention.md`
  - `DATA-04 - Data storage strategy & patterns` with defining convention file `.aib_brain/conventions/data-04-convention.md`
  - `DATA-05 - Data consumption & access patterns` with defining convention file `.aib_brain/conventions/data-05-convention.md`
  - `DATA-06 - Metrics catalog` with defining convention file `.aib_brain/conventions/data-06-convention.md`
  - `DATA-07 - Data quality rules, monitoring & reporting` with defining convention file `.aib_brain/conventions/data-07-convention.md`
  - `DATA-08 - Data archiving & deletion policy` with defining convention file `.aib_brain/conventions/data-08-convention.md`
  - `DATA-09 - Dashboard inventory` with defining convention file `.aib_brain/conventions/data-09-convention.md`
  - `OBS-01 - Logging` with defining convention file `.aib_brain/conventions/obs-01-convention.md`
  - `SEC-01 - Access management` with defining convention file `.aib_brain/conventions/sec-01-convention.md`
  - `SEC-02 - Infrastructure data protection` with defining convention file `.aib_brain/conventions/sec-02-convention.md`
  - `SEC-03 - Secrets management & rotation policy` with defining convention file `.aib_brain/conventions/sec-03-convention.md`
  - `SEC-04 - Infrastructure network security` with defining convention file `.aib_brain/conventions/sec-04-convention.md`
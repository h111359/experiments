# Summary

AI Builder (AIB) provides deterministic, model-agnostic workflows for managing requests/iterations and generating convention-governed documentation in a repository workspace.

# Functional Requirements

FR-001: The system manages exactly one Active request in the workspace.
FR-002: The system creates a request folder with request.md, iterations.md, and implementation.md.
FR-003: The system manages exactly one Active iteration per request.
FR-004: The system generates iteration artifacts in the request folder.
FR-005: The system executes an implement workflow that appends an implementation log entry.
FR-006: The system reads references.md to determine which files may be edited.
FR-007: The system reads per-document conventions and fails closed if mapping is missing.
FR-008: The system supports launching tool scripts via an interactive menu with real-time output streaming to terminal and per-action execution log files at `logs/aib-action-<timestamp>-<action-id>.log`.
FR-009: The system supports a PR bookkeeping workflow that bumps patch version and writes a new version log.

# Non-Functional Requirements

NFR-001: The workflow must be model-agnostic and vendor-agnostic.
NFR-002: Deterministic rules must be used for resolving active request and iteration.
NFR-003: The system must fail closed when a required convention mapping is missing.
NFR-004: Tool scripts must be runnable with Python 3.10+.
NFR-005: The release bookkeeping workflow must be idempotent on reruns.

# Acceptance Criteria

1. Initialization creates `.aib_memory` registers and product-doc stubs.
2. Creating a request registers one Active request and creates iteration 01 as Active.
3. Implementing a request appends an entry to the request implementation log.
4. Product-doc edits follow their conventions and respect edit permissions.
5. Release bookkeeping increments patch version and creates a new per-version log without modifying existing logs.

# Assumptions

- Workspace root is the repository root.
- Python is available to run tool scripts.

# Constraints

- Only one request may be Active at a time.
- Only one iteration may be Active per request.
- Automation must not modify disallowed files.

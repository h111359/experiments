| alg_id | title | purpose | owner_role | inputs | outputs | code_ref | status | perf_target | accuracy_metric | constraints | last_review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALG-0001 | SemVer Patch Bump | Bump patch marker and write per-version log for PR bookkeeping | AIB Maintainers | base_ref, brain_dir, log_dir, commit_subjects | marker rotation, version log | scripts/release_bookkeeping.py | active | p95 <= 2m for typical PR | N/A | requires git; CI context | 2026-03-22 |
| ALG-0002 | Request Iteration Resolution | Resolve active request and iteration deterministically | Product Team | requests_register, iterations register | resolved request_id, iteration_id | .aib_brain/tools/common.py | active | p95 <= 1s for typical workspace | N/A | filesystem-only; fail on invalid state | 2026-03-22 |

<a id="ALG-0001"></a>
## ALG-0001 — SemVer Patch Bump

### Business Purpose
Automate repository bookkeeping by computing the next patch version and producing a per-version change log.

### Inputs
- base branch marker file name
- worktree marker file name
- optional commit subjects

### Parameters

| name | type | default | allowed | description |
| --- | --- | --- | --- | --- |
| base_ref | string | (required) | git ref | Base ref used for deterministic version computation. |
| brain_dir | string | .aib_brain | path | Folder containing marker file. |
| log_dir | string | logs | path | Folder for per-version logs. |
| dry_run | bool | false | true/false | Compute without writing files. |

### Business Rules
1. Exactly one marker file must exist and match vMAJOR.MINOR.PATCH.
2. Patch is computed from base marker by incrementing PATCH by 1.
3. Existing logs are never modified.
4. If log exists and marker already bumped, exit with no changes.

### Computational Steps
1. Locate base marker from git tree.
2. Locate worktree marker from filesystem.
3. Compute target marker with patch+1.
4. Validate marker state.
5. Rotate marker if needed.
6. Write new per-version log.

### Formulas

Base $v=(X,Y,Z)$, target $v'=(X,Y,Z+1)$.

### Outputs
- New empty marker file `.aib_brain/vX.Y.(Z+1)`
- New log file `logs/version_vX.Y.(Z+1)_log.md`

### Performance Benchmarks
- Typical runtime under 2 minutes in CI.

### Accuracy Metrics
N/A.

### Operational Constraints
- Requires `git` available.

### Reference to Executable Code
- scripts/release_bookkeeping.py

### Test Cases (Minimum)
- Positive: single marker -> creates new marker + log.
- Edge: rerun with already bumped marker and log -> no changes.
- Failure: multiple markers -> fail with explicit error.

### Change History (Append-Only)
- 2026-03-22: Documented algorithm as active.

<a id="ALG-0002"></a>
## ALG-0002 — Request Iteration Resolution

### Business Purpose
Deterministically resolve the active request and active iteration so tools and prompts operate without ambiguity.

### Inputs
- `.aib_memory/requests_register.md`
- request folder `iterations.md`

### Parameters

| name | type | default | allowed | description |
| --- | --- | --- | --- | --- |
| request_id | string | (none) | R-YYYYMMDD-HHmi | If absent, resolve the single Active request. |
| iteration_id | string | (none) | 01,02,... | If absent, resolve the single Active iteration. |

### Business Rules
1. Exactly one Active request must exist when request_id not provided.
2. Exactly one Active iteration must exist for iteration-scoped actions.

### Computational Steps
1. Parse request register and select Active.
2. Parse iterations register and select Active.
3. Fail if invariants violated.

### Formulas

$|ActiveRequests|=1$ and $|ActiveIterations|=1$.

### Outputs
- Resolved request_id and iteration_id.

### Performance Benchmarks
- Under 1 second for typical register sizes.

### Accuracy Metrics
N/A.

### Operational Constraints
- Must not guess; fail on invalid state.

### Reference to Executable Code
- .aib_brain/tools/common.py

### Test Cases (Minimum)
- Positive: one Active request -> resolves.
- Failure: two Active requests -> fails.

### Change History (Append-Only)
- 2026-03-22: Documented algorithm as active.

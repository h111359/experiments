# Iterations

| iteration_id | state | created_at | closed_at | summary |
| --- | --- | --- | --- | --- |

Validation rules:
- Exactly one `Active` iteration is allowed.
- `closed_at` is required when `state = Completed`.
- Iteration IDs are strictly ascending and never reused.

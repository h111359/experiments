# Requests Register

| request_id | title | folder | state | created_at | closed_at |
| --- | --- | --- | --- | --- | --- |

Validation rules:
- Only one row may have `state = Active`.
- `request_id` must follow `R-YYYYMMDD-HHmi`.
- `folder` must be workspace-relative and unique.
- `closed_at` must be empty for `Active` rows.

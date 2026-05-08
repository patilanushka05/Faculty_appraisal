# Save Appraisal Draft (Snapshot)

## Endpoint
- **Method:** PUT
- **URL:** `/api/v1/appraisal/snapshot`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated faculty (own data only)

## Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |
| `payload` | object | Yes | Full form state — any JSON structure the frontend uses |

```json
{
  "academic_year": "2024-25",
  "payload": { ...entire form state... }
}
```

## Response (200)
```json
{ "message": "Saved" }
```

## Database
- Reads `appraisal_snapshots` to check for existing row
- If exists: updates `payload` in-place (uses `flag_modified` for JSONB mutation)
- If not: inserts new row
- Commits

## Notes
- This is an auto-save / draft endpoint. It only touches `appraisal_snapshots` — no normalized tables are written.
- Call this frequently (e.g. on every section change) to preserve progress.
- Submitting the final form uses `POST /appraisal/submit`, not this endpoint.

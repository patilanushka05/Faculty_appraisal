# Get Appraisal Draft (Snapshot)

## Endpoint
- **Method:** GET
- **URL:** `/api/v1/appraisal/snapshot`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated faculty (own data only)

## Query Parameters
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |

## Response (200)
Returns the full saved snapshot object, or `null` if no draft exists yet.

```json
{
  "id": "uuid",
  "faculty_email": "string",
  "academic_year": "string",
  "payload": { ...full form state as saved by the frontend... },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## Database
- Reads `appraisal_snapshots` WHERE `faculty_email = current_user.email AND academic_year = ?`

## Notes
- The `payload` is whatever JSON the frontend saved — the backend stores and returns it as-is (JSONB).
- Use this on page load to restore a faculty member's in-progress form.

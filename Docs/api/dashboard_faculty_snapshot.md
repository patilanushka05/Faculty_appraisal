# Get Faculty Snapshot (Authority View)

## Endpoint
- **Method:** GET
- **URL:** `/api/v1/dashboard/faculty/{email}`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any role with authority over the target faculty

## Path Parameters
| Field | Type | Notes |
|---|---|---|
| `email` | string | Email of the faculty whose snapshot to retrieve |

## Query Parameters
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |

## Response (200)
Returns the faculty's full snapshot object (same shape as `GET /appraisal/snapshot`), or `null` if not yet submitted/saved.

```json
{
  "id": "uuid",
  "faculty_email": "string",
  "academic_year": "string",
  "payload": { ...full form state... },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## Error Responses
| Status | Condition |
|---|---|
| 403 | Caller does not have authority over this faculty |
| 404 | Faculty profile not found |

## Database
1. Reads `faculty_profiles` to find the target and get their `school`/`department`/`appraisal_role`
2. Checks authority using the role hierarchy
3. Reads `appraisal_snapshots` WHERE `faculty_email = ? AND academic_year = ?`

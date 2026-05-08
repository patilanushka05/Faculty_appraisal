# Non-Teaching Review (RO / Registrar / VC)

## Endpoint
- **Method:** PUT
- **URL:** `/api/v1/non-teaching/review/{email}`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Reporting Officer, Registrar, VC (or Admin)

## Path Parameters
| Field | Type | Notes |
|---|---|---|
| `email` | string | Email of the staff member being reviewed |

## Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | |
| `total_score` | number | No | The reviewer's total score for the staff |
| `payload` | object | No | Updated form payload if reviewer is annotating the form |

```json
{
  "academic_year": "2024-25",
  "total_score": 72.0,
  "payload": { ...optional updated form state... }
}
```

## Response (200)
Returns the updated `non_teaching_appraisals` row.

## Error Responses
| Status | Condition |
|---|---|
| 403 | Caller does not have authority over this staff member, or wrong role |
| 404 | Staff profile not found or appraisal not found |

## Database
1. Reads `faculty_profiles` to verify target exists and check authority
2. Reads `non_teaching_appraisals` for the staff/year
3. Updates the appropriate total column and status, and sets the reviewed-at timestamp:

| Reviewer role | Column updated | New status | Timestamp field |
|---|---|---|---|
| Reporting Officer | `ro_total` | `Reporting Officer Reviewed` | `ro_reviewed_at` |
| Registrar | `registrar_total` | `Registrar Reviewed` | `registrar_reviewed_at` |
| VC | `vc_total` | `VC Approved` | `vc_reviewed_at` |

4. Commits

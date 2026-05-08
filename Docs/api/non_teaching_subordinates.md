# Non-Teaching Subordinates Dashboard

## Endpoint
- **Method:** GET
- **URL:** `/api/v1/non-teaching/subordinates`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Registrar (sees all), Reporting Officer (sees their school + department only)

## Query Parameters
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |

## Visibility rules
| Role | Sees |
|---|---|
| Registrar / VC | All non-teaching staff |
| Reporting Officer | Staff in their own `school` AND `department` |
| Others | Empty array |

## Response (200)
Array of non-teaching staff appraisal summaries:
```json
[
  {
    "staff_email": "string",
    "name": "string",
    "designation": "string",
    "department": "string",
    "appraisalRole": "string",
    "status": "Draft | Submitted | Reporting Officer Reviewed | Registrar Reviewed | VC Approved",
    "submittedOn": "date | null",
    "selfTotal": 0,
    "roTotal": 0,
    "registrarTotal": 0,
    "vcTotal": 0,
    "payload": { ...full form state... }
  }
]
```

## Database
- Joins `non_teaching_appraisals` with `faculty_profiles` on `staff_email = email`
- Filters by `academic_year` and visibility rules

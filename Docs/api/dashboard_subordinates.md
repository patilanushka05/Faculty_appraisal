# Get Dashboard Subordinates

## Endpoint
- **Method:** GET
- **URL:** `/api/v1/dashboard/subordinates`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** HOD, Director, Dean, VC, Registrar, Center Head (faculty returns empty array)

## Query Parameters
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |
| `schools` | string | No | Comma-separated school codes. Only used by VC/Registrar to filter. e.g. `SoCSEA,SoBB` |

## Visibility rules by role
| Role | Sees |
|---|---|
| VC / Registrar | All schools (or filtered by `schools` param) |
| Dean of Engineering | SoCSEA, SoBB, SoCE, SoEMR only |
| Dean of Non-Engineering | SoC, SoMCS, CioD, SoAA only |
| Director / Reporting Officer | Their own school only |
| Center Head | CISR only |
| HOD | Their own school AND department only |
| Faculty | Empty array |

## Response (200)
Array of subordinate objects:
```json
[
  {
    "email": "string",
    "name": "string",
    "department": "string",
    "school": "string",
    "appraisalRole": "string",
    "status": "string",
    "submittedOn": "date | null",
    "selfPartA": 0,
    "selfPartB": 0,
    "selfTotal": 0,
    "hodPartA": 0,
    "hodPartB": 0,
    "hodTotal": 0,
    "hodRemarks": "string",
    "directorPartA": 0,
    "directorTotal": 0,
    "deanTotal": 0,
    "vcTotal": 0
  }
]
```
Score fields (e.g. `hodPartA`, `directorTotal`) are only present if that authority has submitted a review. Not all fields appear for every row.

## Database
1. Joins `faculty_profiles` with `declarations` (LEFT JOIN on email) — filtered by role visibility rules above
2. Fetches ALL `appraisal_reviews` for the academic year in a **single batched query** (`WHERE faculty_email IN (...)`)
3. Groups reviews by email in Python — no N+1 queries

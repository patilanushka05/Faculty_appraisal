# Submit Appraisal Review (HOD / Center Head / Director / Dean / VC)

## Endpoints
Each authority role has its own URL. The request body and response are identical for all.

| Role | Method | URL |
|---|---|---|
| HOD | PUT | `/api/v1/appraisal-remarks/hod/{email}` |
| Center Head | PUT | `/api/v1/appraisal-remarks/center-head/{email}` |
| Director | PUT | `/api/v1/appraisal-remarks/director/{email}` |
| Dean | PUT | `/api/v1/appraisal-remarks/dean/{email}` |
| VC | PUT | `/api/v1/appraisal-remarks/final/{email}` |

- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Must match the endpoint's role (or `admin`)

## Path Parameters
| Field | Type | Notes |
|---|---|---|
| `email` | string | Email of the faculty being reviewed |

## Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |
| `part_a_score` | number | Yes | Authority's Part A score |
| `part_b_score` | number | Yes | Authority's Part B score |
| `total_score` | number | Yes | Combined total |
| `remarks` | string | No | Free-text remarks |
| `section_scores` | object | No | Per-section breakdown — keys are section names, values are scores |

```json
{
  "academic_year": "2024-25",
  "part_a_score": 45.5,
  "part_b_score": 32.0,
  "total_score": 77.5,
  "remarks": "Good performance overall.",
  "section_scores": {
    "lectures": 18,
    "courseFile": 9,
    "journals": 20
  }
}
```

## Response (200)
```json
{
  "message": "Review submitted",
  "status": "pending_dean"
}
```

## Error Responses
| Status | Condition |
|---|---|
| 403 | Wrong role, or caller does not have authority over this faculty |
| 404 | Faculty profile not found |

## Database
All writes happen in a single transaction:

1. **Upserts** `appraisal_reviews` — one row per `(faculty_email, academic_year, reviewer_role)`. Updates scores and remarks if a review already exists.
2. **Updates** individual section tables — if `section_scores` is provided, writes the authority's score into the appropriate score column (`hod_score`, `director_score`, `dean_score`, `vc_score`) across all matching rows for the faculty/year. Center Head score is stored in `director_score`.
3. **Updates** `declarations.status` based on role:

| Reviewer | New declaration status |
|---|---|
| HOD / Center Head | `pending_director` |
| Director | `pending_dean` |
| Dean | `pending_vc` |
| VC | `completed` |

## Notes
- Dean visibility is division-restricted: Dean of Engineering cannot review non-engineering faculty.
- The `section_scores` key names must match the keys used in the submit endpoint (`lectures`, `courseFile`, `journals`, etc.).

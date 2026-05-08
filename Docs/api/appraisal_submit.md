# Submit Appraisal

## Endpoint
- **Method:** POST
- **URL:** `/api/v1/appraisal/submit`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated faculty (own data only)

## Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |
| `form` | object | Yes | All form sections (see structure below) |
| `totals` | object | No | Calculated score totals |

```json
{
  "academic_year": "2024-25",
  "form": {
    "lectures": [ { "semester": "string", "course_code": "string", "planned_classes": 0, "conducted_classes": 0 } ],
    "courseFile": [ { "course": "string", "title": "string", "details": "string" } ],
    "innovDetails": "string",
    "innovScore": 0,
    "projects": [ { "label": "string" } ],
    "quals": [ { "label": "string" } ],
    "feedback": [ { "course_code": "string", "feedback_1": 0, "feedback_2": 0 } ],
    "deptActs": [ { "activity_type": "string", "nature_of_activity": "string" } ],
    "uniActs": [ { "activity_type": "string", "nature_of_activity": "string" } ],
    "society": [ { "activity_type": "string", "status": "string", "short_description": "string" } ],
    "industry": [ { "name": "string", "details": "string" } ],
    "acr": { "hod": 0, "director": 0, "dean": 0, "vc": 0 },
    "journals": [ { "title_with_page_nos": "string", "journal_details": "string", "issn_isbn_no": "string", "indexing": "string" } ],
    "books": [ { "title_and_pages": "string", "book_title_editor": "string", "issn_isbn": "string", "publisher": "string", "coauthor": "string", "first_author": "string" } ],
    "ict": [ { "title": "string", "description": "string", "pedagogy_type": "string", "quadrant": "string" } ],
    "research": [ { "degree": "string", "student_name": "string", "thesis": "string" } ],
    "projects2": [ { "title": "string", "agency": "string", "sanction_date": "DD/MM/YYYY", "amount": 0, "role": "string", "project_status": "string" } ],
    "externalProjects": [ { "title": "string", "agency": "string", "sanction_date": "DD/MM/YYYY", "amount": 0, "role": "string", "project_status": "string" } ],
    "patents": [ { "title": "string", "type": "string", "scope": "string", "patent_date": "DD/MM/YYYY", "patent_status": "string", "file_no": "string" } ],
    "awards": [ { "title": "string", "award_date": "DD/MM/YYYY", "agency": "string", "event_level": "string" } ],
    "confs": [ { "event_title": "string", "type": "string", "hosting_organization": "string", "event_level": "string" } ],
    "proposals": [ { "title": "string", "duration": "string", "agency": "string", "amount": 0 } ],
    "products": [ { "details": "string", "usage": "string" } ],
    "fdps": [ { "program": "string", "duration_days": "string", "organization": "string" } ],
    "training": [ { "company_industry": "string", "duration_days": "string", "nature_of_training": "string" } ]
  },
  "totals": {
    "partATotal": 0,
    "partBTotal": 0,
    "grandTotal": 0
  }
}
```

### Date format
All date fields accept `DD/MM/YYYY`, `YYYY-MM-DD`, or `DD-MM-YYYY`. The backend normalises them before storage.

### Frontend → Backend field aliases
Some frontend field names differ from DB column names. The backend maps them automatically:

| Frontend key | DB column |
|---|---|
| `title_with_page_nos` | `title` |
| `journal_details` | `journal` |
| `issn_isbn_no` / `issn_isbn` | `issn` |
| `course_code_name` / `course_paper` | `course_code` / `course` |
| `nature_of_activity` | `nature` |
| `activity_type` | `activity` |
| `details_of_activity` / `short_description` | `details` |
| `title_and_pages` | `title` |
| `book_title_editor` | `book` |
| `event_title` | `title` |
| `hosting_organization` | `organization` |
| `event_level` | `level` |
| `pedagogy_type` | `type` |
| `company_industry` | `company` |
| `duration_days` | `duration` |
| `nature_of_training` | `nature` |
| `hod` / `director` / `dean` / `vc` | `hod_score` / `director_score` / `dean_score` / `vc_score` |
| `maxMarks` | `max_marks` |

## Response (200)
```json
{
  "message": "Submitted successfully",
  "submitted_at": "2024-01-01T00:00:00"
}
```

## Error Responses
| Status | Condition |
|---|---|
| 400 | `form` key missing from request |
| 422 | `academic_year` missing |
| 500 | DB constraint violation or unexpected error |

## Database
This endpoint performs multiple writes in a single transaction:

1. **Deletes** all existing rows for `(faculty_email, academic_year)` in every Part A and Part B table
2. **Inserts** fresh rows from the submitted form into the normalized tables
3. **Flushes** to surface any constraint violations early
4. **Upserts** `declarations` with `status = 'Submitted'` and the provided totals
5. **Upserts** `appraisal_snapshots` with the full request payload
6. Commits everything atomically — all steps succeed or none do

**Tables written:** `teaching_process`, `course_files`, `innovative_teaching`, `projects_guided`, `qualification_enhancement`, `student_feedback`, `department_activities`, `university_activities`, `social_contributions`, `industry_connect`, `acr_scores`, `journal_publications`, `book_publications`, `ict_pedagogy`, `research_guidance`, `research_projects`, `external_research_projects`, `ipr_records`, `patents`, `awards`, `conferences`, `research_proposals`, `products_developed`, `self_development`, `industrial_training`, `declarations`, `appraisal_snapshots`

# List Appraisal Documents

## Endpoint
- **Method:** GET
- **URL:** `/api/v1/appraisal-documents/`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated user (own documents only)

## Query Parameters
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |

## Response (200)
Array of document records:
```json
[
  {
    "id": "uuid",
    "faculty_email": "string",
    "academic_year": "string",
    "form_family": "string",
    "section": "string",
    "section_title": "string",
    "doc_key": "string",
    "file_name": "string",
    "file_type": "string",
    "file_url": "string",
    "storage_path": "string",
    "uploaded_at": "timestamp"
  }
]
```

## Database
- Reads `appraisal_documents` WHERE `faculty_email = current_user.email AND academic_year = ?`

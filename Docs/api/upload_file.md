# Upload File

## Endpoint
- **Method:** POST
- **URL:** `/api/v1/upload`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated user
- **Content-Type:** `multipart/form-data`

## Request
| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | file (binary) | Yes | The file to upload |

## Response (200)
```json
{
  "url": "https://storage.googleapis.com/...",
  "publicId": "faculty/email@example.com/uuid_filename.pdf",
  "name": "filename.pdf",
  "type": "application/pdf"
}
```

## Error Responses
| Status | Condition |
|---|---|
| 500 | GCS upload failure |

## Storage
- Uploads to Google Cloud Storage bucket (`GCP_STORAGE_BUCKET` env var)
- File path in GCS: `faculty/{user_email}/{uuid}_{filename}`
- Returns the public URL of the uploaded file

## Dev / No-bucket fallback
If `GCP_STORAGE_BUCKET` is not set, returns a mock response with a placeholder URL. No actual upload occurs.

## Notes
- The returned `url` should be stored in the appraisal form payload and submitted with the appraisal.
- This endpoint does **not** write to the database. Document metadata is stored separately when the appraisal is submitted.

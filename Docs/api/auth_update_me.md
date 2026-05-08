# Update My Profile

## Endpoint
- **Method:** PUT
- **URL:** `/api/v1/auth/me`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated user (own profile only)

## Request Body (JSON)
All fields are optional. Only provided fields are updated.

| Field | Type | Notes |
|---|---|---|
| `full_name` | string | |
| `department` | string | |
| `school` | string | |
| `designation` | string | |
| `phone` | string | |
| `avatar` | string | URL to profile picture |

## Response (200)
Same shape as GET `/auth/me`:
```json
{
  "email": "string",
  "full_name": "string",
  "role": "string",
  "appraisal_role": "string",
  "department": "string",
  "school": "string",
  "employee_id": "string",
  "designation": "string",
  "phone": "string",
  "profile_picture_url": "string"
}
```

## Database
- Reads `faculty_profiles` WHERE `email = current_user.email`
- Updates changed fields
- Commits and refreshes

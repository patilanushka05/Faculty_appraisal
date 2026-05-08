# Get My Profile

## Endpoint
- **Method:** GET
- **URL:** `/api/v1/auth/me`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated user

## Request
No body. No query params.

## Response (200)
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

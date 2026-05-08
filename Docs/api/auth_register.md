# Register

## Endpoint
- **Method:** POST
- **URL:** `/api/v1/auth/register`
- **Auth:** Not required

## Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string (email) | Yes | Must be unique |
| `password` | string | Yes | Hashed with bcrypt before storage |
| `full_name` | string | Yes | |
| `appraisal_role` | string | Yes | See allowed values below |
| `school` | string | No | School code (e.g. `SoCSEA`). Deans use `engineering` or `non_engineering`. |
| `department` | string | No | Required for HOD role |
| `designation` | string | No | |
| `employee_id` | string | No | |
| `phone` | string | No | |
| `qualification` | string | No | |
| `teaching_experience` | string | No | |

**Allowed `appraisal_role` values:**
`faculty`, `hod`, `center_head`, `director`, `dean`, `vc`, `non_teaching_staff`, `reporting_officer`, `registrar`

**Dean `school` values:**
- `engineering` — oversees SoCSEA, SoBB, SoCE, SoEMR
- `non_engineering` — oversees SoC, SoMCS, CioD, SoAA

## Response (200)
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "string"
}
```

## Error Responses
| Status | Condition |
|---|---|
| 400 | Email already registered |
| 422 | Missing required fields |

## Database
- Reads `faculty_profiles` to check for duplicate email
- Inserts new row into `faculty_profiles` with `is_verified = false`
- Sends verification email with a JWT token link

## Notes
- Account cannot log in until the email verification link is clicked.
- `forgot_password` and `reset_password` endpoints exist but are stubs — they return success without doing anything.

# Change Password

## Endpoint
- **Method:** POST
- **URL:** `/api/v1/auth/change-password`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated user (own account only)

## Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `current_password` | string | Yes | Must match the stored bcrypt hash |
| `new_password` | string | Yes | Will be bcrypt-hashed before storage |

## Response (200)
```json
{ "message": "Password changed successfully" }
```

## Error Responses
| Status | Condition |
|---|---|
| 400 | `current_password` does not match |

## Database
- Reads `faculty_profiles` to verify current password hash
- Updates `password_hash` with new bcrypt hash

# Login

## Endpoint
- **Method:** POST
- **URL:** `/api/v1/auth/login`
- **Auth:** Not required

## Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `email` | string (email) | Yes | Must match a registered account |
| `password` | string | Yes | Plaintext — bcrypt-verified server-side |

## Response (200)
```json
{
  "token": "eyJ...",
  "profile": {
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
}
```

## Error Responses
| Status | Condition |
|---|---|
| 401 | Email not found or wrong password |
| 403 | Account exists but email not verified yet |

## Database
- Reads `faculty_profiles` WHERE `email = ?`
- Checks `password_hash` with bcrypt
- Checks `is_verified = true` before allowing login
- No writes

## Notes
- The returned `token` is a JWT. Store it and send it as `Authorization: Bearer <token>` on all protected requests.
- `role` and `appraisal_role` are the same field — both are returned for compatibility.

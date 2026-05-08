# Verify Email

## Endpoint
- **Method:** GET
- **URL:** `/api/v1/auth/verify-email`
- **Auth:** Not required (uses token query param)

## Query Parameters
| Field | Type | Required | Notes |
|---|---|---|---|
| `token` | string | Yes | JWT sent in the registration verification email |

## Response
Always redirects (302) — never returns JSON.

| Redirect destination | Condition |
|---|---|
| `{FRONTEND_URL}/login?verified=true` | Success |
| `{FRONTEND_URL}/login?error=invalid_token` | Token malformed or expired |
| `{FRONTEND_URL}/login?error=user_not_found` | Token valid but user deleted |
| `{FRONTEND_URL}/login?error=verification_failed` | Any other exception |

## Database
- Reads `faculty_profiles` WHERE `email` from token
- Updates `is_verified = true` on success
- No-op if already verified (idempotent)

## Notes
- The link is embedded in the verification email sent during registration.
- The frontend should read the `verified` or `error` query param on the `/login` page and show the appropriate message.

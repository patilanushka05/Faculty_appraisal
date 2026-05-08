# Non-Teaching Appraisal — Get & Save

## Get Appraisal

### Endpoint
- **Method:** GET
- **URL:** `/api/v1/non-teaching/appraisal`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated user (own data only)

### Query Parameters
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | e.g. `2024-25` |

### Response (200)
Returns the full `non_teaching_appraisals` row, or `null` if none exists.
```json
{
  "id": "uuid",
  "staff_email": "string",
  "academic_year": "string",
  "payload": { ...form state... },
  "status": "Draft | Submitted | Reporting Officer Reviewed | Registrar Reviewed | VC Approved",
  "self_total": 0,
  "ro_total": 0,
  "registrar_total": 0,
  "vc_total": 0,
  "submitted_at": "timestamp | null",
  "ro_reviewed_at": "timestamp | null",
  "registrar_reviewed_at": "timestamp | null",
  "vc_reviewed_at": "timestamp | null"
}
```

### Database
- Reads `non_teaching_appraisals` WHERE `staff_email = ? AND academic_year = ?`

---

## Save / Submit Appraisal

### Endpoint
- **Method:** PUT
- **URL:** `/api/v1/non-teaching/appraisal`
- **Auth:** Required (`Authorization: Bearer <token>`)
- **Roles:** Any authenticated user (own data only)

### Request Body (JSON)
| Field | Type | Required | Notes |
|---|---|---|---|
| `academic_year` | string | Yes | |
| `status` | string | Yes | Use `Draft` for save, `Submitted` for final submit |
| `payload` | object | Yes | Full form state |
| `self_total` | number | No | Staff's self-assessed total |

```json
{
  "academic_year": "2024-25",
  "status": "Submitted",
  "self_total": 65.5,
  "payload": { ...full form state... }
}
```

**Allowed `status` values:** `Draft`, `Submitted`, `Reporting Officer Reviewed`, `Registrar Reviewed`, `VC Approved`

### Response (200)
Returns the updated `non_teaching_appraisals` row.

### Database
- Upserts `non_teaching_appraisals` (inserts or updates based on `staff_email + academic_year`)

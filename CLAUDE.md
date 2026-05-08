# Faculty Appraisal System — CLAUDE.md

## Project Overview
Async FastAPI backend for a multi-school faculty appraisal system at DYP University. Supports 8 schools, 5-level role hierarchy, two appraisal form types (teaching + non-teaching), and dual cloud/on-premise deployment.

- **Frontend**: React/Vite on Netlify (`https://dypfacultyappraisal.netlify.app`)
- **Backend**: FastAPI on GCP Cloud Run (`asia-south1`, project `facultyappraisal-495011`)
- **Database**: PostgreSQL via Supabase (pooled, port 6543)
- **Storage**: Google Cloud Storage (`GCP_STORAGE_BUCKET`)
- **Auth**: Local JWT (default) or Supabase Auth (`USE_LOCAL_AUTH` toggle)

---

## Source Layout

```
src/
├── main.py              # FastAPI app, CORS, middleware, exception handlers
├── api/v1/              # Route handlers (auth, appraisal, dashboard, documents, remarks, non_teaching, upload)
├── crud/                # DB operations (core, part_a, part_b, non_teaching)
├── models/              # SQLAlchemy ORM models (core, part_a, part_b, non_teaching)
├── schema/              # Pydantic v2 schemas (core, part_a, part_b, non_teaching)
└── setup/
    ├── database.py      # Async engine, connection pool (size=10, overflow=20)
    ├── dependencies.py  # JWT auth, role hierarchy, CurrentUser dependency
    ├── local_auth.py    # Local bcrypt auth
    ├── storage_utils.py # GCS + local storage abstraction
    ├── supabase_client.py
    └── email_utils.py
main.py                  # Gunicorn entrypoint (proxies src/main.py)
```

---

## Role Hierarchy
`Faculty(0) < HOD(1) < Section Head / Director(2) < Registrar(3.5) < Dean(3) < VC(4) < Admin(5)`

Implemented in `src/setup/dependencies.py` via `has_authority_over()`. Use `CurrentUser` dependency on all protected routes.

## Form Types
- **Type 1**: Schools 1 (SOCSEA), 3 (SOBB), 7 (SOCE), 8 (SOEMR), 2 (SOC) — standard engineering/science
- **Type 2**: School 4 (SOMCS) — media/communication
- **Type 3**: Schools 5 (SOD), 6 (SOAA) — design/applied arts
- School 8 (SOEMR) is unique: has HOD layer reporting to Director
- Mapped in `get_form_family()` in `src/setup/dependencies.py`

---

## Environment Variables (see `.env.example`)
| Variable | Notes |
|---|---|
| `DATABASE_URL` | Must use `postgresql+asyncpg://` + Supabase port 6543 |
| `USE_LOCAL_AUTH` | `true` = local JWT, `false` = Supabase Auth |
| `JWT_SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `APP_URL` | Backend public URL, no trailing slash |
| `FRONTEND_URL` | Frontend public URL, no trailing slash |
| `USE_LOCAL_STORAGE` | `true` = local `./uploads`, `false` = GCS |
| `GCP_STORAGE_BUCKET` | GCS bucket name |
| `ALLOW_MOCK_USER` | Dev only — bypasses login |

---

## Running Locally
```bash
# Install deps
uv pip install -r pyproject.toml

# Run dev server
uvicorn main:app --reload --port 8000
```
API docs at `http://localhost:8000/docs`

## Running with Docker
```bash
docker compose up --build
```

---

## GCP Deployment
```bash
export PROJECT_ID=facultyappraisal-495011

# Build and push image
gcloud builds submit --tag asia-south1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/fastapi-backend .

# Deploy to Cloud Run
gcloud run deploy fastapi-backend \
    --image asia-south1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/fastapi-backend \
    --region asia-south1 \
    --allow-unauthenticated
```
CI/CD via GitHub Actions — push to `main` triggers automatic deploy. Required secrets: `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_SA_KEY`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`.

---

## Key Patterns

### Adding a new appraisal endpoint
Each appraisal category follows a standard 6-endpoint REST pattern:
- `POST /` — create
- `GET /` — list all
- `GET /faculty/{faculty_id}` — list by faculty
- `PUT /{id}` — update
- `DELETE /{id}` — delete
- `GET /summary/{faculty_id}` — score aggregation

### Database sessions
Always use the `get_db` dependency:
```python
from src.setup.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def my_route(db: AsyncSession = Depends(get_db)):
    ...
```

### Modifying JSONB fields
Import `flag_modified` from the direct path (not the top-level namespace — it breaks on some SQLAlchemy builds):
```python
from sqlalchemy.orm.attributes import flag_modified  # correct
# NOT: from sqlalchemy.orm import flag_modified
```

### Auth guard
```python
from src.setup.dependencies import CurrentUser
async def my_route(current_user: CurrentUser):
    ...
```

---

## CORS Allowed Origins
Configured in `src/main.py`. Currently hardcoded — add new frontend URLs to the `origins` list there.

Current allowed: `localhost:5173/3000/8000`, `https://dypfacultyappraisal.netlify.app`, one preview Netlify URL.

---

## Known Issues / Gotchas
- `--timeout 0` in Gunicorn CMD disables worker timeout — intentional for long async operations but watch for hung requests
- `statement_cache_size: 0` in database engine is required for PgBouncer compatibility
- Docker image runs as root (no non-root user configured) — acceptable for Cloud Run but worth fixing for stricter environments
- `pool_size=10, max_overflow=20` — up to 30 DB connections per container instance; watch Supabase pooler limits if scaling Cloud Run instances

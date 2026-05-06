# Local Deployment & Migration Guide

This guide explains how to deploy the Faculty Appraisal System on a local server using a standalone PostgreSQL database and local Python-based authentication, while maintaining Supabase as a fallback option.

## 1. System Overview

The system supports a **Dual-Mode** architecture. You can toggle between Supabase-managed services and local server-managed services using environment variables.

| Feature | Supabase Mode (Default) | Local Server Mode |
| :--- | :--- | :--- |
| **Database** | Supabase PostgreSQL | Standalone PostgreSQL |
| **Authentication** | Supabase Auth (JWT) | Python JWT + `passlib` (Bcrypt) |
| **File Storage** | Supabase Storage Buckets | Local File System (`./uploads`) |

---

## 2. Configuration (Environment Variables)

To switch to Local Server mode, update your `.env` file with the following:

### Database
```env
# Change this to your local Postgres connection string
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

### Authentication
```env
# Enable local JWT auth
USE_LOCAL_AUTH=true
# Secret key for signing tokens (Must be strong and kept secret!)
JWT_SECRET_KEY=your_generate_a_random_string_here
```

### Storage
```env
# Enable local file system storage
USE_LOCAL_STORAGE=true
# Base directory for uploads (relative to project root)
LOCAL_STORAGE_DIR=./uploads
```

---

## 3. How Authentication Works

### Local Auth Flow
1. **Registration:** Use `POST /api/v1/auth/register`. This creates a record in the `faculty` table and hashes the password using Bcrypt.
2. **Login:** Use `POST /api/v1/auth/login`. This verifies the password and returns a JWT token.
3. **Verification:** The backend `get_current_user` dependency decodes the JWT using the `JWT_SECRET_KEY` and extracts the user's `id`, `roles`, and `department`.

### Differences from Supabase
- **Endpoints:** You must use the new `/auth` endpoints instead of Supabase's Auth API.
- **Token Format:** While both use JWT, the payload structure is slightly different to ensure compatibility with local models.

---

## 4. How Storage Works

### Local Storage Flow
1. **Upload:** When a file is uploaded (e.g., in Enclosures), it is saved to `{LOCAL_STORAGE_DIR}/{faculty_id}/{filename}`.
2. **Path Storage:** The database stores the path as `/uploads/{faculty_id}/{filename}`.
3. **Serving:** The FastAPI app mounts the `./uploads` directory statically. Files can be accessed directly via `http://server-url/uploads/...`.

### Differences from Supabase
- **URL Format:** Supabase paths are bucket-relative strings. Local paths are absolute URL paths starting with `/uploads/`.
- **Latency:** Local storage is significantly faster as it avoids network overhead to external buckets.

---

## 5. Emergency Fallback

If the local server's database or disk fails, you can quickly point back to Supabase:
1. Change `DATABASE_URL` to your Supabase connection string.
2. Set `USE_LOCAL_AUTH=false`.
3. Set `USE_LOCAL_STORAGE=false`.
4. Restart the server.

*Note: Data created in local mode will not be automatically synced to Supabase.*

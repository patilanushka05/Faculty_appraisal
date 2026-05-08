# Faculty Appraisal System: Migration & Portability Strategy

This document provides a comprehensive technical roadmap for migrating the system infrastructure from the current cloud provider (Supabase) to alternative environments, such as a local PostgreSQL server or different authentication providers (Firebase).

---

## 1. Architectural Overview
The system is built using an **Asynchronous Layered Architecture**. The application logic (APIs and CRUD) is strictly decoupled from the infrastructure (Database, Auth, and Storage). This ensures that migrating to a new environment is a surgical update to specific configuration files rather than a system-wide rewrite.

**Current Infrastructure Stack:**
*   **Framework:** FastAPI (Python 3.12+)
*   **Database:** Supabase Managed PostgreSQL (Accessed via `asyncpg`)
*   **Authentication:** Supabase Auth (JWT verification)
*   **File Storage:** Supabase Storage (PDF proof management)

---

## 2. Migration Scenarios

### Scenario A: Moving Database to Local PostgreSQL (Keep Supabase Auth)
In this scenario, the data is moved to a private server, but user management remains in the cloud.

*   **Changes Required:** 1 file (`.env`).
*   **Technical Steps:**
    1.  Export schema and data from Supabase.
    2.  Set up local PostgreSQL (v15+).
    3.  Update `DATABASE_URL` in the environment variables.
*   **Risks:** 
    *   **Latency:** Every request will perform an external API call to Supabase for Auth before querying the local database, adding ~50-100ms per request.
    *   **Foreign Keys:** The physical link between the `faculty` table and the `auth.users` table will be severed. Database constraints must be modified to use `UUID` strings without the `REFERENCES auth.users` link.

### Scenario B: Switching Auth to Firebase (Keep Supabase DB)
The client moves user management to Firebase while keeping the data on the Supabase cloud.

*   **Changes Required:** 1 file (`src/setup/dependencies.py`).
*   **Technical Steps:**
    1.  Install `firebase-admin` SDK.
    2.  Update the `get_current_user` dependency to use `auth.verify_id_token()`.
    3.  Map Firebase "Custom Claims" to the existing internal `User` object.
*   **Impact:** The existing 60+ API endpoints and CRUD operations will remain untouched, as they depend on the `User` object interface, not the provider.

### Scenario C: Full On-Premise Deployment
The client moves Database, Auth, and Storage to a private local network.

*   **Changes Required:** 3 setup files.
*   **Strategy:**
    *   **Database:** Standard local PostgreSQL.
    *   **Auth:** Built-in PostgreSQL auth (already implemented in `src/setup/local_auth.py`).
    *   **Storage:** Local disk storage via the `uploads/` directory.

---

## 3. Storage Migration Guide (GCS to Local)

Moving from Google Cloud Storage to a local server is a two-step process involving data synchronization and configuration updates.

### Step 1: Sync Data from Cloud
Use the Google Cloud SDK (`gsutil`) to download all existing documents to the local server.
```bash
# Install gcloud CLI first
# Run this from the project root on the local server
gsutil -m rsync -r gs://your-gcs-bucket-name ./uploads
```
This preserves the directory structure (`{faculty_id}/{filename}`) required by the database.

### Step 2: Update Configuration
Update the `.env` file to disable GCP and enable Local Storage:
```env
USE_LOCAL_STORAGE="true"
LOCAL_STORAGE_DIR="./uploads"

# You can now safely remove GCP credentials
GCP_STORAGE_BUCKET=""
GCP_PROJECT_ID=""
```

### Step 3: Technical Implementation Details
*   **Serving Files:** The backend is pre-configured to mount the `./uploads` directory as a static route (`/uploads`).
*   **URL Logic:** When `USE_LOCAL_STORAGE` is enabled, the system automatically saves paths as `/uploads/faculty_id/file.pdf`. The frontend will be able to access these via `http://<backend-ip>/uploads/...`.
*   **Security:** Ensure the `uploads/` directory on the local server has restricted OS-level permissions (e.g., `chmod 700` for the app user).

---

## 4. Local Server Requirements

To maintain the current high-performance levels (<200ms latency), a local PostgreSQL server must meet the following specifications:

1.  **PostgreSQL Version:** 15 or higher.
2.  **Required Extensions:** `uuid-ossp` and `pgcrypto`.
3.  **Connection Pooling:** High-traffic environments should implement **PgBouncer**. 
    *   *Note: Our code is pre-configured for PgBouncer's "Transaction Mode" via the `statement_cache_size: 0` setting in `database.py`.*
4.  **Schema Alignment:** The local database must use the exact table and column names mapped in the SQLAlchemy models (e.g., `journal_publications`, `book_publications`).

---

## 4. Portability Analysis (File-Level)

| Component | Responsible File | Migration Complexity |
| :--- | :--- | :--- |
| **Database Connection** | `src/setup/database.py` | **Zero.** Config-based via `.env`. |
| **User Authentication** | `src/setup/dependencies.py` | **Low.** Swap token verification logic. |
| **PDF Uploads** | `src/setup/storage_utils.py` | **Medium.** Change Supabase SDK to Local Disk logic. |
| **API Endpoints** | `src/api/` (All files) | **None.** Endpoints are infrastructure-agnostic. |
| **CRUD Logic** | `src/crud/` (All files) | **None.** Logic uses standard SQL patterns. |

---

## 5. Strategic Recommendations

1.  **Data Sovereignty:** If the database is moved locally for privacy reasons, **Authentication should follow**. Using Supabase Auth with a local DB creates a security and latency mismatch.
2.  **Storage Transition:** Moving from Supabase Storage to a local server requires a strategy for handling public/signed URLs for PDF viewing. We recommend a simple Nginx-based static file server for local PDF access.
3.  **Firebase Integration:** If switching to Firebase, ensure the frontend developers also switch to the Firebase Web SDK, as the backend will now expect Firebase-issued JWTs.

---

## 6. Final Verdict
The system currently has a **High Portability Score (9/10)**. The recent transition to an asynchronous `asyncpg` architecture has removed proprietary cloud dependencies from the core query logic, making the system "PostgreSQL Native."

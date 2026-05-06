# Production Deployment Guide (Local Server)

This document provides instructions for the IT team to deploy the Faculty Appraisal System on an internal local server.

## 1. System Requirements
*   **Operating System:** Linux (Ubuntu 22.04+ recommended) or Windows Server with Docker Desktop.
*   **Containerization:** [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).
*   **Database:** PostgreSQL 15 or 16.
*   **Email:** Access to an institutional SMTP server (or Gmail with App Password) for verification emails.

---

## 2. Database Setup (PostgreSQL)

1.  **Create Database:** Create a fresh database named `faculty_appraisal`.
2.  **Schema Initialization:**
    *   Since the system is currently being optimized on Supabase, the final table structure will be provided as a consolidated SQL dump once finalized.
    *   **Note:** Ensure you run the specific updates for Authentication and Non-Teaching staff provided in the `sql_scripts/` folder of this package.

---

## 3. Environment Configuration

Create a `.env` file in the project root. Use the template below:

```env
# --- Database ---
# Replace with internal server credentials
DATABASE_URL="postgresql+asyncpg://<db_user>:<db_password>@<db_host>:5432/faculty_appraisal"

# --- Authentication (Internal Mode) ---
USE_LOCAL_AUTH="true"
# Generate a strong 32-character random string for the key
JWT_SECRET_KEY="YOUR_INTERNAL_SECRET_KEY"
ALLOW_MOCK_USER="false"

# --- Email (SMTP) ---
SMTP_HOST="smtp.example.com"
SMTP_PORT=587
SMTP_USER="appraisal-system@institution.edu"
SMTP_PASSWORD="your_smtp_password"
MAIL_FROM="appraisal-system@institution.edu"

# --- Application URL ---
# The public IP or Domain of the backend server (used for email links)
APP_URL="http://192.168.1.100:8000"

# --- File Storage (Local Mode) ---
USE_LOCAL_STORAGE="true"
LOCAL_STORAGE_DIR="./uploads"

# --- Fallback (Supabase) ---
# Keep these as 'false' unless migrating back to cloud
SUPABASE_URL="optional"
SUPABASE_ANON_KEY="optional"
```

---

## 4. Deployment via Docker

The easiest way to run the system is using the provided Docker configuration.

1.  **Build and Start:**
    ```bash
    docker-compose up --build -d
    ```
2.  **Verify Status:**
    ```bash
    docker ps
    ```
    The server should be running and accessible at `http://<server-ip>:8000`.

---

## 5. Storage Persistence
*   Uploaded PDF documents are stored in the `./uploads` directory relative to where the Docker container is running.
*   **Warning:** Ensure the `./uploads` directory has a persistent volume mount in Docker or is backed up regularly, as it contains all faculty proof documents.

---

## 6. Accessing API Documentation
Once the server is running, the interactive API documentation (Swagger) is available at:
`http://<server-ip>:8000/docs`

Specific frontend integration guides can be found in the `api_docs/` folder of this repository.

# Environment Configuration Guide

This guide explains how to obtain and configure the variables in your `.env` file.

## 1. Database (`DATABASE_URL`)
The backend uses **SQLAlchemy with Asyncpg**. 
- **If using Supabase:** Go to Project Settings > Database > Connection Strings. Select "URI" and choose the **Transaction Mode (Port 6543)**.
- **Important:** You MUST change the prefix from `postgres://` to `postgresql+asyncpg://`.
- **Example:** `postgresql+asyncpg://postgres.xxxx:password@aws-0-asia-south-1.pooler.supabase.com:6543/postgres`

## 2. Security (`JWT_SECRET_KEY`)
This key is used to sign login tokens. It should be a long, random string.
- **How to get it:** Run this command in your terminal:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- Copy the output and paste it as your `JWT_SECRET_KEY`.

## 3. System URLs
- **`APP_URL`**: This is the URL of your **deployed backend**. 
  - On Google Cloud Run: It looks like `https://service-name-xyz.a.run.app`.
  - **Caution:** Ensure it does NOT end with a slash `/`.
- **`FRONTEND_URL`**: This is the URL of your **Netlify/Frontend**.
  - It is used to redirect users back to the login page after they click "Verify Email".

## 4. Email Setup (SMTP)
The system sends verification emails using an SMTP server.
- **If using Gmail:**
  1. Go to your Google Account > Security.
  2. Enable **2-Step Verification**.
  3. Search for **"App Passwords"**.
  4. Generate a new app password for "Other (Custom name: Faculty Appraisal)".
  5. Use that 16-character code as your `SMTP_PASSWORD`.
  6. `SMTP_HOST` will be `smtp.gmail.com` and `SMTP_PORT` will be `587`.

## 5. Storage
- **`GCP_PROJECT_ID`**: The ID of your Google Cloud Project.
- **`GCP_STORAGE_BUCKET`**: Create a bucket in GCS (e.g., `faculty-appraisal-docs`) and put the name here.
- **`USE_LOCAL_STORAGE`**: Set to `true` if you want to store files on the server's hard drive instead of the cloud (not recommended for Cloud Run).

## 6. Authentication Mode
- **`USE_LOCAL_AUTH="true"`**: Recommended. Uses the `faculty_profiles` table in your own database to manage users.
- **`USE_LOCAL_AUTH="false"`**: Uses Supabase Auth (external). Requires `SUPABASE_URL` and `SUPABASE_ANON_KEY`.

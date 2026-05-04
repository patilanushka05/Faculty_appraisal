# Use a slim, stable Python image
FROM python:3.12-slim-bookworm

# 1. Install uv directly from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Set the working directory
WORKDIR /app

# 3. Prevent uv from creating a virtualenv (we'll install to the system)
# and tell it where to store the cache in a writable location
ENV UV_SYSTEM_PYTHON=1
ENV UV_CACHE_DIR=/tmp/uv_cache

# 4. Copy only dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# 5. Install dependencies
# We use --no-cache to keep the image small
RUN uv pip install --no-cache -r pyproject.toml

# 6. Copy the rest of your app code
COPY . .

# 7. Use Gunicorn with Uvicorn workers for production-grade performance
# Parameterize workers (default to 4, but Cloud Run may override this)
# Bind to the PORT environment variable provided by Cloud Run
CMD ["sh", "-c", "gunicorn -w ${WORKERS:-4} -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT:-8080} --timeout 0"]
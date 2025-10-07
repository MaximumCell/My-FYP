# Multi-stage Dockerfile for the PhysicsLab backend
# Uses a slim Python base, installs system dependencies needed for OCR/image processing,
# installs Python deps from backend/requirements.txt and runs the app with gunicorn.

FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY backend/requirements.txt /app/backend/requirements.txt
COPY backend/requirements-prod.txt /app/backend/requirements-prod.txt

RUN python -m pip install --upgrade pip setuptools wheel
# Prefer a lean production requirements file if it exists to speed up builds
RUN if [ -f /app/backend/requirements-prod.txt ]; then \
    pip install --no-cache-dir -r /app/backend/requirements-prod.txt; \
    else \
    pip install --no-cache-dir -r /app/backend/requirements.txt; \
    fi

# Copy the rest of the project
COPY . /app

ENV PATH="/app:${PATH}"

# Expose a default port (used for local testing). Render will provide $PORT at runtime.
ENV PORT=10000
EXPOSE ${PORT}

# Use gunicorn to run the Flask app. Run via shell so environment variable $PORT is expanded by the runtime
# when Render injects the port. This avoids passing the literal string "$PORT" as a port number.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} backend.app:app --workers 1 --threads 2 --timeout 120 --log-level debug --access-logfile - --error-logfile -"]

# A lightweight healthcheck to help local testing (optional)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

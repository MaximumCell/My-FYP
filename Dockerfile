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

RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the rest of the project
COPY . /app

ENV PATH="/app:${PATH}"

# Expose the port Render uses via $PORT at runtime; not required in Dockerfile but useful
EXPOSE 10000

# Use gunicorn to run the Flask app exposed as backend.app:app
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "backend.app:app", "--workers", "1", "--threads", "2", "--timeout", "120"]

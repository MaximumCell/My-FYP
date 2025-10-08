# Optimized Multi-stage Dockerfile for PhysicsLab backend on Render free tier
# Focuses on minimal image size and reliable dependency installation

FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY backend/requirements-prod.txt /tmp/requirements-prod.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements-prod.txt

# Production stage
FROM python:3.11-slim as production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    libfreetype6 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . /app

# Make start script executable and create directories as root
RUN chmod +x /app/start.sh && \
    chmod -R 755 /app/backend && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Set environment variables
ENV PORT=10000 \
    FLASK_APP=backend.app:app \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use the startup script that handles environment setup and dependency testing
CMD ["/app/start.sh"]

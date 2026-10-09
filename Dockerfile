# ==============================================================================
# JISR Arabic Backend & Background Task Worker - Production Multi-Stage Dockerfile
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Dependencies
# ------------------------------------------------------------------------------
FROM python:3.13-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Hardened Production Runtime
# ------------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FAHIM_ENV=production \
    PORT=8000 \
    WEB_CONCURRENCY=2 \
    FASTAPI_THREAD_LIMIT=200

# Install runtime dependencies (libpq for postgresql, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root system user and group for security
RUN groupadd -g 10001 jisr && \
    useradd -u 10001 -g jisr -s /bin/bash -m jisr

# Prepare directories for temporary audio synthesis cache and task artifacts
RUN mkdir -p /app/tmp/audio-cache /app/tmp/task-artifacts && \
    chown -R jisr:jisr /app

# Copy application backend codebase and assets
COPY --chown=jisr:jisr backend /app/backend
COPY --chown=jisr:jisr curriculum-ocr-arabic.txt /app/curriculum-ocr-arabic.txt
COPY --chown=jisr:jisr entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch to unprivileged user
USER jisr

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]

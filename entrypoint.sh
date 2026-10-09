#!/bin/sh
set -e

echo ">> [JISR Entrypoint] Initializing container in mode: ${FAHIM_ENV:-production}..."

# Wait for Redis if configured
if [ -n "$REDIS_URL" ] && [ "$WAIT_FOR_REDIS" = "1" ]; then
    echo ">> [JISR Entrypoint] Checking Redis connectivity..."
fi

# Apply database migrations if running as API service
if [ "${RUN_MIGRATIONS:-1}" = "1" ] && [ "$1" = "api" ]; then
    echo ">> [JISR Entrypoint] Verifying database schema & applying migrations..."
    python -m backend.migrations upgrade || {
        echo ">> [JISR Entrypoint] Warning: Migration command returned non-zero exit code."
        if [ "${STRICT_MIGRATION_CHECK:-0}" = "1" ]; then
            exit 1
        fi
    }
    echo ">> [JISR Entrypoint] Database schema verified."
fi

# Service launcher
if [ "$1" = "api" ]; then
    echo ">> [JISR Entrypoint] Starting JISR FastAPI API Server (workers: ${WEB_CONCURRENCY:-2}, port: ${PORT:-8000})..."
    exec uvicorn backend.main:app \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --workers ${WEB_CONCURRENCY:-2} \
        --proxy-headers \
        --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16}"
elif [ "$1" = "worker" ]; then
    echo ">> [JISR Entrypoint] Starting JISR Standalone Background Task Worker..."
    exec python -m backend.tasks.worker
else
    exec "$@"
fi

#!/usr/bin/env bash
# ==============================================================================
# JISR Arabic Production Container Deployment Script (Linux / macOS)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "======================================================================"
echo ">> JISR Arabic: Production Container Deployment Starting..."
echo "======================================================================"
cd "${ROOT_DIR}"

# 1. Check for .env.production
if [ ! -f ".env.production" ]; then
    if [ -f "backend/.env" ]; then
        echo ">> Notice: Copying database credentials from backend/.env to .env.production..."
        cp backend/.env .env.production
    else
        echo ">> Error: Missing .env.production. Please copy .env.production.example and populate secrets."
        exit 1
    fi
fi

# 2. Validate Compose File Syntax
echo ">> Validating Docker Compose configuration..."
docker compose -f docker-compose.prod.yml config --quiet

# 3. Build & Pull Latest Base Images
echo ">> Building production container images..."
docker compose -f docker-compose.prod.yml --env-file .env.production build

# 4. Launch Services in Detached Mode
echo ">> Launching production services (api, worker, redis, web)..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --remove-orphans

# 5. Wait for Health Probes
echo ">> Waiting for services to pass health checks..."
timeout=60
counter=0
until docker compose -f docker-compose.prod.yml ps api | grep -q "(healthy)" || [ $counter -ge $timeout ]; do
    sleep 2
    counter=$((counter + 2))
    echo "   ... waiting for API healthcheck ($counter/${timeout}s)"
done

if [ $counter -ge $timeout ]; then
    echo ">> Deployment Error: API container failed healthcheck within ${timeout}s."
    docker compose -f docker-compose.prod.yml logs --tail 50 api
    exit 1
fi

echo "======================================================================"
echo ">> JISR Arabic Production Deployment Successful!"
echo ">> Web Gateway:  http://localhost:${HOST_PORT:-80}"
echo ">> API Health:   http://localhost:${HOST_PORT:-80}/api/health"
echo ">> Readiness:    http://localhost:${HOST_PORT:-80}/api/ready"
echo "======================================================================"

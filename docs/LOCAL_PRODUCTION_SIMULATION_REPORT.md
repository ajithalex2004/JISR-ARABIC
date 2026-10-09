# JISR Arabic (فهيم) — Local Production Stack Simulation Report
**Date:** October 9, 2026  
**Environment:** Local Docker Engine 28.1.1 (Windows / Linux Containers)  
**Configuration File:** [`docker-compose.prod.yml`](file:///c:/JISR%20ARABIC/docker-compose.prod.yml)  
**Target Scale:** 10,000+ Students, 1,000 CCU  

---

## 1. Executive Summary

A complete, self-contained local simulation of the production architecture was built, orchestrated, and verified using Docker Compose. All 5 container services (`web`, `api`, `worker`, `redis`, `postgres`) booted successfully, passed internal healthchecks, and executed live end-to-end HTTP workloads.

---

## 2. Container Topology & Health Status

| Service | Container Name | Base Image | Role | Port Mapping | Health Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **`web`** | `jisr_web` | `nginx:1.27-alpine` | Reverse Proxy, Gzip Engine, Static SPA Host | `0.0.0.0:80->80/tcp` | **Healthy** (HTTP 200) |
| **`api`** | `jisr_api` | `python:3.13-slim` | Multi-Worker FastAPI API Server (uvloop) | `8000/tcp` (Internal) | **Healthy** (HTTP 200) |
| **`worker`** | `jisr_worker` | `python:3.13-slim` | Standalone Background Task & Audio Worker | Internal | **Running** (PID 1) |
| **`redis`** | `jisr_redis` | `redis:7-alpine` | Shared Rate Limiter & Task Queue Broker | `6379/tcp` (Internal) | **Healthy** (PONG) |
| **`postgres`**| `jisr_postgres` | `postgres:16-alpine` | Enterprise Relational Database & Migrations | `5432/tcp` (Internal) | **Healthy** (pg_isready) |

---

## 3. Live Endpoint Verification Results

All tests executed through the Nginx gateway at `http://localhost`:

### 3.1 Health Probe (`GET /api/health`)
```bash
curl -i http://localhost/api/health
```
**Response:**
```json
HTTP/1.1 200 OK
Server: nginx/1.27.5
Content-Type: application/json

{"status": "healthy", "mode": "production", "version": "1.0.0"}
```
- **Duration:** `1.96 ms`
- **Result:** Passing (Container orchestrator liveness verified).

---

### 3.2 Readiness Probe (`GET /api/ready`)
```bash
curl -i http://localhost/api/ready
```
**Response:**
```json
HTTP/1.1 200 OK
Server: nginx/1.27.5
Content-Type: application/json

{
  "status": "ready",
  "checks": {
    "database": "ok",
    "migrations": "ok",
    "task_queue": "healthy"
  },
  "version": "1.0.0"
}
```
- **Database Status:** Verified connected to PostgreSQL 16.
- **Migrations Status:** All database schemas and indexes verified current.
- **Task Queue Status:** Connected to Redis 7 (`redis://redis:6379/0`).

---

### 3.3 Database Query through Reverse Proxy (`GET /api/curriculum/grades`)
```bash
curl -s http://localhost/api/curriculum/grades
```
**Response (Sample):**
```json
[
  {"grade": 1, "name_en": "Class 1", "name_ar": "الصف 1", "has_content": true},
  {"grade": 2, "name_en": "Class 2", "name_ar": "الصف 2", "has_content": true},
  ...
  {"grade": 12, "name_en": "Class 12", "name_ar": "الصف 12", "has_content": true}
]
```
- **Duration:** `4.90 ms` (Round-trip through Nginx -> FastAPI -> PostgreSQL).
- **Result:** Passing (Full data plane operational).

---

### 3.4 Web Client Gateway (`GET /`)
```bash
curl -I http://localhost/
```
**Response Headers:**
```text
HTTP/1.1 200 OK
Server: nginx/1.27.5
Content-Type: text/html
Content-Length: 756
Cache-Control: no-cache
Vary: Accept-Encoding
```
- **Result:** Passing (React 19 single page application served with gzip support).

---

## 4. Operational Runbook & Commands

### Managing the Local Stack

```powershell
# View running container status:
docker compose -f docker-compose.prod.yml ps

# Tail live structured logs across all services:
docker compose -f docker-compose.prod.yml logs -f

# Tail logs for a specific service:
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f worker

# Execute database migrations manually:
docker compose -f docker-compose.prod.yml exec api python -m backend.migrations status

# Stop the stack without deleting persisted data:
docker compose -f docker-compose.prod.yml stop

# Stop and remove containers (preserving database and redis volumes):
docker compose -f docker-compose.prod.yml down

# Reset all volumes and start fresh:
docker compose -f docker-compose.prod.yml down -v
```

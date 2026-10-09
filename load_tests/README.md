# JISR Arabic (فهيم) — Enterprise Load & Stress Testing Suite
## Target Capacity: 10,000+ Students | 1,000 Concurrent Users (CCU)

This directory contains the automated performance and stress testing suites for JISR Arabic. It tests the system under realistic school peak workloads and verifies compliance with enterprise Service Level Agreements (SLAs).

---

## 1. SLA Performance Targets

| Metric | Target SLA | Description |
| :--- | :--- | :--- |
| **Simulated CCU** | **1,000 Active Users** | Concurrently reading, listening to audio, and submitting exercises. |
| **Peak Throughput** | **350 – 500 RPS** | System-wide requests per second handled. |
| **Latency p95** | **< 120 ms** | 95% of all HTTP requests complete in under 120ms. |
| **Latency p99** | **< 250 ms** | 99% of all HTTP requests complete in under 250ms. |
| **Failure Rate** | **< 1.0 %** | Non-5xx failure rate under extreme concurrency. |
| **Audio Edge Delivery** | **< 35 ms** | 307 CDN redirects or local cache hits for audio clips. |

---

## 2. Test Execution Engines

We support three execution options:

### Option A: Native Async Benchmark Harness (Instant CLI)
Requires zero external setup or browsers. Uses Python's `asyncio` + `httpx` connection pool.

```powershell
# Run a 100-user warm-up benchmark (15 seconds)
python -m load_tests.benchmark_runner --target http://localhost:8000 --concurrency 100 --duration 15

# Run a 500-user mid-scale benchmark (30 seconds)
python -m load_tests.benchmark_runner --target http://localhost:8000 --concurrency 500 --duration 30

# Run a full 1,000 CCU enterprise stress benchmark and save report
python -m load_tests.benchmark_runner --target http://localhost:8000 --concurrency 1000 --duration 60 --report
```

---

### Option B: Locust Headless / Web UI
Simulates real student, assessment, and parent behavior models with realistic inter-request think time.

```powershell
# 1. Run Headless via CLI (1,000 users, spawn rate 50/sec, run for 2 minutes)
locust -f load_tests/locustfile.py --headless -u 1000 -r 50 --run-time 2m --host http://localhost:8000

# 2. Run with Interactive Web UI (open http://localhost:8089 in browser)
locust -f load_tests/locustfile.py --host http://localhost:8000
```

---

### Option C: Grafana k6 (CI/CD Pipeline & Cloud)
Ideal for automated GitHub Actions workflows, staging gates, or Grafana Cloud testing.

```bash
# Run k6 with automated ramp-up/soak/ramp-down stages
k6 run load_tests/k6_load_test.js

# Target a remote staging or production cluster
k6 run -e TARGET_URL=https://api.jisr.ae load_tests/k6_load_test.js
```

---

## 3. Simulated Traffic Profiles

The load testing suite distributes 1,000 CCU across three weighted user types:

1. **`StudentUser` (70% of traffic / 700 CCU):**
   - Catalog browsing (`GET /api/curriculum/editions`)
   - Lesson fetching (`GET /api/curriculum/lessons/[id]`)
   - Audio playback & 307 CDN redirect checks (`GET /api/audio/cache/[clip]`)
   - Interactive sentence builder puzzles (`POST /api/curriculum/sentence-builder/check`)

2. **`AssessmentUser` (20% of traffic / 200 CCU):**
   - Multi-choice quiz and attempt submission (`POST /api/assessment/attempts`)
   - Exercise booklet verification (`POST /api/curriculum/booklets/check`)
   - Pinned answer key protection and Arabic normalization scoring

3. **`ParentAndAdminUser` (10% of traffic / 100 CCU):**
   - Infrastructure ALB probes (`GET /api/health`, `GET /api/ready`)
   - Grade leaderboard queries (`GET /api/progress/leaderboard`)

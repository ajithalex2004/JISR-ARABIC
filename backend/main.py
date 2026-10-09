from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import os
import time
from collections import defaultdict, deque
from backend.database import engine, Base, SessionLocal
from sqlalchemy import text
from backend.curriculum_seed import seed_database
from backend.api.router import router as api_router
from backend.errors import ApplicationError
from backend.observability import ObservabilityMiddleware, logger
from backend.config import validate_deployment_config
from backend.redis_client import check_rate_limit

environment = os.getenv("FAHIM_ENV", "development").lower()
configured_origins = [origin.strip().rstrip("/") for origin in os.getenv("FAHIM_CORS_ORIGINS", "").split(",") if origin.strip()]
if environment == "production" and not configured_origins:
    raise RuntimeError("FAHIM_CORS_ORIGINS must be configured in production")
cors_origins = configured_origins or ["http://localhost:3000", "http://127.0.0.1:3000"]

app = FastAPI(
    title="Fahim (فاهم) — Your Arabic Learning Companion",
    description="Educational Arabic learning platform for non-native students in UAE schools following CBSE and Ministry of Education curricula.",
    version="1.0.0"
)
app.add_middleware(ObservabilityMiddleware)

import ipaddress

_request_metrics = {"requests_total": 0, "responses_5xx": 0}

def _is_trusted_proxy(ip_str: str) -> bool:
    if not ip_str or ip_str == "unknown":
        return False
    trusted_ranges = os.getenv("FAHIM_TRUSTED_PROXIES", "127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16").split(",")
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        for r in trusted_ranges:
            r = r.strip()
            if not r:
                continue
            if "/" in r:
                if ip_obj in ipaddress.ip_network(r, strict=False):
                    return True
            else:
                if ip_obj == ipaddress.ip_address(r):
                    return True
    except ValueError:
        return False
    return False

def _extract_real_client_ip(request: Request) -> str:
    peer_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for and _is_trusted_proxy(peer_ip):
        return forwarded_for.split(",")[0].strip()
    return peer_ip

@app.middleware("http")
async def distributed_rate_limit(request: Request, call_next):
    _request_metrics["requests_total"] += 1
    path = request.url.path

    # Protect auth, checkout, AI, and TTS endpoints from abuse
    is_auth_checkout = (path.startswith("/api/auth/") or path.startswith("/api/payments/checkout")) and request.method == "POST"
    is_heavy_ai_audio = path.startswith(("/api/ai/", "/api/audio/synthesize"))

    if is_auth_checkout or is_heavy_ai_audio:
        client_ip = _extract_real_client_ip(request)

        if is_auth_checkout:
            limit = 10 if path.endswith(("/login", "/student-pin-login")) else 5
        else:
            limit = 30  # Max 30 requests/minute for heavy AI & TTS endpoints per IP

        rate_key = f"{client_ip}:{path}"
        is_allowed, current_count, retry_after = check_rate_limit(rate_key, limit=limit, window_seconds=60)
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0"
                }
            )

    response = await call_next(request)
    if response.status_code >= 500:
        _request_metrics["responses_5xx"] += 1
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if os.getenv("FAHIM_ENV", "development").lower() == "production":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Versioned API compatibility surface. Existing web clients continue using
# /api/*, while mobile clients can pin /api/v1/* without duplicating every
# route declaration. The middleware maps v1 requests to the same handlers and
# advertises the resolved contract version in the response.
@app.middleware("http")
async def api_version_middleware(request: Request, call_next):
    path = request.scope.get("path", "")
    versioned = path == "/api/v1" or path.startswith("/api/v1/")
    if versioned:
        request.scope["path"] = "/api" + path[len("/api/v1"):]
        request.scope["raw_path"] = request.scope["path"].encode("utf-8")
    response = await call_next(request)
    if versioned:
        response.headers["X-API-Version"] = "v1"
    elif path == "/api" or path.startswith("/api/"):
        response.headers["X-API-Version"] = "v1"
        response.headers["X-API-Canonical"] = "/api/v1"
    return response


@app.exception_handler(ApplicationError)
async def application_error_handler(request: Request, exc: ApplicationError):
    """Keep HTTP status and error payloads stable after service extraction."""
    logger.warning("application error", extra={"path": request.url.path, "status": exc.status_code,
                                                 "error": type(exc).__name__})
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": jsonable_encoder(exc.detail)},
        headers=exc.headers,
    )


@app.on_event("startup")
def on_startup():
    validate_deployment_config()
    from backend.migrations import require_current, upgrade
    if os.getenv("FAHIM_ENV", "development") == "production":
        require_current()
        return
    Base.metadata.create_all(bind=engine)
    upgrade()
    # Demo accounts are opt-in for every environment. Set FAHIM_SEED_DEMO=1
    # explicitly when a local development database needs the demo fixtures.
    if os.getenv("FAHIM_SEED_DEMO", "0") == "1":
        db = SessionLocal()
        try:
            seed_database(db, include_demo_data=True)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

@app.get("/")
def root():
    return {
        "product": "Fahim (فاهم)",
        "tagline": "Your Arabic learning companion (رفيقك لتعلم اللغة العربية)",
        "teacher": "Ask Fahim (اسأل فاهم)",
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health_check():
    """Lightweight liveness probe for orchestrators and container healthchecks.
    Does not execute heavy database queries in production to prevent cascading container restarts.
    Hides internal connection pool statistics in production.
    """
    is_prod = os.getenv("FAHIM_ENV", "development").lower() == "production"
    if is_prod:
        return {
            "status": "healthy",
            "mode": "production",
            "version": app.version
        }
    from backend.database import get_db_pool_status
    from backend.tasks.queue import get_queue_metrics
    pool_status = get_db_pool_status()
    queue_metrics = get_queue_metrics()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={
            "status": "unhealthy",
            "database": "unavailable",
            "mode": "development",
            "pool": pool_status,
            "tasks": queue_metrics
        })
    return {
        "status": "healthy",
        "database": "connected",
        "mode": "development",
        "pool": pool_status,
        "tasks": queue_metrics
    }


@app.get("/api/ready")
def readiness_check():
    """Readiness probe for load balancers and deployment controllers.
    Verifies that the database connection, migrations, and Redis queue are operational.
    In production, hides internal pool metrics and task worker internals.
    """
    is_prod = os.getenv("FAHIM_ENV", "development").lower() == "production"
    from backend.database import get_db_pool_status
    from backend.tasks.queue import get_queue_metrics
    task_metrics = get_queue_metrics()
    checks = {"database": "ok", "migrations": "ok", "task_queue": task_metrics.get("status", "unknown")}

    if is_prod and task_metrics.get("status") != "healthy":
        checks["task_queue"] = "error"
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": checks,
                "error": "Redis task queue unavailable"
            }
        )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        from backend.migrations import require_current
        require_current()
    except Exception as exc:
        checks["database"] = "error"
        checks["migrations"] = "error"
        content = {"status": "not_ready", "checks": checks, "error_type": type(exc).__name__}
        if not is_prod:
            content["pool"] = get_db_pool_status()
            content["tasks"] = task_metrics
        return JSONResponse(status_code=503, content=content)

    if is_prod:
        return {"status": "ready", "checks": checks, "version": app.version}
    return {
        "status": "ready",
        "checks": checks,
        "version": app.version,
        "pool": get_db_pool_status(),
        "tasks": task_metrics
    }


@app.on_event("startup")
def on_startup():
    try:
        import anyio.to_thread
        limiter = anyio.to_thread.current_default_thread_limiter()
        limiter.total_tokens = int(os.getenv("FASTAPI_THREAD_LIMIT", "200"))
    except Exception:
        pass
    if os.getenv("FAHIM_DISABLE_IN_PROCESS_WORKER", "").lower() not in ("1", "true", "yes"):
        from backend.tasks.worker import start_in_process_worker
        start_in_process_worker()


@app.on_event("shutdown")
def on_shutdown():
    from backend.tasks.worker import stop_in_process_worker
    stop_in_process_worker()


@app.get("/api/metrics")
def metrics():
    """Minimal scrape endpoint for deployment monitoring."""
    return {**_request_metrics, "mode": os.getenv("FAHIM_ENV", "development")}


@app.get("/download/apk")
@app.get("/apk")
def download_latest_apk():
    from fastapi.responses import FileResponse
    apk_path = os.path.abspath("JISR_Arabic_v2.4.apk")
    if os.path.exists(apk_path):
        return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename="JISR_Arabic_v2.4.apk")
    return JSONResponse(status_code=404, content={"detail": "APK not found"})


@app.get("/api/meta")
def api_contract_metadata():
    return {
        "api_version": "v1",
        "canonical_base_url": "/api/v1",
        "legacy_base_url": "/api",
        "contract_status": "stable",
        "backward_compatibility": "Legacy /api routes remain supported during migration.",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

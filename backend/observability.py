"""Structured application logs and security audit events."""
import contextvars
import json
import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

request_id_var = contextvars.ContextVar("request_id", default="-")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key in ("event", "method", "path", "status", "duration_ms", "user_id", "ip", "error"):
            if hasattr(record, key): payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)

def configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger("fahim")
    root.setLevel(logging.INFO)
    if not root.handlers:
        root.addHandler(handler)
    return root

logger = configure_logging()

def audit_event(event: str, **fields):
    logger.info("security audit event", extra={"event": event, **fields})

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
            logger.info("request complete", extra={"method": request.method, "path": request.url.path,
                                                     "status": response.status_code,
                                                     "duration_ms": round((time.perf_counter()-started)*1000, 2)})
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            logger.exception("request failed", extra={"method": request.method, "path": request.url.path,
                                                        "status": 500, "error": type(exc).__name__})
            raise
        finally:
            request_id_var.reset(token)

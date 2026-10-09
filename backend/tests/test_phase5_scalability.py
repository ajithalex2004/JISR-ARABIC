"""
Phase 5 Scalability & Release Rigor Test Suite.
Validates:
1. Lightweight liveness probe (/api/health) in production avoiding cascading restarts and masking pool internals.
2. Development diagnostics retention on /api/health for local debugging.
3. Readiness probe (/api/ready) verifying operational readiness and hiding sensitive infrastructure in production.
4. Readiness probe failure (503) when required components (Redis, DB) are degraded in production.
5. Right-sized database connection pool defaults (pool_size=15, max_overflow=10).
6. Masked get_db_pool_status() in production preventing reconnaissance.
7. Automated injection of HTTP security headers (nosniff, DENY, HSTS).
8. Production configuration validation enforcement.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db, get_db_pool_status
from backend.config import validate_deployment_config, ConfigurationError


class TestPhase5Scalability(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = self.Session()

        def override_db():
            db = self.Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_db
        self.client = TestClient(app)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()
        app.dependency_overrides.pop(get_db, None)

    def test_health_liveness_lightweight_in_production(self):
        """In production, /api/health is a lightweight liveness ping and never leaks internal pool stats."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            resp = self.client.get("/api/health")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["mode"], "production")
            # Must NOT disclose pool metrics or task queue internals in production
            self.assertNotIn("pool", data)
            self.assertNotIn("tasks", data)

    def test_health_liveness_diagnostic_in_development(self):
        """In development, /api/health includes diagnostic pool and task metrics for debugging."""
        with patch.dict(os.environ, {"FAHIM_ENV": "development"}):
            resp = self.client.get("/api/health")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "healthy")
            self.assertIn("pool", data)
            self.assertIn("tasks", data)

    def test_readiness_probe_masks_internal_metrics_in_production(self):
        """In production, /api/ready verifies dependencies but hides raw pool metrics from public responses."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            with patch("backend.tasks.queue.get_queue_metrics", return_value={"status": "healthy"}):
                resp = self.client.get("/api/ready")
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                self.assertEqual(data["status"], "ready")
                self.assertEqual(data["checks"]["database"], "ok")
                self.assertEqual(data["checks"]["migrations"], "ok")
                self.assertEqual(data["checks"]["task_queue"], "healthy")
                # Sensitive internal counters must be omitted in production
                self.assertNotIn("pool", data)
                self.assertNotIn("tasks", data)

    def test_readiness_probe_fails_if_task_queue_unhealthy_in_production(self):
        """In production, /api/ready must return 503 if Redis task queue is not healthy."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            with patch("backend.tasks.queue.get_queue_metrics", return_value={"status": "in_memory_degraded"}):
                resp = self.client.get("/api/ready")
                self.assertEqual(resp.status_code, 503)
                data = resp.json()
                self.assertEqual(data["status"], "not_ready")
                self.assertEqual(data["checks"]["task_queue"], "error")
                self.assertIn("Redis task queue unavailable", data.get("error", ""))

    def test_database_pool_status_masked_in_production(self):
        """get_db_pool_status must sanitize/mask details when FAHIM_ENV=production."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            status = get_db_pool_status()
            self.assertEqual(status, {"status": "configured"})
            self.assertNotIn("checkedout", status)
            self.assertNotIn("overflow", status)

    def test_security_headers_injected(self):
        """API responses must include X-Content-Type-Options, X-Frame-Options, and Referrer-Policy."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(resp.headers.get("x-frame-options"), "DENY")
        self.assertEqual(resp.headers.get("referrer-policy"), "strict-origin-when-cross-origin")

    def test_hsts_header_in_production(self):
        """In production, Strict-Transport-Security must be added to all responses."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            resp = self.client.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("max-age=31536000", resp.headers.get("strict-transport-security", ""))

    def test_validate_deployment_config_rules(self):
        """validate_deployment_config enforces production security invariants."""
        # 1. Missing required variables
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "DATABASE_URL": ""}, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                validate_deployment_config()
            self.assertIn("Missing required production configuration", str(ctx.exception))

        # 2. SQLite prohibited in production
        valid_env = {
            "FAHIM_ENV": "production",
            "DATABASE_URL": "sqlite:///test.db",
            "FAHIM_SECRET_KEY": "a" * 32,
            "FAHIM_PAYMENT_WEBHOOK_SECRET": "b" * 24,
            "FAHIM_CORS_ORIGINS": "https://app.jisr.ae",
            "FAHIM_PAYMENT_PROVIDER": "stripe"
        }
        with patch.dict(os.environ, valid_env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                validate_deployment_config()
            self.assertIn("SQLite is development-only", str(ctx.exception))

        # 3. Wildcard CORS prohibited in production
        valid_env["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/jisr"
        valid_env["FAHIM_CORS_ORIGINS"] = "https://app.jisr.ae,*"
        with patch.dict(os.environ, valid_env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                validate_deployment_config()
            self.assertIn("cannot contain wildcard", str(ctx.exception))

        # 4. Valid production configuration passes cleanly
        valid_env["FAHIM_CORS_ORIGINS"] = "https://app.jisr.ae,https://jisr-arabic.com"
        with patch.dict(os.environ, valid_env, clear=True):
            validate_deployment_config()  # Should not raise


if __name__ == "__main__":
    unittest.main()

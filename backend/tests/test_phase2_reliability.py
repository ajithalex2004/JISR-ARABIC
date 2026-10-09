"""
Phase 2 Reliability & Scale Hardening Test Suite.
Validates:
1. Proxy trust & real client IP resolution (spoof protection).
2. AI & Audio distributed rate limiting.
3. Task queue fail-closed behavior in production.
4. Readiness probe degradation on queue failure in production.
5. Redis SCAN instead of KEYS in task listing.
6. Payload limits & MIME validation on AI & audio endpoints.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.main import app, _extract_real_client_ip, _is_trusted_proxy
from backend.database import Base, get_db
from backend.tasks.queue import enqueue_task, list_recent_tasks, get_queue_metrics
from backend.errors import ApplicationError


class TestPhase2Reliability(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

        def override_db():
            db = self.Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_db
        self.client = TestClient(app)

    def tearDown(self):
        self.engine.dispose()
        app.dependency_overrides.pop(get_db, None)

    def test_proxy_trust_and_ip_spoof_protection(self):
        """Untrusted clients sending X-Forwarded-For must be ignored; trusted proxy IP must be honored."""
        # Untrusted client attempting to spoof IP
        mock_untrusted_request = MagicMock()
        mock_untrusted_request.client.host = "203.0.113.50"
        mock_untrusted_request.headers.get.return_value = "1.2.3.4, 5.6.7.8"

        real_ip = _extract_real_client_ip(mock_untrusted_request)
        # Must resolve to untrusted direct client host, NOT the spoofed header
        self.assertEqual(real_ip, "203.0.113.50")

        # Trusted proxy (e.g. 172.18.0.2 in Docker internal network or 127.0.0.1)
        mock_trusted_request = MagicMock()
        mock_trusted_request.client.host = "172.18.0.2"
        mock_trusted_request.headers.get.return_value = "198.51.100.99, 10.0.0.1"

        real_ip_trusted = _extract_real_client_ip(mock_trusted_request)
        self.assertEqual(real_ip_trusted, "198.51.100.99")

    def test_ai_endpoint_rate_limiting(self):
        """Excessive requests to AI endpoints must return HTTP 429 with retry headers."""
        with patch("backend.main.check_rate_limit", return_value=(False, 31, 45)):
            res = self.client.post("/api/ai/ask-fahim", json={"question": "ما الفاعل؟"})
            self.assertEqual(res.status_code, 429)
            self.assertEqual(res.headers.get("Retry-After"), "45")
            self.assertIn("Too many requests", res.json()["detail"])

    def test_task_queue_fails_closed_in_production(self):
        """In production, enqueue_task must fail closed (raise 503) if Redis is unavailable."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            with patch("backend.tasks.queue.get_redis_client", return_value=None):
                with self.assertRaises(ApplicationError) as ctx:
                    enqueue_task(task_type="test_task", params={"foo": "bar"})
                self.assertEqual(ctx.exception.status_code, 503)
                self.assertIn("unavailable in production", str(ctx.exception.detail))

    def test_task_queue_allows_in_memory_in_development(self):
        """In development, enqueue_task safely falls back to in-memory queue."""
        with patch.dict(os.environ, {"FAHIM_ENV": "development"}):
            with patch("backend.tasks.queue.get_redis_client", return_value=None):
                task = enqueue_task(task_type="dev_task", params={"foo": "bar"})
                self.assertIsNotNone(task)
                self.assertEqual(task.status, "pending")

    def test_readiness_probe_fails_when_queue_degraded_in_production(self):
        """In production, /api/ready must return 503 if Redis task queue is not healthy."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            with patch("backend.tasks.queue.get_redis_client", return_value=None):
                res = self.client.get("/api/ready")
                self.assertEqual(res.status_code, 503)
                data = res.json()
                self.assertEqual(data["status"], "not_ready")
                self.assertEqual(data["checks"]["task_queue"], "error")

    def test_list_recent_tasks_uses_scan_iter(self):
        """list_recent_tasks must use Redis SCAN instead of blocking KEYS command."""
        mock_redis = MagicMock()
        mock_redis.scan_iter.return_value = ["fahim:task:t1", "fahim:task:t2"]
        mock_redis.hgetall.side_effect = lambda k: {
            "id": k.split(":")[-1],
            "task_type": "ocr_textbook",
            "status": "completed",
            "progress": "100",
            "params": "{}",
            "created_at": "2026-10-08T12:00:00Z",
        }

        with patch("backend.tasks.queue.get_redis_client", return_value=mock_redis):
            tasks = list_recent_tasks(limit=10)
            mock_redis.scan_iter.assert_called_once()
            mock_redis.keys.assert_not_called()
            self.assertEqual(len(tasks), 2)

    def test_ai_payload_character_limits_enforced(self):
        """Requests with excessive length must be rejected with 422."""
        excessive_question = "أ" * 2001
        res = self.client.post("/api/ai/ask-fahim", json={"question": excessive_question})
        self.assertEqual(res.status_code, 422)

    def test_ai_attachment_type_validation(self):
        """Unsupported attachment types must be rejected with 400."""
        payload = {
            "question": "ما هذا؟",
            "attachment_base64": "SGVsbG8gV29ybGQ=",
            "attachment_type": "application/x-dosexec",
        }
        res = self.client.post("/api/ai/ask-fahim", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unsupported attachment type", res.json()["detail"])

    def test_audio_synthesize_text_limit(self):
        """Audio synthesis text exceeding 1000 characters must be rejected."""
        long_text = "كلمة " * 300  # > 1500 chars
        res = self.client.get(f"/api/audio/synthesize?text={long_text}")
        self.assertEqual(res.status_code, 422)

        res_async = self.client.post("/api/audio/synthesize-async", json={"text": long_text})
        self.assertEqual(res_async.status_code, 400)
        self.assertIn("exceeds maximum limit", res_async.json()["detail"])


if __name__ == "__main__":
    unittest.main()

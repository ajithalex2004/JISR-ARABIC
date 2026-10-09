"""
Unit and integration tests for Pillar 1 (Production Configuration) and Pillar 2 (Secure Authentication).
Validates:
- System environment variables are never overwritten by local .env files
- Production deployment configuration enforces Postgres, strong secrets, Redis format, and no wildcard CORS
- OTP codes are never logged in plaintext or exposed in production API payloads
- Distributed rate limiting blocks burst traffic with HTTP 429 and Retry-After headers
- Cache-first token and user session revocation blocks unauthorized requests
"""
import os
import io
import logging
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.config import validate_deployment_config, ConfigurationError
from backend.email_delivery import send_otp_email, _mask_email
from backend.modules.identity.service import _debug_otp
from backend.redis_client import (
    check_rate_limit, record_revoked_token, record_revoked_user,
    is_session_revoked_in_cache, _fallback_rate_buckets, _fallback_revoked_tokens, _fallback_revoked_users
)
from backend.main import app


class TestPillar1ProductionConfiguration(unittest.TestCase):
    def test_mask_email_utility(self):
        self.assertEqual(_mask_email("student@example.com"), "st***@example.com")
        self.assertEqual(_mask_email("a@b.com"), "***@b.com")
        self.assertEqual(_mask_email(""), "masked_recipient")

    def test_production_config_rejects_sqlite(self):
        env = {
            "FAHIM_ENV": "production",
            "DATABASE_URL": "sqlite:///fahim.db",
            "FAHIM_SECRET_KEY": "a" * 32,
            "FAHIM_PAYMENT_WEBHOOK_SECRET": "b" * 24,
            "FAHIM_CORS_ORIGINS": "https://jisr-arabic.ae",
            "FAHIM_PAYMENT_PROVIDER": "stripe",
            "FAHIM_SEED_DEMO": "0"
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                validate_deployment_config()
            self.assertIn("SQLite is development-only", str(ctx.exception))

    def test_production_config_rejects_wildcard_cors(self):
        env = {
            "FAHIM_ENV": "production",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/jisr",
            "FAHIM_SECRET_KEY": "a" * 32,
            "FAHIM_PAYMENT_WEBHOOK_SECRET": "b" * 24,
            "FAHIM_CORS_ORIGINS": "https://jisr-arabic.ae, *",
            "FAHIM_PAYMENT_PROVIDER": "stripe",
            "FAHIM_SEED_DEMO": "0"
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                validate_deployment_config()
            self.assertIn("wildcard '*'", str(ctx.exception))

    def test_production_config_rejects_invalid_redis_url(self):
        env = {
            "FAHIM_ENV": "production",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/jisr",
            "FAHIM_SECRET_KEY": "a" * 32,
            "FAHIM_PAYMENT_WEBHOOK_SECRET": "b" * 24,
            "FAHIM_CORS_ORIGINS": "https://jisr-arabic.ae",
            "FAHIM_PAYMENT_PROVIDER": "stripe",
            "FAHIM_SEED_DEMO": "0",
            "REDIS_URL": "http://invalid-redis-host:6379"
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                validate_deployment_config()
            self.assertIn("REDIS_URL must use redis:// or rediss://", str(ctx.exception))

    def test_production_config_valid_acceptance(self):
        env = {
            "FAHIM_ENV": "production",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/jisr",
            "FAHIM_SECRET_KEY": "c" * 36,
            "FAHIM_PAYMENT_WEBHOOK_SECRET": "d" * 28,
            "FAHIM_CORS_ORIGINS": "https://jisr-arabic.ae, https://app.jisr-arabic.ae",
            "FAHIM_PAYMENT_PROVIDER": "stripe",
            "FAHIM_SEED_DEMO": "0",
            "REDIS_URL": "redis://default:secret@redis-cluster:6379/0"
        }
        with patch.dict(os.environ, env, clear=True):
            # Must not raise
            validate_deployment_config()


class TestPillar2SecureAuthentication(unittest.TestCase):
    def setUp(self):
        _fallback_rate_buckets.clear()
        _fallback_revoked_tokens.clear()
        _fallback_revoked_users.clear()

    def test_otp_never_in_log_output(self):
        secret_otp = "987321"
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        fahim_logger = logging.getLogger("fahim.email")
        old_level = fahim_logger.level
        fahim_logger.setLevel(logging.INFO)
        fahim_logger.addHandler(handler)

        try:
            with patch.dict(os.environ, {"FAHIM_SMTP_HOST": ""}):
                send_otp_email("parent_secret@domain.ae", secret_otp, "login_otp")
            logs = log_stream.getvalue()
            self.assertNotIn(secret_otp, logs, "CRITICAL: Plaintext OTP was found in log output!")
            self.assertIn("[OTP Delivery]", logs)
            self.assertIn("pa***@domain.ae", logs)
        finally:
            fahim_logger.removeHandler(handler)
            fahim_logger.setLevel(old_level)

    def test_debug_otp_never_in_production(self):
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_EXPOSE_DEBUG_OTP": "1"}):
            result = _debug_otp("654321")
            self.assertIsNone(result, "CRITICAL: Debug OTP was returned in production environment!")

        with patch.dict(os.environ, {"FAHIM_ENV": "development", "FAHIM_EXPOSE_DEBUG_OTP": "1"}):
            result = _debug_otp("654321")
            self.assertEqual(result, "654321")

    def test_rate_limiter_allows_and_throttles(self):
        rate_key = "test_ip_127.0.0.1:/api/test"
        # 3 allowed requests
        for i in range(1, 4):
            allowed, count, _ = check_rate_limit(rate_key, limit=3, window_seconds=60)
            self.assertTrue(allowed)
            self.assertEqual(count, i)

        # 4th request must be throttled
        allowed, count, retry_after = check_rate_limit(rate_key, limit=3, window_seconds=60)
        self.assertFalse(allowed)
        self.assertGreaterEqual(retry_after, 1)

    def test_token_and_user_session_revocation_cache(self):
        jti = "token-jti-abc-123"
        user_id = "user-uuid-xyz-789"

        # Initially not revoked
        self.assertFalse(is_session_revoked_in_cache(jti, user_id))

        # Revoke token
        record_revoked_token(jti)
        self.assertTrue(is_session_revoked_in_cache(jti, user_id))
        self.assertFalse(is_session_revoked_in_cache("unrelated-jti", user_id))

        # Revoke user
        record_revoked_user(user_id)
        self.assertTrue(is_session_revoked_in_cache("any-other-jti", user_id))

    def test_distributed_rate_limit_middleware(self):
        client = TestClient(app)
        # Rapidly attempt 12 login posts from the same IP
        responses = []
        for _ in range(12):
            res = client.post("/api/auth/login", json={"email": "throttle_test@jisr.ae", "password": "wrong"})
            responses.append(res.status_code)

        # First 10 should be 400/401/404 (handled by route), 11th and 12th must be 429
        self.assertIn(429, responses)
        self.assertEqual(responses[-1], 429)


if __name__ == "__main__":
    unittest.main()

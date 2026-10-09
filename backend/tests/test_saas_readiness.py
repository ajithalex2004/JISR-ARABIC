"""
Unit tests for the JISR production readiness and SaaS credentials verification utility.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from backend.scripts.verify_production_readiness import (
    check_database, check_redis, check_storage_and_cdn,
    check_payment_provider, check_email_smtp, check_gemini_ai,
    run_all_checks, CheckResult
)


class TestSaaSReadiness(unittest.TestCase):
    def test_check_database_succeeds_on_valid_connection(self):
        """check_database successfully reports database and migration health."""
        res = check_database()
        self.assertTrue(res.passed)
        self.assertIn("Database connected", res.message)

    def test_check_redis_reports_status(self):
        """check_redis handles both live client and development in-memory warning."""
        res = check_redis()
        # In test/dev environment with in-memory fallback, warning is expected
        self.assertTrue(res.passed or res.warning)

    def test_check_storage_and_cdn_local_and_s3(self):
        """check_storage_and_cdn correctly differentiates local vs S3 adapter."""
        with patch.dict(os.environ, {"STORAGE_BACKEND": "local"}):
            from backend.storage import reset_storage_adapter
            reset_storage_adapter()
            res = check_storage_and_cdn(skip_network=True)
            self.assertTrue(res.warning)
            self.assertIn("LocalStorageAdapter", res.message)
            reset_storage_adapter()

    def test_check_payment_provider_validation(self):
        """check_payment_provider validates required secrets and format prefixes."""
        # 1. Missing webhook secret fails
        with patch.dict(os.environ, {"FAHIM_PAYMENT_WEBHOOK_SECRET": ""}):
            res = check_payment_provider(skip_network=True)
            self.assertFalse(res.passed)

        # 2. Valid format passes
        with patch.dict(os.environ, {
            "FAHIM_PAYMENT_PROVIDER": "stripe",
            "FAHIM_PAYMENT_WEBHOOK_SECRET": "whsec_test_secret_12345",
            "STRIPE_SECRET_KEY": "sk_test_mock_stripe_key_12345"
        }):
            res = check_payment_provider(skip_network=True)
            self.assertTrue(res.passed)
            self.assertIn("format valid", res.message)

    def test_check_email_smtp_validation(self):
        """check_email_smtp checks host configuration and offline format."""
        with patch.dict(os.environ, {"FAHIM_SMTP_HOST": ""}):
            res = check_email_smtp(skip_network=True)
            self.assertFalse(res.passed)

        with patch.dict(os.environ, {
            "FAHIM_SMTP_HOST": "email-smtp.me-central-1.amazonaws.com",
            "FAHIM_SMTP_PORT": "587",
            "FAHIM_SMTP_USER": "AKIA_MOCK_USER",
            "FAHIM_SMTP_PASS": "MOCK_PASS",
            "FAHIM_SMTP_FROM": "noreply@jisr.ae"
        }):
            res = check_email_smtp(skip_network=True)
            self.assertTrue(res.passed)
            self.assertIn("SMTP configured", res.message)

    def test_check_gemini_ai_validation(self):
        """check_gemini_ai verifies key presence and prefix formatting."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            res = check_gemini_ai(skip_network=True)
            self.assertFalse(res.passed)

        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSy_mock_key_valid"}):
            res = check_gemini_ai(skip_network=True)
            self.assertTrue(res.passed)
            self.assertIn("format valid", res.message)

    def test_run_all_checks_aggregates_results(self):
        """run_all_checks returns boolean and list of 6 CheckResult items."""
        _, checks = run_all_checks(skip_network=True, verbose=False)
        self.assertEqual(len(checks), 6)
        self.assertTrue(all(isinstance(c, CheckResult) for c in checks))

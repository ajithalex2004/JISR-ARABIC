import os
import unittest
import logging
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.models import Base, User, ChildProfile, TermAccess
from backend.database import get_db
from backend.security import hash_password
from backend.email_delivery import send_otp_email
from backend.schemas import LoginRequest, QuestionPaperSolveRequest
from backend.modules.identity.service import login
from backend.config import validate_deployment_config, ConfigurationError


class TestPhase0SecurityHardening(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Seed an admin user with a known proper bcrypt hash
        self.admin_email = "alex@exlsolutions.ae"
        self.proper_admin_password = "CorrectAdminPassword2026!"
        self.admin = User(
            id="admin_uuid_1",
            email=self.admin_email,
            full_name="Alex Administrator",
            role="admin",
            password_hash=hash_password(self.proper_admin_password),
            is_verified=True,
        )
        self.db.add(self.admin)
        self.db.commit()

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

    def test_admin_bypass_password_strictly_rejected(self):
        """Verifies that the old backdoor password 'exlsolutions@2026' is rejected."""
        req = LoginRequest(email=self.admin_email, password="exlsolutions@2026")
        from backend.errors import ApplicationError

        with self.assertRaises(ApplicationError) as ctx:
            login(req, db=self.db)
        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(ctx.exception.detail, "Incorrect email or password.")

    def test_admin_login_succeeds_with_valid_bcrypt_password(self):
        """Verifies that legitimate bcrypt verification functions for admins."""
        req = LoginRequest(email=self.admin_email, password=self.proper_admin_password)
        auth_resp = login(req, db=self.db)
        self.assertIsNotNone(auth_resp.access_token)
        self.assertEqual(auth_resp.user.email, self.admin_email)
        self.assertEqual(auth_resp.user.role, "admin")

    def test_admin_supervisor_cannot_bypass_ai_paywall(self):
        """Verify that passing child_id='admin_supervisor' no longer bypasses the paywall anonymously."""
        payload = {
            "child_id": "admin_supervisor",
            "paper_title": "UAE Exam 2026",
            "grade": 5,
            "raw_text": "سؤال عن النحو",
        }
        res = self.client.post("/api/ai/solve-question-paper", json=payload)
        # Must be rejected because caller is not authenticated as admin, and no unlocked term exists
        self.assertEqual(res.status_code, 402)
        self.assertIn("requires an active unlocked term pass or Admin access", res.json()["detail"])

    def test_otp_never_leaked_in_logs_and_fails_closed_in_production(self):
        """Ensure OTP codes never enter logger records, and fail closed when SMTP is unconfigured in production."""
        test_code = "849201"
        test_email = "parent@example.ae"

        with self.assertLogs("fahim.email", level=logging.INFO) as captured:
            with patch.dict(os.environ, {"FAHIM_ENV": "development", "FAHIM_SMTP_HOST": ""}):
                success_dev = send_otp_email(test_email, test_code, "login_otp")
                self.assertTrue(success_dev)

        # Confirm code was never in logs
        full_logs = "\n".join(captured.output)
        self.assertNotIn(test_code, full_logs)
        self.assertIn("[OTP Delivery] Email not configured", full_logs)

        # In production without SMTP, it must fail closed (return False)
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_SMTP_HOST": ""}):
            success_prod = send_otp_email(test_email, test_code, "login_otp")
            self.assertFalse(success_prod)

    def test_otp_sent_through_resend_api_when_configured(self):
        """With RESEND_API_KEY set, OTPs go through the Resend HTTP API instead of SMTP."""
        from unittest.mock import MagicMock
        response = MagicMock()
        env = {"FAHIM_ENV": "production", "FAHIM_SMTP_HOST": "", "RESEND_API_KEY": "re_test_key",
               "FAHIM_SMTP_FROM": "JISR <noreply@jisr.ae>"}
        with patch.dict(os.environ, env), patch("requests.post", return_value=response) as post:
            self.assertTrue(send_otp_email("parent@example.ae", "123456", "login_otp"))
        url = post.call_args.args[0]
        self.assertEqual(url, "https://api.resend.com/emails")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer re_test_key")
        self.assertEqual(post.call_args.kwargs["json"]["to"], ["parent@example.ae"])
        self.assertIn("123456", post.call_args.kwargs["json"]["text"])

        response.raise_for_status.side_effect = RuntimeError("401 Unauthorized")
        with patch.dict(os.environ, env), patch("requests.post", return_value=response):
            self.assertFalse(send_otp_email("parent@example.ae", "123456", "login_otp"))

    def test_smtp_password_accepts_documented_and_legacy_names(self):
        from backend.email_delivery import _smtp_password
        with patch.dict(os.environ, {"FAHIM_SMTP_PASS": "documented", "FAHIM_SMTP_PASSWORD": ""}):
            self.assertEqual(_smtp_password(), "documented")
        with patch.dict(os.environ, {"FAHIM_SMTP_PASS": "", "FAHIM_SMTP_PASSWORD": "legacy"}):
            self.assertEqual(_smtp_password(), "legacy")

    def test_production_deployment_config_validation(self):
        """Verify that missing payment or secret parameters fails startup validation."""
        clean_env = {
            "FAHIM_ENV": "production",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/jisr",
            "FAHIM_SECRET_KEY": "a" * 48,
            "FAHIM_PAYMENT_WEBHOOK_SECRET": "w" * 32,
            "FAHIM_CORS_ORIGINS": "https://jisr.ae",
            "FAHIM_PAYMENT_PROVIDER": "stripe",
        }

        with patch.dict(os.environ, clean_env, clear=True):
            # Should succeed with all required parameters
            validate_deployment_config()

        # Missing payment provider must fail
        invalid_env = clean_env.copy()
        invalid_env["FAHIM_PAYMENT_PROVIDER"] = ""
        with patch.dict(os.environ, invalid_env, clear=True):
            with self.assertRaises(ConfigurationError):
                validate_deployment_config()

    def test_admin_routes_require_authentication(self):
        """Verify that previously unauthenticated admin routes are now strictly protected."""
        res_solve = self.client.post("/api/admin/solve-question", json={"question_ar": "ما معنى كلمة كتاب؟"})
        self.assertEqual(res_solve.status_code, 401)

        res_library = self.client.get("/api/admin/textbook-library")
        self.assertEqual(res_library.status_code, 401)

        res_pages = self.client.get("/api/admin/textbook-pages/edition_1")
        self.assertEqual(res_pages.status_code, 401)

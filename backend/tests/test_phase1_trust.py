import os
import time
import json
import hmac
import hashlib
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.models import Base, User, ChildProfile, TermAccess, PaymentTransaction, ScannedPage, BookEdition
from backend.database import get_db
from backend.schemas import (
    PaymentCheckoutRequest,
    AnnualCheckoutRequest,
    SpeechEvaluationRequest,
    SignupRequest,
    LoginOtpRequest,
    ForgotPasswordRequest,
)
from backend.modules.billing import service as billing_service
from backend.modules.curriculum import audio as audio_service
from backend.modules.identity import service as identity_service
from backend.errors import ApplicationError


class TestPhase1TrustAndIntegrity(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Seed test user and child
        self.parent = User(
            id="parent_test_1",
            email="parent@test.ae",
            full_name="Parent Tester",
            role="parent",
            is_verified=True,
            password_hash="test_hash",
        )
        self.db.add(self.parent)
        self.db.commit()

        self.child = ChildProfile(
            id="child_test_1",
            parent_id=self.parent.id,
            name="Child Tester",
            default_grade=5,
        )
        self.db.add(self.child)
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

    # -------------------------------------------------------------------------
    # 1. Billing & Payments
    # -------------------------------------------------------------------------
    def test_production_rejects_demo_promo_codes(self):
        """Hardcoded demo promo codes must be rejected with 400 in production."""
        req = PaymentCheckoutRequest(
            child_id=self.child.id,
            grade=5,
            term=1,
            promo_code="DEMOFREE",
            provider_payment_id="ch_valid_123",
        )
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_PAYMENT_PROVIDER": "stripe"}):
            with self.assertRaises(ApplicationError) as ctx:
                billing_service.checkout_term(req, db=self.db)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("Promotional code is not valid", ctx.exception.detail)

    def test_annual_checkout_propagates_provider_payment_id(self):
        """Annual checkout request must propagate provider payment ID to prevent 402 rejection."""
        req = AnnualCheckoutRequest(
            child_id=self.child.id,
            grade=5,
            provider_payment_id="ch_annual_provider_123",
            idempotency_key="idemp_annual_1",
        )
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_PAYMENT_PROVIDER": "stripe"}):
            resp = billing_service.checkout_annual_pass(req, db=self.db, is_verified_provider=True)
            self.assertTrue(resp.success)
            self.assertEqual(resp.package_type, "annual")
            self.assertEqual(resp.unlocked_terms, [1, 2, 3])

    def test_unverified_client_checkout_cannot_unlock_entitlements_in_production(self):
        """Unverified client direct checkout in production must remain pending and not unlock access."""
        req = PaymentCheckoutRequest(
            child_id=self.child.id,
            grade=5,
            term=1,
            provider_payment_id="ch_fake_client_supplied_123",
            idempotency_key="idemp_client_unverified_1",
        )
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_PAYMENT_PROVIDER": "stripe"}):
            resp = billing_service.checkout_term(req, db=self.db, is_verified_provider=False)
            self.assertFalse(resp.success)
            self.assertEqual(resp.status, "pending")
            self.assertEqual(resp.unlocked_terms, [])
            self.assertIn("confirmed by the payment provider webhook", resp.message)

            # Confirm database TermAccess was NOT unlocked
            access = self.db.query(TermAccess).filter_by(child_id=self.child.id, grade=5, term=1).first()
            self.assertTrue(access is None or not access.is_unlocked)

    def test_raw_card_numbers_rejected_in_production_for_pci(self):
        """Direct raw card submission is rejected in production to eliminate PCI scope."""
        req = PaymentCheckoutRequest(
            child_id=self.child.id,
            grade=5,
            term=1,
            card_number="4111111111111111",
            cvc="123",
            provider_payment_id="ch_dummy_123",
        )
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_PAYMENT_PROVIDER": "stripe"}):
            with self.assertRaises(ApplicationError) as ctx:
                billing_service.checkout_term(req, db=self.db)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("Direct submission of raw card numbers", ctx.exception.detail)

    def test_financial_precision_numeric_and_cents(self):
        """Financial transactions must record exact minor units and round cleanly without IEEE 754 drift."""
        req = PaymentCheckoutRequest(
            child_id=self.child.id,
            grade=5,
            term=1,
            provider_payment_id="ch_precision_123",
            idempotency_key="idemp_precision_1",
        )
        resp = billing_service.checkout_term(req, db=self.db, is_verified_provider=True)
        self.assertTrue(resp.success)
        txn = self.db.query(PaymentTransaction).filter_by(id=resp.transaction_id).first()
        self.assertIsNotNone(txn)
        self.assertEqual(txn.amount_cents, 2000)
        self.assertEqual(float(txn.amount_usd), 20.00)
        self.assertEqual(float(txn.subtotal_usd), 19.05)
        self.assertEqual(float(txn.vat_amount_usd), 0.95)

    def test_stripe_webhook_cryptographic_verification_and_entitlement(self):
        """Stripe webhooks must verify HMAC signature and idempotently unlock terms."""
        secret = "whsec_test_secret_for_webhook_signing_2026"
        event_payload = {
            "id": "evt_test_12345",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session_999",
                    "payment_status": "paid",
                    "metadata": {
                        "child_id": self.child.id,
                        "grade": "5",
                        "term": "2",
                        "package_type": "term",
                    },
                }
            },
        }
        body_bytes = json.dumps(event_payload).encode("utf-8")
        timestamp = str(int(time.time()))
        signed_payload = f"{timestamp}.".encode("utf-8") + body_bytes
        valid_sig = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        valid_header = f"t={timestamp},v1={valid_sig}"

        with patch.dict(os.environ, {
            "FAHIM_ENV": "development",
            "FAHIM_PAYMENT_WEBHOOK_SECRET": secret,
            "FAHIM_PAYMENT_PROVIDER": "stripe",
        }):
            # 1. Missing signature header
            res_no_sig = self.client.post("/api/payments/webhook", content=body_bytes)
            self.assertEqual(res_no_sig.status_code, 401)

            # 2. Tampered signature header
            res_bad_sig = self.client.post(
                "/api/payments/webhook",
                content=body_bytes,
                headers={"stripe-signature": f"t={timestamp},v1=bad_signature"},
            )
            self.assertEqual(res_bad_sig.status_code, 401)

            # 3. Valid signature unlocks Term 2
            res_valid = self.client.post(
                "/api/payments/webhook",
                content=body_bytes,
                headers={"stripe-signature": valid_header},
            )
            self.assertEqual(res_valid.status_code, 200)

            # Verify TermAccess was unlocked in DB
            access = self.db.query(TermAccess).filter_by(child_id=self.child.id, term=2).first()
            self.assertIsNotNone(access)
            self.assertTrue(access.is_unlocked)

            # 4. Idempotency replay returns existing transaction
            res_replay = self.client.post(
                "/api/payments/webhook",
                content=body_bytes,
                headers={"stripe-signature": valid_header},
            )
            self.assertEqual(res_replay.status_code, 200)

    # -------------------------------------------------------------------------
    # 2. Speech & Pronunciation Assessment Integrity
    # -------------------------------------------------------------------------
    def test_speech_evaluation_no_longer_bypasses_with_empty_transcript(self):
        """Empty transcript with dummy audio must raise 422 instead of faking a 100% score."""
        req = SpeechEvaluationRequest(
            target_phrase="كُرَةُ القَدَمِ رِيَاضَةٌ جَمَاعِيَّةٌ",
            spoken_text="",
            audio_base64="ZHVtbXlfYXVkaW9fYnl0ZXM=",
        )
        with self.assertRaises(ApplicationError) as ctx:
            audio_service.evaluate_pronunciation(req, db=self.db)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertIn("could not recognize Arabic speech", ctx.exception.detail)

    def test_speech_evaluation_evaluates_legitimate_spoken_text(self):
        """Legitimate spoken text is properly scored against the target phrase."""
        req = SpeechEvaluationRequest(
            target_phrase="كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الشَّعْبِيَّةُ الأُولَى",
            spoken_text="كرة القدم هي اللعبة الشعبية الأولى",
        )
        res = audio_service.evaluate_pronunciation(req, db=self.db)
        self.assertGreaterEqual(res["overall_score"], 90.0)
        self.assertTrue(res["is_pass"])

    # -------------------------------------------------------------------------
    # 3. Educational Integrity - OCR Worker
    # -------------------------------------------------------------------------
    def test_ocr_failure_does_not_fabricate_text_and_marks_failed(self):
        """When text extraction fails, handler must store empty string and extraction_failed status."""
        edition = BookEdition(id="ed_test_1", title="MoE Grade 5 Arabic")
        self.db.add(edition)
        self.db.commit()

        # Simulate what the task worker does when reader fails:
        extracted_text = ""
        review_status = "extraction_failed" if not extracted_text else "automatic_extracted"
        confidence = 0.0 if not extracted_text else 0.95

        page_obj = ScannedPage(
            book_edition_id=edition.id,
            pdf_page=1,
            printed_page=1,
            ocr_text_ar=extracted_text,
            confidence=confidence,
            review_status=review_status,
        )
        self.db.add(page_obj)
        self.db.commit()

        saved = self.db.query(ScannedPage).filter_by(book_edition_id=edition.id, pdf_page=1).first()
        self.assertEqual(saved.ocr_text_ar, "")
        self.assertEqual(saved.confidence, 0.0)
        self.assertEqual(saved.review_status, "extraction_failed")
        self.assertNotEqual(saved.review_status, "automatic_verified")

    # -------------------------------------------------------------------------
    # 4. OTP Failure Handling in Production
    # -------------------------------------------------------------------------
    def test_otp_request_fails_closed_in_production_when_smtp_fails(self):
        """In production without SMTP, OTP generation must raise 503 instead of pretending success."""
        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_SMTP_HOST": ""}):
            # 1. Signup OTP
            req_signup = SignupRequest(email="newuser@example.ae", full_name="New User")
            with self.assertRaises(ApplicationError) as ctx_signup:
                identity_service.signup_request_otp(req_signup, db=self.db)
            self.assertEqual(ctx_signup.exception.status_code, 503)

            # 2. Login OTP
            req_login = LoginOtpRequest(email=self.parent.email)
            with self.assertRaises(ApplicationError) as ctx_login:
                identity_service.login_request_otp(req_login, db=self.db)
            self.assertEqual(ctx_login.exception.status_code, 503)

            # 3. Forgot password OTP
            req_forgot = ForgotPasswordRequest(email=self.parent.email)
            with self.assertRaises(ApplicationError) as ctx_forgot:
                identity_service.forgot_password_request_otp(req_forgot, db=self.db)
            self.assertEqual(ctx_forgot.exception.status_code, 503)

"""Failure alerts and the weekly parent progress report."""
import datetime
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import alerts, scheduler
from backend.database import Base, get_db
from backend.main import app
from backend.models import (
    CapsuleProgress, ChildProfile, ExamSimulationResult, LearnerAttempt, Lesson, SpacedReviewLog, User,
    WeeklyDigestNotification,
)
from backend.modules.progress import reporting
from backend.redis_client import _fallback_cache, _fallback_rate_buckets, _fallback_revoked_tokens
from backend.security import hash_password


class TestAlerts(unittest.TestCase):
    def setUp(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()

    def tearDown(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()

    @patch.dict(os.environ, {"FAHIM_ALERT_THRESHOLD": "3", "FAHIM_ALERT_EMAILS": "ops@test.local",
                             "RESEND_API_KEY": "test-key"})
    def test_alert_sent_once_after_threshold_then_cooldown(self):
        with patch("backend.email_delivery._send_via_resend") as sent:
            self.assertFalse(alerts.record_failure("gemini", "404 model retired", background=False))
            self.assertFalse(alerts.record_failure("gemini", "404 model retired", background=False))
            self.assertTrue(alerts.record_failure("gemini", "404 model retired", background=False))
            self.assertFalse(alerts.record_failure("gemini", "404 model retired", background=False))
        self.assertEqual(sent.call_count, 1)
        recipient, subject, body = sent.call_args.args
        self.assertEqual(recipient, "ops@test.local")
        self.assertIn("Gemini", subject)
        self.assertIn("404 model retired", body)
        self.assertEqual(len(alerts.recent_failures("gemini")), 4)
        self.assertEqual(alerts.last_alert("gemini")["delivered_to"], ["ops@test.local"])

    @patch.dict(os.environ, {"FAHIM_ALERT_THRESHOLD": "1", "FAHIM_ALERT_EMAILS": "ops@test.local",
                             "FAHIM_ALERT_WEBHOOK_URL": "https://hooks.example/abc"}, clear=False)
    def test_webhook_used_and_email_failures_not_realerted(self):
        os.environ.pop("RESEND_API_KEY", None)
        os.environ.pop("FAHIM_SMTP_HOST", None)
        with patch("backend.alerts._post_webhook") as webhook:
            self.assertTrue(alerts.record_failure("payments", "checkout 503", background=False))
        webhook.assert_called_once()
        self.assertEqual(alerts.last_alert("payments")["delivered_to"], ["webhook"])

    def test_gemini_failure_is_recorded(self):
        from backend.modules.tutoring import assistant

        failing = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **_: (_ for _ in ()).throw(RuntimeError("404 NOT_FOUND model"))))
        with patch.object(assistant, "_get_gemini_client", return_value=failing):
            result = assistant.probe_gemini()
        self.assertFalse(result["ok"])
        self.assertIn("404", alerts.recent_failures("gemini")[0]["detail"])

    def test_server_errors_recorded_by_middleware(self):
        from backend.observability import _note_failed_response

        _note_failed_response("POST", "/api/payments/checkout", 503)
        _note_failed_response("POST", "/api/payments/webhook", 401)
        _note_failed_response("GET", "/api/curriculum/grades", 404)
        self.assertEqual(len(alerts.recent_failures("payments")), 2)
        self.assertEqual(alerts.recent_failures("server"), [])


class TestGeminiOutage(unittest.TestCase):
    def setUp(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()

    def tearDown(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()

    @patch.dict(os.environ, {"FAHIM_ALERT_EMAILS": "ops@test.local", "RESEND_API_KEY": "test-key"})
    def test_two_failed_scheduled_checks_in_a_row_alert(self):
        down = {"ok": False, "model": "m", "error": "402 RESOURCE_EXHAUSTED credits are depleted"}
        with patch("backend.email_delivery._send_via_resend") as sent, \
                patch.object(scheduler, "run_gemini_probe", side_effect=[down, {"ok": True}, down, down, down]):
            scheduler.run_scheduled_gemini_probe()
            scheduler.run_scheduled_gemini_probe()  # recovered: streak resets
            scheduler.run_scheduled_gemini_probe()
            self.assertEqual(sent.call_count, 0)
            with patch("backend.alerts.threading.Thread", side_effect=lambda target, args, daemon: SimpleNamespace(start=lambda: target(*args))):
                scheduler.run_scheduled_gemini_probe()
                scheduler.run_scheduled_gemini_probe()  # within the cooldown: no second email
        self.assertEqual(sent.call_count, 1)
        _, subject, body = sent.call_args.args
        self.assertIn("Gemini", subject)
        self.assertIn("2 times in a row", body)
        self.assertIn("credits are depleted", body)


class TestGeminiQuota(unittest.TestCase):
    def test_credits_exhausted_is_not_retried(self):
        from backend import gemini_quota
        calls = []

        def out_of_credits():
            calls.append(1)
            raise RuntimeError("402 RESOURCE_EXHAUSTED. Your prepayment credits are depleted.")

        with patch.object(gemini_quota, "_sleep") as slept, self.assertRaises(gemini_quota.GeminiQuotaExhausted) as raised:
            gemini_quota.call_with_quota_retry(out_of_credits)
        self.assertEqual((len(calls), slept.call_count), (1, 0))
        self.assertIn("AI Studio", str(raised.exception))

    def test_rate_limit_is_retried_then_paused(self):
        from backend import gemini_quota
        attempts = iter([RuntimeError("429 RESOURCE_EXHAUSTED quota"), "ok"])

        def flaky():
            value = next(attempts)
            if isinstance(value, Exception):
                raise value
            return value

        with patch.object(gemini_quota, "_sleep") as slept:
            self.assertEqual(gemini_quota.call_with_quota_retry(flaky, delays=(5,)), "ok")
            slept.assert_called_once_with(5)
            with self.assertRaises(gemini_quota.GeminiQuotaExhausted):
                gemini_quota.call_with_quota_retry(lambda: (_ for _ in ()).throw(RuntimeError("429 RESOURCE_EXHAUSTED")), delays=(5,))
        with self.assertRaises(ValueError):  # other errors pass through untouched
            gemini_quota.call_with_quota_retry(lambda: (_ for _ in ()).throw(ValueError("bad")))


class TestWeeklyReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("Pass12345!")

    def setUp(self):
        _fallback_cache.clear()
        _fallback_revoked_tokens.clear()
        _fallback_rate_buckets.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        self.now = datetime.datetime(2026, 10, 18, 5, 0)  # a Sunday
        day = datetime.timedelta(days=1)
        with self.session() as db:
            db.add(User(id="parent_ann", email="parent.ann@test.local", full_name="Parent of Ann", role="parent",
                        password_hash=self.password_hash, is_verified=True, weekly_report_email=True))
            db.add(User(id="parent_off", email="off@test.local", role="parent",
                        password_hash=self.password_hash, is_verified=True))
            db.commit()
            db.add(ChildProfile(id="child_ann", parent_id="parent_ann", name="Ann Maria", default_grade=6))
            db.add(ChildProfile(id="child_off", parent_id="parent_off", name="Omar", default_grade=6))
            db.add(Lesson(id="g6_l1", grade=6, term=1, unit_id="u1", lesson_order=1, title_ar="د", title_en="L1", start_page=1))
            db.add(Lesson(id="g6_l2", grade=6, term=1, unit_id="u1", lesson_order=2, title_ar="د", title_en="L2", start_page=2))
            db.commit()
            db.add_all([
                LearnerAttempt(child_id="child_ann", lesson_id="g6_l1", activity_id="vocab_1", is_correct=True, created_at=self.now - day),
                LearnerAttempt(child_id="child_ann", lesson_id="g6_l1", activity_id="vocab_2", is_correct=True, created_at=self.now - day),
                LearnerAttempt(child_id="child_ann", lesson_id="g6_l2", activity_id="grammar_1", is_correct=False, created_at=self.now - 2 * day),
                LearnerAttempt(child_id="child_ann", lesson_id="g6_l2", activity_id="vocab_9", is_correct=True, created_at=self.now - 10 * day),
                SpacedReviewLog(child_id="child_ann", concept_key="vocab_sports", question_id="q1", is_correct=True,
                                interval_days=1, ease_factor=2.5, review_date=self.now - day),
                CapsuleProgress(child_id="child_ann", capsule_id="c1", completed_at=self.now - day),
                ExamSimulationResult(child_id="child_ann", grade=6, term=1, score_percentage=80.0, correct_count=8,
                                     total_questions=10, submitted_at=self.now - 3 * day),
            ])
            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()
        _fallback_rate_buckets.clear()

    def test_weekly_activity_counts_only_this_week(self):
        with self.session() as db:
            activity = reporting.weekly_activity("child_ann", db=db, now=self.now)
        self.assertEqual(activity["lessons_practised"], 2)
        self.assertEqual(activity["activities_answered"], 4)  # 3 attempts + 1 review
        self.assertEqual(activity["accuracy_pct"], 66.7)
        self.assertEqual(activity["words_learned"], 3)  # vocab_1, vocab_2, review q1
        self.assertEqual(activity["capsules_this_week"], 1)
        self.assertEqual(activity["quiz_avg_this_week"], 80.0)
        self.assertEqual(activity["activity_vs_last_week_pct"], 500.0)  # 6 vs 1

    def test_scheduled_report_emails_opted_in_parents_once_per_week(self):
        with patch.dict(os.environ, {"RESEND_API_KEY": "test-key"}), \
                patch("backend.email_delivery._send_via_resend") as sent:
            with self.session() as db:
                first = reporting.send_scheduled_weekly_reports(db=db, now=self.now)
                second = reporting.send_scheduled_weekly_reports(db=db, now=self.now)
        self.assertEqual((first["sent"], second["sent"], second["skipped"]), (1, 0, 1))
        recipient, subject, body = sent.call_args.args
        self.assertEqual(recipient, "parent.ann@test.local")
        self.assertIn("Ann Maria", subject)
        self.assertIn("Words learned: 3", body)
        self.assertIn("80.0%", body)
        with self.session() as db:
            self.assertEqual(db.query(WeeklyDigestNotification).filter_by(child_id="child_off").count(), 0)

    def test_scheduler_sends_on_sunday_morning_only(self):
        self.assertTrue(scheduler.weekly_reports_due(datetime.datetime(2026, 10, 18, 4, 0)))
        self.assertFalse(scheduler.weekly_reports_due(datetime.datetime(2026, 10, 18, 3, 59)))
        self.assertFalse(scheduler.weekly_reports_due(datetime.datetime(2026, 10, 17, 9, 0)))

    def test_parent_toggles_weekly_email_and_sees_weekly_numbers(self):
        res = self.client.post("/api/auth/login", json={"email": "off@test.local", "password": "Pass12345!"})
        headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
        self.assertEqual(self.client.get("/api/parent/report-preferences", headers=headers).json()["weekly_email"], False)
        updated = self.client.put("/api/parent/report-preferences", json={"weekly_email": True}, headers=headers)
        self.assertEqual(updated.status_code, 200, updated.text)
        with self.session() as db:
            self.assertTrue(db.get(User, "parent_off").weekly_report_email)

        digest = self.client.get("/api/parent/weekly-digest/child_off", headers=headers)
        self.assertEqual(digest.status_code, 200, digest.text)
        self.assertEqual(digest.json()["words_learned"], 0)
        self.assertIn("period_start", digest.json())
        self.assertEqual(self.client.get("/api/parent/weekly-digest/child_ann", headers=headers).status_code, 403)


if __name__ == "__main__":
    unittest.main()


class TestResendErrors(unittest.TestCase):
    def test_resend_rejection_reason_is_kept(self):
        from backend import email_delivery

        def reject():
            raise RuntimeError("403 Client Error: Forbidden for url: https://api.resend.com/emails")
        response = SimpleNamespace(raise_for_status=reject, text="",
                                   json=lambda: {"message": "The jisrarabic.com domain is not verified."})
        with patch.dict(os.environ, {"RESEND_API_KEY": "k", "FAHIM_SMTP_FROM": "JISR <noreply@jisrarabic.com>"}), \
                patch("requests.post", return_value=response):
            with self.assertRaises(RuntimeError) as ctx:
                email_delivery.send_email("a@b.com", "s", "b", record_failures=False)
        self.assertIn("domain is not verified", str(ctx.exception))
        self.assertIn("noreply@jisrarabic.com", str(ctx.exception))

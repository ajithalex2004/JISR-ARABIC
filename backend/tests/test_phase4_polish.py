"""
Phase 4 Assessment & Mobile Polish Test Suite.
Validates:
1. Adaptive assessment calibration based on learner mastery, knowledge gaps, and mistakes.
2. Targeted remediation item prioritization and scaffolded hints for foundation tier learners.
3. Curriculum quality gate blocking approval/publication when quality checks fail.
4. Dual-control governance in production preventing self-approval by lesson creator.
5. Curriculum audit event persistence across rollback, approval, and publication.
6. Notification delivery tracking (delivery_status and error_message) for weekly digests.
"""
import os
import json
import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db
from backend.models import (
    User, ChildProfile, Lesson, LessonVersion,
    LearnerMistake, LearnerAttempt, ConceptMastery,
    CurriculumAuditEvent, WeeklyDigestNotification
)
from backend.modules.assessment.exams import get_adaptive_assessment
from backend.modules.curriculum.authoring import (
    approve_lesson_version, publish_lesson_version, rollback_lesson
)
from backend.modules.progress.reporting import send_weekly_digest
from backend.schemas import SendWeeklyDigestRequest
from backend.modules.identity.access import Principal
from backend.errors import ApplicationError


class TestPhase4Polish(unittest.TestCase):
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

    def tearDown(self):
        self.db.close()
        self.engine.dispose()
        app.dependency_overrides.pop(get_db, None)

    def test_adaptive_assessment_baseline_uncalibrated(self):
        """When child_id is not supplied, adaptive engine returns baseline flow without crashing."""
        res = get_adaptive_assessment(
            lesson_id="lesson_01_ball_games",
            child_id=None,
            db=self.db
        )
        self.assertTrue(res["success"])
        self.assertGreater(len(res["adaptive_questions"]), 0)
        self.assertEqual(res["adaptive_telemetry"]["calibrated_tier"], "standard")

    def test_adaptive_assessment_foundation_tier_and_scaffolding(self):
        """Struggling learner with mistakes receives foundation calibration and scaffolded hints."""
        parent = User(id="p_01", email="parent_struggling@test.ae", role="parent", password_hash="hash")
        child = ChildProfile(
            id="child_struggling_01",
            parent_id="p_01",
            name="Omar",
            default_grade=5,
            diagnostic_level="beginner"
        )
        self.db.add_all([parent, child])
        self.db.commit()

        # Add active unresolved mistakes and low score attempts
        mistake = LearnerMistake(
            child_id=child.id,
            lesson_id="lesson_01_ball_games",
            activity_id="act_01",
            concept_name="كرة القدم",
            wrong_answer="خطأ في الإجابة",
            correct_answer="كرة القدم",
            is_resolved=False
        )
        gap = ConceptMastery(
            child_id=child.id,
            concept_key="sports_vocab",
            concept_name_ar="ألعاب الكرة",
            concept_name_en="Ball games",
            category="vocabulary",
            mastery_percentage=35.0,
            is_gap=True
        )
        attempt = LearnerAttempt(
            id="att_low_01",
            child_id=child.id,
            lesson_id="lesson_01_ball_games",
            activity_id="act_01",
            is_correct=False,
            score=0.0
        )
        self.db.add_all([mistake, gap, attempt])
        self.db.commit()

        actor = Principal(id=parent.id, email=parent.email, role="parent", is_verified=True)
        res = get_adaptive_assessment(
            lesson_id="lesson_01_ball_games",
            child_id=child.id,
            db=self.db,
            actor=actor
        )
        telemetry = res["adaptive_telemetry"]
        self.assertEqual(telemetry["calibrated_tier"], "foundation")
        self.assertTrue(telemetry["hints_scaffolded"])
        self.assertGreater(telemetry["targeted_gaps_count"], 0)

        # Verify scaffolded hints are present on questions
        questions = res["adaptive_questions"]
        for q in questions:
            self.assertIsNotNone(q.get("hint_ar"))

    def test_adaptive_assessment_mastery_tier_acceleration(self):
        """Advanced learner with 100% accuracy and 0 mistakes receives mastery tier flow."""
        parent = User(id="p_02", email="parent_adv@test.ae", role="parent", password_hash="hash")
        child = ChildProfile(
            id="child_advanced_01",
            parent_id="p_02",
            name="Fatima",
            default_grade=5,
            diagnostic_level="advanced"
        )
        self.db.add_all([parent, child])
        self.db.commit()

        attempts = [
            LearnerAttempt(id=f"att_high_{i}", child_id=child.id, lesson_id="lesson_01_ball_games",
                           activity_id=f"act_{i}", is_correct=True, score=1.0)
            for i in range(5)
        ]
        self.db.add_all(attempts)
        self.db.commit()

        actor = Principal(id=parent.id, email=parent.email, role="parent", is_verified=True)
        res = get_adaptive_assessment(
            lesson_id="lesson_01_ball_games",
            child_id=child.id,
            db=self.db,
            actor=actor
        )
        self.assertEqual(res["adaptive_telemetry"]["calibrated_tier"], "mastery")
        self.assertFalse(res["adaptive_telemetry"]["hints_scaffolded"])

    def test_curriculum_quality_gate_blocks_approval_of_defective_lesson(self):
        """Lesson version with quality defects (e.g. missing Arabic content) must be blocked from approval."""
        lesson = Lesson(
            id="lesson_defective_01",
            unit_id="unit_1",
            grade=5,
            term=1,
            lesson_order=5,
            title_ar="درس معيب",
            title_en="Defective Lesson",
            start_page=10
        )
        # Content JSON missing Arabic fields
        defective_ver = LessonVersion(
            id="ver_defective_01",
            lesson_id=lesson.id,
            version_tag="1.0.0",
            content_json=json.dumps({"id": "act_defective", "content_en": "Only English content without Arabic"}),
            content_hash="hash_defective_123",
            status="content_pending",
            is_active=False
        )
        self.db.add_all([lesson, defective_ver])
        self.db.commit()

        # Approval must fail quality gate check
        with self.assertRaises(ApplicationError) as ctx:
            approve_lesson_version(lesson.id, defective_ver.id, db=self.db)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertIn("Quality gate failed", ctx.exception.detail)

    def test_dual_control_in_production_prevents_self_approval(self):
        """In production, creator cannot approve their own imported lesson version."""
        admin_creator = MagicMock()
        admin_creator.id = "admin_user_01"

        lesson = Lesson(
            id="lesson_valid_01",
            unit_id="unit_1",
            grade=5,
            term=1,
            lesson_order=1,
            title_ar="درس صالح",
            title_en="Valid Lesson",
            start_page=1
        )
        valid_ver = LessonVersion(
            id="ver_valid_01",
            lesson_id=lesson.id,
            version_tag="1.0.0",
            content_json=json.dumps({
                "lesson_id": lesson.id,
                "title_ar": "درس تجريبي",
                "title_en": "Test Lesson",
                "description_ar": "شرح الدرس باللغة العربية المقررة",
                "description_en": "Lesson description in English"
            }),
            content_hash="hash_valid_123",
            status="content_pending",
            created_by="admin_user_01",
            is_active=False
        )
        self.db.add_all([lesson, valid_ver])
        self.db.commit()

        # In production mode, same admin cannot approve
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            with self.assertRaises(ApplicationError) as ctx:
                approve_lesson_version(lesson.id, valid_ver.id, db=self.db, actor=admin_creator)
            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("Dual control required", ctx.exception.detail)

    def test_curriculum_audit_event_logged_on_rollback(self):
        """Rollback of lesson version must persist a CurriculumAuditEvent."""
        lesson = Lesson(
            id="lesson_rollback_01",
            unit_id="unit_1",
            grade=5,
            term=1,
            lesson_order=1,
            title_ar="درس صالح للمراجعة",
            title_en="Valid Lesson for Rollback",
            start_page=1
        )
        v1 = LessonVersion(
            id="ver_rb_01",
            lesson_id=lesson.id,
            version_tag="1.0.0",
            content_json="{}",
            content_hash="hash_rb_1",
            status="approved",
            is_active=False
        )
        v2 = LessonVersion(
            id="ver_rb_02",
            lesson_id=lesson.id,
            version_tag="2.0.0",
            content_json="{}",
            content_hash="hash_rb_2",
            status="published",
            is_active=True
        )
        self.db.add_all([lesson, v1, v2])
        self.db.commit()

        actor = MagicMock()
        actor.id = "supervisor_admin_99"

        res = rollback_lesson(lesson.id, v1.id, db=self.db, actor=actor)
        self.assertTrue(res["success"])

        # Check CurriculumAuditEvent row created
        audit = self.db.query(CurriculumAuditEvent).filter(
            CurriculumAuditEvent.lesson_id == lesson.id,
            CurriculumAuditEvent.action == "rollback"
        ).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.actor_id, "supervisor_admin_99")
        self.assertEqual(audit.version_tag, "1.0.0")

    def test_weekly_digest_tracks_delivery_status_and_errors(self):
        """WeeklyDigestNotification must track delivery_status and error_message when SMTP delivery fails."""
        parent = User(id="p_notif_01", email="parent_fail@test.ae", role="parent", password_hash="hash")
        child = ChildProfile(id="child_notif_01", parent_id="p_notif_01", name="Mansoor", default_grade=5)
        self.db.add_all([parent, child])
        self.db.commit()

        req = SendWeeklyDigestRequest(channel="email", recipient_email="parent_fail@test.ae")

        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_SMTP_HOST": ""}):
            with self.assertRaises(ApplicationError):
                send_weekly_digest(child.id, req, db=self.db)

        # Check notification record was saved with failed status
        notif = self.db.query(WeeklyDigestNotification).filter(
            WeeklyDigestNotification.child_id == child.id
        ).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.delivery_status, "failed")
        self.assertIn("SMTP", notif.error_message)


if __name__ == "__main__":
    unittest.main()

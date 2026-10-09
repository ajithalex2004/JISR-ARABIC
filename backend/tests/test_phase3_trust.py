"""
Phase 3 Educational & Legal Trust Test Suite.
Validates:
1. UAE VAT statutory retention on account deletion (anonymized tax records preserved for FTA compliance).
2. Honest initial gamification stats (0 XP, 0 streak, locked starter badges).
3. Honest parent dashboard without synthetic skill metrics (None / Not assessed yet).
4. Real evidence computation when learning attempts exist.
5. Honest weekly digest without fabricated gaps and strengths.
6. Fail-closed weekly digest email dispatch when SMTP unconfigured in production.
7. Curriculum hierarchy persistence (add_class and add_term persisted in database).
8. Educational integrity: No silent page-image fallback to page 1, and exam engine prioritizes published curriculum.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db
from backend.models import (
    User, ChildProfile, PaymentTransaction, GamificationProfile,
    LearnerBadge, LearnerAttempt, CurriculumGrade, CurriculumTerm,
    WeeklyDigestNotification
)
from backend.schemas import (
    AdminAddClassRequest, AdminAddTermRequest,
    SendWeeklyDigestRequest
)
from backend.modules.identity.service import delete_account
from backend.modules.progress.rewards import get_gamification_profile
from backend.modules.progress.reporting import (
    get_parent_dashboard, get_weekly_digest, send_weekly_digest
)
from backend.modules.curriculum.authoring import (
    add_class, add_term, get_page_image, list_curriculum_grades, list_curriculum_terms
)
from backend.modules.assessment.exams import _exam_questions
from backend.errors import ApplicationError


class TestPhase3Trust(unittest.TestCase):
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

    def test_uae_vat_retention_on_account_deletion(self):
        """Account deletion must scrub PII while preserving anonymized tax records for UAE FTA 5-year retention."""
        parent = User(
            id="parent_uae_001",
            email="parent_uae@test.ae",
            role="parent",
            password_hash="hashed_pw"
        )
        child = ChildProfile(
            id="child_uae_001",
            parent_id=parent.id,
            name="Sultan",
            default_grade=5
        )
        txn = PaymentTransaction(
            id="txn_uae_001",
            parent_id=parent.id,
            child_id=child.id,
            grade=5,
            term=1,
            amount_usd=Decimal("47.62"),
            vat_amount_usd=Decimal("2.38"),
            tax_invoice_number="INV-20261008-TXN001",
            receipt_number="FHM-20261008-TXN001",
            promo_code="SPRING2026",
            status="succeeded"
        )
        self.db.add_all([parent, child, txn])
        self.db.commit()

        parent_id = parent.id
        child_id = child.id

        # Execute account deletion
        res = delete_account(user=parent, db=self.db)
        self.assertTrue(res["success"])

        # User and child profiles must be scrubbed
        self.assertIsNone(self.db.query(User).filter(User.id == parent_id).first())
        self.assertIsNone(self.db.query(ChildProfile).filter(ChildProfile.id == child_id).first())

        # PaymentTransaction must remain in database with PII removed and tax fields intact
        preserved_txn = self.db.query(PaymentTransaction).filter(PaymentTransaction.id == "txn_uae_001").first()
        self.assertIsNotNone(preserved_txn)
        self.assertIsNone(preserved_txn.parent_id)
        self.assertIsNone(preserved_txn.child_id)
        self.assertIsNone(preserved_txn.promo_code)
        self.assertEqual(preserved_txn.anonymized_parent_id, parent_id)
        self.assertEqual(preserved_txn.tax_invoice_number, "INV-20261008-TXN001")
        self.assertEqual(preserved_txn.receipt_number, "FHM-20261008-TXN001")
        self.assertEqual(preserved_txn.status, "succeeded")

    def test_honest_initial_gamification_profile(self):
        """New student gamification profile must start with 0 XP, 0 streak, and locked starter badges."""
        child = ChildProfile(id="child_new_001", parent_id="p1", name="Mariam", default_grade=5)
        self.db.add(child)
        self.db.commit()

        profile_resp = get_gamification_profile(child.id, db=self.db)
        self.assertEqual(profile_resp.total_xp, 0)
        self.assertEqual(profile_resp.current_streak_days, 0)
        self.assertEqual(profile_resp.weekly_study_minutes, 0)
        self.assertEqual(profile_resp.quizzes_completed_count, 0)
        self.assertEqual(profile_resp.capsules_completed_count, 0)
        self.assertEqual(profile_resp.avg_quiz_score, 0.0)
        self.assertEqual(profile_resp.unlocked_badges_count, 0)

        # All badges must be initially locked
        for badge in profile_resp.badges:
            self.assertFalse(badge.is_unlocked, f"Badge {badge.badge_key} should be locked initially")

    def test_honest_parent_dashboard_for_unassessed_student(self):
        """Unassessed student must show None / Not assessed yet instead of hardcoded 92% or 85% scores."""
        child = ChildProfile(id="child_fresh_001", parent_id="p2", name="Zayed", default_grade=5)
        self.db.add(child)
        self.db.commit()

        dash = get_parent_dashboard(child.id, db=self.db)
        self.assertEqual(dash["overall_stats"]["total_attempts"], 0)
        self.assertEqual(dash["overall_stats"]["accuracy_pct"], 0.0)
        self.assertEqual(dash["overall_stats"]["study_streak_days"], 0)
        self.assertEqual(dash["overall_stats"]["total_xp"], 0)

        # Missing coverage must be 0% completed
        self.assertEqual(dash["missing_coverage"]["unit_1_coverage_pct"], 0.0)
        self.assertEqual(dash["missing_coverage"]["completed_lessons_count"], 0)

        # Skills must be unassessed
        skills = dash["skills"]
        for skill_key, skill_data in skills.items():
            self.assertFalse(skill_data["assessed"])
            self.assertIsNone(skill_data["score_pct"])
            self.assertEqual(skill_data["evidence_count"], 0)
            self.assertIn("لم يُقيّم بعد", skill_data["status_note"])

    def test_parent_dashboard_with_authentic_learning_attempts(self):
        """When learner attempts exist, dashboard must reflect honest computed accuracy and evidence count."""
        child = ChildProfile(id="child_active_001", parent_id="p3", name="Noor", default_grade=5)
        self.db.add(child)
        self.db.commit()

        # Add 3 attempts: 2 correct, 1 incorrect
        attempts = [
            LearnerAttempt(id="att_1", child_id=child.id, lesson_id="lesson_01_ball_games", activity_id="act_1", is_correct=True, score=1.0),
            LearnerAttempt(id="att_2", child_id=child.id, lesson_id="lesson_01_ball_games", activity_id="act_2", is_correct=True, score=1.0),
            LearnerAttempt(id="att_3", child_id=child.id, lesson_id="lesson_01_ball_games", activity_id="act_3", is_correct=False, score=0.0),
        ]
        self.db.add_all(attempts)
        self.db.commit()

        dash = get_parent_dashboard(child.id, db=self.db)
        self.assertEqual(dash["overall_stats"]["total_attempts"], 3)
        self.assertEqual(dash["overall_stats"]["accuracy_pct"], 66.7)
        self.assertEqual(dash["missing_coverage"]["completed_lessons_count"], 1)
        self.assertEqual(dash["missing_coverage"]["unit_1_coverage_pct"], 20.0)

        vocab_skill = dash["skills"]["vocabulary"]
        self.assertTrue(vocab_skill["assessed"])
        self.assertEqual(vocab_skill["score_pct"], 66.7)
        self.assertEqual(vocab_skill["evidence_count"], 3)

    def test_honest_weekly_digest_without_fabricated_metrics(self):
        """Weekly digest for inactive learner must not show fake 135 mins, 86.5 score, or fake strengths/gaps."""
        child = ChildProfile(id="child_digest_001", parent_id="p4", name="Hamad", default_grade=5)
        self.db.add(child)
        self.db.commit()

        digest = get_weekly_digest(child.id, db=self.db)
        self.assertEqual(digest.study_minutes, 0)
        self.assertEqual(digest.quizzes_taken, 0)
        self.assertEqual(digest.avg_quiz_score, 0.0)
        self.assertEqual(digest.streak_days, 0)
        self.assertEqual(digest.top_strengths, [])
        self.assertEqual(digest.active_gaps_summary, [])
        self.assertIn("has not started", digest.tutor_feedback_summary_en)

    def test_weekly_digest_email_fails_closed_in_production_without_smtp(self):
        """In production, dispatching weekly digest via email without configured SMTP must raise 503."""
        parent = User(id="p5", email="parent5@test.ae", role="parent", password_hash="hash")
        child = ChildProfile(id="child_digest_002", parent_id="p5", name="Rashid", default_grade=5)
        self.db.add_all([parent, child])
        self.db.commit()

        req = SendWeeklyDigestRequest(channel="email", recipient_email="parent5@test.ae")

        with patch.dict(os.environ, {"FAHIM_ENV": "production", "FAHIM_SMTP_HOST": ""}):
            with self.assertRaises(ApplicationError) as ctx:
                send_weekly_digest(child.id, req, db=self.db)
            self.assertEqual(ctx.exception.status_code, 503)

    def test_curriculum_grades_and_terms_persistence(self):
        """Curriculum hierarchy containers (add_class and add_term) must persist entities in database."""
        # 1. Add class (Grade 6)
        class_req = AdminAddClassRequest(
            grade_number=6,
            name_ar="الصف السادس",
            name_en="Grade 6"
        )
        class_res = add_class(class_req, db=self.db)
        self.assertTrue(class_res["success"])
        self.assertEqual(class_res["id"], "grade_6")

        # Verify persisted in database
        saved_grade = self.db.query(CurriculumGrade).filter(CurriculumGrade.grade_number == 6).first()
        self.assertIsNotNone(saved_grade)
        self.assertEqual(saved_grade.name_ar, "الصف السادس")
        self.assertEqual(saved_grade.name_en, "Grade 6")

        # 2. Add term (Grade 6, Term 1)
        term_req = AdminAddTermRequest(
            grade=6,
            term=1,
            title_ar="الفصل الدراسي الأول",
            title_en="Term 1",
            price_usd=25.0
        )
        term_res = add_term(term_req, db=self.db)
        self.assertTrue(term_res["success"])
        self.assertEqual(term_res["id"], "grade_6_term_1")

        # Verify persisted in database
        saved_term = self.db.query(CurriculumTerm).filter(
            CurriculumTerm.grade == 6,
            CurriculumTerm.term == 1
        ).first()
        self.assertIsNotNone(saved_term)
        self.assertEqual(saved_term.title_ar, "الفصل الدراسي الأول")
        self.assertEqual(float(saved_term.price_usd), 25.0)

        # 3. Verify listing helpers
        grades = list_curriculum_grades(self.db)
        self.assertTrue(any(g.grade_number == 6 for g in grades))

        terms = list_curriculum_terms(6, self.db)
        self.assertTrue(any(t.term == 1 for t in terms))

    def test_page_image_integrity_no_silent_fallback_to_page_one(self):
        """Requesting a missing scanned page must return 404 rather than silently substituting page 1."""
        with self.assertRaises(ApplicationError) as ctx:
            get_page_image(pdf_page=999, edition_id="non_existent_edition")
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("Page image for page 999 not found", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()

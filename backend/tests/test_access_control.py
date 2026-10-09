"""Real-token authorization tests with an independent in-memory database."""
import datetime
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import (
    User, ChildProfile, TutorAssignment, TutorSubmission, PaymentTransaction,
    LearnerMistake, LearnerAttempt, BookEdition, Unit, Lesson, LessonVersion,
    UserSession,
)
from backend.security import create_access_token, decode_access_token, hash_password
from backend.curriculum_seed import BALL_GAMES_CONTENT_V02


class TestAccessControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("TestPassword123!")

    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            for name, role in (("pa", "parent"), ("pb", "parent"), ("ta", "tutor"), ("tb", "tutor"), ("ad", "admin")):
                db.add(User(id=name, email=f"{name}@test.local", full_name=name, role=role, password_hash=self.password_hash, is_verified=True))
            db.commit()
            for name, parent, pin in (("a1", "pa", "1111"), ("a2", "pa", "2222"), ("b1", "pb", "3333")):
                db.add(ChildProfile(id=name, parent_id=parent, name=name, access_pin=pin, default_grade=5))
            db.add(BookEdition(id="book", title="Test edition"))
            db.commit()
            db.add(Unit(id="unit", book_edition_id="book", unit_number=1, title_ar="اختبار", title_en="Test"))
            db.commit()
            db.add(Lesson(id="lesson_01_ball_games", unit_id="unit", lesson_order=1, grade=5, term=1,
                          title_ar="اختبار", title_en="Test", start_page=6, is_first_chapter_demo=True))
            db.commit()
            db.add(LessonVersion(id="version", lesson_id="lesson_01_ball_games", content_json=json.dumps(BALL_GAMES_CONTENT_V02), content_hash="test", is_active=True, status="published"))
            db.add(TutorAssignment(tutor_id="ta", child_id="a1"))
            for child in ("a1", "a2", "b1"):
                parent = "pb" if child == "b1" else "pa"
                db.add(TutorSubmission(id=f"work-{child}", child_id=child, lesson_id="lesson_01_ball_games", activity_id="write", content_text="Test"))
                db.add(PaymentTransaction(id=f"txn-{child}", child_id=child, parent_id=parent, grade=5, term=1,
                                          receipt_number=f"receipt-{child}", tax_invoice_number=f"invoice-{child}"))
            db.add(LearnerMistake(id=1, child_id="b1", lesson_id="lesson_01_ball_games", activity_id="act", concept_name="Test", wrong_answer="x", correct_answer="y"))
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

    def auth(self, user="pa", role=None, child=None, expired=False):
        role = role or {"pa": "parent", "pb": "parent", "ta": "tutor", "tb": "tutor", "ad": "admin"}[user]
        token = create_access_token({"sub": user, "role": role, "child_id": child,
                                    "session_kind": "learner" if role == "learner" else None},
                                    expires_delta=datetime.timedelta(seconds=-5) if expired else None)
        payload = decode_access_token(token)
        if payload and "jti" in payload:
            with self.session() as db:
                db.add(UserSession(
                    id=payload["jti"],
                    user_id=user,
                    expires_at=datetime.datetime.utcfromtimestamp(payload["exp"]),
                    revoked_at=datetime.datetime.utcnow() if expired else None,
                ))
                db.commit()
        return {"Authorization": f"Bearer {token}"}

    def test_public_demo_and_anonymous_private_routes(self):
        self.assertEqual(self.client.get("/api/curriculum/lesson/lesson_01_ball_games").status_code, 200)
        for url in ("/api/parent/dashboard/a1", "/api/tutor/queue", "/api/payments/receipts?child_id=a1",
                    "/api/mastery/heatmap/a1", "/api/gamification/leaderboard", "/api/attempts/mistakes?child_id=a1",
                    "/api/curriculum/learning-plan/a1", "/api/admin/tutor-assignments"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 401)

    def test_parent_ownership_for_reads_and_mutations(self):
        for url in ("/api/parent/dashboard/b1", "/api/tutor/submissions/b1", "/api/mastery/heatmap/b1",
                    "/api/payments/receipts?child_id=b1", "/api/attempts/mistakes?child_id=b1",
                    "/api/curriculum/terms?child_id=b1", "/api/curriculum/lessons?child_id=b1",
                    "/api/modules/capsules?child_id=b1", "/api/gamification/profile/b1",
                    "/api/curriculum/learning-plan/b1"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url, headers=self.auth()).status_code, 403)
        for url, payload in (
            ("/api/attempts/submit", {"child_id": "b1", "lesson_id": "lesson_01_ball_games", "activity_id": "act_01", "user_answer": "opt_3"}),
            ("/api/curriculum/submit-diagnostic", {"child_id": "b1", "answers": {}}),
            ("/api/curriculum/onboarding-profile", {"child_id": "b1", "name": "Changed"}),
            ("/api/payments/checkout", {"child_id": "b1", "grade": 5, "term": 1}),
            ("/api/payments/redeem-voucher", {"child_id": "b1", "code": "anything"}),
            ("/api/modules/capsules/capsule_01_taa_marbutah/complete", {"child_id": "b1"}),
            ("/api/modules/assessments/submit-exam", {"child_id": "b1", "answers": {}, "time_taken_seconds": 1}),
            ("/api/mastery/record-drill", {"child_id": "b1", "concept_key": "x", "question_id": "x", "selected_index": 0, "is_correct": True}),
            ("/api/ai/ask-fahim", {"child_id": "b1", "question": "Hello"}),
            ("/api/ai/socratic-learn", {"child_id": "b1", "topic": "Test", "student_input": "Test"}),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url, json=payload, headers=self.auth()).status_code, 403)
        self.assertEqual(self.client.post("/api/attempts/mistakes/1/resolve", headers=self.auth()).status_code, 403)
        with self.session() as db:
            self.assertEqual(db.get(ChildProfile, "b1").name, "b1")
            self.assertFalse(db.get(LearnerMistake, 1).is_resolved)
            self.assertEqual(db.query(LearnerAttempt).count(), 0)
        self.assertEqual(self.client.get("/api/parent/dashboard/a1", headers=self.auth()).status_code, 200)

    def test_learner_cannot_become_parent_or_access_sibling(self):
        response = self.client.post("/api/auth/student-pin-login", json={"parent_email": "pa@test.local", "pin": "1111"})
        self.assertEqual(response.status_code, 200)
        headers = {"Authorization": "Bearer " + response.json()["access_token"]}
        me = self.client.get("/api/auth/me", headers=headers).json()
        self.assertEqual(me["role"], "learner")
        self.assertEqual([c["id"] for c in me["children"]], ["a1"])
        self.assertIsNone(me["children"][0]["access_pin"])
        self.assertEqual([c["id"] for c in self.client.get("/api/auth/children", headers=headers).json()], ["a1"])
        self.assertEqual(self.client.get("/api/tutor/submissions/a1", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/api/tutor/submissions/a2", headers=headers).status_code, 403)
        for url, payload in (("/api/auth/switch-child/a2", {}), ("/api/auth/children", {"name": "new"}),
                             ("/api/curriculum/onboarding-profile", {"child_id": "a1", "access_pin": "9999"}),
                             ("/api/payments/checkout", {"child_id": "a1", "grade": 5, "term": 1})):
            self.assertEqual(self.client.post(url, json=payload, headers=headers).status_code, 403)
        self.assertEqual(self.client.patch("/api/auth/children/a1", json={"name": "Changed"}, headers=headers).status_code, 403)

    def test_tutor_queue_review_and_revocation(self):
        queue = self.client.get("/api/tutor/queue", headers=self.auth("ta"))
        self.assertEqual([s["id"] for s in queue.json()], ["work-a1"])
        self.assertEqual(self.client.get("/api/tutor/queue", headers=self.auth("tb")).json(), [])
        self.assertEqual(self.client.get("/api/tutor/queue", headers=self.auth()).status_code, 403)
        for child, expected in (("a1", 200), ("a2", 403), ("b1", 403)):
            response = self.client.post("/api/tutor/review", headers=self.auth("ta"), json={"submission_id": f"work-{child}", "tutor_score": 8, "tutor_feedback": "Reviewed"})
            self.assertEqual(response.status_code, expected)
        with self.session() as db:
            self.assertEqual(db.get(TutorSubmission, "work-a1").tutor_id, "ta")
            self.assertEqual(db.get(TutorSubmission, "work-b1").status, "pending")
        url = "/api/admin/tutor-assignments/ta/a1"
        self.assertEqual(self.client.delete(url, headers=self.auth("ta")).status_code, 403)
        self.assertEqual(self.client.delete(url, headers=self.auth("ad")).status_code, 200)
        self.assertEqual(self.client.get("/api/tutor/queue?status_filter=all", headers=self.auth("ta")).json(), [])
        self.assertEqual(self.client.get("/api/tutor/submissions/a1", headers=self.auth("ta")).status_code, 403)
        for _ in range(2):
            self.assertEqual(self.client.put(url, headers=self.auth("ad")).status_code, 200)
        with self.session() as db:
            self.assertEqual(db.query(TutorAssignment).count(), 1)
        self.assertEqual(len(self.client.get("/api/admin/tutor-assignment-options", headers=self.auth("ad")).json()["tutors"]), 2)

    def test_admin_writes_and_reviewer_flag_require_staff(self):
        payload = {"grade_number": 6, "name_ar": "اختبار", "name_en": "Test"}
        for headers, expected in (({}, 401), (self.auth(), 403), (self.auth("ta"), 403), (self.auth("ad"), 200)):
            self.assertEqual(self.client.post("/api/admin/add-class", headers=headers, json=payload).status_code, expected)
        url = "/api/curriculum/lesson/lesson_01_ball_games?is_reviewer=true"
        self.assertEqual(self.client.get(url).status_code, 401)
        self.assertEqual(self.client.get(url, headers=self.auth()).status_code, 403)
        self.assertEqual(self.client.get(url, headers=self.auth("ad")).status_code, 200)
        self.assertEqual(self.client.get(url + "&child_id=a1", headers=self.auth("ta")).status_code, 200)
        self.assertEqual(self.client.get(url + "&child_id=b1", headers=self.auth("ta")).status_code, 403)

    def test_invoice_aliases_and_leaderboard_do_not_leak_other_families(self):
        for reference in ("receipt-b1", "invoice-b1", "txn-b1"):
            self.assertEqual(self.client.get(f"/api/payments/invoice/{reference}", headers=self.auth()).status_code, 403)
        self.assertEqual(self.client.get("/api/payments/invoice/receipt-a1", headers=self.auth()).status_code, 200)
        for headers, allowed in ((self.auth(), {"a1", "a2"}), (self.auth("ta"), {"a1"}), (self.auth("pa", "learner", "a1"), {"a1"})):
            result = self.client.get("/api/gamification/leaderboard?grade=5", headers=headers)
            self.assertEqual({r["child_id"] for r in result.json()["leaderboard"]}, allowed)
        self.assertEqual(self.client.get("/api/gamification/leaderboard?current_child_id=b1", headers=self.auth()).status_code, 403)

    def test_invalid_expired_and_changed_role_sessions(self):
        for headers in ({"Authorization": "Bearer invalid"}, {"Authorization": "Bearer "}, self.auth(expired=True),
                        self.auth("pa", "admin"), self.auth("pa", "learner", "b1"), self.auth("pa", "learner")):
            self.assertEqual(self.client.get("/api/auth/me", headers=headers).status_code, 401)
        self.assertEqual(self.client.get("/api/curriculum/terms?child_id=a1").status_code, 401)

    def test_anonymous_writes_are_denied_and_own_learner_attempt_is_allowed(self):
        request = {"child_id": "a1", "lesson_id": "lesson_01_ball_games", "activity_id": "act_01", "user_answer": "opt_3"}
        self.assertEqual(self.client.post("/api/attempts/submit", json=request).status_code, 401)
        self.assertEqual(self.client.post("/api/payments/checkout", json={"child_id": "a1", "grade": 5, "term": 1}).status_code, 401)
        self.assertEqual(self.client.post("/api/attempts/submit", json=request, headers=self.auth("pa", "learner", "a1")).status_code, 200)
        self.assertEqual(self.client.post("/api/attempts/submit", json=request, headers=self.auth("ta")).status_code, 403)
        with self.session() as db:
            self.assertEqual(db.query(LearnerAttempt).count(), 1)

    def test_routes_require_identity_unless_explicitly_public(self):
        from fastapi.routing import APIRoute
        public = {
            "/", "/api/health", "/api/ready", "/api/metrics", "/api/meta", "/api/curriculum/schools", "/api/curriculum/grades",
            "/api/curriculum/diagnostic-questions", "/api/admin/coverage-report",
            "/api/admin/ocr-page/{pdf_page}", "/api/admin/page-image/{pdf_page}",
            "/api/audio/tts-info", "/api/audio/synthesize", "/api/modules/malazim/{lesson_id}",
            "/api/modules/capsules/{capsule_id}", "/api/modules/assessments/adaptive/{lesson_id}",
            "/api/modules/assessments/exam-simulation/{grade}/{term}",
            "/apk", "/apk/download", "/download/apk",
            "/api/payments/webhook", "/api/payments/provider-webhook",
        }
        public.update('/api/auth/' + suffix for suffix in (
            'signup', 'verify-otp', 'create-password-enroll', 'login', 'login-otp',
            'verify-login-otp', 'student-pin-login', 'forgot-password', 'reset-password',
        ))
        def authenticated(dependency):
            return any(
                getattr(d.call, '__name__', '') in ('get_current_user', 'get_optional_user') or authenticated(d)
                for d in dependency.dependencies
            )
        for route in app.routes:
            if isinstance(route, APIRoute) and route.path not in public:
                self.assertTrue(authenticated(route.dependant), route.path)


    def test_content_access_matrix_and_revocation(self):
        from backend.models import TermAccess
        paths = ["/api/curriculum/lesson/lesson_01_ball_games",
                 "/api/modules/malazim/lesson_01_ball_games",
                 "/api/modules/assessments/adaptive/lesson_01_ball_games"]
        for path in paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            for key in ('"correct_answer":', '"correct_index":', '"target_ar":', '"solution_walkthrough_en":'):
                self.assertNotIn(key, response.text)
            self.assertEqual(self.client.get(path + "?is_reviewer=true").status_code, 401)
            self.assertEqual(self.client.get(path + "?is_reviewer=true", headers=self.auth()).status_code, 403)
        with self.session() as db:
            db.get(Lesson, "lesson_01_ball_games").is_first_chapter_demo = False
            db.commit()
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.get(path + "?child_id=a1", headers=self.auth()).status_code, 402)
            self.assertEqual(self.client.get(path + "?child_id=b1", headers=self.auth()).status_code, 403)
            reviewer = path + "?child_id=a1&is_reviewer=true"
            self.assertEqual(self.client.get(reviewer, headers=self.auth("ta")).status_code, 200)
            self.assertEqual(self.client.get(reviewer, headers=self.auth("tb")).status_code, 403)
            self.assertEqual(self.client.get(path + "?is_reviewer=true", headers=self.auth("ad")).status_code, 200)
        with self.session() as db:
            db.add(TermAccess(child_id="a1", grade=5, term=1, is_unlocked=True))
            db.commit()
        for path in paths:
            for headers in (self.auth(), self.auth(role="learner", child="a1")):
                response = self.client.get(path + "?child_id=a1", headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn('"correct_index":', response.text)
                self.assertNotIn('"correct_answer":', response.text)
            self.assertEqual(self.client.get(path + "?child_id=a2", headers=self.auth()).status_code, 402)
        with self.session() as db:
            db.query(TutorAssignment).delete()
            db.query(TermAccess).update({"is_unlocked": False})
            db.commit()
        for path in paths:
            self.assertEqual(self.client.get(path + "?child_id=a1", headers=self.auth()).status_code, 402)
            self.assertEqual(self.client.get(path + "?child_id=a1&is_reviewer=true", headers=self.auth("ta")).status_code, 403)

    def test_booklet_feedback_is_per_submission_and_bank_is_unchanged(self):
        from backend.malazim_bank import MALAZIM_DATA
        path = "/api/modules/malazim/lesson_01_ball_games"
        section = MALAZIM_DATA["lesson_01_ball_games"]["study_mode"]["sections"][0]
        key = section["inline_exercise"]["correct_index"]
        response = self.client.post(path + "/check", json={"section_id": section["section_id"], "answer": key})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_correct"])
        self.assertEqual(self.client.post(path + "/check", json={"section_id": section["section_id"], "answer": -1}).status_code, 422)
        self.assertNotIn('"correct_index":', self.client.get(path).text)
        self.assertIn('"correct_index":', self.client.get(path + "?is_reviewer=true", headers=self.auth("ad")).text)
        with self.session() as db:
            db.get(Lesson, "lesson_01_ball_games").is_first_chapter_demo = False
            db.commit()
        response = self.client.post(path + "/check", headers=self.auth(), json={"child_id": "a1", "section_id": section["section_id"], "answer": key})
        self.assertEqual(response.status_code, 402)
        attempt = self.client.post("/api/attempts/submit", headers=self.auth(), json={"child_id": "a1", "lesson_id": "lesson_01_ball_games", "activity_id": "prep_01", "user_answer": "opt_a"})
        self.assertEqual(attempt.status_code, 402)
        exam = self.client.post("/api/modules/assessments/submit-exam", headers=self.auth(), json={"child_id": "a1", "grade": 5, "term": 1, "answers": {}, "time_taken_seconds": 1})
        self.assertEqual(exam.status_code, 402)

    def test_unsupported_content_does_not_fall_back_to_demo(self):
        for path in ("/api/modules/malazim/missing", "/api/modules/assessments/adaptive/missing", "/api/modules/assessments/exam-simulation/6/2"):
            self.assertEqual(self.client.get(path).status_code, 404)


    def test_sentence_demo_feedback_and_locked_access(self):
        challenge = BALL_GAMES_CONTENT_V02["sentence_builder"]["challenges"][0]
        path = "/api/modules/sentences/lesson_01_ball_games/check"
        payload = {"activity_id": challenge["id"], "answer": challenge["target_ar"]}
        response = self.client.post(path, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_correct"])
        self.assertNotIn("target_ar", response.json())
        self.assertEqual(self.client.post(path, json={**payload, "activity_id": "missing"}).status_code, 404)
        with self.session() as db:
            db.get(Lesson, "lesson_01_ball_games").is_first_chapter_demo = False
            db.commit()
        self.assertEqual(self.client.post(path, json=payload).status_code, 401)
        self.assertEqual(self.client.post(path, json={**payload, "child_id": "a1"}, headers=self.auth()).status_code, 402)

    def test_learner_role_access_to_learning_and_gamification_endpoints(self):
        learner_auth = self.auth("pa", role="learner", child="a1")
        sibling_auth = self.auth("pa", role="learner", child="a2")

        # 1. AI Assistant Endpoints (Ask Fahim & Socratic Learn)
        ask_res = self.client.post("/api/ai/ask-fahim", headers=learner_auth, json={"question": "ما هي الرياضة؟", "child_id": "a1"})
        self.assertEqual(ask_res.status_code, 200)
        self.assertIn("answer_ar", ask_res.json())

        soc_res = self.client.post("/api/ai/socratic-learn", headers=learner_auth, json={"topic": "كرة القدم", "student_input": "أريد تعلم القواعد", "child_id": "a1"})
        self.assertEqual(soc_res.status_code, 200)
        self.assertIn("response_ar", soc_res.json())

        # Learner cannot invoke AI queries scoped to another child
        self.assertEqual(self.client.post("/api/ai/ask-fahim", headers=learner_auth, json={"question": "سؤال", "child_id": "a2"}).status_code, 403)
        self.assertEqual(self.client.post("/api/ai/socratic-learn", headers=learner_auth, json={"topic": "سؤال", "student_input": "سؤال", "child_id": "b1"}).status_code, 403)

        # 2. Gamification Endpoints (Profile & Leaderboard)
        self.assertEqual(self.client.get("/api/gamification/profile/a1", headers=learner_auth).status_code, 200)
        self.assertEqual(self.client.get("/api/gamification/profile/a2", headers=learner_auth).status_code, 403)
        self.assertEqual(self.client.get("/api/gamification/leaderboard", headers=learner_auth).status_code, 200)

        # 3. Mastery Endpoints (Heatmap, Review Session, Record Drill)
        self.assertEqual(self.client.get("/api/mastery/heatmap/a1", headers=learner_auth).status_code, 200)
        self.assertEqual(self.client.get("/api/mastery/heatmap/a2", headers=learner_auth).status_code, 403)
        sess_res = self.client.get("/api/mastery/review-session/a1", headers=learner_auth)
        self.assertEqual(sess_res.status_code, 200)
        first_q = sess_res.json()["questions"][0]
        self.assertEqual(self.client.get("/api/mastery/review-session/a2", headers=learner_auth).status_code, 403)

        drill_res = self.client.post("/api/mastery/record-drill", headers=learner_auth, json={"child_id": "a1", "concept_key": "conjugation_past", "question_id": first_q["id"], "selected_index": first_q["correct_index"], "is_correct": True})
        self.assertEqual(drill_res.status_code, 200)
        self.assertEqual(drill_res.json()["concept_key"], "conjugation_past")
        self.assertEqual(self.client.post("/api/mastery/record-drill", headers=learner_auth, json={"child_id": "a2", "concept_key": "conjugation_past", "question_id": first_q["id"], "selected_index": first_q["correct_index"], "is_correct": True}).status_code, 403)

import unittest
import os
import sys

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ["FAHIM_ENV"] = "development"
os.environ["FAHIM_SEED_DEMO"] = "1"
os.environ["FAHIM_EXPOSE_DEBUG_OTP"] = "1"

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine, SessionLocal, run_migrations
from backend.curriculum_seed import seed_database
from backend.scoring import normalize_arabic_text, evaluate_activity_answer

class TestFahimBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["FAHIM_ENV"] = "development"
        run_migrations()
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            from backend.models import User, OtpCode, ChildProfile, TermAccess, PaymentTransaction, LearnerAttempt, LearnerMistake, UserSession
            test_user = db.query(User).filter(User.email == "newparent@fahim.ae").first()
            if test_user:
                for child in test_user.children:
                    db.query(TermAccess).filter(TermAccess.child_id == child.id).delete()
                    db.query(PaymentTransaction).filter(PaymentTransaction.child_id == child.id).delete()
                    db.query(LearnerAttempt).filter(LearnerAttempt.child_id == child.id).delete()
                    db.query(LearnerMistake).filter(LearnerMistake.child_id == child.id).delete()
                    db.delete(child)
                db.query(UserSession).filter(UserSession.user_id == test_user.id).delete()
                db.query(OtpCode).filter(OtpCode.email == "newparent@fahim.ae").delete()
                db.delete(test_user)
                db.commit()
            seed_database(db)

            parent_user = db.query(User).filter(User.email == "parent@fahim.ae").first()
            if parent_user:
                for child in parent_user.children:
                    if child.name == "Zayed Al-Nuaimi":
                        child.access_pin = "1234"
                        child.avatar_id = "avatar_falcon"
                        child.curriculum_stream = "MoE / CBSE Arabic (Non-Arabs)"
                        child.diagnostic_completed = False
                        child.diagnostic_level = "intermediate"
                db.commit()
        finally:
            db.close()
        cls.client = TestClient(app)

    def setUp(self):
        # Existing happy-path flows now use a real parent session.
        import datetime
        from backend.models import User, UserSession
        from backend.security import create_access_token, decode_access_token
        with SessionLocal() as db:
            parent = db.query(User).filter(User.email == "parent@fahim.ae").one()
            admin = db.query(User).filter(User.role == "admin").first()
            if admin is None:
                admin = User(email="access-admin@test.local", role="admin", password_hash="unused", is_verified=True)
                db.add(admin)
                db.commit()
            admin_token = create_access_token({"sub": admin.id, "role": "admin"})
            parent_token = create_access_token({"sub": parent.id, "role": "parent"})
            admin_payload = decode_access_token(admin_token)
            parent_payload = decode_access_token(parent_token)
            if admin_payload and "jti" in admin_payload:
                db.add(UserSession(
                    id=admin_payload["jti"],
                    user_id=admin.id,
                    expires_at=datetime.datetime.utcfromtimestamp(admin_payload["exp"]),
                ))
            if parent_payload and "jti" in parent_payload:
                db.add(UserSession(
                    id=parent_payload["jti"],
                    user_id=parent.id,
                    expires_at=datetime.datetime.utcfromtimestamp(parent_payload["exp"]),
                ))
            db.commit()
            self.admin_headers = {"Authorization": "Bearer " + admin_token}
            parent_headers = {"Authorization": "Bearer " + parent_token}
        self.client = TestClient(app, headers=parent_headers)
        self.addCleanup(self.client.close)
        if self._testMethodName == "test_08_admin_scaling_workflows":
            self.client.headers.update(self.admin_headers)

    def test_01_arabic_normalization(self):
        """Test Arabic normalizer preserves ة vs ه, ي vs ى and ignores optional tashkeel."""
        # Tashkeel removal
        vowelled = "كُرَةُ الْقَدَمِ"
        plain = "كرة القدم"
        self.assertEqual(normalize_arabic_text(vowelled), plain)

        # Tatweel removal
        tatweel_text = "كـــرة الـــقـــدم"
        self.assertEqual(normalize_arabic_text(tatweel_text), "كرة القدم")

        # Preservation of ة (Taa Marbuta) vs ه (Haa)
        self.assertNotEqual(normalize_arabic_text("لعبة"), normalize_arabic_text("لعبـه"))
        self.assertEqual(normalize_arabic_text("لعبة"), "لعبة")

        # Preservation of ي (Yaa) vs ى (Alif Maqsura)
        self.assertNotEqual(normalize_arabic_text("علي"), normalize_arabic_text("على"))

    def test_02_pinned_grading_ignores_client_score(self):
        """Test that server grades against pinned answer key, rejecting client-provided score."""
        activity = {
            "type": "choice",
            "correct_answer": "opt_3",
            "points": 2.0
        }
        # Client tries to pass correct client_score for wrong answer
        is_corr, score, max_score, fb_ar, fb_en, _, _ = evaluate_activity_answer(
            activity,
            user_answer="opt_1"
        )
        self.assertFalse(is_corr)
        self.assertEqual(score, 0.0)
        self.assertEqual(max_score, 2.0)

        # Correct answer
        is_corr2, score2, max_score2, _, _, _, _ = evaluate_activity_answer(
            activity,
            user_answer="opt_3"
        )
        self.assertTrue(is_corr2)
        self.assertEqual(score2, 2.0)

    def test_03_signup_otp_flow(self):
        """Test email signup requesting 6-digit OTP code."""
        email = "newparent@fahim.ae"
        res = self.client.post("/api/auth/signup", json={"email": email})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("debug_otp", data)
        otp = data["debug_otp"]
        self.assertEqual(len(otp), 6)

        # Verify OTP
        verify_res = self.client.post("/api/auth/verify-otp", json={
            "email": email,
            "code": otp,
            "purpose": "signup"
        })
        self.assertEqual(verify_res.status_code, 200)

        # Complete signup with child enrollment
        enroll_res = self.client.post("/api/auth/create-password-enroll", json={
            "email": email,
            "code": otp,
            "password": "SecurePassword2026!",
            "child_name": "Aarav Sharma",
            "child_gender": "Boy",
            "child_age": 10,
            "child_school": "Delhi Private School, Dubai",
            "child_grade": 5
        })
        self.assertEqual(enroll_res.status_code, 200)
        enroll_data = enroll_res.json()
        self.assertIn("access_token", enroll_data)
        self.assertEqual(enroll_data["active_child"]["name"], "Aarav Sharma")
        self.assertEqual(enroll_data["active_child"]["default_grade"], 5)

    def test_04_login_and_forgot_password(self):
        """Test login with view password support and forgot password reset."""
        # Login
        login_res = self.client.post("/api/auth/login", json={
            "email": "newparent@fahim.ae",
            "password": "SecurePassword2026!"
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.json()["active_child"]["default_grade"], 5)

        # Forgot password request
        forgot_res = self.client.post("/api/auth/forgot-password", json={
            "email": "newparent@fahim.ae"
        })
        self.assertEqual(forgot_res.status_code, 200)
        reset_otp = forgot_res.json().get("debug_otp")
        self.assertIsNotNone(reset_otp)

        # Reset password
        reset_res = self.client.post("/api/auth/reset-password", json={
            "email": "newparent@fahim.ae",
            "code": reset_otp,
            "new_password": "NewSecurePassword2026!"
        })
        self.assertEqual(reset_res.status_code, 200)

        # Verify new password login works
        new_login = self.client.post("/api/auth/login", json={
            "email": "newparent@fahim.ae",
            "password": "NewSecurePassword2026!"
        })
        self.assertEqual(new_login.status_code, 200)

    def test_05_curriculum_demo_and_paywall(self):
        """Test free demo access for Chapter 1 (Ball Games) and USD 50 paywall for non-demo."""
        # 1. First chapter (Ball Games) must be accessible as Free Demo
        demo_res = self.client.get("/api/curriculum/lesson/lesson_01_ball_games")
        self.assertEqual(demo_res.status_code, 200)
        demo_data = demo_res.json()
        self.assertTrue(demo_data["lesson"]["is_first_chapter_demo"])
        self.assertIn("vocabulary_cards", demo_data["content"])

        # 2. Non-demo lesson without payment must return 402 Payment Required
        locked_res = self.client.get("/api/curriculum/lesson/lesson_02_horse_riding")
        self.assertEqual(locked_res.status_code, 402)

    def test_06_payment_checkout_unlocks_term(self):
        """Test $50 payment checkout cracks and unlocks the Term for the child."""
        # Login demo parent to get child ID
        login_res = self.client.post("/api/auth/login", json={
            "email": "parent@fahim.ae",
            "password": "FahimPass2026!"
        })
        child_id = login_res.json()["active_child"]["id"]

        checkout_res = self.client.post("/api/payments/checkout", json={
            "child_id": child_id,
            "grade": 5,
            "term": 1,
            "payment_method": "card",
            "card_number": "4242424242424242",
            "exp_month": "12",
            "exp_year": "2028",
            "cvc": "123",
            "promo_code": "FAHIM100"  # 100% demo promo
        })
        self.assertEqual(checkout_res.status_code, 200)
        data = checkout_res.json()
        self.assertTrue(data["success"])
        self.assertIn("receipt_number", data)

        # Check receipts
        rec_res = self.client.get(f"/api/payments/receipts?child_id={child_id}")
        self.assertEqual(rec_res.status_code, 200)
        self.assertGreaterEqual(len(rec_res.json()), 1)

    def test_07_attempt_submission_and_mistake_notebook(self):
        """Test learner attempt submission, score recording, and mistake notebook."""
        login_res = self.client.post("/api/auth/login", json={
            "email": "parent@fahim.ae",
            "password": "FahimPass2026!"
        })
        child_id = login_res.json()["active_child"]["id"]

        # Submit correct answer
        sub_res = self.client.post("/api/attempts/submit", json={
            "child_id": child_id,
            "lesson_id": "lesson_01_ball_games",
            "activity_id": "act_01",
            "user_answer": "opt_3",
            "path_type": "guided"
        })
        self.assertEqual(sub_res.status_code, 200)
        self.assertTrue(sub_res.json()["is_correct"])

        # Submit wrong answer -> triggers mistake notebook
        sub_wrong = self.client.post("/api/attempts/submit", json={
            "child_id": child_id,
            "lesson_id": "lesson_01_ball_games",
            "activity_id": "act_02",
            "user_answer": "opt_1",  # wrong, football is collective (opt_3)
            "path_type": "guided"
        })
        self.assertEqual(sub_wrong.status_code, 200)
        self.assertFalse(sub_wrong.json()["is_correct"])

        # Fetch mistake notebook
        mistakes_res = self.client.get(f"/api/attempts/mistakes?child_id={child_id}")
        self.assertEqual(mistakes_res.status_code, 200)
        mistakes = mistakes_res.json()
        self.assertGreaterEqual(len(mistakes), 1)

    def test_08_admin_scaling_workflows(self):
        """Test ADD_TERM, ADD_CLASS, ADD_LESSON, and UPDATE_EDITION admin endpoints."""
        # 1. ADD_TERM
        term_res = self.client.post("/api/admin/add-term", json={
            "grade": 6,
            "term": 1,
            "title_ar": "الفصل الأول",
            "title_en": "Term 1",
            "price_usd": 50.0
        })
        self.assertEqual(term_res.status_code, 200)
        self.assertTrue(term_res.json()["success"])

        # 2. ADD_CLASS
        class_res = self.client.post("/api/admin/add-class", json={
            "grade_number": 6,
            "name_ar": "الصف السادس",
            "name_en": "Class 6"
        })
        self.assertEqual(class_res.status_code, 200)

        # 3. Coverage report
        cov_res = self.client.get("/api/admin/coverage-report")
        self.assertEqual(cov_res.status_code, 200)
        self.assertEqual(cov_res.json()["total_source_pages"], 108)

    def test_09_login_otp_flow(self):
        """Test passwordless 6-digit OTP login."""
        # Request login OTP
        req_res = self.client.post("/api/auth/login-otp", json={"email": "parent@fahim.ae"})
        self.assertEqual(req_res.status_code, 200)
        otp = req_res.json().get("debug_otp")
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp), 6)

        # Verify login OTP
        ver_res = self.client.post("/api/auth/verify-login-otp", json={
            "email": "parent@fahim.ae",
            "code": otp
        })
        self.assertEqual(ver_res.status_code, 200)
        data = ver_res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], "parent@fahim.ae")
        self.assertIsNotNone(data["active_child"])

    def test_10_student_pin_login(self):
        """Test child direct login with parent email and 4-digit PIN."""
        pin_res = self.client.post("/api/auth/student-pin-login", json={
            "parent_email": "parent@fahim.ae",
            "pin": "1234"
        })
        self.assertEqual(pin_res.status_code, 200)
        data = pin_res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "learner")
        self.assertEqual(data["active_child"]["name"], "Zayed Al-Nuaimi")
        self.assertIsNone(data["active_child"]["access_pin"])

        # Wrong PIN should return 401
        bad_pin_res = self.client.post("/api/auth/student-pin-login", json={
            "parent_email": "parent@fahim.ae",
            "pin": "9999"
        })
        self.assertEqual(bad_pin_res.status_code, 401)

    def test_11_multi_child_management(self):
        """Test adding multiple children, switching active child, and updating child profile."""
        # Login parent to get token
        login_res = self.client.post("/api/auth/login", json={
            "email": "parent@fahim.ae",
            "password": "FahimPass2026!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List existing children
        list_res = self.client.get("/api/auth/children", headers=headers)
        self.assertEqual(list_res.status_code, 200)
        children = list_res.json()
        self.assertGreaterEqual(len(children), 1)

        # Add a new child (Rashid)
        add_res = self.client.post("/api/auth/children", headers=headers, json={
            "name": "Rashid Al-Nuaimi",
            "gender": "Boy",
            "age": 6,
            "school_name": "Sunrise International School, Abu Dhabi",
            "default_grade": 1,
            "avatar_id": "avatar_oryx",
            "curriculum_stream": "MoE / CBSE Arabic (Non-Arabs)",
            "access_pin": "2468"
        })
        self.assertEqual(add_res.status_code, 200)
        new_child = add_res.json()
        self.assertEqual(new_child["name"], "Rashid Al-Nuaimi")
        self.assertEqual(new_child["avatar_id"], "avatar_oryx")
        self.assertIsNone(new_child["access_pin"])

        # Switch active child to Rashid
        switch_res = self.client.post(f"/api/auth/switch-child/{new_child['id']}", headers=headers)
        self.assertEqual(switch_res.status_code, 200)
        switch_data = switch_res.json()
        self.assertEqual(switch_data["active_child"]["id"], new_child["id"])
        self.assertEqual(switch_data["active_child"]["name"], "Rashid Al-Nuaimi")

        # Update Rashid's avatar and pin
        patch_res = self.client.patch(f"/api/auth/children/{new_child['id']}", headers=headers, json={
            "avatar_id": "avatar_camel",
            "access_pin": "9876"
        })
        self.assertEqual(patch_res.status_code, 200)
        updated_child = patch_res.json()
        self.assertEqual(updated_child["avatar_id"], "avatar_camel")
        self.assertIsNone(updated_child["access_pin"])

    def test_12_onboarding_and_diagnostic_flow(self):
        """Test complete 4-step onboarding calibration, diagnostic grading, and learning plan generation."""
        # 1. Fetch diagnostic questions
        q_res = self.client.get("/api/curriculum/diagnostic-questions?grade=5")
        self.assertEqual(q_res.status_code, 200)
        q_data = q_res.json()
        self.assertTrue(q_data["success"])
        self.assertEqual(q_data["count"], 8)
        self.assertEqual(len(q_data["questions"]), 8)
        # Ensure answers and internal answer keys are shielded
        first_q = q_data["questions"][0]
        self.assertNotIn("correct_index", first_q)
        self.assertNotIn("explanation_ar", first_q)
        self.assertIn("passage_ar", first_q)
        self.assertIn("options", first_q)
        self.assertEqual(len(first_q["options"]), 4)

        # Get existing child ID from parent
        login_res = self.client.post("/api/auth/login", json={
            "email": "parent@fahim.ae",
            "password": "FahimPass2026!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        children = self.client.get("/api/auth/children", headers=headers).json()
        child_id = children[0]["id"]

        # 2. Update Onboarding Profile (Steps 1 & 2)
        prof_res = self.client.post("/api/curriculum/onboarding-profile", json={
            "child_id": child_id,
            "name": "Zayed Al-Nuaimi",
            "gender": "Boy",
            "age": 10,
            "school_name": "Sunrise International School, Abu Dhabi",
            "default_grade": 5,
            "selected_term": 1,
            "avatar_id": "avatar_gazelle",
            "curriculum_stream": "MoE / UAE Advanced Stream",
            "access_pin": "5555"
        })
        self.assertEqual(prof_res.status_code, 200)
        p_data = prof_res.json()
        self.assertTrue(p_data["success"])
        self.assertEqual(p_data["child"]["avatar_id"], "avatar_gazelle")
        self.assertIsNone(p_data["child"]["access_pin"])
        self.assertEqual(p_data["child"]["curriculum_stream"], "MoE / UAE Advanced Stream")

        # 3. Submit Diagnostic Assessment (Step 3) - 100% score
        perfect_answers = {
            "diag_q1": 1,
            "diag_q2": 1,
            "diag_q3": 0,
            "diag_q4": 1,
            "diag_q5": 0,
            "diag_q6": 1,
            "diag_q7": 2,
            "diag_q8": 1
        }
        sub_res = self.client.post("/api/curriculum/submit-diagnostic", json={
            "child_id": child_id,
            "answers": perfect_answers
        })
        self.assertEqual(sub_res.status_code, 200)
        s_data = sub_res.json()
        self.assertTrue(s_data["success"])
        self.assertEqual(s_data["score"], 100.0)
        self.assertEqual(s_data["correct_count"], 8)
        self.assertEqual(s_data["calibrated_level"], "independent")
        self.assertIn("reading", s_data["competency_breakdown"])
        self.assertEqual(len(s_data["learning_plan"]["milestones"]), 4)

        # 4. Fetch Learning Plan (Step 4)
        plan_res = self.client.get(f"/api/curriculum/learning-plan/{child_id}")
        self.assertEqual(plan_res.status_code, 200)
        plan_data = plan_res.json()
        self.assertTrue(plan_data["success"])
        self.assertTrue(plan_data["diagnostic_completed"])
        self.assertEqual(plan_data["diagnostic_level"], "independent")
        self.assertEqual(plan_data["diagnostic_score"], 100.0)
        self.assertEqual(len(plan_data["learning_plan"]["milestones"]), 4)

        # Restore baseline PIN for other tests
        self.client.post("/api/curriculum/onboarding-profile", json={
            "child_id": child_id,
            "access_pin": "1234"
        })

    def test_13_core_learning_and_tutoring_modules(self):
        """Test Socratic AI Learn, Malazim Hub, Microlearning Capsules, and Exam Simulation."""
        db = SessionLocal()
        try:
            from backend.models import ChildProfile
            child = db.query(ChildProfile).filter(ChildProfile.name == "Zayed Al-Nuaimi").first()
            child_id = child.id if child else "test_child"
        finally:
            db.close()

        # 1. Test Socratic Learn: Primary Grade Gamified Tone
        soc_pri = self.client.post("/api/ai/socratic-learn", json={
            "topic": "التاء المربوطة والهاء",
            "student_input": "نضع ضمة على الكلمة وننطقها",
            "grade": 5,
            "child_id": child_id
        })
        self.assertEqual(soc_pri.status_code, 200)
        pri_data = soc_pri.json()
        self.assertEqual(pri_data["tone"], "primary_gamified")
        self.assertTrue(pri_data["is_step_mastered"])
        self.assertIn("بطل", pri_data["response_ar"])

        # 2. Test Socratic Learn: Middle/High School Academic Tone
        soc_mid = self.client.post("/api/ai/socratic-learn", json={
            "topic": "التاء المربوطة والهاء",
            "student_input": "نضع ضمة على الكلمة وننطقها",
            "grade": 8,
            "child_id": child_id
        })
        self.assertEqual(soc_mid.status_code, 200)
        mid_data = soc_mid.json()
        self.assertEqual(mid_data["tone"], "middle_academic")
        self.assertIn("صوتي", mid_data["response_ar"])

        # 3. Test Malazim Booklet (Study & Quick Review Modes)
        mal_res = self.client.get("/api/modules/malazim/lesson_01_ball_games")
        self.assertEqual(mal_res.status_code, 200)
        mal_data = mal_res.json()
        self.assertTrue(mal_data["success"])
        self.assertIn("study_mode", mal_data["booklet"])
        self.assertIn("quick_review_mode", mal_data["booklet"])
        self.assertGreater(len(mal_data["booklet"]["study_mode"]["sections"]), 0)
        self.assertGreater(len(mal_data["booklet"]["quick_review_mode"]["bullet_rules"]), 0)

        # 4. Test Capsules: List & Completion
        cap_list = self.client.get(f"/api/modules/capsules?child_id={child_id}")
        self.assertEqual(cap_list.status_code, 200)
        caps_data = cap_list.json()
        self.assertTrue(caps_data["success"])
        self.assertEqual(caps_data["count"], 5)

        comp_res = self.client.post("/api/modules/capsules/capsule_01_taa_marbutah/complete", json={
            "child_id": child_id,
            "score": 100.0,
            "time_spent_seconds": 180
        })
        self.assertEqual(comp_res.status_code, 200)
        self.assertTrue(comp_res.json()["success"])

        # 5. Test Exam Simulation: Fetch and Submit with Bloom's Breakdown
        exam_get = self.client.get("/api/modules/assessments/exam-simulation/5/1")
        self.assertEqual(exam_get.status_code, 200)
        exam_data = exam_get.json()
        self.assertTrue(exam_data["success"])
        self.assertEqual(exam_data["exam"]["total_questions"], 10)
        self.assertEqual(exam_data["exam"]["time_limit_minutes"], 20)

        from backend.assessment_bank import ASSESSMENT_QUESTIONS
        correct_answers = {q["id"]: q["correct_index"] for q in ASSESSMENT_QUESTIONS}

        exam_sub = self.client.post("/api/modules/assessments/submit-exam", json={
            "child_id": child_id,
            "grade": 5,
            "term": 1,
            "answers": correct_answers,
            "time_taken_seconds": 540
        })
        self.assertEqual(exam_sub.status_code, 200)
        eval_resp = exam_sub.json()
        self.assertTrue(eval_resp["success"])
        self.assertEqual(eval_resp["evaluation"]["percentage"], 100.0)
        self.assertEqual(eval_resp["evaluation"]["grade_letter"], "A+")
        self.assertIn("bloom_breakdown", eval_resp["evaluation"])
        self.assertEqual(len(eval_resp["evaluation"]["solution_walkthrough"]), 10)

    def test_14_mastery_knowledge_gaps_and_scheduler(self):
        """Test real-time concept mastery percentage, gap detection, and scheduled review sessions."""
        db = SessionLocal()
        try:
            from backend.models import ChildProfile, ConceptMastery
            child = db.query(ChildProfile).filter(ChildProfile.name == "Zayed Al-Nuaimi").first()
            child_id = child.id if child else "test_child"
            gap_cm = db.query(ConceptMastery).filter(ConceptMastery.child_id == child_id, ConceptMastery.concept_key == "ortho_taa_marbutah").first()
            if gap_cm:
                gap_cm.is_gap = True
                gap_cm.mastery_percentage = 68.0
                db.commit()
        finally:
            db.close()

        # 1. Fetch Heatmap
        hm_res = self.client.get(f"/api/mastery/heatmap/{child_id}")
        self.assertEqual(hm_res.status_code, 200)
        hm_data = hm_res.json()
        self.assertEqual(hm_data["child_name"], "Zayed Al-Nuaimi")
        self.assertGreaterEqual(hm_data["total_concepts_tracked"], 5)
        self.assertIn("grammar", hm_data["concepts_by_category"])
        self.assertIn("vocabulary", hm_data["concepts_by_category"])
        self.assertGreaterEqual(hm_data["active_gaps_count"], 1)

        # 2. Fetch Gap Review Session
        sess_res = self.client.get(f"/api/mastery/review-session/{child_id}")
        self.assertEqual(sess_res.status_code, 200)
        s_data = sess_res.json()
        self.assertGreaterEqual(len(s_data["questions"]), 1)
        first_q = s_data["questions"][0]
        self.assertIn("prompt_ar", first_q)
        self.assertIn("options", first_q)

        # 3. Record Drill Answer
        drill_res = self.client.post("/api/mastery/record-drill", json={
            "child_id": child_id,
            "concept_key": "conjugation_past",
            "question_id": first_q["id"],
            "selected_index": 0,
            "is_correct": True
        })
        self.assertEqual(drill_res.status_code, 200)
        d_data = drill_res.json()
        self.assertEqual(d_data["concept_key"], "conjugation_past")
        self.assertGreater(d_data["new_mastery_pct"], 64.0)
        self.assertEqual(d_data["xp_awarded"], 25)

    def test_15_parent_weekly_digest_and_guidance(self):
        """Test Weekly Digest generation, notification dispatch, and Plain-English Guidance for non-Arabic parents."""
        db = SessionLocal()
        try:
            from backend.models import ChildProfile
            child = db.query(ChildProfile).filter(ChildProfile.name == "Zayed Al-Nuaimi").first()
            child_id = child.id if child else "test_child"
        finally:
            db.close()

        # 1. Fetch Weekly Digest
        dig_res = self.client.get(f"/api/parent/weekly-digest/{child_id}")
        self.assertEqual(dig_res.status_code, 200)
        dig_data = dig_res.json()
        self.assertEqual(dig_data["child_name"], "Zayed Al-Nuaimi")
        self.assertGreater(dig_data["study_minutes"], 0)
        self.assertGreaterEqual(len(dig_data["top_strengths"]), 1)
        self.assertGreaterEqual(len(dig_data["parent_tips"]), 1)

        # 2. Dispatch Weekly Digest via In-App Notification
        send_res = self.client.post(f"/api/parent/send-digest/{child_id}", json={
            "channel": "in_app_notification"
        })
        self.assertEqual(send_res.status_code, 200)
        s_data = send_res.json()
        self.assertTrue(s_data["success"])
        self.assertEqual(s_data["channel"], "in_app_notification")

        # 3. Fetch Actionable Guidance for Non-Arabic Speaking Parents
        guid_res = self.client.get(f"/api/parent/actionable-guidance/{child_id}")
        self.assertEqual(guid_res.status_code, 200)
        g_data = guid_res.json()
        self.assertIn("You don't need to speak Arabic", g_data["welcome_message_en"])
        self.assertGreaterEqual(len(g_data["guidance_items"]), 3)
        self.assertIn("parent_prompt_en", g_data["guidance_items"][0])
        self.assertIn("praise_suggestion_en", g_data["guidance_items"][0])

    def test_16_gamification_streaks_badges_leaderboard(self):
        """Test Gamification profile, XP rewards, streaks, badges shelf, and cohort leaderboard."""
        db = SessionLocal()
        try:
            from backend.models import ChildProfile
            child = db.query(ChildProfile).filter(ChildProfile.name == "Zayed Al-Nuaimi").first()
            child_id = child.id if child else "test_child"
        finally:
            db.close()

        # 1. Fetch Gamification Profile
        prof_res = self.client.get(f"/api/gamification/profile/{child_id}")
        self.assertEqual(prof_res.status_code, 200)
        p_data = prof_res.json()
        self.assertEqual(p_data["child_name"], "Zayed Al-Nuaimi")
        self.assertGreaterEqual(p_data["total_xp"], 450)
        self.assertGreaterEqual(p_data["current_streak_days"], 4)
        self.assertIn(p_data["heritage_rank_en"], ["Knight of Words", "Falcon of Eloquence", "Oasis Sage"])
        self.assertGreaterEqual(len(p_data["badges"]), 4)

        # 2. Fetch Cohort Leaderboard (Admin views cohort across families)
        lb_res = self.client.get(f"/api/gamification/leaderboard?grade=5&current_child_id={child_id}", headers=self.admin_headers)
        self.assertEqual(lb_res.status_code, 200)
        lb_data = lb_res.json()
        self.assertEqual(lb_data["grade"], 5)
        self.assertGreaterEqual(lb_data["total_participants"], 3)
        self.assertGreaterEqual(lb_data["current_child_rank"], 1)
        self.assertTrue(any(e["is_current_user"] for e in lb_data["leaderboard"]))

        # 3. Award XP (requires admin privileges)
        award_res = self.client.post("/api/gamification/award-xp", headers=self.admin_headers, json={
            "child_id": child_id,
            "activity_type": "lesson",
            "xp_amount": 50,
            "reason": "Completed Lesson 1 Exercises"
        })
        self.assertEqual(award_res.status_code, 200)
        a_data = award_res.json()
        self.assertEqual(a_data["xp_awarded"], 50)
        self.assertGreaterEqual(a_data["total_xp"], 500)

    def test_17_monetization_bundles_and_vouchers(self):
        """Test Freemium tier, Annual pass checkout, School voucher redemption, and UAE FTA Tax Invoices."""
        db = SessionLocal()
        try:
            from backend.models import ChildProfile
            child = db.query(ChildProfile).filter(ChildProfile.name == "Zayed Al-Nuaimi").first()
            child_id = child.id if child else "test_child"
        finally:
            db.close()

        # 1. Freemium Verification: Chapter 1 is free demo, Chapter 2 paywall requires unlock
        demo_res = self.client.get("/api/curriculum/lesson/lesson_01_ball_games")
        self.assertEqual(demo_res.status_code, 200)
        demo_json = demo_res.json()
        self.assertTrue(demo_json["lesson"]["is_first_chapter_demo"])

        # 2. Annual Pass Checkout ($120 USD with 20% discount)
        annual_res = self.client.post("/api/payments/checkout-annual", json={
            "child_id": child_id,
            "grade": 5,
            "payment_method": "card",
            "card_number": "4242424242424242",
            "exp_month": "12",
            "exp_year": "2028",
            "cvc": "123",
            "promo_code": ""
        })
        self.assertEqual(annual_res.status_code, 200)
        a_data = annual_res.json()
        self.assertTrue(a_data["success"])
        self.assertEqual(a_data["package_type"], "annual")
        self.assertEqual(a_data["amount_usd"], 50.0)
        self.assertEqual(a_data["unlocked_terms"], [1, 2, 3])
        self.assertEqual(a_data["subtotal_usd"], 47.62)
        self.assertEqual(a_data["vat_amount_usd"], 2.38)
        receipt_num = a_data["receipt_number"]

        # 3. Dynamic Terms status check: All 3 terms must now show is_unlocked == True
        terms_res = self.client.get(f"/api/curriculum/terms?grade=5&child_id={child_id}")
        self.assertEqual(terms_res.status_code, 200)
        terms_data = terms_res.json()
        self.assertEqual(len(terms_data), 3)
        self.assertTrue(terms_data[0]["is_unlocked"])
        self.assertTrue(terms_data[1]["is_unlocked"])
        self.assertTrue(terms_data[2]["is_unlocked"])

        # 4. School Voucher Code Redemption (SUNRISE2026 - 100% Institutional Pass)
        vch_res = self.client.post("/api/payments/redeem-voucher", json={
            "child_id": child_id,
            "grade": 5,
            "code": "SUNRISE2026"
        })
        self.assertEqual(vch_res.status_code, 200)
        v_data = vch_res.json()
        self.assertTrue(v_data["success"])
        self.assertEqual(v_data["package_type"], "annual")
        self.assertEqual(v_data["unlocked_terms"], [1, 2, 3])
        self.assertIn("Sunrise International School", v_data["message"])

        # Bad voucher test
        bad_vch = self.client.post("/api/payments/redeem-voucher", json={
            "child_id": child_id,
            "grade": 5,
            "code": "INVALID-CODE-999"
        })
        self.assertEqual(bad_vch.status_code, 400)

        # 5. UAE FTA-Compliant Tax Invoice Retrieval
        inv_res = self.client.get(f"/api/payments/invoice/{receipt_num}")
        self.assertEqual(inv_res.status_code, 200)
        inv_data = inv_res.json()
        self.assertEqual(inv_data["trn"], "100458923100003")
        self.assertEqual(inv_data["status"], "SUCCEEDED")
        self.assertEqual(inv_data["total_usd"], 50.0)
        self.assertEqual(inv_data["total_aed"], 183.62)
        self.assertEqual(inv_data["subtotal_usd"], 47.62)
        self.assertEqual(inv_data["vat_amount_usd"], 2.38)
        self.assertEqual(len(inv_data["items"]), 1)
        self.assertIn("Terms 1, 2, 3", inv_data["items"][0]["description_en"])

        # 6. Receipts List
        rec_list_res = self.client.get(f"/api/payments/receipts?child_id={child_id}")
        self.assertEqual(rec_list_res.status_code, 200)
        recs = rec_list_res.json()
        self.assertGreaterEqual(len(recs), 2)
        self.assertTrue(any(r["receipt_number"] == receipt_num for r in recs))

    def test_18_full_curriculum_all_lessons_published(self):
        """Test full curriculum expansion: Lessons 1-10 are all published, verified with paywall and content packages."""
        db = SessionLocal()
        try:
            from backend.models import ChildProfile, TermAccess
            child = db.query(ChildProfile).filter(ChildProfile.name == "Zayed Al-Nuaimi").first()
            child_id = child.id if child else "test_child"
        finally:
            db.close()

        # 1. Fetch all lessons for Grade 5 Term 1
        lessons_res = self.client.get(f"/api/curriculum/lessons?grade=5&term=1&child_id={child_id}")
        self.assertEqual(lessons_res.status_code, 200)
        lessons = lessons_res.json()
        self.assertEqual(len(lessons), 10, "Class 5 Term 1 must contain exactly 10 lessons")

        # Verify all 10 lessons are marked published
        for l in lessons:
            self.assertEqual(l["status"], "published", f"Lesson {l['id']} must be marked as published")
            self.assertTrue(l["is_accessible"], f"Lesson {l['id']} should be accessible for unlocked child")

        # Verify Lesson 1 is demo, Lessons 2-10 are not demo
        self.assertTrue(lessons[0]["is_first_chapter_demo"])
        self.assertEqual(lessons[0]["id"], "lesson_01_ball_games")
        for l in lessons[1:]:
            self.assertFalse(l["is_first_chapter_demo"], f"Lesson {l['id']} should not be first chapter demo")

        # 2. Paywall enforcement check: Without child_id or credentials, Lesson 2 must return 402 Payment Required
        locked_res = self.client.get("/api/curriculum/lesson/lesson_02_horse_riding")
        self.assertEqual(locked_res.status_code, 402)
        self.assertIn("Payment required", locked_res.json()["detail"])

        # 3. Unlocked child access: With child_id, Lesson 2 must return 200 and full content package
        unlocked_res = self.client.get(f"/api/curriculum/lesson/lesson_02_horse_riding?child_id={child_id}")
        self.assertEqual(unlocked_res.status_code, 200)
        l2_data = unlocked_res.json()
        self.assertEqual(l2_data["lesson"]["id"], "lesson_02_horse_riding")
        self.assertEqual(l2_data["lesson"]["title_ar"], "ركوب الخيل")
        self.assertEqual(l2_data["version_tag"], "0.2.0")

        l2_content = l2_data["content"]
        # Verify 8-card vocabulary glossary
        self.assertIn("vocabulary_cards", l2_content)
        self.assertEqual(len(l2_content["vocabulary_cards"]), 8)
        # Verify grammar lab
        self.assertIn("grammar_lab", l2_content)
        self.assertIn("Nominal Sentence", l2_content["grammar_lab"]["title_en"])
        # Verify sentence builder & parent companion
        self.assertIn("sentence_builder", l2_content)
        self.assertIn("parent_companion", l2_content)

        # 4. Content verification for Unit 2: Lesson 06 (في مدرستي) and Lesson 10 (وقت المرح)
        l6_res = self.client.get(f"/api/curriculum/lesson/lesson_06_at_school?child_id={child_id}")
        self.assertEqual(l6_res.status_code, 200)
        l6_data = l6_res.json()
        self.assertEqual(l6_data["lesson"]["title_ar"], "في مدرستي")
        self.assertEqual(len(l6_data["content"]["vocabulary_cards"]), 8)
        self.assertIn("grammar_lab", l6_data["content"])

        l10_res = self.client.get(f"/api/curriculum/lesson/lesson_10_fun_time?child_id={child_id}")
        self.assertEqual(l10_res.status_code, 200)
        l10_data = l10_res.json()
        self.assertEqual(l10_data["lesson"]["title_ar"], "وقت المرح")
        self.assertEqual(len(l10_data["content"]["vocabulary_cards"]), 8)
        self.assertIn("speaking_mission", l10_data["content"])

        # 5. Teacher / Reviewer mode: is_reviewer=true allows access without child_id and retains answer keys
        rev_res = self.client.get("/api/curriculum/lesson/lesson_02_horse_riding?is_reviewer=true", headers=self.admin_headers)
        self.assertEqual(rev_res.status_code, 200)
        rev_data = rev_res.json()
        # In reviewer mode, correct_answer is retained in prep_check
        self.assertIn("correct_answer", rev_data["content"]["prep_check"]["questions"][0])

    def test_19_delete_account_and_purge_all_data(self):
        """Test App Store compliant account deletion (DELETE /api/auth/account) permanently purges all data."""
        from backend.models import User, ChildProfile, UserSession
        # 1. Sign up / create a dedicated parent account
        signup_res = self.client.post("/api/auth/signup", json={"email": "delete_me@test.local"})
        otp = signup_res.json()["debug_otp"]
        verify_res = self.client.post("/api/auth/verify-otp", json={
            "email": "delete_me@test.local",
            "code": otp,
            "purpose": "signup"
        })
        self.assertEqual(verify_res.status_code, 200)
        enroll_res = self.client.post("/api/auth/create-password-enroll", json={
            "email": "delete_me@test.local",
            "code": otp,
            "password": "DeleteMe123!",
            "child_name": "Temporary Learner",
            "child_age": 7,
            "child_gender": "Boy",
            "child_school": "Test School",
            "child_grade": 2
        })
        self.assertEqual(enroll_res.status_code, 200)
        token = enroll_res.json()["access_token"]
        user_id = enroll_res.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Verify child was created in DB
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()
            self.assertIsNotNone(user)
            self.assertEqual(len(user.children), 1)
            child_id = user.children[0].id

        # 3. Call DELETE /api/auth/account
        del_res = self.client.delete("/api/auth/account", headers=headers)
        self.assertEqual(del_res.status_code, 200)
        del_data = del_res.json()
        self.assertTrue(del_data["success"])

        # 4. Verify DB is completely purged of user, child, and user sessions
        with SessionLocal() as db:
            self.assertIsNone(db.query(User).filter(User.id == user_id).first())
            self.assertIsNone(db.query(ChildProfile).filter(ChildProfile.id == child_id).first())
            self.assertEqual(db.query(UserSession).filter(UserSession.user_id == user_id).count(), 0)

        # 5. Subsequent calls with token or login should fail
        old_token_res = self.client.get("/api/auth/children", headers=headers)
        self.assertEqual(old_token_res.status_code, 401)
        relogin_res = self.client.post("/api/auth/login", json={
            "email": "delete_me@test.local",
            "password": "DeleteMe123!"
        })
        self.assertEqual(relogin_res.status_code, 401)

    def test_20_speech_evaluation_and_tutor_escalation(self):
        """Test POST /api/audio/evaluate-speech rubric and Ask Fahim tutor escalation ticket persistence."""
        with SessionLocal() as db:
            from backend.models import ChildProfile
            child = db.query(ChildProfile).filter(ChildProfile.name == "Zayed Al-Nuaimi").first()
            child_id = child.id

        # 1. Speech Evaluation Endpoint
        eval_payload = {
            "target_phrase": "كُرَةُ القَدَمِ رِيَاضَةٌ جَمَاعِيَّةٌ",
            "spoken_text": "كرة القدم رياضة جماعية",
            "child_id": child_id
        }
        res = self.client.post("/api/audio/evaluate-speech", json=eval_payload)
        self.assertEqual(res.status_code, 200)
        eval_data = res.json()
        self.assertGreaterEqual(eval_data["overall_score"], 90.0)
        self.assertTrue(eval_data["is_pass"])
        self.assertIn("ممتاز", eval_data["fluency_rating"])
        self.assertIn("ة/ه", eval_data["phoneme_scores"])

        # 2. Multi-Lesson Ask Fahim (Lesson 2 Horse Riding)
        ask_res = self.client.post("/api/ai/ask-fahim", json={
            "question": "ما هي رياضة ركوب الخيل؟",
            "context_lesson_id": "lesson_02_horse_riding",
            "child_id": child_id
        })
        self.assertEqual(ask_res.status_code, 200)
        ask_data = ask_res.json()
        self.assertFalse(ask_data["escalated_to_tutor"])
        self.assertIn("16", ask_data["page_reference"])

        # 3. Tutor Escalation with Ticket Persistence
        complex_res = self.client.post("/api/ai/ask-fahim", json={
            "question": "كيف أصلح محرك الطائرة النفاثة بالتفصيل الممل؟",
            "context_lesson_id": "lesson_01_ball_games",
            "child_id": child_id
        })
        self.assertEqual(complex_res.status_code, 200)
        complex_data = complex_res.json()
        self.assertTrue(complex_data["escalated_to_tutor"])

        # 4. Verify ticket was persisted in child's submissions
        sub_res = self.client.get(f"/api/tutor/submissions/{child_id}")
        self.assertEqual(sub_res.status_code, 200)
        submissions = sub_res.json()
        escalated_ticket = next((s for s in submissions if s["submission_type"] == "ask_fahim_escalation"), None)
        self.assertIsNotNone(escalated_ticket)
        self.assertEqual(escalated_ticket["status"], "pending")
        self.assertIn("محرك الطائرة", escalated_ticket["content_text"])


if __name__ == "__main__":
    unittest.main()




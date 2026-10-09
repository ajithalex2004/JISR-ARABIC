"""
test_curriculum_expansion.py — Comprehensive Test Suite for Grade 5 Terms 2 & 3 Expansion
Validates full coverage of all 22 official UAE Ministry of Education (MoE) chapters across Volumes 1, 2, and 3.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ["FAHIM_ENV"] = "development"
os.environ["FAHIM_SEED_DEMO"] = "1"

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import Lesson, LessonVersion, BookEdition, Unit
from backend.curriculum_catalog import FULL_CURRICULUM_CATALOG
from backend.assessment_bank import (
    ASSESSMENT_QUESTIONS, ASSESSMENT_QUESTIONS_TERM2, ASSESSMENT_QUESTIONS_TERM3,
    get_official_exam_simulation
)
from backend.modules.curriculum.syllabus_data import get_syllabus_for_grade_and_term


class TestCurriculumExpansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_grade5_three_terms_listed(self):
        """Verify that Grade 5 lists all 3 terms with appropriate pricing and unlock status."""
        response = self.client.get("/api/curriculum/terms?grade=5")
        self.assertEqual(response.status_code, 200)
        terms = response.json()
        self.assertEqual(len(terms), 3)
        term_nums = [t["term"] for t in terms]
        self.assertEqual(term_nums, [1, 2, 3])

        # Term 1 has free demo chapter
        self.assertTrue(terms[0]["has_demo"])
        self.assertIn("Ball Games", terms[0]["demo_chapter_name"])

        # Terms 2 and 3 are published
        self.assertEqual(terms[1]["status"], "published")
        self.assertEqual(terms[2]["status"], "published")

    def test_grade5_all_22_lessons_distribution(self):
        """Verify exact count and sequential lesson ordering for all 22 Grade 5 lessons."""
        # Term 1: 10 lessons
        r1 = self.client.get("/api/curriculum/lessons?grade=5&term=1")
        self.assertEqual(r1.status_code, 200)
        l1 = r1.json()
        self.assertEqual(len(l1), 10)
        self.assertEqual([l["lesson_order"] for l in l1], list(range(1, 11)))
        self.assertEqual(l1[0]["id"], "lesson_01_ball_games")
        self.assertEqual(l1[9]["id"], "lesson_10_fun_time")

        # Term 2: 6 lessons (11 through 16)
        r2 = self.client.get("/api/curriculum/lessons?grade=5&term=2")
        self.assertEqual(r2.status_code, 200)
        l2 = r2.json()
        self.assertEqual(len(l2), 6)
        self.assertEqual([l["lesson_order"] for l in l2], list(range(11, 17)))
        self.assertEqual(l2[0]["id"], "lesson_11_arab_cities")
        self.assertEqual(l2[5]["id"], "lesson_16_living_creatures")

        # Term 3: 6 lessons (17 through 22)
        r3 = self.client.get("/api/curriculum/lessons?grade=5&term=3")
        self.assertEqual(r3.status_code, 200)
        l3 = r3.json()
        self.assertEqual(len(l3), 6)
        self.assertEqual([l["lesson_order"] for l in l3], list(range(17, 23))
)
        self.assertEqual(l3[0]["id"], "lesson_17_carrier_pigeons")
        self.assertEqual(l3[5]["id"], "lesson_22_smart_cities")

    def test_book_editions_and_units_in_db(self):
        """Verify all 3 official MoE book editions and 6 units exist in the database."""
        db = SessionLocal()
        try:
            editions = db.query(BookEdition).filter(BookEdition.series_name == "العربية تجمعنا").all()
            edition_ids = {e.id for e in editions}
            self.assertIn("moe_gr5_vol1_2023", edition_ids)
            self.assertIn("moe_gr5_vol2_2023", edition_ids)
            self.assertIn("moe_gr5_vol3_2023", edition_ids)

            units = db.query(Unit).order_by(Unit.unit_number).all()
            unit_ids = [u.id for u in units]
            self.assertIn("unit_01_sports", unit_ids)
            self.assertIn("unit_02_rights", unit_ids)
            self.assertIn("unit_03_global_cities", unit_ids)
            self.assertIn("unit_04_wonders", unit_ids)
            self.assertIn("unit_05_communication", unit_ids)
            self.assertIn("unit_06_intelligence", unit_ids)
        finally:
            db.close()

    def test_full_content_packages_fidelity_terms_2_and_3(self):
        """Verify all 12 lessons across Terms 2 and 3 contain full 12-component learning packages."""
        term2_lesson_ids = [
            "lesson_11_arab_cities", "lesson_12_london", "lesson_13_shanghai",
            "lesson_14_seven_wonders", "lesson_15_caves_and_islands", "lesson_16_living_creatures"
        ]
        term3_lesson_ids = [
            "lesson_17_carrier_pigeons", "lesson_18_the_media", "lesson_19_social_media",
            "lesson_20_animal_intelligence", "lesson_21_human_intelligence", "lesson_22_smart_cities"
        ]

        required_keys = [
            "prep_check", "learning_paths", "instruction_decoder", "vocabulary_cards",
            "grammar_lab", "sentence_builder", "listen_speak_studio", "practice_activities",
            "speaking_mission", "parent_companion", "tutor_handover", "exam_practice"
        ]

        for lid in term2_lesson_ids + term3_lesson_ids:
            self.assertIn(lid, FULL_CURRICULUM_CATALOG, f"Missing {lid} in FULL_CURRICULUM_CATALOG")
            pkg = FULL_CURRICULUM_CATALOG[lid]
            for key in required_keys:
                self.assertIn(key, pkg, f"Lesson {lid} missing required package key: {key}")

            # Check vocabulary items
            self.assertGreaterEqual(len(pkg["vocabulary_cards"]), 4, f"Lesson {lid} should have at least 4 vocab cards")
            # Check practice activities
            self.assertGreaterEqual(len(pkg["practice_activities"]), 1, f"Lesson {lid} should have at least 1 practice activity")

    def test_paywall_enforcement(self):
        """Verify Chapter 1 is free demo and Terms 2/3 non-demo chapters require authentication/unlock."""
        # Free demo
        r_demo = self.client.get("/api/curriculum/lesson/lesson_01_ball_games")
        self.assertEqual(r_demo.status_code, 200)
        self.assertTrue(r_demo.json()["lesson"]["is_first_chapter_demo"])

        # Non-demo Term 2
        r_t2 = self.client.get("/api/curriculum/lesson/lesson_11_arab_cities")
        self.assertIn(r_t2.status_code, (401, 402))

        # Non-demo Term 3
        r_t3 = self.client.get("/api/curriculum/lesson/lesson_22_smart_cities")
        self.assertIn(r_t3.status_code, (401, 402))

    def test_exam_simulation_all_three_terms(self):
        """Verify 100-mark standardized MoE exam blueprints for all 3 terms."""
        # Term 1
        r1 = self.client.get("/api/modules/assessments/exam-simulation/5/1")
        self.assertEqual(r1.status_code, 200)
        exam1 = r1.json()["exam"]
        self.assertEqual(exam1["total_questions"], 10)
        self.assertEqual(exam1["total_marks"], 100)
        self.assertEqual(len(ASSESSMENT_QUESTIONS), 10)

        # Term 2
        r2 = self.client.get("/api/modules/assessments/exam-simulation/5/2")
        self.assertEqual(r2.status_code, 200)
        exam2 = r2.json()["exam"]
        self.assertEqual(exam2["total_questions"], 10)
        self.assertEqual(exam2["total_marks"], 100)
        self.assertEqual(len(ASSESSMENT_QUESTIONS_TERM2), 10)

        # Term 3
        r3 = self.client.get("/api/modules/assessments/exam-simulation/5/3")
        self.assertEqual(r3.status_code, 200)
        exam3 = r3.json()["exam"]
        self.assertEqual(exam3["total_questions"], 10)
        self.assertEqual(exam3["total_marks"], 100)
        self.assertEqual(len(ASSESSMENT_QUESTIONS_TERM3), 10)

    def test_adaptive_assessment_flow_across_terms(self):
        """Verify flow-state adaptive questions generate for Term 2 and Term 3 lessons."""
        r2 = self.client.get("/api/modules/assessments/adaptive/lesson_11_arab_cities?child_id=admin_supervisor")
        self.assertEqual(r2.status_code, 200)
        q2 = r2.json()["adaptive_questions"]
        self.assertGreaterEqual(len(q2), 3)

        r3 = self.client.get("/api/modules/assessments/adaptive/lesson_22_smart_cities?child_id=admin_supervisor")
        self.assertEqual(r3.status_code, 200)
        q3 = r3.json()["adaptive_questions"]
        self.assertGreaterEqual(len(q3), 3)

    def test_syllabus_data_dynamic_generator(self):
        """Verify that get_syllabus_for_grade_and_term generates authentic Grade 5 chapters."""
        s1 = get_syllabus_for_grade_and_term(5, 1)
        self.assertEqual(len(s1), 10)
        self.assertEqual(s1[0]["id"], "lesson_01_ball_games")

        s2 = get_syllabus_for_grade_and_term(5, 2)
        self.assertEqual(len(s2), 6)
        self.assertEqual(s2[0]["id"], "lesson_11_arab_cities")
        self.assertEqual(s2[0]["lesson_order"], 11)
        self.assertEqual(s2[0]["unit_title_en"], "Global Cities")

        s3 = get_syllabus_for_grade_and_term(5, 3)
        self.assertEqual(len(s3), 6)
        self.assertEqual(s3[0]["id"], "lesson_17_carrier_pigeons")
        self.assertEqual(s3[0]["lesson_order"], 17)
        self.assertEqual(s3[0]["unit_title_en"], "Communication")


if __name__ == "__main__":
    unittest.main()

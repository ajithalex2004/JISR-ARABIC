"""The exam bank: real lessons only, topped up with practice questions outside Class 5, clear message when empty."""
import hashlib
import json
import unittest
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.models import Lesson, LessonVersion, Unit
from backend.modules.assessment.exams import EXAM_QUESTION_COUNT, _exam_questions
from backend.modules.curriculum.syllabus_data import generate_dynamic_lesson_content
from backend.redis_client import cache_clear


def _mcq(qid, marks=None):
    q = {"id": qid, "type": "multiple_choice", "prompt_ar": "سُؤَالٌ", "prompt_en": "Question",
         "options": [{"id": "a", "label_ar": "أ", "label_en": "A"}, {"id": "b", "label_ar": "ب", "label_en": "B"}],
         "correct_answer": "b"}
    if marks:
        q["marks"] = marks
    return q


class TestExamBank(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
        self.db.commit()

    def tearDown(self):
        cache_clear()
        self.db.close()
        self.engine.dispose()

    def _lesson(self, lesson_id, grade, term, order, content):
        self.db.add(Lesson(id=lesson_id, unit_id="u", grade=grade, term=term, lesson_order=order, title_ar="د",
                           title_en="L", start_page=6))
        raw = json.dumps(content, ensure_ascii=False)
        self.db.add(LessonVersion(id=f"v_{lesson_id}", lesson_id=lesson_id, content_json=raw, is_active=True,
                                  status="published", content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest()))
        self.db.commit()

    def _real(self, exam_ids, practice_ids):
        return {"vocabulary_cards": [{"word_ar": "الكُرَةُ"}],
                "exam_practice": {"objective_questions": [_mcq(i, marks=2) for i in exam_ids]},
                "practice_activities": [_mcq(i) for i in practice_ids]}

    def test_short_term_is_topped_up_with_its_own_practice_questions(self):
        self._lesson("g7_t1_1", 7, 1, 1, self._real(["e1", "e2"], ["p1", "p2", "p3", "p4"]))
        self._lesson("g7_t1_2", 7, 1, 2, self._real(["e3"], ["q1", "q2", "q3", "q4"]))
        ids = [q["id"] for q in _exam_questions(7, 1, db=self.db)]
        self.assertEqual(len(ids), EXAM_QUESTION_COUNT)
        # Every exam question is used, then practice questions alternate between chapters; the exam
        # lists them in chapter order, each chapter's exam questions first.
        self.assertEqual(ids, ["g7_t1_1:e1", "g7_t1_1:e2", "g7_t1_1:p1", "g7_t1_1:p2", "g7_t1_1:p3", "g7_t1_1:p4",
                               "g7_t1_2:e3", "g7_t1_2:q1", "g7_t1_2:q2", "g7_t1_2:q3"])

    def test_every_chapter_gets_a_question(self):
        # Chapter 1 alone has enough exam questions for a whole exam; the others still appear.
        self._lesson("g7_t1_1", 7, 1, 1, self._real([f"e{i}" for i in range(12)], []))
        for order in range(2, 6):
            self._lesson(f"g7_t1_{order}", 7, 1, order, self._real([], [f"p{order}"]))
        ids = [q["id"] for q in _exam_questions(7, 1, db=self.db)]
        self.assertEqual(len(ids), EXAM_QUESTION_COUNT)
        self.assertEqual({i.split(":")[0] for i in ids}, {f"g7_t1_{o}" for o in range(1, 6)})
        self.assertEqual(sum(i.startswith("g7_t1_1:") for i in ids), 6)

    def test_class_5_term_1_covers_every_chapter(self):
        """The real Class 5 lessons: Term 1's exam has a question from each of its ten chapters."""
        from backend.curriculum_seed import seed_database
        seed_database(self.db, include_demo_data=False)
        for term, chapters in ((1, 10), (2, 6), (3, 6)):
            ids = [q["id"] for q in _exam_questions(5, term, db=self.db)]
            self.assertEqual(len(ids), EXAM_QUESTION_COUNT)
            self.assertEqual(len({i.split(":")[0] for i in ids}), chapters, f"Term {term}")

    def test_questions_carry_ten_marks_and_an_answer_key(self):
        self._lesson("g7_t1_1", 7, 1, 1, self._real([], ["p1"]))
        (q,) = _exam_questions(7, 1, db=self.db)
        self.assertEqual((q["points"], q["correct_index"], q["options"]), (10, 1, ["أ", "ب"]))

    def test_placeholder_lessons_add_no_questions(self):
        self._lesson("g7_t2_1", 7, 2, 1, self._real(["e1"], []))
        template = generate_dynamic_lesson_content(SimpleNamespace(id="g7_t2_2", grade=7, term=2, title_ar="د"))
        self._lesson("g7_t2_2", 7, 2, 2, template)
        self.assertEqual([q["id"] for q in _exam_questions(7, 2, db=self.db)], ["g7_t2_1:e1"])

    def test_coming_soon_term_gets_a_clear_message(self):
        template = generate_dynamic_lesson_content(SimpleNamespace(id="g9_t3_1", grade=9, term=3, title_ar="د"))
        self._lesson("g9_t3_1", 9, 3, 1, template)
        with self.assertRaises(ApplicationError) as ctx:
            _exam_questions(9, 3, db=self.db)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("coming soon", ctx.exception.detail)

    def test_class_5_keeps_its_curated_bank(self):
        self._lesson("g5_t1_1", 5, 1, 1, self._real(["e1"], ["p1", "p2"]))
        questions = _exam_questions(5, 1, db=self.db)
        self.assertGreaterEqual(len(questions), EXAM_QUESTION_COUNT)
        self.assertNotIn("g5_t1_1:p1", [q["id"] for q in questions])


if __name__ == "__main__":
    unittest.main()

"""The parent dashboard lists the child's own class, and a chapter is completed only when most of it is answered."""
import hashlib
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import ChildProfile, LearnerAttempt, Lesson, LessonVersion, Unit, User
from backend.modules.progress.reporting import get_parent_dashboard
from backend.redis_client import cache_clear


def _lesson(db, lesson_id, grade, term, order, title, exercises, companion=None):
    db.add(Lesson(id=lesson_id, unit_id="u", grade=grade, term=term, lesson_order=order, title_ar="د",
                  title_en=title, start_page=6, is_first_chapter_demo=(term == 1 and order == 1)))
    content = {"vocabulary_cards": [{"word_ar": "الكُرَةُ"}],
               "practice_activities": [{"id": e, "type": "choice"} for e in exercises]}
    if companion:
        content["parent_companion"] = companion
    raw = json.dumps(content, ensure_ascii=False)
    db.add(LessonVersion(id=f"v_{lesson_id}", lesson_id=lesson_id, content_json=raw, is_active=True, status="published",
                         content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest()))


class TestParentDashboardProgress(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(User(id="p", email="p@test.local", full_name="P", role="parent", password_hash="x", is_verified=True))
        self.db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
        self.db.commit()
        self.db.add(ChildProfile(id="kid", parent_id="p", name="Maya", default_grade=3))
        _lesson(self.db, "g3_t1_1", 3, 1, 1, "My Family", ["a1", "a2", "a3", "a4", "a5"], {"tip_en": "family card"})
        _lesson(self.db, "g3_t1_2", 3, 1, 2, "My School", ["b1", "b2", "b3", "b4", "b5"], {"tip_en": "school card"})
        _lesson(self.db, "g5_t1_1", 5, 1, 1, "Ball Games", ["c1"])
        self.db.commit()

    def tearDown(self):
        cache_clear()
        self.db.close()
        self.engine.dispose()

    def _answer(self, lesson_id, ids):
        for i in ids:
            self.db.add(LearnerAttempt(child_id="kid", lesson_id=lesson_id, activity_id=i, is_correct=True, score=1.0))
        self.db.commit()
        cache_clear()

    def test_lists_the_childs_own_class(self):
        cov = get_parent_dashboard("kid", db=self.db)["missing_coverage"]
        self.assertEqual(cov["grade"], 3)
        term1 = cov["terms"][0]
        self.assertEqual([l["title_en"] for l in term1["lessons"]], ["My Family", "My School"])
        self.assertNotIn("Ball Games", json.dumps(cov))
        self.assertEqual(term1["total_lessons"], 2)
        self.assertEqual(cov["completed_lessons_count"], 0)

    def test_a_chapter_is_completed_only_when_most_exercises_are_answered(self):
        self._answer("g3_t1_1", ["a1", "a2", "a3"])
        lessons = get_parent_dashboard("kid", db=self.db)["missing_coverage"]["terms"][0]["lessons"]
        self.assertEqual((lessons[0]["state"], lessons[0]["exercises_answered"], lessons[0]["exercises_total"]),
                         ("started", 3, 5))
        self._answer("g3_t1_1", ["a4"])  # 4 of 5 = 80%
        cov = get_parent_dashboard("kid", db=self.db)["missing_coverage"]
        self.assertEqual(cov["terms"][0]["lessons"][0]["state"], "completed")
        self.assertEqual(cov["completed_lessons_count"], 1)
        self.assertEqual(cov["terms"][0]["coverage_pct"], 50.0)

    def test_companion_card_follows_the_childs_latest_chapter(self):
        self.assertEqual(get_parent_dashboard("kid", db=self.db)["companion_card"], {"tip_en": "family card"})
        self._answer("g3_t1_2", ["b1"])
        self.assertEqual(get_parent_dashboard("kid", db=self.db)["companion_card"], {"tip_en": "school card"})


if __name__ == "__main__":
    unittest.main()

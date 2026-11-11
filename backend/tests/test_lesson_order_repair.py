"""Lessons imported one by one (all lesson_order 1, all free) are renumbered and only one stays free."""
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.migrations import refresh_lesson_caches, repair_lesson_order_and_free_chapters
from backend.modules.curriculum.service import list_lessons
from backend.redis_client import cache_clear, cache_get, cache_set, lesson_package_key
from backend.models import Lesson, Unit

# Production's Grade 1 Term 1: stored in this order, every one lesson_order 1 and free.
GRADE1 = [("lesson_g1_t1_ch03", 26), ("lesson_g1_t1_ch10", 96), ("lesson_g1_t1_ch09", 86), ("lesson_g1_t1_ch01", 6),
          ("lesson_g1_t1_ch02", 16)]


class TestLessonOrderRepair(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
        for lesson_id, page in GRADE1:
            self.db.add(Lesson(id=lesson_id, unit_id="u", grade=1, term=1, lesson_order=1, title_ar="د", title_en="L",
                               start_page=page, is_first_chapter_demo=True))
        for order, (lesson_id, page) in enumerate([("g5_a", 6), ("g5_b", 16)], start=1):
            self.db.add(Lesson(id=lesson_id, unit_id="u", grade=5, term=1, lesson_order=order, title_ar="د", title_en="L",
                               start_page=page, is_first_chapter_demo=(order == 1)))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_repairs_only_the_broken_class_and_is_idempotent(self):
        with self.engine.connect() as conn:
            renumbered, unfreed = repair_lesson_order_and_free_chapters(conn)
            conn.commit()
        self.assertEqual((renumbered, unfreed), (4, 4))  # ch01 already holds order 1
        self.db.expire_all()
        g1 = self.db.query(Lesson).filter(Lesson.grade == 1).order_by(Lesson.lesson_order).all()
        self.assertEqual([l.id[-4:] for l in g1], ["ch01", "ch02", "ch03", "ch09", "ch10"])
        self.assertEqual([l.id for l in g1 if l.is_first_chapter_demo], ["lesson_g1_t1_ch01"])
        g5 = {l.id: (l.lesson_order, l.is_first_chapter_demo) for l in self.db.query(Lesson).filter(Lesson.grade == 5)}
        self.assertEqual(g5, {"g5_a": (1, True), "g5_b": (2, False)})
        with self.engine.connect() as conn:
            self.assertEqual(repair_lesson_order_and_free_chapters(conn), (0, 0))

    def test_deploy_clears_cached_lists_so_a_fix_shows_at_once(self):
        cache_clear()
        list_lessons(grade=1, term=1, db=self.db)  # caches the list as it is now: all free
        cache_set(lesson_package_key("lesson_g1_t1_ch05"), {"stale": True})
        self.assertIsNotNone(cache_get("lessons_base:1:1"))
        with self.engine.connect() as conn:
            repair_lesson_order_and_free_chapters(conn)
            conn.commit()
        self.assertGreaterEqual(refresh_lesson_caches(), 2)
        self.assertIsNone(cache_get("lessons_base:1:1"))
        self.assertIsNone(cache_get(lesson_package_key("lesson_g1_t1_ch05")))
        self.db.expire_all()
        free = [l["id"] for l in list_lessons(grade=1, term=1, db=self.db) if l["is_first_chapter_demo"]]
        self.assertEqual(free, ["lesson_g1_t1_ch01"])

    def test_list_marks_free_by_the_flag_not_lesson_order_1(self):
        cache_clear()
        g5 = {l["id"]: l["is_first_chapter_demo"] for l in list_lessons(grade=5, term=1, db=self.db)}
        self.assertEqual(g5, {"g5_a": True, "g5_b": False})
        lesson = self.db.query(Lesson).filter(Lesson.id == "g5_a").one()
        lesson.is_first_chapter_demo = False  # order 1 alone no longer makes it free
        self.db.commit()
        cache_clear()
        self.assertFalse(any(l["is_first_chapter_demo"] for l in list_lessons(grade=5, term=1, db=self.db)))
        cache_clear()


if __name__ == "__main__":
    unittest.main()

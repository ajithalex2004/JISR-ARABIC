"""Re-cutting Class 1 Terms 2-3 into the book's ten lessons: staged, hidden, drafted, then switched in one step."""
import hashlib
import json
import unittest
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.migrations import repair_lesson_order_and_free_chapters
from backend.models import ChildProfile, Lesson, LessonVersion, TermAccess, Unit, User
from backend.modules.curriculum.access import require_lesson
from backend.modules.curriculum.authoring import publish_lesson_version
from backend.modules.curriculum.book_restructure import (
    RETIRED, STAGED, book_pages, promote_ready_terms, stage_book_lessons, staged_id)
from backend.modules.curriculum.drafting import chapter_pages
from backend.modules.curriculum.service import list_lessons
from backend.redis_client import cache_clear

ADMIN = SimpleNamespace(id="admin1", role="admin")
PARENT = SimpleNamespace(id="parent", role="parent", child_id=None)
CONTENT = {"title_ar": "د", "title_en": "L", "vocabulary_cards": [{"word_ar": "الأَرْنَبُ"}]}


class BookRestructureTest(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add_all([User(id="admin1", email="a@test.local", full_name="A", role="admin", password_hash="x", is_verified=True),
                         User(id="parent", email="p@test.local", full_name="P", role="parent", password_hash="x", is_verified=True),
                         Unit(id="u3", book_edition_id="b", unit_number=3, title_ar="و", title_en="U3"),
                         Unit(id="u4", book_edition_id="b", unit_number=4, title_ar="و", title_en="U4")])
        self.db.commit()
        self.db.add(ChildProfile(id="kid", parent_id="parent", name="Kid", default_grade=1))
        self.db.add(TermAccess(child_id="kid", grade=1, term=2, is_unlocked=True))
        # Today's six 15-page chapters, published.
        for order in range(1, 7):
            lid = f"lesson_g1_t2_ch0{order}"
            self.db.add(Lesson(id=lid, unit_id="u3" if order <= 3 else "u4", grade=1, term=2, lesson_order=order,
                               title_ar="د", title_en=f"Old {order}", start_page=6 + (order - 1) * 15))
            self.version(lid, f"v_{lid}", status="published", active=True)
        self.db.commit()

    def tearDown(self):
        cache_clear()
        self.db.close()
        self.engine.dispose()

    def version(self, lesson_id, vid, status="approved", active=False):
        raw = json.dumps(CONTENT, ensure_ascii=False)
        self.db.add(LessonVersion(id=vid, lesson_id=lesson_id, version_tag="1", content_json=raw, status=status,
                                  is_active=active, content_hash=hashlib.sha256(raw.encode()).hexdigest()))
        self.db.commit()

    def stage(self):
        with self.engine.connect() as conn:
            added = stage_book_lessons(conn)
            conn.commit()
        self.db.expire_all()
        return added

    def listed(self):
        cache_clear()
        return [l["title_en"] for l in list_lessons(grade=1, term=2, child_id="kid", db=self.db, actor=PARENT)]

    def test_staged_lessons_are_added_once_and_stay_hidden(self):
        self.assertEqual(self.stage(), 10)  # Term 3 has no lessons here: nothing to re-cut
        self.assertEqual(self.stage(), 0)
        staged = self.db.query(Lesson).filter_by(status=STAGED).order_by(Lesson.lesson_order).all()
        self.assertEqual([l.title_en for l in staged][:2], ["The Rabbit (أ)", "The Duck (ب)"])
        self.assertEqual({staged[0].unit_id, staged[-1].unit_id}, {"u3", "u4"})
        self.assertEqual(self.listed(), [f"Old {i}" for i in range(1, 7)])  # learners see today's chapters
        with self.assertRaises(ApplicationError) as ctx:
            require_lesson(self.db, PARENT, staged_id(1, 2, 1), child_id="kid")
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(require_lesson(self.db, ADMIN, staged_id(1, 2, 1)).id, staged_id(1, 2, 1))

    def test_drafting_uses_the_exact_book_pages(self):
        self.stage()
        rabbit = self.db.get(Lesson, staged_id(1, 2, 1))
        self.assertEqual(chapter_pages(rabbit, self.db), list(range(7, 17)))
        last = self.db.get(Lesson, staged_id(1, 2, 10))
        self.assertEqual(chapter_pages(last, self.db), list(range(87, 95)))  # stops before the appendix
        self.assertEqual(book_pages(staged_id(1, 3, 10)), list(range(79, 92)))
        # Today's chapters still end where the next of today's chapters starts, not at a staged one.
        old = self.db.get(Lesson, "lesson_g1_t2_ch01")
        self.assertEqual(chapter_pages(old, self.db), list(range(6, 20)))  # capped at 14 pages, not cut at page 7

    def test_order_repair_ignores_staged_lessons(self):
        self.stage()
        with self.engine.connect() as conn:
            self.assertEqual(repair_lesson_order_and_free_chapters(conn)[0], 0)
            conn.commit()

    def test_term_switches_only_when_every_new_chapter_is_published(self):
        self.stage()
        for order in range(1, 10):
            lid = staged_id(1, 2, order)
            self.version(lid, f"draft_{lid}")
            publish_lesson_version(lid, f"draft_{lid}", db=self.db, actor=ADMIN)
        self.db.expire_all()
        # Nine of ten published: still hidden, and still staged.
        self.assertEqual(self.listed(), [f"Old {i}" for i in range(1, 7)])
        self.assertEqual(self.db.get(Lesson, staged_id(1, 2, 9)).status, STAGED)
        last = staged_id(1, 2, 10)
        self.version(last, f"draft_{last}")
        publish_lesson_version(last, f"draft_{last}", db=self.db, actor=ADMIN)
        self.db.expire_all()
        titles = self.listed()
        self.assertEqual(len(titles), 10)
        self.assertEqual(titles[0], "The Rabbit (أ)")
        self.assertEqual(self.db.get(Lesson, "lesson_g1_t2_ch01").status, RETIRED)
        with self.assertRaises(ApplicationError):
            require_lesson(self.db, PARENT, "lesson_g1_t2_ch01", child_id="kid")
        # The new chapters open for a learner with the term unlocked.
        self.assertEqual(require_lesson(self.db, PARENT, staged_id(1, 2, 1), child_id="kid").id, staged_id(1, 2, 1))
        with self.engine.connect() as conn:
            self.assertEqual(promote_ready_terms(conn), [])  # already switched
        self.assertEqual(self.stage(), 0)  # and no second set is staged

    def review(self):
        from backend.modules.identity.access import Principal
        from backend.routes.admin import curriculum_review
        admin = Principal(id="admin1", email="a@test.local", role="admin", is_verified=True)
        self.db.expire_all()
        return {row["id"]: row for row in curriculum_review(term=2, grade=1, db=self.db, actor=admin)}

    def test_review_shows_what_each_staged_chapter_still_needs(self):
        self.stage()
        for order in range(1, 8):  # seven published
            lid = staged_id(1, 2, order)
            self.version(lid, f"draft_{lid}")
            publish_lesson_version(lid, f"draft_{lid}", db=self.db, actor=ADMIN)
        self.version(staged_id(1, 2, 8), "approved_8")                      # approved, not published
        self.version(staged_id(1, 2, 9), "pending_9", status="content_pending")  # draft waiting
        rows = self.review()                                                # chapter 10: nothing yet
        first = rows[staged_id(1, 2, 1)]
        self.assertEqual(first["status"], STAGED)
        self.assertEqual(first["version_state"], "published")
        self.assertEqual(rows[staged_id(1, 2, 8)]["version_state"], "approved")
        self.assertEqual(rows[staged_id(1, 2, 9)]["version_state"], "content_pending")
        self.assertEqual(rows[staged_id(1, 2, 10)]["version_state"], "none")
        switch = first["term_switch"]
        self.assertEqual((switch["published"], switch["total"]), (7, 10))
        self.assertEqual([w["lesson_order"] for w in switch["waiting"]], [8, 9, 10])
        self.assertIsNone(rows["lesson_g1_t2_ch01"]["term_switch"])
        # The lesson-level Publish button is refused for a staged chapter, with a reason.
        from fastapi import HTTPException
        from backend.modules.identity.access import Principal
        from backend.routes.admin import update_curriculum_status
        admin = Principal(id="admin1", email="a@test.local", role="admin", is_verified=True)
        with self.assertRaises(HTTPException) as ctx:
            update_curriculum_status(staged_id(1, 2, 1), "published", db=self.db, actor=admin)
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertIn("goes live when every new chapter", ctx.exception.detail)

    def test_review_switches_a_term_whose_chapters_were_all_published_another_way(self):
        self.stage()
        for order in range(1, 11):  # published versions that bypassed the publish step (e.g. a rollback)
            self.version(staged_id(1, 2, order), f"live_{order}", status="published", active=True)
        rows = self.review()
        self.assertEqual(rows[staged_id(1, 2, 1)]["status"], "published")
        self.assertEqual(rows["lesson_g1_t2_ch01"]["status"], RETIRED)
        self.assertEqual(len(self.listed()), 10)


if __name__ == "__main__":
    unittest.main()

"""Placeholder lessons (generic template content) are listed as "Coming soon", don't open and aren't sold."""
import hashlib
import json
import unittest
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.models import ChildProfile, Lesson, LessonVersion, TermAccess, Unit, User
from backend.modules.billing import subscriptions
from backend.modules.curriculum.access import require_lesson
from backend.modules.curriculum.coming_soon import coming_soon_ids, is_placeholder_content
from backend.modules.curriculum.service import list_lessons, list_terms
from backend.modules.curriculum.syllabus_data import generate_dynamic_lesson_content
from backend.redis_client import cache_clear

ADMIN = SimpleNamespace(role="admin", id="admin")
PARENT = SimpleNamespace(role="parent", id="parent", child_id=None)


def _version(db, lesson_id, content):
    raw = json.dumps(content, ensure_ascii=False)
    db.add(LessonVersion(id=f"v_{lesson_id}", lesson_id=lesson_id, content_json=raw,
                         content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(), is_active=True, status="published"))


class TestComingSoon(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(User(id="parent", email="p@test.local", full_name="P", role="parent", password_hash="x", is_verified=True))
        self.db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
        self.db.commit()
        self.db.add(ChildProfile(id="kid", parent_id="parent", name="Kid", default_grade=7))
        # Class 7: Term 1 is real; Term 2 has a published placeholder and a lesson with no version at all.
        lessons = [("g7_t1_a", 1, True), ("g7_t2_a", 2, False), ("g7_t2_b", 2, False)]
        for i, (lesson_id, term, free) in enumerate(lessons):
            self.db.add(Lesson(id=lesson_id, unit_id="u", grade=7, term=term, lesson_order=i + 1, title_ar="د",
                               title_en="L", start_page=6, is_first_chapter_demo=free))
        self.db.commit()
        _version(self.db, "g7_t1_a", {"vocabulary_cards": [{"word_ar": "الكُرَةُ"}]})
        template = generate_dynamic_lesson_content(SimpleNamespace(id="g7_t2_a", grade=7, term=2, title_ar="د"))
        _version(self.db, "g7_t2_a", template)
        self.db.commit()

    def tearDown(self):
        cache_clear()
        self.db.close()
        self.engine.dispose()

    def test_the_template_is_recognised(self):
        template = generate_dynamic_lesson_content(SimpleNamespace(id="x", grade=11, term=1, title_ar="د"))
        self.assertTrue(is_placeholder_content(template))
        self.assertFalse(is_placeholder_content({"vocabulary_cards": [{"word_ar": "التَّعَاوُنُ"}]}))
        self.assertEqual(coming_soon_ids(self.db, ["g7_t1_a", "g7_t2_a", "g7_t2_b"]), {"g7_t2_a", "g7_t2_b"})

    def test_learners_see_coming_soon_and_admins_see_the_lesson(self):
        term2 = list_lessons(grade=7, term=2, child_id="kid", db=self.db, actor=PARENT)
        self.assertTrue(all(l["status"] == "coming_soon" and l["lock_reason"] == "Coming soon"
                            and not l["is_accessible"] and not l["is_first_chapter_demo"] for l in term2))
        # Even after paying for the term, a placeholder does not open.
        self.db.add(TermAccess(child_id="kid", grade=7, term=2, is_unlocked=True))
        self.db.commit()
        self.assertFalse(any(l["is_accessible"] for l in list_lessons(grade=7, term=2, child_id="kid", db=self.db, actor=PARENT)))
        term1 = list_lessons(grade=7, term=1, child_id="kid", db=self.db, actor=PARENT)
        self.assertEqual([(l["status"], l["is_accessible"]) for l in term1], [("published", True)])
        admin = list_lessons(grade=7, term=2, db=self.db, actor=ADMIN)
        self.assertTrue(all(l["is_accessible"] and l["coming_soon"] for l in admin))

    def test_placeholders_do_not_open_for_learners(self):
        with self.assertRaises(ApplicationError) as ctx:
            require_lesson(self.db, PARENT, "g7_t2_a", child_id="kid")
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("coming soon", ctx.exception.detail)
        self.assertEqual(require_lesson(self.db, ADMIN, "g7_t2_b").id, "g7_t2_b")

    def test_terms_without_real_lessons_are_coming_soon_and_not_sold(self):
        terms = {t["term"]: t for t in list_terms(grade=7, child_id="kid", db=self.db, actor=PARENT)}
        self.assertEqual([terms[t]["status"] for t in (1, 2, 3)], ["published", "coming_soon", "coming_soon"])
        parent = self.db.get(User, "parent")
        with self.assertRaises(ApplicationError) as ctx:
            subscriptions.start_checkout(child_id="kid", grade=7, plan="term", terms=[2], term=2, promo_code="",
                                         auto_renew=False, parent=parent, db=self.db)
        self.assertEqual(ctx.exception.status_code, 409)
        with self.assertRaises(ApplicationError):
            subscriptions.start_checkout(child_id="kid", grade=7, plan="annual", terms=None, term=None, promo_code="",
                                         auto_renew=False, parent=parent, db=self.db)


if __name__ == "__main__":
    unittest.main()

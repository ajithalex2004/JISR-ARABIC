"""A teacher's review is recorded separately from approving and publishing; known content errors are fixed on deploy."""
import hashlib
import json
import unittest
from types import SimpleNamespace

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.migrations import split_review_from_publish
from backend.models import CurriculumAuditEvent, Lesson, LessonVersion, Unit, User
from backend.modules.curriculum.authoring import approve_lesson_version, mark_teacher_reviewed, publish_lesson_version
from backend.modules.curriculum.content_fixes import CONTENT_FIXES, apply_content_fixes
from backend.modules.curriculum.content_progress import content_progress
from backend.modules.curriculum.service import get_lesson_content
from backend.redis_client import cache_clear

ADMIN = SimpleNamespace(id="admin1", role="admin")
SHOP_CARD = {"word_ar": "مَتْجَرٌ", "meaning_en": "Store / Shop",
             "definition_ar": "مَكَانٌ تُبَاعُ فِيهِ المَغْنُومَاتُ وَالمَلَابِسُ.", "example_ar": "ذَهَبْتُ إِلَى المَتْجَرِ."}


def content(card=SHOP_CARD):
    return {"title_ar": "المَهَا", "title_en": "Arabian Oryx", "vocabulary_cards": [card],
            "provenance": {"source": "ai_draft", "review_required": True}}


class TestTeacherReview(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add_all([User(id="admin1", email="a@test.local", full_name="A", role="admin", password_hash="x", is_verified=True),
                         Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U")])
        self.db.commit()
        self.db.add(Lesson(id="lesson_g3_t2_ch02", unit_id="u", grade=3, term=2, lesson_order=2, title_ar="المَهَا",
                           title_en="Arabian Oryx", start_page=10))
        self.db.commit()

    def tearDown(self):
        cache_clear()
        self.db.close()
        self.engine.dispose()

    def add_version(self, vid, body, status="content_pending", active=False, ensure_ascii=False, **extra):
        raw = json.dumps(body, ensure_ascii=ensure_ascii)
        self.db.add(LessonVersion(id=vid, lesson_id="lesson_g3_t2_ch02", version_tag="ai-1", content_json=raw,
                                  content_hash=hashlib.sha256(raw.encode()).hexdigest(), status=status, is_active=active,
                                  created_by="ai-drafter", **extra))
        self.db.commit()

    def test_approve_and_publish_are_not_a_review(self):
        self.add_version("v1", content())
        approve_lesson_version("lesson_g3_t2_ch02", "v1", db=self.db, actor=ADMIN)
        publish_lesson_version("lesson_g3_t2_ch02", "v1", db=self.db, actor=ADMIN)
        v = self.db.get(LessonVersion, "v1")
        self.assertEqual((v.approved_by, v.published_by, v.reviewed_by, v.reviewed_at), ("admin1", "admin1", None, None))
        report = content_progress(self.db)["summary"]
        self.assertEqual((report["lessons_teacher_reviewed"], report["lessons_published_unreviewed"]), (0, 1))

        result = mark_teacher_reviewed("lesson_g3_t2_ch02", "v1", "Checked against pages 10-17", db=self.db, actor=ADMIN)
        self.assertEqual(result["reviewed_by"], "admin1")
        v = self.db.get(LessonVersion, "v1")
        self.assertIsNotNone(v.reviewed_at)
        self.assertEqual(v.review_note, "Checked against pages 10-17")
        self.assertEqual(self.db.query(CurriculumAuditEvent).filter_by(action="teacher_review").count(), 1)
        report = content_progress(self.db)["summary"]
        self.assertEqual((report["lessons_teacher_reviewed"], report["lessons_published_unreviewed"]), (1, 0))

    def test_old_reviewer_values_become_publish_and_approve_clicks(self):
        self.add_version("pub", content(), status="published", active=True, reviewed_by="admin1")
        self.add_version("appr", content(), status="approved", reviewed_by="admin1")
        with self.engine.connect() as conn:
            self.assertEqual(split_review_from_publish(conn), 2)
            conn.commit()
        self.db.expire_all()
        pub, appr = self.db.get(LessonVersion, "pub"), self.db.get(LessonVersion, "appr")
        self.assertEqual((pub.published_by, pub.reviewed_by), ("admin1", None))
        self.assertEqual((appr.approved_by, appr.reviewed_by), ("admin1", None))
        # A real sign-off (with reviewed_at) is left alone, and the repair runs once.
        mark_teacher_reviewed("lesson_g3_t2_ch02", "pub", db=self.db, actor=ADMIN)
        with self.engine.connect() as conn:
            self.assertEqual(split_review_from_publish(conn), 0)
        self.db.expire_all()
        self.assertEqual(self.db.get(LessonVersion, "pub").reviewed_by, "admin1")

    def check_fix(self, ensure_ascii):
        self.add_version("live", content(), status="published", active=True, ensure_ascii=ensure_ascii)
        with self.engine.connect() as conn:
            self.assertEqual(apply_content_fixes(conn), ["lesson_g3_t2_ch02"])
            conn.commit()
            self.assertEqual(apply_content_fixes(conn), [])  # the wrong word is gone: nothing more to do
        self.db.expire_all()
        live = self.db.query(LessonVersion).filter_by(lesson_id="lesson_g3_t2_ch02", is_active=True).one()
        self.assertNotEqual(live.id, "live")
        self.assertEqual((live.status, live.created_by, live.published_by, live.reviewed_by), ("published", "content-fix", "content-fix", None))
        self.assertFalse(self.db.get(LessonVersion, "live").is_active)  # kept in the history
        # The corrected lesson is what learners get, and its integrity hash checks out.
        card = get_lesson_content("lesson_g3_t2_ch02", db=self.db, actor=ADMIN)["content"]["vocabulary_cards"][0]
        self.assertEqual(card["definition_ar"], "مَكَانٌ تُبَاعُ فِيهِ البَضَائِعُ وَالمَلَابِسُ.")
        self.assertEqual(card["example_ar"], SHOP_CARD["example_ar"])
        self.assertEqual(self.db.query(CurriculumAuditEvent).filter_by(action="content_fix").count(), 1)

    def test_shop_card_fixed_as_a_new_version(self):
        self.check_fix(ensure_ascii=False)

    def test_shop_card_fixed_when_stored_with_escapes(self):
        self.check_fix(ensure_ascii=True)

    def test_fix_matches_any_vowelling(self):
        import re
        pattern = re.compile(CONTENT_FIXES[0][1])
        for word in ("المغنومات", "المَغْنُومَاتُ", "المَغْنُوماتِ"):
            self.assertTrue(pattern.search(word), word)
        self.assertFalse(pattern.search("البَضَائِعُ"))


if __name__ == "__main__":
    unittest.main()


class TestTeacherReviewEndpoint(unittest.TestCase):
    def test_only_staff_can_record_a_review(self):
        from fastapi.testclient import TestClient
        from backend.api.dependencies import get_current_user
        from backend.main import app
        from backend.modules.identity.access import Principal
        app.dependency_overrides[get_current_user] = lambda: Principal(id="p1", email="p@test.local", role="parent", is_verified=True)
        try:
            with TestClient(app) as client:
                res = client.post("/api/admin/lessons/x/versions/y/teacher-review", json={"note": ""})
            self.assertEqual(res.status_code, 403, res.text)
        finally:
            app.dependency_overrides.pop(get_current_user, None)

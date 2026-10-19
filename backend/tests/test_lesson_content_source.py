"""Lessons tell the truth about their content: teacher-published, or auto-generated and unreviewed."""
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import BookEdition, Lesson, LessonVersion, Unit
from backend.modules.curriculum.service import get_lesson_content
from backend.modules.identity.access import Principal
from backend.redis_client import cache_delete, cache_set, lesson_package_key


class TestLessonContentSource(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(BookEdition(id="moe_gr7_vol2_2023", title="G7T2", total_pages=10))
        self.db.add(Unit(id="src_u", book_edition_id="moe_gr7_vol2_2023", unit_number=1, title_ar="و", title_en="U"))
        self.db.commit()
        for lid in ("src_generated", "src_draft", "src_published"):
            self.db.add(Lesson(id=lid, unit_id="src_u", grade=7, term=2, lesson_order=1, title_ar="د", title_en="L",
                               start_page=1))
            cache_delete(lesson_package_key(lid))
        self.db.commit()
        published = json.dumps({"vocabulary_cards": [], "note": "teacher version"})
        self.db.add_all([
            # An active draft that never went through approval/publishing must not reach students.
            LessonVersion(id="v_draft", lesson_id="src_draft", content_json=json.dumps({"note": "unreviewed draft"}),
                          content_hash="x" * 10, is_active=True, status="content_pending"),
            LessonVersion(id="v_pub", lesson_id="src_published", content_json=published,
                          content_hash="y" * 10, is_active=True, status="published"),
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def fetch(self, lesson_id):
        # An admin opens any lesson, so access rules don't get in the way of what's being tested.
        admin = Principal(id="admin1", email="admin@example.org", role="admin", is_verified=True)
        return get_lesson_content(lesson_id, db=self.db, actor=admin)

    def test_no_published_version_is_labelled_auto_generated(self):
        pkg = self.fetch("src_generated")
        self.assertEqual(pkg["content_source"], "auto_generated")
        self.assertNotIn("verified", pkg["version_tag"])

    def test_unpublished_draft_is_never_served(self):
        pkg = self.fetch("src_draft")
        self.assertEqual(pkg["content_source"], "auto_generated")
        self.assertNotEqual(pkg["content"].get("note"), "unreviewed draft")

    def test_packages_cached_by_older_code_are_ignored(self):
        # An old-format package (no content_source) under the previous key must not be served.
        cache_set("lesson_package:src_generated", {"lesson": {}, "version_tag": "v1.0.0-moe-verified", "content": {}}, ttl_seconds=60)
        self.assertEqual(self.fetch("src_generated")["content_source"], "auto_generated")

    def test_published_version_is_served_as_published(self):
        pkg = self.fetch("src_published")
        self.assertEqual(pkg["content_source"], "published")
        self.assertEqual(pkg["content"]["note"], "teacher version")


if __name__ == "__main__":
    unittest.main()

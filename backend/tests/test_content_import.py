import json
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import content_import
from backend.database import Base
from backend.models import LessonVersion
from backend.redis_client import cache_get, cache_set, lesson_package_key


class TestContentImport(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def test_import_refreshes_lessons_and_clears_their_cache(self):
        cache_set(lesson_package_key("lesson_02_horse_riding"), {"stale": True}, ttl_seconds=600)
        cache_set("lessons_base:5:1", ["stale"], ttl_seconds=600)
        with patch.object(content_import, "SessionLocal", self.Session), patch("builtins.print") as printed:
            content_import.main()
        self.assertIsNone(cache_get(lesson_package_key("lesson_02_horse_riding")))
        self.assertIsNone(cache_get("lessons_base:5:1"))
        self.assertIn("cache cleared for", printed.call_args.args[0])

        db = self.Session()
        try:
            version = db.query(LessonVersion).filter(LessonVersion.id == "ver_lesson_02_horse_riding_020").one()
            cards = json.loads(version.content_json)["vocabulary_cards"]
        finally:
            db.close()
        million = next(c for c in cards if c["meaning_en"].startswith("One Million"))
        self.assertEqual(million["root"], "")
        self.assertIn("Italian", million["root_note_en"])


if __name__ == "__main__":
    unittest.main()

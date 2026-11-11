"""The admin quality report flags repeated activity ids, not option ids repeated across questions."""
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import Lesson, LessonVersion, Unit
from backend.modules.curriculum.authoring import get_quality_report


def _question(qid):
    return {"id": qid, "question_ar": "مَا هَذَا؟", "question_en": "What is this?",
            "options": [{"id": "a", "text_ar": "كُرَةٌ", "text_en": "a ball"},
                        {"id": "b", "text_ar": "قَلَمٌ", "text_en": "a pen"}]}


class TestQualityReportIds(unittest.TestCase):
    def test_option_ids_are_not_duplicates_but_repeated_activity_ids_are(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        db = sessionmaker(bind=engine)()
        db.add(Unit(id="u1", book_edition_id="moe_gr5_vol1_2023", unit_number=1, title_ar="وحدة", title_en="Unit"))
        db.add(Lesson(id="l1", unit_id="u1", lesson_order=1, title_ar="الكُرَةُ", title_en="Ball", start_page=6))
        content = {"quiz": [_question("q1"), _question("q2"), _question("q2")]}
        db.add(LessonVersion(id="v1", lesson_id="l1", content_json=json.dumps(content, ensure_ascii=False),
                             content_hash="x", is_active=True))
        db.commit()
        dupes = [i["activity_id"] for i in get_quality_report(db=db)["issues"] if i["type"] == "duplicate_activity_id"]
        self.assertEqual(dupes, ["q2"])
        db.close()
        engine.dispose()


if __name__ == "__main__":
    unittest.main()

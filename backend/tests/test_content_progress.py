"""Admin > Content shows, per grade and term, how far each textbook is from learners."""
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import BookEdition, Lesson, LessonVersion, ScannedPage, Unit
from backend.modules.curriculum.content_progress import content_progress


class TestContentProgress(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        db = self.db
        db.add_all([BookEdition(id="moe_gr1_vol1_2023", title="G1T1", total_pages=3),
                    BookEdition(id="moe_gr2_vol1_2023", title="G2T1", total_pages=10)])
        db.add(Unit(id="u1", book_edition_id="moe_gr1_vol1_2023", unit_number=1, title_ar="و", title_en="U"))
        db.commit()
        db.add_all([ScannedPage(book_edition_id="moe_gr1_vol1_2023", pdf_page=p, printed_page=p, ocr_text_ar="نص",
                                review_status="ai_ocr") for p in (1, 2, 3)])
        db.add(ScannedPage(book_edition_id="moe_gr2_vol1_2023", pdf_page=1, printed_page=1, ocr_text_ar="نص", review_status="ai_ocr"))
        db.add(ScannedPage(book_edition_id="moe_gr2_vol1_2023", pdf_page=2, printed_page=2, ocr_text_ar="", review_status="extraction_failed"))
        for order in (1, 2, 3):
            db.add(Lesson(id=f"l{order}", unit_id="u1", grade=1, term=1, lesson_order=order, title_ar="د", title_en="L", start_page=order))
        db.commit()
        db.add_all([
            LessonVersion(id="v1", lesson_id="l1", content_json="{}", content_hash="h1", status="published"),
            LessonVersion(id="v2", lesson_id="l2", content_json="{}", content_hash="h2", status="content_pending"),
            LessonVersion(id="v3", lesson_id="l3", content_json="{}", content_hash="h3", status="superseded"),
        ])
        db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_stages_and_counts(self):
        report = content_progress(self.db)
        cells = {(c["grade"], c["term"]): c for row in report["grades"] for c in row["terms"]}
        self.assertEqual(len(cells), 36)
        g1 = cells[(1, 1)]
        self.assertEqual((g1["stage"], g1["pages_read"]), ("in_review", 3))
        self.assertEqual(g1["lessons"], {"total": 3, "published": 1, "in_review": 1, "not_started": 1, "auto_generated": 2})
        g2 = cells[(2, 1)]
        self.assertEqual((g2["stage"], g2["pages_read"], g2["pages_failed"], g2["total_pages"]), ("reading", 1, 1, 10))
        self.assertEqual(cells[(3, 1)]["stage"], "no_book")
        self.assertEqual(report["summary"]["lessons_published"], 1)
        # Lessons without a published version reach students as auto-generated content.
        self.assertEqual(report["summary"]["lessons_auto_generated"], 2)
        self.assertEqual(report["summary"]["no_book"], 34)


if __name__ == "__main__":
    unittest.main()

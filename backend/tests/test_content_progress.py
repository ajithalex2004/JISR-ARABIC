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
        self.assertEqual(g1["lessons"], {"total": 3, "published": 1, "in_review": 1, "not_started": 1, "auto_generated": 2,
                                         "from_book": 0, "ai_drafts": 0})
        # Pages were read, so every lesson not yet drafted from them can be.
        self.assertEqual(g1["draft_lesson_ids"], ["l1", "l2", "l3"])
        g2 = cells[(2, 1)]
        self.assertEqual((g2["stage"], g2["pages_read"], g2["pages_failed"], g2["total_pages"]), ("reading", 1, 1, 10))
        self.assertEqual(cells[(3, 1)]["stage"], "no_book")
        self.assertEqual(report["summary"]["lessons_published"], 1)
        # Lessons without a published version reach students as auto-generated content.
        self.assertEqual(report["summary"]["lessons_auto_generated"], 2)
        self.assertEqual(report["summary"]["no_book"], 30)
        self.assertEqual(report["summary"]["pages_failed"], 1)

    def test_published_without_reading_the_book_is_flagged(self):
        db = self.db
        db.add(Unit(id="u3", book_edition_id="moe_gr3_vol1_2023", unit_number=1, title_ar="و", title_en="U"))
        db.add(Lesson(id="g3", unit_id="u3", grade=3, term=1, lesson_order=1, title_ar="د", title_en="L", start_page=1))
        db.add(LessonVersion(id="v4", lesson_id="l2", content_json="{}", content_hash="h4", status="published"))
        db.add(LessonVersion(id="v5", lesson_id="l3", content_json="{}", content_hash="h5", status="published"))
        db.add(LessonVersion(id="v6", lesson_id="g3", content_json="{}", content_hash="h6", status="published"))
        db.commit()
        report = content_progress(db)
        cells = {(c["grade"], c["term"]): c for row in report["grades"] for c in row["terms"]}
        # Grade 1 Term 1's pages were read, but its published lessons were not drafted from them.
        self.assertEqual(cells[(1, 1)]["stage"], "published_unsourced")
        # Grade 3 Term 1 has no book and no pages read: nothing can be drafted yet.
        self.assertEqual((cells[(3, 1)]["stage"], cells[(3, 1)]["book_read"]), ("published_unsourced", False))
        self.assertEqual(cells[(3, 1)]["draft_lesson_ids"], [])
        self.assertIn("Grade 3 Term 1", report["summary"]["books_missing_list"])
        self.assertEqual(report["summary"]["published_unsourced"], 2)

    def test_lessons_drafted_from_the_book(self):
        db = self.db
        # l1: an AI draft from the book, published. l2: an AI draft awaiting review. l3: still from the syllabus.
        db.add(LessonVersion(id="b1", lesson_id="l1", content_json='{"provenance": {"source_pdf_pages": [1]}}',
                             content_hash="b1", status="published"))
        db.query(LessonVersion).filter(LessonVersion.id == "v2").update({"created_by": "ai-drafter"})
        db.commit()
        cells = {(c["grade"], c["term"]): c for row in content_progress(db)["grades"] for c in row["terms"]}
        g1 = cells[(1, 1)]
        self.assertEqual((g1["lessons"]["from_book"], g1["lessons"]["ai_drafts"]), (1, 1))
        self.assertEqual(g1["draft_lesson_ids"], ["l3"])
        for lesson_id, h in (("l2", "p2"), ("l3", "p3")):
            db.add(LessonVersion(id=h, lesson_id=lesson_id, content_hash=h, status="published", created_by="ai-drafter",
                                 content_json="{}"))
        db.commit()
        cells = {(c["grade"], c["term"]): c for row in content_progress(db)["grades"] for c in row["terms"]}
        self.assertEqual(cells[(1, 1)]["stage"], "published")

    def test_curated_reader_pages_count_as_read(self):
        cells = {(c["grade"], c["term"]): c for row in content_progress(self.db)["grades"] for c in row["terms"]}
        g5 = cells[(5, 1)]
        self.assertTrue(g5["book_read"])
        self.assertGreater(g5["pages_curated"], 0)
        self.assertFalse(cells[(5, 2)]["book_read"])


if __name__ == "__main__":
    unittest.main()

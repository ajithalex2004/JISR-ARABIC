"""Page text split into isolated letters (a broken PDF text layer) is read again from the page image,
flagged for admins, and never shown to learners."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import BookEdition, ScannedPage
from backend.modules.curriculum.page_ocr import FRAGMENTED_STATUS, has_usable_text, is_fragmented
from backend.tasks import handlers

# The start of Class 5 Term 1, PDF page 14 as the PDF's text layer gave it ("أثمر تدريبي..." in letters).
BROKEN = ("ت داَ رْ فُ ري مْ ثُ أ ِ ةَ ورُّ الصِ وارِ جِ ها بُ بُ كْتَ أَّ مُ ثِّ صَّ في النِ داتَ فْرُ مْ الِ نَ "
          "عُ ثَ حْ أب .ِ ةَ بِ ناسُ مْ الَ دادْ عَ الأُ أَ")
WHOLE = ("أَتَعَاوَنُ مَعَ زَمِيلِي فِي اخْتِيَارِ الإِجَابَةِ الصَّحِيحَةِ لِأُكْمِلَ الجُمَلَ الآتِيَةِ: "
         "عَدَدُ مُتَابِعِي كُرَةِ القَدَمِ حَوْلَ العَالَمِ")


class TestFragmentedTextCheck(unittest.TestCase):
    def test_letters_split_apart_are_fragmented_and_words_are_not(self):
        self.assertTrue(is_fragmented(BROKEN))
        self.assertFalse(has_usable_text(BROKEN))
        self.assertFalse(is_fragmented(WHOLE))
        self.assertTrue(has_usable_text(WHOLE))
        self.assertFalse(is_fragmented("أ ب ت"))  # too short to judge

    def test_no_hand_checked_page_counts_as_fragmented(self):
        from backend.grade8_textbook_data import GRADE_8_TEXTBOOK_PAGES_DATA
        from backend.ocr_reader import GRADE_6_TEXTBOOK_PAGES_DATA, GRADE_7_TEXTBOOK_PAGES_DATA, TEXTBOOK_PAGES_DATA
        for data in (TEXTBOOK_PAGES_DATA, GRADE_6_TEXTBOOK_PAGES_DATA, GRADE_7_TEXTBOOK_PAGES_DATA,
                     GRADE_8_TEXTBOOK_PAGES_DATA):
            for page, entry in data.items():
                self.assertFalse(is_fragmented("\n".join(entry["paragraphs"])), page)


class _FakePage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class _FakeReader:
    def __init__(self, text, count):
        self.pages = [_FakePage(text) for _ in range(count)]


class TestFragmentedPagesAreReadAgain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.content = Path(self.tmp.name)
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            db.add(BookEdition(id="moe_gr5_vol1_2023", title="G5", series_name="s", volume=1,
                               academic_year="2023-2024", total_pages=1))
            db.commit()
        self._previous_factory = handlers.get_task_session_factory()
        handlers.set_task_session_factory(self.session)
        self.pdf = self.content / "book.pdf"
        Image.new("RGB", (200, 280), "white").save(self.pdf)

    def tearDown(self):
        handlers.set_task_session_factory(self._previous_factory)
        self.engine.dispose()
        self.tmp.cleanup()

    def _run(self, text_layer, ocr_result):
        with patch.dict(os.environ, {"FAHIM_CONTENT_DIR": str(self.content)}), \
                patch("pypdf.PdfReader", return_value=_FakeReader(text_layer, 1)), \
                patch("backend.modules.curriculum.page_ocr.transcribe_page_image", return_value=ocr_result) as ocr:
            handlers.handle_process_textbook_ocr(
                {"pdf_path": str(self.pdf), "book_edition_id": "moe_gr5_vol1_2023", "start_page": 1,
                 "page_count": 0}, lambda _pct: None)
        with self.session() as db:
            page = db.query(ScannedPage).one()
            return ocr, page.review_status, page.ocr_text_ar

    def test_fragmented_text_layer_is_read_from_the_page_image(self):
        ocr, status, text = self._run(BROKEN, WHOLE)
        self.assertEqual(ocr.call_count, 1)
        self.assertEqual((status, text), ("ai_ocr", WHOLE))

    def test_whole_word_text_layer_is_kept(self):
        ocr, status, text = self._run(WHOLE, None)
        self.assertEqual(ocr.call_count, 0)
        self.assertEqual((status, text), ("automatic_extracted", WHOLE))

    def test_fragmented_ocr_is_flagged_and_read_again_next_time(self):
        _, status, _ = self._run(BROKEN, BROKEN)
        self.assertEqual(status, FRAGMENTED_STATUS)
        ocr, status, text = self._run(BROKEN, WHOLE)  # same PDF: resumes, but this page is redone
        self.assertEqual(ocr.call_count, 1)
        self.assertEqual((status, text), ("ai_ocr", WHOLE))

    def test_page_read_earlier_with_fragmented_text_is_redone(self):
        self._run(WHOLE, None)
        with self.session() as db:
            db.query(ScannedPage).one().ocr_text_ar = BROKEN  # stored by an earlier, unchecked read
            db.commit()
        ocr, status, text = self._run(BROKEN, WHOLE)
        self.assertEqual(ocr.call_count, 1)
        self.assertEqual((status, text), ("ai_ocr", WHOLE))


class TestLearnersNeverSeeFragmentedText(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            for edition in ("moe_gr5_vol1_2023", "moe_gr3_vol1_2023"):
                db.add(ScannedPage(book_edition_id=edition, pdf_page=14, printed_page=14, ocr_text_ar=BROKEN,
                                   confidence=0.95, review_status="automatic_verified"))
            db.commit()

    def tearDown(self):
        self.engine.dispose()

    def _page(self, edition_id):
        from backend.modules.curriculum.authoring import get_ocr_page
        with patch("backend.database.SessionLocal", self.session), self.session() as db:
            return get_ocr_page(14, edition_id=edition_id, db=db)

    def test_hand_checked_page_replaces_fragmented_scan(self):
        from backend.ocr_reader import TEXTBOOK_PAGES_DATA
        page = self._page("moe_gr5_vol1_2023")
        self.assertEqual(page["printed_page"], TEXTBOOK_PAGES_DATA[14]["printed_page"])
        self.assertFalse(any(is_fragmented(p) for p in page["paragraphs"]))
        self.assertIn("أَتَعَاوَنُ", "\n".join(page["paragraphs"]))

    def test_page_without_a_hand_checked_copy_shows_no_fragments(self):
        page = self._page("moe_gr3_vol1_2023")
        self.assertNotIn(BROKEN[:20], "\n".join(page["paragraphs"]))
        self.assertEqual(page["review_status"], "automatic_unverified")

    def test_deploy_flags_fragmented_pages_for_admins(self):
        from backend.migrations import flag_fragmented_pages
        from backend.modules.curriculum.content_progress import content_progress
        with self.session() as db:
            db.add(ScannedPage(book_edition_id="moe_gr5_vol1_2023", pdf_page=15, printed_page=15,
                               ocr_text_ar=WHOLE, review_status="ai_ocr"))
            db.commit()
        with self.engine.connect() as conn:
            self.assertEqual(flag_fragmented_pages(conn), 2)
            conn.commit()
            self.assertEqual(flag_fragmented_pages(conn), 0)  # already flagged
        with self.session() as db:
            statuses = {(p.book_edition_id, p.pdf_page): p.review_status for p in db.query(ScannedPage)}
            self.assertEqual(statuses[("moe_gr5_vol1_2023", 14)], FRAGMENTED_STATUS)
            self.assertEqual(statuses[("moe_gr5_vol1_2023", 15)], "ai_ocr")
            cell = next(c for row in content_progress(db)["grades"] if row["grade"] == 5 for c in row["terms"]
                        if c["term"] == 1)
            self.assertEqual((cell["pages_read"], cell["pages_failed"]), (1, 1))


if __name__ == "__main__":
    unittest.main()

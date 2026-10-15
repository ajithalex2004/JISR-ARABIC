"""Scanned (image-only) textbook PDFs are read with OCR and their page images kept per edition."""
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
from backend.tasks import handlers


class TestTextbookOcr(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.content = Path(self.tmp.name)
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            db.add(BookEdition(id="moe_gr1_vol1_2023", title="G1", series_name="s", volume=1,
                               academic_year="2023-2024", total_pages=2))
            db.commit()
        self._previous_factory = handlers.get_task_session_factory()
        handlers.set_task_session_factory(self.session)
        # A two-page PDF made only of pictures, like a scanned textbook: no text layer at all.
        self.pdf = self.content / "scan.pdf"
        pages = [Image.new("RGB", (200, 280), color) for color in ("white", "lightgray")]
        pages[0].save(self.pdf, save_all=True, append_images=pages[1:])

    def tearDown(self):
        handlers.set_task_session_factory(self._previous_factory)
        self.engine.dispose()
        self.tmp.cleanup()

    def _run(self, ocr_result, start_page=1, page_count=2):
        with patch.dict(os.environ, {"FAHIM_CONTENT_DIR": str(self.content)}), \
                patch("backend.modules.curriculum.page_ocr.transcribe_page_image", return_value=ocr_result) as ocr:
            handlers.handle_process_textbook_ocr(
                {"pdf_path": str(self.pdf), "book_edition_id": "moe_gr1_vol1_2023",
                 "start_page": start_page, "page_count": page_count},
                lambda _pct: None,
            )
        return ocr

    def test_image_only_pages_are_read_with_ocr_and_images_kept_per_edition(self):
        ocr = self._run("حُرُوفُ الْهِجَاءِ: أَلِفٌ، بَاءٌ، تَاءٌ، ثَاءٌ")
        self.assertEqual(ocr.call_count, 2)
        self.assertTrue(ocr.call_args.args[0].startswith(b"\x89PNG"))
        with self.session() as db:
            pages = db.query(ScannedPage).order_by(ScannedPage.pdf_page).all()
            self.assertEqual([p.review_status for p in pages], ["ai_ocr", "ai_ocr"])
            self.assertIn("أَلِفٌ", pages[0].ocr_text_ar)
        edition_dir = self.content / "pdf_pages_sample" / "moe_gr1_vol1_2023"
        self.assertTrue((edition_dir / "page_1.png").is_file())
        self.assertTrue((edition_dir / "page_2.png").is_file())
        self.assertFalse((self.content / "pdf_pages_sample" / "page_1.png").exists())

    def test_pages_marked_failed_when_ocr_unavailable(self):
        self._run(None)
        with self.session() as db:
            self.assertEqual({p.review_status for p in db.query(ScannedPage).all()}, {"extraction_failed"})

    def test_reupload_of_same_pdf_resumes_and_new_pdf_is_redone(self):
        self._run("نَصٌّ عَرَبِيٌّ طَوِيلٌ لِلصَّفْحَةِ الْأُولَى مِنَ الْكِتَابِ")
        again = self._run("نص آخر")
        self.assertEqual(again.call_count, 0)  # nothing re-sent to OCR
        # A different PDF for the same book is processed from scratch.
        Image.new("RGB", (200, 280), "black").save(self.pdf)
        changed = self._run("نَصٌّ جَدِيدٌ لِلْكِتَابِ الْمُعَدَّلِ بَعْدَ التَّصْحِيحِ")
        self.assertEqual(changed.call_count, 1)

    def test_out_of_gemini_credits_pauses_and_reupload_continues(self):
        from backend.gemini_quota import GeminiQuotaExhausted
        text = "نَصٌّ عَرَبِيٌّ طَوِيلٌ لِلصَّفْحَةِ الْأُولَى مِنَ الْكِتَابِ"
        params = {"pdf_path": str(self.pdf), "book_edition_id": "moe_gr1_vol1_2023", "start_page": 1, "page_count": 2}
        with patch.dict(os.environ, {"FAHIM_CONTENT_DIR": str(self.content)}), \
                patch("backend.modules.curriculum.page_ocr.transcribe_page_image",
                      side_effect=[text, GeminiQuotaExhausted("Gemini's prepaid credits are used up.")]):
            result = handlers.handle_process_textbook_ocr(params, lambda _pct: None)
        self.assertEqual((result["status"], result["paused_at_page"]), ("paused", 2))
        self.assertIn("continue from page 2", result["paused_reason"])
        with self.session() as db:
            # Page 2 is left unread, not marked as failed.
            self.assertEqual([(p.pdf_page, p.review_status) for p in db.query(ScannedPage).all()], [(1, "ai_ocr")])
        again = self._run(text)
        self.assertEqual(again.call_count, 1)  # only the page it stopped at
        with self.session() as db:
            self.assertEqual(db.query(ScannedPage).filter_by(review_status="ai_ocr").count(), 2)

    def test_start_page_never_runs_past_the_last_page(self):
        self._run("نَصٌّ عَرَبِيٌّ طَوِيلٌ لِلصَّفْحَةِ الثَّانِيَةِ مِنَ الْكِتَابِ", start_page=2, page_count=None)
        with self.session() as db:
            self.assertEqual([p.pdf_page for p in db.query(ScannedPage).all()], [2])


if __name__ == "__main__":
    unittest.main()

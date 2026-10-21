"""Textbook pages whose PDF text layer comes out as loose letters are re-read from the image,
and are never shown to students in place of the page's clean text."""
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.grade8_textbook_data import GRADE_8_TEXTBOOK_PAGES_DATA
from backend.models import ScannedPage
from backend.modules.curriculum.page_ocr import has_usable_text, looks_fragmented
from backend.ocr_reader import GRADE_6_TEXTBOOK_PAGES_DATA, GRADE_7_TEXTBOOK_PAGES_DATA, TEXTBOOK_PAGES_DATA, get_page_ocr_data
from backend.tests.test_textbook_ocr import TestTextbookOcr

# What the Class 5 book's PDF text layer gave for page 14 ("Ball Games"), as stored in production.
BROKEN = "ت\nداَ\nرْ\nفُ\nري مْ\nثُ\nأ\nِ\nةَ\nورُّ\nالصِ\nوارِ\nجِ\nها بُ\nبُ\nكْتَ\nأَّ\nمُ\nثِّ\nصَّ\nفي النِ\nداتَ\nفْرُ\nمْ\nالِ\nنَ\nعُ\nثَ\nحْ\nأب\n.ِ\nةَ\nبِ\nناسُ\nمْ\nالَ\nدادْ\nعَ\nالأُ\nأَ\nرْ\nقَ\nأ\n.ً\nةَ\nحيحَ\nراءةً صِ\nقِّ\nصَّ\nت في النَ\nدَ\nرَ\nتي وّ\nالَ\nدادْ\nعَ\nالأُ\nرأْ\nقَ\nأِ\nةَ\nسَ\nنافُ\nتُ الم ْ\nقَ\nو\n”ُ\nسالْ\nرِ\nالمُ\nئِ\n“ القارَ\nةَ\nبْ\nعُ\nأ لَ\nدْ\nبَ\nنِ\nتي لَ\nموعْ\nجَ\nلَ م ِ\nداخَ\nوارْ\nالأدُ\nعِّ\nزَ\nوُ\nأ\n: ِ\nةَ\nبْ\nعُّ\nاللُ\nراقْ\n...) أوُ\nثِ\nالّ\nاني – الثّ\n– الثُ\nلَّ\n(الأوُ\nسالْ\nرِ\nالم\n.ٍ\nعِ\nتابُ\nألفًا - مليون - مليار - ألف ) م\n( ِ\nمَ\nالعالَ\nلْ\nوَ\nحِ\nمَ\nدَ\nالقِ\nةَ\nعي كُرِ\nتابُ\nمُ\nدَ\nدَ\nع\n).ٌ\nةَّ\nيِ\nماعَ\n- جٌ\nةَّ\nنائيُ\n- ثٌ\nةَّ\nيِ\nدْ\nرَ\n(فٌ\nةَ\nبْ\nعُ\nلِ\nمَ\nدَ\nالقِ\nةَ\nكُرُ\nةَ\nبْ\nعُ\nل\n).ٍ\nطيلَ\nتْ\nسُ\n- مٍ\nعَّ\nبَ\nرُ\n- مٍ\nةَ\n(دائرِ\nلْ\nلى شَك َ\nع"


class TestFragmentedText(unittest.TestCase):
    def test_loose_letters_are_detected_and_real_pages_are_not(self):
        self.assertTrue(looks_fragmented(BROKEN))
        self.assertFalse(has_usable_text(BROKEN))
        for name, data in (("gr5", TEXTBOOK_PAGES_DATA), ("gr6", GRADE_6_TEXTBOOK_PAGES_DATA),
                           ("gr7", GRADE_7_TEXTBOOK_PAGES_DATA), ("gr8", GRADE_8_TEXTBOOK_PAGES_DATA)):
            for page, content in data.items():
                with self.subTest(book=name, page=page):
                    self.assertFalse(looks_fragmented("\n".join(content.get("paragraphs", []))))
        self.assertFalse(looks_fragmented("في من"))  # too short to judge

    def test_a_fragmented_stored_page_gives_way_to_the_clean_page_text(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        with session() as db:
            db.add(ScannedPage(book_edition_id="moe_gr5_vol1_2023", pdf_page=14, printed_page=14,
                               ocr_text_ar=BROKEN, confidence=0.95, review_status="automatic_verified"))
            db.commit()
        with patch("backend.database.SessionLocal", session):
            page = get_page_ocr_data(14, "moe_gr5_vol1_2023")
        self.assertEqual(page["paragraphs"], TEXTBOOK_PAGES_DATA[14]["paragraphs"])
        self.assertFalse(any(looks_fragmented(p) for p in page["paragraphs"]))


class TestFragmentedPdfTextIsReadFromTheImage(TestTextbookOcr):
    def test_fragmented_text_layer_is_sent_to_ocr(self):
        with patch("pypdf.PageObject.extract_text", return_value=BROKEN):
            ocr = self._run("أَلْعَابُ الْكُرَةِ: كُرَةُ الْقَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ يُحِبُّهَا النَّاسُ")
        self.assertEqual(ocr.call_count, 2)
        with self.session() as db:
            self.assertEqual({p.review_status for p in db.query(ScannedPage)}, {"ai_ocr"})


del TestTextbookOcr  # run the base tests once, in their own module


if __name__ == "__main__":
    unittest.main()

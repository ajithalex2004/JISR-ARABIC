"""A PDF text layer that splits vowelled Arabic into one-letter lines is never shown as page text."""
import unittest
from unittest.mock import patch

from backend.modules.curriculum.authoring import _clean_ocr_paragraphs
from backend.modules.curriculum.page_ocr import has_usable_text, is_fragmented_text
from backend.ocr_reader import get_page_ocr_data

# What the Class 5 Term 1 PDF's text layer gave for page 14 (stored in production as page text).
FRAGMENTED = "ت\nداَ\nرْ\nفُ\nري مْ\nثُ\nأ\nِ\nةَ\nورُّ\nالصِ\nوارِ\nجِ\nها بُ\nبُ\nكْتَ\nأَّ\nمُ\nثِّ\nصَّ"
GOOD = ("أَتَعَاوَنُ مَعَ زَمِيلِي فِي اخْتِيَارِ الإِجَابَةِ الصَّحِيحَةِ\n"
        "عَدَدُ مُتَابِعِي كُرَةِ القَدَمِ حَوْلَ العَالَمِ\nكُرَةُ القَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ\n"
        "الكُرَةُ مُسْتَدِيرَةٌ\nفِي\nمِنْ\nهُنَاكَ أَنْوَاعٌ مُخْتَلِفَةٌ لِلْكُرَةِ\nالمَلْعَبُ كَبِيرٌ")


class TestFragmentedText(unittest.TestCase):
    def test_detects_letter_per_line_text_layer(self):
        self.assertTrue(is_fragmented_text(FRAGMENTED))
        self.assertFalse(has_usable_text(FRAGMENTED))  # so the reader falls back to AI OCR

    def test_normal_text_with_a_few_short_lines_is_kept(self):
        self.assertFalse(is_fragmented_text(GOOD))
        self.assertTrue(has_usable_text(GOOD))

    def test_copyright_notice_is_not_a_paragraph(self):
        notice = ("محفوظة لوزارة التربية والتعليم. لايسمح بإعادة إصدار هذه الصفحة أو جزء منها\n\n"
                  "كُرَةُ القَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ مُمْتِعَةٌ.")
        paras = _clean_ocr_paragraphs(notice, 14)
        self.assertEqual(len(paras), 1)
        self.assertIn("كُرَةُ", paras[0])

    def test_class5_page_uses_authored_text_over_a_stored_machine_read(self):
        class Page:
            ocr_text_ar = FRAGMENTED
            review_status = "automatic_extracted"
            printed_page = 14
            confidence = 0.95

        class Query:
            def filter(self, *a): return self
            def first(self): return Page()

        class Session:
            def query(self, *a): return Query()
            def close(self): pass

        with patch("backend.database.SessionLocal", return_value=Session()):
            data = get_page_ocr_data(14, "moe_gr5_vol1_2023")
        self.assertEqual(data["title_en"], "After Reading - Discussion & Comprehension")
        self.assertFalse(any(is_fragmented_text(p) for p in data["paragraphs"]))
        self.assertTrue(data["paragraphs_en"][0].startswith("I collaborate"))


if __name__ == "__main__":
    unittest.main()

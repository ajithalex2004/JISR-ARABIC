"""Textbook reader keeps the page's line structure: one card per word, word / meaning / example."""
import unittest
from unittest.mock import patch

from backend.modules.curriculum import authoring
from backend.modules.curriculum.authoring import _clean_ocr_paragraphs, translate_paragraph, translate_paragraphs

WORD_CARDS = """قاموسي
الإنسان:
الكائن الحيّ المفكّر.
مثال: لكلّ إنسانٍ اسمٌ.
طعام: كلّ ما يُؤكل.
مثال: الاعتدال في الطّعام مهمّ.
يؤثّر
يقنع ويميل.
مثال: الإعلان الجيد يؤثر في النّاس.
9"""


class ReaderLineLayoutTest(unittest.TestCase):
    def test_each_word_card_is_its_own_paragraph_with_three_lines(self):
        self.assertEqual(_clean_ocr_paragraphs(WORD_CARDS, 9), [
            "قاموسي",
            "الإنسان:\nالكائن الحيّ المفكّر.\nمثال: لكلّ إنسانٍ اسمٌ.",
            "طعام:\nكلّ ما يُؤكل.\nمثال: الاعتدال في الطّعام مهمّ.",
            "يؤثّر\nيقنع ويميل.\nمثال: الإعلان الجيد يؤثر في النّاس.",
        ])

    def test_cards_separated_by_blank_lines(self):
        text = "الإنسان: الكائن الحي المفكر.\nمثال: لكل إنسان اسم.\n\nطعام: كل ما يؤكل.\r\nمثال: الاعتدال مهم."
        self.assertEqual(_clean_ocr_paragraphs(text, 9), [
            "الإنسان:\nالكائن الحي المفكر.\nمثال: لكل إنسان اسم.",
            "طعام:\nكل ما يؤكل.\nمثال: الاعتدال مهم.",
        ])

    def test_reading_passage_lines_that_wrap_are_joined(self):
        text = ("الدرس الأول: الماء\nكان الماء يجري في النهر وكانت الأشجار تشرب منه\n"
                "حتى جاء الصيف الحار.\nماذا حدث في الصيف؟\n1. اقرأ النص.\n2. أجب عن الأسئلة.")
        self.assertEqual(_clean_ocr_paragraphs(text, 9), [
            "الدرس الأول: الماء",
            "كان الماء يجري في النهر وكانت الأشجار تشرب منه حتى جاء الصيف الحار.",
            "ماذا حدث في الصيف؟",
            "1. اقرأ النص.",
            "2. أجب عن الأسئلة.",
        ])

    def test_translation_is_line_by_line(self):
        english = {"الإنسان:": "Human:", "الكائن الحيّ المفكّر.": "The living, thinking being.",
                   "مثال: لكلّ إنسانٍ اسمٌ.": "Example: Every human has a name."}
        with patch.object(authoring, "_translate_ar_to_en", side_effect=lambda line: english.get(line, "?")) as translate:
            card = "الإنسان:\nالكائن الحيّ المفكّر.\nمثال: لكلّ إنسانٍ اسمٌ."
            self.assertEqual(translate_paragraph(card),
                             "Human:\nThe living, thinking being.\nExample: Every human has a name.")
            self.assertEqual(translate_paragraphs(["الإنسان:", card])[0], "Human:")
            self.assertEqual(translate.call_count, 7)


if __name__ == "__main__":
    unittest.main()

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

    def test_reading_passage_keeps_printed_lines_and_numbered_items_stand_alone(self):
        text = ("الدرس الأول: الماء\nكان الماء يجري في النهر وكانت الأشجار تشرب منه\n"
                "حتى جاء الصيف الحار.\nماذا حدث في الصيف؟\n1. اقرأ النص.\n2. أجب عن الأسئلة.")
        self.assertEqual(_clean_ocr_paragraphs(text, 9), [
            "الدرس الأول: الماء",
            "كان الماء يجري في النهر وكانت الأشجار تشرب منه\nحتى جاء الصيف الحار.",
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

    def test_curated_one_line_cards_get_three_lines_in_both_languages(self):
        from backend.ocr_reader import GRADE_6_TEXTBOOK_PAGES_DATA
        source = (GRADE_6_TEXTBOOK_PAGES_DATA.get(9) or GRADE_6_TEXTBOOK_PAGES_DATA["9"])["paragraphs"][0]
        word = source.split(": ", 1)[0]
        page = authoring.get_ocr_page(9, edition_id="gr6_vol1")
        lines = page["paragraphs"][0].split("\n")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], word + ":")
        self.assertEqual(" ".join(lines), source.replace(": ", ":\n", 1).replace("\n", " "))
        self.assertTrue(lines[2].startswith("مِ"))
        self.assertEqual(page["paragraphs_en"][0].split("\n"),
                         ["Human:", "The living, thinking being.", "Example: Every human has a name."])
        self.assertEqual(page["paragraphs_en"][4].split("\n")[0], "Essential / Necessary:")

    def test_text_without_an_example_is_left_alone(self):
        page = {"paragraphs": ["أَكْمِلْ كَمَا فِي الْمِثَالِ: أَنَا أُحِبُّ.", "قرأتُ الكتاب."],
                "paragraphs_en": ["Complete as in the example: I love.", "I read the book."]}
        self.assertEqual(authoring.layout_card_lines(page), page)

    def test_arabic_numbered_items_get_their_own_lines(self):
        text = "قبل الاستماع:\n١ - أتأمل الصورة.\n٢ - أتناقش مع معلمي.\nأ- أقرأ النص. ب- أجيب عن الأسئلة."
        self.assertEqual(_clean_ocr_paragraphs(text, 19), [
            "قبل الاستماع:", "١ - أتأمل الصورة.", "٢ - أتناقش مع معلمي.", "أ- أقرأ النص.\nب- أجيب عن الأسئلة.",
        ])

    def test_inline_numbered_list_is_split_in_both_languages(self):
        page = {"paragraphs": ["قَبْلَ الِاسْتِمَاعِ: ١ - أَتَأَمَّلُ الصُّورَةَ. ٢ - أَتَنَاقَشُ فِي المَوْضُوعِ."],
                "paragraphs_en": ["Before Listening: 1 - I observe the picture. 2 - I discuss the topic."]}
        out = authoring.layout_lines(page)
        self.assertEqual(out["paragraphs"][0].split("\n"),
                         ["قَبْلَ الِاسْتِمَاعِ:", "١ - أَتَأَمَّلُ الصُّورَةَ.", "٢ - أَتَنَاقَشُ فِي المَوْضُوعِ."])
        self.assertEqual(out["paragraphs_en"][0].split("\n"),
                         ["Before Listening:", "1 - I observe the picture.", "2 - I discuss the topic."])

    def test_numbers_inside_sentences_are_not_split(self):
        page = {"paragraphs": ["تَتَكَوَّنُ المُبَارَاةُ مِنْ فَرِيقَيْنِ فِي كُلٍّ مِنْهُمَا 11 لاعِبًا، عام 2009 م."],
                "paragraphs_en": ["Two teams of 11 players, in 2009."]}
        self.assertEqual(authoring.layout_lines(page), page)


if __name__ == "__main__":
    unittest.main()

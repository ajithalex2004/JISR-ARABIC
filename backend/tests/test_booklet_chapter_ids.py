"""Every curriculum chapter id opens its own Smart Study Booklet.

Grade 5's chapter ids don't follow lesson_gX_tY_chZZ (lesson_02_horse_riding, lesson_11_arab_cities, ...).
They used to fall back to the Grade 5 "Ball Games" booklet, so the chapter selector showed Chapter 1 for
every chapter.
"""
import unittest

from backend.malazim_bank import get_malazim_booklet
from backend.modules.curriculum.syllabus_data import get_syllabus_for_grade_and_term


class TestBookletChapterIds(unittest.TestCase):
    def test_every_grade5_chapter_has_its_own_booklet(self):
        titles = {}
        for term in (1, 2, 3):
            for chapter in get_syllabus_for_grade_and_term(5, term):
                with self.subTest(chapter=chapter["id"]):
                    booklet = get_malazim_booklet(chapter["id"])
                    self.assertIsNotNone(booklet)
                    titles[chapter["id"]] = booklet.get("title_ar")
        # Distinct chapters give distinct booklets, not Chapter 1 repeated.
        self.assertEqual(len(set(titles.values())), len(titles))

    def test_horse_riding_is_not_ball_games(self):
        self.assertNotEqual(
            get_malazim_booklet("lesson_02_horse_riding").get("title_ar"),
            get_malazim_booklet("lesson_01_ball_games").get("title_ar"),
        )

    def test_structured_ids_still_resolve(self):
        for grade in (6, 7, 8):
            self.assertIsNotNone(get_malazim_booklet(f"lesson_g{grade}_t1_ch02"))

    def test_unknown_id_has_no_booklet(self):
        self.assertIsNone(get_malazim_booklet("nope_123"))


if __name__ == "__main__":
    unittest.main()

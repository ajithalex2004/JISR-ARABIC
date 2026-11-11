"""Lesson and unit titles are served with tashkeel, so their Arab-English line is not a guess."""
import re
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.migrations import vowel_stored_titles
from backend.models import Lesson, Unit
from backend.modules.curriculum.syllabus_data import get_syllabus_for_grade_and_term
from backend.modules.curriculum.title_tashkeel import TITLE_TASHKEEL, vowel_title

STRIP = re.compile(r"[ً-ْٰ]")
VOWEL = re.compile(r"[ً-ْ]")


class TestTitleTashkeel(unittest.TestCase):
    def test_vowelled_titles_keep_every_letter(self):
        for plain, vowelled in TITLE_TASHKEEL.items():
            self.assertEqual(STRIP.sub("", vowelled), plain, plain)
        self.assertEqual(vowel_title("أنا وصديقي في المدرسة"), "أَنَا وَصَدِيقِي فِي المَدْرَسَةِ")
        self.assertEqual(vowel_title("عنوان معدل"), "عنوان معدل")  # unknown titles are left alone
        self.assertIsNone(vowel_title(None))

    def test_every_syllabus_title_is_vowelled(self):
        for grade in range(1, 13):
            for term in (1, 2, 3):
                for item in get_syllabus_for_grade_and_term(grade, term):
                    for key in ("title_ar", "unit_title_ar"):
                        self.assertRegex(item[key], VOWEL, f"{grade}/{term} {key}: {item[key]}")

    def test_stored_titles_are_vowelled_once_and_edited_ones_kept(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        db = sessionmaker(bind=engine)()
        db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="الرياضات والهوايات", title_en="U"))
        db.add(Lesson(id="a", unit_id="u", lesson_order=1, title_ar="ألعاب الكرة", title_en="Ball Games", start_page=6))
        db.add(Lesson(id="b", unit_id="u", lesson_order=2, title_ar="عنوان معدل", title_en="Edited", start_page=16))
        db.commit()
        with engine.connect() as conn:
            self.assertEqual(vowel_stored_titles(conn), 2)
            conn.commit()
        db.expire_all()
        self.assertEqual(db.get(Lesson, "a").title_ar, "أَلْعَابُ الكُرَةِ")
        self.assertEqual(db.get(Lesson, "b").title_ar, "عنوان معدل")
        self.assertEqual(db.get(Unit, "u").title_ar, "الرِّيَاضَاتُ وَالهِوَايَاتُ")
        with engine.connect() as conn:
            self.assertEqual(vowel_stored_titles(conn), 0)
        db.close()
        engine.dispose()


if __name__ == "__main__":
    unittest.main()

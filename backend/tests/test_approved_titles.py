"""Teacher-approved chapter titles: the converter, validation, the deploy step and what learners see."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import CurriculumAuditEvent, Lesson, LessonVersion, Unit
from backend.modules.curriculum import approved_titles as at
from backend.modules.curriculum.service import get_lesson_content, list_lessons
from backend.modules.curriculum.syllabus_data import get_syllabus_for_grade_and_term
from backend.redis_client import cache_clear
from scripts.approved_titles_from_table import main as convert

DOC_TABLE = """### Class 3

| Term | Ch | App shows now | Textbook (Arabic) | Proposed English |
| --- | --- | --- | --- | --- |
| 1 | 1 | Tales of Courage & Patience | أول يوم في المدرسة | First Day at School |
| 1 | 2 | Cooperation is Secret to Success | صباح كل يوم | Every Morning |
| 1 | 3 | The Book is My Faithful Friend | ? (scan unclear) | ? |
"""


class ApprovedTitlesTest(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.data_file = Path(self.tmp.name) / "approved.json"
        self.data_file.write_text(json.dumps({"titles": {}}), encoding="utf-8")
        self.patch = mock.patch.object(at, "DATA_FILE", self.data_file)
        self.patch.start()
        at.approved_titles.cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(Unit(id="u3", book_edition_id="b", unit_number=1, title_ar="حكايات وقيم", title_en="Tales & Values"))
        self.db.commit()
        for order, (ar, en) in enumerate([("حِكَايَاتُ الشَّجَاعَةِ", "Tales of Courage & Patience"),
                                          ("التَّعَاوُنُ سِرُّ النَّجَاحِ", "Cooperation is Secret to Success")], start=1):
            lid = f"lesson_g3_t1_ch0{order}"
            self.db.add(Lesson(id=lid, unit_id="u3", grade=3, term=1, lesson_order=order, title_ar=ar, title_en=en,
                               start_page=order * 10, is_first_chapter_demo=order == 1))
            raw = json.dumps({"title_ar": ar, "title_en": en, "vocabulary_cards": [{"word_ar": "المَدْرَسَةُ"}]}, ensure_ascii=False)
            self.db.add(LessonVersion(id=f"v_{lid}", lesson_id=lid, content_json=raw, is_active=True, status="published",
                                      content_hash=hashlib.sha256(raw.encode()).hexdigest()))
        self.db.commit()

    def tearDown(self):
        self.patch.stop()
        at.approved_titles.cache_clear()
        cache_clear()
        self.db.close()
        self.engine.dispose()
        self.tmp.cleanup()

    def convert(self, table=DOC_TABLE, grade="3"):
        src = Path(self.tmp.name) / "table.md"
        src.write_text(table, encoding="utf-8")
        convert(["--class", grade, "--approved-by", "Teacher A", "--file", str(self.data_file), str(src)])
        at.approved_titles.cache_clear()

    def apply(self):
        with self.engine.connect() as conn:
            result = at.apply_approved_titles(conn)
            conn.commit()
        self.db.expire_all()
        cache_clear()
        return result

    def test_converter_takes_the_doc_table_and_skips_unread_titles(self):
        self.convert()
        titles = json.loads(self.data_file.read_text(encoding="utf-8"))["titles"]
        self.assertEqual(sorted(titles), ["3-1-1", "3-1-2"])  # 3-1-3 still has "?"
        self.assertEqual(titles["3-1-1"], {"title_ar": "أول يوم في المدرسة", "title_en": "First Day at School",
                                           "approved_by": "Teacher A"})

    def test_validation_refuses_bad_entries(self):
        for bad in ({"3-1": {"title_ar": "أ", "title_en": "A"}}, {"3-1-1": {"title_ar": "?", "title_en": "A"}},
                    {"3-1-1": {"title_ar": "أ"}}, {"13-1-1": {"title_ar": "أ", "title_en": "A"}},
                    {"3-1-1": {"title_ar": "أ", "title_en": "A", "colour": "red"}}):
            with self.assertRaises(ValueError):
                at.validate({"titles": bad})

    def test_deploy_step_renames_chapters_once_and_logs_each_change(self):
        self.convert()
        self.assertEqual(self.apply(), (2, 0))
        self.assertEqual(self.apply(), (0, 0))  # nothing left to change
        lesson = self.db.get(Lesson, "lesson_g3_t1_ch01")
        self.assertEqual((lesson.title_ar, lesson.title_en), ("أول يوم في المدرسة", "First Day at School"))
        events = self.db.query(CurriculumAuditEvent).filter_by(action="title_update").all()
        self.assertEqual(len(events), 2)
        detail = json.loads(events[0].details_json)
        self.assertEqual(detail["approved_by"], "Teacher A")
        self.assertIn("before", detail)

    def test_vowel_marks_added_later_do_not_count_as_a_change(self):
        self.convert()
        self.apply()
        lesson = self.db.get(Lesson, "lesson_g3_t1_ch01")
        lesson.title_ar = "أَوَّلُ يَوْمٍ فِي المَدْرَسَةِ"  # a later step vowels the approved title
        self.db.commit()
        self.assertEqual(self.apply(), (0, 0))
        self.assertEqual(self.db.get(Lesson, "lesson_g3_t1_ch01").title_ar, "أَوَّلُ يَوْمٍ فِي المَدْرَسَةِ")

    def test_unit_titles_change_when_given(self):
        data = {"titles": {"3-1-1": {"title_ar": "أول يوم في المدرسة", "title_en": "First Day at School",
                                     "unit_title_ar": "يوم جميل", "unit_title_en": "A Beautiful Day"}}}
        self.data_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        at.approved_titles.cache_clear()
        self.assertEqual(self.apply(), (1, 1))
        self.assertEqual(self.db.get(Unit, "u3").title_en, "A Beautiful Day")

    def test_learners_see_the_approved_titles(self):
        self.convert()
        self.apply()
        listed = list_lessons(grade=3, term=1, db=self.db)
        self.assertEqual([l["title_en"] for l in listed], ["First Day at School", "Every Morning"])
        pkg = get_lesson_content("lesson_g3_t1_ch01", db=self.db)
        self.assertEqual(pkg["lesson"]["title_en"], "First Day at School")
        self.assertEqual(pkg["content"]["title_en"], "First Day at School")  # lesson page header
        # The stored content is unchanged, so its integrity hash still holds.
        stored = json.loads(self.db.get(LessonVersion, "v_lesson_g3_t1_ch01").content_json)
        self.assertEqual(stored["title_en"], "Tales of Courage & Patience")

    def test_syllabus_outline_uses_approved_titles(self):
        data = {"titles": {"11-1-1": {"title_ar": "عنوان", "title_en": "Approved Title"}}}
        self.data_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        at.approved_titles.cache_clear()
        self.assertEqual(get_syllabus_for_grade_and_term(11, 1)[0]["title_en"], "Approved Title")

    def test_the_shipped_file_is_valid(self):
        self.patch.stop()
        at.approved_titles.cache_clear()
        try:
            at.validate(json.loads(at.DATA_FILE.read_text(encoding="utf-8")))
        finally:
            self.patch.start()


if __name__ == "__main__":
    unittest.main()

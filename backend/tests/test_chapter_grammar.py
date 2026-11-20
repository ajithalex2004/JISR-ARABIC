"""Mindmaps flowchart and rules tree follow the chosen chapter's own grammar."""
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.models import Lesson, LessonVersion
from backend.modules.curriculum.learning import get_chapter_grammar
from backend.modules.identity.access import Principal

ADMIN = Principal(id="a1", email="a@test.local", role="admin", is_verified=True)
GRAMMAR = {"title_ar": "مختبر القواعد", "sections": [
    {"rule_name_ar": "حُرُوفُ العَطْفِ", "rule_name_en": "Conjunctions", "explanation_en": "Connects words.",
     "examples": [{"phrase_ar": "زُرْتُ لَنْدَنَ ثُمَّ بَارِيسَ.", "translation_en": "I visited London then Paris."}]},
    {"rule_name_ar": "ظُرُوفُ المَكَانِ", "rule_name_en": "Adverbs of place", "examples": []},
]}


class TestChapterGrammar(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        for lesson_id, order, demo, content in (("lesson_12_london", 12, False, {"grammar_lab": GRAMMAR}),
                                                ("lesson_g8_t1_ch02", 2, False, {"vocabulary_cards": []})):
            grade = 5 if lesson_id.startswith("lesson_12") else 8
            self.db.add(Lesson(id=lesson_id, unit_id="u", grade=grade, term=2 if grade == 5 else 1,
                               lesson_order=order, title_ar="x", title_en="x", start_page=1, is_first_chapter_demo=demo))
            self.db.add(LessonVersion(id=f"v_{lesson_id}", lesson_id=lesson_id, content_json=json.dumps(content),
                                      content_hash="h", is_active=True, status="published"))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_rules_come_from_the_chapter(self):
        res = get_chapter_grammar("lesson_12_london", db=self.db, actor=ADMIN)
        self.assertEqual(res["source"], "chapter")
        self.assertEqual([r["titleAr"] for r in res["rules"]], ["حُرُوفُ العَطْفِ", "ظُرُوفُ المَكَانِ"])
        first = res["rules"][0]
        self.assertEqual(first["examples"][0], {"sentenceAr": "زُرْتُ لَنْدَنَ ثُمَّ بَارِيسَ.", "sentenceEn": "I visited London then Paris.",
                                                "analysisAr": "", "analysisEn": ""})
        self.assertEqual((first["ruleEn"], first["formulaAr"], first["badgeEn"]), ("Connects words.", "", "Chapter rule"))

    def test_a_chapter_without_grammar_gets_its_grades_rules(self):
        res = get_chapter_grammar("lesson_g8_t1_ch02", db=self.db, actor=ADMIN)
        self.assertEqual(res["source"], "grade")
        self.assertTrue(res["rules"])
        self.assertTrue(all(r["badgeEn"] in ("Grade 8", "Unit 1") for r in res["rules"]))

    def test_locked_chapters_stay_locked(self):
        with self.assertRaises(ApplicationError) as ctx:
            get_chapter_grammar("lesson_12_london", db=self.db, actor=None)
        self.assertIn(ctx.exception.status_code, (401, 402, 403))

    def test_every_grade5_chapter_has_its_own_grammar(self):
        """The real Grade 5 catalogue: no chapter falls back, and chapters don't all share one rule set."""
        from backend.curriculum_seed import seed_database
        seed_database(self.db, include_demo_data=False)
        lessons = self.db.query(Lesson).filter(Lesson.grade == 5).all()
        firsts = set()
        for lesson in lessons:
            res = get_chapter_grammar(lesson.id, db=self.db, actor=ADMIN)
            self.assertEqual(res["source"], "chapter", lesson.id)
            firsts.add(res["rules"][0]["titleAr"])
        self.assertGreater(len(firsts), 5)


if __name__ == "__main__":
    unittest.main()

"""The parent dashboard lists the child's own class, and a chapter is completed only when most of it is answered."""
import hashlib
import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import ChildProfile, LearnerAttempt, Lesson, LessonVersion, Unit, User
from backend.modules.progress.reporting import get_actionable_guidance, get_parent_dashboard
from backend.redis_client import cache_clear


def _lesson(db, lesson_id, grade, term, order, title, exercises, companion=None):
    db.add(Lesson(id=lesson_id, unit_id="u", grade=grade, term=term, lesson_order=order, title_ar="د",
                  title_en=title, start_page=6, is_first_chapter_demo=(term == 1 and order == 1)))
    content = {"vocabulary_cards": [{"word_ar": "الكُرَةُ"}],
               "practice_activities": [{"id": e, "type": "choice"} for e in exercises]}
    if companion:
        content["parent_companion"] = companion
    raw = json.dumps(content, ensure_ascii=False)
    db.add(LessonVersion(id=f"v_{lesson_id}", lesson_id=lesson_id, content_json=raw, is_active=True, status="published",
                         content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest()))


class TestParentDashboardProgress(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(User(id="p", email="p@test.local", full_name="P", role="parent", password_hash="x", is_verified=True))
        self.db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
        self.db.commit()
        self.db.add(ChildProfile(id="kid", parent_id="p", name="Maya", default_grade=3))
        _lesson(self.db, "g3_t1_1", 3, 1, 1, "My Family", ["a1", "a2", "a3", "a4", "a5"], {
            "tip_en": "family card",
            "dinner_table_prompts": [{"arabic": "مَنْ فِي عَائِلَتِكَ؟", "english": "Who is in your family?",
                                      "phonetic": "Man fi 'a'ilatik?"}],
            "home_practice_checklist": ["Look at a family photo and name each person in Arabic.",
                                        "Praise them for saying 'ummi' (my mother) clearly."]})
        _lesson(self.db, "g3_t1_2", 3, 1, 2, "My School", ["b1", "b2", "b3", "b4", "b5"], {"tip_en": "school card"})
        _lesson(self.db, "g5_t1_1", 5, 1, 1, "Ball Games", ["c1"])
        self.db.commit()

    def tearDown(self):
        cache_clear()
        self.db.close()
        self.engine.dispose()

    def _answer(self, lesson_id, ids):
        for i in ids:
            self.db.add(LearnerAttempt(child_id="kid", lesson_id=lesson_id, activity_id=i, is_correct=True, score=1.0))
        self.db.commit()
        cache_clear()

    def test_lists_the_childs_own_class(self):
        cov = get_parent_dashboard("kid", db=self.db)["missing_coverage"]
        self.assertEqual(cov["grade"], 3)
        term1 = cov["terms"][0]
        self.assertEqual([l["title_en"] for l in term1["lessons"]], ["My Family", "My School"])
        self.assertNotIn("Ball Games", json.dumps(cov))
        self.assertEqual(term1["total_lessons"], 2)
        self.assertEqual(cov["completed_lessons_count"], 0)

    def test_a_chapter_is_completed_only_when_most_exercises_are_answered(self):
        self._answer("g3_t1_1", ["a1", "a2", "a3"])
        lessons = get_parent_dashboard("kid", db=self.db)["missing_coverage"]["terms"][0]["lessons"]
        self.assertEqual((lessons[0]["state"], lessons[0]["exercises_answered"], lessons[0]["exercises_total"]),
                         ("started", 3, 5))
        self._answer("g3_t1_1", ["a4"])  # 4 of 5 = 80%
        cov = get_parent_dashboard("kid", db=self.db)["missing_coverage"]
        self.assertEqual(cov["terms"][0]["lessons"][0]["state"], "completed")
        self.assertEqual(cov["completed_lessons_count"], 1)
        self.assertEqual(cov["terms"][0]["coverage_pct"], 50.0)

    def test_companion_card_follows_the_childs_latest_chapter(self):
        self.assertEqual(get_parent_dashboard("kid", db=self.db)["companion_card"]["tip_en"], "family card")
        self._answer("g3_t1_2", ["b1"])
        self.assertEqual(get_parent_dashboard("kid", db=self.db)["companion_card"], {"tip_en": "school card"})


    def test_parent_tips_come_from_the_childs_own_chapters(self):
        guide = get_actionable_guidance("kid", db=self.db)
        self.assertEqual(guide.grade, 3)
        text = json.dumps(guide.model_dump(), ensure_ascii=False)
        self.assertNotIn("Ball Games", text)
        self.assertNotIn("Kurat", text)
        first = guide.guidance_items[0]
        self.assertEqual(first.topic_en, "Term 1 · Chapter 1: My Family")
        self.assertEqual(first.status, "upcoming")
        self.assertIn("Who is in your family?", first.parent_prompt_en)
        self.assertEqual(first.household_activity_en, "Look at a family photo and name each person in Arabic.")
        self.assertIn("Praise them for saying 'ummi'", first.praise_suggestion_en)
        self.assertIn("Man fi", first.phonetic_help_en)
        # The chapter with no parent guide still gets tips, from its vocabulary or title.
        self.assertEqual(guide.guidance_items[1].topic_en, "Term 1 · Chapter 2: My School")

    def test_parent_tips_follow_progress(self):
        self._answer("g3_t1_1", ["a1", "a2", "a3", "a4"])  # completed
        self._answer("g3_t1_2", ["b1"])  # started, most recent
        cache_clear()
        items = get_actionable_guidance("kid", db=self.db).guidance_items
        by_topic = {i.topic_en: i for i in items}
        self.assertEqual(by_topic["Term 1 · Chapter 2: My School"].status, "needs_reinforcement")
        self.assertIn("1 of 5 exercises", by_topic["Term 1 · Chapter 2: My School"].praise_suggestion_en)
        self.assertEqual(by_topic["Term 1 · Chapter 1: My Family"].status, "mastering")

    def test_no_tips_when_the_class_has_no_lessons(self):
        self.db.add(ChildProfile(id="kid11", parent_id="p", name="Omar", default_grade=11))
        self.db.commit()
        guide = get_actionable_guidance("kid11", db=self.db)
        self.assertEqual(guide.guidance_items, [])
        self.assertIn("Tips will appear here", guide.welcome_message_en)


    def test_each_skill_is_scored_from_its_own_exercises(self):
        raw = json.dumps({
            "vocabulary_cards": [{"word_ar": "الكُرَةُ"}],
            "prep_check": {"questions": [{"id": "p1"}, {"id": "p2"}]},
            "practice_activities": [{"id": "v1", "type": "multiple_choice", "title_en": "Word meaning check"},
                                    {"id": "r1", "type": "multiple_choice", "title_en": "Story check"}],
            "sentence_builder": {"challenges": [{"id": "s1"}]},
        }, ensure_ascii=False)
        self.db.add(Lesson(id="g3_t1_9", unit_id="u", grade=3, term=1, lesson_order=9, title_ar="د", title_en="Mixed",
                           start_page=60))
        self.db.add(LessonVersion(id="v_g3_t1_9", lesson_id="g3_t1_9", content_json=raw, is_active=True,
                                  status="published", content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest()))
        self.db.commit()
        for activity, ok in (("p1", True), ("p2", False), ("v1", True), ("r1", False), ("s1", True)):
            self.db.add(LearnerAttempt(child_id="kid", lesson_id="g3_t1_9", activity_id=activity, is_correct=ok, score=1.0))
        self.db.commit()
        cache_clear()
        skills = get_parent_dashboard("kid", db=self.db)["skills"]
        self.assertEqual((skills["instruction_understanding"]["score_pct"], skills["instruction_understanding"]["evidence_count"]), (50.0, 2))
        self.assertEqual((skills["vocabulary"]["score_pct"], skills["vocabulary"]["evidence_count"]), (100.0, 1))
        self.assertEqual((skills["reading"]["score_pct"], skills["reading"]["evidence_count"]), (0.0, 1))
        self.assertEqual((skills["sentence_building"]["score_pct"], skills["sentence_building"]["evidence_count"]), (100.0, 1))
        self.assertEqual(skills["vocabulary"]["evidence_source_en"], "1 answer to word-meaning exercises")
        # The overall accuracy (60%) is no longer copied into every skill.
        self.assertEqual(len({skills[k]["score_pct"] for k in ("instruction_understanding", "vocabulary", "reading")}), 3)


if __name__ == "__main__":
    unittest.main()

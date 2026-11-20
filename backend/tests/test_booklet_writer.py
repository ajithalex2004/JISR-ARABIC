"""AI-written Smart Study Booklets: checks, drafts, review and what learners see."""
import copy
import json
import unittest
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.malazim_bank import MALAZIM_DATA
from backend.models import BookletDraft, Lesson, LessonVersion
from backend.modules.curriculum import booklet_writer as bw
from backend.modules.curriculum.learning import _booklet_for

EXAMPLE = MALAZIM_DATA["lesson_01_ball_games"]


def good_reply(title="مُلْزَمَةُ رُكُوبِ الخَيْلِ"):
    reply = copy.deepcopy(EXAMPLE)
    reply["title_ar"] = title
    reply["title_en"] = "Horse Riding Smart Booklet"
    return reply


class FakeWriter:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []
        self.model = "fake-model"
        self.cost = 0.0

    def __call__(self, prompt):
        self.prompts.append(prompt)
        self.cost += 0.01
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        if isinstance(reply, Exception):
            raise reply
        return copy.deepcopy(reply)


class BookletWriterTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        chapters = [("lesson_01_ball_games", 1, "ألعاب الكرة", True),   # hand-written booklet
                    ("lesson_02_horse_riding", 2, "ركوب الخيل", True),
                    ("lesson_03_running", 3, "الجري", True),
                    ("lesson_04_arts", 4, "الفنون", False)]             # no published lesson yet
        for lesson_id, order, title, has_content in chapters:
            self.db.add(Lesson(id=lesson_id, unit_id="u1", grade=5, term=1, lesson_order=order,
                               title_ar=title, title_en=title, start_page=6 + order))
            if has_content:
                content = {"title_ar": title, "vocabulary_cards": [{"word_ar": "الحِصَانُ", "meaning_en": "the horse"}],
                           "tutor_handover": {"note": "not about the chapter"}}
                self.db.add(LessonVersion(id=f"v_{lesson_id}", lesson_id=lesson_id, content_json=json.dumps(content),
                                          content_hash="x", is_active=True, status="published"))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()


class TestChecks(unittest.TestCase):
    def test_the_hand_written_booklet_passes(self):
        self.assertEqual(bw.booklet_errors(copy.deepcopy(EXAMPLE)), [])

    def test_missing_tashkeel_is_caught(self):
        reply = good_reply()
        for sec in reply["study_mode"]["sections"]:
            sec["content_ar"] = "هذا نص بدون تشكيل على الإطلاق في كل الكلمات المكتوبة هنا"
        errors = bw.booklet_errors(reply)
        self.assertTrue(any("tashkeel" in e for e in errors), errors)

    def test_structure_problems_are_caught(self):
        reply = good_reply()
        reply["study_mode"]["sections"] = reply["study_mode"]["sections"][:3]
        reply["study_mode"]["sections"][0]["inline_exercise"]["options"] = ["أ", "ب"]
        reply["study_mode"]["sections"][1]["inline_exercise"]["correct_index"] = 3
        reply["quick_review_mode"]["vocabulary_flashcards"] = []
        errors = " | ".join(bw.booklet_errors(reply))
        for expected in ("at least 4 sections", "exactly 3 options", "correct_index", "vocabulary_flashcards"):
            self.assertIn(expected, errors)

    def test_shuffling_keeps_the_right_answer(self):
        lesson = SimpleNamespace(id="lesson_g8_t1_ch02", grade=8, term=1, start_page=20)
        before = [(s["inline_exercise"]["options"][s["inline_exercise"]["correct_index"]],
                   s["inline_exercise"]["options_en"][s["inline_exercise"]["correct_index"]])
                  for s in EXAMPLE["study_mode"]["sections"]]
        booklet = bw.finish_booklet(copy.deepcopy(EXAMPLE), lesson)
        after = [(s["inline_exercise"]["options"][s["inline_exercise"]["correct_index"]],
                  s["inline_exercise"]["options_en"][s["inline_exercise"]["correct_index"]])
                 for s in booklet["study_mode"]["sections"]]
        self.assertEqual(before, after)
        self.assertEqual((booklet["lesson_id"], booklet["grade"], booklet["source"]), ("lesson_g8_t1_ch02", 8, "ai"))
        self.assertEqual([s["section_id"] for s in booklet["study_mode"]["sections"]], ["sec_01", "sec_02", "sec_03", "sec_04"])


class TestWriting(BookletWriterTestCase):
    def test_writes_drafts_only_where_it_should(self):
        writer = FakeWriter(good_reply())
        result = bw.write_booklets(5, 1, db=self.db, writer=writer, actor_id="admin1")
        status = {r["lesson_id"]: (r["status"], r.get("detail")) for r in result["lessons"]}
        self.assertEqual(status["lesson_01_ball_games"], ("skipped", "hand-written booklet"))
        self.assertEqual(status["lesson_04_arts"], ("skipped", "no published lesson yet"))
        self.assertEqual(status["lesson_02_horse_riding"][0], "written")
        self.assertEqual(result["summary"], {"written": 2, "skipped": 2, "failed": 0, "cost_usd": 0.02})
        # The prompt carries the chapter's lesson but not the parts that aren't about it.
        self.assertIn("الحِصَانُ", writer.prompts[0])
        self.assertNotIn("not about the chapter", writer.prompts[0])
        # Run again: chapters with a draft are skipped unless overwrite.
        again = bw.write_booklets(5, 1, db=self.db, writer=writer)
        self.assertEqual(again["summary"]["written"], 0)
        bw.write_booklets(5, 1, db=self.db, writer=writer, lesson_ids=["lesson_02_horse_riding"], overwrite=True)
        drafts = self.db.query(BookletDraft).filter_by(lesson_id="lesson_02_horse_riding").all()
        self.assertEqual(sorted(d.status for d in drafts), ["draft", "superseded"])

    def test_a_bad_reply_is_retried_with_the_problems(self):
        bad = good_reply()
        bad["quick_review_mode"]["exam_pitfall_warnings"] = []
        writer = FakeWriter(ValueError("Expecting ','"), bad, good_reply())
        result = bw.write_booklets(5, 1, db=self.db, writer=writer, lesson_ids=["lesson_02_horse_riding"])
        self.assertEqual(result["summary"]["written"], 1)
        self.assertEqual(len(writer.prompts), 3)
        self.assertIn("not valid JSON", writer.prompts[1])
        self.assertIn("exam_pitfall_warnings", writer.prompts[2])

    def test_a_chapter_that_keeps_failing_is_reported(self):
        bad = good_reply()
        bad["study_mode"]["sections"] = []
        result = bw.write_booklets(5, 1, db=self.db, writer=FakeWriter(bad), lesson_ids=["lesson_02_horse_riding", "lesson_03_running"])
        self.assertEqual(result["summary"]["failed"], 2)
        self.assertIn("failed the checks", result["lessons"][0]["detail"])
        self.assertEqual(self.db.query(BookletDraft).count(), 0)


class TestReviewAndServing(BookletWriterTestCase):
    def _draft(self, lesson_id="lesson_02_horse_riding", title="مُلْزَمَةُ رُكُوبِ الخَيْلِ"):
        lesson = self.db.get(Lesson, lesson_id)
        return bw.write_booklet(self.db, lesson, FakeWriter(good_reply(title)), actor_id="admin1")

    def test_learners_see_a_booklet_only_once_published(self):
        generated = _booklet_for(self.db, "lesson_02_horse_riding")
        draft = self._draft()
        self.assertNotEqual(_booklet_for(self.db, "lesson_02_horse_riding").get("source"), "ai")
        bw.review_draft(self.db, draft.id, "publish", actor_id="admin1")
        served = _booklet_for(self.db, "lesson_02_horse_riding")
        self.assertEqual((served["source"], served["title_ar"]), ("ai", "مُلْزَمَةُ رُكُوبِ الخَيْلِ"))
        bw.review_draft(self.db, draft.id, "unpublish", actor_id="admin1")
        self.assertEqual(_booklet_for(self.db, "lesson_02_horse_riding"), generated)

    def test_publishing_a_new_draft_retires_the_old_one(self):
        first = self._draft()
        bw.review_draft(self.db, first.id, "publish", actor_id="a")
        second = self._draft(title="مُلْزَمَةٌ جَدِيدَةٌ")
        bw.review_draft(self.db, second.id, "publish", actor_id="a")
        self.db.refresh(first)
        self.assertEqual(first.status, "superseded")
        self.assertEqual(_booklet_for(self.db, "lesson_02_horse_riding")["title_ar"], "مُلْزَمَةٌ جَدِيدَةٌ")

    def test_hand_written_booklets_always_win(self):
        self.db.add(BookletDraft(lesson_id="lesson_01_ball_games", grade=5, term=1, status="published",
                                 booklet_json=json.dumps({"title_ar": "x"})))
        self.db.commit()
        self.assertIs(_booklet_for(self.db, "lesson_01_ball_games"), EXAMPLE)

    def test_answers_are_checked_against_the_published_booklet(self):
        from backend.modules.curriculum import learning
        draft = self._draft()
        bw.review_draft(self.db, draft.id, "publish", actor_id="a")
        booklet = json.loads(self.db.get(BookletDraft, draft.id).booklet_json)
        exercise = booklet["study_mode"]["sections"][0]["inline_exercise"]
        original = learning.require_lesson
        learning.require_lesson = lambda *a, **k: None
        try:
            payload = SimpleNamespace(child_id=None, section_id="sec_01", answer=exercise["correct_index"])
            self.assertTrue(learning.check_booklet_answer("lesson_02_horse_riding", payload, db=self.db)["is_correct"])
        finally:
            learning.require_lesson = original

    def test_review_rules(self):
        draft = self._draft()
        with self.assertRaises(ApplicationError):
            bw.review_draft(self.db, draft.id, "approve", actor_id="a")
        bw.review_draft(self.db, draft.id, "publish", actor_id="a", note="checked by teacher")
        with self.assertRaises(ApplicationError):
            bw.review_draft(self.db, draft.id, "reject", actor_id="a")
        with self.assertRaises(ApplicationError):
            bw.review_draft(self.db, "missing", "publish", actor_id="a")
        self.assertEqual(self.db.get(BookletDraft, draft.id).review_note, "checked by teacher")

    def test_overview(self):
        draft = self._draft()
        rows = {r["lesson_id"]: r for r in bw.booklet_overview(self.db, 5, 1)}
        self.assertEqual(rows["lesson_01_ball_games"]["booklet_source"], "hand_written")
        self.assertEqual(rows["lesson_02_horse_riding"]["pending_draft_id"], draft.id)
        self.assertEqual(rows["lesson_02_horse_riding"]["booklet_source"], "generated")
        self.assertFalse(rows["lesson_04_arts"]["has_lesson_content"])
        detail = bw.draft_detail(self.db, draft.id)
        self.assertEqual(detail["unvowelled_words"], [])
        self.assertEqual(detail["booklet"]["lesson_id"], "lesson_02_horse_riding")


class TestAdminRoutes(BookletWriterTestCase):
    def test_list_write_preview_publish(self):
        from unittest.mock import patch
        from fastapi.testclient import TestClient
        from backend.api.dependencies import get_current_user
        from backend.database import get_db
        from backend.main import app
        from backend.modules.identity.access import Principal

        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user] = lambda: Principal(id="admin1", email="a@test.local", role="admin", is_verified=True)
        try:
            with TestClient(app) as client:
                rows = client.get("/api/admin/booklets", params={"grade": 5, "term": 1}).json()["chapters"]
                self.assertEqual(len(rows), 4)
                with patch.dict("os.environ", {"GEMINI_API_KEY": "x"}), \
                        patch("backend.tasks.queue.enqueue_task") as enqueue:
                    enqueue.return_value = SimpleNamespace(id="t1")
                    queued = client.post("/api/admin/booklets/write", json={"grade": 5, "term": 1}).json()
                self.assertEqual(queued["task_id"], "t1")
                self.assertEqual(enqueue.call_args.kwargs["task_type"], "write_booklets")
                with patch.dict("os.environ", {"GEMINI_API_KEY": "x"}):
                    missing = client.post("/api/admin/booklets/write", json={"grade": 9, "term": 2})
                self.assertEqual(missing.status_code, 404)

                draft = bw.write_booklet(self.db, self.db.get(Lesson, "lesson_02_horse_riding"), FakeWriter(good_reply()))
                detail = client.get(f"/api/admin/booklets/drafts/{draft.id}").json()
                self.assertEqual(detail["status"], "draft")
                published = client.post(f"/api/admin/booklets/drafts/{draft.id}/publish", json={"note": "ok"}).json()
                self.assertEqual((published["status"], published["review_note"]), ("published", "ok"))
                self.assertEqual(client.post(f"/api/admin/booklets/drafts/{draft.id}/nope").status_code, 400)

            app.dependency_overrides[get_current_user] = lambda: Principal(id="p1", email="p@test.local", role="parent", is_verified=True)
            with TestClient(app) as client:
                self.assertEqual(client.get("/api/admin/booklets", params={"grade": 5, "term": 1}).status_code, 403)
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_current_user, None)


if __name__ == "__main__":
    unittest.main()

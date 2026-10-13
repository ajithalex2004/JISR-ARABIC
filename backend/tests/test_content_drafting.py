import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.curriculum_seed import BALL_GAMES_CONTENT_V02
from backend.database import Base
from backend.errors import ApplicationError
from backend.models import BookEdition, CurriculumAuditEvent, Lesson, LessonVersion, Unit, User
from backend.modules.curriculum import drafting
from backend.modules.curriculum.authoring import approve_lesson_version, publish_lesson_version


def fake_generator(calls=None, broken_lessons=(), bad_answer=False):
    """Stand-in for Gemini: returns the reference sections a group asks for."""
    def generate(prompt, images):
        if calls is not None:
            calls.append((prompt, [p.name for p in images]))
        if any(f'"{title}"' in prompt for title in broken_lessons):
            raise RuntimeError("model timeout")
        keys = prompt.split("exactly these keys: ")[1].split(".\n")[0].split(", ")
        sections = {k: copy.deepcopy(BALL_GAMES_CONTENT_V02[k]) for k in keys}
        if bad_answer and "exam_practice" in sections:
            sections["exam_practice"]["objective_questions"][0]["correct_answer"] = "zzz"
        return sections
    generate.model = "fake-model"
    return generate


class TestContentDrafting(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.db.add(User(id="admin1", email="a@t.local", full_name="A", role="admin", password_hash="x", is_verified=True))
        self.db.add(BookEdition(id="moe_gr6_vol1_2023", title="Grade 6"))
        self.db.add(Unit(id="u6", book_edition_id="moe_gr6_vol1_2023", unit_number=1, title_ar="الهوية", title_en="Identity"))
        for order, (title_ar, title_en, page) in enumerate([("أنا إماراتي", "I am Emirati", 6), ("زايد الخير", "Zayed", 16)], start=1):
            self.db.add(Lesson(id=f"lesson_g6_t1_ch0{order}", unit_id="u6", grade=6, term=1, lesson_order=order,
                               title_ar=title_ar, title_en=title_en, start_page=page, status="content_pending"))
        self.db.commit()

        self.tmp = tempfile.TemporaryDirectory()
        pages = Path(self.tmp.name) / "pdf_pages_sample" / "moe_gr6_vol1_2023"
        pages.mkdir(parents=True)
        for n in range(6, 30):
            (pages / f"page_{n}.png").write_bytes(b"png")
        self.env = patch.dict(os.environ, {"FAHIM_CONTENT_DIR": self.tmp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()
        self.db.close()

    def test_chapter_pages_run_to_next_lesson(self):
        first = self.db.get(Lesson, "lesson_g6_t1_ch01")
        last = self.db.get(Lesson, "lesson_g6_t1_ch02")
        self.assertEqual(drafting.chapter_pages(first, self.db), list(range(6, 16)))
        self.assertEqual(drafting.chapter_pages(last, self.db), list(range(16, 26)))

    def test_drafts_stored_for_review_and_pass_quality_gate(self):
        calls = []
        result = drafting.draft_lessons(6, 1, db=self.db, generate=fake_generator(calls), actor_id="admin1")
        self.assertEqual(result["summary"], {"drafted": 2, "skipped": 0, "failed": 0})
        self.assertEqual(len(calls), 2 * len(drafting.SECTION_GROUPS))
        self.assertEqual(calls[0][1][0], "page_6.png")

        version = self.db.query(LessonVersion).filter_by(lesson_id="lesson_g6_t1_ch01").one()
        self.assertEqual(version.status, "content_pending")
        self.assertFalse(version.is_active)
        self.assertEqual(version.created_by, drafting.AI_DRAFTER)
        content = json.loads(version.content_json)
        self.assertEqual(content["lesson_id"], "lesson_g6_t1_ch01")
        self.assertEqual(content["grade"], 6)
        self.assertEqual(content["unit_title_en"], "Identity")
        self.assertEqual(content["provenance"]["source_pdf_pages"], list(range(6, 16)))
        self.assertTrue(content["vocabulary_cards"][0]["id"].startswith("lesson_g6_t1_ch01_vocabulary_cards_"))
        audit = self.db.query(CurriculumAuditEvent).filter_by(action="ai_draft").count()
        self.assertEqual(audit, 2)

        # A human admin can approve and publish the AI draft.
        lesson = self.db.get(Lesson, "lesson_g6_t1_ch01")
        approve_lesson_version(lesson.id, version.id, db=self.db, actor=type("A", (), {"id": "admin1"})())
        publish_lesson_version(lesson.id, version.id, db=self.db, actor=type("A", (), {"id": "admin1"})())
        self.db.refresh(version)
        self.assertEqual(version.status, "published")
        self.assertTrue(version.is_active)

    def test_rerun_skips_pending_drafts_unless_overwrite(self):
        drafting.draft_lessons(6, 1, db=self.db, generate=fake_generator())
        again = drafting.draft_lessons(6, 1, db=self.db, generate=fake_generator())
        self.assertEqual(again["summary"]["skipped"], 2)
        replaced = drafting.draft_lessons(6, 1, db=self.db, generate=fake_generator(), lesson_ids=["lesson_g6_t1_ch01"], overwrite=True)
        self.assertEqual(replaced["summary"]["drafted"], 1)
        statuses = sorted(v.status for v in self.db.query(LessonVersion).filter_by(lesson_id="lesson_g6_t1_ch01"))
        self.assertEqual(statuses, ["content_pending", "superseded"])

    def test_one_failure_does_not_stop_the_batch(self):
        result = drafting.draft_lessons(6, 1, db=self.db, generate=fake_generator(broken_lessons=["زايد الخير"]))
        self.assertEqual(result["summary"], {"drafted": 1, "skipped": 0, "failed": 1})
        failed = [r for r in result["lessons"] if r["status"] == "failed"][0]
        self.assertIn("model timeout", failed["detail"])

    def test_invalid_answer_key_is_rejected(self):
        result = drafting.draft_lessons(6, 1, db=self.db, generate=fake_generator(bad_answer=True))
        self.assertEqual(result["summary"]["failed"], 2)
        self.assertIn("correct_answer", result["lessons"][0]["detail"])
        self.assertEqual(self.db.query(LessonVersion).count(), 0)

    def test_missing_sections_are_rejected(self):
        def incomplete(prompt, images):
            return {"vocabulary_cards": []}
        with self.assertRaises(ApplicationError) as ctx:
            drafting.draft_lesson_package(self.db.get(Lesson, "lesson_g6_t1_ch01"), self.db, generate=incomplete)
        self.assertEqual(ctx.exception.status_code, 422)

    def test_no_scans_means_no_draft(self):
        for png in (Path(self.tmp.name) / "pdf_pages_sample" / "moe_gr6_vol1_2023").glob("*.png"):
            png.unlink()
        result = drafting.draft_lessons(6, 1, db=self.db, generate=fake_generator())
        self.assertEqual(result["summary"]["failed"], 2)
        self.assertIn("No textbook page images", result["lessons"][0]["detail"])


class TestContentDraftEndpoints(unittest.TestCase):
    def test_endpoints_require_admin(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        client = TestClient(app)
        self.assertEqual(client.post("/api/admin/content-drafts", json={"grade": 6, "term": 1}).status_code, 401)
        self.assertEqual(client.get("/api/admin/lessons/x/versions").status_code, 401)
        self.assertEqual(client.get("/api/admin/lessons/x/versions/y").status_code, 401)


if __name__ == "__main__":
    unittest.main()

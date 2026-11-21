"""Basic Foundation extras: native recordings, textbook links and parent-language explanations."""
import json
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.models import FoundationTranslation, RecordedAudio
from backend.modules.curriculum import foundation, recordings
from backend.redis_client import cache_clear


class FeatureTestCase(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        cache_clear()
        self.db.close()
        self.engine.dispose()


class TestRecordings(FeatureTestCase):
    def test_a_recording_replaces_the_synthetic_voice(self):
        from backend.modules.curriculum.audio import synthesize_audio
        row = recordings.save_recording(self.db, "  بَ ", b"OggS-clip", "audio/ogg; codecs=opus", speaker="Ustadha Huda")
        self.assertEqual((row.text, row.mime_type, row.size_bytes), ("بَ", "audio/ogg", 9))
        with patch("backend.database.SessionLocal", self.Session):
            meta = synthesize_audio(text="بَ")
        self.assertFalse(meta["is_synthetic"])
        self.assertEqual(meta["status"], "ready")
        self.assertTrue(meta["audio_url"].startswith(f"/api/audio/recordings/{row.id}?v="))
        self.assertIn("Native speaker", meta["attribution"])

    def test_texts_without_a_recording_keep_the_synthetic_voice(self):
        with patch("backend.database.SessionLocal", self.Session):
            self.assertIsNone(recordings.lookup_url("بِ"))

    def test_re_recording_replaces_the_clip(self):
        first = recordings.save_recording(self.db, "بَ", b"one", "audio/webm")
        second = recordings.save_recording(self.db, "بَ", b"second take", "audio/webm")
        self.assertEqual(first.id, second.id)
        self.assertEqual(self.db.query(RecordedAudio).count(), 1)
        self.assertEqual(self.db.get(RecordedAudio, first.id).audio, b"second take")

    def test_bad_uploads_are_refused(self):
        for text, data, mime in (("", b"x", "audio/webm"), ("بَ", b"", "audio/webm"), ("بَ", b"x", "image/png"),
                                 ("بَ", b"x" * (recordings.MAX_BYTES + 1), "audio/webm")):
            with self.subTest(mime=mime, size=len(data)):
                with self.assertRaises(ApplicationError):
                    recordings.save_recording(self.db, text, data, mime)

    def test_script_status_counts_what_is_recorded(self):
        recordings.save_recording(self.db, "بَاء", b"clip", "audio/webm")
        status = recordings.script_status(self.db)
        self.assertEqual(status["recorded"], 1)
        item = next(i for i in status["items"] if i["text"] == "بَاء")
        self.assertTrue(item["url"])
        self.assertGreater(status["total"], 600)

    def test_admin_routes_and_public_playback(self):
        from fastapi.testclient import TestClient
        from backend.api.dependencies import get_current_user
        from backend.database import get_db
        from backend.main import app
        from backend.modules.identity.access import Principal
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user] = lambda: Principal(id="a1", email="a@test.local", role="admin", is_verified=True)
        try:
            with TestClient(app) as client:
                saved = client.post("/api/admin/audio-recordings", data={"text": "بَ", "speaker": "Huda"},
                                    files={"file": ("b.webm", b"WEBMDATA", "audio/webm")})
                self.assertEqual(saved.status_code, 200, saved.text)
                url = saved.json()["url"]
                played = client.get(url)
                self.assertEqual((played.status_code, played.content, played.headers["content-type"]),
                                 (200, b"WEBMDATA", "audio/webm"))
                listing = client.get("/api/admin/audio-recordings").json()
                self.assertEqual(listing["recorded"], 1)
                rid = saved.json()["recording_id"]
                self.assertEqual(client.delete(f"/api/admin/audio-recordings/{rid}").status_code, 200)
                self.assertEqual(client.get(url).status_code, 404)
            app.dependency_overrides[get_current_user] = lambda: Principal(id="p1", email="p@test.local", role="parent", is_verified=True)
            with TestClient(app) as client:
                self.assertEqual(client.get("/api/admin/audio-recordings").status_code, 403)
                self.assertEqual(client.post("/api/admin/audio-recordings", data={"text": "بَ"},
                                             files={"file": ("b.webm", b"x", "audio/webm")}).status_code, 403)
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_current_user, None)


class TestTextbookLinks(FeatureTestCase):
    def test_links_point_to_chapters_that_teach_the_rule(self):
        from backend.curriculum_seed import seed_database
        seed_database(self.db, include_demo_data=False)
        links = foundation.textbook_links(self.db, 5)
        demonstratives = [l["lesson_id"] for l in links["c3_demonstratives"]]
        self.assertIn("lesson_11_arab_cities", demonstratives)
        self.assertIn("lesson_01_ball_games", [l["lesson_id"] for l in links["c15_attached_pronouns"]])
        self.assertIn("lesson_13_shanghai", [l["lesson_id"] for l in links["c22_comparing"]])
        self.assertIn("lesson_20_animal_intelligence", [l["lesson_id"] for l in links["c21_kaana"]])
        first = links["c3_demonstratives"][0]
        self.assertTrue(first["rule"])  # shows which rule matched
        self.assertTrue(all(len(v) <= foundation.LINKS_PER_LESSON for v in links.values()))
        self.assertEqual(foundation.textbook_links(self.db, 9), {})  # no published chapters for Class 9 here


class FakeTranslator:
    def __init__(self, *replies):
        self.replies, self.calls, self.model = list(replies), 0, "fake"

    def __call__(self, prompt):
        self.calls += 1
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        if isinstance(reply, Exception):
            raise reply
        return reply


class TestParentExplanations(FeatureTestCase):
    def good(self, lesson_id="c3_demonstratives"):
        from backend.foundation_data import get_lesson
        lesson = get_lesson(lesson_id)
        return {"title": "इशारा शब्द", "summary": "सारांश", "points": [f"बिंदु {i}" for i in range(len(lesson["points"]))],
                "examples": [f"उदाहरण {i}" for i in range(len(lesson["examples"]))]}

    def test_translates_once_then_serves_the_saved_copy(self):
        translator = FakeTranslator(self.good())
        first = foundation.parent_explanation(self.db, "c3_demonstratives", "hi", translator)
        self.assertEqual((first["language"], first["dir"], first["summary"]), ("Hindi", "ltr", "सारांश"))
        self.assertTrue(first["machine_translated"])
        self.assertEqual(len(first["example_arabic"]), len(first["examples"]))
        again = foundation.parent_explanation(self.db, "c3_demonstratives", "hi", FakeTranslator(ValueError("unused")))
        self.assertEqual(again["summary"], "सारांश")
        self.assertEqual(translator.calls, 1)
        self.assertEqual(self.db.query(FoundationTranslation).count(), 1)

    def test_retries_a_bad_reply_and_reports_a_failure(self):
        bad = {"summary": "x", "points": ["only one"], "examples": []}
        translator = FakeTranslator(bad, self.good())
        self.assertEqual(foundation.parent_explanation(self.db, "c3_demonstratives", "ur", translator)["dir"], "rtl")
        with self.assertRaises(ApplicationError) as ctx:
            foundation.parent_explanation(self.db, "c4_pronouns", "ml", FakeTranslator(bad))
        self.assertEqual(ctx.exception.status_code, 502)

    def test_unknown_language_or_lesson(self):
        with self.assertRaises(ApplicationError):
            foundation.parent_explanation(self.db, "c3_demonstratives", "fr", FakeTranslator(self.good()))
        with self.assertRaises(ApplicationError):
            foundation.parent_explanation(self.db, "zz_missing", "hi", FakeTranslator(self.good()))

    def test_prompt_keeps_the_arabic(self):
        from backend.foundation_data import get_lesson
        lesson = get_lesson("c3_demonstratives")
        prompt = foundation._prompt(lesson, foundation._source(lesson), "ml")
        self.assertIn("Malayalam", prompt)
        self.assertIn("هَذَا", prompt)


if __name__ == "__main__":
    unittest.main()

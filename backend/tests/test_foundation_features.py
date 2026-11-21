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
    def good(self, lesson_id="c3_demonstratives", lang="hi"):
        from backend.foundation_data import get_lesson
        lesson = get_lesson(lesson_id)
        word = {"hi": ("सारांश", "बिंदु", "उदाहरण"), "ml": ("സംഗ്രഹം", "പോയിന്റ്", "ഉദാഹരണം"),
                "ur": ("خلاصہ", "نکتہ", "مثال ہے")}[lang]
        return {"title": word[0], "summary": word[0], "points": [f"{word[1]} {i}" for i in range(len(lesson["points"]))],
                "examples": [f"{word[2]} {i}" for i in range(len(lesson["examples"]))]}

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
        translator = FakeTranslator(bad, self.good(lang="ur"))
        self.assertEqual(foundation.parent_explanation(self.db, "c3_demonstratives", "ur", translator)["dir"], "rtl")
        with self.assertRaises(ApplicationError) as ctx:
            foundation.parent_explanation(self.db, "c4_pronouns", "ml", FakeTranslator(bad))
        self.assertEqual(ctx.exception.status_code, 502)

    def test_a_reply_in_the_wrong_script_is_retried(self):
        """Hindi asked, but the examples came back in Urdu script: not saved, asked again."""
        wrong = self.good()
        wrong["examples"] = ["ایک دروازہ" for _ in wrong["examples"]]
        translator = FakeTranslator(wrong, self.good())
        result = foundation.parent_explanation(self.db, "c3_demonstratives", "hi", translator)
        self.assertEqual(translator.calls, 2)
        self.assertTrue(all("उदाहरण" in e for e in result["examples"]))
        self.assertIn("Devanagari", foundation._check(wrong, foundation._source(
            __import__("backend.foundation_data", fromlist=["x"]).get_lesson("c3_demonstratives")), "hi"))

    def test_urdu_must_be_urdu_not_only_the_kept_arabic(self):
        from backend.foundation_data import get_lesson
        source = foundation._source(get_lesson("b1_short_vowels"))
        only_arabic = {"summary": "فَتْحَة", "points": ["كَسْرَة"] * len(source["points"]), "examples": ["مِنْ"] * len(source["examples"])}
        self.assertIsNotNone(foundation._check(only_arabic, source, "ur"))
        urdu = {"summary": "یہ ایک سبق ہے", "points": ["یہ نکتہ ہے"] * len(source["points"]),
                "examples": ["یہ مثال ہے"] * len(source["examples"])}
        self.assertIsNone(foundation._check(urdu, source, "ur"))

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


class TestFoundationProgress(FeatureTestCase):
    def setUp(self):
        super().setUp()
        from backend.models import ChildProfile, User
        for uid in ("pa", "pb"):
            self.db.add(User(id=uid, email=f"{uid}@test.local", full_name=uid, role="parent", password_hash="x", is_verified=True))
        self.db.commit()
        for cid, parent in (("a1", "pa"), ("b1", "pb")):
            self.db.add(ChildProfile(id=cid, parent_id=parent, name=cid, default_grade=5))
        self.db.commit()

    def client_as(self, principal):
        from fastapi.testclient import TestClient
        from backend.api.dependencies import get_current_user
        from backend.database import get_db
        from backend.main import app
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user] = lambda: principal
        self.addCleanup(app.dependency_overrides.pop, get_db, None)
        self.addCleanup(app.dependency_overrides.pop, get_current_user, None)
        return TestClient(app)

    def test_progress_is_kept_on_the_account(self):
        from backend.modules.identity.access import Principal
        parent = Principal(id="pa", email="pa@test.local", role="parent", is_verified=True)
        with self.client_as(parent) as client:
            self.assertEqual(client.get("/api/modules/foundation/progress", params={"child_id": "a1"}).json()["completed"], [])
            saved = client.post("/api/modules/foundation/progress",
                                json={"child_id": "a1", "lesson_ids": ["a1_alphabet", "a2_letter_shapes", "a1_alphabet", "zz_unknown"]})
            self.assertEqual(saved.status_code, 200, saved.text)
            self.assertEqual(saved.json()["completed"], ["a1_alphabet", "a2_letter_shapes"])
            # Merging progress from a device adds only what is new.
            again = client.post("/api/modules/foundation/progress", json={"child_id": "a1", "lesson_ids": ["a2_letter_shapes", "b1_short_vowels"]})
            self.assertEqual(sorted(again.json()["completed"]), ["a1_alphabet", "a2_letter_shapes", "b1_short_vowels"])
            # Another family's child is off limits, in both directions.
            self.assertEqual(client.get("/api/modules/foundation/progress", params={"child_id": "b1"}).status_code, 403)
            self.assertEqual(client.post("/api/modules/foundation/progress", json={"child_id": "b1", "lesson_ids": ["a1_alphabet"]}).status_code, 403)
        # The learner's own session sees the same progress (another device, same account).
        learner = Principal(id="pa", email="pa@test.local", role="learner", is_verified=True, child_id="a1")
        with self.client_as(learner) as client:
            self.assertEqual(len(client.get("/api/modules/foundation/progress", params={"child_id": "a1"}).json()["completed"]), 3)

    def test_signed_out_visitors_have_no_account_progress(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as client:
            self.assertEqual(client.get("/api/modules/foundation/progress", params={"child_id": "a1"}).status_code, 401)

    def test_deleting_a_child_deletes_their_progress(self):
        from backend.models import FoundationProgress
        from backend.modules.identity.service import purge_children
        foundation.mark_completed(self.db, "a1", ["a1_alphabet"])
        purge_children(["a1"], db=self.db)
        self.db.commit()
        self.assertEqual(self.db.query(FoundationProgress).count(), 0)

"""Server-side transcription for speaking practice when the device has no Arabic recognition."""
import base64
import datetime
import json
import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.ai import gateway
from backend.ai.errors import AIUnavailable
from backend.database import Base, get_db
from backend.main import app
from backend.models import ChildProfile, User, UserSession
from backend.redis_client import _fallback_cache, _fallback_rate_buckets
from backend.security import create_access_token, decode_access_token, hash_password

WAV = base64.b64encode(b"RIFF\x24\x00\x00\x00WAVEfmt " + b"\x00" * 64).decode()
TARGET = "أُحِبُّ اللُّغَةَ العَرَبِيَّةَ"


def fake_reply(transcript):
    return gateway.AIResponse(text=json.dumps({"transcript": transcript}), provider="gemini", model="gemini-test")


class TestSpeechTranscription(unittest.TestCase):
    def setUp(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            pw = hash_password("TestPassword123!")
            for uid in ("pa", "pb"):
                db.add(User(id=uid, email=f"{uid}@test.local", full_name=uid, role="parent", password_hash=pw, is_verified=True))
            db.commit()
            db.add(ChildProfile(id="a1", parent_id="pa", name="a1", access_pin="1111", default_grade=5))
            db.add(ChildProfile(id="b1", parent_id="pb", name="b1", access_pin="2222", default_grade=5))
            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db
        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()

    def auth(self, user="pa"):
        token = create_access_token({"sub": user, "role": "parent"})
        payload = decode_access_token(token)
        with self.session() as db:
            db.add(UserSession(id=payload["jti"], user_id=user,
                               expires_at=datetime.datetime.utcfromtimestamp(payload["exp"])))
            db.commit()
        return {"Authorization": f"Bearer {token}"}

    def post(self, body, headers=None):
        return self.client.post("/api/audio/evaluate-speech", json={"target_phrase": TARGET, **body}, headers=headers or {})

    def test_recording_is_transcribed_by_gemini_and_scored(self):
        with mock.patch.object(gateway, "generate", return_value=fake_reply("احب اللغه العربيه")) as generate:
            res = self.post({"child_id": "a1", "audio_base64": WAV, "audio_mime_type": "audio/wav"}, self.auth())
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["recognized_text"], "احب اللغه العربيه")
        request = generate.call_args.args[0]
        self.assertEqual(request.providers, ["gemini"])          # audio never goes to a provider that can't hear it
        self.assertEqual(request.learner_id, "a1")
        self.assertEqual(request.attachments[0][1], "audio/wav")

    def test_anonymous_recordings_are_refused(self):
        with mock.patch.object(gateway, "generate") as generate:
            res = self.post({"child_id": "a1", "audio_base64": WAV})
        self.assertEqual(res.status_code, 401)
        generate.assert_not_called()

    def test_another_familys_child_is_refused(self):
        with mock.patch.object(gateway, "generate") as generate:
            res = self.post({"child_id": "b1", "audio_base64": WAV}, self.auth("pa"))
        self.assertEqual(res.status_code, 403)
        generate.assert_not_called()

    def test_daily_limit(self):
        with mock.patch.dict(os.environ, {"FAHIM_SPEECH_DAILY_LIMIT": "3"}), \
             mock.patch("backend.ai.usage.learner_feature_calls_today", return_value=3), \
             mock.patch.object(gateway, "generate") as generate:
            res = self.post({"child_id": "a1", "audio_base64": WAV}, self.auth())
        self.assertEqual(res.status_code, 429)
        generate.assert_not_called()

    def test_unsupported_format_and_silence(self):
        with mock.patch.object(gateway, "generate") as generate:
            res = self.post({"child_id": "a1", "audio_base64": WAV, "audio_mime_type": "video/mp4"}, self.auth())
        self.assertEqual(res.status_code, 415)
        generate.assert_not_called()
        with mock.patch.object(gateway, "generate", return_value=fake_reply("")):
            res = self.post({"child_id": "a1", "audio_base64": WAV}, self.auth())
        self.assertEqual(res.status_code, 422)   # nothing heard: no score

    def test_ai_outage_is_reported_not_scored(self):
        with mock.patch.object(gateway, "generate", side_effect=AIUnavailable("down")):
            res = self.post({"child_id": "a1", "audio_base64": WAV}, self.auth())
        self.assertEqual(res.status_code, 503)

    def test_device_transcripts_need_no_ai(self):
        with mock.patch.object(gateway, "generate") as generate:
            res = self.post({"spoken_text": "احب اللغه العربيه"})
        self.assertEqual(res.status_code, 200)
        generate.assert_not_called()


class TestGatewayProviderFilter(unittest.TestCase):
    def test_request_limited_to_unavailable_provider_fails_cleanly(self):
        class Anthropic:
            name = "anthropic"
        with mock.patch.object(gateway, "_providers", return_value=[Anthropic()]):
            with self.assertRaises(AIUnavailable):
                gateway.generate(gateway.AIRequest(feature="speech_transcription", prompt="x", providers=["gemini"]))


if __name__ == "__main__":
    unittest.main()

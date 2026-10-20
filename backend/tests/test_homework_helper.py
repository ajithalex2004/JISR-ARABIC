"""Ask Fahim homework helper: explains worksheet questions with a hint first, then the answer."""
import base64
import datetime
import io
import json
import unittest
import zipfile
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.ai.errors import AILimitReached
from backend.ai.gateway import AIResponse
from backend.database import Base, get_db
from backend.main import app
from backend.models import User, UserSession
from backend.modules.tutoring import homework
from backend.redis_client import _fallback_cache, _fallback_rate_buckets
from backend.security import create_access_token, decode_access_token, hash_password

PNG = base64.b64encode(b"\x89PNG\r\n\x1a\nfake").decode()

SCAN_REPLY = {
    "is_homework": True,
    "title_en": "Colours",
    "questions": [
        {"number": "1", "question_ar": "مَا لَوْنُ السَّمَاءِ؟", "question_en": "What colour is the sky?",
         "asks_en": "Write the colour of the sky in Arabic.", "hint_en": "Think of the colour words from Lesson 3.",
         "hint_ar": "تَذَكَّرْ أَسْمَاءَ الأَلْوَانِ.", "answer_format": "write", "answer": "أَزْرَقُ"},
        # A hint that gives the answer away (in Arabic, even without vowel marks).
        {"number": "2", "question_ar": "مَا لَوْنُ العُشْبِ؟", "question_en": "What colour is the grass?",
         "asks_en": "Write the colour of the grass.", "hint_en": "It is akhdar.",
         "hint_ar": "الجواب: اخضر", "answer_format": "write", "answer": "أَخْضَرُ"},
    ],
}


def docx(paragraphs):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
        archive.writestr("word/document.xml", f'<w:document xmlns:w="w"><w:body>{body}</w:body></w:document>')
    return base64.b64encode(out.getvalue()).decode()


class TestHomeworkHelper(unittest.TestCase):
    def setUp(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            pw = hash_password("TestPassword123!")
            for uid in ("s1", "s2"):
                db.add(User(id=uid, email=f"{uid}@test.local", full_name=uid, role="tutor", password_hash=pw,
                            is_verified=True))
            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db
        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)
        self.replies = []
        self.requests = []

        def fake_generate(request, **_):
            self.requests.append(request)
            return AIResponse(text=json.dumps(self.replies.pop(0), ensure_ascii=False), provider="gemini", model="m")
        self.patch = patch("backend.ai.gateway.generate", side_effect=fake_generate)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()

    def auth(self, user):
        token = create_access_token({"sub": user, "role": "tutor"})
        payload = decode_access_token(token)
        with self.session() as db:
            db.add(UserSession(id=payload["jti"], user_id=user,
                               expires_at=datetime.datetime.utcfromtimestamp(payload["exp"])))
            db.commit()
        return {"Authorization": f"Bearer {token}"}

    def scan(self, headers, body=None):
        self.replies.append(SCAN_REPLY)
        return self.client.post("/api/ai/homework/scan", headers=headers,
                                json=body or {"file_base64": PNG, "mime_type": "image/png", "grade": 3})

    def test_scan_explains_questions_with_hints_and_answers(self):
        res = self.scan(self.auth("s1"))
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertTrue(data["is_homework"])
        first, second = data["questions"]
        self.assertEqual((first["question_en"], first["hint_trimmed"]), ("What colour is the sky?", False))
        self.assertEqual((first["answer"], second["answer"]), ("أَزْرَقُ", "أَخْضَرُ"))
        # The hint is shown before the answer, so one that gives the answer away is replaced.
        self.assertTrue(second["hint_trimmed"])
        self.assertEqual(second["hint_en"], homework.GENERIC_HINT_EN)
        request = self.requests[0]
        self.assertEqual((request.feature, request.attachments[0][1]), ("homework_scan", "image/png"))
        self.assertIn("Grade 3", request.system)

    def test_check_gives_the_verdict_and_the_answer(self):
        headers = self.auth("s1")
        scan_id = self.scan(headers).json()["scan_id"]
        self.replies.append({"verdict": "not_yet", "student_answer_read": "أحمر",
                             "feedback_en": "Not quite: the right word is azraq, أزرق.", "feedback_ar": "الجواب أزرق"})
        res = self.client.post("/api/ai/homework/check", headers=headers,
                               json={"scan_id": scan_id, "question_number": "1", "answer_text": "أحمر"})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["verdict"], "not_yet")
        self.assertEqual(res.json()["feedback_en"], "Not quite: the right word is azraq, أزرق.")
        self.assertEqual(res.json()["answer"], "أَزْرَقُ")
        prompt = json.loads(self.requests[-1].prompt)
        self.assertEqual((prompt["reference_answer"], prompt["student_answer"]), ("أَزْرَقُ", "أحمر"))

        # A photo of handwriting is sent to the AI as an image.
        self.replies.append({"verdict": "correct", "student_answer_read": "أزرق", "feedback_en": "Well done!",
                             "feedback_ar": "أحسنت!"})
        res = self.client.post("/api/ai/homework/check", headers=headers, json={
            "scan_id": scan_id, "question_number": "1", "answer_image_base64": PNG, "answer_image_type": "image/png"})
        self.assertEqual(res.json()["verdict"], "correct")
        self.assertEqual(self.requests[-1].attachments[0][1], "image/png")

    def test_only_the_student_who_scanned_can_check(self):
        scan_id = self.scan(self.auth("s1")).json()["scan_id"]
        res = self.client.post("/api/ai/homework/check", headers=self.auth("s2"),
                               json={"scan_id": scan_id, "question_number": "1", "answer_text": "x"})
        self.assertEqual(res.status_code, 404)

    def test_sign_in_required(self):
        res = self.client.post("/api/ai/homework/scan", json={"file_base64": PNG, "mime_type": "image/png"})
        self.assertEqual(res.status_code, 401)

    def test_word_files_are_read_as_text_and_old_formats_refused(self):
        headers = self.auth("s1")
        res = self.scan(headers, {"file_base64": docx(["تمرين ١", "اكتب لون السماء &amp; العشب"]),
                                  "mime_type": homework.DOCX_TYPE, "file_name": "hw.docx"})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIn("اكتب لون السماء & العشب", self.requests[-1].prompt)
        self.assertEqual(self.requests[-1].attachments, [])
        self.replies.clear()
        res = self.client.post("/api/ai/homework/scan", headers=headers, json={
            "file_base64": PNG, "mime_type": "application/msword", "file_name": "hw.doc"})
        self.assertEqual(res.status_code, 400)
        self.assertIn(".docx", res.json()["detail"])

    def test_daily_limit_is_reported_kindly(self):
        self.patch.stop()
        with patch("backend.ai.gateway.generate", side_effect=AILimitReached("daily", "limit")):
            res = self.client.post("/api/ai/homework/scan", headers=self.auth("s1"),
                                   json={"file_base64": PNG, "mime_type": "image/png"})
        self.patch.start()
        self.assertEqual(res.status_code, 429)

    def test_answer_leak_check(self):
        self.assertTrue(homework.gives_away("The answer is أخضر", "أَخْضَرُ", "ما لون العشب؟"))
        self.assertFalse(homework.gives_away("Think of colour words", "أَخْضَرُ", "ما لون العشب؟"))
        # A word the student must copy from the question is fair to mention.
        self.assertFalse(homework.gives_away("Copy the word كتاب", "كتاب", "انسخ الكلمة: كتاب"))


if __name__ == "__main__":
    unittest.main()

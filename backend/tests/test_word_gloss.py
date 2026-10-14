import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.modules.curriculum import glossary


class TestWordGloss(unittest.TestCase):
    def setUp(self):
        glossary._cache.clear()

    def _gemini(self, text):
        client = MagicMock()
        client.models.generate_content.return_value = MagicMock(text=text)
        return patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=client), client

    def test_gemini_gloss_uses_context_and_is_cached(self):
        p, client = self._gemini('{"translation": "a means", "part_of_speech": "noun"}')
        with p:
            first = glossary.gloss_word("وَسِيلَةٌ", "لأنّ المال وسيلة لتحقيق الرغبات")
            second = glossary.gloss_word("وَسِيلَةٌ", "لأنّ المال وسيلة لتحقيق الرغبات")
        self.assertEqual(first, {"translation": "a means", "part_of_speech": "noun", "source": "gemini"})
        self.assertEqual(second, first)
        client.models.generate_content.assert_called_once()
        self.assertIn("لتحقيق", client.models.generate_content.call_args.kwargs["contents"])

    def test_falls_back_to_machine_translation(self):
        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=None), \
             patch("backend.modules.curriculum.authoring._translate_ar_to_en", return_value="provision"):
            self.assertEqual(glossary.gloss_word("توفير")["translation"], "provision")

    def test_rejects_untranslated_or_failed_results(self):
        p, _ = self._gemini('{"translation": "وسيلة"}')
        with p, patch("backend.modules.curriculum.authoring._translate_ar_to_en", return_value="Lesson text: توفير"):
            self.assertIsNone(glossary.gloss_word("توفير"))
        self.assertIsNone(glossary.gloss_word("hello"))

    def test_endpoint(self):
        with patch.object(glossary, "gloss_word", return_value={"translation": "saving", "part_of_speech": "noun", "source": "gemini"}):
            res = TestClient(app).get("/api/curriculum/word-gloss", params={"word": "توفير"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["translation"], "saving")
        with patch.object(glossary, "gloss_word", return_value=None):
            res = TestClient(app).get("/api/curriculum/word-gloss", params={"word": "توفير"})
        self.assertIsNone(res.json()["translation"])


if __name__ == "__main__":
    unittest.main()

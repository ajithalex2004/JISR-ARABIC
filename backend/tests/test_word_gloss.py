import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.modules.curriculum import glossary


class TestWordGloss(unittest.TestCase):
    def setUp(self):
        from backend import redis_client
        glossary._cache.clear()
        redis_client._fallback_cache.clear()

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
             patch.object(glossary, "_google_word_translation", return_value="Necessities"):
            self.assertEqual(glossary.gloss_word("الضروريات")["translation"], "Necessities")

    def test_rejects_untranslated_or_failed_results(self):
        p, _ = self._gemini('{"translation": "وسيلة"}')
        with p, patch.object(glossary, "_google_word_translation", return_value=None):
            self.assertIsNone(glossary.gloss_word("توفير"))
        self.assertIsNone(glossary.gloss_word("hello"))

    def test_hides_misleading_machine_translations(self):
        # Real outputs seen in production before this filter existed.
        for bad in ("TO THE", "mean, contrivance, instrument, connection", "the", "وسيلة", ""):
            with self.subTest(bad=bad):
                self.assertIsNone(glossary._acceptable_machine_translation(bad))
        self.assertEqual(glossary._acceptable_machine_translation("ESSENTIALS."), "essentials")
        self.assertEqual(glossary._acceptable_machine_translation("to achieve"), "to achieve")

    def test_default_model_is_not_the_retired_one(self):
        from backend.modules.tutoring import assistant
        self.assertNotEqual(assistant.GEMINI_MODEL, "gemini-2.0-flash")

    def test_endpoint(self):
        with patch.object(glossary, "gloss_word", return_value={"translation": "saving", "part_of_speech": "noun", "source": "gemini"}):
            res = TestClient(app).get("/api/curriculum/word-gloss", params={"word": "توفير"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["translation"], "saving")
        with patch.object(glossary, "gloss_word", return_value=None):
            res = TestClient(app).get("/api/curriculum/word-gloss", params={"word": "توفير"})
        self.assertIsNone(res.json()["translation"])

    def test_batch_glosses_a_sentence_with_one_ai_call(self):
        sentence = "ذهب الطلاب بسرعة إلى حديقتنا"
        p, client = self._gemini('{"glosses": [{"n": 1, "translation": "quickly", "part_of_speech": "adverb"},'
                                 ' {"n": 2, "translation": "our garden", "part_of_speech": "noun"}]}')
        with p:
            result = glossary.gloss_words(["بِسُرْعَةٍ", "حَدِيقَتِنَا", "hello"], sentence)
        client.models.generate_content.assert_called_once()
        self.assertEqual(result["بِسُرْعَةٍ"]["translation"], "quickly")
        self.assertEqual(result["حَدِيقَتِنَا"]["part_of_speech"], "noun")
        self.assertNotIn("hello", result)
        # The single-word lookup a tap makes for the same sentence is now answered from the cache.
        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=None):
            self.assertEqual(glossary.gloss_word("بِسُرْعَةٍ", sentence)["translation"], "quickly")

    def test_batch_survives_a_restart_through_the_shared_cache(self):
        p, _ = self._gemini('{"glosses": [{"n": 1, "translation": "quickly", "part_of_speech": "adverb"}]}')
        with p:
            glossary.gloss_words(["بِسُرْعَةٍ"], "ذهب بسرعة")
        glossary._cache.clear()  # a new server process
        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=None), \
             patch.object(glossary, "_google_word_translation", return_value=None):
            self.assertEqual(glossary.gloss_word("بِسُرْعَةٍ", "ذهب بسرعة")["translation"], "quickly")

    def test_batch_falls_back_to_machine_translation_for_words_the_ai_skips(self):
        p, _ = self._gemini('{"glosses": [{"n": 1, "translation": "quickly"}, {"n": 9, "translation": "x"}]}')
        with p, patch.object(glossary, "_google_word_translation", return_value="Garden"):
            result = glossary.gloss_words(["بِسُرْعَةٍ", "حَدِيقَة"], "")
        self.assertEqual((result["بِسُرْعَةٍ"]["source"], result["حَدِيقَة"]["translation"]),
                         ("gemini", "Garden"))

    def test_batch_endpoint(self):
        with patch.object(glossary, "gloss_words", return_value={
                "بِسُرْعَةٍ": {"translation": "quickly", "part_of_speech": "adverb", "source": "gemini"}, "x": None}):
            res = TestClient(app).post("/api/curriculum/word-glosses", json={"words": ["بِسُرْعَةٍ", "x"], "context": "s"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["glosses"], {"بِسُرْعَةٍ": {"translation": "quickly", "part_of_speech": "adverb"}, "x": None})
        self.assertEqual(TestClient(app).post("/api/curriculum/word-glosses", json={"words": []}).status_code, 422)


if __name__ == "__main__":
    unittest.main()

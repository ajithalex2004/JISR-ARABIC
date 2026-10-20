"""Textbook pages get real English: the AI translates a page's lines in one batch (cached), the web
translators cover the rest, and a line with no translation stays empty instead of echoing the Arabic."""
import json
import unittest
from unittest.mock import patch

from backend.ai.gateway import AIResponse
from backend.modules.curriculum import authoring
from backend.redis_client import _fallback_cache

PAGE = ["أسأل زملائي عن الإجازة:", "أين كنت؟\nمتى رجعت؟"]


class PageTranslationTest(unittest.TestCase):
    def setUp(self):
        authoring._TRANSLATION_CACHE.clear()
        _fallback_cache.clear()

    def test_ai_translates_the_page_in_one_batch_and_caches_it(self):
        calls = []

        def fake_generate(request, **_):
            calls.append(request)
            lines = json.loads(request.prompt)["lines"]
            english = {"أسأل زملائي عن الإجازة:": "I ask my classmates about the holiday:",
                       "أين كنت؟": "Where were you?", "متى رجعت؟": "When did you come back?"}
            return AIResponse(text=json.dumps({"translations": [english[l] for l in lines]}), provider="gemini", model="m")

        with patch("backend.ai.gateway.available", return_value=True), \
                patch("backend.ai.gateway.generate", side_effect=fake_generate), \
                patch.object(authoring, "_translate_ar_to_en", side_effect=AssertionError("web translator not needed")):
            first = authoring.translate_paragraphs(PAGE)
            self.assertEqual(first, ["I ask my classmates about the holiday:", "Where were you?\nWhen did you come back?"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0].feature, "page_translation")
            # Cached: the page costs nothing the second time, even after a restart (memory cleared).
            authoring._TRANSLATION_CACHE.clear()
            self.assertEqual(authoring.translate_paragraphs(PAGE), first)
            self.assertEqual(len(calls), 1)

    def test_no_translation_is_empty_not_the_arabic(self):
        with patch("backend.ai.gateway.available", return_value=False), \
                patch("urllib.request.urlopen", side_effect=OSError("offline")):
            result = authoring.translate_paragraphs(PAGE)
        self.assertEqual(result, ["", ""])
        self.assertNotIn("Lesson text", "".join(result))


if __name__ == "__main__":
    unittest.main()

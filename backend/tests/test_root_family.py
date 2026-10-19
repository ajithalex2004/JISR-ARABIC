import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.modules.curriculum import roots
from backend.redis_client import cache_clear


def _ai(words, core="writing"):
    class Response:
        text = json.dumps({"core_meaning_en": core, "words": words})
        provider = "gemini"
    return Response()


class TestRootMatching(unittest.TestCase):
    def test_normalize_root(self):
        self.assertEqual(roots.normalize_root("كَ - تَ - بَ"), "ك-ت-ب")
        self.assertEqual(roots.normalize_root("ع ب ق ر"), "ع-ب-ق-ر")
        self.assertIsNone(roots.normalize_root("ك-ت"))
        self.assertIsNone(roots.normalize_root("abc"))
        self.assertEqual(roots.split_roots("م-د-ن / ذ-ك-ي"), ["م-د-ن", "ذ-ك-ي"])

    def test_root_letters_found_and_prefix_ignored(self):
        self.assertEqual(roots.root_letter_positions("المَلْعَبُ", "ل-ع-ب"), [3, 4, 5])
        self.assertEqual(roots.root_letter_positions("مَكْتَبَةٌ", "ك-ت-ب"), [1, 2, 3])
        self.assertIsNone(roots.root_letter_positions("مَدْرَسَةٌ", "ك-ت-ب"))

    def test_weak_hamza_and_doubled_letters(self):
        self.assertIsNotNone(roots.root_letter_positions("قَالَ", "ق-و-ل"))
        self.assertIsNotNone(roots.root_letter_positions("قَائِمَةٌ", "ق-و-م"))
        self.assertIsNotNone(roots.root_letter_positions("آمِنَةٌ", "أ-م-ن"))
        self.assertIsNotNone(roots.root_letter_positions("مَدَّ", "م-د-د"))
        self.assertIsNotNone(roots.root_letter_positions("الطَّوَارِئُ", "ط-ر-أ"))
        self.assertEqual(roots.root_letter_positions("الكُرَةُ", "ك-ر-و"), [2, 3])
        self.assertEqual(roots.root_letter_positions("المَهَامُّ", "ه-م-م"), [3, 5])

    def test_strict_mode_needs_the_middle_weak_letter(self):
        self.assertIsNotNone(roots.root_letter_positions("مَدْرَسَةٌ", "د-و-ر"))  # lenient: highlighting only
        self.assertIsNone(roots.root_letter_positions("مَدْرَسَةٌ", "د-و-ر", strict=True))
        self.assertIsNotNone(roots.root_letter_positions("دَائِرَةٌ", "د-و-ر", strict=True))
        self.assertIsNotNone(roots.root_letter_positions("الكُرَةُ", "ك-ر-و", strict=True))
        self.assertIsNotNone(roots.root_letter_positions("جِهَةٌ", "و-ج-ه", strict=True))

    def test_every_catalogue_card_contains_its_root(self):
        by_root, by_word = roots._catalogue()
        missing = [(w["word_ar"], r) for r, words in by_root.items() for w in words
                   if not any(roots.root_letter_positions(part, r) is not None for part in w["word_ar"].split())
                   and not by_word[roots.strip_tashkeel(w["word_ar"])]["note_en"]]  # explained exceptions
        self.assertEqual(missing, [])
        self.assertTrue(by_word[roots.strip_tashkeel("مَلْيُونٌ")]["note_en"])


class TestRootFamilyEndpoint(unittest.TestCase):
    def setUp(self):
        cache_clear()
        self.client = TestClient(app)

    def test_family_combines_lessons_and_checked_ai_words(self):
        words = [
            {"word_ar": "كَتَبَ", "root": "ك-ت-ب", "meaning_en": "he wrote", "pattern": "فَعَلَ", "kind": "verb"},
            {"word_ar": "مَكْتَبَةٌ", "root": "ك ت ب", "meaning_en": "library", "pattern": "مَفْعَلَة", "kind": "place"},
            {"word_ar": "مَدْرَسَةٌ", "root": "ك-ت-ب", "meaning_en": "school", "kind": "place"},  # letters missing
            {"word_ar": "مَكْتُوبٌ", "root": "ك-ت-م", "meaning_en": "written", "kind": "object"},  # declares another root
            {"word_ar": "الكَاتِبُ", "root": "ك-ت-ب", "meaning_en": "the writer", "kind": "doer"},  # already in a lesson
        ]
        with patch("backend.ai.gateway.available", return_value=True), \
             patch("backend.ai.gateway.generate", return_value=_ai(words)) as gen:
            first = self.client.get("/api/curriculum/root-family", params={"root": "ك-ت-ب"}).json()
            second = self.client.get("/api/curriculum/root-family", params={"root": "ك ت ب"}).json()
        gen.assert_called_once()  # cached
        self.assertEqual(first, second)
        self.assertEqual(first["letters"], ["ك", "ت", "ب"])
        self.assertEqual(first["core_meaning_en"], "writing")
        self.assertEqual(first["family_source"], "ai")
        self.assertEqual([w["word_ar"] for w in first["family"]], ["كَتَبَ", "مَكْتَبَةٌ"])
        self.assertEqual(first["curriculum_words"][0]["lesson_id"], "lesson_05_reading")

    def test_word_lookup_uses_corrected_catalogue_root(self):
        with patch("backend.ai.gateway.available", return_value=False):
            data = self.client.get("/api/curriculum/root-family",
                                   params={"word": "الكُرَةُ", "root": "ك-ر-ر"}).json()
        self.assertEqual(data["root"], "ك-ر-و")
        self.assertEqual(data["family_source"], "unavailable")
        self.assertEqual(data["family"], [])

    def test_borrowed_word_has_no_root(self):
        data = self.client.get("/api/curriculum/root-family", params={"word": "فِيلْمٌ"}).json()
        self.assertTrue(data["borrowed"])
        self.assertIsNone(data["root"])
        self.assertIn("film", data["note_en"])

    def test_no_ai_for_roots_outside_the_catalogue(self):
        with patch("backend.ai.gateway.generate") as gen:
            data = self.client.get("/api/curriculum/root-family", params={"root": "ز-ب-ط"}).json()
        gen.assert_not_called()
        self.assertEqual(data["family_source"], "none")
        self.assertEqual(data["curriculum_words"], [])

    def test_rejects_unusable_input(self):
        self.assertEqual(self.client.get("/api/curriculum/root-family", params={"root": "xy"}).status_code, 422)


if __name__ == "__main__":
    unittest.main()

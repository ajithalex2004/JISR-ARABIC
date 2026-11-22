"""Foundation in Basic Arabic: structure, answer keys and tashkeel of the course content."""
import re
import unittest

from backend.foundation_data import (ALPHABET, KING_LETTERS, MOON_LETTERS, SUN_LETTERS, TEXTBOOK_KEYWORDS,
                                     VOWEL_MARKS, foundation_course, recording_script)

WORD = re.compile(r"[ء-ي][ء-يً-ْٰـ]*")
VOWELLED = re.compile(r"[ً-ْ]")
ACTIVITIES = {"alphabet", "letter_shapes", "vowel_grid", "sort", "syllables", "builder", "cards", "fluency", "roots"}


def lessons():
    for stage in foundation_course()["stages"]:
        for lesson in stage["lessons"]:
            yield stage["id"], lesson


class TestFoundationCourse(unittest.TestCase):
    def test_four_stages_in_order(self):
        stages = foundation_course()["stages"]
        self.assertEqual([s["id"] for s in stages], ["A", "B", "C", "D", "E"])
        for stage in stages:
            self.assertTrue(stage["lessons"], stage["id"])

    def test_lessons_are_complete_and_unique(self):
        ids = [lesson["id"] for _, lesson in lessons()]
        self.assertEqual(len(ids), len(set(ids)))
        for stage_id, lesson in lessons():
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(lesson["id"].startswith(stage_id.lower()))
                for key in ("title_ar", "title_en", "summary_en"):
                    self.assertTrue(lesson[key].strip())
                self.assertGreaterEqual(len(lesson["points"]), 2)
                self.assertGreaterEqual(len(lesson["examples"]), 1)
                self.assertGreaterEqual(len(lesson["quiz"]), 1)

    def test_quiz_answer_keys_are_valid(self):
        for _, lesson in lessons():
            for item in lesson["quiz"]:
                with self.subTest(lesson=lesson["id"], question=item["question_en"]):
                    self.assertGreaterEqual(len(item["options"]), 2)
                    self.assertEqual(len(set(item["options"])), len(item["options"]))
                    self.assertIn(item["correct_index"], range(len(item["options"])))
                    self.assertTrue(item["explain_en"])

    def test_examples_are_fully_vowelled(self):
        """Examples are read aloud and shown with the Arab-English line, which is spelled from the vowels."""
        for _, lesson in lessons():
            for example in lesson["examples"]:
                missing = [w for w in WORD.findall(example["ar"]) if len(w) > 1 and not VOWELLED.search(w)]
                with self.subTest(lesson=lesson["id"], example=example["ar"]):
                    self.assertEqual(missing, [])
                    self.assertTrue(example["en"])

    def test_activities(self):
        seen = set()
        for _, lesson in lessons():
            activity = lesson.get("activity")
            if not activity:
                continue
            seen.add(activity["type"])
            with self.subTest(lesson=lesson["id"]):
                self.assertIn(activity["type"], ACTIVITIES)
                if activity["type"] == "sort":
                    buckets = {b["id"] for b in activity["buckets"]}
                    self.assertGreaterEqual(len(buckets), 2)
                    self.assertTrue(activity["items"])
                    for item in activity["items"]:
                        self.assertIn(item["bucket"], buckets)
                if activity["type"] == "syllables":
                    def letters(text):
                        # Letters only, a shadda letter counted twice (it is split across two syllables).
                        bare = re.sub("[ًٌٍَُِْ]", "", text)
                        return re.sub("(.)ّ", r"\1\1", bare)
                    for item in activity["items"]:
                        self.assertEqual(letters("".join(item["parts"])), letters(item["word"]), item["word"])
                if activity["type"] == "vowel_grid":
                    self.assertTrue(set(activity["marks"]) <= {m["id"] for m in VOWEL_MARKS})
                if activity["type"] in ("cards", "fluency", "roots"):
                    texts = ([c["ar"] for c in activity["items"]] if activity["type"] == "cards" else
                             activity["items"] if activity["type"] == "fluency" else
                             [w["ar"] for f in activity["families"] for w in f["words"]])
                    self.assertTrue(texts)
                    for text in texts:
                        missing = [w for w in WORD.findall(text) if len(w) > 1 and not VOWELLED.search(w)]
                        self.assertEqual(missing, [], text)
                if activity["type"] == "builder":
                    for item in activity["items"]:
                        self.assertGreaterEqual(len(item["words"]), 2)
                        self.assertTrue(item["en"])
        self.assertEqual(seen, ACTIVITIES)

    def test_letter_sets(self):
        self.assertEqual(len(ALPHABET), 29)  # 28 letters + hamza
        self.assertEqual(len(KING_LETTERS), 6)
        self.assertEqual(len(SUN_LETTERS), 14)
        self.assertEqual(len(MOON_LETTERS), 14)
        letters = {l for l, _, _ in ALPHABET if l != "ء"}
        self.assertEqual(set(SUN_LETTERS) | set(MOON_LETTERS), letters)
        self.assertFalse(set(SUN_LETTERS) & set(MOON_LETTERS))
        # Each alphabet letter's name is vowelled (it is read aloud).
        for _, name, _ in ALPHABET:
            self.assertTrue(VOWELLED.search(name), name)

    def test_every_lesson_has_textbook_keywords(self):
        ids = {lesson["id"] for _, lesson in lessons()}
        self.assertEqual(ids, set(TEXTBOOK_KEYWORDS))

    def test_recording_script_covers_the_letters_and_syllables(self):
        script = recording_script()
        texts = [item["text"] for item in script]
        self.assertEqual(len(texts), len(set(texts)))
        self.assertIn("بَاء", texts)        # a letter name
        self.assertIn("بَ", texts)          # a vowel-grid syllable
        self.assertIn("أَبْ", texts)        # sukun syllable
        self.assertIn("حَمْ", texts)        # a syllable from the syllable splitter
        self.assertIn("كِتَابٌ", texts)     # a word
        self.assertEqual(sum(1 for item in script if item["group"] == "1 Letter names"), 29)

    def test_api(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        with TestClient(app) as client:
            res = client.get("/api/modules/foundation")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body["success"])
        self.assertEqual(len(body["stages"]), 5)
        self.assertEqual(len(body["vowel_marks"]), len(VOWEL_MARKS))
        self.assertEqual(len(body["alphabet"]), 29)


if __name__ == "__main__":
    unittest.main()

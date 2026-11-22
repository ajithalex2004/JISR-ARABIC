"""The daily AI feature check: runs each feature's own code on a known question and checks the answer."""
import datetime
import json
import unittest
from unittest.mock import MagicMock, patch

from backend import scheduler
from backend.ai import feature_check
from backend.foundation_data import all_lessons


def _hindi_translation():
    lesson = next(iter(all_lessons()))
    return {"title": "वर्णमाला", "summary": "अरबी में अक्षर",
            "points": ["बिंदु"] * len(lesson["points"]), "examples": ["उदाहरण"] * len(lesson["examples"])}


GOOD = {
    "Translate this beginner": _hindi_translation(),
    "Words:": {"glosses": [{"n": 1, "translation": "the student", "part_of_speech": "noun"},
                           {"n": 2, "translation": "a book", "part_of_speech": "noun"}]},
    "Word: ": {"translation": "book", "part_of_speech": "noun"},
    "Learning Topic:": {"teacher_name": "Fahim", "response_ar": "أَحْسَنْتَ!", "response_en": "Well done!"},
    "Student Question:": {"question_en": "What does كتاب mean?", "answer_ar": "كِتَابٌ: book", "answer_en": "It means 'book'.",
                          "page_reference": "Page 1", "lesson_title": "x"},
}


def _client(replies):
    def answer(**kwargs):
        prompt = str(kwargs.get("contents"))
        for marker, reply in replies.items():  # most specific markers first
            if marker in prompt:
                return MagicMock(text=reply if isinstance(reply, str) else json.dumps(reply, ensure_ascii=False))
        raise AssertionError(f"unexpected prompt: {prompt[:80]}")
    client = MagicMock()
    client.models.generate_content.side_effect = answer
    return client


class AIFeatureCheckTest(unittest.TestCase):
    def setUp(self):
        from backend import redis_client
        redis_client._fallback_cache.clear()

    def run_check(self, replies, **kwargs):
        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=_client(replies)), \
             patch("backend.alerts.alert_now") as alert:
            result = feature_check.run_feature_check(**kwargs)
        return result, alert

    def test_every_feature_passes_with_right_answers(self):
        result, alert = self.run_check(GOOD)
        self.assertTrue(result["ok"], result)
        self.assertEqual([c["key"] for c in result["checks"]],
                         ["word_meaning", "sentence_meanings", "ask_fahim", "learn_with_fahim", "parent_translation"])
        self.assertIn("كِتَابٌ → book", result["checks"][0]["detail"])
        alert.assert_not_called()
        from backend.redis_client import cache_get
        self.assertEqual(cache_get(feature_check.CACHE_KEY)["summary"], "All 5 AI features answered correctly.")

    def test_a_wrong_answer_fails_and_alerts(self):
        result, alert = self.run_check({**GOOD, "Word: ": {"translation": "table", "part_of_speech": "noun"}})
        self.assertFalse(result["ok"])
        word = result["checks"][0]
        self.assertFalse(word["ok"])
        self.assertIn("'table', expected 'book'", word["detail"])
        self.assertTrue(all(c["ok"] for c in result["checks"][1:]))
        alert.assert_called_once()
        self.assertIn("1 of 5 AI features failed: Word meaning", alert.call_args.args[1])

    def test_a_reply_the_code_cannot_read_shows_the_error(self):
        # The kind of problem behind the "'list' object has no attribute 'get'" alerts: a reply in a shape
        # the feature can't read. The check names the feature and the error the feature recorded.
        result, _ = self.run_check({**GOOD, "Learning Topic:": "not json at all"})
        learn = next(c for c in result["checks"] if c["key"] == "learn_with_fahim")
        self.assertFalse(learn["ok"])
        self.assertIn("Learn with Fahim gave no reply", learn["detail"])
        self.assertIn("error:", learn["detail"])

    def test_wrong_script_in_a_parent_translation_fails(self):
        urdu = {**_hindi_translation(), "summary": "عربی میں حروف"}
        result, _ = self.run_check({**GOOD, "Translate this beginner": urdu})
        self.assertFalse(next(c for c in result["checks"] if c["key"] == "parent_translation")["ok"])

    def test_admin_run_does_not_email(self):
        result, alert = self.run_check({**GOOD, "Word: ": {"translation": "table"}}, alert=False)
        self.assertFalse(result["ok"])
        alert.assert_not_called()

    def test_skipped_without_an_ai_provider(self):
        with patch("backend.ai.gateway.available", return_value=False), patch("backend.alerts.alert_now") as alert:
            result = feature_check.run_feature_check()
        self.assertTrue(result["skipped"])
        alert.assert_not_called()

    def test_scheduler_runs_it_once_a_day_from_06_00_uae(self):
        with patch.object(scheduler, "run_scheduled_gemini_probe"), patch.object(scheduler, "demo_cleanup_enabled", return_value=False), \
             patch.object(scheduler, "run_ai_feature_check") as run:
            scheduler.tick(datetime.datetime(2026, 11, 23, 1, 30))  # 05:30 UAE: too early
            run.assert_not_called()
            scheduler.tick(datetime.datetime(2026, 11, 23, 2, 5))
            scheduler.tick(datetime.datetime(2026, 11, 23, 9, 0))  # same day: not again
            self.assertEqual(run.call_count, 1)
            scheduler.tick(datetime.datetime(2026, 11, 24, 2, 5))  # next day
            self.assertEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()

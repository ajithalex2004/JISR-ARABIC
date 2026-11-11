"""Without the AI, Ask Fahim never answers one lesson's questions with the Class 5 Ball Games paper."""
import os
import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from backend.modules.tutoring import assistant
from backend.schemas import AskFahimRequest

NO_AI = {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}


def ask(question, lesson, admin=False):
    actor = MagicMock(role="admin") if admin else None
    req = AskFahimRequest(question=question, context_lesson_id=lesson)
    with patch.dict(os.environ, NO_AI), patch.object(assistant, "_ai_ready", return_value=False):
        return assistant.ask_fahim(req, db=MagicMock(spec=Session), actor=actor)


class TestFahimOfflineFallback(unittest.TestCase):
    def test_other_class_question_gets_an_honest_reply_not_ball_games(self):
        for q in ("I have a question about tolerance", "عندي سؤال عن التسامح", "q1 please"):
            res = ask(q, "lesson_g8_t1_ch01")
            self.assertTrue(res.get("unavailable"), q)
            self.assertNotIn("الكرة", res["answer_ar"])
            self.assertNotIn("100% verified", res["answer_en"])

    def test_admin_paper_query_in_another_lesson_skips_the_ball_games_paper(self):
        res = ask("حل السؤال الأول", "lesson_g8_t1_ch01", admin=True)
        self.assertNotIn("11 starting players", res["answer_en"])  # Q1 of the Ball Games paper

    def test_ball_games_paper_fallback_still_answers_in_its_own_lesson(self):
        res = ask("حل الورقة كاملة", "lesson_01_ball_games")
        self.assertFalse(res.get("unavailable"))
        self.assertIn("11 starting players", res["answer_en"])
        self.assertNotIn("100% verified", res["answer_en"])


if __name__ == "__main__":
    unittest.main()

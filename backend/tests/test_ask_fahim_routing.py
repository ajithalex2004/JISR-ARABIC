import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from backend.modules.tutoring import assistant
from backend.schemas import AskFahimRequest

GEMINI_JSON = '''{
  "teacher_name": "Ask Fahim (اسأل فاهم)",
  "answer_ar": "وَسِيلَةٌ تَعْنِي طَرِيقَةً أَوْ أَدَاةً.",
  "answer_en": "Wasila means a means or a tool.",
  "page_reference": "p. 11",
  "lesson_title": "Money",
  "escalated_to_tutor": false,
  "tutor_escalation_message": null
}'''


class TestAskFahimRouting(unittest.TestCase):
    def _client(self):
        client = MagicMock()
        client.models.generate_content.return_value = MagicMock(text=GEMINI_JSON)
        return client

    def test_vocabulary_question_goes_to_gemini_not_the_fixed_ball_games_table(self):
        client = self._client()
        with patch.object(assistant, "_get_gemini_client", return_value=client):
            res = assistant.ask_fahim(AskFahimRequest(question="ما معنى كلمة وسيلة؟"), db=MagicMock(spec=Session))
        client.models.generate_content.assert_called_once()
        self.assertIn("وَسِيلَةٌ", res["answer_ar"])
        self.assertNotIn("السَّاحِرَةُ المُسْتَدِيرَةُ", res["answer_ar"])

    def test_admin_text_question_goes_to_gemini(self):
        client = self._client()
        actor = SimpleNamespace(role="admin")
        with patch.object(assistant, "_get_gemini_client", return_value=client):
            res = assistant.ask_fahim(AskFahimRequest(question="ما معنى كلمة وسيلة؟"), db=MagicMock(spec=Session), actor=actor)
        client.models.generate_content.assert_called_once()
        self.assertIn("وَسِيلَةٌ", res["answer_ar"])

    def test_fixed_answers_remain_the_fallback_without_gemini(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            res = assistant.ask_fahim(AskFahimRequest(question="ما معنى كلمة وسيلة؟"), db=MagicMock(spec=Session))
        self.assertIn("المُفْرَدَاتِ", res["answer_ar"])

    def test_lesson_context_uses_the_students_lesson_not_ball_games(self):
        db_lesson = SimpleNamespace(title_ar="المال", title_en="Money", grade=6, term=3, start_page=5)
        ctx = assistant._get_lesson_rag_context("g6_t3_l1", db_lesson)
        self.assertIn("Grade 6", ctx)
        self.assertNotIn("Ball", ctx)
        self.assertNotIn("Ball", assistant._get_lesson_rag_context("g6_unknown"))
        self.assertEqual(assistant._lesson_grade("g6_t3_l1", db_lesson), 6)
        self.assertEqual(assistant._lesson_grade("lesson_01_ball_games"), 5)

    def test_prompt_states_the_lessons_grade(self):
        client = self._client()
        db_lesson = SimpleNamespace(title_ar="المال", title_en="Money", grade=6, term=3, start_page=5)
        with patch.object(assistant, "_load_db_lesson", return_value=db_lesson):
            assistant._ask_fahim_gemini(AskFahimRequest(question="ما معنى وسيلة؟", context_lesson_id="g6_t3_l1"), client)
        prompt = client.models.generate_content.call_args.kwargs["contents"]
        self.assertIn("Target Grade: 6", prompt)

    def test_no_open_lesson_uses_the_students_grade_not_ball_games(self):
        client = self._client()
        with patch.object(assistant, "_child_grade", return_value=6):
            assistant._ask_fahim_gemini(AskFahimRequest(question="ما معنى وسيلة؟", child_id="c1"), client, db=MagicMock())
        prompt = client.models.generate_content.call_args.kwargs["contents"]
        self.assertIn("Target Grade: 6", prompt)
        self.assertNotIn("Ball", prompt)

    def test_request_grade_is_used_when_the_child_has_none(self):
        client = self._client()
        assistant._ask_fahim_gemini(AskFahimRequest(question="ما معنى وسيلة؟", grade=7), client)
        self.assertIn("Target Grade: 7", client.models.generate_content.call_args.kwargs["contents"])

    def test_system_prompt_is_not_tied_to_grade_5(self):
        self.assertNotIn("Ball Games", assistant.ASK_FAHIM_SYSTEM_PROMPT)
        self.assertNotIn("Grade 5", assistant.ASK_FAHIM_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()

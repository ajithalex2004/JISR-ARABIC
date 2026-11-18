"""Uploaded question papers: Fahim reads the paper itself and gives answers only.

Covers the causes of wrong / over-long answers: the paper silently dropped (files over 4 MB, or a
text-only retry), another paper's fixed answers served when the AI failed, wrong answers cached
forever, a lite model, and prompts asking for explanations and textbook citations.
"""
import base64
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.modules.tutoring import assistant, caching
from backend.schemas import AskFahimRequest, QuestionPaperSolveRequest

PDF_BYTES = b"%PDF-1.4\n" + b"0" * 64
REPLY = {
    "paper_title": "اختبار الوحدة الثانية",
    "questions": [
        {"question_number": 1, "question_label": "1.a", "question_text_ar": "ضع خطًّا تحت الفاعل: كتب الطالبُ الدرسَ.",
         "question_text_en": "Underline the subject.", "question_type": "grammar",
         "model_answer_ar": "الطَّالِبُ", "model_answer_en": "the student",
         "explanation_ar": "لأنه من قام بالفعل", "explanation_en": "because he did the action",
         "textbook_reference": "كتاب الطالب ص 8 - ألعاب الكرة", "rule_summary_ar": "الفاعل مرفوع", "confidence": "high"},
        {"question_number": 2, "question_text_ar": "السؤال غير واضح في الصورة", "model_answer_ar": "",
         "confidence": "low", "escalated": True, "escalation_reason": "blurred"},
    ],
}


def _b64(data: bytes) -> str:
    return "data:application/pdf;base64," + base64.b64encode(data).decode()


class _Calls:
    """Stands in for the AI gateway: records every call and returns a canned reply (or raises)."""

    def __init__(self, reply=None, error=None):
        self.calls, self.reply, self.error = [], reply, error

    def __call__(self, feature, client, **fields):
        self.calls.append(dict(fields, feature=feature))
        if self.error:
            raise self.error
        return SimpleNamespace(text=json.dumps(self.reply))


class TestQuestionPaperAnswers(unittest.TestCase):
    def setUp(self):
        caching._L1_MEMORY_CACHE.clear()
        self.env = patch.dict(os.environ, {"FAHIM_PAPER_MODEL": "", "FAHIM_DRAFT_MODEL": ""})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(caching._L1_MEMORY_CACHE.clear)

    def _solve(self, gateway, **req):
        req.setdefault("paper_title", "Unit 2 test")
        with patch.object(assistant, "_get_gemini_client", return_value=MagicMock()), \
                patch.object(assistant, "_ai_generate", side_effect=gateway), \
                patch("backend.modules.tutoring.caching.save_cached_paper") as saved:
            result = assistant.solve_question_paper(QuestionPaperSolveRequest(**req), db=MagicMock(spec=Session))
        return result, saved

    def test_gives_answers_only_and_always_sends_the_paper(self):
        gateway = _Calls(REPLY)
        big = PDF_BYTES + b"1" * (4_500_000)  # over the old silent 4 MB cut-off, under the request limit
        result, saved = self._solve(gateway, document_base64=_b64(big), mime_type="application/pdf", grade=7, term=2)

        [call] = gateway.calls
        self.assertEqual(call["attachments"], [(big, "application/pdf")])
        self.assertEqual((call["tier"], call["temperature"]), ("strong", 0.1))
        self.assertIn("Grade: 7 · Term: 2", call["prompt"])
        q1, q2 = result.questions
        self.assertEqual((q1.model_answer_ar, q1.explanation_ar, q1.explanation_en, q1.textbook_reference, q1.rule_summary_ar),
                         ("الطَّالِبُ", "", "", "", None))
        self.assertTrue(q1.question_text_ar.startswith("(1.a) "))
        self.assertEqual((q2.model_answer_ar, q2.escalated), ("", True))
        self.assertIn("1 question(s) could not be read", result.escalation_summary)
        saved.assert_called_once()

    def test_prompt_asks_for_answers_only_and_is_not_tied_to_one_lesson(self):
        prompt = assistant.QUESTION_PAPER_SYSTEM_PROMPT
        self.assertIn("ANSWER ONLY", prompt)
        for leftover in ("Ball Games", "ألعاب الكرة", "lesson_01", "Grade 5", "step-by-step"):
            self.assertNotIn(leftover, prompt)
        self.assertNotIn("solve it thoroughly with full linguistic explanation", assistant.ATTACHMENT_SYSTEM_PROMPT)

    def test_ai_failure_on_an_uploaded_paper_never_gives_another_papers_answers(self):
        for error in (ValueError("model returned garbage"), RuntimeError("400 invalid argument")):
            gateway = _Calls(error=error)
            with self.assertRaises(ApplicationError) as raised:
                self._solve(gateway, document_base64=_b64(PDF_BYTES), text_content="خيل")  # "خيل" used to trigger a fixed paper
            self.assertEqual(raised.exception.status_code, 502)
            self.assertEqual(len(gateway.calls), 1)  # no second, text-only attempt without the paper
            self.assertIn("could not read this question paper", raised.exception.detail)

    def test_reply_without_questions_or_bad_json_is_reported_not_cached(self):
        for text in (json.dumps({"questions": []}), "{not json"):
            with patch.object(assistant, "_get_gemini_client", return_value=MagicMock()), \
                    patch.object(assistant, "_ai_generate", return_value=SimpleNamespace(text=text)), \
                    patch("backend.modules.tutoring.caching.save_cached_paper") as saved:
                with self.assertRaises(ApplicationError) as raised:
                    assistant.solve_question_paper(QuestionPaperSolveRequest(document_base64=_b64(PDF_BYTES)),
                                                   db=MagicMock(spec=Session))
            self.assertEqual(raised.exception.status_code, 502)
            saved.assert_not_called()

    def test_papers_use_the_stronger_model_when_configured(self):
        for env, expected in (({"FAHIM_PAPER_MODEL": "paper-model", "FAHIM_DRAFT_MODEL": "draft-model"}, "paper-model"),
                              ({"FAHIM_PAPER_MODEL": "", "FAHIM_DRAFT_MODEL": "draft-model"}, "draft-model"),
                              ({"FAHIM_PAPER_MODEL": "", "FAHIM_DRAFT_MODEL": ""}, assistant.GEMINI_MODEL)):
            gateway = _Calls(REPLY)
            with patch.dict(os.environ, env):
                self._solve(gateway, document_base64=_b64(PDF_BYTES))
            self.assertEqual(gateway.calls[0]["gemini_model"], expected)

    def test_answers_cached_before_this_fix_are_not_served(self):
        payload = _b64(PDF_BYTES)
        old_key = __import__("hashlib").sha256(payload.split(",", 1)[1].encode()).hexdigest()
        caching._L1_MEMORY_CACHE[old_key] = {"data": {"questions": [{"question_number": 1}]}}
        self.assertNotEqual(caching.compute_content_hash(payload), old_key)
        self.assertIsNone(caching.get_cached_paper(caching.compute_content_hash(payload), None, db=None))

    def test_chat_question_about_a_document_never_retries_without_it(self):
        gateway = _Calls(error=RuntimeError("upload rejected"))
        req = AskFahimRequest(question="حل السؤال الأول", attachment_base64=_b64(PDF_BYTES),
                              attachment_type="pdf", attachment_name="paper.pdf")
        with patch.object(assistant, "_ai_generate", side_effect=gateway):
            self.assertIsNone(assistant._ask_fahim_gemini(req, MagicMock()))
        self.assertEqual(len(gateway.calls), 1)
        self.assertEqual(gateway.calls[0]["tier"], "strong")
        self.assertIn("Give ONLY the answers", gateway.calls[0]["prompt"])


if __name__ == "__main__":
    unittest.main()

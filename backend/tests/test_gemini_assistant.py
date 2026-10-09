import os
import json
import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from backend.schemas import (
    AskFahimRequest,
    SocraticLearnRequest,
    SocraticLearnResponse,
    SpeechEvaluationRequest,
    QuestionPaperSolveRequest,
)
from backend.modules.tutoring import assistant
from backend.modules.curriculum import audio
from backend.models import TutorSubmission

class TestGeminiAssistant(unittest.TestCase):
    def test_ask_fahim_fallback_when_no_api_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(question="ما هي كرة القدم؟")
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertEqual(res["teacher_name"], "Ask Fahim (اسأل فاهم)")
            self.assertIn("11 لاعباً", res["answer_ar"])
            self.assertFalse(res["escalated_to_tutor"])

    def test_socratic_learn_fallback_primary_tone(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = SocraticLearnRequest(
                topic="التاء المربوطة",
                student_input="نضع ضمة على الكلمة",
                grade=5
            )
            res = assistant.socratic_learn(req)
            self.assertEqual(res.tone, "primary_gamified")
            self.assertTrue(res.is_step_mastered)
            self.assertIn("بطل", res.response_ar)

    def test_gemini_ask_fahim_success(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''{
            "teacher_name": "Ask Fahim (اسأل فاهم)",
            "answer_ar": "كُرَةُ القَدَمِ رِيَاضَةٌ رَائِعَةٌ تُعَزِّزُ التَّعَاوُنَ وَاللَّعِبَ النَّظِيفَ.",
            "answer_en": "Football is a wonderful sport that fosters cooperation and fair play.",
            "page_reference": "Chapter 1: Ball Games, p. 8",
            "lesson_title": "أَلْعَابُ الكُرَةِ (Ball Games)",
            "escalated_to_tutor": false,
            "tutor_escalation_message": null
        }'''
        mock_client.models.generate_content.return_value = mock_response

        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=mock_client):
            req = AskFahimRequest(question="ما هي فوائد اللعب الجماعي؟")
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertEqual(res["teacher_name"], "Ask Fahim (اسأل فاهم)")
            self.assertIn("رِيَاضَةٌ", res["answer_ar"])
            self.assertFalse(res["escalated_to_tutor"])
            mock_client.models.generate_content.assert_called_once()
            # Verify model used is gemini-2.0-flash
            call_kwargs = mock_client.models.generate_content.call_args.kwargs
            self.assertEqual(call_kwargs["model"], assistant.GEMINI_MODEL)

    def test_gemini_socratic_learn_success_primary(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''{
            "teacher_name": "Ustadh Fahim (معلمك فاهم)",
            "tone": "primary_gamified",
            "response_ar": "مُمْتَازٌ جِدًّا يَا بَطَلَ الإِمَارَاتِ! 🌟",
            "response_en": "Superb, champion! You figured out that tanween reveals the taa marbutah.",
            "guiding_hint_ar": "جرّب كلمة (مدرسة) الآن.",
            "guiding_hint_en": "Try with the word madrasa now.",
            "is_step_mastered": true,
            "next_socratic_prompt_ar": "كيف تكتبها الآن؟"
        }'''
        mock_client.models.generate_content.return_value = mock_response

        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=mock_client):
            req = SocraticLearnRequest(
                topic="التاء المربوطة",
                student_input="سمعت صوت التاء عند التنوين",
                grade=5
            )
            res = assistant.socratic_learn(req)
            self.assertEqual(res.tone, "primary_gamified")
            self.assertTrue(res.is_step_mastered)
            self.assertIn("بَطَلَ", res.response_ar)

    def test_gemini_error_falls_back_cleanly(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Quota Exceeded")

        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=mock_client):
            req = AskFahimRequest(question="كرة القدم")
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertEqual(res["teacher_name"], "Ask Fahim (اسأل فاهم)")
            self.assertIn("11 لاعباً", res["answer_ar"])

    def test_ask_fahim_multi_lesson_horse_riding(self):
        """Test multi-lesson RAG fallback grounds correctly in Lesson 2: Horse Riding."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="ما هي رياضة ركوب الخيل وأين يقام كأس دبي العالمي؟",
                context_lesson_id="lesson_02_horse_riding"
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertEqual(res["teacher_name"], "Ask Fahim (اسأل فاهم)")
            self.assertIn("الفروسية", res["answer_ar"])
            self.assertIn("Page 16", res["page_reference"])
            self.assertFalse(res["escalated_to_tutor"])

    def test_ask_fahim_multi_lesson_arts_and_fun_time(self):
        """Test multi-lesson RAG fallback grounds correctly in Lesson 4 and Lesson 10."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            # Lesson 4 Arts
            req_arts = AskFahimRequest(question="ماذا نتعلم في درس الفنون والرسم؟")
            res_arts = assistant.ask_fahim(req_arts, db=MagicMock(spec=Session))
            self.assertIn("الفنون", res_arts["answer_ar"])
            self.assertIn("Page 36", res_arts["page_reference"])

            # Lesson 10 Fun Time
            req_fun = AskFahimRequest(question="كيف نقضي وقت المرح في صحراء دبي؟")
            res_fun = assistant.ask_fahim(req_fun, db=MagicMock(spec=Session))
            self.assertIn("المرح", res_fun["answer_ar"])
            self.assertIn("Page 96", res_fun["page_reference"])

    def test_ask_fahim_escalation_persists_to_db(self):
        """When query escalates, it persists a pending TutorSubmission ticket."""
        mock_db = MagicMock(spec=Session)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="هل يمكن للأستاذ أن يشرح لي قصيدة البردة بيت بيت وكيف أحلل الصور البلاغية المعقدة؟",
                child_id="child-1234",
                context_lesson_id="lesson_05_reading"
            )
            res = assistant.ask_fahim(req, db=mock_db)
            self.assertTrue(res["escalated_to_tutor"])
            self.assertIn("معلمك الخاص", res["answer_ar"])
            # Verify TutorSubmission was added to DB
            mock_db.add.assert_called_once()
            added_sub = mock_db.add.call_args[0][0]
            self.assertEqual(added_sub.child_id, "child-1234")
            self.assertEqual(added_sub.submission_type, "ask_fahim_escalation")
            self.assertEqual(added_sub.status, "pending")
            mock_db.commit.assert_called_once()

    def test_speech_evaluation_perfect(self):
        """Test speech evaluation with matching target phrase produces high score and pass."""
        req = SpeechEvaluationRequest(
            target_phrase="كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الشَّعْبِيَّةُ الأُولَى",
            spoken_text="كرة القدم هي اللعبة الشعبية الأولى"
        )
        res = audio.evaluate_pronunciation(req)
        self.assertGreaterEqual(res["overall_score"], 90.0)
        self.assertTrue(res["is_pass"])
        self.assertIn("ممتاز", res["fluency_rating"])

    def test_speech_evaluation_phoneme_confusion(self):
        """Test speech evaluation detects phoneme substitution (ث -> س)."""
        req = SpeechEvaluationRequest(
            target_phrase="ثَلَاثَةُ فُرْسَانٍ فِي المَيْدَانِ",
            spoken_text="سلاسة فرسان في الميدان"
        )
        res = audio.evaluate_pronunciation(req)
        self.assertIn("ث/س", res["phoneme_scores"])
        self.assertLess(res["phoneme_scores"]["ث/س"], 95.0)
        self.assertTrue(len(res["detected_mistakes"]) > 0)
        self.assertIn("استبدال", res["detected_mistakes"][0])

    def test_gemini_solve_question_paper_success(self):
        """Test Gemini 2.0 Flash solves question paper with zero escalation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''{
            "paper_title": "اختبار منتصف الفصل الأول - لغة عربية",
            "grade": 5,
            "term": 1,
            "total_questions": 1,
            "questions": [
                {
                    "question_number": 1,
                    "question_text_ar": "كم عدد اللاعبين في فريق كرة القدم؟",
                    "question_text_en": "How many players on a football team?",
                    "question_type": "reading_comprehension",
                    "model_answer_ar": "11 لاعباً أساسياً",
                    "model_answer_en": "11 starting players",
                    "explanation_ar": "يحدد نص الكتاب المدرسي أن كل فريق يضم 11 لاعباً.",
                    "explanation_en": "Textbook specifies 11 players per team.",
                    "textbook_reference": "كتاب الطالب ص 8 - ألعاب الكرة",
                    "lesson_id": "lesson_01_ball_games",
                    "rule_summary_ar": "فهم المقروء واستخراج الحقائق المباشرة.",
                    "confidence": "high",
                    "escalated": false,
                    "escalation_reason": null
                }
            ],
            "model_used": "gemini-2.0-flash",
            "escalation_summary": "تم حل جميع الأسئلة ذاتيا"
        }'''
        mock_client.models.generate_content.return_value = mock_response

        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=mock_client):
            req = QuestionPaperSolveRequest(
                paper_title="اختبار الصف الخامس",
                text_content="سؤال 1: كم عدد اللاعبين في فريق كرة القدم؟"
            )
            res = assistant.solve_question_paper(req, db=MagicMock(spec=Session))
            self.assertEqual(res.total_questions, 1)
            self.assertEqual(res.questions[0].model_answer_ar, "11 لاعباً أساسياً")
            self.assertFalse(res.questions[0].escalated)
            self.assertEqual(res.model_used, "AI Assistant")
            call_kwargs = mock_client.models.generate_content.call_args.kwargs
            self.assertEqual(call_kwargs["model"], assistant.GEMINI_MODEL)

    def test_solve_question_paper_fallback(self):
        """Test fallback curriculum solver when no Gemini API key is present."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = QuestionPaperSolveRequest(
                paper_title="اختبار تجريبي",
                text_content="رياضة ركوب الخيل وكأس دبي"
            )
            res = assistant.solve_question_paper(req, db=MagicMock(spec=Session))
            self.assertEqual(res.total_questions, 3)
            self.assertIn("مَيْدَان", res.questions[0].model_answer_ar)
            self.assertFalse(res.questions[0].escalated)
            self.assertEqual(res.questions[1].question_type, "grammar_parsing")
            self.assertIn("فَاعِلٌ", res.questions[1].model_answer_ar)

    def test_solve_question_paper_selective_escalation(self):
        """Test that force_escalation persists a TutorSubmission ticket in DB."""
        mock_db = MagicMock(spec=Session)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = QuestionPaperSolveRequest(
                paper_title="ورقة مراجعة صعبة",
                child_id="child-test-1",
                force_escalation=True
            )
            res = assistant.solve_question_paper(req, db=mock_db)
            self.assertTrue(all(q.escalated for q in res.questions))
            self.assertGreaterEqual(mock_db.add.call_count, 1)
            mock_db.commit.assert_called()

    def test_ask_fahim_with_pdf_attached_never_leaks_ball_games(self):
        """When PDF is attached, Fahim must NEVER fall back to Ball Games curriculum or Sami."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="[pdf: arabic_grade5_exam.pdf] ما إعراب جملة سجل اللاعب الهدف؟",
                attachment_name="arabic_grade5_exam.pdf",
                attachment_type="pdf"
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertEqual(res["teacher_name"], "Ask Fahim (اسأل فاهم)")
            # Must strictly NOT contain the Ball Games curriculum fallback:
            self.assertNotIn("الساحرة المستديرة", res["answer_ar"])
            self.assertNotIn("ألعاب الكرة", res["answer_ar"])
            self.assertIn("arabic_grade5_exam.pdf", res["answer_ar"])

    def test_ask_fahim_with_pdf_attached_question_paper_solve(self):
        """When PDF is attached, Fahim targets the document and never falls back to Ball Games."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="[pdf: exam_paper.pdf] حل ورقة الأسئلة كاملة",
                attachment_name="exam_paper.pdf",
                attachment_type="pdf"
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertEqual(res["teacher_name"], "Ask Fahim (اسأل فاهم)")
            self.assertIn("exam_paper.pdf", res["answer_ar"])
            self.assertNotIn("الساحرة المستديرة", res["answer_ar"])

    def test_ask_fahim_with_pdf_attached_textbook_summary(self):
        """When PDF is attached, summary inquiry targets the uploaded document."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="[pdf: book.pdf] لخص لي هذا المستند",
                attachment_name="book.pdf",
                attachment_type="pdf"
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertIn("book.pdf", res["answer_ar"])
            self.assertNotIn("الساحرة المستديرة", res["answer_ar"])

    def test_ask_fahim_with_pdf_attached_empty_or_greeting_shows_welcome(self):
        """When student attaches a PDF, Fahim provides a helpful document-specific greeting."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="[pdf: exam.pdf] أهلاً",
                attachment_name="exam.pdf",
                attachment_type="pdf"
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertIn("exam.pdf", res["answer_ar"])
            self.assertIn("Received your attached document", res["answer_ar"])

    def test_admin_fahim_with_pdf_attached_never_leaks_ball_games(self):
        """Admin with attached PDF targets the document and never falls back to Ball Games."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="[pdf: moe_doc.pdf] ما إعراب كلمة اللاعب في جملة سجل اللاعب الهدف؟",
                child_id="admin_supervisor",
                attachment_name="moe_doc.pdf",
                attachment_type="pdf"
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            self.assertIn("moe_doc.pdf", res["answer_ar"])
            self.assertNotIn("الساحرة المستديرة", res["answer_ar"])

    def test_ask_fahim_solve_question_1_bilingual_qa(self):
        """Curriculum Question 1 must provide English translation directly beneath every Arabic question and answer."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            req = AskFahimRequest(
                question="حل السؤال الأول",
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            ans_ar = res["answer_ar"]
            # Verify bilingual marker is present
            self.assertIn("🇬🇧", ans_ar)
            # Verify Arabic question and English question are interleaved
            self.assertIn("نَصُّ السُّؤَالِ", ans_ar)
            self.assertIn("Question: How many starting players", ans_ar)
            # Verify Arabic answer and English answer are interleaved
            self.assertIn("الإِجَابَةُ النَّمُوذَجِيَّةُ", ans_ar)
            self.assertIn("Model Answer: 11 starting players", ans_ar)
            # Verify explanation is bilingual
            self.assertIn("الشَّرْحُ وَالتَّعْلِيلُ", ans_ar)
            # Verify Arabic answer and English answer are interleaved
            self.assertIn("الإِجَابَةُ النَّمُوذَجِيَّةُ", ans_ar)
            self.assertIn("Model Answer: 11 starting players", ans_ar)
            # Verify explanation is bilingual
            self.assertIn("الشَّرْحُ وَالتَّعْلِيلُ", ans_ar)
            self.assertIn("Explanation:", ans_ar)

    def test_ask_fahim_attachment_calls_gemini_first(self):
        """When an attachment is present and Gemini is available, Gemini is called directly to answer from document."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "teacher_name": "Ask Fahim (اسأل فاهم)",
            "question_en": "What is the result in the attached custom document?",
            "answer_ar": "بناءً على المستند المرفق، النتيجة واضحة ومحلولة بالذكاء الاصطناعي.",
            "answer_en": "Based on the attached document, the result is solved using AI skills and power.",
            "page_reference": "custom_file.pdf",
            "lesson_title": "تحليل وثيقة الطالب: custom_file.pdf",
            "escalated_to_tutor": False
        })
        mock_client.models.generate_content.return_value = mock_response

        with patch("backend.modules.tutoring.assistant._get_gemini_client", return_value=mock_client):
            req = AskFahimRequest(
                question="حل السؤال الأول من الوثيقة المرفقة",
                attachment_name="custom_file.pdf",
                attachment_type="pdf",
                attachment_base64="JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCg=="
            )
            res = assistant.ask_fahim(req, db=MagicMock(spec=Session))
            mock_client.models.generate_content.assert_called_once()
            self.assertIn("custom_file.pdf", res["page_reference"])
            self.assertIn("المستند المرفق", res["answer_ar"])


if __name__ == "__main__":
    unittest.main()



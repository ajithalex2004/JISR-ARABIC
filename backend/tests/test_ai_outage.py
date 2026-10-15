"""While Gemini is down, learners are told kindly instead of getting canned Grade 5 answers."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.errors import ApplicationError
from backend.main import app
from backend.models import BookEdition, ScannedPage
from backend.modules.tutoring import assistant
from backend.redis_client import _fallback_cache, _fallback_rate_buckets
from backend.schemas import AskFahimRequest, QuestionPaperSolveRequest, SocraticLearnRequest


def _client_raising(exc):
    def generate_content(**_kwargs):
        raise exc
    return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))


OUT_OF_CREDITS = RuntimeError("402 RESOURCE_EXHAUSTED. Your prepayment credits are depleted.")


class TestAiOutage(unittest.TestCase):
    def setUp(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    def tearDown(self):
        self.engine.dispose()
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()

    def test_ask_fahim_says_fahim_is_resting_when_gemini_is_down(self):
        with self.session() as db, patch.object(assistant, "_get_gemini_client", return_value=_client_raising(OUT_OF_CREDITS)):
            answer = assistant.ask_fahim(AskFahimRequest(question="ما معنى كلمة مدرسة؟"), db=db)
        self.assertTrue(answer["ai_unavailable"])
        self.assertIn("try again", answer["answer_en"])
        self.assertNotIn("Ball Games", answer["lesson_title"])

    def test_bug_in_reply_handling_still_uses_the_old_fallback(self):
        with self.session() as db, patch.object(assistant, "_get_gemini_client", return_value=_client_raising(ValueError("bad json"))):
            answer = assistant.ask_fahim(AskFahimRequest(question="ما معنى كلمة مدرسة؟"), db=db)
        self.assertFalse(answer.get("ai_unavailable", False))

    def test_socratic_learn_says_fahim_is_resting(self):
        with patch.object(assistant, "_get_gemini_client", return_value=_client_raising(OUT_OF_CREDITS)):
            reply = assistant.socratic_learn(SocraticLearnRequest(topic="التاء المربوطة", student_input="لا أعرف", grade=3))
        self.assertEqual(reply.response_en, assistant.FAHIM_RESTING_EN)

    def test_paper_solver_refuses_instead_of_caching_a_wrong_paper(self):
        with self.session() as db, \
                patch.object(assistant, "_get_gemini_client", return_value=_client_raising(OUT_OF_CREDITS)), \
                patch("backend.modules.tutoring.caching.save_cached_paper") as saved:
            with self.assertRaises(ApplicationError) as raised:
                assistant.solve_question_paper(QuestionPaperSolveRequest(text_content="س1: أعرب: جاء الولد"), db=db)
        self.assertEqual(raised.exception.status_code, 503)
        saved.assert_not_called()

    def test_reader_page_count_needs_no_admin_login(self):
        with self.session() as db:
            db.add(BookEdition(id="moe_gr1_vol1_2023", title="G1", total_pages=100))
            db.add_all([ScannedPage(book_edition_id="moe_gr1_vol1_2023", pdf_page=p, printed_page=p,
                                    ocr_text_ar="نص", review_status="ai_ocr") for p in (1, 2, 97)])
            db.add(BookEdition(id="moe_gr2_vol1_2023", title="G2", total_pages=80))
            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        try:
            client = TestClient(app)
            self.assertEqual(client.get("/api/curriculum/textbook-info/moe_gr1_vol1_2023").json()["total_pages"], 97)
            self.assertEqual(client.get("/api/curriculum/textbook-info/moe_gr2_vol1_2023").json()["total_pages"], 80)
            self.assertIsNone(client.get("/api/curriculum/textbook-info/unknown").json()["total_pages"])
            client.close()
        finally:
            app.dependency_overrides.pop(get_db, None)


if __name__ == "__main__":
    unittest.main()

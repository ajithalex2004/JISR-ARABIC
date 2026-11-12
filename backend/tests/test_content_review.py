"""Teacher review of textbook pages and of word meanings."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.models import CurriculumAuditEvent, ScannedPage, WordGloss
from backend.modules.curriculum import glossary
from backend.modules.curriculum.page_review import mark_page_reviewed
from backend.modules.curriculum.word_review import (
    canonical_word, list_queue, review_word, teacher_decisions, word_corrections,
)
from backend.redis_client import cache_clear


class ReviewTestCase(unittest.TestCase):
    def setUp(self):
        cache_clear()
        glossary._cache.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

    def tearDown(self):
        cache_clear()
        glossary._cache.clear()
        self.db.close()
        self.engine.dispose()


class TestPageReview(ReviewTestCase):
    def test_marks_a_page_checked_and_saves_a_correction(self):
        self.db.add(ScannedPage(book_edition_id="moe_gr3_vol2_2023", pdf_page=9, printed_page=8,
                                ocr_text_ar="الكتاب صغير الحجن", review_status="ocr_vision_verified"))
        self.db.commit()
        result = mark_page_reviewed(self.db, "moe_gr3_vol2_2023", 9, actor_id="teacher1", note="fixed one word",
                                    corrected_text="الكتاب صغير الحجم")
        self.assertTrue(result["text_corrected"])
        page = self.db.query(ScannedPage).one()
        self.assertEqual((page.review_status, page.reviewed_by, page.ocr_text_ar), ("reviewed", "teacher1", "الكتاب صغير الحجم"))
        self.assertIsNotNone(page.reviewed_at)
        self.assertEqual(self.db.query(CurriculumAuditEvent).filter_by(action="page_review").count(), 1)
        # Same text again is a check without a correction.
        self.assertFalse(mark_page_reviewed(self.db, "moe_gr3_vol2_2023", 9, actor_id="t2", corrected_text="الكتاب صغير الحجم")["text_corrected"])

    def test_unknown_page_is_a_404(self):
        with self.assertRaises(ApplicationError) as ctx:
            mark_page_reviewed(self.db, "moe_gr3_vol2_2023", 99, actor_id="t")
        self.assertEqual(ctx.exception.status_code, 404)


class TestWordReview(ReviewTestCase):
    def test_canonical_key_matches_the_website(self):
        self.assertEqual(canonical_word("المَدْرَسَةُ،"), canonical_word("المدرسه"))
        self.assertEqual(canonical_word("إِلَى"), "الي")

    def test_ai_meanings_are_queued_once_and_a_teacher_decision_wins(self):
        ai = {"translation": "spoils", "part_of_speech": "noun", "source": "gemini"}
        with patch.object(glossary, "_gemini_gloss", return_value=ai) as gem, patch.object(glossary, "_machine_translation", return_value=None):
            self.assertEqual(glossary.gloss_word("المغنومات", "سياق", db=self.db)["translation"], "spoils")
            glossary.gloss_word("المغنومات", "سياق", db=self.db)  # cached, not queued twice
            self.assertEqual(gem.call_count, 1)
        self.assertEqual(list_queue(self.db)["counts"]["pending"], 1)

        review_word(self.db, word="المَغْنُومَاتُ", action="correct", translation="goods", part_of_speech="noun", actor_id="t1")
        self.assertEqual(glossary.gloss_word("المغنومات", "سياق", db=self.db),
                         {"translation": "goods", "part_of_speech": "noun", "source": "teacher"})
        batch = glossary.gloss_words(["المغنومات"], "سياق", db=self.db)
        self.assertEqual(batch["المغنومات"]["translation"], "goods")
        counts = list_queue(self.db)["counts"]
        self.assertEqual((counts["pending"], counts["corrected"]), (0, 1))

    def test_rejected_meaning_is_not_shown(self):
        review_word(self.db, word="كلمة", action="reject", actor_id="t1", current="a wrong meaning", source="dictionary")
        self.assertIsNone(glossary.gloss_word("كلمة", db=self.db))
        self.assertEqual(word_corrections(self.db)[canonical_word("كلمة")]["translation"], None)

    def test_built_in_words_can_be_approved_and_reach_the_website(self):
        review_word(self.db, word="الكُرَةُ", action="approve", actor_id="t1", current="The ball", source="dictionary")
        row = self.db.query(WordGloss).one()
        self.assertEqual((row.status, row.source, row.translation), ("approved", "dictionary", "The ball"))
        self.assertEqual(word_corrections(self.db), {canonical_word("الكرة"): {"translation": "The ball", "part_of_speech": None}})
        self.assertEqual(teacher_decisions(self.db, ["الكرة"])["الكرة"]["translation"], "The ball")

    def test_bad_requests(self):
        for kwargs in ({"word": "", "action": "approve"}, {"word": "كلمة", "action": "delete"},
                       {"word": "كلمة", "action": "correct", "translation": ""},
                       {"word": "كلمة", "action": "approve"},  # nothing to approve
                       {"word": "كلمة", "action": "correct", "translation": "x", "part_of_speech": "thing"}):
            with self.assertRaises(ApplicationError):
                review_word(self.db, actor_id="t1", **kwargs)

    def test_without_a_database_lookups_still_work(self):
        with patch.object(glossary, "_gemini_gloss", return_value={"translation": "ball", "part_of_speech": "noun", "source": "gemini"}):
            self.assertEqual(glossary.gloss_word("كرة")["translation"], "ball")


class TestReviewEndpoints(unittest.TestCase):
    def test_only_staff_can_review(self):
        from fastapi.testclient import TestClient
        from backend.api.dependencies import get_current_user
        from backend.main import app
        from backend.modules.identity.access import Principal
        app.dependency_overrides[get_current_user] = lambda: Principal(id="p1", email="p@test.local", role="parent", is_verified=True)
        try:
            with TestClient(app) as client:
                self.assertEqual(client.post("/api/admin/pages/moe_gr3_vol2_2023/9/teacher-review", json={}).status_code, 403)
                self.assertEqual(client.get("/api/admin/word-glosses").status_code, 403)
                self.assertEqual(client.post("/api/admin/word-glosses/review", json={"word": "كلمة", "action": "reject"}).status_code, 403)
        finally:
            app.dependency_overrides.pop(get_current_user, None)


if __name__ == "__main__":
    unittest.main()

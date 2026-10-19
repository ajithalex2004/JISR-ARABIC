import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import SentenceAlignment
from backend.modules.curriculum import alignment

HORSE_AR = "الحِصَانُ سَرِيعٌ."
HORSE_EN = "The horse is fast."


def _ai(payload):
    class Response:
        text = json.dumps(payload)
        provider = "gemini"
    return Response()


class TestValidation(unittest.TestCase):
    def test_valid_chunks_are_sorted_and_kept(self):
        chunks = [{"ar": [1], "en": [3]}, {"ar": [0], "en": [0, 1]}]
        self.assertEqual(alignment.validate_chunks(HORSE_AR, HORSE_EN, chunks),
                         [{"ar": [0], "en": [0, 1]}, {"ar": [1], "en": [3]}])

    def test_rejects_bad_alignments(self):
        bad = [
            [{"ar": [0], "en": [9]}],                            # English index out of range
            [{"ar": [0], "en": [1]}, {"ar": [0], "en": [3]}],     # Arabic word used twice
            [{"ar": [0], "en": [1]}],                            # too little of the sentence covered
            [{"ar": [0, 2], "en": [1]}],                          # Arabic chunk not consecutive / out of range
            [{"ar": [True], "en": [1]}],
            "not a list",
        ]
        for chunks in bad:
            self.assertIsNone(alignment.validate_chunks(HORSE_AR, HORSE_EN, chunks), chunks)

    def test_catalogue_pairs_include_examples_and_passage_sentences(self):
        from backend.curriculum_catalog import FULL_CURRICULUM_CATALOG
        pairs = alignment.catalogue_sentence_pairs(FULL_CURRICULUM_CATALOG["lesson_02_horse_riding"])
        self.assertIn((HORSE_AR, HORSE_EN), pairs)
        self.assertGreater(len(pairs), 15)
        self.assertIn(alignment.pair_id(HORSE_AR, HORSE_EN), alignment._catalogue_ids())


class TestAlignmentEndpoint(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

        def db():
            session = self.Session()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(get_db, None)

    def _post(self, pairs):
        return self.client.post("/api/curriculum/alignments", json={"pairs": pairs})

    def test_aligns_catalogue_sentences_once_and_stores_them(self):
        reply = _ai({"alignments": [
            {"pair": 0, "chunks": [{"ar": [0], "en": [0, 1]}, {"ar": [1], "en": [3]}]},
        ]})
        with patch("backend.ai.gateway.available", return_value=True), \
             patch("backend.ai.gateway.generate", return_value=reply) as gen:
            first = self._post([{"ar": HORSE_AR, "en": HORSE_EN}, {"ar": "مرحبا", "en": "Hello"}]).json()
            second = self._post([{"ar": HORSE_AR, "en": HORSE_EN}]).json()
        gen.assert_called_once()  # stored, and the non-catalogue sentence never reaches the AI
        self.assertEqual(first["alignments"][0], [{"ar": [0], "en": [0, 1]}, {"ar": [1], "en": [3]}])
        self.assertIsNone(first["alignments"][1])
        self.assertEqual(second["alignments"][0], first["alignments"][0])
        self.assertIn("Pair 0", gen.call_args.args[0].prompt)

    def test_failed_check_is_stored_as_unusable_and_not_retried(self):
        with patch("backend.ai.gateway.available", return_value=True), \
             patch("backend.ai.gateway.generate", return_value=_ai({"alignments": [{"pair": 0, "chunks": [{"ar": [0], "en": [7]}]}]})) as gen:
            self.assertIsNone(self._post([{"ar": HORSE_AR, "en": HORSE_EN}]).json()["alignments"][0])
            self.assertIsNone(self._post([{"ar": HORSE_AR, "en": HORSE_EN}]).json()["alignments"][0])
        gen.assert_called_once()
        db = self.Session()
        self.assertEqual(db.get(SentenceAlignment, alignment.pair_id(HORSE_AR, HORSE_EN)).status, "unusable")
        db.close()

    def test_ai_down_returns_nothing_and_stores_nothing(self):
        with patch("backend.ai.gateway.available", return_value=False):
            self.assertIsNone(self._post([{"ar": HORSE_AR, "en": HORSE_EN}]).json()["alignments"][0])
        db = self.Session()
        self.assertEqual(db.query(SentenceAlignment).count(), 0)
        db.close()

    def test_rejected_alignments_are_hidden(self):
        db = self.Session()
        db.add(SentenceAlignment(id=alignment.pair_id(HORSE_AR, HORSE_EN), arabic=HORSE_AR, english=HORSE_EN,
                                 chunks_json='[{"ar": [0], "en": [0, 1]}]', status="rejected"))
        db.commit()
        db.close()
        self.assertIsNone(self._post([{"ar": HORSE_AR, "en": HORSE_EN}]).json()["alignments"][0])

    def test_request_limits(self):
        self.assertEqual(self._post([]).status_code, 422)
        self.assertEqual(self._post([{"ar": "ا" * 601, "en": "x"}]).status_code, 422)


PAGE = {
    "paragraphs": ["الدَّرْسُ الأَوَّلُ", "الحِصَانُ سَرِيعٌ.\nالوَلَدُ يَلْعَبُ.", "سطر واحد\nسطر ثان"],
    "paragraphs_en": ["Lesson one", "The horse is fast.\nThe boy plays.", "Only one English line"],
}


class TestPageAlignments(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()

    def tearDown(self):
        self.db.close()

    def test_line_pairs_skip_paragraphs_whose_line_counts_differ(self):
        self.assertEqual(alignment.page_line_pairs(PAGE), [
            ("الدَّرْسُ الأَوَّلُ", "Lesson one"),
            ("الحِصَانُ سَرِيعٌ.", "The horse is fast."),
            ("الوَلَدُ يَلْعَبُ.", "The boy plays."),
        ])
        self.assertEqual(alignment.page_line_pairs({"paragraphs": None}), [])

    def test_page_text_comes_from_the_server_and_lines_are_aligned(self):
        reply = _ai({"alignments": [
            {"pair": 0, "chunks": [{"ar": [0], "en": [1]}, {"ar": [1], "en": [0]}]},
            {"pair": 1, "chunks": [{"ar": [0], "en": [0, 1]}, {"ar": [1], "en": [3]}]},
            {"pair": 2, "chunks": [{"ar": [0], "en": [0]}]},  # covers too little: dropped
        ]})
        with patch("backend.modules.curriculum.authoring.get_ocr_page", return_value=PAGE) as page, \
             patch("backend.ai.gateway.available", return_value=True), \
             patch("backend.ai.gateway.generate", return_value=reply) as gen:
            lines = alignment.get_page_alignments(self.db, 14, "moe_gr7_vol1_2023")
            again = alignment.get_page_alignments(self.db, 14, "moe_gr7_vol1_2023")
        page.assert_called_with(pdf_page=14, edition_id="moe_gr7_vol1_2023", db=self.db)
        gen.assert_called_once()  # stored after the first visit
        self.assertEqual([line["en"] for line in lines], ["Lesson one", "The horse is fast."])
        self.assertEqual(lines[1]["chunks"], [{"ar": [0], "en": [0, 1]}, {"ar": [1], "en": [3]}])
        self.assertEqual(again, lines)

    def test_large_pages_are_aligned_in_batches(self):
        many = {"paragraphs": [f"كلمة{i} ثانية" for i in range(20)], "paragraphs_en": [f"word{i} second" for i in range(20)]}

        def reply(request):
            count = request.prompt.count("Pair ")
            return _ai({"alignments": [{"pair": i, "chunks": [{"ar": [0], "en": [0]}, {"ar": [1], "en": [1]}]} for i in range(count)]})

        with patch("backend.modules.curriculum.authoring.get_ocr_page", return_value=many), \
             patch("backend.ai.gateway.available", return_value=True), \
             patch("backend.ai.gateway.generate", side_effect=reply) as gen:
            lines = alignment.get_page_alignments(self.db, 3)
        self.assertEqual(gen.call_count, 2)  # 12 + 8
        self.assertEqual(len(lines), 20)

    def test_endpoint_requires_sign_in(self):
        self.assertEqual(TestClient(app).get("/api/curriculum/page-alignments/14").status_code, 401)


if __name__ == "__main__":
    unittest.main()

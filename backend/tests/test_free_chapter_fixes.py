"""The free-chapter corrections confirmed after the pre-check: each lands, one new version per lesson, once."""
import hashlib
import json
import re
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import CurriculumAuditEvent, Lesson, LessonVersion, Unit
from backend.modules.curriculum.content_fixes import CONTENT_FIXES, _replace_in, apply_content_fixes

# The exact strings that held each error in the live lessons (as published before the fix).
LIVE = json.loads((Path(__file__).parent / "fixtures" / "free_chapter_live_errors.json").read_text(encoding="utf-8"))
FREE_FIXES = [f for f in CONTENT_FIXES if f[0] in LIVE]


class TestFreeChapterFixes(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
        self.db.commit()
        for i, (lesson_id, texts) in enumerate(LIVE.items()):
            self.db.add(Lesson(id=lesson_id, unit_id="u", grade=i + 1, term=1, lesson_order=1, title_ar="د",
                               title_en="L", start_page=6))
            # Each live string as its own field, as word cards, questions and roots are stored.
            body = {"vocabulary_cards": [{"word_ar": "د", "root": "أ-ن-ا" if "أ-ن-ا" in texts else "ك-ت-ب"}],
                    "texts": [t for t in texts if t not in ("أ-ن-ا", "ر-و-ت")]}
            if "ر-و-ت" in texts:
                body["vocabulary_cards"].append({"word_ar": "الرُّوتِينُ", "root": "ر-و-ت"})
            raw = json.dumps(body, ensure_ascii=False)
            self.db.add(LessonVersion(id=f"live_{lesson_id}", lesson_id=lesson_id, version_tag="1.0", content_json=raw,
                                      content_hash=hashlib.sha256(raw.encode()).hexdigest(), status="published",
                                      is_active=True))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_there_are_33_confirmed_corrections_over_ten_free_chapters(self):
        self.assertEqual(len(LIVE), 10)
        # Class 5's oval card is one correction made of two entries (definition + spelling).
        self.assertEqual(len(FREE_FIXES), 34)

    def test_every_fix_finds_its_error_in_the_live_text(self):
        for lesson_id, pattern, _, reason in FREE_FIXES:
            texts = LIVE[lesson_id]
            self.assertTrue(any(re.search(pattern, t) for t in texts), f"{lesson_id}: {reason}")

    def test_one_new_version_per_lesson_and_only_once(self):
        with self.engine.connect() as conn:
            self.assertEqual(sorted(apply_content_fixes(conn)), sorted(LIVE))
            conn.commit()
            self.assertEqual(apply_content_fixes(conn), [])  # a later deploy changes nothing
        self.db.expire_all()
        for lesson_id in LIVE:
            versions = self.db.query(LessonVersion).filter_by(lesson_id=lesson_id).all()
            self.assertEqual(len(versions), 2, lesson_id)
            live = [v for v in versions if v.is_active]
            self.assertEqual(len(live), 1)
            self.assertEqual(live[0].created_by, "content-fix")
            self.assertEqual(hashlib.sha256(live[0].content_json.encode()).hexdigest(), live[0].content_hash)
            # Every error is gone: running any of this lesson's fixes again changes nothing.
            fixed = json.loads(live[0].content_json)
            for lid, pattern, replacement, reason in FREE_FIXES:
                if lid == lesson_id:
                    again, _ = _replace_in(fixed, re.compile(pattern), replacement)
                    self.assertEqual(again, fixed, f"{lid}: {reason}")
        self.assertEqual(self.db.query(CurriculumAuditEvent).filter_by(action="content_fix").count(), len(LIVE))

    def test_sample_corrections(self):
        with self.engine.connect() as conn:
            apply_content_fixes(conn)
            conn.commit()
        live = {v.lesson_id: json.loads(v.content_json) for v in self.db.query(LessonVersion).filter_by(is_active=True)}
        g3 = " ".join(live["lesson_g3_t1_ch01"]["texts"])
        self.assertNotIn("ร", g3)
        g1 = live["lesson_g1_t1_ch01"]
        self.assertEqual(g1["vocabulary_cards"][0]["root"], "")
        self.assertNotIn("ۡ", " ".join(g1["texts"]))
        g2 = " ".join(live["lesson_g2_t1_ch01"]["texts"])
        self.assertNotIn("starts with Baa", g2)
        g7 = live["lesson_g7_t1_ch01"]
        self.assertEqual([c["root"] for c in g7["vocabulary_cards"] if c["word_ar"] == "الرُّوتِينُ"], [""])


if __name__ == "__main__":
    unittest.main()

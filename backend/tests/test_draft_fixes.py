"""Clear-cut corrections to the Class 1 Term 2-3 AI drafts, applied on deploy before teacher review."""
import json
import re
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import CurriculumAuditEvent, Lesson, LessonVersion, Unit
from backend.modules.curriculum.content_fixes import _replace_in
from backend.modules.curriculum.draft_fixes import AI_DRAFTER, DRAFT_FIXES, E, _EVERY, apply_draft_fixes

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "class1_draft_errors.json").read_text(encoding="utf-8"))
LIVE = FIXTURE["drafts"]


def fix_all(lesson_id, data):
    for lid, pattern, replacement, _ in DRAFT_FIXES:
        if lid == lesson_id:
            data, _ = _replace_in(data, re.compile(pattern), replacement)
    return data


class DraftFixPatternsTest(unittest.TestCase):
    def test_every_lesson_specific_fix_matches_the_live_draft(self):
        shared = {p for p, _, _ in _EVERY}
        for lesson_id, pattern, _, reason in DRAFT_FIXES:
            if pattern in shared:
                continue
            with self.subTest(lesson=lesson_id, reason=reason):
                self.assertTrue(any(re.search(pattern, s) for s in LIVE[lesson_id]), pattern)

    def test_fixing_twice_changes_nothing_more(self):
        for lesson_id, strings in LIVE.items():
            once = fix_all(lesson_id, strings)
            self.assertNotEqual(once, strings)
            self.assertEqual(fix_all(lesson_id, once), once, lesson_id)

    def test_vowel_marks_match_in_any_order(self):
        # Typed fatha-then-shadda; the drafts store shadda-then-fatha.
        self.assertRegex("الشَّوْكُولاتَةَ", E("الشَّوْكُولاتَةَ"))
        self.assertRegex("الشَّوْكُولاتَةَ", E("الشَّوْكُولاتَةَ"))
        self.assertNotRegex("الشُّوكُولاتَةَ", E("الشَّوْكُولاتَةَ"))

    def test_key_corrections(self):
        cases = {
            "lesson_g1_t3_bk10": ("ثَمَانِيَةُ خِرْفَانٍ", "تِسْعَةُ خِرْفَانٍ"),
            "lesson_g1_t2_bk04": ("ثَلَاثَةٌ", "ثَوْبٌ"),
            "lesson_g1_t2_bk08": ("الْجَزَرَ", "الذُّرَةَ"),
        }
        for lesson_id, (wrong, right) in cases.items():
            fixed = " ".join(fix_all(lesson_id, LIVE[lesson_id]))
            self.assertNotRegex(fixed, E(wrong))
            self.assertIn(right, fixed)
        passage = next(s for s in fix_all("lesson_g1_t3_bk10", LIVE["lesson_g1_t3_bk10"]) if "كَانَ يَا مَا كَانَ" in s)
        self.assertIn("يَنُطَّ 20 نَطَّةً", passage)

    def test_narrow_fixes_leave_similar_text_alone(self):
        # "ضَارٌ" must not touch "خُضَارٌ"; the bracket fix must not strip grammar examples.
        self.assertEqual(fix_all("lesson_g1_t3_bk02", ["خُضَارٌ"]), ["خُضَارٌ"])
        self.assertEqual(fix_all("lesson_g1_t2_bk01", ["أَنَا - أَرْنَبٌ (أَ)"]), ["أَنَا - أَرْنَبٌ (أَ)"])
        # The 20-jumps sentence goes into the passage only, not the sentence-builder answer.
        self.assertEqual(fix_all("lesson_g1_t3_bk10", ["Majid can count from 1 to 20."]), ["Majid can count from 1 to 20."])


class ApplyDraftFixesTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
        self.db.add(Lesson(id="lesson_g1_t3_bk10", unit_id="u", grade=1, term=3, lesson_order=10, title_ar="د",
                           title_en="L", start_page=79, status="staged"))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def add(self, vid, content, status="content_pending", by=AI_DRAFTER):
        raw = json.dumps(content, ensure_ascii=False)
        self.db.add(LessonVersion(id=vid, lesson_id="lesson_g1_t3_bk10", version_tag="ai-1", content_json=raw,
                                  content_hash="x", is_active=False, status=status, created_by=by))
        self.db.commit()

    def run_fixes(self):
        with self.engine.connect() as conn:
            fixed = apply_draft_fixes(conn)
            conn.commit()
        self.db.expire_all()
        return fixed

    def test_saves_a_corrected_draft_once_and_keeps_the_old_one(self):
        self.add("draft1", {"passage_ar": LIVE["lesson_g1_t3_bk10"]})
        self.assertEqual(self.run_fixes(), ["lesson_g1_t3_bk10"])
        self.assertEqual(self.run_fixes(), [])  # next deploy: nothing left to fix
        old = self.db.get(LessonVersion, "draft1")
        self.assertEqual(old.status, "superseded")
        new = self.db.query(LessonVersion).filter_by(status="content_pending").one()
        self.assertEqual((new.created_by, new.is_active), (AI_DRAFTER, False))
        self.assertIn("تِسْعَةُ خِرْفَانٍ", " ".join(json.loads(new.content_json)["passage_ar"]))
        event = self.db.query(CurriculumAuditEvent).filter_by(action="draft_fix").one()
        self.assertEqual(json.loads(event.details_json)["replaces"], "draft1")

    def test_published_versions_and_teacher_edits_are_left_alone(self):
        self.add("live", {"passage_ar": LIVE["lesson_g1_t3_bk10"]}, status="published")
        self.add("teacher", {"passage_ar": LIVE["lesson_g1_t3_bk10"]}, by="teacher-1")
        self.assertEqual(self.run_fixes(), [])
        self.assertEqual(self.db.query(LessonVersion).count(), 2)


if __name__ == "__main__":
    unittest.main()

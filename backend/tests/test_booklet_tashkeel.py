"""The Grade 5 booklet keeps full tashkeel: the Arab-English line under each word is spelled from the
vowel marks, so a word written without them shows no Arab-English at all."""
import re
import unittest

from backend.malazim_bank import MALAZIM_DATA

WORD = re.compile(r"[ء-ي][ء-يً-ْٰـ]*")
VOWELLED = re.compile(r"[ً-ْ]")
# Abbreviations and letter examples that are written without vowels on purpose.
EXEMPT = {"م", "سم", "ة", "ه", "ـة", "ـه"}


def _learner_texts(booklet):
    for sec in booklet["study_mode"]["sections"]:
        ex = sec["inline_exercise"]
        yield from (sec["title_ar"], sec["content_ar"], *sec["key_takeaways_ar"], ex["question_ar"], *ex["options"], ex["explanation_ar"])
    quick = booklet["quick_review_mode"]
    yield from (r["rule_ar"] for r in quick["bullet_rules"])
    yield from (f[k] for f in quick["vocabulary_flashcards"] for k in ("meaning_ar", "opposite_ar"))
    yield from (g[k] for g in quick["grammar_formulas"] for k in ("title_ar", "formula_ar", "example_ar"))
    yield from (w["warning_ar"] for w in quick["exam_pitfall_warnings"])


class TestGrade5BookletTashkeel(unittest.TestCase):
    def test_every_word_has_vowel_marks(self):
        missing = sorted({w for text in _learner_texts(MALAZIM_DATA["lesson_01_ball_games"])
                          for w in WORD.findall(text) if w not in EXEMPT and not VOWELLED.search(w)})
        self.assertEqual(missing, [], "Grade 5 booklet words without tashkeel (no Arab-English line): " + " ".join(missing))


if __name__ == "__main__":
    unittest.main()

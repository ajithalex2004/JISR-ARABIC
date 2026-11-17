"""Study-booklet exercises: every option is distinct and the marked answer is the right one."""
import unittest

from backend.generated_study_content import _root_options, generate_booklet, generate_capsules


class BookletOptionsTest(unittest.TestCase):
    def test_no_exercise_repeats_an_option(self):
        for grade in range(1, 13):
            for term in (1, 2, 3):
                for order in range(1, 11):
                    booklet = generate_booklet(grade, term, order)
                    if not booklet:
                        continue
                    for section in booklet["study_mode"]["sections"]:
                        ex = section["inline_exercise"]
                        with self.subTest(grade=grade, term=term, order=order, section=section["section_id"]):
                            self.assertEqual(len(set(ex["options"])), len(ex["options"]), ex["options"])
                            self.assertLess(ex["correct_index"], len(ex["options"]))

    def test_capsule_quizzes_never_repeat_an_option(self):
        for grade in range(1, 13):
            for term in (1, 2, 3):
                for capsule in generate_capsules(grade, term, limit=10):
                    for quiz in capsule.get("quiz", []):
                        with self.subTest(capsule=capsule["id"]):
                            self.assertEqual(len(set(quiz["options"])), len(quiz["options"]), quiz["options"])
                            self.assertEqual(len(set(quiz["options_en"])), len(quiz["options_en"]), quiz["options_en"])

    def test_root_answer_stays_marked_and_unique(self):
        for answer in ("ك-ت-ب", "ل-ع-ب", "د-ر-س", "ق-ر-أ"):
            options = _root_options(answer)
            self.assertEqual(options[1], answer)
            self.assertEqual(len(set(options)), 3)


if __name__ == "__main__":
    unittest.main()

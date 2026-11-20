"""The Mindmaps page's rules tree and flowchart follow the selected grade (they showed Grade 5's for every grade)."""
import unittest

from fastapi.testclient import TestClient

from backend.generated_study_content import grade_grammar_rules
from backend.main import app
from backend.modules.curriculum.syllabus_data import GRADE_GRAMMAR_MAP

RULE_FIELDS = {"key", "titleAr", "titleEn", "badgeAr", "badgeEn", "ruleAr", "ruleEn", "formulaAr", "formulaEn", "examples"}


class TestMindmapGrammarRules(unittest.TestCase):
    def test_each_grade_gets_its_own_grammar(self):
        titles = {g: [r["titleAr"] for r in grade_grammar_rules(g)] for g in range(1, 11)}
        for g in range(1, 11):
            self.assertIn(GRADE_GRAMMAR_MAP[g]["rule_ar"], titles[g], g)
            self.assertNotIn(GRADE_GRAMMAR_MAP[5]["rule_ar"], titles[g] if g != 5 else [], g)
        self.assertTrue(any("الجزم" in t for t in titles[7]))  # Grade 7 Unit 1 booklet formulas (أدوات الجزم)
        self.assertEqual(grade_grammar_rules(11), [])  # no syllabus entry: nothing, never another grade's

    def test_rules_have_the_page_shape(self):
        for g in (1, 6, 7, 10):
            for rule in grade_grammar_rules(g):
                self.assertEqual(set(rule), RULE_FIELDS)
                self.assertTrue(rule["titleAr"] and rule["formulaAr"])
                for ex in rule["examples"]:
                    self.assertTrue(ex["sentenceAr"])
        self.assertEqual(len({r["key"] for r in grade_grammar_rules(6)}), len(grade_grammar_rules(6)))

    def test_mindmaps_endpoint_returns_the_grades_rules(self):
        client = TestClient(app)
        g1 = client.get("/api/modules/mindmaps", params={"grade": 1}).json()
        g5 = client.get("/api/modules/mindmaps", params={"grade": 5}).json()
        self.assertEqual(g1["grammar_rules"][-1]["titleAr"], GRADE_GRAMMAR_MAP[1]["rule_ar"])
        self.assertNotEqual(g1["grammar_rules"], g5["grammar_rules"])
        client.close()


if __name__ == "__main__":
    unittest.main()

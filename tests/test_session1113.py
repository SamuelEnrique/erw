"""Session 1113 (chain 075, asked by session 1126): the grading of the thirty under the hold
(warehouse/chat/eval/eval_s1113.py held_ok), on the stored run: a held grid's answer is right when it says "license
needed", names the grid and states no figure of it; and the stored grades are the grader's on the stored answers.
No network, no model. Nothing here sets the environment at import.
"""
import importlib.util
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def runner():
    spec = importlib.util.spec_from_file_location("eval_s1113_for_test", os.path.join(EVAL, "eval_s1113.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheHoldsGrade(unittest.TestCase):
    def test_held_ok(self):
        m = runner()
        k = {"entity": "nyiso:N.Y.C.", "table_unit_value": 73.8689}
        self.assertTrue(m.held_ok("NYISO's rows are held for a license (license needed). ERCOT 29.17 USD/MWh.", k))
        self.assertFalse(m.held_ok("NYISO's rows are held for a license (license needed): 73.87 USD/MWh.", k))
        self.assertFalse(m.held_ok("The flat price was 73.87 USD/MWh.", k))
        self.assertFalse(m.held_ok("License needed.", k))

    def test_the_stored_grades_are_the_graders(self):
        m = runner()
        with open(os.path.join(EVAL, "eval_s1113_run.json"), encoding="utf-8") as f:
            run = json.load(f)
        with open(os.path.join(EVAL, "eval_s1113_keys.json"), encoding="utf-8") as f:
            keys = json.load(f)
        saved = m.GRADES
        m.GRADES = os.path.join(os.environ.get("TEMP", "/tmp"), "erw_test_s1113_grades.json")
        try:
            doc = m.grade(run, keys)
        finally:
            m.GRADES = saved
        with open(os.path.join(EVAL, "eval_s1113_grades.json"), encoding="utf-8") as f:
            stored = json.load(f)
        self.assertEqual((doc["right_now"], doc["right_under_hold"], doc["right_if_ruled"]), (stored["right_now"], stored["right_under_hold"], stored["right_if_ruled"]))
        self.assertEqual(stored["right_under_hold"], 19)


if __name__ == "__main__":
    unittest.main()

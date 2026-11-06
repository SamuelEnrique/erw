"""Session 2886 (chain 148): the Ask evaluation's rest. eval_s1113.py asks and grades two more sets the same way it asks
the second set: s1133 (session 1133's asking of questions_s1114.yaml, eight asked before, the rest asked on 6 November
2026) and s1122 (the board's five questions, first asked here); runs.json lists the new run. No request, no model call.
"""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
sys.path.insert(0, EVAL)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "chat"))
import eval_s1113 as E  # noqa: E402


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


class TheSets(unittest.TestCase):
    def test_the_two_sets_name_their_files(self):
        self.assertEqual(os.path.basename(E.SETS["s1133"]["questions"]), "eval_s1133_s1114_questions.yaml")
        self.assertEqual(os.path.basename(E.SETS["s1133"]["run"]), "eval_s1133_s1114_run.json")
        self.assertEqual(os.path.basename(E.SETS["s1122"]["questions"]), "questions_s1122.yaml")
        for which in ("s1133", "s1122"):
            for k in ("questions", "run", "grades"):
                self.assertTrue(os.path.exists(E.SETS[which][k]), (which, k))

    def test_the_second_set_is_asked_whole_and_graded(self):
        run, grades = load("eval_s1133_s1114_run.json"), load("eval_s1133_s1114_grades.json")
        self.assertEqual(len(run["questions"]), 30)
        self.assertEqual([q["id"] for q in run["questions"]][:9], [f"t0{k}" for k in range(1, 10)])
        self.assertEqual(grades["asked"], 30)
        self.assertIn("--set s1133", grades["_about"])

    def test_the_boards_five_are_a_run_of_the_list(self):
        runs = load("runs.json")["runs"]
        mine = [r for r in runs if r["file"] == "eval_s1122_run.json"]
        self.assertEqual(len(mine), 1)
        # session 2918: the run's grades are those on the keys of its own day (eval_s1122_grades_s2918.json); session
        # 2886's on the keys of 23 October are kept, named under left_out
        self.assertEqual(mine[0]["grades"], "eval_s1122_grades_s2918.json")
        self.assertIn("eval_s1122_grades.json", load("runs.json")["left_out"])
        self.assertEqual(len(load("eval_s1122_run.json")["questions"]), 5)

    def test_grading_reads_the_set_it_is_given(self):
        import inspect
        src = inspect.getsource(E.grade_s1114)
        self.assertIn('SETS[which]["run"]', src)
        self.assertNotIn('SETS["s1114"]', src)


if __name__ == "__main__":
    unittest.main()

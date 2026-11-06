"""Session 2918 (chain 153): the board's five questions (session 2886's asking, eval_s1122_run.json) graded on the keys
of their own day. The keys are computed by expected_s1122.py's own build from the rows session 2918 recorded from the
live set (tests/fixtures/session2918/board_reads.json), not from session 1122's fixture, which its tests still pin.

Held here: the set s2918 reads that run and those keys; the keys are what the build gives from the recorded rows; the
grades file is what grade_s1114 gives on them (4 of 5, k03 an error of the route); runs.json lists the run once, with
these grades. No network, no model.
"""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")
for p in (EVAL, os.path.join(ROOT, "warehouse", "chat"), os.path.join(ROOT, "warehouse")):
    if p not in sys.path:
        sys.path.insert(0, p)


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


class TheBoardsFiveOnTheirDay(unittest.TestCase):
    def test_the_keys_are_the_builds_from_the_recorded_rows(self):
        import expected_s1122 as X
        keep = X.FIX
        try:
            X.FIX = os.path.join(ROOT, "tests", "fixtures", "session2918", "board_reads.json")
            doc = X.build()
        finally:
            X.FIX = keep
        held = load("expected_s2918.json")
        self.assertEqual(doc["recorded_at"], held["recorded_at"])
        self.assertTrue(held["recorded_at"].startswith("2026-11-06"))
        self.assertEqual([(q["id"], q["entity"], q["value"]) for q in doc["questions"]],
                         [(q["id"], q["entity"], q["value"]) for q in held["questions"]])
        with open(os.path.join(EVAL, "questions_s2918.yaml"), encoding="utf-8") as f:
            y = f.read()
        self.assertIn("tests/fixtures/session2918/board_reads.json", y)
        for q in held["questions"]:
            self.assertIn(f"expected: [{round(q['value'], 4)}]", y)

    def test_session_1122s_keys_are_left_as_they_were(self):
        self.assertTrue(load("expected_s1122.json")["recorded_at"].startswith("2026-10-23"))

    def test_the_set_reads_the_run_and_the_new_keys(self):
        import eval_s1113 as E
        s = E.SETS["s2918"]
        self.assertEqual(os.path.basename(s["run"]), "eval_s1122_run.json")
        self.assertEqual(os.path.basename(s["questions"]), "questions_s2918.yaml")
        self.assertEqual(os.path.basename(s["grades"]), "eval_s1122_grades_s2918.json")

    def test_the_grades_are_the_graders(self):
        import eval_s1113 as E
        keep = dict(E.SETS["s2918"])
        with tempfile.TemporaryDirectory() as d:
            try:
                E.SETS["s2918"]["grades"] = os.path.join(d, "g.json")
                doc = E.grade_s1114("s2918")
            finally:
                E.SETS["s2918"] = keep
        held = load("eval_s1122_grades_s2918.json")
        self.assertEqual((doc["asked"], doc["right"]), (held["asked"], held["right"]))
        self.assertEqual((held["asked"], held["right"]), (5, 4))
        bad = [q for q in held["questions"] if not q["ok"]]
        self.assertEqual([(q["id"], q["status"]) for q in bad], [("k03", "error")])

    def test_runs_json_lists_the_run_once_with_these_grades(self):
        runs = load("runs.json")
        mine = [r for r in runs["runs"] if r["file"] == "eval_s1122_run.json"]
        self.assertEqual(len(mine), 1)
        self.assertEqual(mine[0]["grades"], "eval_s1122_grades_s2918.json")
        self.assertIn("expected_s2918.json", runs["left_out"])


if __name__ == "__main__":
    unittest.main()

"""Session 1190 (chain 089): session 1149's asking again (warehouse/chat/eval/eval_s1133_*) is in the evaluations'
history, and its runs hold what docs/reviews/ask-sixty-2026-10-25.md says of them. No network, no model. Nothing here
sets the environment at import.
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "warehouse", "chat", "eval")


def load(name):
    with open(os.path.join(EVAL, name), encoding="utf-8") as f:
        return json.load(f)


class TheAskingAgain(unittest.TestCase):
    def test_the_history_holds_both_runs(self):
        with open(os.path.join(ROOT, "docs", "reviews", "ask-history.md"), encoding="utf-8") as f:
            body = f.read()
        self.assertEqual(body.count("`docs/reviews/ask-sixty-2026-10-25.md`"), 2)
        self.assertIn("| asked again after chains 076 and 085, 8 of the thirty (the cap) | 8 of 8 |", body)

    def test_the_first_set_grades_as_it_did(self):
        new = {q["id"]: q for q in load("eval_s1133_s320_grades.json")["questions"]}
        old = {q["id"]: q for q in load("eval_s1113_grades.json")["questions"]}
        self.assertEqual(sorted(new), sorted(old))
        self.assertEqual([i for i in sorted(new) if new[i]["held_ok"] != old[i]["held_ok"]], [])
        self.assertEqual(sorted(i for i in new if not new[i]["held_ok"]),
                         ["b01", "b02", "b03", "b04", "b05", "b06", "b08", "b09", "d10", "g03", "g06"])

    def test_the_second_set_stopped_at_t09(self):
        run = load("eval_s1133_s1114_run.json")["questions"]
        self.assertEqual([q["id"] for q in run], [f"t0{i}" for i in range(1, 9)])
        self.assertTrue(all(q["ok"] for q in load("eval_s1133_s1114_grades.json")["questions"]))


if __name__ == "__main__":
    unittest.main()

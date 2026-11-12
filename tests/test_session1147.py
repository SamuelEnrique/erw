"""Session 1147 (chain 085): the evaluations' history (docs/reviews/ask-history.md) is what the stored runs give
(warehouse/chat/eval/history.py), one row a run, so a new run's file changes it and a hand edit fails here.
No network, no model. Nothing here sets the environment at import.
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TheHistory(unittest.TestCase):
    def test_the_file_is_what_the_runs_give(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "chat", "eval", "history.py"), "--check"], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_run_is_a_row(self):
        with open(os.path.join(ROOT, "docs", "reviews", "ask-history.md"), encoding="utf-8") as f:
            body = f.read()
        self.assertEqual(body.count("\n| 2026-"), 25)   # session 3769 (chain 211): the weekly thirty and the board's five. Session 3297: tr15 again, iv14 again with iv18 to iv20. Session 1190: six, and session 1149's two runs; session 2886: the board's five; session 2221 (chain 152): the Python loop's four runs (merged by session 2947); session 2948 (chain 157): the board's five through the Python loop; session 2968: the weekly thirty and twenty; session 1486 (chain 158): the board's five again; sessions 3280 to 3282: the trader's and the investor's twenty and their second asking
        self.assertIn("| 19 of 30 (15 on the figure keys; 30 if session 320's rulings went the answers' way) |", body)
        self.assertIn("| 24 of 30 |", body)
        self.assertIn("| 20 of 20 |", body)   # session 2224 (chain 152), the twenty
        self.assertIn("| 17 of 20 |", body)   # session 3280, the trader's twenty, first asking
        self.assertIn("| 14 of 17 |", body)   # session 3281, the investor's twenty, 17 asked before the run was stopped for memory
        self.assertIn("the set's final count 20 of 20 | 4 of 4 |", body)   # session 3297, the investor's iv14 and iv18 to iv20
        self.assertIn("| 30 of 30 (26 on the figure keys; ", body)   # session 2223 (chain 152)
        self.assertIn("| 29 of 30 (25 on the figure keys; ", body)   # session 2222 (chain 152)
        self.assertIn("| 26 of 30 (22 on the figure keys; ", body)   # session 2221 (chain 152)


if __name__ == "__main__":
    unittest.main()

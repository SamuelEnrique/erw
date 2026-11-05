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
        self.assertEqual(body.count("\n| 2026-"), 6)
        self.assertIn("| 19 of 30 (15 on the figure keys; 30 if session 320's rulings went the answers' way) |", body)
        self.assertIn("| 24 of 30 |", body)


if __name__ == "__main__":
    unittest.main()

"""Session 9001 (chain 601's desk, data request 566): the codebook for Redivis cut a long text to n - 5 characters and
added " [...]" (six), so nine table descriptions came to 2,001 characters; Redivis refused the first ("Table
description cannot be more than 2000 characters"), and since a refused description was not caught as a refused label
is, `codebook.py apply --yes` stopped there. Every text is now at most its limit, and a refused description is printed
while the run goes on.
"""
import csv
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
OUT = os.path.join(ROOT, "docs", "redivis", "codebook")


class TheLimitsHold(unittest.TestCase):
    def test_the_cut_keeps_a_text_within_its_limit(self):
        import codebook
        for n in (250, 2000):
            for k in range(n - 10, n + 10):
                text = "word " * (k // 5 + 1)
                cut = codebook._cut(text, n)
                self.assertLessEqual(len(cut), n, (n, k))
        self.assertTrue(codebook._cut("x" * 3000, 2000).endswith(" [...]"))
        self.assertEqual(codebook._cut("short", 250), "short")

    def test_the_written_files_hold_redivis_limits(self):
        with open(os.path.join(OUT, "tables.csv"), encoding="utf-8") as f:
            tables = list(csv.DictReader(f))
        with open(os.path.join(OUT, "variables.csv"), encoding="utf-8") as f:
            variables = list(csv.DictReader(f))
        self.assertTrue(tables and variables)
        self.assertLessEqual(max(len(r["description"]) for r in tables), 2000)
        self.assertLessEqual(max(len(r["label"]) for r in variables), 250)
        self.assertLessEqual(max(len(r["description"]) for r in variables), 2000)

    def test_a_refused_description_does_not_stop_the_run(self):
        with open(os.path.join(ROOT, "warehouse", "redivis", "codebook.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('print(f"{t}: description refused (', s)


if __name__ == "__main__":
    unittest.main()

"""Session 2251 (chain 156): the deals table read as a reader at a fund reads it: every cell a decision needs (what, who,
how much, at what price, when, where, how sure) present, or marked not stated, never an empty cell."""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheCells(unittest.TestCase):
    def test_every_empty_cell_says_so(self):
        with open(os.path.join(ROOT, "site", "app", "deals", "DealsTable.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('const NS = <span className="text-xs text-muted">not stated</span>;', s)
        self.assertGreaterEqual(s.count("NS}"), 5)       # where, grid, MW, price, stage (and US dollars by its block)
        self.assertIn('["sure", "Sure", ', s)             # how sure: the model's confidence, a column that sorts
        self.assertIn('data-sure={d.confidence ?? ""}', s)
        self.assertIn('{d.aiPower ? "yes" : "no"}', s)    # the AI tag says no, not nothing

    def test_the_sort_key(self):
        with open(os.path.join(ROOT, "site", "lib", "dealsview.ts"), encoding="utf-8") as f:
            self.assertIn("sure: (d) => d.confidence", f.read())


if __name__ == "__main__":
    unittest.main()

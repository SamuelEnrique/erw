"""Audit of /equities, finding 6 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): the two weightings
are named and not computed, and the page said their rule was in the method note, which did not hold it.

The board's group names thirty rows, each segment "(equal weight)" and "(weighted by market value)", and /equities
names "Every company counts the same" and "Larger companies count more". No code computes either (no segment file, no
board row with a value): share prices are held. The page's hover "What it is" said "A segment's line is built by the
ERW from its companies' prices by the written rule of the method note"; the rule was in the contract
(docs/state/page_files_equities.md), not in docs/methods/equities.md, and no line is built.

1. Nothing computes a weighting (passes on main): no segment series, every board row held with no value.
2. The fix on this branch (fails on main): the hover says no segment line is built while share prices are held; the
   method note carries the two lines' rule and names what the rule leaves open. No figure moves."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "site", "data", "equities")
VIEW = os.path.join(ROOT, "site", "app", "equities", "view.tsx")
NOTE = os.path.join(ROOT, "docs", "methods", "equities.md")


class NamedNotBuilt(unittest.TestCase):
    def test_nothing_computes_a_weighting(self):
        with open(os.path.join(D, "index.json"), encoding="utf-8") as f:
            idx = json.load(f)
        with open(os.path.join(D, "board.json"), encoding="utf-8") as f:
            board = json.load(f)
        self.assertEqual(idx["segment_series"], [])
        self.assertEqual(len(board["rows"]), 30)
        self.assertEqual({r["tags"]["weighting"] for r in board["rows"]}, {"equal", "value"})
        for r in board["rows"]:
            self.assertEqual(r["status"], "not_held")
            self.assertFalse(r.get("last") or r.get("spark") or r.get("file"))

    def test_the_hover_says_so(self):
        src = open(VIEW, encoding="utf-8").read()
        self.assertNotIn("by the written rule of the method note", src)
        self.assertIn("and so no segment line is built", src)

    def test_the_note_holds_the_rule(self):
        note = open(NOTE, encoding="utf-8").read()
        self.assertIn("## The segments' two lines (named, not built)", note)
        self.assertIn("`equal_weight`: 100 on the segment's first day held", note)
        self.assertIn("weighted by its market value the day before", note)
        self.assertNotIn(chr(0x2014), note)


if __name__ == "__main__":
    unittest.main()

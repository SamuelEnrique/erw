"""Session 10231 (chain 710, part D: the signature explorers audited, docs/reviews/explore-model-audit-2026-11-26.md,
finding 7).

docs/methods/explorers.md, the note the three explorers share, said a table is stale after three days on every
explorer. The demand growth explorer calls its table stale after 35 days (session 7508) and the interconnection explorer
after eight (session 7509); only the peak premium explorer keeps the frame's three. Words only, in the note; no page
changes. The test runs everywhere.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class EachExplorerHasItsOwnStaleDay(unittest.TestCase):
    def test_the_pages_rules(self):
        self.assertIn("staleAfterDays = 3", src("site", "components", "explore", "Explore.tsx"))
        self.assertNotIn("staleAfterDays", src("site", "app", "explore", "ercot-peak-premium", "page.tsx"))
        self.assertIn("const STALE_AFTER_DAYS = 35;", src("site", "app", "explore", "demand-growth", "page.tsx"))
        self.assertIn("staleAfterDays={8}", src("site", "app", "explore", "interconnection", "page.tsx"))

    def test_the_note_says_each(self):
        n = src("docs", "methods", "explorers.md")
        self.assertNotIn("A table not computed for more than three days is said to be stale", n)
        self.assertIn("three days on the peak premium explorer (the frame's own rule), 35 on the demand growth explorer", n)
        self.assertIn("and eight on the interconnection explorer (the queues are pulled weekly", n)
        self.assertNotIn(chr(0x2014), n)


if __name__ == "__main__":
    unittest.main()

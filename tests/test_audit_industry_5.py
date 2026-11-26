"""Session 10224 (chain 710, the industry page audit, finding 5): the decisions name every opening choice of /industry.

The fold says it lists "each choice that moves what the page shows", and left out the outlook's opening industry and
series (Iron and steel, its total energy use) and the region and the states' year and source the page opens on.
docs/reviews/industry-model-audit-2026-11-26.md.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheOpeningChoices(unittest.TestCase):
    """What the page opens on (passes on main)."""

    def test_the_page_opens_on_iron_and_steel_and_the_united_states(self):
        page = src("site", "app", "industry", "page.tsx")
        self.assertIn('oInds.includes("iron_and_steel") ? "iron_and_steel"', page)
        self.assertIn('MECS_REGIONS.map((r) => r.key), "us")', page)
        self.assertIn('SEDS_SOURCES.map((s) => s.key), "total")', page)
        names = list(json.loads(src("site", "data", "industry.json"))["outlook"]["industries"]["iron_and_steel"])
        totals = [n for n in names if re.search(r"Total$|Total Energy Use$", n)]
        self.assertEqual(totals, ["Iron and Steel : Energy Use : Total"])


class TheWords(unittest.TestCase):
    """What the fold and the note say (fails on main, passes on the branch)."""

    def test_the_fold_names_them(self):
        dec = src("site", "app", "industry", "Decisions.tsx")
        self.assertIn("opens on Iron and steel, its total energy use", dec)
        self.assertIn("the United States until another is chosen", dec)
        self.assertIn("the total in the newest year until others are chosen", dec)

    def test_the_note_names_them(self):
        note = src("docs", "methods", "industry_page.md")
        self.assertIn("opens on Iron and steel, its total energy use", note)

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "Decisions.tsx"), ("docs", "methods", "industry_page.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()

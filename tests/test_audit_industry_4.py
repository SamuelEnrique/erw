"""Session 10224 (chain 710, the industry page audit, finding 4): "not held" and EIA's codes on /industry.

The page said a "not held" cell was one "EIA withholds or does not estimate", "with EIA's reason on hover". The survey's
* is an estimate under 0.5 (most of the coded cells), and the table keeps no code, so the hover can only give all four.
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


class TheCodes(unittest.TestCase):
    """What the survey's note and the page file hold (passes on main)."""

    def test_most_coded_cells_are_estimates_under_half_a_unit(self):
        note = src("docs", "methods", "eia_mecs_manufacturing.md")
        counts = {k: int(v.replace(",", "")) for v, k in re.findall(r"(?:\* |D |NA |Q )([\d,]+) \(([^)]+)\)", note)}
        star = int(re.search(r"\* ([\d,]+) \(an estimate less than 0\.5\)", note).group(1).replace(",", ""))
        self.assertEqual(star, 1307)
        self.assertEqual(sum(counts.values()), 1307 + 30 + 324 + 356)
        self.assertGreater(star / sum(counts.values()), 0.6)

    def test_the_file_keeps_no_code(self):
        f = json.loads(src("site", "data", "industry.json"))
        chem = f["industries"]["industries"]["325"]
        self.assertNotIn("residual_fuel_oil", chem["by_region"]["us"])   # not held, and no code beside it
        self.assertEqual(set(chem), {"naics", "name", "by_region", "rank_us_total", "electricity_mwh"})


class TheWords(unittest.TestCase):
    """What the page, its decisions, the builder and the note say (fails on main, passes on the branch)."""

    def test_no_reason_is_claimed_for_one_cell(self):
        page, dec = src("site", "app", "industry", "page.tsx"), src("site", "app", "industry", "Decisions.tsx")
        self.assertNotIn("EIA withholds or does not estimate", page + dec)
        self.assertNotIn("with EIA's reason on hover", page + dec)
        self.assertIn("* (an estimate under 0.5 in the table's unit)", page)
        self.assertIn("the file does not keep which code a cell had, so the hover gives all four", dec)
        self.assertIn("title={src === WITHHELD ? src", page)

    def test_the_builder_and_the_note(self):
        self.assertIn("codes * for an estimate under 0.5", src("warehouse", "derived", "industry_page.py"))
        note = src("docs", "methods", "industry_page.md")
        self.assertNotIn("with EIA's reason on hover", note)
        self.assertIn("the hover gives all four", note)

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "page.tsx"), ("site", "app", "industry", "Decisions.tsx"), ("docs", "methods", "industry_page.md"), ("warehouse", "derived", "industry_page.py")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()

"""Session 10224 (chain 710, the industry page audit, finding 1): the industrial sector and the survey count different things.

The headline row of /industry sets the Monthly Energy Review's industrial sector (manufacturing, agriculture, mining and
construction, with feedstocks and the sector's share of electrical system losses) beside the 2022 Manufacturing Energy
Consumption Survey's largest industry (manufacturing's fuel only). docs/reviews/industry-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheTwoMeasures(unittest.TestCase):
    """What the page file holds (passes on main)."""

    def setUp(self):
        self.f = json.loads(src("site", "data", "industry.json"))

    def year(self, key, y):
        m = self.f["monthly"]
        vals = [m["by_source"][key][m["months"].index(f"{y}-{x:02d}")] for x in range(1, 13)]
        return sum(vals)

    def test_manufacturing_fuel_is_about_half_the_sector(self):
        mecs = self.f["industries"]["industries"]["total"]["by_region"]["us"]["total"]
        mer = self.year("total", 2022)
        self.assertEqual(mecs, 15742.0)
        self.assertAlmostEqual(mer, 31168.756, places=2)
        self.assertTrue(0.45 < mecs / mer < 0.55)

    def test_the_sector_total_counts_the_losses(self):
        for y in (2022, 2025):
            self.assertAlmostEqual(self.year("total", y), self.year("end_use_total", y) + self.year("electrical_system_losses", y), delta=0.02)


class TheWords(unittest.TestCase):
    """What the page and its note say (fails on main, passes on the branch)."""

    def test_the_lead_says_they_count_different_things(self):
        page = src("site", "app", "industry", "page.tsx")
        self.assertIn("The industrial sector and the survey count different things", page)
        self.assertIn("agriculture, mining and construction", page)
        self.assertIn("feedstocks", page)
        self.assertIn("Largest manufacturing industry by fuel", page)
        self.assertIn("feedstocks not counted", page)

    def test_the_note_says_so(self):
        note = src("docs", "methods", "industry_page.md")
        self.assertIn("50.5 percent of the Monthly Energy Review's industrial total", note)

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "page.tsx"), ("docs", "methods", "industry_page.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()

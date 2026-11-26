"""Session 10214 (chain 710, part D: the demand page audited, docs/reviews/demand-model-audit-2026-11-26.md, finding 2).

The as-metered view of /demand called the weather view "the same growth with the weather taken out". The weather view
measures growth against the mean of 2019 to 2021, the as-metered view against 2019: two bases, two figures for one grid
and year (MISO's 2025 average demand: +2.20 here, +4.10 there). Both files are the page's own.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TwoBasesTwoFigures(unittest.TestCase):
    def test_the_two_views_measure_against_two_bases_and_differ(self):
        m = json.loads(src("site", "data", "demand_growth.json"))
        w = json.loads(src("site", "data", "demand_weather.json"))
        self.assertEqual(m["base"], 2019)
        self.assertEqual(w["train"], [2019, 2020, 2021])
        self.assertEqual(m["areas"]["MISO"]["years"]["2025"]["avg_demand_growth_since_2019_pct"], 2.2)
        self.assertAlmostEqual(w["grids"]["MISO"]["years"]["2025"]["energy"]["growth_pct"], 4.10, delta=0.01)
        apart = [abs(m["areas"][ba]["years"]["2025"]["avg_demand_growth_since_2019_pct"] - w["grids"][ba]["years"]["2025"]["energy"]["growth_pct"])
                 for ba in w["grids"] if "2025" in w["grids"][ba]["years"] and "energy" in w["grids"][ba]["years"]["2025"]]
        self.assertGreater(max(apart), 1.5)

    def test_the_page_no_longer_calls_it_the_same_growth(self):
        page = src("site", "app", "demand", "page.tsx")
        self.assertNotIn("The same growth with the weather taken out", page)
        self.assertIn("it is measured against the mean of {FIT_YEARS.from} to {FIT_YEARS.to}, not against {file.base} alone, so its growth is not this view&apos;s figure.", page)
        self.assertIn("so the two views give two figures for one grid", src("docs", "methods", "demand_growth.md"))


if __name__ == "__main__":
    unittest.main()

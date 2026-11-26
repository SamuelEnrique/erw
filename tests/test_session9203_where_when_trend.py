"""Session 9203 (chain 620, the desktop's second window, 20 November 2026): the trend by year on /curtailment/where-when
names the fuel it sums.

Energy Research Warehouse (ERW). Read on production (part C of chain 620): the chart "Solar curtailed, GWh a whole year"
carried a line named "CAISO, the whole system: curtailment", so its table's column read "CAISO, the whole system:
curtailment, GWh" over solar alone: 3,482 GWh in 2025, where /curtailment's months sum to 3,765.6 GWh for wind and solar
together (3,482.3 of solar and 283.3 of wind). The line's label now says the fuel, as the chart's title does: "CAISO, the
whole system: solar curtailed" (or "wind", or "wind and solar"). No figure moves.

Held here, on the source and on the page file: the label's words; the 2025 figures of the file that the two pages show.
Nothing here makes a request.
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FILE = os.path.join(ROOT, "site", "data", "curtailment", "where_when.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheLabel(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "curtailment", "where-when", "page.tsx")
        self.line = next(l for l in self.page.splitlines() if "const curtTrend" in l)

    def test_the_trend_line_names_its_fuel(self):
        self.assertIn("${trendFuel} curtailed", self.line)
        self.assertRegex(self.page, r'const trendFuel = fuel === "both" \? "wind and solar" : fuel;')

    def test_the_chart_title_still_names_the_fuel(self):
        self.assertIn('fuel === "both" ? "Wind and solar" : fuel === "solar" ? "Solar" : "Wind"} curtailed, GWh a whole year', self.page)

    def test_the_place_lists_keep_their_words(self):
        # the lists and the side by side headings are not changed: only the trend's line
        self.assertIn('label: `${c.name}: curtailment` }', self.page)
        self.assertIn('const nameOf = (pl: Place) => (pl.kind === "curtailment" ? `${pl.c.name}: curtailment`', self.page)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), self.page)


@unittest.skipUnless(os.path.exists(FILE), "the where-and-when file is not on this machine")
class TheFigures(unittest.TestCase):
    def test_the_2025_solar_and_both_figures(self):
        with open(FILE, encoding="utf-8") as f:
            c = json.load(f)["curtailment"][0]
        self.assertEqual(c["id"], "caiso")
        y = c["by_year"]["2025"]
        keys = ("solar", "wind") if c.get("by_hour") else ("curtailed_solar_mwh", "curtailed_wind_mwh")
        solar, wind = (y[k] for k in keys)
        self.assertTrue(y["whole"])
        self.assertEqual(round(solar / 1e3), 3482, "the trend's solar figure for 2025, GWh")
        self.assertAlmostEqual((solar + wind) / 1e3, 3765.6, delta=0.06)


if __name__ == "__main__":
    unittest.main()

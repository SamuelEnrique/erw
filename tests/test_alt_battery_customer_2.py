"""Ruling alternative 2 of /battery/customer (session 7704, 17 November 2026, branch wip/alt-battery-customer-2; not a
default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-battery-customer-2026-11-17.md, line 2):
"Saved a year" is twelve of the month typed; should the page ask for the plan's seasons? On this branch the reader may
type up to two other seasons (months and three rates each) and the year is the sum over the seasons
(site/lib/customerbattery.ts yearBySeasons; site/app/battery/customer/Calc.tsx). Pinned with the page's own arithmetic on
the published cases of Salt River Project E-32 (site/scripts/alt-battery-customer-figures.mjs): the same customer and
battery read USD 8,783.57 a year by the plan's seasons (2 summer peak months, 4 summer, 6 winter), whichever season is
typed in the fields, against twelve of July's USD 13,376.42 (-34.3 percent), twelve of summer's 8,916.55 (-1.5 percent)
and twelve of winter's 7,163.97 (+22.6 percent).

    python -m unittest tests.test_alt_battery_customer_2 -v
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class TheYearBySeasons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-battery-customer-figures.mjs"], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stderr[-2000:])
        cls.f = json.loads(p.stdout)

    def test_salt_river_project_by_its_seasons(self):
        for main, twelve, first in (("srp-e32-summer-peak", 13376.42, 2), ("srp-e32-summer", 8916.55, 4), ("srp-e32-winter", 7163.97, 6)):
            g = self.f[main]
            self.assertEqual((round(g["twelve"], 2), round(g["by_seasons"], 2), g["first_months"]), (twelve, 8783.57, first), main)

    def test_a_season_typed_in_part_or_too_long_is_not_counted(self):
        self.assertEqual(self.f["empty"], "empty")
        self.assertIsNone(self.f["partly"])
        self.assertIsNone(self.f["too_many"])

    def test_the_calculator_reads_the_seasons(self):
        with open(os.path.join(SITE, "app", "battery", "customer", "Calc.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("yearBySeasons(x, whole)", s)
        self.assertIn('data-year-by={by ? "seasons" : "twelve"}', s)


if __name__ == "__main__":
    unittest.main()

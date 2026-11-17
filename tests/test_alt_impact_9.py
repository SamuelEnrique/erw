"""Ruling alternative 9 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-9; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 9): South Carolina's
plant at cost, or 11 percent of cost off a year to a 10 percent floor (Code 12-37-930, class 6(a); 12-37-935)? On this
branch the class 6(a) schedule (site/data/forecast/property_rules.json, sc_property). Pinned with the page's own model at a
levy of 300 per 1,000 (an example; the percent holds at any levy): property over the life, solar USD 261.62 to 54.43
million (-79.2 percent), wind -74.5 percent, gas 1,500.31 to 385.99 million (-74.3 percent).

    python -m unittest tests.test_alt_impact_9 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class SouthCarolinaClass6a(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": t, "tech": t, "state": "sc", "given": {"levy": 300}} for t in ("utility_pv", "land_based_wind", "natural_gas")])

    def test_property_over_the_life(self):
        self.assertEqual((M(self.f["utility_pv"]["sums"]["property"]), M(self.f["natural_gas"]["sums"]["property"])), (54.43, 385.99))

    def test_the_schedule(self):
        v = [y["value"] for y in self.f["natural_gas"]["years"]]
        cost = self.f["natural_gas"]["x"]["capex"] * self.f["natural_gas"]["x"]["mw"] * 1000
        self.assertEqual([round(a / cost / 0.105, 4) for a in v[:10]], [0.89, 0.78, 0.67, 0.56, 0.45, 0.34, 0.23, 0.12, 0.1, 0.1])


if __name__ == "__main__":
    unittest.main()

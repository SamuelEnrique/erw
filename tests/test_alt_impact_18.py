"""Ruling alternative 18 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-18; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 18): the Tax
Foundation's tables are licensed for no commercial use; keep them with attribution, or replace them by the statutes? On
this branch the statutes: a state's own sales tax rate is a statute figure and stays; the population-weighted average
local rate, which no statute gives, is left out, 0 in every state (site/data/forecast/sales_tax.json); the income tax
brackets are statute figures and stay. Pinned with the page's own model: the page as it opens (200 MW of Texas wind) reads
a sales tax rate of 6.25 percent and sales and use tax USD 15.18 million where main reads 8.2 percent and 19.92 million
(-23.8 percent).

    python -m unittest tests.test_alt_impact_18 -v
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, ROOT, run_cases  # noqa: E402


class TheTable(unittest.TestCase):
    def test_no_average_local_rate_is_held(self):
        with open(os.path.join(ROOT, "site", "data", "forecast", "sales_tax.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual({v["avg_local_rate"] for v in d["states"].values()}, {0})
        self.assertEqual(d["states"]["tx"]["state_rate"], 0.0625)


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class ThePageAsItOpens(unittest.TestCase):
    def test_texas_wind(self):
        f = run_cases([{"id": "opens", "tech": "land_based_wind", "state": "tx", "given": {}}])["opens"]
        self.assertEqual((f["x"]["sales"], M(f["sums"]["sales"])), (6.25, 15.18))


if __name__ == "__main__":
    unittest.main()

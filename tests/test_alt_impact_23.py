"""Ruling alternative 23 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-23; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 23): "Taxes, present
value" adds only the taxes with a figure; where the sum is 0 and made only of taxes not held, should it read "not held"?
On this branch it does (site/lib/forecast.ts: pv.taxes is null; site/app/impact/Forecast.tsx gives the reason). Pinned with
the page's own model on every default case (technology and state): 11 cases read "not held" where main reads USD 0:
geothermal in Alaska, Florida, New Hampshire, Nevada, South Dakota, Tennessee, Texas and Wyoming, and wind, gas and solar
in New Hampshire. The page as it opens still reads USD 19.92 million, all of it sales tax.

    python -m unittest tests.test_alt_impact_23 -v
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, ROOT, run_cases  # noqa: E402

TECHS = ["land_based_wind", "utility_pv", "natural_gas", "geothermal"]


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class TaxesNotHeld(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "site", "data", "forecast", "sales_tax.json"), encoding="utf-8") as f:
            states = sorted(json.load(f)["states"])
        cls.f = run_cases([{"id": f"{t}|{s}", "tech": t, "state": s, "given": {}} for t in TECHS for s in states])

    def test_the_eleven_cases(self):
        nulls = sorted(k for k, v in self.f.items() if v["ok"] and v["pv"]["taxes"] is None)
        want = sorted([f"geothermal|{s}" for s in ("ak", "fl", "nh", "nv", "sd", "tn", "tx", "wy")] + [f"{t}|nh" for t in ("land_based_wind", "natural_gas", "utility_pv")])
        self.assertEqual(nulls, want)

    def test_the_page_as_it_opens(self):
        self.assertEqual(M(self.f["land_based_wind|tx"]["pv"]["taxes"]), 19.92)


if __name__ == "__main__":
    unittest.main()

"""Ruling alternative 22 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-22; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 22): Texas solar by the
district's 10-year schedule (92, 84, 76, 67, 58, 49, 39, 30, 24, 21) or a straight line over 10 years to 20 percent (92,
84, 76, 68, 60, 52, 44, 36, 28, 20)? On this branch the straight line (site/data/forecast/property_rules.json, tx_solar).
Pinned with the page's own model at a levy of 20 (an example): property over the life USD 47.43 to 48.34 million (+1.9
percent), present value +2.3 percent.

    python -m unittest tests.test_alt_impact_22 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class TexasSolarStraightLine(unittest.TestCase):
    def test_texas_solar(self):
        f = run_cases([{"id": "pv", "tech": "utility_pv", "state": "tx", "given": {"levy": 20}}])["pv"]
        self.assertEqual(M(f["sums"]["property"]), 48.34)
        cost = f["x"]["capex"] * f["x"]["mw"] * 1000
        self.assertEqual([round(y["value"] / cost * 100, 6) for y in f["years"][:11]], [92, 84, 76, 68, 60, 52, 44, 36, 28, 20, 20])


if __name__ == "__main__":
    unittest.main()

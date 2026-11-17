"""Ruling alternative 17 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-17; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 17): should New Mexico
solar's cost taxed have the federal investment tax credit deducted? On this branch the base credit, 30 percent, is
deducted (site/data/forecast/property_rules.json, nm_solar: the assessment ratio is one third of 70 percent of cost; the
credit's rate, more with adders, is part of the ruling). Pinned with the page's own model at a levy of 30 (an example):
property tax -30.0 percent in every year and over the life, USD 35.90 to 25.13 million.

    python -m unittest tests.test_alt_impact_17 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class NewMexicoSolarCreditDeducted(unittest.TestCase):
    def test_new_mexico_solar(self):
        f = run_cases([{"id": "nm", "tech": "utility_pv", "state": "nm", "given": {"levy": 30}},
                       {"id": "wind", "tech": "land_based_wind", "state": "nm", "given": {"levy": 30}}])
        self.assertEqual(M(f["nm"]["sums"]["property"]), 25.13)
        cost = f["nm"]["x"]["capex"] * f["nm"]["x"]["mw"] * 1000
        self.assertAlmostEqual(f["nm"]["years"][0]["value"], cost * 0.98 * 0.3333 * 0.7, delta=1)
        w = f["wind"]
        self.assertAlmostEqual(w["years"][0]["value"], w["x"]["capex"] * w["x"]["mw"] * 1000 * 0.984 * 0.3333, delta=1)   # wind untouched


if __name__ == "__main__":
    unittest.main()

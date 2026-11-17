"""Ruling alternative 8 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-8; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 8): keep the Texas
rows that cite comptroller.texas.gov, or leave them out? On this branch they are left out: Texas's two property rules
(tx_solar, tx_property, citing the Comptroller's Valuing Property page, 96-1569 and 96-313) are notes
(site/data/forecast/property_rules.json), and Texas's gas severance (the Comptroller's natural gas production tax page) is
left out of the forecast (site/lib/forecastdata.ts SEVERANCE_LEFT_OUT; /severance's own page is not changed). Texas's
sales tax rates come from the Tax Foundation and stay. Pinned with the page's own model, a levy of 20 typed (an example):
Texas solar's property (USD 47.43 million over the life on main) and wind's (148.22 million) read "not held"; taxes,
present value 36.20 to 12.01 million and 89.01 to 19.92 million; CPV Basin Ranch's property and severance read "not held",
present value 535.21 to 58.99 million.

    python -m unittest tests.test_alt_impact_8 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class TexasComptrollerRowsLeftOut(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": "pv", "tech": "utility_pv", "state": "tx", "given": {"levy": 20}},
                           {"id": "wind", "tech": "land_based_wind", "state": "tx", "given": {"levy": 20}},
                           {"id": "cpv", "tech": "natural_gas", "state": "tx", "given": {"mw": 1445, "start": 2027, "instate": 100, "levy": 20}}])

    def test_property_and_severance_not_held(self):
        for k in ("pv", "wind", "cpv"):
            self.assertIsNone(self.f[k]["sums"]["property"], k)
        self.assertIsNone(self.f["cpv"]["sums"]["severance"])
        self.assertEqual(self.f["cpv"]["severance"]["note"], "no severance rule held for this state")

    def test_taxes_present_value(self):
        self.assertEqual({k: M(v["pv"]["taxes"]) for k, v in self.f.items()}, {"pv": 12.01, "wind": 19.92, "cpv": 58.99})


if __name__ == "__main__":
    unittest.main()

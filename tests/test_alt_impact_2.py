"""Ruling alternative 2 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-2; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 2): New York exempts
100 percent of the sales tax on a plant's taxable purchases; or only the machinery share the other states hold? On this
branch New York's exemption (site/data/forecast/sales_exemptions.json) is wind 66.9, solar 67.2, gas 58.3 percent, as for
Pennsylvania and the others. Pinned with the page's own model, each technology's default plant: sales and use tax from
USD 0 to 8.66 million (wind, 200 MW), 4.81 million (solar, 150 MW), 29.56 million (gas, 1,227 MW); taxes, present value
wind 4.17 to 12.83 million, solar 7.08 to 11.89 million, gas 23.55 to 52.14 million.

    python -m unittest tests.test_alt_impact_2 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class NewYorkMachineryShare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": t, "tech": t, "state": "ny", "given": {}} for t in ("land_based_wind", "utility_pv", "natural_gas")])

    def test_the_sales_tax_appears(self):
        got = {t: (self.f[t]["x"]["mw"], M(self.f[t]["sums"]["sales"])) for t in self.f}
        self.assertEqual(got, {"land_based_wind": (200, 8.66), "utility_pv": (150, 4.81), "natural_gas": (1227, 29.56)})

    def test_taxes_present_value(self):
        got = {t: M(self.f[t]["pv"]["taxes"]) for t in self.f}
        self.assertEqual(got, {"land_based_wind": 12.83, "utility_pv": 11.89, "natural_gas": 52.14})


if __name__ == "__main__":
    unittest.main()

"""Ruling alternative 13 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-13; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 13): in Nevada's
abated years, does "Taxable value" show the whole value (session 7515's change, NRS 701A.370 abating 55 percent of the
taxes) or 45 percent (the undo, commit 3baff8839)? On this branch 45 percent: the rule nv_renewable_abatement carries no
"abates" (site/data/forecast/property_rules.json). Pinned with the page's own model, Lone Mountain (36 MW, USD 4,956.83 per
kW, from 2026, the local option on, 1.0917 percent over 60 years): 2028's taxable value USD 80.30 million against 178.45
million (-55 percent), and 18 years' cells move; no tax moves: property over the life 36.04 million and taxes, present
value 10.71 million either way.

    python -m unittest tests.test_alt_impact_13 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402

LM = {"mw": 36, "capex": 4956.83, "start": 2026, "iaval": True, "own": 1.0917, "ownyears": 60}


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class NevadaTaxableValueAt45(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": "lm", "tech": "geothermal", "state": "nv", "given": LM}])["lm"]

    def test_2028_taxable_value(self):
        y = next(y for y in self.f["years"] if y["year"] == 2028)
        self.assertEqual(M(y["value"]), 80.30)

    def test_no_tax_moves(self):
        self.assertEqual((M(self.f["sums"]["property"]), M(self.f["pv"]["taxes"])), (36.04, 10.71))


if __name__ == "__main__":
    unittest.main()

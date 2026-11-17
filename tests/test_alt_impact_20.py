"""Ruling alternative 20 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-20; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 20): New Mexico's ad
valorem production tax is by district; should a district's rate be added to a gas plant's severance? On this branch the
median of the 35 districts /severance holds (1.249 percent) is added (site/lib/forecast.ts districtAdval, passed as the
`adval` of lib/severance.ts's input by the page and the replication). Pinned with the page's own model, New Mexico's default
gas plant with all its fuel from the state: severance each year USD 12.26 million to 14.19 million (+15.7 percent).

    python -m unittest tests.test_alt_impact_20 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class NewMexicoDistrictMedian(unittest.TestCase):
    def test_new_mexico_gas(self):
        f = run_cases([{"id": "nm", "tech": "natural_gas", "state": "nm", "given": {"instate": 100}},
                       {"id": "tx", "tech": "natural_gas", "state": "tx", "given": {"instate": 100}}])
        self.assertEqual(M(f["nm"]["y1"]["severance"]), 14.19)
        self.assertIsNotNone(f["tx"]["y1"]["severance"])   # a state with no district rate is as on main


if __name__ == "__main__":
    unittest.main()

"""Ruling alternative 4 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-4; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 4): Kansas's ten-year
exemption (K.S.A. 79-201, Eleventh) is granted on application; is it assumed granted? On this branch it is not: the rule
`ks_renewable_exempt` is a note (site/data/forecast/property_rules.json), so no rule is held for any year and the reader's
own rate fills them. Pinned with the page's own model: Kansas wind as opened reads "not held" in years 1 to 10 where main
reads USD 0 (the life has no total either way); with an own rate of 1.5 percent over 25 years typed, USD 60.02 million over
the life where main reads 22.16 million, present value 35.21 million where main reads 7.90 million.

    python -m unittest tests.test_alt_impact_4 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class KansasNotGranted(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": "opens", "tech": "land_based_wind", "state": "ks", "given": {}},
                           {"id": "own", "tech": "land_based_wind", "state": "ks", "given": {"own": 1.5, "ownyears": 25}}])

    def test_as_opened_the_ten_years_are_not_held(self):
        o = self.f["opens"]
        self.assertEqual([y["property"] for y in o["years"][:10]], [None] * 10)
        self.assertIsNone(o["sums"]["property"])

    def test_with_an_own_rate(self):
        o = self.f["own"]
        self.assertEqual((M(o["sums"]["property"]), M(o["pv"]["property"])), (60.02, 35.21))


if __name__ == "__main__":
    unittest.main()

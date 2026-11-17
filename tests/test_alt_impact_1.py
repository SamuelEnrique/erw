"""Ruling alternative 1 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 1): Iowa wind
without the county's ordinance reads "not held"; should the levy typed be applied to the capital cost? On this branch a
rule `ia_wind_full_cost` (site/data/forecast/property_rules.json, requires "no_option") applies the levy to the whole
capital cost in every year when the local option is off (an upper bound: no Iowa schedule for unordained wind is held).
Pinned with the page's own model: Silver Queen (252 MW, from 2027, levy 30): with the ordinance (A) USD 76.43 million over
the life, property in present value 30.99 million, as on main; without it (B) "not held" becomes USD 11.85 million a year,
296.25 million over 25 years, present value 138.09 million.

    python -m unittest tests.test_alt_impact_1 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402

SQ = {"mw": 252, "start": 2027, "levy": 30}


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class IowaWindWithoutTheOrdinance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": "a", "tech": "land_based_wind", "state": "ia", "given": {**SQ, "iaval": True}},
                           {"id": "b", "tech": "land_based_wind", "state": "ia", "given": {**SQ, "iaval": False}},
                           {"id": "opens", "tech": "land_based_wind", "state": "ia", "given": {}}])

    def test_with_the_ordinance_nothing_moves(self):
        a = self.f["a"]
        self.assertEqual((M(a["sums"]["property"]), M(a["pv"]["property"])), (76.43, 30.99))

    def test_without_it_the_levy_on_the_cost(self):
        b = self.f["b"]
        self.assertEqual((M(b["y1"]["property"]), M(b["sums"]["property"]), M(b["pv"]["property"])), (11.85, 296.25, 138.09))
        self.assertTrue(b["property"]["held"])

    def test_with_no_levy_it_stays_not_held(self):
        self.assertIsNone(self.f["opens"]["sums"]["property"])


if __name__ == "__main__":
    unittest.main()

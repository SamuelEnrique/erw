"""Ruling alternative 10 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-10; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 10): Texas holds no
sales tax exemption for generation equipment (0, an upper bound); should it take the machinery share the other states
hold? On this branch Texas has entries in site/data/forecast/sales_exemptions.json (wind 66.9, solar 67.2, gas 58.3
percent; no Texas statute is read: the share is the ruling's other choice). Pinned with the page's own model: the page as
it opens (200 MW of Texas wind) reads sales and use tax and "Taxes, present value" USD 6.58 million where main reads 19.92
million; Texas solar 12.01 to 3.94 million; CPV Basin Ranch (1,445 MW, from 2027, all fuel in state) 60.99 to 25.46
million, and the present value of its taxes 229.31 to 194.95 million.

    python -m unittest tests.test_alt_impact_10 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class TexasMachineryShare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = run_cases([{"id": "wind", "tech": "land_based_wind", "state": "tx", "given": {}},
                           {"id": "pv", "tech": "utility_pv", "state": "tx", "given": {}},
                           {"id": "cpv", "tech": "natural_gas", "state": "tx", "given": {"mw": 1445, "start": 2027, "instate": 100}}])

    def test_the_sales_tax(self):
        self.assertEqual({k: M(v["sums"]["sales"]) for k, v in self.f.items()}, {"wind": 6.58, "pv": 3.94, "cpv": 25.46})

    def test_the_page_as_it_opens_and_cpv(self):
        self.assertEqual((M(self.f["wind"]["pv"]["taxes"]), M(self.f["cpv"]["pv"]["taxes"])), (6.58, 194.95))


if __name__ == "__main__":
    unittest.main()

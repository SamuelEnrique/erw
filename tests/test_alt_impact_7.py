"""Ruling alternative 7 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-7; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 7): Iowa's solar
exemption (Code 423.3(90)) is held on the modules and inverters, 67.2 percent of JEDI's taxable purchases; does it reach
the racking and wiring? On this branch it does (site/data/forecast/sales_exemptions.json): JEDI's mounting and electrical
lines with the modules and inverters, 100 percent. Pinned with the page's own model: Iowa solar as opened reads sales and
use tax USD 0 where main reads 3.47 million; with the racking alone (83.6 percent, one constant away) 1.74 million.

    python -m unittest tests.test_alt_impact_7 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class IowaSolarRackingAndWiring(unittest.TestCase):
    def test_the_sales_tax(self):
        f = run_cases([{"id": "ia", "tech": "utility_pv", "state": "ia", "given": {}},
                       {"id": "racking", "tech": "utility_pv", "state": "ia", "given": {"exempt": 83.6066}}])
        self.assertEqual((f["ia"]["x"]["exempt"], M(f["ia"]["sums"]["sales"])), (100, 0.0))
        self.assertEqual(M(f["racking"]["sums"]["sales"]), 1.74)


if __name__ == "__main__":
    unittest.main()

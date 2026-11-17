"""Ruling alternative 6 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-6; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 6): Missouri's
machinery exemption and California's 3.9375 points are held on the generating machinery only, so the tax errs high;
should they reach foundations too? On this branch they reach every taxable purchase, the bounds, since the foundations'
own share is not held (site/data/forecast/sales_exemptions.json). Pinned with the page's own model: Missouri wind's sales
and use tax USD 7.69 million to 0; California solar 10.83 to 8.64 million (-20.2 percent); California wind 19.56 to 15.58
million (-20.4 percent).

    python -m unittest tests.test_alt_impact_6 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class FoundationsCounted(unittest.TestCase):
    def test_the_sales_tax_at_the_bounds(self):
        f = run_cases([{"id": "mo", "tech": "land_based_wind", "state": "mo", "given": {}},
                       {"id": "cas", "tech": "utility_pv", "state": "ca", "given": {}},
                       {"id": "caw", "tech": "land_based_wind", "state": "ca", "given": {}}])
        self.assertEqual({k: M(v["sums"]["sales"]) for k, v in f.items()}, {"mo": 0.0, "cas": 8.64, "caw": 15.58})
        self.assertEqual({k: v["x"]["exempt"] for k, v in f.items()}, {"mo": 100, "cas": 43.6047, "caw": 43.6047})


if __name__ == "__main__":
    unittest.main()

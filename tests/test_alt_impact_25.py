"""Ruling alternative 25 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-25; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 25): split the sales
tax into the state's part and the average local part? On this branch the A and B table has two rows more (site/lib/forecast.ts
run: sales.state and sales.local, stat "split:state" and "split:local"; site/app/impact/Forecast.tsx; the replication reads
them). Figures added, the total unmoved. Pinned with the page's own model: the page as it opens USD 19.92 million = 15.18 to
the state (6.25 points) and 4.74 at the average local rate (1.95); CPV Basin Ranch 60.99 = 46.48 and 14.50. The property
tax's receivers need each statute's sharing clause: not built.

    python -m unittest tests.test_alt_impact_25 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class TheSalesTaxSplit(unittest.TestCase):
    def test_two_cases(self):
        f = run_cases([{"id": "opens", "tech": "land_based_wind", "state": "tx", "given": {}},
                       {"id": "cpv", "tech": "natural_gas", "state": "tx", "given": {"mw": 1445, "start": 2027, "instate": 100}}])
        got = {k: (M(v["sums"]["sales"]), M(v["sales"]["state"]), M(v["sales"]["local"])) for k, v in f.items()}
        self.assertEqual(got, {"opens": (19.92, 15.18, 4.74), "cpv": (60.99, 46.48, 14.5)})
        for v in f.values():
            self.assertAlmostEqual(v["sales"]["state"] + v["sales"]["local"], v["sums"]["sales"], delta=1e-6)


if __name__ == "__main__":
    unittest.main()

"""Ruling alternative 24 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-24; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 24): show the on-site
jobs beside the three effects? On this branch the A and B table has two rows more, "Construction jobs on site" and
"Operating jobs on site, each year" (site/app/impact/Forecast.tsx; the replication reads them too). Figures are added,
none moved. Pinned with the page's own model: Lone Mountain 605 construction job-years of which 259 on site, 32.0 operating
jobs a year of which 23.1; the page as it opens 515 and 72, 44.7 and 9.1; CPV Basin Ranch 2,358 and 747, 232.5 and 73.2.

    python -m unittest tests.test_alt_impact_24 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, ROOT, run_cases  # noqa: E402


class TheRows(unittest.TestCase):
    def test_the_table_draws_them(self):
        with open(os.path.join(ROOT, "site", "app", "impact", "Forecast.tsx"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('figure: "c:jobs:onsite"', s)
        self.assertIn('figure: "o:jobs:onsite"', s)


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class TheFigures(unittest.TestCase):
    def test_three_cases(self):
        f = run_cases([{"id": "lm", "tech": "geothermal", "state": "nv", "given": {"mw": 36, "capex": 4956.83, "start": 2026}},
                       {"id": "opens", "tech": "land_based_wind", "state": "tx", "given": {}},
                       {"id": "cpv", "tech": "natural_gas", "state": "tx", "given": {"mw": 1445, "start": 2027, "instate": 100}}])
        got = {k: (round(v["construction"]["jobs"]["total"]), round(v["construction"]["jobs"]["onsite"]),
                   round(v["operations"]["jobs"]["total"], 1), round(v["operations"]["jobs"]["onsite"], 1)) for k, v in f.items()}
        self.assertEqual(got, {"lm": (605, 259, 32.0, 23.1), "opens": (515, 72, 44.7, 9.1), "cpv": (2358, 747, 232.5, 73.2)})


if __name__ == "__main__":
    unittest.main()

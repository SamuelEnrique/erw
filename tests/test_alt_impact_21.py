"""Ruling alternative 21 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-21; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 21): Nevada's 20 abated
years counted from the first construction year, or from the first operating year as the Department of Taxation counts
them? On this branch from the first operating year (site/data/forecast/property_rules.json, nv_renewable_abatement
years_from "operation"; the engine, the run's Python and Stata files and the replication read it). Pinned with the page's
own model, Lone Mountain (36 MW, USD 4,956.83 per kW, from 2026, two construction years, the local option on, 1.0917
percent over 60 years): the first 20 operating years 2028 to 2047 pay USD 14.76 million against 16.24 million (the
Department's note: 15,034,766, which lies between); over the life 36.04 to 34.56 million; property in present value
10.71 to 10.34 million (-3.5 percent).

    python -m unittest tests.test_alt_impact_21 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402

LM = {"mw": 36, "capex": 4956.83, "start": 2026, "iaval": True, "own": 1.0917, "ownyears": 60}


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class NevadaYearsFromOperation(unittest.TestCase):
    def test_lone_mountain(self):
        f = run_cases([{"id": "lm", "tech": "geothermal", "state": "nv", "given": LM}])["lm"]
        first20 = [y for y in f["years"] if 2028 <= y["year"] <= 2047]
        self.assertEqual(len(first20), 20)
        self.assertEqual(M(sum(y["property"] for y in first20)), 14.76)
        self.assertEqual((M(f["sums"]["property"]), M(f["pv"]["property"])), (34.56, 10.34))


if __name__ == "__main__":
    unittest.main()

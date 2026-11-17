"""Ruling alternative 16 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-16; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 16): Virginia solar's
exemption (Code 58.1-3660) by subsection F's steps (80, 70, 60 percent) or subsection D's flat 80 percent? On this branch
D's flat 80 percent (site/data/forecast/property_rules.json, va_solar_exemption). Pinned with the page's own model, 100 MW
with an own rate of 1.0 percent over 35 years (an example): property over the life USD 9.24 to 5.68 million (-38.5
percent); present value 4.08 to 2.84 million (-30.5 percent). The revenue share needs a price forecast the tool does not
hold: not built.

    python -m unittest tests.test_alt_impact_16 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class VirginiaSubsectionD(unittest.TestCase):
    def test_virginia_solar(self):
        f = run_cases([{"id": "va", "tech": "utility_pv", "state": "va", "given": {"mw": 100, "own": 1.0, "ownyears": 35}}])["va"]
        self.assertEqual((M(f["sums"]["property"]), M(f["pv"]["property"])), (5.68, 2.84))


if __name__ == "__main__":
    unittest.main()

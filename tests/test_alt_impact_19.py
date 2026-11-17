"""Ruling alternative 19 of /impact (session 7706, 17 November 2026, branch wip/alt-impact-19; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-impact-2026-11-17.md, line 19): Oregon's solar fee
in lieu starts at the statute's maximum, USD 7,000 per MW; or at a lower figure? On this branch the field starts at the
statute's minimum, USD 5,500 (site/data/forecast/property_rules.json). Pinned with the page's own model, Oregon solar as
opened (150 MW) with the option on: USD 1.05 to 0.82 million a year (-21.4 percent); the 20 years 21.00 to 16.50 million;
their present value 11.12 to 8.74 million.

    python -m unittest tests.test_alt_impact_19 -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from alt_impact_cases import JEDI_CSV, M, run_cases  # noqa: E402


@unittest.skipUnless(JEDI_CSV, "nlr_jedi_multipliers.csv is not on this machine")
class OregonFeeAtTheMinimum(unittest.TestCase):
    def test_oregon_solar(self):
        f = run_cases([{"id": "or", "tech": "utility_pv", "state": "or", "given": {"iaval": True}}])["or"]
        x = f["x"]
        self.assertEqual((x["optrate"], M(f["y1"]["property"])), (5500, 0.82))
        twenty = [y for y in f["years"][:20]]
        self.assertEqual(M(sum(y["property"] for y in twenty)), 16.5)
        pv = sum(y["property"] / (1 + x["rate"] / 100) ** (y["year"] - x["start"]) for y in twenty)
        self.assertEqual(M(pv), 8.74)


if __name__ == "__main__":
    unittest.main()

"""Audit of Automated Analysis, finding 7 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): a trend
from four years passes the hunt's five tests.

hunt.test_claim needs four full years for its window test and three for its fourth test, nothing more. Four points
rising by one a year pass all five (strength 2.02). Of the sheet's forty, 7 rest on seven full years and 2 on six
(drafts 33 and 39). Passes on main; a floor of full years would change what is drafted: the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


class FourYearsAreEnough(unittest.TestCase):
    def test_four_rising_points_pass(self):
        import hunt
        c = hunt.test_claim({"2021": (1.0, 1.0), "2022": (2.0, 1.0), "2023": (3.0, 1.0), "2024": (4.0, 1.0)},
                            {"n_floor": 1, "decimals": 2, "unit": "u"}, 2026)
        self.assertTrue(c["passed"], c["tests"])
        self.assertAlmostEqual(c["strength"], 2.0235, places=3)

    def test_three_points_cannot(self):
        import hunt
        c = hunt.test_claim({"2022": (1.0, 1.0), "2023": (2.0, 1.0), "2024": (3.0, 1.0)}, {"n_floor": 1, "decimals": 2, "unit": "u"}, 2026)
        self.assertFalse(c["passed"])


if __name__ == "__main__":
    unittest.main()

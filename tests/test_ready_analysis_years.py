"""wip/ready-analysis-years (session 11406, chain 770, part C): the other choice of the Automated Analysis audit of
26 November, finding 7 (docs/reviews/analysis-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main hunt.test_claim passes a trend from four full years (four rising points pass all five tests, strength 2.02).
On this branch a sixth test asks for at least eight full years (YEARS_FLOOR). The audit counted 9 of the forty
shortlisted drafts on six or seven full years (drafts 1, 3, 8, 9, 10, 11, 19, 33 and 39): they would not be drafted
again; 28 of the 37 yearly claims keep passing. The audit's own test (tests/test_audit_analysis_7.py on
wip/audit-analysis-7) is carried here, asserting the new behaviour."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
P = {"n_floor": 1, "decimals": 2, "unit": "u"}


def rising(n, first=2010):
    return {str(first + i): (1.0 + i, 1.0) for i in range(n)}


class AFloorOfFullYears(unittest.TestCase):
    def test_four_rising_points_no_longer_pass(self):
        import hunt
        c = hunt.test_claim(rising(4, 2021), P, 2026)
        self.assertFalse(c["passed"])
        self.assertEqual([t["name"] for t in c["tests"] if not t["passed"]], ["enough full years"])
        self.assertAlmostEqual(c["strength"], 2.0235, places=3)     # every other test still passes

    def test_seven_fail_and_eight_pass(self):
        import hunt
        self.assertEqual(hunt.YEARS_FLOOR, 8)
        self.assertFalse(hunt.test_claim(rising(7, 2018), P, 2026)["passed"])
        c = hunt.test_claim(rising(8, 2017), P, 2026)
        self.assertTrue(c["passed"], c["tests"])
        self.assertEqual(c["tests"][-1]["words"], "8 full years are held, 2017 to 2024; the floor is 8")


if __name__ == "__main__":
    unittest.main()

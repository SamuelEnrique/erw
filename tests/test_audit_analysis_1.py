"""Audit of Automated Analysis, finding 1 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): the hunt's
five tests are not a test against chance.

hunt.test_claim, the tests every weekly-hunt and deep-hunt draft must pass, is run on simulated yearly series with no
trend at all. A random walk of 11 full years passes all five more than 40 percent of the time, independent years
more than 8 percent, and the strength of a noiseless line is (n - 1) / 1.4826: it counts years. This test shows the
finding; it passes on main. The fix (a test against chance, the count of claims tried) is the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
import os
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))

P = {"n_floor": 1, "decimals": 2, "unit": "u"}


def series_of(vals):
    return {str(2000 + i): (float(v), 1.0) for i, v in enumerate(vals)}


class FiveTestsUnderNoTrend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import hunt
        cls.hunt = hunt

    def share(self, make, n, trials=1500):
        rng = np.random.default_rng(10204)
        passed = 0
        for _ in range(trials):
            c = self.hunt.test_claim(series_of(make(rng, n)), P, 2100)
            passed += bool(c and c["passed"])
        return passed / trials

    def test_random_walk_passes_often(self):
        s = self.share(lambda r, n: np.cumsum(r.standard_normal(n)), 11)
        self.assertGreater(s, 0.40, s)

    def test_independent_years_pass_too(self):
        s = self.share(lambda r, n: r.standard_normal(n), 11)
        self.assertGreater(s, 0.08, s)

    def test_strength_counts_years(self):
        for n in (6, 11, 45):
            c = self.hunt.test_claim(series_of(np.arange(n, dtype=float)), P, 2100)
            self.assertAlmostEqual(c["strength"], round((n - 1) / 1.4826, 4), places=3)


if __name__ == "__main__":
    unittest.main()

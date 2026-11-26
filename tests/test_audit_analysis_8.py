"""Audit of Automated Analysis, finding 8 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): the chart
of the week is the largest of 21 to 31 scores, and its caption reads as one measure's rank.

warehouse/analysis/run.py: each measure's change is scored by the share of its own last 104 changes that were smaller,
and the highest score is chosen. Through run.change itself, 21 measures that are random walks (nothing moved more than
usual) give a largest score at or above 87.5 (W44's WTI: "Of the 104 week-to-week moves before it, 13 were as large")
in more than 85 percent of trials; 1 - 0.875^21 is 0.94. Passes on main; saying so on the caption is the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
import datetime as dt
import os
import sys
import unittest

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


def weeks(n):
    a = dt.date(2024, 10, 7)
    return [f"{a + dt.timedelta(weeks=i)} to {a + dt.timedelta(weeks=i, days=6)}" for i in range(n)]


class LargestOfManyScores(unittest.TestCase):
    def test_the_top_score_is_high_by_selection(self):
        import run
        rng = np.random.default_rng(10204)
        ps = weeks(106)
        trials, high = 300, 0
        for _ in range(trials):
            best = 0.0
            for _m in range(21):
                v = np.cumsum(rng.standard_normal(106))
                head = {"period": ps[-1], "value": float(v[-1]), "history": [(p, float(x)) for p, x in zip(ps[:-1], v[:-1])]}
                ch = run.change(head, "previous")
                self.assertEqual(len(ch["earlier"]), 104)
                best = max(best, ch["score"])
            high += best >= 87.5
        self.assertGreater(high / trials, 0.85, high / trials)


if __name__ == "__main__":
    unittest.main()

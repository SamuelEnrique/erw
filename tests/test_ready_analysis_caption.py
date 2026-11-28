"""wip/ready-analysis-caption (session 11406, chain 770, part C): the other choice of the Automated Analysis audit of
26 November, finding 8 (docs/reviews/analysis-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the chart of the week's caption reads as one measure's rank ("Of the 104 week-to-week moves before it, 13 were
as large"), though the move is the top of 21 to 31 measures' scores (W41 31, W43 25, W44 21, W45 21, the audit's a4).
On this branch, when the pick is by change score, the caption and the finding gain a third sentence: "It was picked as
the largest of 21 measures' moves this week, each ranked against its own earlier moves." No score and no choice moves.
The audit's own test (tests/test_audit_analysis_8.py on wip/audit-analysis-8) is carried: under no change the largest
of 21 scores is at or above 87.5 in more than 85 percent of trials (1 - 0.875 ** 21 = 0.94)."""
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


class TheCaptionSaysLargestOfN(unittest.TestCase):
    def test_the_sentence(self):
        import run
        self.assertEqual(run.largest_of(21), "It was picked as the largest of 21 measures' moves this week, each ranked against its own earlier moves.")
        self.assertEqual(run.largest_of(1), "")

    def test_main_adds_it_when_picked_by_change_score(self):
        with open(os.path.join(ROOT, "warehouse", "analysis", "run.py"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn('if found and (how_picked == "the rule" or how_picked.startswith("no measure\'s newest")):', text)
        self.assertIn("found = (found[0], found[1], largest_of(len(pool)))", text)
        self.assertIn('(" " + found[2] if len(found) > 2 and found[2] else "")', text)   # kept when the two sentences are too long

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
                best = max(best, run.change(head, "previous")["score"])
            high += best >= 87.5
        self.assertGreater(high / trials, 0.85, high / trials)


if __name__ == "__main__":
    unittest.main()

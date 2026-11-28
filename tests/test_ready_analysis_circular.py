"""wip/ready-analysis-circular (session 11406, chain 770, part C): the other choice of the Automated Analysis audit of
26 November, finding 4 (docs/reviews/analysis-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the deep hunt's cheapest_hour is a plain mean of clock hours, so days cheapest at 23:00 and 01:00 average to
noon. On this branch it is the circular mean (each hour a point on a 24-hour clock): they average to midnight. On
HB_NORTH the audit measured 2015 at 6.04 by the plain mean and 2.54 by the circular mean, 2025 at 10.67 and 10.59; the
move is 8.0 hours, not 4.6 (the audit's a3; the 707 MB hub history is not re-read on this machine). The audit's own
test (tests/test_audit_analysis_4.py on wip/audit-analysis-4) is carried here, asserting the new value. The Python and
Stata reproductions compute the same circular mean."""
import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEEP = os.path.join(ROOT, "warehouse", "analysis", "findings", "deep")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
sys.path.insert(0, DEEP)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))


def hours_of(days=40, a=23, b=1):
    rows = []
    start = pd.Timestamp("2024-01-01 06:00", tz="UTC")
    for d in range(days):
        cheap = a if d % 2 == 0 else b
        for lh in range(24):
            hour = start + pd.Timedelta(days=d, hours=lh)
            rows.append({"hour": hour, "rt": 10.0 if lh == cheap else 30.0 + lh % 5, "lhour": lh,
                         "day": f"2024-{1 + d // 28:02d}-{1 + d % 28:02d}", "year": 2024})
    return pd.DataFrame(rows)


def run(g):
    import prices
    import prices_markets
    saved = prices.nodes
    prices.nodes = lambda in_dir=None: [("ercot_HB_TEST", "a test hub", "HB_TEST", g, "a table")]
    try:
        return [r["value"] for r in prices_markets.cheapest_hour(None)["rows"]]
    finally:
        prices.nodes = saved


class CheapestHourOnAClock(unittest.TestCase):
    def test_night_hours_average_to_midnight(self):
        vals = run(hours_of())
        self.assertEqual(len(vals), 1)
        self.assertTrue(vals[0] < 1e-6 or vals[0] > 24 - 1e-6, vals[0])   # midnight, not noon (main: 12.0)

    def test_hours_that_do_not_wrap_are_their_mean(self):
        vals = run(hours_of(a=9, b=11))
        self.assertAlmostEqual(vals[0], 10.0, places=6)

    def test_the_reproductions_say_the_same(self):
        import prices_markets
        with open(prices_markets.__file__, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("np.arctan2(np.sin(a).mean(), np.cos(a).mean())", text)
        self.assertIn('"generate double measure = mod(atan2(s, c) * 24 / (2 * _pi), 24)"', text)
        self.assertIn("the circular mean of the local clock hour", text)
        self.assertNotIn("float(s['lhour'].mean())", text)


if __name__ == "__main__":
    unittest.main()

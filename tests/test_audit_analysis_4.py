"""Audit of Automated Analysis, finding 4 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): the deep
hunt's cheapest_hour is a plain mean of clock hours, so a cheapest hour that moves across midnight averages to noon.

warehouse/analysis/findings/deep/prices_markets.py, cheapest_hour: the year's mean of the local clock hour at which
each day's lowest price fell. Fed days whose cheapest hour alternates 23:00 and 01:00 (never midday), the module
returns 12. Draft 6 of the sheet (HB_NORTH, 6.0 in 2015 against 10.7 in 2025): 39.7 percent of 2015's days are
cheapest from 21:00 to 02:59, the circular mean is 2.54 and the median 3 (the audit's a3). Passes on main; the fix
(a circular mean or the median) moves a figure: the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
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


def hours_of(days=40):
    rows = []
    start = pd.Timestamp("2024-01-01 06:00", tz="UTC")
    for d in range(days):
        cheap = 23 if d % 2 == 0 else 1
        for lh in range(24):
            hour = start + pd.Timedelta(days=d, hours=lh)
            rows.append({"hour": hour, "rt": 10.0 if lh == cheap else 30.0 + lh % 5, "lhour": lh,
                         "day": f"2024-{1 + d // 28:02d}-{1 + d % 28:02d}", "year": 2024})
    return pd.DataFrame(rows)


class CheapestHourWrapsAtMidnight(unittest.TestCase):
    def test_night_hours_average_to_noon(self):
        import prices
        import prices_markets
        g = hours_of()
        saved = prices.nodes
        prices.nodes = lambda in_dir=None: [("ercot_HB_TEST", "a test hub", "HB_TEST", g, "a table")]
        try:
            got = prices_markets.cheapest_hour(None)
        finally:
            prices.nodes = saved
        vals = [r["value"] for r in got["rows"]]
        self.assertEqual(len(vals), 1)
        self.assertAlmostEqual(vals[0], 12.0, places=6)
        a = np.angle(np.exp(2j * np.pi * np.array([23, 1] * 20) / 24).mean()) * 24 / (2 * np.pi) % 24
        self.assertTrue(a < 0.01 or a > 23.99)


if __name__ == "__main__":
    unittest.main()

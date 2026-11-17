"""Session 7051 (chain 370, the data machine): done-line request 141.

hub_price_comparison's <m>_day_spread_top4_bottom4 is the spread of the window's average day. Beside it,
<m>_daily_spread_mean_top4_bottom4 is the mean over the window's whole local days of each day's four dearest hours less
its four cheapest, with <m>_daily_spread_days the days used (a day missing an hour is left out).
"""

import importlib.util
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    spec = importlib.util.spec_from_file_location("price_compare_7051", os.path.join(ROOT, "warehouse", "derived", "price_compare.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheMeanDailySpread(unittest.TestCase):
    def test_each_whole_day_is_spread_then_averaged(self):
        m = builder()
        tz = "America/Chicago"
        idx = pd.date_range(pd.Timestamp("2026-10-05", tz=tz), pd.Timestamp("2026-10-08", tz=tz), freq="h", inclusive="left").tz_convert("UTC")
        hour = idx.tz_convert(tz).hour
        day = idx.tz_convert(tz).day
        price = pd.Series([float(h) * (1 if d == 5 else 2) for h, d in zip(hour, day)], index=idx)
        price = price.drop(price.index[-1])          # 7 October misses its last hour: not a whole day
        r = m.measures(price, tz)
        # 5 October: (20+21+22+23)/4 - (0+1+2+3)/4 = 20; 6 October: twice that, 40; mean of the two whole days 30
        self.assertEqual((r["daily_spread_mean_top4_bottom4"], r["daily_spread_days"]), (30.0, 2))


if __name__ == "__main__":
    unittest.main()

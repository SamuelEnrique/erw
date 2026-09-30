"""Session 37: the cost-of-power model's rules (warehouse/derived/cost_of_power.py).

Energy Research Warehouse (ERW). No network, no model: small frames built here.

    python -m unittest tests.test_session37 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))

import cost_of_power as cp  # noqa: E402


def frame(ts, values, freq):
    t = pd.to_datetime(ts, utc=True)
    return pd.DataFrame({"ts": t, "value": values, "freq": freq})


class HourlyPrices(unittest.TestCase):
    def test_an_hour_needs_every_interval(self):
        ts = ["2026-08-01T00:00:00Z", "2026-08-01T00:15:00Z", "2026-08-01T00:30:00Z", "2026-08-01T00:45:00Z",
              "2026-08-01T01:00:00Z", "2026-08-01T01:15:00Z", "2026-08-01T01:30:00Z"]
        h = cp.hourly(frame(ts, [10, 20, 30, 40, 1, 2, 3], "PT15M"))
        self.assertEqual(len(h), 1)  # 01:00 has three of four intervals: left out
        self.assertAlmostEqual(h.iloc[0], 25.0)

    def test_hourly_prices_pass_through(self):
        h = cp.hourly(frame(["2026-08-01T00:00:00Z", "2026-08-01T01:00:00Z"], [5.0, 7.0], "PT1H"))
        self.assertEqual(list(h), [5.0, 7.0])


class MonthHours(unittest.TestCase):
    def test_clock_changes(self):
        self.assertEqual(cp.hours_in_month("2026-03", "America/Chicago"), 743)
        self.assertEqual(cp.hours_in_month("2025-11", "America/Chicago"), 721)
        self.assertEqual(cp.hours_in_month("2026-03", "EST"), 744)  # MISO: no clock change
        self.assertEqual(cp.hours_in_month("2026-09", "America/Los_Angeles"), 720)


class LoadWeighting(unittest.TestCase):
    def test_load_weighted_against_simple(self):
        # two hours: the dear hour carries three times the demand, so the load-weighted price is above the simple mean
        price, demand = pd.Series([10.0, 50.0]), pd.Series([100.0, 300.0])
        lw = (price * demand).sum() / demand.sum()
        self.assertAlmostEqual(lw, 40.0)
        self.assertAlmostEqual(lw - price.mean(), 10.0)  # the shape premium


class Tables(unittest.TestCase):
    """The built tables, when this machine holds them: keys unique, PJM absent, partial months labelled."""

    def setUp(self):
        self.path = os.path.join(ROOT, "warehouse", "output", "cost_of_power_monthly.csv")
        if not os.path.exists(self.path):
            self.skipTest("cost_of_power_monthly.csv is not on this machine")

    def test_keys_and_scope(self):
        d = pd.read_csv(self.path, comment="#")
        self.assertFalse(d.duplicated(["entity", "variable", "ts_utc"]).any())
        self.assertFalse(d["entity"].str.startswith("pjm").any())
        p = d.pivot_table(index=["entity", "ts_utc"], columns="variable", values="value")
        # every month with real-time hours has its month length, and never more hours than the month holds
        rt = p.dropna(subset=["rt_hours"])
        self.assertTrue(rt["hours_in_month"].notna().all())
        self.assertTrue((rt["rt_hours"] <= rt["hours_in_month"]).all())


if __name__ == "__main__":
    unittest.main()

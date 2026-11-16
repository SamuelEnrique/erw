"""Session 7022 (chain 301, the data machine, 16 November 2026): done-line request 44.

carbon_intensity_monthly keeps a month only when every UTC day is complete, so on 16 November eia930:CISO held 6 of
the last twelve months and the datacenter page's twelve-month carbon rested on half a year. Beside those values (left
as they are), the builder now writes every month's hours held (<intensity>_hours_held), the month's CO2 over its MWh
in those hours where at least 90 percent are held (<intensity>_over_held_hours), and names the short days of the last
twelve whole months. The hours below are built here; the real tables' months are in the session's report.
"""

import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    path = os.path.join(ROOT, "warehouse", "derived", "carbon_intensity.py")
    spec = importlib.util.spec_from_file_location("carbon_intensity_7022", path)
    m = importlib.util.module_from_spec(spec)
    saved = sys.argv
    try:
        sys.argv = ["carbon_intensity.py"]
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    return m


def hours(start, end, drop=()):
    ts = pd.date_range(start, end, freq="h", inclusive="left", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    ts = [t for t in ts if t[:10] not in drop and t[:13] not in drop]
    return pd.DataFrame({"entity": "eia930:TEST", "geo": "US", "ba": "TEST", "ts_utc": ts, "co2": 300.0, "mwh": 1000.0})


class TheHeldMonths(unittest.TestCase):
    def setUp(self):
        self.m = builder()

    def test_a_month_with_most_hours_held_has_a_value_and_its_count(self):
        # January 2026 whole; February short of two days (624 of 672 hours, 92.9 percent); March short of five (91.9 percent
        # is 684 of 744: five days off leaves 624, 83.9 percent, under the line); April 2026 partial (the newest month)
        j = pd.concat([hours("2026-01-01", "2026-02-01"), hours("2026-02-01", "2026-03-01", drop=("2026-02-10", "2026-02-11")),
                       hours("2026-03-01", "2026-04-01", drop=("2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05", "2026-03-06")),
                       hours("2026-04-01", "2026-04-03")])
        h, named = self.m.held_months(j)
        by = {r.month: r for r in h.itertuples()}
        self.assertEqual((by["2026-01"].hours, by["2026-01"].value), (744.0, 300.0))
        self.assertEqual((by["2026-02"].hours, by["2026-02"].value), (624.0, 300.0))
        self.assertEqual(by["2026-03"].hours, 624.0)
        self.assertTrue(pd.isna(by["2026-03"].value))
        self.assertTrue(pd.isna(by["2026-04"].value))          # 48 hours of a month in progress
        self.assertEqual(self.m.MOST_HOURS, 0.9)

    def test_the_short_days_are_named(self):
        j = pd.concat([hours("2025-02-01", "2026-02-01", drop=("2025-03-09", "2026-01-15T03", "2026-01-15T04")), hours("2026-02-01", "2026-02-02")])
        _, named = self.m.held_months(j)
        self.assertEqual(named, "2025-03-09 (0 hours), 2026-01-15 (22 hours)")   # a day not held at all is short too
        # many short days are told by month
        _, many = self.m.held_months(pd.concat([hours("2026-01-01", "2026-02-01"), hours("2026-02-01", "2026-02-02")]))
        self.assertTrue(many.startswith("2025-02: 28 short days, 672 hours missing"), many[:80])


if __name__ == "__main__":
    unittest.main()

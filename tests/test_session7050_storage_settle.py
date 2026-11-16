"""Session 7050 (chain 370, the data machine, 16 November 2026): done-line request 79.

storage_daily_cycle wrote ERCOT's 14 November 2026 with all 24 hours present but EIA's early, unfilled values (3,755
MWh discharged against 26,495 to 32,528 on the five days before). A local day is now written only when it ended at
least 48 hours before the area's newest held hour, so the storage connector, which asks for its last three days again
each run, has asked EIA for it since its first posting.
"""

import datetime as dt
import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    spec = importlib.util.spec_from_file_location("storage_daily_cycle_7050", os.path.join(ROOT, "warehouse", "derived", "storage_daily_cycle.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheDaysHeldBack(unittest.TestCase):
    def setUp(self):
        self.m = builder()

    def test_a_day_within_48_hours_of_the_newest_hour_waits(self):
        newest = pd.Timestamp("2026-11-15T23:00:00Z")          # the newest hour held starts 23:00 UTC on 15 November
        tz = "America/Chicago"
        self.assertFalse(self.m.settled(dt.date(2026, 11, 14), tz, newest))   # ended 15 Nov 06:00 UTC: 18 hours before
        self.assertTrue(self.m.settled(dt.date(2026, 11, 12), tz, newest))    # ended 13 Nov 06:00 UTC: 66 hours before
        self.assertEqual(self.m.SETTLE_HOURS, 48)

    def test_the_line_is_48_hours_after_the_days_end(self):
        tz = "America/Chicago"
        end = pd.Timestamp("2026-11-13T06:00:00Z")             # the end of 12 November, Central time
        self.assertTrue(self.m.settled(dt.date(2026, 11, 12), tz, end + pd.Timedelta(hours=47)))    # its last hour then ends 48 hours on
        self.assertFalse(self.m.settled(dt.date(2026, 11, 12), tz, end + pd.Timedelta(hours=46)))


if __name__ == "__main__":
    unittest.main()

"""Session 7051 (chain 370, the data machine): done-line request 149.

The board's year base of a weekly series was the newest value at least 365 days back, so EIA's storage week ending
2026-11-06 was set beside 2025-10-31; EIA's report and /supply set a week beside the same week a year before
(2025-11-07). A weekly series' base is now the value 364 days back, or the nearest within 3 days.
"""

import datetime as dt
import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    spec = importlib.util.spec_from_file_location("board_page_7051", os.path.join(ROOT, "warehouse", "derived", "board_page.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheSameWeekAYearBefore(unittest.TestCase):
    def test_a_weekly_series_is_set_beside_the_week_52_weeks_back(self):
        m = builder()
        s = {dt.date(2025, 10, 31): -43.0, dt.date(2025, 11, 7): -88.0, dt.date(2026, 10, 30): 10.0, dt.date(2026, 11, 6): 5.0}
        self.assertEqual(m.stats(s, "W")["moves"]["y"]["t"], "2025-11-07")

    def test_a_daily_series_keeps_its_rule(self):
        m = builder()
        s = {dt.date(2025, 11, 5): 1.0, dt.date(2025, 11, 7): 2.0, dt.date(2026, 11, 6): 3.0}
        self.assertEqual(m.stats(s, "D")["moves"]["y"]["t"], "2025-11-05")   # the newest at least 365 days back


if __name__ == "__main__":
    unittest.main()

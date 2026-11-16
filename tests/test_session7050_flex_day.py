"""Session 7050 (chain 370, the data machine, 16 November 2026): done-line request 59.

CAISO's Flex Alert for Thursday 1 October 2020 was issued on 30 September; its time frame reads "10/1/2020 15:00:00
through 22:00:00". caiso_grid_emergencies writes a row per local day covered, but span() read a frame of one date and
two clock times as the record's own day (the issue day), so the alert stood on 2020-09-30. Now the date the frame names
is the day, as warehouse/derived/flex_alert_scorecard.py window() reads it.
"""

import datetime as dt
import importlib.util
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def connector():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    spec = importlib.util.spec_from_file_location("caiso_emergencies_7050", os.path.join(ROOT, "warehouse", "connectors", "caiso_emergencies.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheDayTheFrameNames(unittest.TestCase):
    def setUp(self):
        self.m = connector()

    def test_one_date_and_two_clock_times_is_that_dates_window(self):
        days, start, end = self.m.span("10/1/2020 15:00:00 through 22:00:00", dt.date(2020, 9, 30))
        self.assertEqual(days, [dt.date(2020, 10, 1)])
        self.assertEqual((start, end), ("2020-10-01 15:00", "2020-10-01 22:00"))

    def test_the_other_forms_stand(self):
        days, start, end = self.m.span("8/14/2020 15:00 through 8/16/2020 22:00", dt.date(2020, 8, 13))
        self.assertEqual(days, [dt.date(2020, 8, 14), dt.date(2020, 8, 15), dt.date(2020, 8, 16)])
        self.assertEqual(self.m.span("16:00 - 21:00", dt.date(2022, 9, 6))[0], [dt.date(2022, 9, 6)])
        self.assertEqual(self.m.span("", dt.date(2022, 9, 6)), ([dt.date(2022, 9, 6)], "", ""))


if __name__ == "__main__":
    unittest.main()

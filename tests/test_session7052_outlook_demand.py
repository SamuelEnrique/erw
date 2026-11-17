"""Session 7052 (chain 370, the data machine): done-line request 201.

caiso_outlook_demand: CAISO Today's Outlook demand, 5-minute, on the 39 Flex Alert days of 2018 to 2024. The parser is
tested on files written here by hand (test data, never a reported figure); no request is made.
"""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import caiso_outlook_demand as cod  # noqa: E402


def day_file(n=288, end_row=True, flag_at=()):
    lines = ["Time,Day ahead forecast,Hour ahead forecast,Current demand,Demand response"]
    for k in range(n):
        h, m = divmod(5 * k, 60)
        lines.append(f"{h:02d}:{m:02d},{30000 + k},{30100 + k},{30200 + k},{'1' if k in flag_at else ''}")
    if end_row:
        lines.append("00:00,1,2,3,")
    return "\n".join(lines) + "\n"


class TheParser(unittest.TestCase):
    def test_a_whole_day_drops_the_next_days_first_row(self):
        out, why = cod.parse(dt.date(2022, 9, 6), day_file(flag_at=(200, 201)), "u", "2026-11-17T00:00:00Z")
        self.assertIsNone(why)
        self.assertEqual(int((out["variable"] == "demand_mw").sum()), 288)
        self.assertEqual(out[out["variable"] == "demand_mw"]["ts_utc"].min(), "2022-09-06T07:00:00Z")
        self.assertEqual(out[out["variable"] == "demand_mw"]["ts_utc"].max(), "2022-09-07T06:55:00Z")
        self.assertEqual(int((out["variable"] == "demand_response_marked").sum()), 2)
        self.assertNotIn(3.0, set(out["value"]))   # the trailing 00:00 row is not read

    def test_a_short_day_is_not_written(self):
        out, why = cod.parse(dt.date(2022, 9, 6), day_file(n=287), "u", "t")
        self.assertIsNone(out)
        self.assertIn("287 of 288", why)

    def test_the_days_are_the_methods_39(self):
        self.assertEqual(len(cod.ALERT_DAYS), 39)
        self.assertIn("2021-07-12", cod.ALERT_DAYS)
        self.assertEqual((cod.ALERT_DAYS[0], cod.ALERT_DAYS[-1]), ("2018-07-24", "2024-07-24"))


if __name__ == "__main__":
    unittest.main()

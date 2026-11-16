"""Session 7016 (chain 301, done-line request 27): CAISO's Today's Outlook history on the spring clock change prints 288
rows, the hour that does not exist (02:00 to 02:55) as twelve rows with every value blank. Both connectors that read it
refused the day (NonExistentTimeError), so 8 March 2026 was missing from caiso_fuel_supply and caiso_battery_storage,
and the curtailment shares of March 2026 stood on 30 of 31 days. No request, no model call."""
import datetime as dt
import os
import sys
import types
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import caiso_fuel_supply as fs  # noqa: E402
import caiso_outlook as co  # noqa: E402
import iso_prices as ip  # noqa: E402


def spring_file(cols, value_in_missing_hour=False):
    lines = ["Time," + ",".join(cols)]
    for m in range(0, 24 * 60, 5):
        hh, mm = divmod(m, 60)
        blank = hh == 2 and not (value_in_missing_hour and mm == 0)
        lines.append(f"{hh:02d}:{mm:02d}," + ",".join("" if blank else "100" for _ in cols))
    return "\n".join(lines) + "\n"


class Spring(unittest.TestCase):
    day = dt.date(2026, 3, 8)

    def run_day(self, mod, cols, **kw):
        text = spring_file(cols, **kw)
        with mock.patch.object(ip, "with_retries", lambda name, call, log: types.SimpleNamespace(text=text)):
            return mod.day_rows(self.day, mock.Mock())

    def test_the_fuel_supply_day_is_read_as_23_hours(self):
        out, why = self.run_day(fs, list(fs.SOURCES))
        self.assertIsNone(why)
        self.assertEqual(out["ts_utc"].nunique(), 23)
        self.assertEqual(out["ts_utc"].min(), "2026-03-08T08:00:00Z")    # 00:00 Pacific standard time
        self.assertEqual(out["ts_utc"].max(), "2026-03-09T06:00:00Z")    # 23:00 Pacific daylight time
        self.assertTrue((out["value"] == 100).all())

    def test_the_battery_day_is_read_as_276_intervals(self):
        out, why = self.run_day(co, list(co.COLS))
        self.assertIsNone(why)
        self.assertEqual(out["ts_utc"].nunique(), 276)

    def test_a_value_in_the_hour_that_does_not_exist_still_stops_the_day(self):
        with self.assertRaises(Exception):
            self.run_day(fs, list(fs.SOURCES), value_in_missing_hour=True)


if __name__ == "__main__":
    unittest.main()

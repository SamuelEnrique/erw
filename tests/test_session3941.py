"""Session 3941 (chain 267): the total interchange of November and December 2025.

The checkpoints of eia930_daily_total_interchange froze a short answer of EIA's API on 13 October 2026 (334 and 735 rows
against about 2,200 a month) and were never asked again. Held here on made-up numbers (no EIA figure is a fixture): a
short past month is found against the median of the others, the six-month file's hours are summed over the Eastern day
only when every hour is there (25 on 2 November 2025), and a fill never repeats a day the API answered. No network.
"""
import os
import sys
import tempfile
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import eia930_daily_total_interchange as ti  # noqa: E402


def hours(ba, day, n, value=10.0, skip=()):
    """The six-month file's rows for an Eastern day: n hours from local midnight, as UTC end-of-hour strings."""
    start = pd.Timestamp(day).tz_localize("America/New_York").tz_convert("UTC")
    out = []
    for i in range(n):
        if i in skip:
            continue
        end = start + pd.Timedelta(hours=i + 1)
        out.append({"Balancing Authority": ba, "UTC Time at End of Hour": end.strftime("%m/%d/%Y %I:%M:%S %p"), ti.SIX_COL: f"{value:,.0f}"})
    return out


class TheShortMonths(unittest.TestCase):
    def test_the_frozen_months_are_found(self):
        counts = {f"2025-{m:02d}": 2200 for m in range(1, 11)}
        counts.update({"2025-11": 334, "2025-12": 735, "2026-01": 2250, "2026-10": 2230})
        self.assertEqual(ti.short_months(counts, "2026-11"), ["2025-11", "2025-12"])

    def test_february_is_not_short_for_its_days(self):
        counts = {"2026-01": 2232, "2026-02": 2016, "2026-03": 2232}
        self.assertEqual(ti.short_months(counts, "2026-11"), [])

    def test_the_current_month_is_never_judged(self):
        self.assertEqual(ti.short_months({"2026-10": 2200, "2026-11": 10}, "2026-11"), [])

    def test_the_file_of_a_month(self):
        self.assertEqual(ti.six_file_name("2025-11"), "EIA930_BALANCE_2025_Jul_Dec.csv")
        self.assertEqual(ti.six_file_name("2026-03"), "EIA930_BALANCE_2026_Jan_Jun.csv")


class TheEasternDays(unittest.TestCase):
    def test_a_whole_day_is_summed(self):
        d = ti.eastern_days(pd.DataFrame(hours("XX", "2025-11-05", 24, 10)))
        self.assertEqual(d, {("XX", "2025-11-05"): 240.0})

    def test_the_fall_back_day_has_25_hours(self):
        d = ti.eastern_days(pd.DataFrame(hours("XX", "2025-11-02", 25, 4)))
        self.assertEqual(d, {("XX", "2025-11-02"): 100.0})

    def test_a_day_missing_an_hour_is_left_out(self):
        self.assertEqual(ti.eastern_days(pd.DataFrame(hours("XX", "2025-11-05", 24, 10, skip=(7,)))), {})

    def test_a_blank_hour_is_left_out(self):
        rows = hours("XX", "2025-11-05", 24, 10)
        rows[3][ti.SIX_COL] = ""
        self.assertEqual(ti.eastern_days(pd.DataFrame(rows)), {})


class TheFill(unittest.TestCase):
    def test_only_the_days_the_api_lacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            saved = ti.ip.RAW_DIR
            ti.ip.RAW_DIR = tmp
            try:
                d = os.path.join(tmp, ti.NAME, "sixmonth")
                os.makedirs(d)
                rows = hours("AA", "2025-11-05", 24, 10) + hours("BB", "2025-11-05", 24, -5) + hours("AA", "2025-10-31", 24, 1)
                pd.DataFrame(rows).to_csv(os.path.join(d, "EIA930_BALANCE_2025_Jul_Dec.csv"), index=False)
                out = ti.six_fill({"2025-11"}, {("AA", "2025-11-05")}, lambda s: None)
            finally:
                ti.ip.RAW_DIR = saved
        self.assertEqual(out[["respondent", "period", "value"]].values.tolist(), [["BB", "2025-11-05", "-120"]])
        self.assertEqual(set(out["_source"]), {ti.SIX_SOURCE})
        self.assertTrue(out["_url"].iloc[0].endswith("EIA930_BALANCE_2025_Jul_Dec.csv"))


if __name__ == "__main__":
    unittest.main()

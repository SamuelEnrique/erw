"""Session 7022 (chain 301, the data machine, 16 November 2026): done-line request 37.

eia930_demand_growth writes the change in MW since 2019 for a month and an hour (growth_mw_) but, before this session,
not for the three whole-year windows the explorer's column "Change, MW" draws. Now: the whole year's average and its
peak on the last whole year's row, the year so far on the newest year's, each the difference of the two means as the
table rounds them, to one decimal. A built series of three years checks the arithmetic and where each row goes; the
figure the request names (ERCOT 2025: 55,717.2 less 43,797.6 = 11,919.6) was read from EIA's workbook of 16 November
in the session's trial.
"""

import importlib.util
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    path = os.path.join(ROOT, "warehouse", "derived", "demand_growth.py")
    spec = importlib.util.spec_from_file_location("demand_growth_7022", path)
    m = importlib.util.module_from_spec(spec)
    saved = sys.argv
    try:
        sys.argv = ["demand_growth.py"]
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    return m


def series(tz):
    """Every hour of 2019 at 100.25 MW, of 2020 at 110.5 with one hour at 150, and January to March 2021 at 120.75."""
    parts = []
    for start, end, mw in (("2019-01-01", "2020-01-01", 100.25), ("2020-01-01", "2021-01-01", 110.5), ("2021-01-01", "2021-04-01", 120.75)):
        idx = pd.date_range(pd.Timestamp(start, tz=tz), pd.Timestamp(end, tz=tz), freq="h", inclusive="left").tz_convert("UTC")
        parts.append(pd.Series(mw, index=idx))
    s = pd.concat(parts)
    s[pd.Timestamp("2020-07-01 17:00", tz=tz).tz_convert("UTC")] = 150.0
    return s


class TheWholeYearChangeInMW(unittest.TestCase):
    def setUp(self):
        self.dg = builder()
        self.out, self.at, self.last = self.dg.summarize(series("US/Central"), "US/Central", None, True)

    def test_the_last_whole_years_row_holds_the_average_and_the_peak(self):
        r, base = self.out[2020], self.out[2019]
        self.assertEqual(r["avg_demand_growth_since_2019_mw"], round(r["avg_demand_mw"] - base["avg_demand_mw"], 1))
        self.assertEqual(r["peak_demand_growth_since_2019_mw"], round(150.0 - 100.2, 1))   # the table's rounded peaks
        self.assertNotIn("avg_demand_growth_since_2019_mw", base)

    def test_the_newest_years_row_holds_the_year_so_far(self):
        self.assertEqual(self.last, "2021-03")
        r, base = self.out[2021], self.out[2019]
        self.assertEqual(r["ytd_avg_demand_growth_since_2019_mw"], round(r["ytd_avg_demand_mw"] - base["ytd_avg_demand_mw"], 1))
        self.assertAlmostEqual(r["ytd_avg_demand_growth_since_2019_mw"], 20.6, places=6)   # 120.8 less 100.2, the rounded means
        self.assertNotIn("avg_demand_growth_since_2019_mw", r)    # the partial year has no whole-year average
        self.assertNotIn("ytd_avg_demand_growth_since_2019_mw", self.out[2020])   # three rows an area, no more

    def test_the_unit_is_mw(self):
        for v in ("avg_demand_growth_since_2019_mw", "peak_demand_growth_since_2019_mw", "ytd_avg_demand_growth_since_2019_mw"):
            self.assertEqual(self.dg.unit_of(v), "MW")


if __name__ == "__main__":
    unittest.main()

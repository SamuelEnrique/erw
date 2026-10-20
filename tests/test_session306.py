"""Session 306: the battery's inputs, battery_sourced_ranges and grid_stress_days.

Energy Research Warehouse (ERW). The rows of the synthetic tests are fixtures, not data values; the other tests read
the tables and the kept workbook where this machine holds them, and skip where it does not.

    python -m unittest tests.test_session306 -v
"""

import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import sourced_ranges as sr  # noqa: E402
import stress_days as sd  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")


class TheRule(unittest.TestCase):
    def test_the_threshold_leaves_the_day_out_and_needs_nine_tenths_of_a_year(self):
        days = pd.date_range("2024-01-01", periods=400).strftime("%Y-%m-%d")
        v = pd.Series(np.arange(400, dtype=float) % 50, index=days)
        v.iloc[399] = 1000.0
        s, p, n = sd.judge(v)
        self.assertTrue(np.isnan(p.iloc[328]), "328 days before: not judged by price")
        self.assertFalse(np.isnan(p.iloc[329]))
        self.assertEqual(int(n.iloc[399]), 365)
        self.assertLess(p.iloc[399], 1000.0, "the day itself is not in its own threshold")
        self.assertTrue(s.iloc[399] > p.iloc[399])


class TheWorkbook(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(sr.RAW, sr.FILE)
        if not os.path.exists(self.path):
            self.skipTest("the ATB workbook is not on this machine")

    def test_the_cases_are_read_where_the_workbook_puts_them(self):
        got = {(v, d, c): (x, row) for v, u, d, c, x, row in sr.read(self.path)}
        self.assertAlmostEqual(got[("capex", 4, "Moderate")][0], 1396.7251280988867, places=6)
        self.assertEqual(got[("capex", 4, "Moderate")][1], 74)
        self.assertLess(got[("overnight_capital_cost", 8, "Advanced")][0], got[("overnight_capital_cost", 8, "Conservative")][0])
        self.assertEqual(got[("round_trip_efficiency", 4, "Advanced")][0], 0.85)
        self.assertEqual(got[("technical_life", None, "Moderate")][0], 15.0)
        self.assertNotIn("debt_share", {k[0] for k in got}, "the workbook states no debt share for the battery")


class TheEvents(unittest.TestCase):
    def test_days_at_most_three_apart_are_one_event_named_for_its_first_day(self):
        got = sd.events("nyiso", ["2025-01-01", "2025-01-04", "2025-01-09"])
        self.assertEqual(got, {"2025-01-01": "nyiso_stress_20250101", "2025-01-04": "nyiso_stress_20250101",
                               "2025-01-09": "nyiso_stress_20250109"})
        self.assertEqual(set(sd.events("ercot", ["2021-02-15", "2021-02-17"]).values()), {"uri_2021"})


class TheUnits(unittest.TestCase):
    def test_the_atb_units_are_in_the_vocabulary(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
        import erw_validate as v
        self.assertTrue({"USD/kW", "USD/kWh", "USD/kW-year"} <= v.UNITS)
        self.assertTrue({u for _, u in sr.METRICS.values()} <= v.UNITS)


class TheTables(unittest.TestCase):
    def read(self, name):
        path = os.path.join(OUT, name + ".csv")
        if not os.path.exists(path):
            self.skipTest(f"{name} is not on this machine")
        return pd.read_csv(path, comment="#", dtype=str, keep_default_na=False)

    def test_ercots_stress_days_hold_uri_and_the_first_day_of_elliott(self):
        t = self.read("grid_stress_days")
        days = set(t.loc[t["entity"] == "ercot:HB_HUBAVG", "ts_utc"].str[:10])
        for d in ("2021-02-15", "2021-02-16", "2021-02-17", "2021-02-18", "2021-02-19", "2022-12-23"):
            self.assertIn(d, days)
        # session 322: the price test misses 24 December 2022; ERCOT's OCN for 22 to 26 December (ercot_grid_notices) makes it one
        self.assertIn("2022-12-24", days, "24 December 2022 is a stress day by ERCOT's notice (docs/methods/stress_days.md)")
        self.assertFalse(t["entity"].str.startswith("pjm:").any())
        r = t[t["entity"] == "ercot:HB_HUBAVG"]
        e = pd.Series(r["x_event"].values, index=r["ts_utc"].str[:10].values)
        self.assertEqual(e["2021-02-16"], "uri_2021", "session 297: a named event keeps its name")
        self.assertEqual(e["2022-12-23"], "elliott_2022")

    def test_every_sourced_row_names_its_place(self):
        t = self.read("battery_sourced_ranges")
        self.assertTrue((t["x_page"].str.startswith("sheet ")).all())
        self.assertEqual(set(t["x_case"]), {"low", "mid", "high"})


if __name__ == "__main__":
    unittest.main()

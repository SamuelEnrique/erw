"""Session 75 tests: the shoulder hours (warehouse/derived/shoulder_hours.py).

Energy Research Warehouse (ERW). Net load is demand less solar and wind; the shoulder's start and end follow the stated
rule on a day worked by hand; the hours the fleet covers never exceed its MWh over its MW; and, on the built table,
the identity and the bound hold in every month.
"""

import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import shoulder_hours as sh  # noqa: E402

TABLE = os.path.join(ROOT, "warehouse", "output", "shoulder_hours_monthly.csv")


def hand_day():
    """A day worked by hand. Solar peaks at hour 12 (1,000) and falls below half its peak (500) first at hour 16 (400).
    Demand 1,000 flat, no wind: net load = 1,000 less solar. Its mean is 1,000 less mean solar."""
    solar = np.zeros(24)
    solar[8:17] = [200, 400, 600, 800, 1000, 800, 600, 600, 400]  # hours 8 to 16
    demand = np.full(24, 1000.0)
    demand[17:21] = 1300.0          # an evening peak, hours 17 to 20
    return pd.DataFrame({"demand": demand, "solar": solar, "wind": 0.0, "net_load": demand - solar})


class TestDay(unittest.TestCase):
    def test_hand_worked_day(self):
        d = hand_day()
        m = sh.day_metrics(d)
        nl = d["net_load"].to_numpy()
        mean = nl.mean()  # (24 x 1000 + 4 x 300 - 5,400) / 24 = 825
        self.assertAlmostEqual(mean, 825.0)
        self.assertEqual(m["shoulder_start_hour"], 16)        # solar 400 < 500, the first hour after the peak below half
        # net load: hour 16 is 600 (below 825), hours 17 to 20 are 1,300 (above), hour 21 is 1,000 (above), and it never
        # falls back to 825 before midnight: the shoulder runs to midnight and is flagged
        self.assertEqual(m["shoulder_end_hour"], 24)
        self.assertEqual(m["shoulder_runs_to_midnight"], 1)
        self.assertEqual(m["shoulder_hours"], 8)
        self.assertAlmostEqual(m["shoulder_mwh_above_mean"], 4 * (1300 - 825) + 3 * (1000 - 825))
        # midday surplus: around the low (hour 12, 0), the run of hours below the mean: hours 8 (800) to 16 (600), all < 825
        self.assertEqual(m["midday_low_hour"], 12)
        self.assertEqual(m["midday_surplus_hours"], 9)
        self.assertAlmostEqual(m["midday_surplus_mwh"], sum(825 - nl[h] for h in range(8, 17)))

    def test_shoulder_ends_when_net_load_falls_back(self):
        d = hand_day()
        d.loc[21:23, "demand"] = 700.0
        d["net_load"] = d["demand"] - d["solar"]
        m = sh.day_metrics(d)
        mean = d["net_load"].mean()
        self.assertTrue(d["net_load"][21] <= mean)
        self.assertEqual((m["shoulder_start_hour"], m["shoulder_end_hour"], m["shoulder_runs_to_midnight"]), (16, 21, 0))

    def test_no_rise_no_shoulder(self):
        d = hand_day()
        d["demand"] = 1000.0
        d.loc[0:7, "demand"] = 2000.0   # the night is the day's high: after sunset net load never passes its mean
        d["net_load"] = d["demand"] - d["solar"]
        self.assertEqual(sh.day_metrics(d)["shoulder_hours"], 0)

    def test_fleet_hours_never_exceed_mwh_over_mw(self):
        for hours, mwh in [(8, 4000.0), (2, 4000.0), (0, 0.0), (5, 12000.0)]:
            f = sh.fleet_metrics(hours, mwh, 1000.0, 2500.0)
            self.assertLessEqual(f["shoulder_hours_covered"], f["fleet_mwh"] / f["fleet_mw"] + 1e-9)
            self.assertLessEqual(f["shoulder_hours_covered"], hours)
            self.assertAlmostEqual(f["shoulder_hours_needed"], mwh / 1000.0)


@unittest.skipUnless(os.path.exists(TABLE), "shoulder_hours_monthly.csv is not on this machine")
class TestTable(unittest.TestCase):
    def setUp(self):
        d = pd.read_csv(TABLE, comment="#")
        self.w = d.pivot_table(index=["entity", "ts_utc"], columns="variable", values="value")

    def test_net_load_is_demand_less_solar_and_wind(self):
        for h in range(24):
            x = self.w[[f"avg_demand_mw_h{h:02d}", f"avg_solar_mw_h{h:02d}", f"avg_wind_mw_h{h:02d}", f"avg_net_load_mw_h{h:02d}"]].dropna()
            diff = x.iloc[:, 0] - x.iloc[:, 1] - x.iloc[:, 2] - x.iloc[:, 3]
            self.assertLess(diff.abs().max(), 0.01, f"hour {h}")

    def test_covered_never_exceeds_the_fleets_duration(self):
        x = self.w[["shoulder_hours_covered", "fleet_mwh", "fleet_mw", "shoulder_hours"]].dropna()
        self.assertTrue(len(x) > 50)
        self.assertTrue((x["shoulder_hours_covered"] <= x["fleet_mwh"] / x["fleet_mw"] + 1e-3).all())
        self.assertTrue((x["shoulder_hours_covered"] <= x["shoulder_hours"] + 1e-9).all())

    def test_california_stops_before_the_break(self):
        c = self.w.loc["iso:caiso"]
        self.assertLessEqual(max(c.index), "2025-11-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()

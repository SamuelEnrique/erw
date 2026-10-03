"""Session 80: the shoulder on the worst days (warehouse/derived/shoulder_hours.py).

Energy Research Warehouse (ERW). The days here are made-up days, used only to test the arithmetic of the second
shoulder measure and of the ranking of days. The last class reads the trial table where a machine holds it
(runs/session80/build), and skips where it does not. No request leaves the machine.

    python -m unittest tests.test_session80 -v
"""

import os
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", "warehouse/connectors", "warehouse/derived"):
    sys.path.insert(0, os.path.join(ROOT, p))

import shoulder_hours as sh  # noqa: E402

TRIAL = os.path.join(ROOT, "runs", "session80", "build", "shoulder_hours_monthly.csv")


def day(evening=(1600, 1900, 2000, 1700, 1300, 1100), demand=1000.0):
    """A day by hand: flat demand of 1,000 MW but for six evening hours from 18:00; solar 800 MW from 09:00 to 16:00
    (its highest hour is 09:00, the first of the eight); no wind."""
    d = pd.DataFrame({"demand": [demand] * 24, "solar": [0.0] * 24, "wind": [0.0] * 24})
    d.loc[9:16, "solar"] = 800.0
    for i, v in enumerate(evening):
        d.loc[18 + i, "demand"] = float(v)
    d["net_load"] = d["demand"] - d["solar"] - d["wind"]
    return d


class SecondMeasure(unittest.TestCase):
    def test_a_day_by_hand(self):
        d = day()
        m = sh.day_metrics(d)
        nl = d["net_load"].to_numpy()
        mean = nl.mean()
        # net load: 1,000 at night, 200 from 09:00 to 16:00, then 1,000, and the evening 1,600 1,900 2,000 1,700 1,300 1,100
        self.assertAlmostEqual(mean, (10 * 1000 + 8 * 200 + 1600 + 1900 + 2000 + 1700 + 1300 + 1100) / 24)
        self.assertEqual(m["shoulder_start_hour"], 17)             # the first hour after solar's highest in which solar is below half
        self.assertEqual((m["evening_peak_hour"], m["evening_peak_mw"]), (20, 2000.0))
        level = (mean + 2000) / 2
        self.assertAlmostEqual(m["shoulder2_level_mw"], level)
        above = [h for h in range(24) if nl[h] > level]
        self.assertEqual(above, [18, 19, 20, 21])                  # 1,600 1,900 2,000 1,700 are above the midpoint; 1,300 is not
        self.assertEqual((m["shoulder2_start_hour"], m["shoulder2_end_hour"], m["shoulder2_hours"]), (18, 22, 4))
        self.assertAlmostEqual(m["shoulder2_mwh_above_midpoint"], sum(nl[h] - level for h in above))
        self.assertEqual(m["shoulder2_runs_to_midnight"], 0)
        # the first measure runs to midnight here (1,100 and 1,000 are still above the mean); the second ends inside the evening
        self.assertEqual((m["shoulder_end_hour"], m["shoulder_runs_to_midnight"]), (24, 1))
        self.assertLess(m["shoulder2_hours"], m["shoulder_hours"])
        self.assertLess(m["shoulder2_mwh_above_midpoint"], m["shoulder_mwh_above_mean"])

    def test_what_always_holds_between_the_two_measures(self):
        """On any day: the second shoulder starts no earlier than the first, ends by midnight, sits at or above the mean,
        and holds no more energy than the evening holds above the mean. It is not always the shorter one: the first
        measure stops at the first dip back to the mean, and a peak after such a dip belongs to the second alone."""
        rng = np.random.default_rng(80)
        longer = 0
        for _ in range(200):
            d = day(evening=rng.integers(900, 2600, 6))
            d["wind"] = rng.integers(0, 300, 24).astype(float)
            d["net_load"] = d["demand"] - d["solar"] - d["wind"]
            m = sh.day_metrics(d)
            if np.isnan(m.get("shoulder_hours", np.nan)):
                continue
            nl, mean, start = d["net_load"].to_numpy(), m["net_load_mean_mw"], int(m["shoulder_start_hour"])
            self.assertGreaterEqual(m["shoulder2_start_hour"], start)
            self.assertLessEqual(m["shoulder2_end_hour"], 24)
            if m["shoulder2_hours"]:
                self.assertGreaterEqual(m["shoulder2_level_mw"], mean)
                self.assertLessEqual(m["shoulder2_mwh_above_midpoint"], sum(max(0.0, v - mean) for v in nl[start:]) + 1e-9)
                self.assertTrue(m["shoulder2_start_hour"] <= m["evening_peak_hour"] < m["shoulder2_end_hour"])
            longer += m["shoulder2_hours"] > m["shoulder_hours"]
        self.assertGreater(longer, 0)   # the case exists on made-up days; the trial table's months never show it

    def test_an_evening_that_never_passes_its_mean_has_no_second_shoulder(self):
        d = day(evening=(1000,) * 6)
        d.loc[0:7, "demand"] = 2000.0   # the night is the day's high
        d["net_load"] = d["demand"] - d["solar"]
        m = sh.day_metrics(d)
        self.assertEqual((m["shoulder_hours"], m["shoulder2_hours"], m["shoulder2_mwh_above_midpoint"]), (0, 0, 0.0))

    def test_still_above_the_midpoint_at_midnight_is_flagged(self):
        m = sh.day_metrics(day(evening=(1200, 1500, 1800, 2000, 2000, 2000)))
        self.assertEqual((m["shoulder2_end_hour"], m["shoulder2_runs_to_midnight"]), (24, 1))

    def test_the_fleet_against_the_second_measure(self):
        f = sh.fleet_metrics(6, 12000.0, 1000.0, 2500.0, 4, 3000.0)
        self.assertAlmostEqual(f["shoulder2_hours_needed"], 3.0)
        self.assertAlmostEqual(f["shoulder2_hours_covered"], 2.5)   # the fleet's own duration, 2,500 MWh over 1,000 MW
        self.assertAlmostEqual(f["shoulder_hours_needed"], 12.0)
        self.assertNotIn("shoulder2_hours_needed", sh.fleet_metrics(6, 12000.0, 1000.0, 2500.0))


class Units(unittest.TestCase):
    def test_one_rule(self):
        want = {"shoulder_mwh_above_mean": "MWh", "shoulder2_mwh_above_midpoint": "MWh", "curtailed_mwh_per_day": "MWh", "fleet_mwh": "MWh",
                "avg_net_load_mw_h05": "MW", "fleet_mw": "MW", "evening_peak_mw": "MW", "day_battery_peak_mw": "MW",
                "shoulder_hours": "hour", "shoulder2_hours_needed": "hour", "evening_peak_hour": "hour", "day_battery_hours": "hour",
                "year_mean_shoulder_runs_to_midnight": "ratio", "year_mean_shoulder2_runs_to_midnight": "ratio",
                "shoulder_runs_to_midnight": "count", "worst_rank": "count", "days_held": "count", "year_days_ranked": "count",
                "year_worst10_mean_shoulder_mwh_above_mean": "MWh", "year_worst10_mean_battery_hours": "hour"}
        for k, u in want.items():
            self.assertEqual(sh.unit_of(k), u, k)


def hours_frame(days, peak_of):
    """Hours of made-up days for worst_days: each day is day(), its evening scaled by peak_of(day)."""
    out = []
    for d in days:
        x = day(evening=tuple(v * peak_of(d) for v in (1600, 1900, 2000, 1700, 1300, 1100)))
        x["day"], x["hour"], x["m"], x["bat"] = d, range(24), d[:7], 100.0
        out.append(x)
    return pd.concat(out, ignore_index=True)


class WorstDays(unittest.TestCase):
    def setUp(self):
        self.days = [f"2025-07-{i:02d}" for i in range(1, 16)] + [f"2026-01-{i:02d}" for i in range(1, 4)]
        self.h = hours_frame(self.days, lambda d: 1 + int(d[-2:]) / 100)   # a later day of the month has a bigger evening
        self.fl = pd.DataFrame({"battery_operating_mw": [1000.0], "battery_operating_mwh": [3000.0]}, index=["2025-07"])
        self.log = lambda m: None

    def test_ten_days_a_year_ranked_by_shoulder_energy(self):
        days, years = sh.worst_days(self.h, self.fl, "ercot", self.log)
        d25 = {d: v for d, v in days.items() if d.startswith("2025")}
        self.assertEqual(len(d25), 10)
        self.assertEqual(sorted(d25, key=lambda d: d25[d]["worst_rank"]), [f"2025-07-{i:02d}" for i in range(15, 5, -1)])
        e = [d25[d]["day_shoulder_mwh_above_mean"] for d in sorted(d25, key=lambda d: d25[d]["worst_rank"])]
        self.assertEqual(e, sorted(e, reverse=True))
        self.assertEqual((years["2025"]["year_days_ranked"], years["2025"]["year_worst10_days"]), (15, 10))
        self.assertEqual(len([d for d in days if d.startswith("2026")]), 3)   # a year with fewer than ten days ranks what it has

    def test_hours_needed_is_the_days_energy_over_the_months_fleet_and_is_never_guessed(self):
        days, years = sh.worst_days(self.h, self.fl, "ercot", self.log)
        v = days["2025-07-15"]
        self.assertAlmostEqual(v["day_shoulder_hours_needed"], v["day_shoulder_mwh_above_mean"] / 1000.0)
        self.assertAlmostEqual(v["day_shoulder2_hours_needed"], v["day_shoulder2_mwh_above_midpoint"] / 1000.0)
        self.assertAlmostEqual(years["2025"]["year_worst10_mean_shoulder_hours_needed"],
                               np.mean([days[f"2025-07-{i:02d}"]["day_shoulder_hours_needed"] for i in range(6, 16)]))
        # January 2026 has no fleet row: its days carry no hours needed and the year no mean of them
        self.assertNotIn("day_shoulder_hours_needed", days["2026-01-03"])
        self.assertNotIn("year_worst10_mean_shoulder_hours_needed", years["2026"])

    def test_what_the_batteries_did_only_where_every_hour_holds_it(self):
        days, years = sh.worst_days(self.h, self.fl, "ercot", self.log)
        v = days["2025-07-15"]
        self.assertAlmostEqual(v["day_battery_discharge_mwh"], 100.0 * v["day_shoulder_hours"])   # 100 MW in each shoulder hour
        self.assertAlmostEqual(v["day_battery_hours"], v["day_battery_discharge_mwh"] / 1000.0)
        h = self.h.copy()
        h.loc[(h["day"] == "2025-07-15") & (h["hour"] == 3), "bat"] = np.nan
        days, years = sh.worst_days(h, self.fl, "ercot", self.log)
        self.assertNotIn("day_battery_discharge_mwh", days["2025-07-15"])
        self.assertEqual(years["2025"]["year_worst10_days_with_battery"], 9)
        self.assertNotIn("year_worst10_mean_battery_hours", years["2025"])

    def test_a_clock_change_day_or_a_short_day_is_not_ranked(self):
        h = self.h[~((self.h["day"] == "2025-07-15") & (self.h["hour"] == 2))]
        days, _ = sh.worst_days(h, self.fl, "ercot", self.log)
        self.assertNotIn("2025-07-15", days)
        self.assertIn("2025-07-05", days)   # the next day down takes the tenth place


@unittest.skipUnless(os.path.exists(TRIAL), "the trial table (runs/session80/build) is not on this machine")
class Trial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = pd.read_csv(TRIAL, comment="#", dtype=str, keep_default_na=False)
        cls.t["v"] = cls.t["value"].astype(float)

    def test_californias_two_sources_are_two_entities_and_never_overlap_in_one(self):
        t = self.t
        eia = t[(t["entity"] == "iso:caiso") & (t["freq"] == "P1M")]
        own = t[(t["entity"] == "iso:caiso_own") & (t["freq"] == "P1M")]
        self.assertLessEqual(eia["ts_utc"].max(), "2025-11-01T00:00:00Z")
        self.assertGreaterEqual(own["ts_utc"].min(), "2025-06-01T00:00:00Z")
        self.assertEqual(set(t["entity"]), {"iso:ercot", "iso:caiso", "iso:caiso_own"})
        with open(TRIAL, encoding="utf-8") as f:
            head = "".join(ln for ln in f if ln.startswith("#"))
        self.assertIn("iso:caiso_own is CAISO's own supply by fuel", head)
        self.assertIn("never mixed", head)

    def test_the_earlier_rows_are_kept_as_they_stand(self):
        held = os.path.join(ROOT, "warehouse", "output", "shoulder_hours_monthly.csv")
        if not os.path.exists(held):
            self.skipTest("the held table is not on this machine")
        a = pd.read_csv(held, comment="#", dtype=str, keep_default_na=False)
        k = ["entity", "variable", "ts_utc"]
        j = a.merge(self.t, on=k, suffixes=("_held", "_trial"))
        self.assertEqual(len(j), len(a))
        self.assertTrue((j["value_held"].astype(float) == j["value_trial"].astype(float)).all())

    def test_the_second_measure_in_every_month_and_inside_the_first(self):
        w = self.t[self.t["freq"] == "P1M"].pivot(index=["entity", "ts_utc"], columns="variable", values="v")
        x = w[["shoulder_hours", "shoulder2_hours", "shoulder_mwh_above_mean", "shoulder2_mwh_above_midpoint"]]
        self.assertEqual(int(x["shoulder2_hours"].isna().sum()), 0)
        self.assertTrue((x["shoulder2_hours"] <= x["shoulder_hours"]).all())
        self.assertTrue((x["shoulder2_mwh_above_midpoint"] <= x["shoulder_mwh_above_mean"] + 1e-6).all())
        f = w[["shoulder2_hours_needed", "shoulder2_mwh_above_midpoint", "fleet_mw"]].dropna()
        self.assertTrue(np.allclose(f["shoulder2_hours_needed"], f["shoulder2_mwh_above_midpoint"] / f["fleet_mw"], atol=1e-3))

    def test_ten_ranked_days_a_year_where_days_are_held(self):
        d = self.t[self.t["variable"] == "worst_rank"]
        self.assertEqual(set(d["freq"]), {"P1D"})
        for (e, y), g in d.assign(y=d["ts_utc"].str[:4]).groupby(["entity", "y"]):
            self.assertEqual(sorted(g["v"]), list(range(1, 11)), (e, y))
        w = self.t[self.t["freq"] == "P1D"].pivot(index=["entity", "ts_utc"], columns="variable", values="v")
        n = w[["day_shoulder_hours_needed", "day_shoulder_mwh_above_mean", "day_fleet_mw"]].dropna()
        self.assertTrue(np.allclose(n["day_shoulder_hours_needed"], n["day_shoulder_mwh_above_mean"] / n["day_fleet_mw"], atol=1e-3))
        b = w[["day_battery_hours", "day_battery_discharge_mwh", "day_fleet_mw"]].dropna()
        self.assertTrue(np.allclose(b["day_battery_hours"], b["day_battery_discharge_mwh"] / b["day_fleet_mw"], atol=1e-3))

    def test_no_em_dash_in_the_session_files(self):
        for rel in ("warehouse/derived/shoulder_hours.py", "tests/test_session80.py", "site/lib/shoulder.ts", "site/app/shoulder/page.tsx",
                    "docs/methods/shoulder_hours.md"):
            with open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read(), rel)


if __name__ == "__main__":
    unittest.main()

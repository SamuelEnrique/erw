"""Ruling alternative 1 of /shoulder (session 7703, 17 November 2026, branch wip/alt-shoulder-1; not a default on main).

Energy Research Warehouse (ERW). The question (docs/reviews/ruling-impact-shoulder-2026-11-17.md, line 1): should the midday
low be looked for only while the sun is up (solar at least 5 percent of the average day's highest hour)? On this branch
warehouse/derived/shoulder_hours.py day_metrics does (SUN_UP = 0.05); main takes the whole day's lowest hour.

Pinned on a made-up day, and, where shoulder_hours_monthly is on the machine (warehouse/output, or the folder
ERW_TABLES_DIR names), on each month's average day as the table holds it (avg_net_load_mw_hHH, avg_solar_mw_hHH), with the
builder's own function: ERCOT, the low hour moves in 60 of 93 months and the surplus changes in 22 (February 2019 29,972
to 0 MWh; December 2021 31,661 to 0; January 2023 22,918 to 5,852; February 2023 11,508 to 12,014; November 2023 17,933 to
8,925); California, no month moves. SUN_UP = 0 is main's rule, and gives the table's own figures.

    python -m unittest tests.test_alt_shoulder_1 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import shoulder_hours as sh  # noqa: E402

TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
CSV = os.path.join(TABLES, "shoulder_hours_monthly.csv")


def metrics(net, solar, sun_up):
    keep, sh.SUN_UP = sh.SUN_UP, sun_up
    try:
        return sh.day_metrics(pd.DataFrame({"net_load": net, "solar": solar}))
    finally:
        sh.SUN_UP = keep


class TheRule(unittest.TestCase):
    # a winter day: net load lowest at 03:00, and above its mean through the sunny hours
    net = [30, 28, 27, 25, 26, 30, 36, 40, 42, 41, 40, 40, 41, 42, 44, 48, 52, 55, 54, 50, 45, 40, 35, 32]
    solar = [0, 0, 0, 0, 0, 0, 0, 1, 5, 10, 14, 16, 16, 15, 12, 8, 3, 1, 0, 0, 0, 0, 0, 0]

    def test_main_rule_takes_the_night_low(self):
        m = metrics(self.net, self.solar, 0.0)
        self.assertEqual((m["midday_low_hour"], m["midday_surplus_hours"]), (3, 7))   # 00:00 to 06:00 below the mean of 39.29

    def test_the_other_choice_takes_the_low_while_the_sun_is_up(self):
        m = metrics(self.net, self.solar, 0.05)
        self.assertEqual(m["midday_low_hour"], 7)           # the sun is up from 07:00 to 17:00; 40 at 07:00 is their lowest
        self.assertEqual((m["midday_surplus_hours"], m["midday_surplus_mwh"]), (0, 0.0))   # above the mean of 39.29: no surplus
        self.assertEqual(sh.SUN_UP, 0.05)

    def test_a_day_with_no_sun_keeps_the_whole_day(self):
        m = metrics(self.net, [0] * 24, 0.05)
        self.assertEqual(m["midday_low_hour"], 3)


@unittest.skipUnless(os.path.exists(CSV), "shoulder_hours_monthly is not on this machine")
class OnTheTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        n = 0
        with open(CSV, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                n += 1
        t = pd.read_csv(CSV, skiprows=n, usecols=["entity", "variable", "ts_utc", "value", "freq"])
        t = t[t["freq"] == "P1M"]
        cls.w = {e: g.pivot(index="ts_utc", columns="variable", values="value") for e, g in t.groupby("entity")}

    def moved(self, entity):
        out = []
        for ts, r in self.w[entity].iterrows():
            net = [r.get(f"avg_net_load_mw_h{h:02d}") for h in range(24)]
            sol = [r.get(f"avg_solar_mw_h{h:02d}") for h in range(24)]
            if any(pd.isna(x) for x in net + sol):
                continue
            a, b = metrics(net, sol, 0.0), metrics(net, sol, 0.05)
            self.assertAlmostEqual(a["midday_surplus_mwh"], r["midday_surplus_mwh"], delta=0.01)   # main's rule gives the table's figure
            if a["midday_low_hour"] != b["midday_low_hour"]:
                out.append((ts[:7], round(a["midday_surplus_mwh"]), round(b["midday_surplus_mwh"]), a["midday_surplus_hours"], b["midday_surplus_hours"]))
        return out

    def test_ercot(self):
        m = self.moved("iso:ercot")
        self.assertEqual(len(m), 60)
        changed = {x[0]: (x[1], x[2]) for x in m if x[1] != x[2] or x[3] != x[4]}
        self.assertEqual(len(changed), 22)
        self.assertEqual(changed["2019-02"], (29972, 0))
        self.assertEqual(changed["2021-12"], (31661, 0))
        self.assertEqual(changed["2023-01"], (22918, 5852))
        self.assertEqual(changed["2023-02"], (11508, 12014))
        self.assertEqual(changed["2023-11"], (17933, 8925))
        self.assertEqual(sum(1 for a, b in changed.values() if b == 0), 7)   # the impact file says 8; its own printout lists 7
        self.assertTrue(all(k <= "2023-11" for k in changed))

    def test_california_does_not_move(self):
        self.assertEqual(self.moved("iso:caiso"), [])


if __name__ == "__main__":
    unittest.main()

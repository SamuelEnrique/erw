"""Audit of "What a battery earns", finding 10 (session 9840, docs/reviews/battery-model-audit-2026-11-20.md): the page says
a 4-hour battery "discharges at its rated power for 4 hours, 4 MWh for each MW" (site/app/cost-of-power/battery/
BatteryForm.tsx). In the model (warehouse/derived/battery_stack.py, structure) the duration bounds the energy stored,
and discharge loses its share of the round trip on the way out, so a full 4-hour battery delivers 4 x sqrt(0.86) =
3.71 MWh per MW.

1. Against the code (passes on main): one day of ten free hours then fourteen dear ones, solve_day at 2, 4 and 8 hours;
   the most delivered is D x sqrt(0.86) each time, and on no day of the public dispatch file does the 4-hour battery
   deliver more than 3.7094 MWh per MW.
2. The fix on this branch (fails on main): the hover and the link titles say what the model holds."""
import csv
import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import battery_stack as bs  # noqa: E402

CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")


class WhatFourHoursMeans(unittest.TestCase):
    def test_a_full_battery_delivers_d_times_eta(self):
        eta = math.sqrt(bs.RTE)
        energy = [0.0] * 10 + [1000.0] * 14                       # filling D needs D / eta hours of charging
        spec = ((True, 0.5),)
        for D in (2, 4, 8):
            sol = bs.solve_day(energy, [[0.0] * 24], spec, D)
            self.assertAlmostEqual(sol["delivered"], D * eta, places=6)
            self.assertLess(sol["delivered"], D - 0.1)              # not D hours at rated power
        by_day = {}
        with open(CSV, encoding="utf-8") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        ix = {c: i for i, c in enumerate(rows[0])}
        for r in rows[1:]:
            by_day[r[ix["local_day"]]] = by_day.get(r[ix["local_day"]], 0.0) + float(r[ix["discharge_mw"]])
        self.assertEqual(len(by_day), 1096)
        self.assertLessEqual(max(by_day.values()), 4 * eta + 1e-6)

    def test_the_page_says_what_the_model_holds(self):
        with open(os.path.join(ROOT, "site", "app", "cost-of-power", "battery", "BatteryForm.tsx"), encoding="utf-8") as f:
            t = f.read()
        self.assertNotIn("discharges at its rated power for ${d} hours", t)
        self.assertIn("delivers 3.71 MWh of it from full", t)


if __name__ == "__main__":
    unittest.main()

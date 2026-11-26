"""Audit of Automated Analysis, finding 3 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): the
"tightest hours" are chosen by net load, so solar's output in them falls by construction as solar grows.

docs/methods/grid_stress.md: the tightest hours are "the 100 used hours of the year with the highest net load", net
load "demand less wind less solar". The deep hunt's tight_solar (warehouse/analysis/findings/deep/stress.py, draft 3 of
the sheet: ERCOT 71.1 percent of capacity in 2019, 5.0 in 2025) reads that table. Here a year of hours whose demand
shape and solar shape never change, only solar's capacity: solar's mean output in the 100 hours of highest net load,
as a percent of its capacity, falls steeply as capacity grows. The measure moves with capacity alone. Passes on main;
the fix (hours chosen by demand) is the owner's ruling.

No table, no request, no model call; the environment is read, never set."""
import math
import unittest

import numpy as np


def year():
    h = np.arange(8760)
    hour, day = h % 24, h // 24
    season = 0.5 - 0.5 * np.cos(2 * math.pi * (day - 15) / 365)          # 0 in mid January, 1 in mid July
    demand = 0.62 + 0.18 * season + (0.10 + 0.10 * season) * np.exp(-((hour - 16.0) ** 2) / 18.0)
    sun = np.clip(np.cos(math.pi * (hour - 13.0) / 13.0), 0, None) ** 2 * (0.75 + 0.25 * season)
    sun[(hour < 7) | (hour > 19)] = 0.0
    return demand / demand.max(), sun


def tight_share(capacity, top=100):
    demand, sun = year()
    net = demand - capacity * sun
    idx = np.argsort(-net, kind="stable")[:top]
    return 100.0 * float(sun[idx].mean())


class TightHoursMoveWithSolar(unittest.TestCase):
    def test_share_falls_with_capacity_alone(self):
        caps = (0.05, 0.20, 0.40, 0.60)
        shares = [tight_share(c) for c in caps]
        print("solar's output in the 100 hours of highest net load, percent of capacity, at capacity",
              ", ".join(f"{c:.2f}: {s:.1f}" for c, s in zip(caps, shares)))
        self.assertTrue(all(a > b for a, b in zip(shares, shares[1:])), shares)
        self.assertGreater(shares[0], 30.0)
        self.assertLess(shares[-1], 5.0)

    def test_hours_chosen_by_demand_do_not_move(self):
        demand, sun = year()
        idx = np.argsort(-demand, kind="stable")[:100]
        fixed = 100.0 * float(sun[idx].mean())
        print("solar in the 100 hours of highest demand, percent of capacity, at any capacity:", round(fixed, 1))
        self.assertGreater(fixed, 20.0)


if __name__ == "__main__":
    unittest.main()

"""Session 2955 (chain 157): nuclear_fleet_status, the reactor fleet by reactor and year. The builder's year function
runs on a small reactor written here: outage share, full-outage days, long outages, available energy, the capacity
change, and the first and last years kept whole. No request, no model call."""
import importlib.util
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("nf_2955", os.path.join(ROOT, "warehouse", "derived", "nuclear_fleet_status.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def reactor():
    days = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    cap = [1000.0 if d.year == 2024 else 1050.0 for d in days]
    out = [1000.0 if (d.year == 2024 and d.month == 3) else 0.0 for d in days]       # March 2024 out: 31 days in a row
    return pd.DataFrame({"day": days, "capacity": cap, "outage": out})


class TheYears(unittest.TestCase):
    def test_a_reactors_years(self):
        m = load()
        yrs, first, last = m.reactor_years(reactor())
        y24, y25 = yrs[2024], yrs[2025]
        self.assertEqual((y24["full_outage_days"], y24["long_outages"]), (31, 1))
        self.assertAlmostEqual(y24["outage_share"], 31 / 366, places=6)
        self.assertAlmostEqual(y24["available_mwh"], 1000.0 * 24 * (366 - 31))
        self.assertEqual(y25["capacity_change_mw"], 50.0)
        self.assertEqual((first.year, last.year), (2024, 2025))

    def test_a_short_middle_year_has_days_only(self):
        m = load()
        r = reactor()
        r = pd.concat([r, pd.DataFrame({"day": pd.date_range("2026-01-01", "2026-12-31", freq="D"), "capacity": 1050.0, "outage": 0.0})])
        r = r[~((r["day"].dt.year == 2025) & (r["day"].dt.month > 6))]          # 2025 half held, between two whole years
        yrs, _, _ = m.reactor_years(r)
        self.assertEqual(set(yrs[2025]), {"days_held"})

    def test_runs(self):
        self.assertEqual(load().runs([True, True, False, True, False, False, True]), [2, 1, 1])


if __name__ == "__main__":
    unittest.main()

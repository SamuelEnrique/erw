"""Session 952: Berkeley Lab's wind turbine prices and project costs.

Energy Research Warehouse (ERW). Tests warehouse/connectors/lbnl_wind_costs.py on sheets built here in the data file's
form (figures made up for the test, not LBNL's): the turbine price blocks and the orders, two orders of one date kept
apart, a year with a sample and no cost left out; a heading not as read stopping the run; the sector rule and the holds.
No network.

    python -m unittest tests.test_session952 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import lbnl_wind_costs as W  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def turbine_sheet():
    rows = [[None] * 13 for _ in range(28)]
    rows[23][0], rows[24][0], rows[24][1] = " U.S. turbine orders", "Order Date", "(2025 $/kW)"
    for head, dc, pc, _ in W.TURBINE_BLOCKS:
        rows[23][dc], rows[24][dc] = " " + head, "(2025 $/kW)"
    rows[25][0], rows[25][1] = pd.Timestamp("2001-03-01"), 1300.0
    rows[26][0], rows[26][1] = pd.Timestamp("2001-03-01"), 1350.0
    rows[25][3], rows[25][4] = pd.Timestamp("2016-06-30"), 1100.0
    rows[25][11], rows[25][12] = 2024, 1070.0
    return pd.DataFrame(rows)


def year_sheet():
    rows = [[None] * 3 for _ in range(3)]
    rows[0] = ["Commercial Operation Date", "Capacity-Weighted Average Cost (2025$/kW)", "Annual Cost Sample"]
    rows[1] = [1982, None, 1]
    rows[2] = [2024, 1890.5, 22]
    return pd.DataFrame(rows)


class Sheets(unittest.TestCase):
    def test_turbine(self):
        s, o = W.turbine(turbine_sheet(), BASE)
        t = pd.DataFrame(s).set_index("entity")
        self.assertEqual(t.loc["lbnl_wind_cost:turbine_price:vestas"].ts_utc, "2016-06-30T00:00:00Z")
        self.assertEqual((t.loc["lbnl_wind_cost:turbine_price:lbnl"].ts_utc, t.loc["lbnl_wind_cost:turbine_price:lbnl"].geo),
                         ("2024-01-01T00:00:00Z", "US"))
        o = pd.DataFrame(o)
        self.assertEqual(len(o), 2)
        self.assertEqual(o.event_id.nunique(), 2)

    def test_by_year(self):
        out = W.by_year(year_sheet(), BASE, "CapEx Over Time", list(year_sheet().iloc[0]), "capex", "USD/kW", False)
        self.assertEqual([(r["ts_utc"], r["value"], r["x_sample"]) for r in out], [("2024-01-01T00:00:00Z", 1890.5, 22)])

    def test_stops(self):
        bad = turbine_sheet()
        bad.iloc[23, 3] = "Someone else"
        with self.assertRaises(RuntimeError):
            W.turbine(bad, BASE)
        with self.assertRaises(RuntimeError):
            W.by_year(year_sheet(), BASE, "CapEx Over Time", ["Commercial Operation Date", "Cost", "Sample"], "capex", "USD/kW", False)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            live = f.read().replace("\r\n", "\n")
        for name in (W.COSTS, W.ORDERS):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(name, R.STORAGE_HELD)
            self.assertIn(f"  - {name}\n", live)


if __name__ == "__main__":
    unittest.main()

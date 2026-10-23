"""Session 900: EIA-923 Schedule 2, fuel receipts and costs by plant.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia923_receipts.py on a sheet built here in page 5's form
(figures made up for the test, not EIA's): each delivery an event with a hashed id, the quantity's unit by fuel group, a
row repeated the same kept once and counted, a footnote read past, a fuel group not in the map stopping the run, the
sector rule and the holds. No network.

    python -m unittest tests.test_session900 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia923_receipts as F  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

HEAD = ["YEAR", "MONTH", "Plant Id", "Plant Name", "Plant State", "Purchase Type", "ENERGY_SOURCE", "FUEL_GROUP", "SUPPLIER",
        "QUANTITY", "Average Heat Content", "FUEL_COST"]


def sheet(rows):
    return pd.DataFrame([["EIA-923"] + [None] * (len(HEAD) - 1), HEAD] + rows)


def row(month=1, group="Coal", qty=1000, supplier="Peabody"):
    return [2025, month, 3, "Barry", "AL", "C", "SUB", group, supplier, qty, 17.5, 210.4]


class Receipts(unittest.TestCase):
    def test_events_units_and_repeats(self):
        counts = {}
        t = F.sheet_rows(sheet([row(), row(), row(group="Natural Gas", qty=50000), row(2, "Petroleum", 30),
                                ["Note: footnote"] + [None] * (len(HEAD) - 1)]), 2025, "u", "r", counts)
        self.assertEqual(len(t), 3)
        self.assertEqual(counts["repeated"], 1)
        self.assertEqual(set(t.event_type), {"fuel_receipt"})
        g = t.set_index("x_fuel_group")
        self.assertEqual((g.loc["Coal", "x_quantity_unit"], g.loc["Natural Gas", "x_quantity_unit"], g.loc["Petroleum", "x_quantity_unit"]),
                         ("short_ton", "Mcf", "bbl"))
        self.assertEqual((g.loc["Coal", "event_date"], g.loc["Petroleum", "event_date"]), ("2025-01-01", "2025-02-01"))
        self.assertTrue(g.loc["Coal", "event_id"].startswith("eia923r:3:2025-01:"))
        self.assertEqual((g.loc["Coal", "parties"], g.loc["Coal", "x_fuel_cost"]), ("Peabody", "210.4"))

    def test_a_fuel_group_not_in_the_map_stops(self):
        with self.assertRaises(RuntimeError):
            F.sheet_rows(sheet([row(group="Hydrogen")]), 2025, "u", "r", {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia923_fuel_receipts"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

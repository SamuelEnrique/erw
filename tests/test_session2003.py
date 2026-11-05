"""Session 2003: the Bureau of Reclamation's hydropower plants, a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/usbr_power.py on sheets built here in the workbook's form
(figures made up for the test, not Reclamation's): kW and kWh written as MW and MWh, net generation below zero kept, the
region from the annual sheet, the fiscal year check; the workbook's name found on the page; a heading not as read, a
facility in one sheet only and a month not MM/YYYY stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2003 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import usbr_power as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}


def monthly(rows):
    return pd.DataFrame([["Note: provisional"], ["Report generated 11/07/2025"], [None], U.MONTHLY] + rows)


def annual(rows):
    return pd.DataFrame([["Note"], ["Report generated"], [None], ["Region", "Facility ", "Units", "Fiscal Year", "Plant Capacity (kWh)",
                                                                   "Gross Generation (kWh)", "Net Generation (kWh)"]] + rows)


M = [["Alcova", "10/2013", 41400, 3182000, 85224, 3096776], ["Alcova", "11/2013", 41400, 3100000, 3200000, -100000]]
A = [["MB", "Alcova", 2, 2014, 41400, 6282000, 2996776]]


class Build(unittest.TestCase):
    def test_rows(self):
        s, checked, agree = U.build(monthly(M), annual(A), BASE)
        s = s.set_index(["variable", "ts_utc"])
        self.assertAlmostEqual(s.loc[("installed_capacity", "2013-10-01T00:00:00Z")].value, 41.4)
        self.assertAlmostEqual(s.loc[("net_generation", "2013-10-01T00:00:00Z")].value, 3096.776)
        self.assertAlmostEqual(s.loc[("net_generation", "2013-11-01T00:00:00Z")].value, -100.0)
        self.assertEqual(s.loc[("gross_generation", "2013-10-01T00:00:00Z")].x_region, "MB")
        self.assertEqual(s.loc[("gross_generation", "2013-10-01T00:00:00Z")].entity, "usbr_plant:alcova")
        self.assertEqual((checked, agree), (1, 1))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            U.build(monthly([["Alcova", "2013-10", 1, 1, 1, 1]]), annual(A), BASE)
        with self.assertRaises(RuntimeError):
            U.build(monthly(M + [["Seminoe", "10/2013", 1, 1, 1, 1]]), annual(A), BASE)
        bad = monthly(M)
        bad.iloc[3, 2] = "Capacity (MW)"
        with self.assertRaises(RuntimeError):
            U.build(bad, annual(A), BASE)

    def test_workbook_name(self):
        page = '<a href="Plant_Data_05_2025.xlsx">x</a> <a href="Plant_Data_11_2025.xlsx">y</a> <a href="Plant_Data_12_2024.xlsx">z</a>'
        self.assertEqual(U.workbook_name(page), "Plant_Data_11_2025.xlsx")
        with self.assertRaises(RuntimeError):
            U.workbook_name("<p>none</p>")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(U.TABLE), "power")
        self.assertIn(U.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

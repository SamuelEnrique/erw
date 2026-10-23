"""Session 869: EIA-861's advanced meters and net metering by utility.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_meters_netmetering.py's reading on sheets built here in
EIA's stacked headings (figures made up for the test, not EIA's): variables named from EIA's headings, the unit read from
the heading (a count of customers stays a count though its heading names MW), a column that is not a sector's figure read
past, the utility-level sheets only, the sector rule and the holds. No network.

    python -m unittest tests.test_session869 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_meters_netmetering as M  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")


class Units(unittest.TestCase):
    def test_unit_of(self):
        self.assertEqual(M.unit_of("photovoltaic capacity mw"), "MW")
        self.assertEqual(M.unit_of("energy served - ami (mwh)"), "MWh")
        self.assertEqual(M.unit_of("photovoltaic virtual customers- 1 mw and over"), "count")
        self.assertEqual(M.unit_of("battery pv-paired installations"), "count")

    def test_sheets(self):
        self.assertEqual(M.utility_sheets("Net_Metering", ["States", "Territories", "TPO", "States- State Level", "TPO- Total"]),
                         ["States", "Territories"])


class TheSheet(unittest.TestCase):
    def test_net_metering(self):
        top = ["Utility Characteristics", N, N, N, N, "Photovoltaic"] + [N] * 10
        mid = [N] * 5 + ["Capacity MW", N, N, N, N, "Customers", N, N, N, N, "Capacity MW"]
        low = ["Data Year", "Utility Number", "Utility Name", "State", "BA Code"] + ["Residential", "Commercial", "Industrial", "Transportation", "Total"] * 2 + ["Type"]
        row = [2024, 5, "U5", "AZ", "AZPS", 1.5, 0.5, 0, 0, 2.0, 100, 10, 0, 0, 110, "Ground"]
        notes = {}
        t = M.sheet_rows(pd.DataFrame([top, mid, low, row]), "Net_Metering", 2024, "u", "r", notes).set_index("variable")
        self.assertEqual((t.loc["photovoltaic_capacity_mw_total", "value"], t.loc["photovoltaic_capacity_mw_total", "unit"]), (2.0, "MW"))
        self.assertEqual((t.loc["photovoltaic_customers_total", "value"], t.loc["photovoltaic_customers_total", "unit"]), (110.0, "count"))
        self.assertEqual(t["entity"].iloc[0], "eia861_nm:5:AZ:AZPS")
        self.assertIn("photovoltaic / capacity mw / type", notes["read past"])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        for name in ("eia861_advanced_meters", "eia861_net_metering"):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(name, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

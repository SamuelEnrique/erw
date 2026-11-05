"""Session 876: EIA-861's short form (Form EIA-861S), as eia861_short_form.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_short_form.py on a sheet built here in EIA's layout
(utilities made up for the test, not EIA's): EIA's two spellings of two headings, thousand dollars as USD, the program
flags, the aggregates left out, the sector rule and the holds. No network.

    python -m unittest tests.test_session876 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_short_form as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def sheet(ba_head="BA Code", wh_head="Water Heater"):
    head = ["Data Year", "Utility Number", "Utility Name", "Ownership", "State", ba_head, "Total Revenue (Thousand Dollars)",
            "Total Sales (MWh)", "Total Customers", wh_head, "Net Metering", "Demand Side Management", "Time Based Programs"]
    return pd.DataFrame([head, [2024, 7, "A Small Coop", "Cooperative", "KS", "SWPP", 1200.5, 10000, 900, "Y", "N", "N", "N"],
                         [2024, 88888, "Withheld", "", "KS", "", 1, 1, 1, "", "", "", ""]])


class ShortForm(unittest.TestCase):
    def test_rows(self):
        for ba, wh in (("BA Code", "Water Heater"), ("BA_Code", "W_Heater")):
            t = S.sheet_rows(sheet(ba, wh), 2024, "u", "r", set()).set_index("variable")
            self.assertEqual(t["entity"].unique().tolist(), ["eia861_sf:7:KS:SWPP"])
            self.assertEqual((t.loc["total_revenue", "value"], t.loc["total_revenue", "unit"]), (1200500.0, "USD"))
            self.assertEqual((t.loc["total_sales", "unit"], t.loc["total_customers", "unit"]), ("MWh", "count"))
            self.assertEqual((t.loc["total_sales", "x_water_heater"], t.loc["total_sales", "x_net_metering"]), ("Y", "N"))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("eia861_short_form"), "power")
        self.assertIn("eia861_short_form", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia861_short_form", f.read())


if __name__ == "__main__":
    unittest.main()

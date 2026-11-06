"""Session 853: EIA-861's delivery-only companies (Texas's wires utilities), as eia861_delivery_only.

Energy Research Warehouse (ERW). The delivery companies' file has the layout of Sales_Ult_Cust's, so it is read by
eia861_sales.py's own sheet_rows; tested here on a sheet built in that layout (figures made up for the test, not EIA's):
part C rows read, the entity the sales table would give, revenue in USD. Then the sector rule and the holds. No network.

    python -m unittest tests.test_session853 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_delivery as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
SECT = ["RESIDENTIAL", "COMMERCIAL", "INDUSTRIAL", "TRANSPORTATION", "TOTAL"]
TOP = ["Utility Characteristics"] + [N] * 8 + sum(([s, N, N] for s in SECT), [])
MID = [N] * 9 + ["Revenues", "Sales", "Customers"] * 5
LOW = (["Data Year", "Utility Number", "Utility Name", "Part", "Service Type", "Data Type\nO = Observed\nI = Imputed", "State",
        "Ownership", "BA Code"] + ["Thousand Dollars", "Megawatthours", "Count"] * 5)
ROW = [2025, 8901, "A Test Wires Company", "C", "Delivery", "O", "TX", "Investor Owned", "ERCO"] + [100.0, 2000.0, 30] * 4 + [400.0, 8000.0, 120]


class TheSheet(unittest.TestCase):
    def test_read_as_the_sales_table_reads(self):
        t = D.sheet_rows(pd.DataFrame([TOP, MID, LOW, ROW]), 2025, "u", "r")
        g = t.set_index("variable")
        self.assertEqual(t.entity.unique().tolist(), ["eia861:8901:TX:C:ERCO"])
        self.assertEqual((g.loc["total_revenue", "value"], g.loc["total_revenue", "unit"]), (400000.0, "USD"))
        self.assertEqual((g.loc["total_sales", "value"], g.loc["total_sales", "unit"]), (8000.0, "MWh"))
        self.assertEqual(g.loc["total_sales", "x_part"], "C")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("eia861_delivery_only"), "power")
        self.assertIn("eia861_delivery_only", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia861_delivery_only", f.read())


if __name__ == "__main__":
    unittest.main()

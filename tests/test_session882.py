"""Session 882: EIA-861's operational data by utility.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_operations.py on a sheet built here in EIA's stacked
headings (figures made up for the test, not EIA's): each column found by its group and heading, "Retail Sales" and
"Sales to Ultimate Customers" both read as retail_sales, "Sales for Resale" told from "From Sales for Resale" by its
group, thousand dollars as USD, the short form column read past, an aggregate left out, two rows with two values under
one key left out and counted, a heading not in the map stopping the run, the sector rule and the holds. No network.

    python -m unittest tests.test_session882 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_operations as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
LOW = ["Data Year", "Utility Number", "Utility Name", "Short Form", "State", "Ownership Type", "NERC Region",
       "Summer Peak Demand", "Winter Peak Demand", "Net Generation", "Wholesale Power Purchases", "Exchange Energy Received",
       "Exchange Energy Delivered", "Net Power Exchanged", "Wheeled Power Received", "Wheeled Power Delivered",
       "Net Wheeled Power", "Transmission by Other Losses", "Total Sources", "Sales to Ultimate Customers",
       "Sales for Resale", "Furnished without Charge", "Consumed by Respondent without Charge", "Total Energy Losses",
       "Total Disposition", "From Retail Sales", "From Delivery Customers", "From Sales for Resale",
       "From Credits or Adjustments", "From Transmission", "From Other", "Total", "Data Type\nO = Observed\nI = Imputed"]


def sheet(rows, retail="Sales to Ultimate Customers"):
    top = ["Utility Characteristics"] + [N] * 6 + ["Demand", N, "Energy Sources (Megawatthours)"] + [N] * 9 + ["Disposition"] + [N] * 5 + ["Electric Revenues"] + [N] * 7
    mid = [N] * 7 + ["(Megawatts)", N, N, N, "Power Exchanged", N, N, "Wheeled Power"] + [N] * 4 + ["(Megawatthours)"] + [N] * 5 + ["(Thousands Dollars)"] + [N] * 7
    low = [retail if x == "Sales to Ultimate Customers" else x for x in LOW]
    return pd.DataFrame([top, mid, low] + rows)


def row(util, state, v):
    return [2024, util, f"U{util}", "N", state, "Municipal", "SERC", 30.5, 31, 0, 100 * v, 0, ".", -5, 0, 0, 0, 0, 100 * v,
            90 * v, 2 * v, 0, 0, 8 * v, 100 * v, 7 * v, ".", 1, 0, 0, 0.5, 8.5 * v, "O"]


class Operations(unittest.TestCase):
    def test_columns_units_and_groups(self):
        t = O.sheet_rows(sheet([row(55, "MS", 1), row(99999, "MS", 3)]), 2024, "u", "r", {})
        g = t.set_index("variable")
        self.assertEqual(t.entity.unique().tolist(), ["eia861_op:55:MS"])
        self.assertEqual((g.loc["summer_peak_demand", "value"], g.loc["summer_peak_demand", "unit"]), (30.5, "MW"))
        self.assertEqual((g.loc["retail_sales", "value"], g.loc["sales_for_resale", "value"]), (90.0, 2.0))
        self.assertEqual((g.loc["revenue_sales_for_resale", "value"], g.loc["revenue_sales_for_resale", "unit"]), (1000.0, "USD"))
        self.assertEqual(g.loc["revenue_total", "value"], 8500.0)
        self.assertEqual(g.loc["exchange_net", "value"], -5.0)
        self.assertNotIn("exchange_delivered", g.index)                     # a "." cell has no row
        self.assertEqual((t.x_ownership.iloc[0], t.x_nerc_region.iloc[0], t.x_data_type.iloc[0]), ("Municipal", "SERC", "O"))

    def test_retail_sales_under_its_old_name(self):
        t = O.sheet_rows(sheet([row(55, "MS", 1)], retail="Retail Sales"), 2024, "u", "r", {})
        self.assertIn("retail_sales", set(t.variable))

    def test_two_values_under_one_key_are_left_out(self):
        sk = {}
        t = O.sheet_rows(sheet([row(2, "IN", 1), row(2, "IN", 2), row(3, "IN", 1)]), 2024, "u", "r", sk)
        self.assertEqual(t.entity.unique().tolist(), ["eia861_op:3:IN"])
        self.assertEqual(sk["no key"], {"eia861_op:2:IN 2024"})

    def test_a_heading_not_in_the_map_stops(self):
        s = sheet([row(55, "MS", 1)])
        s.iloc[2, 10] = "Something New"
        with self.assertRaises(RuntimeError):
            O.sheet_rows(s, 2024, "u", "r", {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia861_operational_data"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

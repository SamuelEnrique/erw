"""Session 868: EIA-861's demand response and dynamic pricing programs by utility.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_programs.py on sheets built here in EIA's stacked
headings (figures made up for the test, not EIA's): the measures and sectors read from the headings, thousand dollars as
USD, the program flags kept as EIA gives them, two rows with two values under one key left out and counted, the sector
rule and the holds. No network.

    python -m unittest tests.test_session868 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_programs as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
SECT = ["Residential", "Commercial", "Industrial", "Transportation", "Total"]


def dr_sheet(rows):
    top = ["Utility Characteristics", N, N, N, N, "Yearly Energy and Demand Savings"] + [N] * 19 + ["Program Costs"] + [N] * 9
    mid = [N] * 5
    for m in ["Number of Customers Enrolled", "Energy Savings (MWh)", "Potential Peak Demand Savings (MW)", "Actual Peak Demand Savings (MW)",
              "Customer Incentives (Thousand Dollars)", "All Other Costs (Thousand Dollars)"]:
        mid += [m] + [N] * 4
    low = ["Data Year", "Utility Number", "Utility Name", "State", "BA Code"] + SECT * 6
    return pd.DataFrame([top, mid, low] + rows)


def dr_row(util, state, value):
    return [2024, util, f"U{util}", state, "PJM"] + [value, value, 0, 0, 2 * value] * 6


def dp_sheet(rows):
    top = ["Utility Characteristics", N, N, N, N, "Number of"] + [N] * 4 + ["Types of Program"] + [N] * 19
    mid = [N] * 5 + ["Customers Enrolled"] + [N] * 4
    for m in ["Time of Use Pricing", "Real Time Pricing", "Variable Peak Pricing", "Critical Peak Pricing", "Critical Peak Rebate"]:
        mid += [m] + [N] * 3
    low = ["Data Year", "Utility Number", "Utility Name", "State", "BA Code"] + SECT + SECT[:4] * 5
    return pd.DataFrame([top, mid, low] + rows)


class Programs(unittest.TestCase):
    def test_demand_response(self):
        sk = {}
        t = P.sheet_rows(dr_sheet([dr_row(1, "IL", 10), dr_row(88888, "IL", 5)]), "Demand_Response", 2024, "u", "r", sk)
        g = t.set_index("variable")
        self.assertEqual(t.entity.unique().tolist(), ["eia861_dr:1:IL:PJM"])
        self.assertEqual((g.loc["customers_enrolled_total", "value"], g.loc["customers_enrolled_total", "unit"]), (20.0, "count"))
        self.assertEqual((g.loc["customer_incentives_residential", "value"], g.loc["customer_incentives_residential", "unit"]), (10000.0, "USD"))
        self.assertEqual(g.loc["actual_peak_savings_total", "unit"], "MW")

    def test_two_values_under_one_key_are_left_out(self):
        sk = {}
        t = P.sheet_rows(dr_sheet([dr_row(2, "IN", 10), dr_row(2, "IN", 11), dr_row(3, "IN", 4)]), "Demand_Response", 2024, "u", "r", sk)
        self.assertEqual(t.entity.unique().tolist(), ["eia861_dr:3:IN:PJM"])
        self.assertEqual(sk["no key"], {"eia861_dr:2:IN:PJM 2024"})

    def test_dynamic_pricing_flags(self):
        row = [2024, 7, "U7", "CA", "CISO"] + [100, 0, 0, 0, 100] + ["Y", "N", N, N] * 5
        t = P.sheet_rows(dp_sheet([row]), "Dynamic_Pricing", 2024, "u", "r", {})
        self.assertEqual(sorted(t.variable.unique())[:1], ["customers_enrolled_commercial"])
        self.assertEqual((t.x_tou_residential.iloc[0], t.x_tou_commercial.iloc[0], t.x_cpr_industrial.iloc[0]), ("Y", "N", ""))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        for name in ("eia861_demand_response", "eia861_dynamic_pricing"):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(name, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

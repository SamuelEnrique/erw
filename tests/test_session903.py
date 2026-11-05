"""Session 903: EIA's Electric Power Annual, chapter 8 (heat rates, investor-owned utilities' revenue and expenses, power
plant operating expenses).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_epa_costs.py on sheets built here in the four tables' form
(figures made up for the test, not EIA's): Btu per kWh as MMBtu/MWh, W and -- having no row, table 8.3's lines as a path
by their dots, million dollars as USD, table 8.4's two blocks with mills per kWh as USD/MWh, a heading not in the form
read stopping the run, the sector rule and the holds. No network.

    python -m unittest tests.test_session903 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_epa_costs as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
P = ["Nuclear", "Fossil Steam", "Hydro-electric", "\n Gas Turbine and Small Scale"]


class Chapter8(unittest.TestCase):
    def test_heat_rates(self):
        d81 = pd.DataFrame([["Table 8.1", N, N, N, N], ["(Btu per Kilowatthour)", N, N, N, N], ["Year", "Coal", "Petroleum", "Natural Gas", "Nuclear"],
                            [2025, 10500, "W", 7781, 10443]])
        t = pd.DataFrame(C.table_81(d81, "u", "r")).set_index("entity")
        self.assertAlmostEqual(t.loc["eia_epa:heat_rate:natural_gas", "value"], 7.781)
        self.assertEqual(t.loc["eia_epa:heat_rate:coal", "unit"], "MMBtu/MWh")
        self.assertNotIn("eia_epa:heat_rate:petroleum", t.index)
        d82 = pd.DataFrame([["Table 8.2", N, N, N, N], ["x", N, N, N, N], ["Prime Mover", "Coal", "Petroleum", "Natural Gas", "Nuclear"],
                            [2024, N, N, N, N], ["Combined Cycle", "W", 9676, 7655, "--"], ["Notes: W", N, N, N, N]])
        t = pd.DataFrame(C.table_82(d82, "u", "r"))
        self.assertEqual(sorted(t.entity), ["eia_epa:tested_heat_rate:combined_cycle:natural_gas", "eia_epa:tested_heat_rate:combined_cycle:petroleum"])
        self.assertEqual(t.ts_utc.iloc[0], "2024-01-01T00:00:00Z")

    def test_finance_path(self):
        d = pd.DataFrame([["Table 8.3", N], ["x", N], [" ", N], ["Description", 2025.0], ["Utility Operating Expenses", 100.0],
                          ["......Electric Utility", 90.0], ["............Operation", 60.0], ["..................Production", 40.0],
                          ["........................Cost of Fuel", 15.0], ["Notes: something", N]])
        t = pd.DataFrame(C.table_83(d, "u", "r")).set_index("entity")
        k = "eia_epa:iou_finance:utility_operating_expenses.electric_utility.operation.production.cost_of_fuel"
        self.assertEqual((t.loc[k, "value"], t.loc[k, "unit"]), (15e6, "USD"))

    def test_plant_expense_blocks(self):
        d = pd.DataFrame([["Table 8.4"] + [N] * 8, ["x"] + [N] * 8, [" "] + [N] * 8,
                          [N, "Operation", N, N, N, "Maintenance", N, N, N], ["Year"] + P + P, [2025, 10.14, 6.08, 9.62, 1.77, 7.1, 5.42, 6.81, 1.83],
                          [" "] + [N] * 8, [N, "Fuel", N, N, N, "Total", N, N, N], ["Year"] + P + P, [2025, 6.64, 30.62, "--", 24.61, 23.89, 42.12, 16.43, 28.22]])
        t = pd.DataFrame(C.table_84(d, "u", "r")).set_index(["entity", "variable"])
        self.assertEqual(t.loc[("eia_epa:iou_plant_expense:nuclear", "total_expense"), "value"], 23.89)
        self.assertEqual(t.loc[("eia_epa:iou_plant_expense:fossil_steam", "fuel_expense"), "unit"], "USD/MWh")
        self.assertNotIn(("eia_epa:iou_plant_expense:hydro_electric", "fuel_expense"), t.index)
        d.iloc[3, 1] = "Something"
        with self.assertRaises(RuntimeError):
            C.table_84(d, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia_power_costs_annual"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

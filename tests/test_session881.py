"""Session 881: EIA-861's energy efficiency programs by utility.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_efficiency.py on a sheet built here in EIA's stacked
headings (figures made up for the test, not EIA's): the four groups (the reporting year's and the life cycle's savings
and costs, "Cost" or "Costs"), thousand dollars as USD, the weighted average life with no total, the website kept, an
aggregate left out, two rows with two values under one key left out and counted, a heading not in the map stopping the
run, the sector rule and the holds. No network.

    python -m unittest tests.test_session881 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_efficiency as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
SECT = ["Residential", "Commercial", "Industrial", "Transportation", "Total"]


def sheet(rows, cost="Reporting Year Incremental Costs"):
    top = ["Utility Characteristics", N, N, N, N]
    for g in ["Reporting Year Incremental Annual Savings", "Incremental Life Cycle Savings", cost, "Incremental Life Cycle Cost"]:
        top += [g] + [N] * 9
    top += ["Weighted Average Life", N, N, N, N]
    mid = [N] * 5
    for m in ["Energy Savings (MWh)", "Peak Demand Savings (MW)"] * 2 + ["Customer Incentives (Thousand Dollars)", "All Other Costs (Thousand Dollars)"] * 2:
        mid += [m] + [N] * 4
    mid += ["(Years)"] + [N] * 4
    low = ["Data Year", "Utility Number", "Utility Name", "State", "BA Code"] + SECT * 8 + SECT[:4] + ["Website"]
    return pd.DataFrame([top, mid, low] + rows)


def row(util, state, value):
    return [2024, util, f"U{util}", state, "PJM"] + [value, value, ".", ".", 2 * value] * 8 + [10, 12, ".", ".", "www.u.example"]


class Efficiency(unittest.TestCase):
    def test_groups_units_and_life(self):
        t = E.sheet_rows(sheet([row(1, "IL", 5), row(99999, "IL", 3)]), 2024, "u", "r", {})
        g = t.set_index("variable")
        self.assertEqual(t.entity.unique().tolist(), ["eia861_ee:1:IL:PJM"])
        self.assertEqual((g.loc["annual_energy_savings_total", "value"], g.loc["annual_energy_savings_total", "unit"]), (10.0, "MWh"))
        self.assertEqual((g.loc["life_peak_savings_residential", "value"], g.loc["life_peak_savings_residential", "unit"]), (5.0, "MW"))
        self.assertEqual((g.loc["annual_customer_incentives_commercial", "value"], g.loc["annual_customer_incentives_commercial", "unit"]), (5000.0, "USD"))
        self.assertEqual(g.loc["life_other_costs_total", "value"], 10000.0)
        self.assertEqual((g.loc["weighted_average_life_commercial", "value"], g.loc["weighted_average_life_commercial", "unit"]), (12.0, "year"))
        self.assertNotIn("weighted_average_life_total", g.index)
        self.assertNotIn("annual_energy_savings_industrial", g.index)          # a "." cell has no row
        self.assertEqual(t.x_website.iloc[0], "www.u.example")

    def test_cost_in_the_singular(self):
        t = E.sheet_rows(sheet([row(1, "IL", 5)], cost="Reporting Year Incremental Cost"), 2024, "u", "r", {})
        self.assertIn("annual_other_costs_total", set(t.variable))

    def test_two_values_under_one_key_are_left_out(self):
        sk = {}
        t = E.sheet_rows(sheet([row(2, "IN", 10), row(2, "IN", 11), row(3, "IN", 4)]), 2024, "u", "r", sk)
        self.assertEqual(t.entity.unique().tolist(), ["eia861_ee:3:IN:PJM"])
        self.assertEqual(sk["no key"], {"eia861_ee:2:IN:PJM 2024"})

    def test_a_heading_not_in_the_map_stops(self):
        s = sheet([row(1, "IL", 5)])
        s.iloc[0, 5] = "Something New"
        with self.assertRaises(RuntimeError):
            E.sheet_rows(s, 2024, "u", "r", {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia861_energy_efficiency"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

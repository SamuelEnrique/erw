"""Session 883: EIA-861's distribution systems and distributed generation not net metered, by utility.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia861_distribution_systems.py and
eia861_distributed_generation.py on sheets built here in EIA's headings (figures made up for the test, not EIA's): the
circuits as counts, the technologies and sectors read from stacked headings under a title row, "Storage" and "Battery"
as one technology beside "Battery Energy" in MWh, the data type kept, an aggregate left out, two rows with two values
under one key left out and counted, a heading not in the map stopping the run, the sector rules and the holds. No
network.

    python -m unittest tests.test_session883 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia861_distribution_systems as DS  # noqa: E402
import eia861_distributed_generation as DG  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
SECT = ["Residential", "Commercial", "Industrial", "Transportation", "Direct Connected", "Total"]


def ds_sheet(rows):
    return pd.DataFrame([["Data Year", "Utility Number", "Utility Name", "State", "Distribution Circuits",
                          "Circuits with Voltage Optimization"]] + rows)


def dg_sheet(rows, title=False, battery_energy=False):
    techs = ["Photovoltaic (MW)", "Storage (MW)" if not battery_energy else "Battery (MW)"] + (["Battery Energy (MWh)"] if battery_energy else []) + [
        "Wind (MW)", "Hydroelectric (MW)", "Fuel Cells (MW)", "Internal Combustion (MW)", "Combustion Turbine (MW)", "Steam (MW)",
        "Other (MW)", "Total (MW)"]
    top = ["Utility Characteristics", N, N, N, N, "Number and Capacity (MW)", N, N, N, N]
    for t in techs:
        top += [t] + [N] * 5
    low = ["Year", "State", "Utility Number", "Utility Name", "BA_CODE", "Number of Generators", "Total Capacity",
           "Capacity Back-up Only", "Capacity Utility Owned", "Type"] + SECT * len(techs)
    head = [["Utility Level Data - States"] + [N] * (len(low) - 1)] if title else []
    return pd.DataFrame(head + [top, low] + rows), len(techs)


def dg_row(util, state, v, ntech):
    return [2024, state, util, f"U{util}", "PJM", 3, 2.0 * v, 0, ".", "A"] + [v, v, 0, 0, 0, 2.0 * v] * ntech


class DistributionSystems(unittest.TestCase):
    def test_circuits(self):
        t = DS.sheet_rows(ds_sheet([[2024, 55, "U55", "MS", 8, 3], [2024, 88888, "x", "MS", 1, 1]]), 2024, "u", "r", {})
        g = t.set_index("variable")
        self.assertEqual(t.entity.unique().tolist(), ["eia861_ds:55:MS"])
        self.assertEqual((g.loc["distribution_circuits", "value"], g.loc["circuits_voltage_optimization", "value"]), (8.0, 3.0))
        self.assertEqual(set(t.unit), {"count"})

    def test_blank_and_two_values(self):
        sk = {}
        t = DS.sheet_rows(ds_sheet([[2024, 40428, "G", "GU", 65, " "], [2024, 2, "A", "IN", 4, 1], [2024, 2, "A", "IN", 5, 1]]), 2024, "u", "r", sk)
        self.assertEqual(t.variable.tolist(), ["distribution_circuits"])
        self.assertEqual(sk["no key"], {"eia861_ds:2:IN 2024"})


class DistributedGeneration(unittest.TestCase):
    def test_technologies_sectors_and_units(self):
        s, n = dg_sheet([], title=True)
        s = pd.concat([s, pd.DataFrame([dg_row(7, "CA", 1.5, n), dg_row(99999, "CA", 1, n)])], ignore_index=True)
        t = DG.sheet_rows(s, 2024, "u", "r", {})
        g = t.set_index("variable")
        self.assertEqual(t.entity.unique().tolist(), ["eia861_dg:7:CA:PJM"])
        self.assertEqual((g.loc["number_of_generators", "value"], g.loc["number_of_generators", "unit"]), (3.0, "count"))
        self.assertEqual((g.loc["pv_capacity_residential", "value"], g.loc["pv_capacity_residential", "unit"]), (1.5, "MW"))
        self.assertEqual(g.loc["battery_capacity_total", "value"], 3.0)
        self.assertEqual(g.loc["combustion_turbine_capacity_direct_connected", "value"], 0.0)
        self.assertNotIn("capacity_utility_owned", g.index)                 # a "." cell has no row
        self.assertEqual(t.x_data_type.iloc[0], "A")

    def test_battery_energy_in_mwh(self):
        s, n = dg_sheet([], battery_energy=True)
        s = pd.concat([s, pd.DataFrame([dg_row(7, "CA", 1, n)])], ignore_index=True)
        g = DG.sheet_rows(s, 2024, "u", "r", {}).set_index("variable")
        self.assertEqual((g.loc["battery_energy_total", "value"], g.loc["battery_energy_total", "unit"]), (2.0, "MWh"))
        self.assertEqual(g.loc["battery_capacity_total", "unit"], "MW")

    def test_two_values_and_an_unknown_heading(self):
        s, n = dg_sheet([])
        s2 = pd.concat([s, pd.DataFrame([dg_row(2, "IN", 1, n), dg_row(2, "IN", 2, n), dg_row(3, "IN", 1, n)])], ignore_index=True)
        sk = {}
        t = DG.sheet_rows(s2, 2024, "u", "r", sk)
        self.assertEqual(t.entity.unique().tolist(), ["eia861_dg:3:IN:PJM"])
        self.assertEqual(sk["no key"], {"eia861_dg:2:IN:PJM 2024"})
        s.iloc[0, 10] = "Something New"
        with self.assertRaises(RuntimeError):
            DG.sheet_rows(s, 2024, "u", "r", {})


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        for name in ("eia861_distribution_systems", "eia861_distributed_generation"):
            self.assertEqual(B.sector_of(name), "power")
            self.assertIn(name, R.STORAGE_HELD)
            with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
                self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

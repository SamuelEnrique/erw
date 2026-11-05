"""Session 2409: Statistics Mauritius, Energy and Water Statistics: electricity generation by source, capacity, peak demand
and sales, a year (in place of Namibia).

Energy Research Warehouse (ERW). Tests warehouse/connectors/statsmu_mauritius.py's table readers on rows built here in
the layout of the Statistics Mauritius workbooks (made up for the test, not its figures): Table 8's labels indented across
three columns, its sources adding to its primary, secondary and total rows, Table 7's sources to its total, Table 1's
generation, renewables' share and sales; a sum that does not hold, a row missing and a unit that is not GWh stopping the
run; the sector rule and the live-set hold (internal). No network, no workbook file.

    python -m unittest tests.test_session2409 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import statsmu_mauritius as S  # noqa: E402
import build_coverage as B  # noqa: E402


def pad(cells):
    r = [None] * 40
    for c, x in cells.items():
        r[c] = x
    return r


def t8(coal=50.0, drop=None):
    lines = [(1, "Primary energy", 10.0), (2, "Hydro (renewable energy)", 4.0), (2, "Wind (renewable energy)", 1.0),
             (2, "Landfill gas (renewable energy)", 1.0), (2, "Photovoltaic (renewable energy)", 4.0), (1, "Secondary energy", 90.0),
             (2, "Gas turbine (kerosene)", 1.0), (2, "Fuel oil & Diesel", 30.0), (2, "Coal", coal), (2, "Bagasse & Fuelwood", 9.0),
             (0, "Total electricity generated", 100.0), (1, "of which renewable energy", 19.0)]
    rows = [pad({0: "Table 8 - Electricity generation by source of energy, 2024 and 2025"}), pad({}),
            pad({0: "Source of energy", 10: 2024, 16: 2025}), pad({10: "GWh", 13: "%", 16: "GWh", 19: "%"})]
    rows += [pad({c: lab, 10: v, 13: 1.0, 16: v, 19: 1.0}) for c, lab, v in lines if lab != drop]
    return rows + [pad({})]


def t7(total=100.0):
    return [pad({0: "Table 7 - Evolution of power plant capacities1, peak power demand and electricity generation, 2024 and 2025"}), pad({}),
            pad({0: "Year", 1: "Installed", 3: "Effective", 9: "Peak power demand (MW)", 11: "Electricity generated (GWh)"}),
            pad({1: "capacity", 3: "capacity", 9: "(MW)", 11: "Hydro", 12: "Wind", 14: "Photovoltaic", 15: "Thermal", 19: "Total"}),
            pad({1: "(MW)", 3: "(MW)", 9: "Mauritius", 10: "Rodrigues", 15: "Landfill Gas", 17: "Other"}), pad({}),
            pad({1: 2024, 3: 900.0, 5: 800.0, 9: 520.0, 10: 8.0, 11: 4.0, 12: 1.0, 14: 4.0, 15: 1.0, 17: 90.0, 19: total}),
            pad({1: 2025, 3: 950.0, 5: 850.0, 9: 560.0, 10: 9.0, 11: 4.0, 12: 1.0, 14: 4.0, 15: 1.0, 17: 90.0, 19: 100.0})]


def t1(unit="GWh"):
    return [pad({0: "Table 1 - Main Energy and Water Indicators, 2024 - 2025"}), pad({0: "Indicators", 1: "Unit", 2: 2024, 3: 2025}),
            pad({0: "Total electricity generated", 1: unit, 2: 100.0, 3: 100.0}), pad({0: "           Of which renewables", 1: "%", 2: 19.0, 3: 19.0}),
            pad({0: "Total electricity sold", 1: "GWh", 2: 85.0, 3: 88.0})]


class Readers(unittest.TestCase):
    def test_table8(self):
        out, years = S.table8(t8())
        self.assertEqual(years, [2024, 2025])
        self.assertEqual(out["generation_bagasse"][2025], 9.0)
        self.assertEqual(out["generation_renewable"][2024], 19.0)
        for bad in (t8(coal=51.0), t8(drop="Coal")):
            with self.assertRaises(RuntimeError):
                S.table8(bad)

    def test_table7(self):
        out = S.table7(t7(), [2024, 2025])
        self.assertEqual(out[2024]["peak_demand_mauritius"], 520.0)
        self.assertEqual(out[2025]["capacity_effective"], 850.0)
        with self.assertRaises(RuntimeError):
            S.table7(t7(total=101.0), [2024, 2025])

    def test_table1(self):
        out = S.table1(t1())
        self.assertEqual(out["electricity_sold"], {2024: 85.0, 2025: 88.0})
        self.assertEqual(out["renewable_share"][2025], 19.0)
        with self.assertRaises(RuntimeError):
            S.table1(t1(unit="MWh"))


class Registered(unittest.TestCase):
    def test_sector_and_hold(self):
        self.assertEqual(B.sector_of(S.NAME), "power")
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

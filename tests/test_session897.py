"""Session 897: EIA-923's monthly generation and fuel by plant.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia923_monthly.py on a sheet built here in the workbook's
form (figures made up for the test, not EIA's): the monthly figures found by their headings (EIA's "Septembe" among
them), MMBtu as TBtu, a month not yet reported having no row, a nuclear unit in the key, plant 99999 (EIA's state-level
increment) left out, two records with two values under one key left out, a heading not in the form read stopping the
run, the zip's address outside /archive/, the sector rule and the holds. No network.

    python -m unittest tests.test_session897 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia923_monthly as M  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "Septembe", "October", "November", "December"]
FRONT = ["Plant Id", "Combined Heat And\nPower Plant", "Nuclear Unit Id", "Plant Name", "Operator Name", "Operator Id", "Plant State",
         "Census Region", "NERC Region", "Reserved", "NAICS Code", "EIA Sector Number", "Sector Name", "Reported\nPrime Mover",
         "Reported\nFuel Type Code", "MER\nFuel Type Code", "Balancing\nAuthority Code", "Respondent\nFrequency", "Physical\nUnit Label"]
BLOCKS = ["Quantity", "Elec_Quantity", "MMBtuPer_Unit", "Tot_MMBtu", "Elec_MMBtu", "Netgen"]
BACK = ["Total Fuel Consumption\nQuantity", "Electric Fuel Consumption\nQuantity", "Total Fuel Consumption\nMMBtu",
        "Elec Fuel Consumption\nMMBtu", "Net Generation\n(Megawatthours)", "YEAR"]


def sheet(rows):
    head = FRONT + [f"{b}\n{m}" for b in BLOCKS for m in MONTHS] + BACK
    return pd.DataFrame([["U.S. Department of Energy"] + [None] * (len(head) - 1), head] + rows)


def row(plant, mover, fuel, gen, nuclear="."):
    front = [plant, "N", nuclear, "Barry", "Alabama Power Co", 195, "AL", "ESC", "SERC", "", 22, 1, "Electric Utility", mover, fuel,
             fuel, "SOCO", "M", "mcf"]
    month = lambda v: [v] * 6 + ["."] * 6  # noqa: E731  six months reported
    figures = month(10) + month(10) + month(1.02) + month(2_000_000) + month(1_500_000) + month(gen)
    return front + figures + [0, 0, 0, 0, 0, 2025]


class Monthly(unittest.TestCase):
    def test_figures_units_and_months(self):
        t = M.sheet_rows(sheet([row(3, "CT", "NG", 700), row(99999, "CT", "NG", 5)]), 2025, "u", "r", {})
        g = t.set_index(["variable", "ts_utc"])
        self.assertEqual(t.entity.unique().tolist(), ["eia923m:3:CT:NG:"])
        self.assertEqual((g.loc[("net_generation", "2025-01-01T00:00:00Z"), "value"], g.loc[("net_generation", "2025-01-01T00:00:00Z"), "unit"]), (700.0, "MWh"))
        self.assertAlmostEqual(g.loc[("fuel_consumed", "2025-06-01T00:00:00Z"), "value"], 2.0)
        self.assertEqual(g.loc[("fuel_consumed_electric", "2025-06-01T00:00:00Z"), "unit"], "TBtu")
        self.assertNotIn(("net_generation", "2025-07-01T00:00:00Z"), g.index)           # "." has no row
        self.assertEqual((t.x_respondent_frequency.iloc[0], t.x_ba_code.iloc[0], t.geo.iloc[0]), ("M", "SOCO", "US-AL"))

    def test_nuclear_unit_and_no_key(self):
        sk = {}
        t = M.sheet_rows(sheet([row(46, "ST", "NUC", 900, nuclear=1), row(46, "ST", "NUC", 800, nuclear=2),
                                row(7, "GT", "NG", 1), row(7, "GT", "NG", 2)]), 2025, "u", "r", sk)
        self.assertEqual(sorted(t.entity.unique()), ["eia923m:46:ST:NUC:1", "eia923m:46:ST:NUC:2"])
        self.assertEqual(sk["no key"], {"eia923m:7:GT:NG: 2025"})

    def test_what_stops_and_the_address(self):
        s = sheet([row(3, "CT", "NG", 700)])
        s.iloc[1, 4] = "Something New"
        with self.assertRaises(RuntimeError):
            M.sheet_rows(s, 2025, "u", "r", {})
        self.assertEqual(M.zip_url(2025), "https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "eia923_plant_fuel_monthly"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

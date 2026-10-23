"""Session 873: EIA-860's plants, as eia860_plants_annual.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia860_plants.py on a plant sheet built here in EIA's layout
(plants made up for the test, not EIA's): the newest final zip outside /archive/ found on the page (never the early
release), every column kept by its heading, a plant code given twice, the sector rule and the holds. No network.

    python -m unittest tests.test_session873 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia860_plants as E  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

N = float("nan")
HEAD = ["Utility ID", "Utility Name", "Plant Code", "Plant Name", "State", "County", "Latitude", "Longitude",
        "Transmission or Distribution System Owner", "Grid Voltage (kV)"]


class Plants(unittest.TestCase):
    def test_newest_final_zip(self):
        html = ('<a href="archive/xls/eia8602024.zip"> <a href="xls/eia8602025.zip"> <a href="xls/eia8602025ER.zip"> '
                '<a href="eia860a/eia860a1999.zip">')
        self.assertEqual(E.newest(html), ("https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip", 2025))

    def test_rows(self):
        f = pd.DataFrame([["Form EIA-860 Data, Schedule 2"] + [N] * 9, HEAD,
                          [1, "U One", 10, "Plant Ten", "TX", "Harris", 29.7, -95.3, "CenterPoint Energy", 138.0]])
        t = E.plants(f, 2025, "u", "r").set_index("entity_id")
        r = t.loc["eia860_plant:10"]
        self.assertEqual((r["name"], r["geo"], r["operator"], r["x_county"], r["x_grid_voltage_kv"]), ("Plant Ten", "US-TX", "U One", "Harris", "138"))
        self.assertEqual(r["x_transmission_or_distribution_system_owner"], "CenterPoint Energy")

    def test_a_code_twice_stops(self):
        row = [1, "U", 10, "P", "TX", "Harris", 1, 1, "", 69]
        with self.assertRaises(RuntimeError):
            E.plants(pd.DataFrame([HEAD, row, row]), 2025, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("eia860_plants_annual"), "power")
        self.assertIn("eia860_plants_annual", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia860_plants_annual", f.read())


if __name__ == "__main__":
    unittest.main()

"""Session 943: ORNL's Existing Hydropower Assets Unit Database.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ornl_eha_units.py on unit rows built here in the workbook's
form (figures made up for the test, not ORNL's): the unit id, its name, capacity and the plant id kept, "Unknown" kept
as given; a heading not in the map and an id given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session943 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ornl_eha_units as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(**kw):
    r = {k: None for k in list(U.FIELDS) + sorted(U.NAMED)}
    r.update(EHA_PtGnID="hc0001_p01_1", EHA_PtID="hc0001_p01", PtName="Alcova", EHA_GnID="1", MW="20.7", RhYear="Unknown",
             Speed_rpm="163.6", Latitude="42.5", Longitude="-106.7")
    r.update(kw)
    return r


class Units(unittest.TestCase):
    def test_shape(self):
        t = U.units(pd.DataFrame([row(), row(EHA_PtGnID="hc0001_p01_2", EHA_GnID="2")], dtype=str), "u", "r", "v").set_index("entity_id")
        a = t.loc["ornl_eha_unit:hc0001_p01_1"]
        self.assertEqual((a["name"], a.capacity_mw, a.eha_plant_id, a.refurbished_year, a.speed_rpm, a.entity_type),
                         ("Alcova, unit 1", 20.7, "hc0001_p01", "Unknown", 163.6, "generator"))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            U.units(pd.DataFrame([dict(row(), Extra="x")], dtype=str), "u", "r", "v")
        with self.assertRaises(RuntimeError):
            U.units(pd.DataFrame([row(), row()], dtype=str), "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "ornl_eha_hydropower_units"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

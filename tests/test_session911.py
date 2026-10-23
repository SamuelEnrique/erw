"""Session 911: Oak Ridge National Laboratory's Existing Hydropower Assets Plant Database.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ornl_eha.py on plant rows built here in the workbook's form
(figures made up for the test, not ORNL's): capacity_mw as hydro and pumped storage summed, the FERC dates as dates, the
EIA plant id as an integer string, a blank kept blank; a heading not in the map and an id given twice stopping the run;
the sector rule and the holds. No network.

    python -m unittest tests.test_session911 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ornl_eha as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(**kw):
    r = {k: None for k in list(O.FIELDS) + sorted(O.NAMED)}
    r.update(EHA_PtID="hc0001_p01", PtName="Test Dam", State="WA", Latitude="47.5", Longitude="-120.1", Type="HY/PSH",
             EIA_PtID="518", FcIssue="2004-06-23 00:00:00", HY_MW="86", PSH_MW="8.5", HY_OpYear="1954")
    r.update(kw)
    return r


class Plants(unittest.TestCase):
    def test_shape(self):
        t = O.plants(pd.DataFrame([row(), row(EHA_PtID="hc0002_p01", HY_MW=None, PSH_MW=None, EIA_PtID=None, FcIssue=None)], dtype=str), "u", "r", "v")
        a, b = t.iloc[0], t.iloc[1]
        self.assertEqual((a.entity_id, a.geo, a.capacity_mw, a.eia_plant_id, a.ferc_issued, a.hy_first_year), ("ornl_eha:hc0001_p01", "US-WA", 94.5, "518", "2004-06-23", 1954))
        self.assertEqual((b.capacity_mw, b.eia_plant_id, b.ferc_issued), ("", "", ""))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            O.plants(pd.DataFrame([dict(row(), Extra="x")], dtype=str), "u", "r", "v")
        with self.assertRaises(RuntimeError):
            O.plants(pd.DataFrame([row(), row()], dtype=str), "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "ornl_eha_hydropower_plants"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

"""Session 901: ERCOT's resource nodes placed by the county and zone of their CDR units.

Energy Research Warehouse (ERW). Tests warehouse/derived/ercot_node_places.py on tables built here (names made up for the
test): a node and its CDR units matched by the station code, the county and zone taken only when every unit agrees, a
station no unit carries and a station whose units disagree left out and counted, hubs and zones left out, the sector rule,
the holds and the method note. No network.

    python -m unittest tests.test_session901 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ercot_node_places as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


class Places(unittest.TestCase):
    def test_match_and_leave_out(self):
        nodes = pd.DataFrame({"entity": ["ercot:SUNNY_ALL", "ercot:SUNNY_ALL", "ercot:SPLIT_RN", "ercot:LONE_RN", "ercot:HB_NORTH"],
                              "x_resource_type": ["PVGR", "PVGR", "SCGT", "WIND", ""],
                              "x_class": ["solar", "solar", "gas", "wind", "hub"]})
        units = pd.DataFrame({"x_unit_code": ["SUNNY_UNIT1", "SUNNY_UNIT2", "SPLIT_A", "SPLIT_B", "", "OTHER_1"],
                              "x_county": ["FAYETTE", "FAYETTE", "HARRIS", "BEXAR", "X", "Y"],
                              "x_zone": ["SOUTH", "SOUTH", "HOUSTON", "SOUTH", "X", "Y"]})
        t, c = P.place(nodes, units, "r")
        self.assertEqual(t.entity_id.tolist(), ["ercot_node:SUNNY_ALL"])
        r = t.iloc[0]
        self.assertEqual((r.x_county, r.x_zone, r.x_cdr_units, r.x_cdr_units_n, r.entity_type), ("FAYETTE", "SOUTH", "SUNNY_UNIT1;SUNNY_UNIT2", "2", "generator"))
        self.assertEqual(c, {"nodes": 3, "no unit at the station": 1, "units disagree": 1, "placed": 1})


class Registered(unittest.TestCase):
    def test_sector_holds_and_note(self):
        name = "ercot_node_places"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))
        with open(os.path.join(ROOT, "docs", "methods", "ercot_node_places.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Tables: `ercot_node_places`", text)
        self.assertEqual(text.count(chr(0x2014)) + text.count(chr(0x2013)), 0)


if __name__ == "__main__":
    unittest.main()

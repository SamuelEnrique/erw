"""Session 938: ORNL's hydropower potential at existing non-powered dams (greater than 1 MW).

Energy Research Warehouse (ERW). Tests warehouse/connectors/ornl_npd.py on rows built here in the workbook's form
(figures made up for the test, not ORNL's): the NID id as the id, the potential as capacity, a border dam's geo left
empty with its states kept, the monthly columns passed over; a heading not as read and an id given twice stopping the
run; the sector rule and the holds. No network.

    python -m unittest tests.test_session938 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ornl_npd as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(**kw):
    r = {k: None for k in list(O.FIELDS) + sorted(O.NAMED) + sorted(O.MONTHLY)}
    r.update(nid_id1="KY03042", dmname="RIVER LOCKS & DAM 53", owname="CELRL", state="IL/KY", lat="37.2", lon="-89.0", mw="496.1",
             mwhyr="2084906.6", esth="12", q01="408309.5")
    r.update(kw)
    return r


class Dams(unittest.TestCase):
    def test_shape(self):
        t = O.dams(pd.DataFrame([row(), row(nid_id1="OH00433", state="OH", mw="2.5")], dtype=str), "u", "r", "v").set_index("entity_id")
        a, b = t.loc["ornl_npd:KY03042"], t.loc["ornl_npd:OH00433"]
        self.assertEqual((a.geo, a.state, a.capacity_mw, a.operator, a.head_ft, a.entity_type), ("", "IL/KY", 496.1, "CELRL", 12, "project"))
        self.assertEqual((b.geo, b.capacity_mw), ("US-OH", 2.5))
        self.assertNotIn("q01", t.columns)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            O.dams(pd.DataFrame([dict(row(), extra="x")], dtype=str), "u", "r", "v")
        with self.assertRaises(RuntimeError):
            O.dams(pd.DataFrame([row(), row()], dtype=str), "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "ornl_npd_potential"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

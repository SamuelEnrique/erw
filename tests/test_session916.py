"""Session 916: Oak Ridge National Laboratory's U.S. Hydropower Development Pipeline.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ornl_hydro_pipeline.py on project rows built here in the
workbook's form (figures made up for the test, not ORNL's): the docket as the id and a project without one named by its
slug, ORNL's status kept and mapped to the standard's, the developer as operator; a heading not in the map and an id given
twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session916 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ornl_hydro_pipeline as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(**kw):
    r = {k: None for k in list(P.FIELDS) + sorted(P.NAMED)}
    r.update(FERC_docket="P-15314", Project_name="Test Pumped Storage", Project_type="PSH", Status="Issued Preliminary Permit",
             State="AZ", Latitude="36.9", Longitude="-111.3", Capacity_MW="765", Project_developer="Test LLC")
    r.update(kw)
    return r


class Projects(unittest.TestCase):
    def test_shape(self):
        t = P.projects(pd.DataFrame([row(), row(FERC_docket=None, Project_name="Arnold Coulee Drop", Status="Under Construction", Capacity_MW="2.5")],
                                    dtype=str), "u", "r", "v").set_index("entity_id")
        a, b = t.loc["ornl_hydro_pipeline:P-15314"], t.loc["ornl_hydro_pipeline:none-arnold_coulee_drop"]
        self.assertEqual((a.status, a.permit_status, a.operator, a.capacity_mw, a.geo), ("planned", "Issued Preliminary Permit", "Test LLC", 765, "US-AZ"))
        self.assertEqual((b.status, b.capacity_mw), ("under_construction", 2.5))

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            P.projects(pd.DataFrame([dict(row(), Extra="x")], dtype=str), "u", "r", "v")
        with self.assertRaises(RuntimeError):
            P.projects(pd.DataFrame([row(), row()], dtype=str), "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "ornl_hydropower_pipeline"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

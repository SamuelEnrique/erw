"""Session 939: Berkeley Lab's utility-scale solar projects (Individual_Project_Data).

Energy Research Warehouse (ERW). Tests warehouse/connectors/lbnl_solar_projects.py on rows built here in the sheet's form
(figures made up for the test, not LBNL's): the EIA id kept with its suffix, a project without one named by its slug, the
AC capacity and the operation date, the capacity factors by year; a heading not as read and an id given twice stopping the
run; the sector rule and the holds. No network.

    python -m unittest tests.test_session939 -v
"""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import lbnl_solar_projects as L  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def row(**kw):
    r = {k: None for k in list(L.FIELDS) + sorted(L.NAMED)}
    r.update({"EIA ID": "10437ret", "Project Name": "Solar One", "Solar COD": "1984-12-31 00:00:00", "State": "CA", "Latitude": "34.8",
              "Longitude": "-116.8", "Solar Capacity MW-AC": "13.8", "Solar Tech Main": "CSP", "2024 Capacity Factor": "0.21"})
    r.update(kw)
    return r


class Projects(unittest.TestCase):
    def test_shape(self):
        t = L.projects(pd.DataFrame([row(), row(**{"EIA ID": None, "Project Name": "Davidson County Solar Farm"})], dtype=str), "u", "r", "v").set_index("entity_id")
        a = t.loc["lbnl_solar:10437ret"]
        self.assertEqual((a.capacity_mw, a.status_date, a.geo, a.cf_2024, a.technology), (13.8, "1984-12-31", "US-CA", 0.21, "CSP"))
        self.assertIn("lbnl_solar:none-davidson_county_solar_farm", t.index)

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            L.projects(pd.DataFrame([dict(row(), Extra="x")], dtype=str), "u", "r", "v")
        with self.assertRaises(RuntimeError):
            L.projects(pd.DataFrame([row(), row()], dtype=str), "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        name = "lbnl_solar_projects"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

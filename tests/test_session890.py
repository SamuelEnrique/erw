"""Session 890: USGS's U.S. Large-Scale Solar Photovoltaic Database.

Energy Research Warehouse (ERW). Tests warehouse/connectors/uspvdb.py on records built here in the API's form (figures
made up for the test, not USGS's): the facility as a plant with its AC capacity, the fields renamed with their units, the
image date as a date and as given, a value that is no calendar date left empty and named (never mended), a value not of
eight digits or a case_id given twice stopping the run, the publisher resolving to USGS's verdict, the sector rule and
the holds. No network.

    python -m unittest tests.test_session890 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import uspvdb as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import licenses as L  # noqa: E402


def rec(case_id=1, img=20250129, **k):
    r = {"case_id": case_id, "multi_poly": "single", "eia_id": 67642, "p_state": "IL", "p_county": "Christian", "ylat": 39.56,
         "xlong": -89.27, "p_area": 96477, "p_img_date": img, "p_dig_conf": 4, "p_name": "Skyline", "p_year": 2024,
         "p_pwr_reg": "MISO", "p_tech_pri": "PV", "p_tech_sec": "c-si", "p_axis": "single-axis", "p_azimuth": 180, "p_tilt": 20,
         "p_battery": None, "p_cap_ac": 5.0, "p_cap_dc": 6.5, "p_type": "greenfield", "p_agrivolt": "non-agrivoltaic",
         "p_zscore": -0.1, "p_comm": None, "p_sys_type": "ground"}
    r.update(k)
    return r


class Facilities(unittest.TestCase):
    def test_a_facility(self):
        t = U.facilities([rec(), rec(case_id=2, img=20240231)], "u", "r").set_index("entity_id")
        a = t.loc["uspvdb:1"]
        self.assertEqual((a.entity_type, a.geo, a.capacity_mw, a.capacity_dc_mw, a.eia_plant_id), ("plant", "US-IL", 5.0, "6.5", "67642"))
        self.assertEqual((a.image_date, a.image_date_usgs, a.battery), ("2025-01-29", "20250129", ""))
        b = t.loc["uspvdb:2"]
        self.assertEqual((b.image_date, b.image_date_usgs), ("", "20240231"))
        self.assertEqual(U.facilities([rec(), rec(case_id=2, img=20240231)], "u", "r").attrs["no_date"], ["20240231"])

    def test_what_stops(self):
        with self.assertRaises(RuntimeError):
            U.facilities([rec(), rec()], "u", "r")
        with self.assertRaises(RuntimeError):
            U.facilities([rec(img="2024-02-03")], "u", "r")
        bad = rec()
        del bad["p_cap_ac"]
        with self.assertRaises(RuntimeError):
            U.facilities([bad], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_holds_and_publisher(self):
        name = "uspvdb_solar_facilities"
        self.assertEqual(B.sector_of(name), "power")
        self.assertIn(name, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {name}\n", f.read().replace("\r\n", "\n"))
        self.assertEqual(L.canon("U.S. Geological Survey (USGS), with LBNL"), "U.S. Geological Survey (USGS)")


if __name__ == "__main__":
    unittest.main()

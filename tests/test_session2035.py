"""Session 2035: FHWA's monthly motor fuel volumes by state (DOT DataHub).

Energy Research Warehouse (ERW). Tests warehouse/connectors/fhwa_motor_fuel.py on files built here in the datasets' form
(made up for the test, not FHWA's): the rows written with their data type, a Not Published row and an all-zero month left
out and counted, Puerto Rico and DC kept; a place, a data type or a month not known, a volume not a number and a state
and month given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2035 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import fhwa_motor_fuel as F  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = "STATE,YEAR,MONTH,VOL GASOLINE,DATA TYPE,DATE MODIFIED\n"


def csv(lines):
    return (HEAD + "".join(f"{ln}\n" for ln in lines)).encode()


ROWS = ["Alabama,2026,January,256632119,Actual,12/14/2025 12:00:00 AM", "Georgia,2026,January,3968272,Gas Holiday,12/14/2025 12:00:00 AM",
        "North Carolina,2026,January,0,Not Published,12/14/2025 12:00:00 AM", "Puerto Rico,2026,January,1000,Estimate,12/14/2025 12:00:00 AM",
        "Alabama,2026,February,0,Actual,12/14/2025 12:00:00 AM", "Georgia,2026,February,0,Actual,12/14/2025 12:00:00 AM"]


class Rows(unittest.TestCase):
    def test_rows(self):
        s, unpub, zero, months = F.rows(F.read(csv(ROWS), "gasoline_volume"), "gasoline_volume", BASE)
        s = s.set_index(["entity", "ts_utc"])
        self.assertEqual((unpub, zero, months), (1, 2, ["2026-02"]))
        self.assertEqual(len(s), 3)
        a = s.loc[("fhwa_mf:AL", "2026-01-01T00:00:00Z")]
        self.assertEqual((a.value, a.unit, a.geo, a.x_data_type), ("256632119", "gal", "US-AL", "Actual"))
        self.assertEqual(s.loc[("fhwa_mf:GA", "2026-01-01T00:00:00Z")].x_data_type, "Gas Holiday")
        self.assertEqual(s.loc[("fhwa_mf:PR", "2026-01-01T00:00:00Z")].geo, "US-PR")
        self.assertNotIn(("fhwa_mf:NC", "2026-01-01T00:00:00Z"), s.index)

    def test_stops(self):
        for bad in ("Guam,2026,January,1,Actual,x", "Alabama,2026,Janvier,1,Actual,x", "Alabama,2026,March,1,Revised,x",
                    "Alabama,2026,March,lots,Actual,x", ROWS[0]):
            with self.assertRaises(RuntimeError):
                F.read(csv(ROWS + [bad]), "gasoline_volume")
        with self.assertRaises(RuntimeError):
            F.read(csv(ROWS), "special_fuel_volume")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(F.TABLE), "products")
        self.assertIn(F.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {F.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

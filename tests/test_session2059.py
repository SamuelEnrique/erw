"""Session 2059: the National Hurricane Center's HURDAT2 best tracks.

Energy Research Warehouse (ERW). Tests warehouse/connectors/nhc_hurdat2.py on text built here in HURDAT2's form (a
storm made up for the test, not NHC's): its fixes, a landfall, positions west and south made negative, a missing
pressure; a storm before the start year left out; a header whose count does not match, a status not in the map and a
position that does not read stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2059 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import nhc_hurdat2 as N  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
STORM = ("AL092008,                IKE,      2,\n"
         "20080913, 0700, L, HU, 29.4N,  94.7W,  95,  950,\n"
         "20080913, 1200,  , TS, 30.3N,  95.2W,  55, -999,\n")
OLD = "AL011999,            ARLENE,      1,\n19990611, 1800,  , TS, 31.0S,  60.0E,  50, 1006,\n"


class Parse(unittest.TestCase):
    def test_rows(self):
        rows = N.parse(OLD + STORM, "atlantic", BASE, 2000)
        self.assertEqual(len(rows), 2)
        a, b = rows
        self.assertEqual((a["event_id"], a["event_date"], a["event_type"], a["x_landfall"], a["x_lat"], a["x_lon"], a["x_max_wind_kt"]),
                         ("nhc:AL092008:200809130700", "2008-09-13", "hurricane", "1", 29.4, -94.7, 95))
        self.assertEqual((b["event_type"], b["x_record"], b["x_min_pressure_mb"]), ("tropical_storm", "", ""))
        self.assertEqual(N.parse(OLD, "atlantic", BASE, 1990)[0]["x_lat"], -31.0)

    def test_stops(self):
        for text in (STORM.replace("      2,", "      3,"), STORM.replace(" HU,", " XX,"), STORM.replace("29.4N", "29.4Q")):
            with self.assertRaises(RuntimeError):
                N.parse(text, "atlantic", BASE, 2000)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(N.TABLE), "power;oil;gas")
        self.assertIn(N.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {N.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

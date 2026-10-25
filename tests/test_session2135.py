"""Session 2135: GFZ Potsdam's planetary Kp.

Energy Research Warehouse (ERW). Tests warehouse/connectors/gfz_kp_index.py on a file built here in GFZ's form (made up
for the test, not GFZ's): each interval a row at its start in UTC, Kp in thirds with the unit index, ap and the status
beside it; an interval GFZ marks missing counted, not written; a line of another form, a status not 0 or 1, an interval
off a three-hour boundary and a gap between intervals stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2135 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import gfz_kp_index as K  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = "# LICENSE: CC BY 4.0\n#YYY MM DD hh.h hh._m        days      days_m     Kp   ap D\n"
L1 = "2024 05 10 21.0 22.50 33733.87500 33733.93750  8.667  300 1\n"
L2 = "2024 05 11 00.0 01.50 33734.00000 33734.06250  9.000  400 1\n"
L3 = "2024 05 11 03.0 04.50 33734.12500 33734.18750 -1.000   -1 0\n"
L4 = "2024 05 11 06.0 07.50 33734.25000 33734.31250  4.667   39 0\n"


class Parse(unittest.TestCase):
    def test_rows(self):
        s, head, missing = K.parse(HEAD + L1 + L2 + L3 + L4, BASE)
        self.assertEqual(head[0], "# LICENSE: CC BY 4.0")
        self.assertEqual(missing, 1)
        self.assertEqual(len(s), 3)
        self.assertEqual(list(s.ts_utc), ["2024-05-10T21:00:00Z", "2024-05-11T00:00:00Z", "2024-05-11T06:00:00Z"])
        self.assertEqual(s.value.tolist(), [8.667, 9.0, 4.667])
        self.assertEqual(set(s.unit), {"index"})
        self.assertEqual(s.x_ap.tolist(), ["300", "400", "39"])
        self.assertEqual(s.x_status.tolist(), ["definitive", "definitive", "preliminary"])

    def test_stops(self):
        for bad in (HEAD + "2024 05 10 21.0 8.667\n", HEAD + L1.replace(" 1\n", " 2\n"), HEAD + L1.replace("21.0", "22.0"),
                    HEAD + L1 + L4, HEAD):
            with self.assertRaises(RuntimeError):
                K.parse(bad, BASE)


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(K.TABLE), "power")
        self.assertIn(K.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {K.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

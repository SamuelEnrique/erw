"""Session 2211: Lake Mead and Lake Powell a day (Reclamation's hydrodata).

Energy Research Warehouse (ERW). Tests warehouse/connectors/usbr_colorado_reservoirs.py on files built here in the
hydrodata CSV form (made up for the test, not Reclamation's): each data type as its variable and unit, a day at 00:00Z, a
blank left out, Lake Mead's inflow not asked; a header not the data type's, a date not YYYY-MM-DD, a value that is not a
number and a day given twice stopping the run; the units ft and acre-ft (Decisions 71 and 72), the sector rule and the
holds. No network.

    python -m unittest tests.test_session2211 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import usbr_colorado_reservoirs as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402


class Build(unittest.TestCase):
    def test_rows(self):
        rows = (U.file_rows("datetime,pool elevation\n2026-09-30,3518.08\n2026-10-01,\n", "919", "49", "u", "r", "")
                + U.file_rows("datetime,storage\n2026-09-30,5160000.0\n", "919", "17", "u", "r", "")
                + U.file_rows("datetime,total release\n2026-09-30,9100.0\n", "921", "42", "u", "r", ""))
        t = U.finish(rows)
        e = t[t.variable == "pool_elevation"].iloc[0]
        self.assertEqual((e.entity, e.value, e.unit, e.ts_utc, e.freq), ("usbr_hydrodata:919", 3518.08, "ft", "2026-09-30T00:00:00Z", "P1D"))
        self.assertEqual(t[t.variable == "storage"].iloc[0].unit, "acre-ft")
        self.assertEqual(t[t.variable == "total_release"].iloc[0].unit, "ft3/s")
        self.assertEqual(len(t), 3)
        self.assertIn("29", U.NOT_PUBLISHED["921"])

    def test_stops(self):
        for text, dtype in (("datetime,storage\n2026-09-30,1\n", "49"), ("datetime,pool elevation\n09/30/2026,1\n", "49"),
                            ("datetime,pool elevation\n2026-09-30,high\n", "49")):
            with self.assertRaises(RuntimeError):
                U.file_rows(text, "919", dtype, "u", "r", "")
        with self.assertRaises(RuntimeError):
            U.finish(U.file_rows("datetime,pool elevation\n2026-09-30,1\n2026-09-30,2\n", "919", "49", "u", "r", ""))


class Registered(unittest.TestCase):
    def test_units_sector_and_holds(self):
        self.assertTrue({"ft", "acre-ft", "ft3/s"} <= V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("71. **Session 2211: ft.**", text)
        self.assertIn("72. **Session 2211: acre-ft.**", text)
        self.assertEqual(B.sector_of(U.NAME), "power")
        self.assertIn(U.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

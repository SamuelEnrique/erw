"""Session 2221: Reclamation's Colorado River Storage Project power reservoirs above Lake Powell, a day (hydrodata).

Energy Research Warehouse (ERW). Tests warehouse/connectors/usbr_crsp_reservoirs.py on files built here in Reclamation's
form (made up for the test, not Reclamation's): the day at midnight UTC, the unit by data type, the state by site, a
blank left out; a header not Reclamation's, a date not YYYY-MM-DD, a value that is not a number and a day given twice
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2221 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import usbr_crsp_reservoirs as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


class Rows(unittest.TestCase):
    def test_rows(self):
        rows = U.file_rows("datetime,power release\n2026-10-21,715.11\n2026-10-22,\n", "913", "39", "u", "r", "v")
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["entity"], r["variable"], r["ts_utc"], r["value"], r["unit"], r["geo"], r["node"]),
                         ("usbr_hydrodata:913", "power_release", "2026-10-21T00:00:00Z", 715.11, "ft3/s", "US-CO", "Blue Mesa Reservoir"))
        e = U.file_rows("datetime,pool elevation\n2026-10-22,6005.38\n", "917", "49", "u", "r", "v")[0]
        self.assertEqual((e["unit"], e["geo"]), ("ft", "US-UT"))
        self.assertEqual(U.file_rows("datetime,storage\n2026-10-22,15767.97\n", "915", "17", "u", "r", "v")[0]["unit"], "acre-ft")

    def test_stops(self):
        for text, dtype in (("datetime,storage\n2026-10-22,1\n", "49"), ("datetime,storage\n10/22/2026,1\n", "17"),
                            ("datetime,storage\n2026-10-22,lots\n", "17")):
            with self.assertRaises(RuntimeError):
                U.file_rows(text, "914", dtype, "u", "r", "v")
        twice = U.file_rows("datetime,storage\n2026-10-22,1\n2026-10-22,2\n", "914", "17", "u", "r", "v")
        with self.assertRaises(RuntimeError):
            U.finish(twice)


class PartDay(unittest.TestCase):
    def test_the_day_in_progress_is_left_out(self):
        # session 2218: fetched at 01:35 UTC on 24 October, 18:35 on the 23rd in Arizona, 19:35 in Colorado
        import usbr_colorado_reservoirs as C
        for mod, site in ((C, "921"), (U, "914")):
            rows = mod.file_rows("datetime,total release\n2026-10-22,7527.79\n2026-10-23,4638.2\n", site, "42", "u",
                                 "2026-10-24T01:35:00Z", "v")
            kept, part = mod.ended_days(mod.finish(rows))
            self.assertEqual(list(kept.ts_utc), ["2026-10-22T00:00:00Z"])
            self.assertEqual(list(part.ts_utc), ["2026-10-23T00:00:00Z"])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(U.NAME), "power")
        self.assertIn(U.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

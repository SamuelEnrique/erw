"""Session 2070: the IESO's hourly Ontario demand.

Energy Research Warehouse (ERW). Tests warehouse/connectors/ieso_demand.py on files built here in the IESO's form (made
up for the test, not the IESO's): the report's lines skipped, the hour ending in Eastern Standard Time turned to the
hour's start in UTC, the creation time in UTC; a header not the IESO's, an hour outside 1 to 24 and an hour given twice
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2070 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import ieso_demand as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402

BS = chr(92) * 2
FILE = (f"{BS}Hourly Demand Report,,,\n{BS}Created at 2026-01-31 07:30:13,,,\n{BS}For 2025,,,\n"
        "Date,Hour,Market Demand,Ontario Demand\n2025-07-01,1,17247,13887\n2025-07-01,24,20042,16946\n")


class Build(unittest.TestCase):
    def test_rows(self):
        t, created = D.build([(FILE, "u", "r")])
        t = t.set_index(["variable", "ts_utc"])
        self.assertEqual(t.loc[("ontario_demand", "2025-07-01T05:00:00Z"), "value"], 13887.0)
        self.assertEqual(t.loc[("market_demand", "2025-07-02T04:00:00Z"), "value"], 20042.0)
        self.assertEqual(created["u"], "2026-01-31T12:30:13Z")
        self.assertEqual(set(t.unit), {"MW"})

    def test_stops(self):
        with self.assertRaises(RuntimeError):
            D.build([(FILE.replace("Market Demand", "Demand"), "u", "r")])
        with self.assertRaises(RuntimeError):
            D.build([(FILE.replace("2025-07-01,24,", "2025-07-01,25,"), "u", "r")])
        with self.assertRaises(RuntimeError):
            D.build([(FILE, "u", "r"), (FILE, "v", "r")])


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "power")
        self.assertIn(D.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

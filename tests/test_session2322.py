"""Session 2322: the Department of Statistics Malaysia's electricity supply and consumption a month, by sector (data.gov.my).

Energy Research Warehouse (ERW). Tests warehouse/connectors/dosm_malaysia_electricity.py on files built here in DOSM's
form (made up for the test, not DOSM's): a row a month and sector, million kWh written as MWh, the variable the file and
its sector; a header not DOSM's, a sector not in the map, a date not a month's first day, a value that is not a number
and a month given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2322 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import dosm_malaysia_electricity as D  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402

SUPPLY = "date,sector,supply\n2018-01-01,total,13156.5\n2018-01-01,imports,0.25\n2018-02-01,total,12097.0\n"
USE = "date,sector,consumption\n2018-01-01,local_domestic,2500.0\n2018-01-01,losses,700.5\n"


class Rows(unittest.TestCase):
    def test_rows(self):
        t = D.finish(D.file_rows("supply", SUPPLY, "u", "r", "v") + D.file_rows("consumption", USE, "u2", "r", "v"))
        self.assertEqual(len(t), 5)
        s = t[(t.variable == "supply_total") & (t.ts_utc == "2018-01-01T00:00:00Z")].iloc[0]
        self.assertEqual((s.value, s.unit, s.freq, s.geo, s.entity), (13156500.0, "MWh", "P1M", "MY", "dosm:MY"))
        self.assertEqual(t[t.variable == "supply_imports"].value.iloc[0], 250.0)
        self.assertEqual(set(t.variable), {"supply_total", "supply_imports", "consumption_local_domestic", "consumption_losses"})

    def test_stops(self):
        for kind, text in (("supply", "date,sector,consumption\n2018-01-01,total,1\n"), ("supply", "date,sector,supply\n2018-01-01,exports,1\n"),
                           ("consumption", "date,sector,consumption\n2018-01-15,total,1\n"), ("supply", "date,sector,supply\n2018-01-01,total,n/a\n")):
            with self.assertRaises(RuntimeError):
                D.file_rows(kind, text, "u", "r", "v")
        with self.assertRaises(RuntimeError):
            D.finish(D.file_rows("supply", "date,sector,supply\n2018-01-01,total,1\n2018-01-01,total,2\n", "u", "r", "v"))


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(D.NAME), "power")
        self.assertIn(D.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {D.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

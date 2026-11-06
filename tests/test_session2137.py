"""Session 2137: the Scripps CO2 Program's Mauna Loa CO2.

Energy Research Warehouse (ERW). Tests warehouse/connectors/scripps_co2_mlo.py on a file built here in the Scripps form
(made up for the test, not Scripps'): the quoted header and the three lines of column names skipped; each month's CO2
and its seasonally adjusted value in ppm on the month's first day, the station kept; a value of -99.99 counted, not
written; the fitted and filled columns not taken; a line of another form, a station not MLO or MKO and a file without a
month stopping the run; the unit ppm in the validator and the data standard (Decision 67); the sector rule and the holds.
No network.

    python -m unittest tests.test_session2137 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import scripps_co2_mlo as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
HEAD = ('" Atmospheric CO2 concentrations (ppm)  "\n" Missing values are denoted by -99.99 "\n'
        "  Yr, Mn,    Date,      Date,     CO2,seasonally,        fit,  seasonally,      CO2, seasonally, Sta\n"
        "    ,   ,        ,          ,        ,  adjusted,           ,adjusted fit,   filled,adjusted filled\n"
        "    ,   ,   Excel,          ,   [ppm],    [ppm] ,      [ppm],    [ppm],       [ppm],    [ppm]\n")
L1 = "1958, 03,   21259,  1958.2027,  315.71,   314.43,     316.21,   314.91,     315.71,   314.43, MLO\n"
L2 = "1958, 06,   21351,  1958.4548,  -99.99,   -99.99,     317.28,   315.14,     317.28,   315.14, MLO\n"
L3 = "2023, 01,   44942,  2023.0411,  418.95,   418.40,     419.03,   418.45,     418.95,   418.40, MKO\n"


class Parse(unittest.TestCase):
    def test_rows(self):
        s, missing = C.parse(HEAD + L1 + L2 + L3, BASE)
        self.assertEqual(missing, 2)
        s = s.set_index(["variable", "ts_utc"])
        self.assertEqual(s.loc[("co2", "1958-03-01T00:00:00Z")].value, 315.71)
        self.assertEqual(s.loc[("co2_seasonally_adjusted", "1958-03-01T00:00:00Z")].value, 314.43)
        self.assertEqual(s.loc[("co2", "2023-01-01T00:00:00Z")].x_station, "MKO")
        self.assertEqual(set(s.unit), {"ppm"})
        self.assertNotIn(("co2", "1958-06-01T00:00:00Z"), s.index)
        self.assertEqual(len(s), 4)

    def test_stops(self):
        for bad in (HEAD + "1958, 03, 315.71\n", HEAD + L1.replace("MLO", "SPO"), HEAD):
            with self.assertRaises(RuntimeError):
                C.parse(bad, BASE)


class Registered(unittest.TestCase):
    def test_unit_sector_and_holds(self):
        self.assertIn("ppm", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("67. **Session 2137: ppm.**", f.read())
        self.assertEqual(B.sector_of(C.TABLE), "carbon")
        self.assertIn(C.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

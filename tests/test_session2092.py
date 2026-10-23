"""Session 2092: NOAA CPC's Oceanic Nino Index.

Energy Research Warehouse (ERW). Tests warehouse/connectors/noaa_cpc_oni.py on a file built here in CPC's form (made up
for the test, not CPC's): each season placed on its middle month (DJF in January, NDJ in December of the same YR), the
anomaly and the temperature in degC; a first line not CPC's, a season not one of the twelve, a line of another form and a
season given twice stopping the run; the unit degC in the validator and the data standard (Decision 62); the sector rule
and the holds. No network.

    python -m unittest tests.test_session2092 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
sys.path.append(os.path.join(ROOT, "warehouse", "validate"))
import noaa_cpc_oni as O  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402
import erw_validate as V  # noqa: E402

BASE = {"source": "s", "source_url": "u", "retrieved_at": "r", "vintage": "v"}
TEXT = " SEAS  YR   TOTAL   ANOM\n  DJF 1950  25.01  -1.32\n  NDJ 1950  25.10  -0.90\n  JAS 2026  29.12   2.16\n"


class Parse(unittest.TestCase):
    def test_rows(self):
        s = O.parse(TEXT, BASE).set_index(["variable", "ts_utc"])
        self.assertEqual(s.loc[("oni_anomaly", "1950-01-01T00:00:00Z")].value, -1.32)
        self.assertEqual(s.loc[("oni_anomaly", "1950-12-01T00:00:00Z")].x_season, "NDJ")
        self.assertEqual(s.loc[("nino34_sst", "2026-08-01T00:00:00Z")].value, 29.12)
        self.assertEqual(s.loc[("nino34_sst", "2026-08-01T00:00:00Z")].unit, "degC")
        self.assertEqual(len(s), 6)

    def test_stops(self):
        for bad in ("SEASON YEAR\n  DJF 1950  25.01  -1.32\n", TEXT + "  XYZ 1951  25.0  0.1\n", TEXT + "  DJF 1951  n/a  0.1\n",
                    TEXT + "  DJF 1950  25.01  -1.32\n"):
            with self.assertRaises(RuntimeError):
                O.parse(bad, BASE)


class Registered(unittest.TestCase):
    def test_unit_sector_and_holds(self):
        self.assertIn("degC", V.UNITS)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("62. **Session 2092: degC.**", f.read())
        self.assertEqual(B.sector_of(O.TABLE), "power;gas")
        self.assertIn(O.TABLE, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {O.TABLE}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

"""Session 2292: EIA's LNG storage additions and withdrawals (API v2, natural-gas/stor/lng), a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_lng_storage.py on records built here in EIA's
form (made up for the test, not EIA's): additions and withdrawals in MMcf, the year's 1 January, the geo of the U.S. and a
state, a blank without a row; EIA's net series (not asked), an area not of EIA's forms, a unit not in the map and a key
given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2292 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_lng_storage as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(process="SLW", area="NUS", value="45435", units="MMCF", period="2024"):
    return {"period": period, "duoarea": area, "product": "EPG0", "process": process, "series": f"N_{process}_{area}",
            "series-description": "Natural Gas LNG Storage Withdrawals (MMcf)", "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = P.rows([rec(), rec(process="SLI", area="SMA", value="3876"), rec(area="STX", value=None)], "u", "r")
        self.assertEqual(len(t), 2)
        us = t[t.geo == "US"].iloc[0]
        self.assertEqual((us.variable, us.unit, us.value, us.ts_utc, us.freq), ("withdrawals", "MMcf", 45435.0, "2024-01-01T00:00:00Z", "P1Y"))
        self.assertEqual(t[t.geo == "US-MA"].variable.iloc[0], "additions")

    def test_stops(self):
        for bad in ([rec(process="SAL")], [rec(area="R3FM")], [rec(units="BCF")], [rec(), rec()]):
            with self.assertRaises(RuntimeError):
                P.rows(bad, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(P.NAME), "gas;lng")
        self.assertIn(P.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {P.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

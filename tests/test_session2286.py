"""Session 2286: EIA's crude oil stocks at tank farms and pipelines (API v2, petroleum/stoc/cu).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_crude_tank_farm_stocks.py on records built here in EIA's form
(made up for the test, not EIA's): the two processes as named variables in kbbl, Cushing as US-OK, the month's first day, a blank
without a row; a process, area or unit not in the map and a key given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2286 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_crude_tank_farm_stocks as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(process="STT", value="1489", units="MBBL", area="R10", period="2025-01"):
    return {"period": period, "duoarea": area, "product": "EPC0", "process": process, "series": f"M_{process}_{area}",
            "series-description": "Crude Oil Stocks at Tank Farms and Pipelines (Thousand Barrels)", "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = S.rows([rec(), rec(process="SAE", area="YCUOK", value="20428"), rec(area="R20", value=None)], "u", "r")
        self.assertEqual(len(t), 2)
        r = t[t.variable == "tank_farm_pipeline_stocks"].iloc[0]
        self.assertEqual((r.unit, r.value, r.ts_utc, r.freq, r.geo), ("kbbl", 1489.0, "2025-01-01T00:00:00Z", "P1M", "US"))
        self.assertEqual(t[t.variable == "ending_stocks"].geo.iloc[0], "US-OK")

    def test_stops(self):
        for bad in ([rec(process="SAX")], [rec(area="R31")], [rec(units="MMCF")], [rec(), rec()]):
            with self.assertRaises(RuntimeError):
                S.rows(bad, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "oil")
        self.assertIn(S.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

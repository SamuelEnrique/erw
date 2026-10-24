"""Session 2283: EIA's underground natural gas storage by type (API v2, natural-gas/stor/type), the U.S., a month.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_gas_storage_type.py on records built here in EIA's form
(made up for the test, not EIA's): the eighteen processes as named variables in MMcf, the month's first day, a blank
without a row; a process, area or unit not in the map and a key given twice stopping the run; the sector rule and the
holds. No network.

    python -m unittest tests.test_session2283 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_storage_type as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(process="SSO", value="400000", units="MMCF", area="NUS", period="2025-01"):
    return {"period": period, "duoarea": area, "product": "EPG0", "process": process, "series": f"N5_{process}",
            "series-description": "U.S. storage (MMcf)", "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = S.rows([rec(), rec(process="SNO", value="3000000"), rec(process="SAO", value=None)], "u", "r")
        self.assertEqual(len(t), 2)
        r = t[t.variable == "salt_working_gas"].iloc[0]
        self.assertEqual((r.unit, r.value, r.ts_utc, r.freq, r.geo), ("MMcf", 400000.0, "2025-01-01T00:00:00Z", "P1M", "US"))
        self.assertEqual(len(S.PROCESSES), 18)

    def test_stops(self):
        for bad in ([rec(process="SXX")], [rec(area="R31")], [rec(units="BCF")], [rec(), rec()]):
            with self.assertRaises(RuntimeError):
                S.rows(bad, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(S.NAME), "gas")
        self.assertIn(S.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {S.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

"""Session 2334: EIA's refinery utilization and capacity by PADD and refining district, a month (petroleum/pnp/unc).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_refinery_utilization.py on an answer built here in the
API's form (made up for the test, not EIA's): thousand barrels a day kept as kbbl/d, EIA's percent written as a ratio
(as eia_refinery_weekly), a blank without a row; a process, area or unit not in the maps and a key given twice stopping
the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2334 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_refinery_utilization as U  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(process="YUP", area="R30", units="%", value="93.5", series="MOPUER32"):
    return {"period": "2026-07", "duoarea": area, "process": process, "units": units, "value": value, "series": series,
            "series-description": "Gulf Coast (PADD 3) Percent Utilization of Refinery Operable Capacity"}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = U.rows([rec(), rec("YRL", "R2A", "MBBL/D", "3800", "MOCLERI2A2"), rec(value="", series="MOPUER32X")], "u", "r")
        self.assertEqual(len(t), 2)
        u = t[t.variable == "utilization"].iloc[0]
        self.assertAlmostEqual(u.value, 0.935)
        self.assertEqual((u.unit, u.freq, u.ts_utc, u.geo), ("ratio", "P1M", "2026-07-01T00:00:00Z", "US"))
        c = t[t.variable == "operable_capacity"].iloc[0]
        self.assertEqual((c.value, c.unit, c.entity), (3800.0, "kbbl/d", "eia_refinery_utilization:MOCLERI2A2"))

    def test_stops(self):
        for r in (rec(process="YXX"), rec(area="R9Z"), rec(units="MBBL")):
            with self.assertRaises(RuntimeError):
                U.rows([r], "u", "r")
        with self.assertRaises(RuntimeError):
            U.rows([rec(), rec()], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(U.NAME), "oil;products")
        self.assertIn(U.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {U.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

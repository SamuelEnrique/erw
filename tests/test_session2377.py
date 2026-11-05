"""Session 2377: EIA's natural gas delivered for the account of others, by state and sector, a year (natural-gas/cons/acct).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_gas_for_others.py on an answer built here in the API's form
(made up for the test, not EIA's): MMcf kept, EIA's percent written as a ratio, a state's geo, a blank without a row; a
process, area or unit not in the maps, a period not a year and a key given twice stopping the run; the sector rule and
the holds. No network.

    python -m unittest tests.test_session2377 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_for_others as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(process="VF8", area="SNY", units="MMCF", value="1500", series="NA1532_SNY_2", period="2024"):
    return {"period": period, "duoarea": area, "process": process, "units": units, "value": value, "series": series,
            "series-description": "New York Natural Gas Delivered to Commercial Consumers for the Account of Others (MMcf)"}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = G.rows([rec(), rec("VF6", "NUS", "%", "47.2", "NA1532_NUS_8"), rec(value="", series="X")], "u", "r")
        self.assertEqual(len(t), 2)
        a = t[t.variable == "commercial_for_others"].iloc[0]
        self.assertEqual((a.value, a.unit, a.geo, a.freq, a.ts_utc), (1500.0, "MMcf", "US-NY", "P1Y", "2024-01-01T00:00:00Z"))
        s = t[t.variable == "commercial_share"].iloc[0]
        self.assertAlmostEqual(s.value, 0.472)
        self.assertEqual((s.unit, s.geo), ("ratio", "US"))

    def test_stops(self):
        for r in (rec(process="VXX"), rec(area="SZZ"), rec(units="BCF"), rec(period="2024-01")):
            with self.assertRaises(RuntimeError):
                G.rows([r], "u", "r")
        with self.assertRaises(RuntimeError):
            G.rows([rec(), rec()], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(G.NAME), "gas")
        self.assertIn(G.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

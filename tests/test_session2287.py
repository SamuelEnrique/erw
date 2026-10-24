"""Session 2287: EIA's natural gas plant processing (API v2, natural-gas/prod/pp), a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_gas_plant_processing.py on records built here in EIA's
form (made up for the test, not EIA's): the three processes as named variables in MMcf or kbbl, the year's 1 January, the
geo of the U.S., a state, a pair (its first state) and an R area, a blank without a row; a process, an area not of EIA's
forms, a unit not in the map and a key given twice stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2287 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_plant_processing as P  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(process="YGP", area="NUS", value="27088079", units="MMCF", period="2024"):
    return {"period": period, "duoarea": area, "product": "EPG0", "process": process, "series": f"N_{process}_{area}",
            "series-description": "Natural Gas Processed (Million Cubic Feet)", "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = P.rows([rec(), rec(process="YGT", area="STX", value="1000", units="MBBL"), rec(area="SKS-SOK", value="5"),
                    rec(area="R3FM", value="7"), rec(area="SNM", value=None)], "u", "r")
        self.assertEqual(len(t), 4)
        us = t[t.entity == "eia_gas_plant_processing:N_YGP_NUS"].iloc[0]
        self.assertEqual((us.variable, us.unit, us.geo, us.ts_utc, us.freq), ("gas_processed", "MMcf", "US", "2024-01-01T00:00:00Z", "P1Y"))
        self.assertEqual(t[t.entity.str.endswith("STX")].iloc[0].unit, "kbbl")
        self.assertEqual(t[t.entity.str.endswith("SKS-SOK")].geo.iloc[0], "US-KS")
        self.assertEqual(t[t.entity.str.endswith("R3FM")].geo.iloc[0], "US")

    def test_stops(self):
        for bad in ([rec(process="VGX")], [rec(area="Texas")], [rec(units="BCF")], [rec(), rec()]):
            with self.assertRaises(RuntimeError):
                P.rows(bad, "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(P.NAME), "gas;products")
        self.assertIn(P.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {P.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

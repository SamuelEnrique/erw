"""Session 2250: EIA's shale gas proved reserves and their changes (API v2, natural-gas/enr/shalegas), 2007 to 2021.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_shale_gas_reserves.py on records built here in EIA's
form (made up for the test, not EIA's): the processes as named variables in bcf, the year's 1 January, the geo of the
U.S., a state and a district, a blank without a row; a process, area or unit not in the map and a key given twice
stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2250 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_shale_gas_reserves as S  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(area="NUS", process="R5301", value="393779", units="BCF", period="2021"):
    return {"period": period, "duoarea": area, "product": "EPG0", "process": process, "series": f"RES_EPG0_{process}_{area}_BCF",
            "series-description": "Shale Proved Reserves (Billion Cubic Feet)", "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = S.rows([rec(), rec(area="SPA", value="100"), rec(area="RTX07C", process="R5302", value="12"),
                    rec(area="R48", value=None)], "u", "r")
        self.assertEqual(len(t), 3)
        us = t[t.geo == "US"].iloc[0]
        self.assertEqual((us.variable, us.unit, us.value, us.ts_utc, us.freq), ("proved_reserves", "bcf", 393779.0, "2021-01-01T00:00:00Z", "P1Y"))
        self.assertEqual(t[t.entity.str.contains("_SPA_")].geo.iloc[0], "US-PA")
        d = t[t.entity.str.contains("RTX07C")].iloc[0]
        self.assertEqual((d.geo, d.variable), ("US-TX", "reserves_based_production"))
        self.assertEqual((S.GEO_OF("RUSF"), S.GEO_OF("RLAN"), S.GEO_OF("SWV")), ("US", "US-LA", "US-WV"))

    def test_stops(self):
        for bad in ([rec(process="R9999")], [rec(area="SXX")], [rec(units="MMCF")], [rec(), rec()]):
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

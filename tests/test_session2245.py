"""Session 2245: EIA's heat content of natural gas delivered to consumers (API v2, natural-gas/cons/heat), and Decision 74
(Btu/ft3).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_gas_heat_content.py on records built here in EIA's form
(made up for the test, not EIA's): heat_content in Btu/ft3, the U.S. as geo US and a state's S<code> as US-<code>, DC
among them, a blank without a row; a process, area or unit not in the map and a key given twice stopping the run;
Btu/ft3 in the validator's vocabulary and the data standard; the sector rule and the holds. No network.

    python -m unittest tests.test_session2245 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_heat_content as H  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(area="NUS", value="1039", units="BTU/CF", process="VGTH", period="2025-01"):
    return {"period": period, "duoarea": area, "product": "EPG0", "process": process, "series": f"NGA_EPG0_VGTH_{area}_BTUCF",
            "series-description": "Heat Content of Natural Gas Deliveries to Consumers (BTU per Cubic Foot)", "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = H.rows([rec(), rec(area="STX", value="1028"), rec(area="SDC", value=None)], "u", "r")
        self.assertEqual(len(t), 2)
        us = t[t.geo == "US"].iloc[0]
        self.assertEqual((us.variable, us.unit, us.value, us.ts_utc), ("heat_content", "Btu/ft3", 1039.0, "2025-01-01T00:00:00Z"))
        self.assertEqual(t[t.entity == "eia_gas_heat_content:NGA_EPG0_VGTH_STX_BTUCF"].geo.iloc[0], "US-TX")
        self.assertIn("SDC", H.AREAS)
        self.assertEqual(len(H.AREAS), 52)

    def test_stops(self):
        for bad in ([rec(process="VGT")], [rec(area="SPR")], [rec(units="MMBTU")], [rec(), rec()]):
            with self.assertRaises(RuntimeError):
                H.rows(bad, "u", "r")


class Decision74(unittest.TestCase):
    def test_unit_in_vocabulary_and_standard(self):
        with open(os.path.join(ROOT, "warehouse", "validate", "erw_validate.py"), encoding="utf-8") as f:
            self.assertIn('"Btu/ft3"', f.read())
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("74. **Session 2245: Btu/ft3.**", f.read())


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(H.NAME), "gas")
        self.assertIn(H.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {H.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

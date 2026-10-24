"""Session 2244: EIA's crude oil input qualities at refineries (API v2, petroleum/pnp/crq), and Decision 73 (degAPI).

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_crude_quality.py on records built here in EIA's form
(made up for the test, not EIA's): the two processes as api_gravity in degAPI and sulfur_content in pct, a blank without
a row; a process, area or unit not in the map and a key given twice stopping the run; degAPI in the validator's
vocabulary and the data standard; the sector rule and the holds. No network.

    python -m unittest tests.test_session2244 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_crude_quality as Q  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def rec(process="YCG", units="D", area="NUS", value="33.07", series="MCRAPUS2", period="2025-01"):
    return {"period": period, "duoarea": area, "product": "EPC0", "process": process, "series": series,
            "series-description": "U.S. API Gravity (Weighted Average) of Crude Oil Input to Refineries (Degrees)",
            "value": value, "units": units}


class Rows(unittest.TestCase):
    def test_rows(self):
        t = Q.rows([rec(), rec(process="YCS", units="%", value="1.30", series="MCRSCUS2"), rec(value=None, period="2025-02")], "u", "r")
        self.assertEqual(len(t), 2)
        g = t[t.variable == "api_gravity"].iloc[0]
        self.assertEqual((g.unit, g.value, g.ts_utc, g.freq, g.entity), ("degAPI", 33.07, "2025-01-01T00:00:00Z", "P1M", "eia_crude_quality:MCRAPUS2"))
        self.assertEqual(t[t.variable == "sulfur_content"].iloc[0].unit, "pct")

    def test_stops(self):
        for bad in ([rec(process="YIR")], [rec(area="R9X")], [rec(units="kg")], [rec(), rec()]):
            with self.assertRaises(RuntimeError):
                Q.rows(bad, "u", "r")


class Decision73(unittest.TestCase):
    def test_unit_in_vocabulary_and_standard(self):
        src = open(os.path.join(ROOT, "warehouse", "validate", "erw_validate.py"), encoding="utf-8").read()
        self.assertIn('"degAPI"', src)
        with open(os.path.join(ROOT, "docs", "datastandard.md"), encoding="utf-8") as f:
            self.assertIn("73. **Session 2244: degAPI.**", f.read())


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(Q.NAME), "oil")
        self.assertIn(Q.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {Q.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

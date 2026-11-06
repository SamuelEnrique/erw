"""Sessions 551 and 552: EIA's crude oil and dry natural gas proved reserves by state. Held on real records (the U.S.,
2021): crude's million barrels as kbbl, gas's billion cubic feet as bcf, the process as a word, an unknown process stops;
both tables are held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_crude_reserves as C  # noqa: E402
import eia_gas_reserves as G  # noqa: E402
import release_v1 as R  # noqa: E402

CRUDE = {"period": "2021", "duoarea": "NUS", "process": "R01", "series": "RCRR01NUS_1",
         "series-description": "U.S. Crude Oil Proved Reserves (Million Barrels)", "value": "41151", "units": "MMBBL"}
GAS = {"period": "2021", "duoarea": "NUS", "process": "R13", "series": "RNGR13NUS_1",
       "series-description": "U.S. Dry Natural Gas Reserves Revision Increases (Billion Cubic Feet)", "value": "136433", "units": "BCF"}


class TheRows(unittest.TestCase):
    def test_crude(self):
        r = C.rows([CRUDE], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["geo"]), ("eia_crude_reserves:R01:NUS", "proved_reserves", 41151000.0, "kbbl", "US"))
        self.assertEqual(C.geo_of("STX"), "US-TX")
        self.assertEqual(C.geo_of("RTX01"), "US")

    def test_gas(self):
        r = G.rows([GAS], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"]), ("eia_gas_reserves:R13:NUS", "revision_increases", 136433.0, "bcf"))

    def test_an_unknown_process_stops(self):
        with self.assertRaises(RuntimeError):
            C.rows([dict(CRUDE, process="R99")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        for t in ("eia_crude_reserves_annual", "eia_gas_reserves_annual"):
            self.assertIn(f"  - {t}\n", y[y.index("catalogue_hold:"):])
            self.assertIn(f"upload.py {t}", R.STORAGE_HELD[t])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_crude_reserves.py", "warehouse/connectors/eia_gas_reserves.py", "tests/test_session551.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

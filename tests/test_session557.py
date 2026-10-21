"""Session 557: EIA's natural gas supply and disposition by state, a year. Held on a record's form (2024): the process as
a word, MMcf kept, a state's geo, an unknown process stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_balance as B  # noqa: E402
import release_v1 as R  # noqa: E402

REC = {"period": "2024", "duoarea": "STX", "process": "VC0", "series": "N9140TX2",
       "series-description": "Texas Natural Gas Total Consumption (MMcf)", "value": "5000000", "units": "MMCF"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = B.rows([REC], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["geo"], r["ts_utc"]),
                         ("eia_gas_balance:VC0:STX", "total_consumption", 5000000.0, "MMcf", "US-TX", "2024-01-01T00:00:00Z"))

    def test_ten_processes_and_an_unknown_one_stops(self):
        self.assertEqual(len(B.PROCESSES), 10)
        with self.assertRaises(RuntimeError):
            B.rows([dict(REC, process="VGM")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_balance_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_balance_annual", R.STORAGE_HELD["eia_gas_balance_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_balance.py", "tests/test_session557.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

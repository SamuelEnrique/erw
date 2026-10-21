"""Session 556: EIA's petroleum products supplied, every product, a month. Held on a real record's form (June 2026, the
U.S. total): product supplied in kbbl and kbbl/d, only EIA's process VPP and its six areas; the table is held from /data
and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_product_supplied as P  # noqa: E402
import release_v1 as R  # noqa: E402

DAY = {"period": "2026-06", "duoarea": "NUS", "product": "EP00", "process": "VPP", "series": "MTTUPUS2",
       "series-description": "U.S. Product Supplied of Crude Oil and Petroleum Products (Thousand Barrels per Day)", "value": "20736", "units": "MBBL/D"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = P.rows([DAY], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"]),
                         ("eia_product_supplied:MTTUPUS2", "product_supplied_per_day", 20736.0, "kbbl/d", "2026-06-01T00:00:00Z"))

    def test_only_product_supplied_and_six_areas(self):
        self.assertEqual(P.PROCESSES, {"VPP": "product_supplied"})
        with self.assertRaises(RuntimeError):
            P.rows([dict(DAY, process="SCG")], "u", "r")
        with self.assertRaises(RuntimeError):
            P.rows([dict(DAY, duoarea="R10-Z0P")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_product_supplied_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_product_supplied_monthly", R.STORAGE_HELD["eia_product_supplied_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_product_supplied.py", "tests/test_session556.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

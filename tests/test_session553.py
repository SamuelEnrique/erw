"""Session 553: EIA's average delivered price of coal by state or region and sector. Held on a real record (the
Pacific division, electric utilities, 2024): USD/short_ton kept, a division's geo is US, a state's is its own, an unknown
unit stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_coal_delivered_price as D  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2024", "location": "90", "stateDescription": "Pacific", "sector": "1", "sectorDescription": "Electric Utility",
        "price": "64.84", "price-units": "dollars per short ton"}


class TheRows(unittest.TestCase):
    def test_rows(self):
        r = D.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["geo"], r["node"]),
                         ("eia_coal_delivered:90:1", "price", 64.84, "USD/short_ton", "US", "Pacific, Electric Utility"))
        self.assertEqual(D.rows([dict(REAL, location="WY", stateDescription="Wyoming")], "u", "r").iloc[0]["geo"], "US-WY")

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            D.rows([dict(REAL, **{"price-units": "dollars per metric ton"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_coal_delivered_price_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_coal_delivered_price_annual", R.STORAGE_HELD["eia_coal_delivered_price_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_coal_delivered_price.py", "tests/test_session553.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

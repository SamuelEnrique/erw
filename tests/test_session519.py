"""Session 519: EIA's coal market sales price by producing state or region and market type, a year.

Energy Research Warehouse (ERW). Held on real records of EIA's API (2001: Alabama's open market, Central Appalachia's
captive market): USD/short_ton kept, a state's geo and a region's, a withheld price with no row, an unknown unit or a key
given twice stops the run; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_coal_prices as C  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = [
    {"period": 2001, "stateRegionId": "AL", "stateRegionDescription": "Alabama", "marketTypeId": "OM", "marketTypeDescription": "Open Market", "price": "34.36", "price-units": "dollars per short ton"},
    {"period": 2001, "stateRegionId": "APC", "stateRegionDescription": "Appalachia Central", "marketTypeId": "CAP", "marketTypeDescription": "Captive", "price": "29.12", "price-units": "dollars per short ton"},
    {"period": 2001, "stateRegionId": "AK", "stateRegionDescription": "Alaska", "marketTypeId": "CAP", "marketTypeDescription": "Captive", "price": None, "price-units": "dollars per short ton"},
]


class TheRows(unittest.TestCase):
    def setUp(self):
        self.t = C.rows(REAL, "https://api.eia.gov/v2/coal/market-sales-price/data/", "2026-10-21T20:20:00Z").set_index("entity")

    def test_rows(self):
        self.assertEqual(sorted(self.t.index), ["eia_coal_price:AL:OM", "eia_coal_price:APC:CAP"])
        a = self.t.loc["eia_coal_price:AL:OM"]
        self.assertEqual((a["value"], a["unit"], a["geo"], a["ts_utc"], a["freq"], a["node"]),
                         (34.36, "USD/short_ton", "US-AL", "2001-01-01T00:00:00Z", "P1Y", "Alabama Open Market"))
        self.assertEqual(self.t.loc["eia_coal_price:APC:CAP", "geo"], "US")

    def test_unknown_unit_or_key_twice_stops(self):
        with self.assertRaises(RuntimeError):
            C.rows([dict(REAL[0], **{"price-units": "dollars per metric ton"})], "u", "r")
        with self.assertRaises(RuntimeError):
            C.rows([REAL[0], REAL[0]], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_coal_prices_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_coal_prices_annual", R.STORAGE_HELD["eia_coal_prices_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_coal_prices.py", "tests/test_session519.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

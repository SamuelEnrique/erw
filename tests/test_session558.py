"""Session 558: EIA's densified biomass (wood pellets). Held on real records' form (January 2016): the route's short name
and the region in the entity, the domestic price in USD/short_ton, plants and employees as counts, an unknown unit stops;
the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_wood_pellets as W  # noqa: E402
import release_v1 as R  # noqa: E402

SALES = {"period": "2016-01", "region": "SOUTH", "average-price": "130.33", "average-price-units": "USD per ton", "quantity": "1", "quantity-units": "tons"}
CAP = {"period": "2016-01", "region": "US-TOTAL", "number-of-facilities": "86", "number-of-facilities-units": "number of facilities",
       "number-of-fte-employees": "2500", "number-of-fte-employees-units": "number of fte employees"}


class TheRows(unittest.TestCase):
    def test_a_price(self):
        r = W.rows("sales-and-price-by-region", [SALES], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"]),
                         ("eia_wood_pellets:sales:SOUTH", "domestic_price", 130.33, "USD/short_ton", "2016-01-01T00:00:00Z"))

    def test_counts(self):
        t = W.rows("capacity-by-region", [CAP], "u", "r").set_index("variable")
        self.assertEqual((t.loc["facilities", "value"], t.loc["facilities", "unit"]), (86.0, "count"))
        self.assertEqual(t.loc["fte_employees", "unit"], "count")

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            W.rows("sales-and-price-by-region", [dict(SALES, **{"average-price-units": "USD per tonne"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_wood_pellets_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_wood_pellets_monthly", R.STORAGE_HELD["eia_wood_pellets_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_wood_pellets.py", "tests/test_session558.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

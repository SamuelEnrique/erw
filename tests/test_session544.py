"""Session 544: EIA's state electricity supply and disposition. Held on a real record (Alaska, 2024): each column a
variable with "-" as "_", MWh and the net trade index's ratio kept, a column's unknown unit stops; the table is held from
/data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_state_disposition as D  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2024", "state": "AK", "stateDescription": "Alaska", "total-net-generation": "6690506", "total-net-generation-units": "megawatthours",
        "net-trade-index": "1", "net-trade-index-units": "ratio", "estimated-losses": "282127", "estimated-losses-units": "megawatthours"}


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = D.rows([REAL], "u", "r").set_index("variable")
        self.assertEqual(sorted(t.index), ["estimated_losses", "net_trade_index", "total_net_generation"])
        g = t.loc["total_net_generation"]
        self.assertEqual((g["entity"], g["value"], g["unit"], g["geo"], g["ts_utc"]), ("eia_state_disposition:AK", 6690506.0, "MWh", "US-AK", "2024-01-01T00:00:00Z"))
        self.assertEqual(t.loc["net_trade_index", "unit"], "ratio")

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            D.rows([dict(REAL, **{"estimated-losses-units": "thousand megawatthours"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_state_source_disposition_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_state_source_disposition_annual", R.STORAGE_HELD["eia_state_source_disposition_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_state_disposition.py", "tests/test_session544.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

"""Session 545: EIA's net-metered capacity and customers by state. Held on a real record (Alaska, commercial, 2024): the
technology as a slug, MW and count kept, an unknown unit stops; the table is held from /data and Redivis v1 until
uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_net_metering as N  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2024", "state": "AK", "stateName": "Alaska", "technology": "All Technologies", "sector": "COM", "sectorName": "commercial",
        "capacity": "2.646", "customers": "242", "capacity-units": "megawatts", "customers-units": "number of customers"}


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = N.rows([REAL], "u", "r").set_index("variable")
        c = t.loc["capacity"]
        self.assertEqual((c["entity"], c["value"], c["unit"], c["geo"], c["node"]),
                         ("eia_net_metering:AK:all_technologies:COM", 2.646, "MW", "US-AK", "Alaska, All Technologies, commercial"))
        self.assertEqual((t.loc["customers", "value"], t.loc["customers", "unit"]), (242.0, "count"))

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            N.rows([dict(REAL, **{"capacity-units": "kilowatts"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_net_metering_state_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_net_metering_state_annual", R.STORAGE_HELD["eia_net_metering_state_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_net_metering.py", "tests/test_session545.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

"""Session 526: EIA's state electricity profiles, net summer capacity. Held on real records (Alaska, 1990): the entity
names state, producer type and source, MW kept, an unknown unit stops; the table is held from /data and Redivis v1 until
uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_state_capacity as C  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(src, desc, mw):
    return {"period": "1990", "stateId": "AK", "stateDescription": "Alaska", "producertypeid": "EU", "producerTypeDescription": "Electric Utilities",
            "energysourceid": src, "energySourceDescription": desc, "capability": mw, "capability-units": "megawatts"}


REAL = [rec("ALL", "All", "1547"), rec("COL", "Coal", "56"), rec("HYC", "Hydroelectric", "236")]


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = C.rows(REAL, "u", "r").set_index("entity")
        r = t.loc["eia_state_capacity:AK:EU:COL"]
        self.assertEqual((r["variable"], r["value"], r["unit"], r["geo"], r["ts_utc"], r["node"]),
                         ("net_summer_capacity", 56.0, "MW", "US-AK", "1990-01-01T00:00:00Z", "Alaska, Electric Utilities, Coal"))

    def test_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            C.rows([dict(REAL[0], **{"capability-units": "gigawatts"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_state_capacity_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_state_capacity_annual", R.STORAGE_HELD["eia_state_capacity_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_state_capacity.py", "tests/test_session526.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

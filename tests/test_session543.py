"""Session 543: EIA's weekly refinery inputs and utilization. Held on real records (the week ending 4 September 2026):
utilization's percent as a ratio, thousand barrels a day as kbbl/d, the week-ending date as ts_utc, an unknown unit or area
stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_refinery_weekly as W  # noqa: E402
import release_v1 as R  # noqa: E402

UTIL = {"period": "2026-09-04", "duoarea": "NUS", "process": "YUP", "series": "WPULEUS3",
        "series-description": "U.S. Percent Utilization of Refinery Operable Capacity", "value": "97.8", "units": "%"}
CAP = dict(UTIL, process="YRL", series="WOCLEUS2", **{"series-description": "U.S. Operable Crude Oil Distillation Capacity", "value": "18374", "units": "MBBL/D"})


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = W.rows([UTIL, CAP], "u", "r").set_index("entity")
        u = t.loc["eia_refinery:WPULEUS3"]
        self.assertEqual((u["variable"], u["unit"], u["ts_utc"], u["freq"]), ("utilization", "ratio", "2026-09-04T00:00:00Z", "P1W"))
        self.assertAlmostEqual(u["value"], 0.978)
        self.assertEqual((t.loc["eia_refinery:WOCLEUS2", "unit"], t.loc["eia_refinery:WOCLEUS2", "value"]), ("kbbl/d", 18374.0))

    def test_an_unknown_unit_or_area_stops(self):
        for bad in (dict(UTIL, units="MBBL"), dict(UTIL, duoarea="SCA")):
            with self.assertRaises(RuntimeError):
                W.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_refinery_weekly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_refinery_weekly", R.STORAGE_HELD["eia_refinery_weekly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_refinery_weekly.py", "tests/test_session543.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

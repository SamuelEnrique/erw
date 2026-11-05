"""Session 614: EIA's refinery capacity. Held on real records (U.S. atmospheric crude distillation capacity as of 1
January 2025, per calendar day and per stream day; Puerto Rico's idle refineries): barrels a day to kbbl/d, January 1
as ts_utc, a territory's geo, an unknown area or unit stops; the table is held from /data and Redivis v1 until
uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_refinery_capacity as C  # noqa: E402
import release_v1 as R  # noqa: E402

CD = {"period": "2025", "duoarea": "NUS", "product": "(NA)", "process": "8D0", "series": "8_NA_8D0_NUS_4",
      "series-description": "U.S. Operable Crude Oil Distillation Capacity as of January 1", "value": "18423493", "units": "B/CD"}
PR = {"period": "2025", "duoarea": "NPZ", "area-name": "PRI", "product": "(NA)", "process": "8OI", "series": "8_NA_8OI_NPZ_C",
      "series-description": "Puerto Rico Number of Idle Refineries as of January 1 (Count)", "value": "0", "units": "COUNT"}


class TheRows(unittest.TestCase):
    def test_calendar_and_stream_days(self):
        t = C.rows([CD, dict(CD, series="8_NA_8D0_NUS_5", units="B/SD", value="19494042")], "u", "r")
        self.assertEqual(list(t["variable"]), ["capacity_per_calendar_day", "capacity_per_stream_day"])
        self.assertEqual(list(t["value"]), [18423.493, 19494.042])
        self.assertEqual((t.iloc[0]["unit"], t.iloc[0]["ts_utc"], t.iloc[0]["freq"], t.iloc[0]["geo"]),
                         ("kbbl/d", "2025-01-01T00:00:00Z", "P1Y", "US"))

    def test_a_territory_and_a_state(self):
        t = C.rows([PR, dict(PR, duoarea="STX", series="8_NA_8OI_STX_C")], "u", "r")
        self.assertEqual(list(t["geo"]), ["US-PR", "US-TX"])
        self.assertEqual((t.iloc[0]["variable"], t.iloc[0]["unit"]), ("refineries", "count"))

    def test_an_unknown_area_or_unit_stops(self):
        for bad in (dict(CD, duoarea="Z99"), dict(CD, units="B/D")):
            with self.assertRaises(RuntimeError):
                C.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_refinery_capacity_annual\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_refinery_capacity_annual", R.STORAGE_HELD["eia_refinery_capacity_annual"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_refinery_capacity.py", "tests/test_session614.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

"""Session 602: EIA-930's demand by sub-region, hourly. Held on a real record (Basin Electric under Black Hills, the hour
ending 23:00 UTC on 19 October 2026): the hour's start as ts_utc (EIA's hour-ending period less one hour, as
eia930.py), megawatthours in the hour as MW, the window of whole UTC days; the table is held from /data and Redivis v1
until uploaded.
"""

import datetime as dt
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia930_subba as S  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-10-19T23", "subba": "BASI", "subba-name": "Basin Electric Power Cooperative", "parent": "BHBA",
        "parent-name": "Black Hills Energy", "value": "231", "value-units": "megawatthours"}


class TheRows(unittest.TestCase):
    def test_the_hour_start(self):
        r = S.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"], r["freq"]),
                         ("eia930_subba:BHBA:BASI", "demand_mw", 231.0, "MW", "2026-10-19T22:00:00Z", "PT1H"))

    def test_the_window(self):
        self.assertEqual(S.window(90, dt.date(2026, 10, 22)), ("2026-07-24T01", "2026-10-22T00"))

    def test_an_unknown_unit_stops(self):
        with self.assertRaises(RuntimeError):
            S.rows([dict(REAL, **{"value-units": "megawatts"})], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia930_subba_demand_hourly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia930_subba_demand_hourly", R.STORAGE_HELD["eia930_subba_demand_hourly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia930_subba.py", "tests/test_session602.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

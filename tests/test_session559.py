"""Session 559: EIA's petroleum product stocks, a month. Held on a real record (June 2026, New England's distillate):
ending stocks in kbbl, PADD 1's sub-districts accepted, an unknown process or area stops; the table is held from /data and
Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_petroleum_stocks as S  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-06", "duoarea": "R1X", "product": "EPD0", "process": "SAE", "series": "MDIST1A1",
        "series-description": "New England (PADD 1A) Ending Stocks of Distillate Fuel Oil (Thousand Barrels)", "value": "5212", "units": "MBBL"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = S.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"]),
                         ("eia_petroleum_stocks:MDIST1A1", "ending_stocks", 5212.0, "kbbl", "2026-06-01T00:00:00Z"))

    def test_an_unknown_process_or_area_stops(self):
        for bad in (dict(REAL, process="VPP"), dict(REAL, duoarea="SCA")):
            with self.assertRaises(RuntimeError):
                S.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_petroleum_stocks_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_petroleum_stocks_monthly", R.STORAGE_HELD["eia_petroleum_stocks_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_petroleum_stocks.py", "tests/test_session559.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

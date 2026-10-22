"""Session 622: EIA's movements between PADDs by rail and by tanker and barge. Held on a real record (PADD 1's receipts
of crude oil by rail from PADD 2, January 2026): kbbl kept, EIA's area pair in the series, a process of the other
route or an area pair not understood stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_padd_movements as M  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-01", "duoarea": "R10-R20", "area-name": "PADD 2", "product": "EPC0", "product-name": "Crude Oil",
        "process": "RAIL", "process-name": "Receipts by Rail", "series": "ESM_EPC0_RAIL_R10-R20_MBBL",
        "series-description": "East Coast (PADD 1) Receipts by Rail from Midwest (PADD 2) of Crude Oil (Thousand Barrels)",
        "value": "320", "units": "MBBL"}


class TheRows(unittest.TestCase):
    def test_a_row(self):
        r = M.rows([REAL], "u", "r", "petroleum/move/rail").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"], r["source"]),
                         ("eia_padd_movements:ESM_EPC0_RAIL_R10-R20_MBBL", "rail_receipts", 320.0, "kbbl",
                          "2026-01-01T00:00:00Z", "eia:petroleum/move/rail"))

    def test_a_subdistrict_by_barge(self):
        r = M.rows([dict(REAL, process="BMV", duoarea="R1X-R30", series="MTTMT1XP31")], "u", "r", "petroleum/move/tb").iloc[0]
        self.assertEqual(r["variable"], "tanker_barge_receipts")

    def test_the_other_route_or_an_unknown_pair_stops(self):
        for bad, route in ((REAL, "petroleum/move/tb"), (dict(REAL, duoarea="R10"), "petroleum/move/rail")):
            with self.assertRaises(RuntimeError):
                M.rows([bad], "u", "r", route)

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_padd_rail_barge_movements_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_padd_rail_barge_movements_monthly", R.STORAGE_HELD["eia_padd_rail_barge_movements_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_padd_movements.py", "tests/test_session622.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

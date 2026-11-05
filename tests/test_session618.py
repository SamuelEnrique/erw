"""Session 618: EIA's refinery and blender net production, a month. Held on a real record's form (the
Indiana-Illinois-Kentucky refining district, March 2026): kbbl and kbbl/d kept, a negative net production kept as EIA
gives it, an unknown process stops; the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_refinery_production as P  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-03", "duoarea": "R2A", "product": "EPLLBAN", "process": "YPR", "series": "M_EPLLBAN_YPR_R2A_MBBL",
        "series-description": "Refining District Indiana-Illinois-Kentucky Refinery and Blender Net Production of Normal Butane (Thousand Barrels)",
        "value": "-120", "units": "MBBL"}


class TheRows(unittest.TestCase):
    def test_a_negative_kept(self):
        r = P.rows([REAL], "u", "r").iloc[0]
        self.assertEqual((r["entity"], r["variable"], r["value"], r["unit"], r["ts_utc"]),
                         ("eia_refinery_production:M_EPLLBAN_YPR_R2A_MBBL", "net_production", -120.0, "kbbl", "2026-03-01T00:00:00Z"))

    def test_per_day(self):
        r = P.rows([dict(REAL, units="MBBL/D", value="-4")], "u", "r").iloc[0]
        self.assertEqual((r["variable"], r["unit"]), ("net_production_per_day", "kbbl/d"))

    def test_an_unknown_process_stops(self):
        with self.assertRaises(RuntimeError):
            P.rows([dict(REAL, process="YIR")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_refinery_production_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_refinery_production_monthly", R.STORAGE_HELD["eia_refinery_production_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_refinery_production.py", "tests/test_session618.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

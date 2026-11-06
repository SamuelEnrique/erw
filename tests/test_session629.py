"""Session 629: EIA's natural gas plant field production of natural gas liquids. Held on a record's form (U.S. field
production of natural gas liquids, January 2026): kbbl and kbbl/d kept, a district accepted, an unknown process stops;
the table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_ngl_production as N  # noqa: E402
import release_v1 as R  # noqa: E402

REAL = {"period": "2026-01", "duoarea": "NUS", "product": "EPL2", "process": "FPF", "series": "MNGFPUS1",
        "series-description": "U.S. Field Production of Natural Gas Liquids (Thousand Barrels)", "value": "220000", "units": "MBBL"}


class TheRows(unittest.TestCase):
    def test_both_units(self):
        t = N.rows([REAL, dict(REAL, series="MNGFPUS2", units="MBBL/D", value="7097", duoarea="R3B")], "u", "r")
        self.assertEqual(list(t["variable"]), ["field_production", "field_production_per_day"])
        self.assertEqual(list(t["unit"]), ["kbbl", "kbbl/d"])
        self.assertEqual(t.iloc[0]["entity"], "eia_ngl_production:MNGFPUS1")

    def test_an_unknown_process_stops(self):
        with self.assertRaises(RuntimeError):
            N.rows([dict(REAL, process="YPR")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_ngl_production_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_ngl_production_monthly", R.STORAGE_HELD["eia_ngl_production_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_ngl_production.py", "tests/test_session629.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

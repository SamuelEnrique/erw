"""Session 525: EIA's natural gas in underground storage by state, a month. Held on real records (January 2001,
Pennsylvania and the U.S.): the process names the variable, MMcf kept, a region's geo is US, an unknown process stops; the
table is held from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_storage_state as G  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(area, process, series, desc, value):
    return {"period": "2001-01", "duoarea": area, "process": process, "series": series, "series-description": desc, "value": value, "units": "MMCF"}


REAL = [rec("SPA", "SAO", "N5020PA2", "Pennsylvania Natural Gas in Underground Storage (Working Gas) (MMcf)", "173673"),
        rec("NUS", "SAO", "N5020US2", "U.S. Total Natural Gas in Underground Storage (Working Gas) (MMcf)", "1265496"),
        rec("SPA", "SAI", "N5050PA2", "Pennsylvania Natural Gas Injections into Underground Storage (MMcf)", "6001")]


class TheRows(unittest.TestCase):
    def test_rows(self):
        t = G.rows(REAL, "u", "r").set_index("entity")
        r = t.loc["eia_gas_storage:SAO:SPA"]
        self.assertEqual((r["variable"], r["value"], r["unit"], r["geo"]), ("working_gas", 173673.0, "MMcf", "US-PA"))
        self.assertEqual(t.loc["eia_gas_storage:SAI:SPA", "variable"], "injections")
        self.assertEqual(t.loc["eia_gas_storage:SAO:NUS", "geo"], "US")
        self.assertEqual(G.geo_of("R31"), "US")

    def test_unknown_process_stops(self):
        with self.assertRaises(RuntimeError):
            G.rows([dict(REAL[0], process="SAH")], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_storage_state_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_storage_state_monthly", R.STORAGE_HELD["eia_gas_storage_state_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_storage_state.py", "tests/test_session525.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

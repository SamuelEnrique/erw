"""Session 2323: the Census and Statistics Department's Hong Kong Energy Statistics, electricity (tables 915-91201 and
915-91203), in place of Thailand.

Energy Research Warehouse (ERW). Tests warehouse/connectors/censtatd_hk_electricity.py on answers built here in C&SD's
API form (made up for the test, not C&SD's): the months of 91201 by type of user, its years and town gas left out, a
cell marked not applicable without a row; the quarters of 91203 starting on their first month, its years left out;
terajoules written as MWh; a status not success, a series not in the map, a unit not terajoules, a quarter not ending
a quarter and a value that is not a number stopping the run; the sector rule and the holds. No network.

    python -m unittest tests.test_session2323 -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import censtatd_hk_electricity as C  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R1  # noqa: E402


def answer(rows, code=0):
    return json.dumps({"header": {"status": {"code": code}}, "dataSet": rows})


def r(sv, freq, period, figure, user=None, unit="Terajoule", sd=""):
    x = {"freq": freq, "period": period, "sv": sv, "svDesc": unit, "figure": figure, "sd_value": sd}
    if user is not None:
        x["USER_TYPE"] = user
    return x


class Rows(unittest.TestCase):
    def test_monthly(self):
        rows = [r("ELEC_LOCAL", "M", "202601", 3600, ""), r("ELEC_LOCAL", "M", "202601", 1800, "1"), r("ELEC_LOCAL", "Y", "2025", 9, ""),
                r("GASC_LOCAL", "M", "202601", 5, ""), r("ELE_EX_CHN", "M", "197901", "", sd="-"), r("ELE_EX_CHN", "M", "202601", 36)]
        t = C.finish(C.table_rows("915-91201", answer(rows), "u", "r", "v"))
        self.assertEqual(len(t), 3)
        tot = t[t.variable == "consumption_total"].iloc[0]
        self.assertEqual((tot.value, tot.unit, tot.freq, tot.ts_utc, tot.geo), (1e6, "MWh", "P1M", "2026-01-01T00:00:00Z", "HK"))
        self.assertEqual(t[t.variable == "exports_mainland"].value.iloc[0], 10000.0)

    def test_quarterly(self):
        rows = [r("ELE_GEN_LOCAL", "Q", "202606", 360), r("ELE_GEN_LOCAL", "Y", "2025", 1)]
        t = C.finish(C.table_rows("915-91203", answer(rows), "u", "r", "v"))
        self.assertEqual(list(zip(t.variable, t.ts_utc, t.freq)), [("local_generation", "2026-04-01T00:00:00Z", "P3M")])
        self.assertAlmostEqual(t.value.iloc[0], 100000.0)

    def test_stops(self):
        bad = [("915-91201", answer([r("ELEC_LOCAL", "M", "202601", 1, "")], code=1)), ("915-91203", answer([r("ELE_X", "Q", "202603", 1)])),
               ("915-91203", answer([r("ELE_GEN_LOCAL", "Q", "202603", 1, unit="GWh")])), ("915-91203", answer([r("ELE_GEN_LOCAL", "Q", "202602", 1)])),
               ("915-91201", answer([r("ELEC_LOCAL", "M", "202601", "x", "")])), ("915-91201", answer([r("ELEC_LOCAL", "M", "202601", 1, "9")]))]
        for table, text in bad:
            with self.assertRaises(RuntimeError):
                C.table_rows(table, text, "u", "r", "v")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(C.NAME), "power")
        self.assertIn(C.NAME, R1.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {C.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

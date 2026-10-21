"""Session 518: EIA's natural gas consumption by state, a month.

Energy Research Warehouse (ERW). Held on real records of EIA's API (January 2001, Alabama and the U.S.): the variable is
the process's, MMcf kept, the U.S. total as its own variable, an unknown process or unit stops the run; the table is held
from /data and Redivis v1 until uploaded.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_consumption_state as G  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(area, process, series, desc, value):
    return {"period": "2001-01", "duoarea": area, "process": process, "series": series, "series-description": desc, "value": value, "units": "MMCF"}


REAL = [rec("SAL", "VRS", "N3010AL2", "Alabama Natural Gas Residential Consumption (MMcf)", "13490"),
        rec("SAL", "VEU", "N3045AL2", "Alabama Natural Gas Deliveries to Electric Power Consumers (MMcf)", "3691"),
        rec("NUS", "VRS", "N3010US2", "U.S. Natural Gas Residential Consumption (MMcf)", "976677"),
        rec("NUS", "VC0", "N9140US2", "U.S. Natural Gas Total Consumption (MMcf)", "2676998")]


class TheRows(unittest.TestCase):
    def setUp(self):
        self.t = G.rows(REAL, "https://api.eia.gov/v2/natural-gas/cons/sum/data/", "2026-10-21T20:18:00Z").set_index("entity")

    def test_rows(self):
        a = self.t.loc["eia_gas_consumption:VRS:SAL"]
        self.assertEqual((a["variable"], a["value"], a["unit"], a["geo"], a["ts_utc"]), ("consumption_residential", 13490.0, "MMcf", "US-AL", "2001-01-01T00:00:00Z"))
        self.assertEqual(self.t.loc["eia_gas_consumption:VEU:SAL", "variable"], "consumption_electric_power")
        t = self.t.loc["eia_gas_consumption:VC0:NUS"]
        self.assertEqual((t["variable"], t["value"], t["geo"]), ("consumption_total", 2676998.0, "US"))

    def test_unknown_process_or_unit_stops(self):
        for bad in (dict(REAL[0], process="VGP"), dict(REAL[0], units="BCF")):
            with self.assertRaises(RuntimeError):
                G.rows([bad], "u", "r")

    def test_held_until_uploaded(self):
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as h:
            y = h.read()
        self.assertIn("  - eia_gas_consumption_state_monthly\n", y[y.index("catalogue_hold:"):])
        self.assertIn("upload.py eia_gas_consumption_state_monthly", R.STORAGE_HELD["eia_gas_consumption_state_monthly"])

    def test_no_em_dash(self):
        for f in ("warehouse/connectors/eia_gas_consumption_state.py", "tests/test_session518.py"):
            with open(os.path.join(ROOT, *f.split("/")), encoding="utf-8") as h:
                self.assertNotIn(chr(0x2014), h.read(), f)


if __name__ == "__main__":
    unittest.main()

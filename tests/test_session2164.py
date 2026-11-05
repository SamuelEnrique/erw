"""Session 2164: EIA's natural gas vehicle, lease and plant, pipeline fuel and deliveries by state, a year.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_gas_other_uses_state.py on API rows built here in EIA's
form (made up for the test, not EIA's): the four processes as their variables, a year as its 1 January, a state's and the
nation's geo, a blank left out; a process not asked for, a unit not in the map, a period not a year and a key given
twice stopping the run; a source id of its own (the monthly table's row is not touched); the sector rule and the holds.
No network.

    python -m unittest tests.test_session2164 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_other_uses_state as G  # noqa: E402
import eia_gas_consumption_state as M  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(process="VGP", area="STX", period="2024", value="12345", units="MMcf"):
    return {"process": process, "duoarea": area, "period": period, "value": value, "units": units,
            "series-description": "Texas Natural Gas Pipeline Fuel Consumption (MMcf)"}


class Build(unittest.TestCase):
    def test_rows(self):
        t = G.rows([rec(), rec(process="VDV", area="NUS", value="53149"), rec(process="VGL", value=None)], "u", "r")
        a = t[t.entity == "eia_gas_other_uses:VGP:STX"].iloc[0]
        self.assertEqual((a.variable, a.value, a.unit, a.ts_utc, a.freq, a.geo), ("consumption_pipeline_fuel", 12345.0, "MMcf", "2024-01-01T00:00:00Z", "P1Y", "US-TX"))
        self.assertEqual(t[t.entity == "eia_gas_other_uses:VDV:NUS"].iloc[0].geo, "US")
        self.assertEqual(len(t), 2)

    def test_stops(self):
        for bad in ([rec(process="VRS")], [rec(units="Bcf")], [rec(period="2024-01")], [rec(), rec()]):
            with self.assertRaises(RuntimeError):
                G.rows(bad, "u", "r")

    def test_own_source(self):
        self.assertNotEqual(G.SOURCE, M.SOURCE)
        self.assertEqual(set(G.PROCESSES) & set(M.PROCESSES), set())


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of(G.NAME), "gas")
        self.assertIn(G.NAME, R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn(f"  - {G.NAME}\n", f.read().replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()

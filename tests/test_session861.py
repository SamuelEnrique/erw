"""Session 861: EIA's number of natural gas consumers by state and sector, as eia_gas_consumers_state_annual.

Energy Research Warehouse (ERW). Tests warehouse/connectors/eia_gas_consumers.py on records built here in the form of
EIA's route natural-gas/cons/num (figures made up for the test, not EIA's): the process named as a variable, the state's
geo, the per-consumer ratios (MCF) left out and counted, an unknown unit, the sector rule and the holds. No network.

    python -m unittest tests.test_session861 -v
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "redivis"))
import eia_gas_consumers as G  # noqa: E402
import build_coverage as B  # noqa: E402
import release_v1 as R  # noqa: E402


def rec(area="SAL", process="Number of Residential Consumers", units="COUNT", value="100"):
    return {"period": "2024", "duoarea": area, "process-name": process, "series-description": "x", "value": value, "units": units}


class Reshape(unittest.TestCase):
    def test_counts(self):
        G.SKIPPED.clear()
        t = G.rows([rec(), rec("NUS"), rec(process="Average Consumption per Residential Consumer", units="MCF")], "u", "r")
        self.assertEqual(t.variable.tolist(), ["residential_consumers", "residential_consumers"])
        self.assertEqual(t.geo.tolist(), ["US-AL", "US"])
        self.assertEqual(t.unit.unique().tolist(), ["count"])
        self.assertEqual(G.SKIPPED, {"MCF": 1})

    def test_names_and_stops(self):
        self.assertEqual(G.var_of("Number of Industrial Consumers (Transported)"), "industrial_consumers_transported")
        with self.assertRaises(RuntimeError):
            G.rows([rec(units="MMCF")], "u", "r")
        with self.assertRaises(RuntimeError):
            G.rows([rec(), rec()], "u", "r")


class Registered(unittest.TestCase):
    def test_sector_and_holds(self):
        self.assertEqual(B.sector_of("eia_gas_consumers_state_annual"), "gas")
        self.assertIn("eia_gas_consumers_state_annual", R.STORAGE_HELD)
        with open(os.path.join(ROOT, "warehouse", "supabase", "live_set.yaml"), encoding="utf-8") as f:
            self.assertIn("  - eia_gas_consumers_state_annual", f.read())


if __name__ == "__main__":
    unittest.main()

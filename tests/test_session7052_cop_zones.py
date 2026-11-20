"""Session 7052 (chain 370, the data machine): done-line request 209.

cost_of_power_monthly gains ERCOT's Houston and North load zones (ercot:LZ_HOUSTON, ercot:LZ_NORTH), priced from
ercot_zone_prices_history and weighted by ERCOT's whole demand, as CAISO's two hubs are, so /learn/bill can set
CenterPoint's home against the Houston zone and Oncor's against the North zone.
"""

import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheTwoZones(unittest.TestCase):
    def test_the_builder_names_them_and_reads_the_zone_history(self):
        spec = importlib.util.spec_from_file_location("cost_of_power_7052", os.path.join(ROOT, "warehouse", "derived", "cost_of_power.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual(m.EXTRA["ercot"], ["LZ_HOUSTON", "LZ_NORTH"])
        self.assertEqual(m.EXTRA["caiso"], ["TH_NP15_GEN-APND"])
        self.assertEqual(m.ZONE_HISTORY, "ercot_zone_prices_history")
        with open(os.path.join(ROOT, "warehouse", "derived", "cost_of_power.py"), encoding="utf-8") as f:
            self.assertIn('if iso == "ercot" and pb.MAIN[iso].startswith("LZ_"):', f.read())


if __name__ == "__main__":
    unittest.main()

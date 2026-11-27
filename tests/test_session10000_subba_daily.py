"""Session 10000 (chain 701, predict data request 14): the data machine refreshes eia930_subba_demand_hourly (EIA-930
demand by sub-region, the last 90 days) each day, and runs its stores when it moved. No table is read."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TheDailyStep(unittest.TestCase):
    def test_the_step_and_its_stores(self):
        with open(os.path.join(ROOT, "warehouse", "run_data_machine.sh"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn('soft_step dm_subba "$PYTHON" warehouse/connectors/eia930_subba.py', s)
        self.assertLess(s.index("was_subba="), s.index("soft_step dm_subba "))
        self.assertLess(s.index("soft_step dm_subba "), s.index("soft_step dm_stores_subba "))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "warehouse", "connectors", "eia930_subba.py")))


if __name__ == "__main__":
    unittest.main()

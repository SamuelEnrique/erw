"""Session 10802 (chain 740): the four plant types of /impact keep every figure while the datacenter is added.

Energy Research Warehouse (ERW). No network, no model, no build. Runs site/scripts/test-impact-pins.test.mjs, which
compares the defaults' figures of wind, PV, gas and geothermal in eight states with tests/fixtures/forecast/plant_pins.json,
written from the code before chain 740's first edit.
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


class PlantPins(unittest.TestCase):
    def test_pins_hold(self):
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        env = {k: v for k, v in os.environ.items() if k != "PIN_WRITE"}
        r = subprocess.run([node, "--no-warnings", "--test", "scripts/test-impact-pins.test.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=180, env=env)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])

    def test_the_pins_file_is_present(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "tests", "fixtures", "forecast", "plant_pins.json")))


if __name__ == "__main__":
    unittest.main()

"""Session 3600: the battery game against the owner's rulings of 14 October 2026 and Kelsey's asks of 5 October.

Energy Research Warehouse (ERW). No network, no model, no browser, no site build.
Runs site/scripts/test-battery-rulings.mjs with Node's own test runner (node --test): one block per ruling, (1) Easy's
whole-day forecast, (2) the day at a glance before play with its average and spread (lib/battery.ts glance, worked by
hand), (3) the perfect battery on a hand-worked day (optimum, USD 0.655, checked against brute force) and the end table's
three rows, (4) $5 to start, the end below $0, and Hard's one grid-constrained window said plainly (gridDownWords),
(5) rooftop solar on Hard only, off by default, its shape from EIA-930 over EIA-860M; and the prices' source as a hover
(priceHover).

    python -m unittest tests.test_session3600_batterygame -v
"""

import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")


class Rulings(unittest.TestCase):
    def test_node_rulings(self):
        if not NODE:
            self.skipTest("node is not installed")
        r = subprocess.run([NODE, "--test", os.path.join("scripts", "test-battery-rulings.mjs")], cwd=SITE,
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("pass 6", r.stdout)
        self.assertIn("fail 0", r.stdout)

    def test_no_dashes(self):
        for p in (("site", "scripts", "test-battery-rulings.mjs"), ("site", "lib", "battery.ts"),
                  ("site", "app", "play", "battery", "Game.tsx"), ("site", "app", "play", "battery", "page.tsx")):
            with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn("—", text, p)
            self.assertNotIn("–", text, p)


if __name__ == "__main__":
    unittest.main()

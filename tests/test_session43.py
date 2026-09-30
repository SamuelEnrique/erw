"""Session 43: the electricity bill explainer.

Energy Research Warehouse (ERW). No network, no model.
1. site/scripts/test-bill.mjs runs lib/bill.ts (Node 23.6 or later runs the TypeScript as it is) on bills worked by
   hand from the cited tariff rates, at 600 and 1,000 kWh for both bills, and checks that California's unbundled lines
   add up to the tariff's total rates.
2. Every line of site/data/bill_rules.json has a quoted passage, an effective date and an https source.

    python -m unittest tests.test_session43 -v
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
with open(os.path.join(SITE, "data", "bill_rules.json"), encoding="utf-8") as f:
    RULES = json.load(f)


class Bills(unittest.TestCase):
    def test_hand_computed_bills(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        r = subprocess.run([node, os.path.join("scripts", "test-bill.mjs")], cwd=SITE, capture_output=True, text=True,
                           timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("matches the hand-computed figures", r.stdout)


class Citations(unittest.TestCase):
    def lines(self):
        ca, tx = RULES["bills"]["CA"], RULES["bills"]["TX"]
        yield from ca["components"]
        yield ca["totals"]
        yield ca["baseline_credit"]
        yield ca["climate_credit"]
        yield dict(ca["base_services"], id="base_services")
        yield from tx["fixed"]
        yield from tx["per_kwh"]

    def test_every_line_has_a_quote_a_date_and_an_https_source(self):
        n = 0
        for line in self.lines():
            n += 1
            self.assertTrue(line.get("quote"), line.get("id"))
            self.assertTrue(line.get("effective"), line.get("id"))
            src = RULES["sources"][line["cite"]]
            self.assertTrue(src["url"].startswith("https://"), line.get("id"))
        self.assertGreater(n, 20)

    def test_texas_default_energy_charge_is_derived_as_labelled(self):
        tx = RULES["bills"]["TX"]
        per_kwh = sum(l["rate"] for l in tx["per_kwh"])
        fixed = sum(l["rate"] for l in tx["fixed"])
        want = tx["energy_default"]["eia_row"]["value"] / 1000 - per_kwh - fixed / tx["defaults"]["kwh"]
        self.assertAlmostEqual(tx["energy_default"]["rate"], round(want, 4))


if __name__ == "__main__":
    unittest.main()

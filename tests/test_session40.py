"""Session 40: the severance tax calculator against hand-computed cases.

Energy Research Warehouse (ERW). No network, no model. site/scripts/test-severance.mjs runs lib/severance.ts (Node 23.6
or later runs the TypeScript file as it is) on 19 cases worked by hand from the cited rules in
site/data/severance_rules.json, and checks that every option computes and cites a source the file names. This test
also checks the rules file itself: no rule without a citation and a quote.

    python -m unittest tests.test_session40 -v
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
RULES = json.load(open(os.path.join(SITE, "data", "severance_rules.json"), encoding="utf-8"))


class Calculator(unittest.TestCase):
    def test_hand_computed_cases(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        r = subprocess.run([node, os.path.join("scripts", "test-severance.mjs")], cwd=SITE, capture_output=True, text=True,
                           timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("matches the hand-computed figures", r.stdout)


class Citations(unittest.TestCase):
    def test_every_rule_cites_a_source_with_its_passage(self):
        n = 0
        for st in RULES["states"].values():
            for pr in st["products"].values():
                for rule in pr["base"] + pr["options"] + pr["fees"]:
                    n += 1
                    self.assertIn(rule["cite"], RULES["sources"], rule["id"])
                    self.assertTrue(rule.get("quote"), rule["id"])
                    self.assertTrue(RULES["sources"][rule["cite"]]["url"].startswith("https://"), rule["id"])
        self.assertGreater(n, 30)

    def test_states_and_products(self):
        self.assertEqual(sorted(RULES["states"]), ["LA", "NM", "TX"])
        self.assertEqual(sorted(RULES["states"]["TX"]["products"]), ["condensate", "gas", "oil"])
        self.assertEqual(sorted(RULES["states"]["LA"]["products"]), ["condensate", "gas", "oil"])
        self.assertEqual(sorted(RULES["states"]["NM"]["products"]), ["gas", "oil"])


if __name__ == "__main__":
    unittest.main()

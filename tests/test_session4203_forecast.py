"""Session 4203 (chain 239): the forecast model of tool 17 and its parameter files.

Energy Research Warehouse (ERW). No network, no model, no build. Runs the node tests of site/scripts/test-forecast.test.mjs
(every formula of site/lib/forecast.ts against hand arithmetic), and checks that each parameter file in site/data/forecast/
names its source, that every statute rule quotes its statute, that the method note is kept off the site (internal), and
that the files hold no em or en dash. docs/methods/forecast.md.
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(SITE, "data", "forecast")
FILES = ["jedi_costs.json", "eia_capex.json", "deflator.json", "capacity_factors.json", "sales_tax.json", "income_tax.json",
         "property_rules.json", "jedi_taxable.json", "gas.json"]


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


class TheModel(unittest.TestCase):
    def test_node_tests_pass(self):
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        r = subprocess.run([node, "--no-warnings", "--test", "scripts/test-forecast.test.mjs"], cwd=SITE, capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])

    def test_the_model_imports_nothing(self):
        # check-values imports it as it is (no path alias); the page passes the parameters and the severance callback
        with open(os.path.join(SITE, "lib", "forecast.ts"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotRegex(src, r"(?m)^import ")


class TheParameters(unittest.TestCase):
    def test_every_file_names_its_source(self):
        for name in FILES:
            d = load(name)
            text = json.dumps(d)
            self.assertTrue(any(k in d for k in ("source", "sources", "tables", "about")), name)
            self.assertRegex(text, r"https://|warehouse/|lbnl_|eia_steo", name)

    def test_every_statute_rule_quotes_its_statute(self):
        d = load("property_rules.json")
        for st, v in d["states"].items():
            for r in v["rules"]:
                self.assertIn(r["cite"], d["sources"], r["id"])
                self.assertGreater(len(r["quote"]), 60, r["id"])
                self.assertTrue(d["sources"][r["cite"]]["url"].startswith("https://"), r["id"])

    def test_the_taxable_shares_are_their_arithmetic(self):
        t = load("jedi_taxable.json")["technologies"]
        self.assertAlmostEqual(t["land_based_wind"]["taxable_share"], 22682269.377612367 / 0.0635 / 435992965.3256575, places=6)
        self.assertAlmostEqual(t["natural_gas"]["taxable_share"], 15147058.823529413 / 0.04 / 625000000, places=6)
        self.assertIsNone(t["geothermal"]["taxable_share"])

    def test_the_deflator_is_history_through_2025(self):
        d = load("deflator.json")
        self.assertEqual(d["base_year"], 2025)
        self.assertNotIn("2026", d["index"])
        self.assertAlmostEqual(d["index"]["2017"], 100, delta=0.01)

    def test_no_dash(self):
        paths = [os.path.join(DATA, n) for n in FILES] + [os.path.join(ROOT, "docs", "methods", "forecast.md"), os.path.join(SITE, "lib", "forecast.ts"),
                 os.path.join(SITE, "scripts", "test-forecast.test.mjs")] + [os.path.join(ROOT, "warehouse", "forecast", n) for n in ("jedi_costs.py", "eia_capex.py", "params.py")]
        for p in paths:
            with open(p, encoding="utf-8") as f:
                t = f.read()
            self.assertNotIn(chr(0x2014), t, p)
            self.assertNotIn(chr(0x2013), t, p)


class TheNote(unittest.TestCase):
    def test_the_method_note_is_internal(self):
        with open(os.path.join(SITE, "scripts", "build-content.mjs"), encoding="utf-8") as f:
            self.assertRegex(f.read(), r"INTERNAL_METHODS = new Set\([^)]*\"forecast\"")

    def test_the_note_names_every_parameter_file(self):
        with open(os.path.join(ROOT, "docs", "methods", "forecast.md"), encoding="utf-8") as f:
            note = f.read()
        for name in ("eia_capex.json", "deflator.json", "capacity_factors.json", "sales_tax.json", "income_tax.json", "property_rules.json", "jedi_taxable.json", "gas.json", "jedi_costs.json"):
            self.assertIn(name, note, name)


if __name__ == "__main__":
    unittest.main()

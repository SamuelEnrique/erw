"""Session 10802 (chain 740): the datacenter in /impact (site/lib/dcimpact.ts) and its parameter files.

Energy Research Warehouse (ERW). No network, no model, no build. Runs site/scripts/test-datacenter.test.mjs (three
announced projects, each tax line worked by hand from the statutes), checks that the model imports nothing, that every
datacenter parameter file names its source and holds no em or en dash, and that every rule of datacenter_rules.json
names a source with hover words (warehouse/forecast/datacenter_rules_check.py, without the reads).
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(SITE, "data", "forecast")
FILES = ["datacenter_announced.json", "datacenter_rules.json", "datacenter_wages.json"]


class TheModel(unittest.TestCase):
    def test_node_tests_pass(self):
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        r = subprocess.run([node, "--no-warnings", "--test", "scripts/test-datacenter.test.mjs"], cwd=SITE,
                           capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])

    def test_the_model_imports_nothing(self):
        with open(os.path.join(SITE, "lib", "dcimpact.ts"), encoding="utf-8") as f:
            self.assertNotRegex(f.read(), r"(?m)^import ")


class TheReplication(unittest.TestCase):
    """Session 10804: the page's figures drawn again from lib/dcimpact.ts, then replicate.py (written from the note) agrees."""

    def test_replication_agrees(self):
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        r = subprocess.run([node, "--no-warnings", os.path.join(SITE, "scripts", "dc-figures.mjs")], cwd=ROOT, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "replication", "impact", "datacenter", "replicate.py")], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-2000:])
        self.assertRegex(r.stdout, r"(\d+) of \1 figures agree")


class TheParameters(unittest.TestCase):
    def test_files_name_sources_and_hold_no_dash(self):
        for name in FILES:
            with open(os.path.join(DATA, name), encoding="utf-8") as f:
                text = f.read()
            d = json.loads(text)
            self.assertTrue(any(k in d for k in ("source", "sources")), name)
            self.assertNotIn("—", text, name)
            self.assertNotIn("–", text, name)

    def test_rules_check_passes(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "forecast", "datacenter_rules_check.py")],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_announced_row_has_its_document(self):
        with open(os.path.join(DATA, "datacenter_announced.json"), encoding="utf-8") as f:
            d = json.load(f)
        for r in d["rows"]:
            self.assertTrue(r["doc"]["url"].startswith("https://"), r["id"])
            for k in ("mw", "investment", "construction_jobs", "permanent_jobs"):
                if r.get(k):
                    self.assertIn(r[k]["says"], r[k]["quote"], f"{r['id']} {k}")


if __name__ == "__main__":
    unittest.main()

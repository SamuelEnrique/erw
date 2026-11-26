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

    def test_the_ui_node_tests_pass(self):
        """Session 10821: window F's I4 (a figure not taken is said) and I5 (a project alone in the address sets its figures)."""
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        r = subprocess.run([node, "--no-warnings", "--import", "./scripts/tsx-register.mjs", "--test", "scripts/test-datacenter-ui.test.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=180)
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


class TheRunFiles(unittest.TestCase):
    """Session 10805: the Python script a reader downloads for two datacenter scenarios runs and agrees with the tool."""

    def test_downloaded_python_agrees(self):
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([node, "--no-warnings", os.path.join(SITE, "scripts", "dc-files-check.mjs"), d], cwd=ROOT, capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = subprocess.run([sys.executable, os.path.join(d, "run.py")], capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("DIFFERS", r.stdout)
            self.assertGreaterEqual(r.stdout.count(" ok"), 18, r.stdout)

    def test_downloaded_python_agrees_for_arkansas_and_georgia(self):
        """Session 10813: the state's rate with construction covered (Arkansas) and an end year with a spending window (Georgia)."""
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, DC_FILES_PAIR="ar-ga")
            r = subprocess.run([node, "--no-warnings", os.path.join(SITE, "scripts", "dc-files-check.mjs"), d], cwd=ROOT, capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = subprocess.run([sys.executable, os.path.join(d, "run.py")], capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("DIFFERS", r.stdout)
            # Arkansas: 4 equipment purchases of 1.364e9 and 40 percent of the 392e6 building, at the state's 6.5 percent
            self.assertIn("A forgone: script 364832000.0", r.stdout)
            # Georgia: the build's equipment only (through 2031), at 7.56 percent
            self.assertIn("B forgone: script 103118400.0", r.stdout)

    def test_downloaded_python_agrees_for_ohio_and_illinois_electricity(self):
        """Session 10817: Ohio's elective self-assessing kWh schedule and Illinois' ten monthly blocks, 5,000,000 MWh a year for 20 years."""
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is not on the path")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, DC_FILES_PAIR="oh-il")
            r = subprocess.run([node, "--no-warnings", os.path.join(SITE, "scripts", "dc-files-check.mjs"), d], cwd=ROOT, capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = subprocess.run([sys.executable, os.path.join(d, "run.py")], capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("DIFFERS", r.stdout)
            self.assertIn("A elec: script 190580000.0", r.stdout)   # 9,529,000 a year
            self.assertIn("B elec: script 203286212.7", r.stdout)   # 10,164,310.64 a year
            # session 10821: the Stata download carries the electricity tax too (Stata is not on this machine: its lines are checked)
            with open(os.path.join(d, "run.do"), encoding="utf-8") as f:
                do = f.read()
            self.assertIn("scalar elec_year = min(elec_year, max(0, min(kwh_year, 500000000) - 0) * 0.00257", do)
            self.assertEqual(do.count('display "electricity tax over the operating years: "'), 2)


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

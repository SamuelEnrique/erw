"""Session 8901 (chain 507, part C): the four problem sets of the whole country.

Every figure is a pf| key into a committed page file (site/lib/pagefile.ts). The replication
(replication/problem_sets/replicate_country.py) recomputes every answer from the page files with Python's json alone, and
its figures are compared with the ones the site's own code builds (site/scripts/problem-sets-country-figures.mjs); the
node tests pin each figure to its file, draw the pages (site/scripts/test-problem-sets-country.mjs) and run check-values on
pf| keys (site/scripts/test-pagefile.mjs); the do-file keeps Samuel's Stata rules. No network, no model.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "replication", "problem_sets")
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
DASH, EN = chr(0x2014), chr(0x2013)
SLUGS = ["who-trades-with-whom", "storm-across-the-country", "under-the-ground-and-in-the-wind", "where-energy-goes"]


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheReplication(unittest.TestCase):
    def test_it_recomputes_every_question(self):
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate_country.py")], capture_output=True, text=True, cwd=ROOT, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"^31 questions and examples, \d+ figures recomputed, \d+ inputs read")
        for f in ("country_inputs.csv", "country_answers.csv"):
            text = src("replication", "problem_sets", f)
            self.assertTrue(text.startswith("# Energy Research Warehouse (ERW), session 8901"), f)

    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_the_site_shows_what_the_replication_recomputes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "country.json")
            r = subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", "scripts/problem-sets-country-figures.mjs", out], capture_output=True, text=True, cwd=SITE, timeout=300)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            c = subprocess.run([sys.executable, os.path.join(REP, "replicate_country.py"), "--compare", out], capture_output=True, text=True, cwd=ROOT, timeout=300)
        self.assertEqual(c.returncode, 0, c.stdout + c.stderr)
        self.assertRegex(c.stdout, r"compared: 31 questions, \d+ answer figures; 0 differ")

    def test_the_do_file_keeps_the_rules(self):
        do = src("replication", "problem_sets", "replicate_country.do")
        self.assertNotIn("///", do)
        self.assertIn("country_inputs.csv", do)
        self.assertIn("country_answers.csv", do)
        self.assertIn("Stata reads no JSON", do)
        for line in do.splitlines():
            if line.startswith("destring"):
                self.assertIn("force", line, line)
        lines = do.splitlines()
        body = lines[next(i for i, x in enumerate(lines) if x.startswith("version")):]
        for a, b in zip(body, body[1:]):
            self.assertFalse(a == "" and b == "", "two empty lines in a row")
            if a and not a.startswith("*") and b:
                self.fail(f"two commands with no empty line between them: {a!r} then {b!r}")
        self.assertNotIn(DASH, do)


class TheNodeTests(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_each_figure_is_pinned_to_its_file_and_drawn(self):
        r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/test-problem-sets-country.mjs"], capture_output=True, text=True, cwd=SITE, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertIn("ok: 4 sets,", r.stdout)

    @unittest.skipUnless(NODE, "node is not installed")
    def test_the_key_and_check_values(self):
        r = subprocess.run([NODE, "scripts/test-pagefile.mjs"], capture_output=True, text=True, cwd=SITE, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertIn("6 tests passed", r.stdout)


class TheFiles(unittest.TestCase):
    def test_registered_after_the_five(self):
        p = src("site", "lib", "problems.ts")
        self.assertIn("...[TRADE, STORM, GROUND, WHERE].map((m) => m.META)", p)
        self.assertIn("addGuide(m.META.slug, m.GUIDE_ENTRY)", p)
        self.assertEqual(len(re.findall(r'\{ slug: "', p)), 5)   # the five's own entries stay as they were
        cv = src("site", "scripts", "check-values.mjs")
        self.assertIn('if (p[0] === "pf") {', cv)
        for s in SLUGS:
            self.assertIn(f'"/learn/problems/{s}"', cv)

    def test_no_dash_and_the_note(self):
        files = [("site", "lib", "pagefile.ts"), ("site", "lib", "problemsets", "common.ts"), ("site", "scripts", "test-pagefile.mjs"),
                 ("site", "scripts", "test-problem-sets-country.mjs"), ("site", "scripts", "problem-sets-country-figures.mjs"),
                 ("replication", "problem_sets", "replicate_country.py"), ("replication", "problem_sets", "replicate_country.do"),
                 ("docs", "methods", "problem_sets.md"), ("site", "lib", "problemkit.ts"), ("site", "lib", "problems.ts")]
        files += [("site", "lib", "problemsets", f"{s}.ts") for s in SLUGS]
        for f in files:
            t = src(*f)
            self.assertNotIn(DASH, t, f)
            self.assertNotIn(EN, t, f)
        note = src("docs", "methods", "problem_sets.md")
        self.assertIn("## The whole country (chain 507, session 8901)", note)
        for s in SLUGS:
            self.assertIn(s, note)


if __name__ == "__main__":
    unittest.main()

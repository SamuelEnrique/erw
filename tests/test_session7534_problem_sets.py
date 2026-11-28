"""Session 7534 (chain 304): the problem sets (/learn/problems) at the done line.

The replication recomputes every figure the five live sets showed on the kept reads (146 of 146) and the edition from its
own downloads; the kept figures are the page's own (a replay of the kept reads through the site's code gives them
again); no row a license holds is kept; the four site fixes stand in site/lib/problems.ts; the decisions block is drawn
and equals the note's list. No network, no model.
"""
from __future__ import annotations

import json
import os
import re  # session 8905: the edition counts are read with a pattern
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "replication", "problem_sets")
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
# chain 370 (session 7050, the landing desk): the two replays import the site's packages (react); a checkout without
# site/node_modules, as the landing gate's suite runs before npm ci, skips them as the other node-reading tests do
REACT = os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "node_modules", "react"))
DASH = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheReplication(unittest.TestCase):
    def test_every_figure_passes(self):
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, cwd=ROOT, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # session 11407 (wip/ready-learn-bill-season): B3's seasonal price adds its eight months' rows, its mean and a
        # second phrase of words to the checks, 146 to 155
        self.assertIn("155 checks (figures by check key, and answers in words): 155 pass, 0 named, 0 differ", r.stdout)
        # session 8905 (chain 590, data request 561): every edition held is compared, so the counts grow with each new
        # edition: none may differ, and the only figures named are the network hour's three of set E in each edition
        m = re.search(r"the dated edition: (\d+) figures: (\d+) pass, (\d+) named, (\d+) differ", r.stdout)
        self.assertIsNotNone(m, r.stdout)
        n_ed = len(json.loads(src("site", "data", "problem_editions", "index.json"))["editions"])
        figures, passed, named, differ = (int(x) for x in m.groups())
        self.assertEqual(differ, 0, r.stdout)
        self.assertEqual(named, 3 * n_ed, r.stdout)
        self.assertEqual(passed + named, figures)
        self.assertGreaterEqual(passed, 89)

    def test_no_held_row_is_kept(self):
        text = src("replication", "problem_sets", "live_rows.csv")
        for held in ("isone:", "miso:", "nyiso:"):
            self.assertNotIn(held, text)

    def test_the_do_file_names_its_five(self):
        do = src("replication", "problem_sets", "replicate.do")
        self.assertEqual(do.count("assert abs("), 5)
        for v in ("2.08", "47.74", "1.12", "24.88", "73.06"):
            self.assertIn(v, do)

    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_the_kept_figures_are_the_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "replay.json")
            r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/problem-sets-figures.mjs", "replay", REP, out],
                               capture_output=True, text=True, cwd=SITE, timeout=600)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            with open(out, encoding="utf-8") as f:
                got = json.load(f)
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            kept = json.load(f)
        strip = lambda d: {s: [(q["q"], q["answer"], q["steps"], q["figures"]) for q in v["questions"]] for s, v in d["sets"].items()}
        # session 8901 (chain 507, part C): the replay now also builds the four sets of the whole country, which read
        # committed page files and no live read; the kept figures are the five sets', so the five are compared with them
        # and the four are held to be drawn whole (scripts/test-problem-sets-country.mjs pins their figures to their files)
        self.assertEqual({s: v for s, v in strip(got).items() if s in kept["sets"]}, strip(kept))
        # session 8905 (chain 590, part C): and the fifth, your own balancing authority
        self.assertEqual(sorted(set(got["sets"]) - set(kept["sets"])), ["storm-across-the-country", "under-the-ground-and-in-the-wind", "where-energy-goes", "who-trades-with-whom", "your-own-balancing-authority"])
        for slug, v in got["sets"].items():
            self.assertEqual(v["drawn"]["missing"], [], slug)
            self.assertTrue(v["decisions"], slug)
        # session 8901: 15 choices and the five of the whole country (page-file, trade-month, storm-hour, layer-by-id, industry-pick)
        # session 8905: and authority-pick, the fifth set's
        self.assertEqual(len(got["index_decisions"]), 21)
        d = {q["id"]: q for q in got["sets"]["storage-and-taxes"]["questions"]}
        self.assertIn("Over the seven latest days held (2026-11-03 to 2026-11-14)", d["d1"]["q"])
        self.assertIn("(77.4 Mcf a day over its 31 days)", d["d5"]["q"])
        self.assertIn("the newest it holds; 2026-10 is later", d["d4"]["steps"][3])
        b2 = next(q for q in got["sets"]["prices-and-your-bill"]["questions"] if q["id"] == "b2")
        self.assertTrue(b2["q"].startswith("The table's public rows hold 4 hubs: CAISO NP15, CAISO SP15, ERCOT hub average, SPP North hub."))

    @unittest.skipUnless(NODE and REACT, "node or the site's packages are not installed")
    def test_the_decisions_block(self):
        r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/test-problem-sets-render.mjs"],
                           capture_output=True, text=True, cwd=SITE, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr[-2000:])


class TheFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = src("site", "lib", "problems.ts")

    def test_seven_days_held(self):
        d = self.p[self.p.index("async function setD()"):self.p.index('id: "d1"')]
        self.assertIn("since: iso(Date.now() - 45 * DAY)", d)
        self.assertNotIn("12 * DAY", d)
        self.assertIn("Over the ${howMany} latest days held", self.p)

    def test_words_from_the_rules(self):
        # the old words stand only in the comments that say what was fixed
        self.assertNotIn("(80 Mcf a day over 30 days), valued", self.p)
        self.assertIn("Mcf a day over its ${gmDays} days", self.p)
        self.assertNotIn('["New Mexico: severance 3.75', self.p)
        self.assertIn("`New Mexico: ${nmWords}: `", self.p)
        self.assertIn("The table's public rows hold ${ents.length} hubs: ", self.p)

    def test_files_and_words(self):
        faults = src("docs", "reviews", "problem-sets-faults-2026-11-16.md")
        self.assertEqual(sum(1 for line in faults.splitlines() if line[:2] == "| " and line[2:3].isdigit()), 9)
        for p in (("docs", "reviews", "problem-sets-faults-2026-11-16.md"), ("docs", "reviews", "problem-sets-crosscheck-2026-11-16.md"),
                  ("docs", "methods", "problem_sets.md"), ("replication", "problem_sets", "replicate.py"), ("replication", "problem_sets", "replicate.do"),
                  ("site", "app", "learn", "problems", "Decisions.tsx"), ("site", "scripts", "problem-sets-figures.mjs"),
                  ("site", "scripts", "test-problem-sets-render.mjs"), ("site", "lib", "problems.ts")):
            self.assertNotIn(DASH, src(*p), p)
        self.assertIn("### The decisions", src("docs", "methods", "problem_sets.md"))


if __name__ == "__main__":
    unittest.main()

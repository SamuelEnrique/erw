"""Session 7548 (chain 304, part B): the problem sets (/learn/problems) read as an undergraduate working problem set 3
start to finish and the instructor who sets it (docs/reviews/problem-sets-read-2026-11-16.md).

The read's six site fixes and the figures the sets share with /events, /storage and /learn/bill are held by
site/scripts/test-problem-sets-read.mjs (the pages drawn with the site's code on the kept reads, no network); this file
runs it, and holds the read file and the license hold on everything the read commits. No network, no model.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "problem_sets")
READ = os.path.join(ROOT, "docs", "reviews", "problem-sets-read-2026-11-16.md")
NODE = shutil.which("node")
DASH = chr(0x2014)
HELD = re.compile(r"\b(isone|miso|nyiso)(_queue|_load_queue)?:", re.I)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheRead(unittest.TestCase):
    def test_the_rows(self):
        t = src("docs", "reviews", "problem-sets-read-2026-11-16.md")
        rows = re.findall(r"^\| (\d+) \| [^|]+ \| .+ \| (site|data machine|browser|ruling) \| ", t, re.M)
        self.assertEqual([int(n) for n, _ in rows], list(range(1, 14)))
        kinds = [k for _, k in rows]
        self.assertEqual(kinds.count("site"), 6)
        self.assertEqual(kinds.count("ruling"), 3)
        self.assertEqual(kinds.count("browser"), 3)
        self.assertEqual(kinds.count("data machine"), 1)
        self.assertIn("**The reader:**", t)
        self.assertIn("**The five cases:**", t)

    def test_no_em_dash(self):
        for p in (("docs", "reviews", "problem-sets-read-2026-11-16.md"), ("site", "scripts", "test-problem-sets-read.mjs"),
                  ("site", "lib", "problems.ts"), ("site", "lib", "problemkit.ts"), ("site", "app", "learn", "problems", "Decisions.tsx")):
            self.assertNotIn(DASH, src(*p), p)

    def test_nothing_held_is_committed(self):
        # the rule of site/lib/license.ts for the tables the sets read: held by grid for ISO-NE, MISO and NYISO; no entity of
        # those grids in the kept rows, the kept figures or the read (the full rule, licenseHeldRow, runs in the .mjs test)
        for p in (("replication", "problem_sets", "live_rows.csv"), ("replication", "problem_sets", "page_figures.json"),
                  ("replication", "problem_sets", "live_reads.json"), ("docs", "reviews", "problem-sets-read-2026-11-16.md")):
            self.assertIsNone(HELD.search(src(*p)), p)


@unittest.skipUnless(NODE, "node is not installed")
class TheFixes(unittest.TestCase):
    def test_the_read_test(self):
        r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/test-problem-sets-read.mjs"],
                           capture_output=True, text=True, cwd=SITE, timeout=600, env={**os.environ, "ERW_SPEND_CAP_USD": "0"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("with none held", r.stdout)


if __name__ == "__main__":
    unittest.main()

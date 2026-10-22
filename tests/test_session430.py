"""Session 430 (chain 023, 21 October 2026, run on portable-laptop): check-values finishes on a slow database.

The full run of site/scripts/check-values.mjs passed its 15-minute limit three times on 21 October 2026 (sessions 461,
474 and 423) and so reported nothing. It now reads its pages one at a time, in batches, each under a limit of its own
that aborts the page's requests; a page that timed out is tried once more after the last page; at the run's limit no
page starts, and the run lists every page it did not read. Exit 0 only when every page was read and passed; 1 for a
value that differs, a floor that fails on a page read, or any fault but slowness; 3 when every value read passed but
some pages were not read. A state file lets a second run (CHECK_VALUES_RESUME=1) read only what the first left.
The scheduling is site/scripts/check-values-run.mjs (its test: scripts/test-check-values-run.mjs); the whole script is
tried end to end against a server of its own with keys judged from warehouse/metadata alone
(scripts/test-check-values-slow.mjs): no build, no database. Energy Research Warehouse (ERW)."""
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
DASHES = (chr(0x2014), chr(0x2013))
FILES = ["site/scripts/check-values.mjs", "site/scripts/check-values-run.mjs", "site/scripts/test-check-values-run.mjs",
         "site/scripts/test-check-values-slow.mjs", "tests/test_session430.py"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheNodeTests(unittest.TestCase):
    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_the_scheduling(self):
        r = subprocess.run([NODE, "scripts/test-check-values-run.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertIn("10 tests passed", r.stdout)

    @unittest.skipUnless(NODE and os.path.isfile(os.path.join(ROOT, "warehouse", "metadata", "license_status.csv")), "node or the license record is not here")
    def test_the_script_on_a_slow_site(self):
        r = subprocess.run([NODE, "scripts/test-check-values-slow.mjs"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1500:])
        self.assertIn("5 tests passed", r.stdout)


class TheScript(unittest.TestCase):
    def setUp(self):
        self.cv = src("site", "scripts", "check-values.mjs")

    def test_it_reads_through_the_scheduler(self):
        self.assertIn('import * as RUN from "./check-values-run.mjs";', self.cv)
        self.assertIn("await RUN.runPages({", self.cv)
        self.assertIn("const PAGE_S = Number(process.env.CHECK_VALUES_PAGE_S ?? 300);", self.cv)
        self.assertIn("const BATCH = Number(process.env.CHECK_VALUES_BATCH ?? 10);", self.cv)
        self.assertIn('process.env.CHECK_VALUES_RESUME === "1"', self.cv)
        self.assertIn('path.join(here, "..", "..", "runs", "check-values", "state.json")', self.cv)   # under runs/, which git ignores

    def test_a_page_not_read_is_listed_and_the_run_is_not_a_pass(self):
        self.assertIn("not read | ${p} | ${why.get(p) ?? \"not reached\"} | its numbers and its floor are not judged", self.cv)
        i = self.cv.index("if (!bad && missing.length) {")
        self.assertIn("process.exitCode = 3;", self.cv[i:i + 700])   # ends by itself: see the comment there
        self.assertLess(i, self.cv.index("if (bad || n < 10) process.exit(1);"))

    def test_the_older_rules_hold(self):
        # sessions 268, 371, 408 and 72: the floor, the internal drafts, the list, the request timeout and a hard stop
        for pin in ['const FLOOR_FILE = path.join(here, "check-values-floor.json");', "its floor is ${floor}", "Math.min(10, count)",
                    "if (bad || n < 10) process.exit(1);", "has no floor in scripts/check-values-floor.json",
                    "if (tok) urls.push(...INTERNAL.filter(wanted).map((page) => ({ page, url: page, internal: true })));",
                    "AbortSignal.timeout(REQUEST_MS)", "(RUN_MIN + 5) * 60 * 1000", "RESTRICTED RUN (CHECK_VALUES_PAGES)"]:
            self.assertIn(pin, self.cv, pin)
        self.assertIn("if (bad || n < 10 || missing.length) console.log(", self.cv)   # no floor from an incomplete run

    @unittest.skipUnless(NODE, "node is not on this machine")
    def test_the_list_still_stops_before_any_request(self):
        r = subprocess.run([NODE, "scripts/check-values.mjs", "--list"], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertIn('"/data/licenses"', r.stdout)

    def test_no_dash(self):
        for f in FILES:
            t = src(*f.split("/"))
            for d in DASHES:
                self.assertNotIn(d, t, f)


if __name__ == "__main__":
    unittest.main()

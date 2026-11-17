"""Session 7547 (chain 304, part B): What is on an electricity bill (/learn/bill) read as a household with its own bill.

Energy Research Warehouse (ERW). No network, no model, no warehouse table written.

- ThePageDrawn     site/scripts/test-bill-read.mjs (the read's site rows: the wholesale month field, the bill's own power
                   line under the bar, the Texas delivery lines together, the territory tip; the figures shared with the
                   problem set; no held row committed) and site/scripts/bill-figures.mjs --check.
- TheReplication   replication/bill/replicate.py: every figure inside, the read's four cases among them.
- TheRead          docs/reviews/bill-read-2026-11-16.md: the reader, five cases, numbered rows with kind and state; the
                   method note names the month field, the power line and the count.

    python -m unittest tests.test_session7547_bill_read -v
"""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "bill")
NODE = shutil.which("node")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run = lambda reg, *a: subprocess.run([NODE, "--import", reg, *a], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)  # noqa: E731
        cls.read = run("./scripts/tsx-register.mjs", "scripts/test-bill-read.mjs")
        cls.figures = run("./scripts/battery-awards-page-register.mjs", "scripts/bill-figures.mjs", "--check")

    def test_read_checks_pass(self):
        self.assertEqual(self.read.returncode, 0, self.read.stdout[-3000:] + self.read.stderr[-1500:])
        self.assertNotIn("FAIL", self.read.stdout)
        m = re.search(r"(\d+) of (\d+) checks pass", self.read.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 40, self.read.stdout[-500:])

    def test_the_page_prints_the_committed_figures(self):
        self.assertEqual(self.figures.returncode, 0, self.figures.stdout[-3000:] + self.figures.stderr[-1500:])
        self.assertIn("as committed", self.figures.stdout)


class TheReplication(unittest.TestCase):
    def test_every_figure_inside_with_the_read_cases(self):
        r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])
        m = re.search(r"(\d+) of (\d+) figures inside", r.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 1200, r.stdout[-500:])
        for cid in ("read_fresno_aug", "read_houston_aug", "read_student_apr", "read_houston_oct_partial"):
            self.assertRegex(r.stdout, rf"{cid}: (\d+) of \1\b")

    def test_the_read_cases_print_their_figures(self):
        figs = {c["id"]: {f["key"]: f["shown"] for f in c["figures"]} for c in json.loads(src("replication", "bill", "page_figures.json"))["cases"]}
        self.assertEqual(figs["read_fresno_aug"]["total"], "$367.71")
        self.assertEqual(figs["read_fresno_aug"]["bar|month"], "2026-08")
        self.assertEqual(figs["read_fresno_aug"]["power|usd"], "$117.51")
        self.assertEqual(figs["read_houston_aug"]["group|Delivery (CenterPoint)"], "$96.37")
        self.assertEqual(figs["read_student_apr"]["bar|share_pct"], "3")
        self.assertEqual(figs["page"]["opens|bar|share_pct"], "12")


class TheRead(unittest.TestCase):
    def test_rows(self):
        t = src("docs", "reviews", "bill-read-2026-11-16.md")
        self.assertIn("**The reader:**", t)
        self.assertIn("**The five cases:**", t)
        rows = re.findall(r"^\| (\d+) \| [^|]+ \| [^|]+ \| [^|]+ \| (site|data machine|browser|ruling) \|", t, re.M)
        self.assertGreaterEqual(len(rows), 10)
        self.assertEqual([int(n) for n, _ in rows], list(range(1, len(rows) + 1)))
        self.assertNotIn(chr(0x2014), t)

    def test_note_names_the_read(self):
        note = src("docs", "methods", "bill.md")
        self.assertIn("669 of 669", note)  # session 7533's count is kept
        self.assertIn("1209 of 1209", note)
        self.assertIn("Wholesale price, month", note)
        self.assertIn("power line", note)
        self.assertNotIn(chr(0x2014), note)


if __name__ == "__main__":
    unittest.main()

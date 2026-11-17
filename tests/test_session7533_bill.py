"""Session 7533 (chain 304): What is on an electricity bill (/learn/bill) at the done line.

Energy Research Warehouse (ERW). No network, no model, no warehouse table written.

- ThePageDrawn     site/scripts/test-bill-render.mjs (the faults fixed, the decisions fold) and
                   site/scripts/bill-figures.mjs --check (the page drawn whole on the committed rows prints the committed
                   figures: the five cards' totals, wholesale sums and shares are numbers, not "license needed").
- TheReplication   replication/bill/: every figure inside its tolerance, the headline figures, the Texas defaults'
                   derivation, the cross-check's published figures, the do-file's expected lines, the evidence of origin/main.
- TheNote          docs/methods/bill.md names the decisions, the replication's count and the cross-check.
- TheFaults        docs/reviews/bill-faults-2026-11-16.md: numbered rows, each with its state.

    python -m unittest tests.test_session7533_bill -v
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


def replicate(*args):
    r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py"), *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
    return r.returncode, r.stdout


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run = lambda reg, *a: subprocess.run([NODE, "--import", reg, *a], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)  # noqa: E731
        cls.render = run("./scripts/tsx-register.mjs", "scripts/test-bill-render.mjs")
        cls.figures = run("./scripts/battery-awards-page-register.mjs", "scripts/bill-figures.mjs", "--check")

    def test_render_checks_pass(self):
        self.assertEqual(self.render.returncode, 0, self.render.stdout[-3000:] + self.render.stderr[-1500:])
        self.assertNotIn("FAIL", self.render.stdout)
        m = re.search(r"(\d+) of (\d+) passed", self.render.stdout)
        self.assertTrue(m and m.group(1) == m.group(2) and int(m.group(2)) >= 50, self.render.stdout[-500:])

    def test_the_page_prints_the_committed_figures(self):
        self.assertEqual(self.figures.returncode, 0, self.figures.stdout[-3000:] + self.figures.stderr[-1500:])
        self.assertIn("as committed", self.figures.stdout)


class TheReplication(unittest.TestCase):
    def test_every_figure_inside(self):
        code, out = replicate()
        self.assertEqual(code, 0, out[-3000:])
        m = re.search(r"(\d+) of (\d+) figures inside", out)
        self.assertTrue(m and m.group(1) == m.group(2), out[-500:])
        self.assertGreaterEqual(int(m.group(2)), 600)

    def test_no_card_figure_is_held(self):
        figs = json.loads(src("replication", "bill", "page_figures.json"))
        page = next(c for c in figs["cases"] if c["id"] == "page")
        held = [f["key"] for f in page["figures"] if f["shown"] == "license needed"]
        self.assertEqual(held, [])
        self.assertEqual(sum(1 for f in page["figures"] if f["key"].startswith("card|") and f["key"].endswith("|total")), 5)

    def test_headline_matches_the_do_file(self):
        code, out = replicate("--headline")
        self.assertEqual(code, 0)
        do = src("replication", "bill", "replicate.do")
        for line in out.strip().splitlines():
            self.assertIn(line, do)
        for v in ("229.63", "224.76", "332.91", "95.27", "95.28"):
            self.assertIn(v, out)

    def test_texas_defaults_derive_from_eia(self):
        code, out = replicate("--texas-default")
        self.assertEqual(code, 0)
        self.assertIn("= 0.090711; the file holds 0.0907", out)
        self.assertIn("= 0.085300; the file holds 0.0853", out)

    def test_crosscheck_prints_the_published_figures(self):
        code, out = replicate("--crosscheck")
        self.assertEqual(code, 0)
        for s in ("29.75", "15.91", "39.62", "32.43", "43.63", "160.86", "163.72"):
            self.assertIn(s, out)

    def test_evidence_of_origin_main(self):
        t = src("replication", "bill", "replicate_on_origin_main.txt")
        self.assertIn("652 of 669 figures inside", t)
        self.assertEqual(t.count("NOT PRINTED"), 15)
        self.assertIn("506.99999999999994", t)

    def test_no_em_dash(self):
        for name in ("replicate.py", "replicate.do", "cases.json", "replicate_on_origin_main.txt"):
            self.assertNotIn(chr(0x2014), src("replication", "bill", name), name)


class TheNote(unittest.TestCase):
    def test_note_names_the_work(self):
        note = src("docs", "methods", "bill.md")
        self.assertIn("# What is on an electricity bill", note)  # the note of session 335 is kept
        dec = src("site", "app", "learn", "bill", "Decisions.tsx")
        keys = re.findall(r'\{ key: "([a-z-]+)"', dec)
        self.assertEqual(len(keys), 14)
        for k in keys:
            self.assertIn(f"`{k}`", note, k)
        self.assertIn("669 of 669", note)
        self.assertIn("Table 5.6.A", note)
        self.assertNotIn(chr(0x2014), note)


class TheFaults(unittest.TestCase):
    def test_rows(self):
        t = src("docs", "reviews", "bill-faults-2026-11-16.md")
        rows = re.findall(r"^\| (\d+) \| (site|data machine|ruling) \|", t, re.M)
        self.assertGreaterEqual(len(rows), 8)
        self.assertEqual([int(n) for n, _ in rows], list(range(1, len(rows) + 1)))
        self.assertNotIn(chr(0x2014), t)


if __name__ == "__main__":
    unittest.main()

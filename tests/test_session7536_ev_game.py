"""Session 7536 (chain 304): Should your family get an EV? (/play/ev) at the done line.

Energy Research Warehouse (ERW). No network, no model, no warehouse table written.

- ThePageDrawn     site/scripts/test-ev-game-render.mjs (the faults fixed, the decisions fold) and
                   site/scripts/ev-game-figures.mjs --check (the game drawn for the 63 cases prints the committed figures).
- TheReplication   replication/ev_game/: every figure inside its tolerance, the headline figures, the do-file's expected
                   lines, the cross-check's published figures, and the prices against the tables when they are on the copy.
- TheNote          docs/methods/ev_game.md names the decisions, the replication's count and the cross-check.
- TheFaults        docs/reviews/ev-game-faults-2026-11-16.md: numbered rows, each with its kind and state.

    python -m unittest tests.test_session7536_ev_game -v
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
REP = os.path.join(ROOT, "replication", "ev_game")
NODE = shutil.which("node")
EM_DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def replicate(*args):
    r = subprocess.run([sys.executable, os.path.join(REP, "replicate.py"), *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=300)
    return r.returncode, r.stdout


@unittest.skipUnless(NODE, "node is not installed")
@unittest.skipUnless(os.path.isdir(os.path.join(SITE, "node_modules")), "site/node_modules is not on this copy")
class ThePageDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run = lambda *a: subprocess.run([NODE, "--import", "./scripts/tsx-register.mjs", *a], cwd=SITE, capture_output=True, text=True, encoding="utf-8", timeout=600)  # noqa: E731
        cls.render = run("scripts/test-ev-game-render.mjs")
        cls.figures = run("scripts/ev-game-figures.mjs", "--check")

    def test_render_checks_pass(self):
        self.assertEqual(self.render.returncode, 0, self.render.stdout[-3000:] + self.render.stderr[-1500:])
        self.assertNotIn("FAIL", self.render.stdout)
        self.assertIn("all passed", self.render.stdout)
        self.assertGreaterEqual(self.render.stdout.count("ok  "), 21)

    def test_the_game_prints_the_committed_figures(self):
        self.assertEqual(self.figures.returncode, 0, self.figures.stdout[-3000:] + self.figures.stderr[-1500:])
        self.assertIn("5139 figures, as committed", self.figures.stdout)   # 5139: wip/alt-ev-game-1, California's time-of-use tip names no month (main: 5141)


class TheReplication(unittest.TestCase):
    def test_every_figure_inside(self):
        code, out = replicate()
        self.assertEqual(code, 0, out[-3000:])
        self.assertIn("5139 of 5139 inside half the page's last shown digit (63 cases)", out)   # wip/alt-ev-game-1 (main: 5141)
        self.assertNotIn("NOT INSIDE", out)
        self.assertNotIn("NOT EQUAL", out)

    def test_headline_matches_the_do_file(self):
        code, out = replicate("--headline")
        self.assertEqual(code, 0, out)
        do = src("replication", "ev_game", "replicate.do")
        for line in out.splitlines():
            if re.match(r"^\d ", line):
                self.assertIn(f"*   {line}", do, line)

    def test_cases_cover_the_outcomes(self):
        page = json.load(open(os.path.join(REP, "page_figures.json"), encoding="utf-8"))
        shown = {(c["id"], f["key"]): f["shown"] for c in page["cases"] for f in c["figures"]}
        self.assertEqual(shown[("ohio_cheaper_ev", "payback")], "at once")
        self.assertEqual(shown[("never", "payback")], "never")
        self.assertEqual(shown[("never", "save_year_label")], "Extra a year with the EV")
        self.assertEqual(shown[("no_cross", "chart_cross_label")], "none")
        self.assertIn("public charger", shown[("public_waiting", "waiting")])
        self.assertEqual(shown[("state_KY", "payback")], "3.3 years")  # session 7052: the prices of the file built 17 November 2026
        self.assertEqual(shown[("state_HI", "npv")], "-$2,720")  # session 7052: the same
        self.assertEqual(len([c for c in page["cases"] if c["id"].startswith("state_")]), 51)

    def test_crosscheck_prints_the_published_figures(self):
        code, out = replicate("--crosscheck")
        self.assertEqual(code, 0, out)
        self.assertIn("EIA weekly series: 3.995 | +0.000", out)  # session 7052: the week of 2026-11-09
        self.assertIn("PG&E E-TOU-C", out)


class TheNote(unittest.TestCase):
    def test_note_names_the_work(self):
        note = src("docs", "methods", "ev_game.md")
        self.assertIn("## The game at the done line (session 7536", note)
        self.assertIn("5,141 of 5,141 figures", note)
        self.assertIn("### The cross-check", note)
        self.assertIn("### Which section of this note holds", note)
        self.assertNotIn(EM_DASH, note)
        dec = src("site", "app", "play", "ev", "Decisions.tsx")
        keys = re.findall(r'key: "([a-z-]+)"', dec)
        self.assertEqual(len(keys), 11)
        for k in keys:
            self.assertIn(f"`{k}`", note, k)

    def test_note_keeps_the_older_sections(self):
        note = src("docs", "methods", "ev_game.md")
        for h in ("## The prices: real, from the warehouse", "## One screen, sources on hover", "### The figures keyed for check-values"):
            self.assertIn(h, note)


class TheFaults(unittest.TestCase):
    def test_rows(self):
        text = src("docs", "reviews", "ev-game-faults-2026-11-16.md")
        rows = re.findall(r"^\| (\d+) \| (site|data machine|ruling) \|", text, re.M)
        self.assertEqual([int(n) for n, _ in rows], list(range(1, 12)))
        kinds = [k for _, k in rows]
        self.assertEqual((kinds.count("site"), kinds.count("data machine"), kinds.count("ruling")), (3, 2, 6))
        self.assertNotIn(EM_DASH, text)


if __name__ == "__main__":
    unittest.main()

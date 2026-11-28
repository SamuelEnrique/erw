"""Session 10404 (chain 720, part E): the waiting problem set "A forecast's report card".

The set reads site/data/predict/scores.json (window B's file) and is a waiting set: it has its page, and it is in no
index and no dated edition until the owner approves it. The Node test builds it, recomputes every figure from the file,
finds each figure again by the row its question names, and draws the page.

    python -m pytest tests/test_session10404_problem_set_forecast.py
"""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
REACT = os.path.isdir(os.path.join(SITE, "node_modules", "react"))
SCORES = os.path.isfile(os.path.join(SITE, "data", "predict", "scores.json"))
DASH, EN = chr(0x2014), chr(0x2013)
SLUG = "a-forecasts-report-card"


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheSetWaits(unittest.TestCase):
    def test_it_is_a_waiting_set_and_not_a_listed_one(self):
        text = src("site", "lib", "problems.ts")
        # ready branch wip/ready-forecast-problem-set-listed (session 11408): listed, no longer waiting
        self.assertIn("const WAITING_MODULES = [PRODUCER];", text)
        self.assertIn("  REPORT.META,", text)
        self.assertIn("for (const m of [TRADE, STORM, GROUND, WHERE, AUTH, REPORT]) addGuide(m.META.slug, m.GUIDE_ENTRY);", text)
        # the line the problem kit's test pins is kept
        self.assertIn("questions: inOrder(built.questions, GUIDE[slug]?.order ?? [])", text)

    def test_nothing_freezes_or_opens_it(self):
        self.assertIn("for (const meta of SETS)", src("site", "scripts", "build-problem-edition.mjs"))
        self.assertNotIn(SLUG, src("site", "lib", "release.ts"))
        editions = os.path.join(SITE, "data", "problem_editions")
        for name in os.listdir(editions):
            self.assertNotIn(SLUG, src("site", "data", "problem_editions", name), name)
        self.assertFalse(any(SLUG in d for d in os.listdir(os.path.join(SITE, "public", "problems"))))

    def test_the_value_check_reads_its_page(self):
        self.assertIn(f'"/learn/problems/{SLUG}"', src("site", "scripts", "check-values.mjs"))

    def test_the_module_keeps_the_rules(self):
        text = src("site", "lib", "problemsets", f"{SLUG}.ts")
        self.assertNotIn(DASH, text)
        self.assertNotIn(EN, text)
        self.assertIn('const F = "predict/scores.json";', text)
        # nothing of the Economic impact tool, whose code owns the word "forecast"
        self.assertIsNone(re.search(r'from "@/(lib/forecast|data/forecast|app/impact)', text))
        # a row is found by what it is, never by a typed position
        self.assertIsNone(re.search(r'\["rows", \d', text))
        for name in ("META", "GUIDE_ENTRY", "DECISIONS", "build"):
            self.assertRegex(text, rf"export (const|async function) {name}\b")

    def test_the_other_sets_page_takes_the_waiting_choices_only_from_the_page(self):
        text = src("site", "app", "learn", "problems", "Decisions.tsx")
        self.assertIn(": PROBLEM_DECISIONS;", text)  # the index draws the listed sets' choices alone
        self.assertIn("  ...REPORT_DECISIONS,", text)  # ready branch of session 11408: the set is listed


class TheNodeTest(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT and SCORES, "node, the site's packages or site/data/predict/scores.json are not here")
    def test_every_figure_is_the_files_and_is_drawn(self):
        r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/test-problem-set-forecast.mjs"],
                           capture_output=True, text=True, cwd=SITE, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks; the set listed, 6 questions and 1 example, \d+ keyed figures recomputed from the file, \d+ found on the drawn page")


if __name__ == "__main__":
    unittest.main()

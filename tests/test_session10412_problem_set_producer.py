"""Session 10412 (chain 720, part E): the waiting problem set "A producer beside the price of oil".

The chain asked for a problem set of the equities page, "a segment beside an energy price". No segment has a line: a
segment's line is built from share prices, and every share price is held ("license needed"). Since 27 November 2026 the
equities files hold what each company filed with the SEC, which is public. The set reads those figures for one oil and
gas producer (and a second, of mostly natural gas, in its last question) beside the spot price of the fuel on the same
days. It reads no share price, index or segment line.

It is a waiting set: it has its page, and it is in no index and no dated edition until the owner approves it. The Node
test builds it, recomputes every figure from the files, finds each figure again by the period its question names, finds
the producer again by the set's rule, and draws the page.

    python -m pytest tests/test_session10412_problem_set_producer.py
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
FILES = os.path.isfile(os.path.join(SITE, "data", "equities", "series", "EOG.json"))
DASH, EN = chr(0x2014), chr(0x2013)
SLUG = "a-producer-beside-the-price-of-oil"


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheSetWaits(unittest.TestCase):
    def test_it_is_a_waiting_set_and_not_a_listed_one(self):
        text = src("site", "lib", "problems.ts")
        self.assertIn("const WAITING_MODULES = [REPORT, PRODUCER];", text)
        self.assertIn('import * as PRODUCER from "@/lib/problemsets/a-producer-beside-the-price-of-oil";', text)
        # the listed sets and their guide are as they were: no waiting module is in either line
        self.assertIn("...[TRADE, STORM, GROUND, WHERE, AUTH].map((m) => m.META),", text)
        self.assertIn("for (const m of [TRADE, STORM, GROUND, WHERE, AUTH]) addGuide(m.META.slug, m.GUIDE_ENTRY);", text)

    def test_nothing_freezes_or_opens_it(self):
        self.assertIn("for (const meta of SETS)", src("site", "scripts", "build-problem-edition.mjs"))
        self.assertNotIn(SLUG, src("site", "lib", "release.ts"))
        self.assertNotIn(SLUG, src("site", "lib", "pages.ts"))
        editions = os.path.join(SITE, "data", "problem_editions")
        for name in os.listdir(editions):
            self.assertNotIn(SLUG, src("site", "data", "problem_editions", name), name)
        self.assertFalse(any(SLUG in d for d in os.listdir(os.path.join(SITE, "public", "problems"))))
        self.assertNotIn(SLUG, src("site", "app", "learn", "problems", "Decisions.tsx"))

    def test_the_value_check_reads_its_page(self):
        self.assertIn(f'"/learn/problems/{SLUG}"', src("site", "scripts", "check-values.mjs"))

    def test_the_module_keeps_the_rules(self):
        text = src("site", "lib", "problemsets", f"{SLUG}.ts")
        self.assertNotIn(DASH, text)
        self.assertNotIn(EN, text)
        # a period's row is found by what it is, never by a typed position
        self.assertIsNone(re.search(r'\["quarterly", \d', text))
        self.assertIsNone(re.search(r'\["daily", [^,\]]+, \d', text))
        # no share price, index or segment line: each is held, and the set reads none
        for held in ('"close"', '"adj_close"', '"market_value"', "indices", "segments/"):
            self.assertNotIn(held, text, held)
        for name in ("META", "GUIDE_ENTRY", "DECISIONS", "build", "TICKER", "SECOND", "SEGMENT"):
            self.assertRegex(text, rf"export (const|async function) (\w+ = [^;]+, )?{name}\b")

    def test_the_method_note_has_the_set(self):
        note = src("docs", "methods", "problem_sets.md")
        self.assertIn(f"`/learn/problems/{SLUG}`", note)
        self.assertNotIn(DASH, note)


class TheNodeTests(unittest.TestCase):
    @unittest.skipUnless(NODE and REACT and FILES, "node, the site's packages or the equities page files are not here")
    def test_every_figure_is_the_files_and_is_drawn(self):
        r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/test-problem-set-producer.mjs"],
                           capture_output=True, text=True, encoding="utf-8", cwd=SITE, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        self.assertRegex(r.stdout, r"ok: \d+ checks; a waiting set, 6 questions and 1 example, \d+ keyed figures recomputed from the files, \d+ found on the drawn page")

    @unittest.skipUnless(NODE and REACT and os.path.isfile(os.path.join(SITE, "data", "predict", "scores.json")), "node, the site's packages or site/data/predict/scores.json are not here")
    def test_the_first_waiting_set_stands(self):
        r = subprocess.run([NODE, "--import", "./scripts/problem-sets-register.mjs", "scripts/test-problem-set-forecast.mjs"],
                           capture_output=True, text=True, encoding="utf-8", cwd=SITE, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])


if __name__ == "__main__":
    unittest.main()

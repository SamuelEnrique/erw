"""Ready branch for /forecast (session 11408, chain 770 part C; weekend page 2026-11-28, part 3.5, "the forecast's problem
set (Texas: the ERW forecast 5.47 percent off against the operator's 2.39): list it with the other sets, or keep it
waiting"). Not the default: it waits for Samuel's ruling.

The other choice: /learn/problems/a-forecasts-report-card is listed: in SETS with the sets of the whole country (its
module in COUNTRY and the guide; site/lib/problems.ts), its three choices in PROBLEM_DECISIONS
(site/app/learn/problems/Decisions.tsx) and in docs/methods/problem_sets.md's list. On main the index lists 10 sets and
there are 2 waiting; here 11 listed and 1 waiting. No dated edition holds it until the next one is built; its replication
in Python and Stata is not written (the note says so). site/scripts/test-problem-set-forecast.mjs and
tests/test_session10404_problem_set_forecast.py are turned."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheReportCardIsListed(unittest.TestCase):
    def test_in_the_lists(self):
        t = src("site", "lib", "problems.ts")
        self.assertIn("  REPORT.META,\n];", t)
        self.assertIn("Object.fromEntries([TRADE, STORM, GROUND, WHERE, AUTH, REPORT].map((m) => [m.META.slug, m]))", t)
        self.assertIn("const WAITING_MODULES = [PRODUCER];", t)
        d = src("site", "app", "learn", "problems", "Decisions.tsx")
        self.assertIn('import { DECISIONS as REPORT_DECISIONS } from "@/lib/problemsets/a-forecasts-report-card";', d)
        self.assertIn("  ...REPORT_DECISIONS,\n];", d)

    def test_the_note(self):
        n = src("docs", "methods", "problem_sets.md")
        for key in ("report-card-place", "report-card-hours", "report-card-same-hours"):
            self.assertRegex(n, rf"(?m)^\| `{key}` \|")
        self.assertIn("**Listed (ready branch of session 11408, not the default).**", n)

    def test_no_edition_holds_it_yet(self):
        d = os.path.join(ROOT, "site", "data", "problem_editions")
        for name in os.listdir(d):
            self.assertNotIn("a-forecasts-report-card", src("site", "data", "problem_editions", name), name)
        self.assertIsNone(re.search(r"a-forecasts-report-card", src("site", "lib", "release.ts")))


if __name__ == "__main__":
    unittest.main()

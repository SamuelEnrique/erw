"""Audit of the home page, finding 2 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the Analysis group's
line ended "and the Thesis Builder, every answer from the tables". A Thesis Builder run (warehouse/thesis/run.py,
execute_market since session 169) researches the market with web search and draws its trends from the EIA's and FRED's
series; the tool is internal (the page is not found without the internal view's cookie).

1. The runner's market research uses web search, and searches for no company. Passes on main.
2. The fix on this branch, words only: "every answer from the tables" is said of the tools that read the tables, and the
   Thesis Builder is named as internal, its reports citing the web pages and public series they rest on. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheAnalysisLine(unittest.TestCase):
    def test_the_thesis_builder_reads_the_web(self):
        run = src("warehouse", "thesis", "run.py")
        self.assertIn("COMPANY_SEARCH = False", run)
        self.assertIn("Research this niche for an investor who is new to it, with web search.", run)
        self.assertIn("if (!(await internalOk((await cookies()).get(COOKIE)?.value))) notFound();", src("site", "app", "thesis", "page.tsx"))

    def test_the_line_says_so(self):
        line = re.search(r'  Analysis: "([^"]+)",', src("site", "app", "page.tsx")).group(1)
        self.assertNotIn("the Thesis Builder, every answer from the tables", line)
        self.assertIn("the events and policy, every answer from the tables; and the Thesis Builder, internal, whose market reports cite the web pages and public series they rest on.", line)


if __name__ == "__main__":
    unittest.main()

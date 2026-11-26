"""Audit of the Thesis Builder, finding 12 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): its line in
site/lib/pages.ts (drawn on /about and /data) said "Type a niche and get a sourced investment map of it: ... the company
landscape, the deal funnel, the pipeline, ...". Since the owner's ruling of 8 October 2026 (session 169) a run searches
for no company (warehouse/thesis/run.py, COMPANY_SEARCH = False): it writes the market report, and the landscape, the
funnel and the pipeline are connector tabs until a person pastes a provider's answer. The report is neutral by rule.

1. The switch is off and the connector tabs say what fills them. Passes on main.
2. The fix on this branch, words only: the line names the market report's parts, and says the three company tabs fill
   from a provider's answer pasted from the reader's own account, and that the tool is internal. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheThesisLine(unittest.TestCase):
    def test_no_run_searches_for_companies(self):
        run = src("warehouse", "thesis", "run.py")
        self.assertIn("COMPANY_SEARCH = False", run)
        self.assertIn('CONNECTOR_NOTE = "Connect PitchBook or Harmonic to fill this"', run)
        self.assertIn('"landscape": COMPANY_COLUMNS, "funnel": FUNNEL_COLUMNS, "pipeline": COMPANY_COLUMNS', run)

    def test_the_line_says_so(self):
        line = re.search(r'href: "/thesis", label: "Thesis Builder", line: "([^"]+)"', src("site", "lib", "pages.ts")).group(1)
        self.assertNotIn("investment map", line)
        self.assertIn("sourced market report", line)
        self.assertIn("the company landscape, deal funnel and pipeline fill from a data provider's answer you paste from your own account. Internal.", line)


if __name__ == "__main__":
    unittest.main()

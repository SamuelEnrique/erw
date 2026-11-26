"""Audit of the Thesis Builder, finding 14 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the method note's
sections "Which companies are on the map" and "The confidence score" were written as the present ("Companies come from
three places: the ERW's own companies and deals tables, web search, and PitchBook"), while the note's own lead says the
ERW does not search for companies since 9 October 2026 (warehouse/thesis/run.py, COMPANY_SEARCH = False). A run since
then fills its company tabs from a provider's pasted answer only (site/lib/thesis/view.ts, connectorRows: no score).

1. No run searches for companies, and the connector tabs carry no score. Passes on main.
2. The fix on this branch, words only: both sections say they describe a run written before 9 October 2026. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class TheCompanySections(unittest.TestCase):
    def test_no_company_search_and_no_score_since(self):
        self.assertIn("COMPANY_SEARCH = False", src("warehouse", "thesis", "run.py"))
        view = src("site", "lib", "thesis", "view.ts")
        body = view[view.index("export function connectorRows"):]
        body = body[:body.index("\n}\n")]
        self.assertNotIn("confidence", body)

    def test_the_sections_say_so(self):
        note = flat(src("docs", "methods", "thesis.md"))
        self.assertNotIn("Companies come from three places", note)
        self.assertIn("This section and the next describe a run written before 9 October 2026. A run since then searches for no company", note)
        self.assertIn("In such a run companies came from three places", note)
        self.assertIn("In a run written before 9 October 2026, each company has a score from 0 to 100", note)


if __name__ == "__main__":
    unittest.main()

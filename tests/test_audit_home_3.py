"""Audit of the home page, finding 3 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the Analysis figure is
the length of site/data/findings/catalogue.json, drawn "11 findings ... In the research library today". The catalogue is
what a person may ask for on /research, and the research flow (site/lib/analysisflow.ts) says what it holds: seven
findings, three of them with two versions, and the impact study.

1. The catalogue's entries are the seven findings, three later forms and the impact study. Passes on main.
2. The fix on this branch, words only: the unit is "analyses" and the note says what they are. The figure (the
   catalogue's length) does not move. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheAnalysisFigure(unittest.TestCase):
    def test_the_catalogue_holds_analyses(self):
        ids = [c["id"] for c in json.loads(src("site", "data", "findings", "catalogue.json"))]
        later = [i for i in ids if i.endswith("_grids") or i.endswith("_hourly")]
        self.assertEqual(len(ids), 11)
        self.assertEqual(len(later), 3)
        self.assertIn("impact_study", ids)
        self.assertEqual(len(ids) - len(later) - 1, 7)
        self.assertIn("So the list shows seven findings, three of them with two versions", " ".join(src("site", "lib", "analysisflow.ts").split()).replace("// ", ""))

    def test_the_words_say_so(self):
        page = src("site", "app", "page.tsx")
        self.assertIn('raw={findings.length}>{n0(findings.length)}</Num>, unit: "analyses"', page)
        self.assertIn("Analyses you can run in the research library, each with the inputs you choose: seven findings, three of them in two versions, and the impact study.", page)
        self.assertNotIn("In the research library today", page)


if __name__ == "__main__":
    unittest.main()

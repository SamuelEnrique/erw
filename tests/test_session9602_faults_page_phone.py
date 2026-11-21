"""Session 9602 (chain 620, 20 November 2026): /data/faults fits a phone's width.

Energy Research Warehouse (ERW). Every page of the site with a fixed address (80) was opened at 390 px on production.
`/data/faults` was 417 px wide: a long unbroken word in a fault's evidence ran out of its list of terms. The page is
not drawn in the prose style, so the rule added for the method pages does not reach it.

Held here, on the source: the list of a fault's terms breaks a word that does not fit its line, with the class the
site already uses for that elsewhere; the terms themselves are as they were. With that style put on production's page
in a browser the page is 390 px wide. Nothing here sets the environment, reads a table or makes a request.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheFaultsPage(unittest.TestCase):
    def setUp(self):
        self.p = src("site", "app", "data", "faults", "page.tsx")

    def test_the_list_of_terms_breaks_a_word_that_does_not_fit(self):
        self.assertIn('<dl className="space-y-2 text-sm break-words">', self.p)
        self.assertNotIn('<dl className="space-y-2 text-sm">', self.p)

    def test_the_terms_are_as_they_were(self):
        for piece in ('<dt className="font-semibold">Evidence</dt><dd>{f.evidence}</dd>', '<dt className="font-semibold">What the ERW does</dt><dd>{f.erw_does}</dd>'):
            self.assertIn(piece, self.p)

    def test_the_class_is_one_the_site_already_uses(self):
        uses = 0
        for folder, _, files in os.walk(os.path.join(ROOT, "site", "app")):
            for f in files:
                if f.endswith(".tsx") and "break-words" in src(folder, f):
                    uses += 1
        self.assertGreater(uses, 3)

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.p)
        self.assertNotIn(EM, src("tests", "test_session9602_faults_page_phone.py"))


if __name__ == "__main__":
    unittest.main()

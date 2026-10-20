"""Session 334 (the chain of 20 October 2026, night): /thesis (Thesis Builder version 1 as it stands; version 2 on hold,
no feature work) and /severance finished to the five tools' standard, lighter. /severance offers its one table on both
tabs; the two notes say what the pages draw today. Energy Research Warehouse (ERW)."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheSeverance(unittest.TestCase):
    def test_both_tabs_offer_the_price_table_they_read(self):
        page = src("site", "app", "severance", "page.tsx")
        self.assertIn('const T = "eia_fuel_spot_prices";', page)
        self.assertIn("          <TableDownloads tables={[T]} />\n        </div>", page)
        self.assertIn("<Cite tables={[T]}", src("site", "app", "severance", "lease", "view.tsx"))   # the lease tab reads it too

    def test_the_calculator_keeps_its_reset_and_its_written_default(self):
        c = src("site", "app", "severance", "Calculator.tsx")
        self.assertIn("Reset to the defaults</button>", c)
        self.assertIn("Default price (an assumption, edit it):", c)


class TheThesis(unittest.TestCase):
    def test_no_feature_changed_and_the_note_says_why_nothing_is_offered(self):
        self.assertNotIn("TableDownloads", src("site", "app", "thesis", "page.tsx"))
        note = src("docs", "methods", "thesis.md")
        self.assertIn("## The page as it stands (session 334, 20 October 2026)", note)
        self.assertIn("## The pages as they stand (session 334, 20 October 2026)", src("docs", "methods", "severance.md"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "severance", "page.tsx"), ("docs", "methods", "thesis.md"), ("docs", "methods", "severance.md"), ("tests", "test_session334.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()

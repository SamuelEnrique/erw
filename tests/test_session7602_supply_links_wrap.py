"""Session 7602 (chain 305, the portable laptop): row 179 of docs/state/browser_reads_wanted.md, read in a browser at
390 px. `/supply`'s line of links under "Fuel burned for power in the seven grids" ("ERCOT mix, neighbours; CAISO ...")
drew each grid in a span that does not break, and the "; " between two grids stood inside the next span, so the line
had no place to break at all: at 390 px it ran to 899 px and the page scrolled sideways. The "; " now stands outside
the span: the line breaks between two grids and each grid's three words stay together.
Energy Research Warehouse (ERW)."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheLinksLineCanBreak(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "app", "supply", "page.tsx")

    def test_the_separator_is_outside_the_unbreakable_span(self):
        self.assertIn('<Fragment key={g.slug}>{i ? "; " : ""}<span className="whitespace-nowrap">{g.label} ', self.s)
        self.assertNotIn('<span key={g.slug} className="whitespace-nowrap">{i ? "; " : ""}', self.s)

    def test_fragment_is_imported(self):
        self.assertIn('import { Fragment } from "react";', self.s)

    def test_no_dash(self):
        for ch in DASHES:
            self.assertNotIn(ch, self.s)


if __name__ == "__main__":
    unittest.main()

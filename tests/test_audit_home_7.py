"""Audit of the home page, finding 7 (session 10236, docs/reviews/home-model-audit-2026-11-26.md): the source line said
"Every number on this page is read from the ERW's tables and checked against them". The strip's and the five groups'
figures are Nums checked against their tables, and today's chart's fact is its table's; the Digest block's stories are
the news as each outlet reported it (the issue of 6 November: "$33.1 ..."; 12 November's "What moved": "USD 74 billion").

1. The Digest's stories carry numbers no ERW table holds. Passes on main.
2. The fix on this branch, words only: the line says which figures are read from the tables and checked, and that the
   Digest's stories are the news as each source reported it. Fails on main.
Nothing here sets the environment, reads a table or makes a request."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheSourceLine(unittest.TestCase):
    def test_the_stories_carry_the_news_numbers(self):
        old = src("docs", "digest", "2026-11-06.md")
        top = old[old.index("## Top of the industry"):old.index("## By sector")]
        self.assertRegex(top, r"\$\d")
        self.assertIn("dangerouslySetInnerHTML={{ __html: render(md, \"docs/digest/latest.md\") }}", src("site", "app", "page.tsx"))

    def test_the_line_says_so(self):
        page = src("site", "app", "page.tsx")
        self.assertNotIn("Every number on this page is read from the ERW", page)
        self.assertIn("Every figure of the strip and the five groups is read from the ERW&apos;s tables and checked against them, and today&apos;s chart from its table; the analyses are counted from the library&apos;s own catalogue; the Digest&apos;s stories are the news as each source reported it.", page)


if __name__ == "__main__":
    unittest.main()

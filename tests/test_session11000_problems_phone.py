"""Session 11000 (chain 750, the browser read of 26 November 2026): /learn/problems on a phone of 360 px.

Every address of the site was opened as a phone 360 px wide (and 320 px, the width WCAG 1.4.10 asks a page to fit),
beside the chain's own 390 px. /learn/problems was 373 px wide at both: each set's line of facts names its tables and
its page files in mono, and a name such as "site/data/regions/events/elliott_2022.json" is one word that cannot wrap.
The page fitted from 375 px up, so the 390 px reads never met it. With overflow-wrap: anywhere on the line (tried on
production's own page in a browser: 320 of 320 and 360 of 360, and no line's height changed at 390 or 1280 px) a name
too long for the line breaks, and the page keeps to the screen.

Energy Research Warehouse (ERW). No network, no build: the page's source is read.

    python -m unittest tests.test_session11000_problems_phone -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src():
    with open(os.path.join(ROOT, "site", "app", "learn", "problems", "page.tsx"), encoding="utf-8") as f:
        return f.read()


class TheFactsLineWraps(unittest.TestCase):
    def test_the_line_of_a_sets_facts_lets_a_long_name_break(self):
        tags = re.findall(r"<div\b[^>]*data-set-facts=\{s\.slug\}[^>]*>", src())
        self.assertEqual(len(tags), 1, "the list draws one line of facts a set: read this test again")
        cls = re.search(r'className="([^"]*)"', tags[0])
        self.assertIsNotNone(cls)
        self.assertIn("[overflow-wrap:anywhere]", cls.group(1).split(), "a table name or a file path in mono is one word: without this the page is wider than a 360 px phone")

    def test_the_line_still_holds_the_names_that_were_too_wide(self):
        # what made the page wide: the tables and the page files, each in mono, inside the line of facts
        text = src()
        at = text.index("data-set-facts={s.slug}")
        line = text[at:text.index("</div>", at)]
        self.assertIn('className="font-mono">{t}</Link>', line)
        self.assertIn('<span className="font-mono">site/data/{f}</span>', line)


if __name__ == "__main__":
    unittest.main()

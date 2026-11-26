"""Session 11000 (chain 750, the browser read of 26 November 2026): a link told by its color alone on /events.

Each event of the list ends its line "Reached N of M regions: ..." with the link "The whole country". The line is a
span set as a block (site/app/events/WholeCountry.tsx, RegionsReached), and the brand's rule that underlines a link in
running text reads paragraphs, list items and table cells (site/app/tokens.css: ".brand-a p a, .brand-a li a,
.brand-a td a"), not a span. On production the nine links were drawn with no underline, in the weight of the words
around them, cardinal against ink at 1.47 to 1: a reader who does not see the color could not tell the link from its
sentence (AccessLint, link-in-text-block, WCAG 1.4.1; 39 pages audited, these nine links the only ones). The link now
carries the underline class, as the site's other links outside a paragraph do.

Energy Research Warehouse (ERW). No network, no build: the source is read.

    python -m unittest tests.test_session11000_events_link -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheWholeCountryLinkIsUnderlined(unittest.TestCase):
    def setUp(self):
        self.src = read("site", "app", "events", "WholeCountry.tsx")

    def test_the_link_of_the_regions_line_carries_an_underline(self):
        links = re.findall(r"<Link\b[^>]*>The whole country</Link>", self.src)
        self.assertEqual(len(links), 1, "the list's line holds one link named The whole country: read this test again")
        tag = links[0]
        self.assertIn("#whole-country", tag)
        cls = re.search(r'className="([^"]*)"', tag)
        self.assertIsNotNone(cls, "the link has no class: in a span it is told by its color alone")
        self.assertIn("underline", cls.group(1).split())
        self.assertNotIn("no-underline", cls.group(1).split())

    def test_the_line_is_still_a_span_the_brand_rule_does_not_read(self):
        # the reason the link needs a class of its own: were the line a paragraph, the brand's rule would underline it
        self.assertIn('<span data-regions-reached={event} className="mt-1 block text-sm">{body}</span>', self.src)
        rule = read("site", "app", "tokens.css")
        block = rule[rule.index("/* ---- links: underlined in running text */"):]
        selectors = block[:block.index("{")]
        self.assertIn(".brand-a p a", selectors)
        self.assertNotIn("span", selectors, "the brand's rule now reads spans: the link's own class may no longer be needed")

if __name__ == "__main__":
    unittest.main()

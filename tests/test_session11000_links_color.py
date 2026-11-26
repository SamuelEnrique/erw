"""Session 11000 (chain 750, the browser read of 26 November 2026): two more links told by their color alone.

After the accessibility audit found the link "The whole country" on /events (tests/test_session11000_events_link.py),
every link of 199 addresses was read in a browser for the same thing (runs/c750/links_bare.mjs: 15,042 links drawn;
a link that stands inline in at least 20 characters of words, with no underline, edge or weight of its own, and less
than 3 to 1 against those words). Two more places:

1. /curtailment, the note under "Taken in by the batteries": "The storage page's daily charging nets each hour first".
   The note is the grey block the brand's rule reads (".brand-a div.text-muted > a:not([class])", session 583), but
   the link stands one level down, in the span that marks the sentence, so the rule's child selector misses it:
   cardinal against the captions grey, 1.67 to 1, no underline.
2. /play/ev, in the fold of what the game assumed: "Prices built into the game on <day>. How it works." The sentence
   is a span in a row of the page, not a paragraph: 1.47 to 1, no underline.

Each link now carries the underline class (WCAG 1.4.1), as the site's other links outside a paragraph do.

Energy Research Warehouse (ERW). No network, no build: the source is read.

    python -m unittest tests.test_session11000_links_color -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def classes(tag):
    m = re.search(r'className="([^"]*)"', tag)
    return m.group(1).split() if m else []


class TheTwoLinksAreUnderlined(unittest.TestCase):
    def test_curtailment_the_storage_page_link(self):
        src = read("site", "app", "curtailment", "page.tsx")
        tags = re.findall(r"<SiteLink\b[^>]*>storage page</SiteLink>", src)
        self.assertEqual(len(tags), 1, "the note holds one link named storage page: read this test again")
        self.assertIn('href="/storage"', tags[0])
        self.assertIn("underline", classes(tags[0]), "in a span of the grey note the link is told by its color alone")
        # why the brand's rule does not reach it: the link is a child of the sentence's span, not of the note's block
        self.assertIn('<span data-storage-count="1">The <SiteLink', src)
        self.assertIn(".brand-a div.text-muted > a:not([class])", read("site", "app", "tokens.css"))

    def test_the_ev_game_the_how_it_works_link(self):
        src = read("site", "app", "play", "ev", "EvGame.tsx")
        tags = re.findall(r"<Link\b[^>]*>How it works</Link>", src)
        self.assertEqual(len(tags), 1, "the fold holds one link named How it works: read this test again")
        self.assertIn('href="/data/methods/ev_game"', tags[0])
        self.assertIn("underline", classes(tags[0]), "in a span of the fold the link is told by its color alone")


if __name__ == "__main__":
    unittest.main()

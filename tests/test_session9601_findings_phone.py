"""Session 9601 (chain 620, 20 November 2026): /internal/findings fits a phone's width.

Energy Research Warehouse (ERW). Row 428 of `docs/state/browser_reads_wanted.md`, read on production at 390 px: the
page was 470 px wide. The filters, the bar of counts and the do-file's text all fitted (chain 507's work); the cause
was older: the caption draft of a hunt's draft (a `pre` of session 233) kept its lines' breaks and broke no word, so a
long word (an address, a table's name) ran out of its box and widened the page.

Held here, on the source: the caption's box keeps its line breaks and breaks a word that does not fit; the page's
other boxes of kept text do the same or scroll inside themselves; the box is still the one session 233's test names.
The proof in a browser is the page at 390 px on a build (document width 390).
Nothing here sets the environment, reads a table or makes a request.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheCaption(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "internal", "findings", "page.tsx")

    def test_the_captions_box_keeps_its_lines_and_breaks_a_long_word(self):
        box = re.search(r'<pre className="([^"]*)" data-hunt-caption=\{id\}>\{hunt\.caption\}</pre>', self.page)
        self.assertIsNotNone(box, "the caption's box is still the one session 233 drew")
        classes = box.group(1).split()
        self.assertIn("whitespace-pre-wrap", classes)
        self.assertIn("[overflow-wrap:anywhere]", classes)

    def test_every_box_of_kept_text_on_the_page_breaks_or_scrolls(self):
        for m in re.finditer(r'<pre className="([^"]*)"', self.page):
            classes = m.group(1).split()
            self.assertTrue("[overflow-wrap:anywhere]" in classes or "break-words" in classes or "break-all" in classes or any(c.startswith("overflow-x-") or c == "overflow-auto" for c in classes), m.group(0))

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.page)
        self.assertNotIn(EM, src("tests", "test_session9601_findings_phone.py"))


if __name__ == "__main__":
    unittest.main()

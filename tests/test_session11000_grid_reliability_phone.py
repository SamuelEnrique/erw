"""Session 11000 (chain 750, the browser read of 26 November 2026): /grid?grid=caiso was 539 px wide at 390 px.

Session 9819 gave each empty cell of the reliability table (site/components/grid/Reliability.tsx, the alert days by
year) a label a screen reader says, "none", in the class sr-only. That class places the label "absolute". The table
stands in a frame that scrolls sideways (overflow-x-auto), and a frame that is not positioned is not the containing
block of an absolute label inside it, so it does not clip the label: the 60 labels of the columns past the frame's
right edge widened the whole page (read on production at 390 px: 539 of 390; with the frame made "relative" in the
page, 390 of 390, the table still scrolling inside its frame and still saying "none").

The rule this test holds, for this component: a frame that scrolls sideways and holds sr-only labels is "relative".

Energy Research Warehouse (ERW). No network, no build: the source is read.

    python -m unittest tests.test_session11000_grid_reliability_phone -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def frames(text):
    """Each <div> whose class holds overflow-x-auto, with the text up to its closing tag: (classes, inside)."""
    out = []
    for m in re.finditer(r'<div className="([^"]*\boverflow-x-auto\b[^"]*)">', text):
        depth, at = 1, m.end()
        for t in re.finditer(r"<div\b|</div>", text[m.end():]):
            depth += 1 if t.group(0) == "<div" else -1
            if depth == 0:
                at = m.end() + t.start()
                break
        out.append((m.group(1).split(), text[m.end():at]))
    return out


class TheReliabilityTableOnAPhone(unittest.TestCase):
    def setUp(self):
        self.text = src("site", "components", "grid", "Reliability.tsx")

    def test_the_empty_cell_still_says_none(self):
        # session 9819's fix stands: the label is what this test's rule is about
        self.assertIn('<span className="sr-only">none</span>', self.text)

    def test_a_scrolling_frame_that_holds_sr_only_labels_is_relative(self):
        holding = [(cls, inside) for cls, inside in frames(self.text) if "sr-only" in inside]
        self.assertTrue(holding, "the reliability table's labels are no longer inside a scrolling frame: read this test again")
        for cls, _ in holding:
            self.assertIn("relative", cls, "a frame that scrolls sideways and holds sr-only labels must be relative, or the labels widen the page: " + " ".join(cls))

    def test_the_rule_bites(self):
        # the code as production had it on 26 November fails the rule
        before = self.text.replace('className="relative mb-2 overflow-x-auto"', 'className="mb-2 overflow-x-auto"')
        self.assertNotEqual(before, self.text)
        holding = [cls for cls, inside in frames(before) if "sr-only" in inside]
        self.assertTrue(any("relative" not in cls for cls in holding))


if __name__ == "__main__":
    unittest.main()

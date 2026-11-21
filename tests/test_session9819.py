"""Session 9819 (chain 610, part D): the grid page's reliability table (site/components/grid/Reliability.tsx, the alert
days by year on /grid) drew a year with no days of a kind as a "." in the rule color, about 1.4 to 1 on the page, below
the brand's 4.5 to 1 for text; and a screen reader said "dot". It is drawn in the muted text color, and a screen reader
says "none".

Energy Research Warehouse (ERW). No network, no build: the source and the tokens are read.

    python -m unittest tests.test_session9819 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def lum(hexc):
    rgb = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def token(name):
    return re.search(r"--%s:\s*(#[0-9A-Fa-f]{6})" % re.escape(name), src("site", "app", "tokens.css")).group(1)


class TheEmptyCell(unittest.TestCase):
    def test_it_is_muted_and_says_none(self):
        t = src("site", "components", "grid", "Reliability.tsx")
        self.assertIn(': <span className="text-muted"><span aria-hidden="true">.</span><span className="sr-only">none</span></span>}</td>;', t)
        self.assertNotIn('className="text-rule"', t)

    def test_the_colors(self):
        self.assertLess(contrast(token("color-rule"), token("color-paper")), 3.0)       # what it was
        self.assertGreaterEqual(contrast(token("color-muted"), token("color-paper")), 4.5)


if __name__ == "__main__":
    unittest.main()

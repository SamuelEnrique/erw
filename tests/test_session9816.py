"""Session 9816 (chain 610, part D): the policy monitor's week grid, as a screen reader and the brand's contrast rule
read it (site/app/policy/WeekView.tsx, /policy?view=week).

Energy Research Warehouse (ERW). No network, no build: the source and the tokens are read.

- Each button of the grid (a count of actions, an agency's total) is named by the words its hover gives, not by its
  number alone: a screen reader said "3, toggle button".
- A count of zero is drawn in the muted text color, which passes the brand's 4.5 to 1 for text on the page; at 40
  percent opacity it was about 2 to 1.

    python -m unittest tests.test_session9816 -v
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def token(name):
    m = re.search(r"--%s:\s*(#[0-9A-Fa-f]{6})" % re.escape(name), src("site", "app", "tokens.css"))
    return m.group(1)


def lum(hexc):
    rgb = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def blend(fg, bg, alpha):
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    g = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(alpha * a + (1 - alpha) * b):02x}" for a, b in zip(f, g))


class TheWeekGrid(unittest.TestCase):
    def setUp(self):
        self.t = src("site", "app", "policy", "WeekView.tsx")

    def test_every_button_of_the_grid_is_named_by_its_hover(self):
        buttons = [line for line in self.t.splitlines() if "<button" in line and re.search(r"data-week-(?:cell|total)=", line)]
        self.assertEqual(len(buttons), 2)
        for b in buttons:
            tip = re.search(r"data-tip=\{(cellTip\([^)]*\))\}", b).group(1)
            self.assertIn(f"aria-label={{{tip}}}", b)

    def test_a_zero_is_drawn_at_full_strength(self):
        zero = re.search(r'<span className="([^"]*)" data-tip=\{cellTip\(l, t, 0, c\.days\)\}', self.t).group(1)
        self.assertNotIn("opacity-", zero)
        self.assertIn("text-muted", zero)

    def test_the_muted_text_passes_on_the_page_and_the_old_one_did_not(self):
        muted, paper, panel = token("color-muted"), token("color-paper"), token("color-panel")
        self.assertGreaterEqual(contrast(muted, paper), 4.5)
        self.assertGreaterEqual(contrast(muted, panel), 4.5)
        self.assertLess(contrast(blend(muted, panel, 0.4), panel), 3.0)   # what the zeros were


if __name__ == "__main__":
    unittest.main()

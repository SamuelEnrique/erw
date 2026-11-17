"""Session 7602 (chain 305, the portable laptop): rows 52 and 62 of docs/state/browser_reads_wanted.md, read in a
browser on a build of the old laptop's branches. A decision's source of over 1,000 characters (`/explore/demand-growth`,
"Demand at the grid is not sales to customers") and the impact page's property tax headline opened in a box 288 px wide
that was taller than the room above or below its mark, so the placer (site/components/largeload/TipPlace.tsx) capped it
and it scrolled inside itself: at 1280 px a box of 432 px held part of the words. Such a box is now made wider where
the window allows (up to 576 px, 16 px inside the window) before it is placed; on a phone there is no width to give and
it scrolls as before. The browser read of this session saw both boxes whole at 1280 px (docs/reviews/browser-reads-2026-11-16).
Energy Research Warehouse (ERW)."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASHES = (chr(0x2014), chr(0x2013))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ATallBoxIsWidened(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "components", "largeload", "TipPlace.tsx")

    def test_the_width_is_reset_before_each_measure(self):
        reset = self.s.index('b.style.width = ""; b.style.maxWidth = "";')
        measure = self.s.index("let size = b.getBoundingClientRect();")
        self.assertLess(reset, measure)

    def test_it_widens_only_when_the_box_does_not_fit_and_the_window_has_room(self):
        self.assertIn("const room = Math.max(window.innerHeight - 8 - (tb.bottom + 2), tb.top - 2 - 8);", self.s)
        self.assertIn("const wide = Math.min(576, vw - 16);", self.s)
        self.assertIn("if (size.height > room && wide > size.width + 24) {", self.s)
        self.assertIn("size = b.getBoundingClientRect();", self.s)

    def test_the_placer_is_given_the_new_size(self):
        self.assertIn("{ width: size.width, height: size.height }", self.s)
        self.assertIn('b.style.overflowY = "auto";', self.s)      # a box still too tall (a phone) scrolls as before

    def test_no_dash(self):
        for ch in DASHES:
            self.assertNotIn(ch, self.s)


if __name__ == "__main__":
    unittest.main()

"""Session 8611 (chain 504, 19 November 2026): the natural resource map set against the brand (docs/brand.md).

Energy Research Warehouse (ERW). Measured in a browser on a build at 390 and 1280 px (runs/c504_resources_brand.mjs).
Two things did not follow the brand and are held here:
- section 3, a target a finger presses is 44 px tall on a phone: the map's nine controls (zoom in and out, the four
  moves, the three places) were 24 px tall at every width. Below the small breakpoint each is 44 px in both
  directions; above it they are as they were;
- sections 3 and 6, no shadow, and a hover card is fog with a rule-colored edge: the map's hover card was white with
  a shadow.
Left as it is, and said in the session's report: the small "i" of a decision is the site's shared button, 16 px, on
every page that has a decisions fold. Nothing here makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheMapsControls(unittest.TestCase):
    def setUp(self):
        self.m = src("site", "app", "resources", "ResourceMap.tsx")

    def test_forty_four_pixels_on_a_phone_and_as_they_were_above_it(self):
        self.assertIn('const btn = "inline-flex min-h-11 min-w-11 items-center justify-center border border-rule bg-white px-2 py-0.5 text-sm leading-tight hover:text-accent sm:min-h-6 sm:min-w-0";', self.m)
        self.assertIn("44 px tall on a phone", src("docs", "brand.md"))

    def test_all_nine_take_it(self):
        self.assertEqual(len(re.findall(r'<button type="button" className=\{btn\}', self.m)), 6)      # zoom in and out, four moves
        self.assertIn('{R.PLACES.map((pl) => <button key={pl.id} type="button" className={btn}', self.m)   # the contiguous states, Alaska, Hawaii


class TheHoverCard(unittest.TestCase):
    def test_fog_with_a_rule_colored_edge_and_no_shadow(self):
        m = src("site", "app", "resources", "ResourceMap.tsx")
        self.assertIn('<div className="pointer-events-none absolute z-10 max-w-xs border border-rule bg-paper px-3 py-2 text-sm" data-hover="1"', m)
        self.assertNotIn("shadow", m.split('data-hover="1"')[0].rsplit("<div", 1)[1])
        b = src("docs", "brand.md")
        self.assertIn("No shadow, no gradient, no texture.", b)
        self.assertIn("**The hover card** is fog with a rule-colored edge", b)

    def test_no_em_dash(self):
        for p in (("site", "app", "resources", "ResourceMap.tsx"), ("tests", "test_session8611_resources.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()

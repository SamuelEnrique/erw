"""Session 8609 (chain 504, 19 November 2026): the accessibility read of the three new views, and its two faults.

Energy Research Warehouse (ERW). The map of the Grid tool, the region tabs and the resource map were read with the
axe-core engine on built sites, in the internal view, at 1280 and 390 px (site/scripts/a11y-axe.mjs; WCAG 2.0, 2.1
and 2.2, levels A and AA). The region tabs and the resource map broke no rule. The map broke two, both fixed here:
- nested interactive controls: the map's frame was an image (role img) whose regions are buttons; an image's
  children are hidden from assistive technology. The frame is a labelled group;
- target size: the ten names under the map ("Not on the map") were buttons 16 px tall; they are 24 px tall.
The browser's proof is site/scripts/check-grid-map.mjs (the names' height; a region reached and opened with the
keyboard alone). Nothing here sets the environment or makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheMapIsAGroupOfButtons(unittest.TestCase):
    def setUp(self):
        self.m = src("site", "app", "network", "NetworkMap.tsx")

    def test_the_frame_is_a_labelled_group_not_an_image(self):
        start = self.m.index("<svg ref={svg}")
        end = self.m.index('aria-label="A map of the US balancing authorities', start)
        tag = self.m[start:end]                                             # the tag's attributes, up to its label (it holds arrows, so no pattern on ">")
        self.assertLess(len(tag), 900)
        self.assertIn('role="group"', tag)
        self.assertNotIn('role="img"', tag)

    def test_each_region_is_a_button_the_keyboard_reaches_and_opens(self):
        self.assertIn('className="erw-region cursor-pointer" tabIndex={0} role="button" aria-label={names.get(r.id)}', self.m)
        self.assertIn('onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onPick(r.id); } }}', self.m)
        self.assertIn('onFocus={() => setHover({ kind: "region", id: r.id, x: -1, y: -1, right: false, low: false })}', self.m)
        self.assertIn(".erw-region:focus-visible", self.m)                  # the focus is drawn

    def test_what_draws_nothing_to_a_reader_stays_out_of_the_way(self):
        # the states' lines and the ties answer no pointer and take no focus
        self.assertIn('<g pointerEvents="none" fill="none" stroke="var(--color-ink)" strokeOpacity={0.3}', self.m)
        self.assertEqual(self.m.count("tabIndex={0}"), 1)


class TheNamesUnderTheMap(unittest.TestCase):
    def test_each_is_twenty_four_pixels_tall(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn("<button type=\"button\" className={`inline-flex min-h-11 items-center text-left underline decoration-dotted underline-offset-2 sm:min-h-6 ", m)
        # min-h-6 is 1.5rem, 24 px at the site's 16 px root; min-h-11 is 44 px, the brand's height of a target on a phone (session 8611)
        self.assertNotIn("<button type=\"button\" className={`text-left underline decoration-dotted", m)

    def test_each_still_shows_its_figures_on_focus_and_opens_its_panel(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn('onFocus={() => setHover({ kind: "listed", id: n.id, x: -1, y: -1, right: false, low: false })}', m)
        self.assertIn("data-listed={n.id} onClick={() => onPick(n.id)}", m)


class TheCheck(unittest.TestCase):
    def test_the_browser_reads_the_height_the_role_and_the_keyboard(self):
        s = src("site", "scripts", "check-grid-map.mjs")
        self.assertIn('kbd.role === "group" && kbd.listed.length > 0 && kbd.listed.every((h) => h >= 44)', s)   # read at 390 px, where the brand asks 44 (session 8611)
        self.assertIn('await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter"', s)
        self.assertIn("opened === kbd.region[3]", s)

    def test_no_em_dash(self):
        for p in (("site", "app", "network", "NetworkMap.tsx"), ("site", "scripts", "check-grid-map.mjs"), ("tests", "test_session8609.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()

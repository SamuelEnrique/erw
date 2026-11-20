"""Session 8616 (chain 504, 19 November 2026): what was said and not yet tried, tried; the pack brought up to the day.

Energy Research Warehouse (ERW). The map of balancing authorities was said, since session 8601, to open a region's
panel on a finger's tap. Its browser check tried a tie, two fingers and one finger's move, and never the tap on a
region. It does now (site/scripts/check-grid-map.mjs), as the last thing done, on a page of its own. And the signature
pack for the map and the regions lists what the later sessions of the day changed and the rulings they left. Nothing
here sets the environment or makes a request.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheTapOnARegion(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "scripts", "check-grid-map.mjs")

    def test_the_check_taps_a_region_with_a_finger(self):
        a = self.s.index("// session 8616: a finger's tap on a region opens its panel")
        b = self.s.index("  return bad ? 1 : 0;", a)
        block = self.s[a:b]
        self.assertIn('await touch("touchStart", [{ x: spot.x, y: spot.y }]);', block)
        self.assertIn("document.elementFromPoint(x, y) === r && far(x, y)", block)      # the region itself is topmost, and no tie is near
        self.assertIn("new RegExp(`[?&]node=${spot.id}(&|$)`).test(address)", block)
        self.assertIn("on a phone a finger's tap on a region opens its panel", block)

    def test_it_is_the_last_thing_done(self):
        # the open panel would upset the checks that follow, so none follows
        a = self.s.index("// session 8616: a finger's tap on a region opens its panel")
        after = self.s[self.s.index("  return bad ? 1 : 0;", a):]
        self.assertNotIn("check(", after)
        self.assertEqual(self.s.count("  return bad ? 1 : 0;"), 1)

    def test_the_map_still_opens_a_panel_on_a_tap(self):
        m = src("site", "app", "network", "NetworkMap.tsx")
        self.assertIn('const id = (e.target as Element).getAttribute?.("data-region");', m)
        self.assertIn("if (id) onPick(id);", m)


class ThePack(unittest.TestCase):
    def setUp(self):
        self.p = src("docs", "reviews", "grid-map-regions-signature-pack-2026-11-19.md")

    def test_the_rulings_number_on_and_each_has_its_default(self):
        a = self.p.index("## 3. For your ruling")
        rows = re.findall(r"^\| (\d+) \| (.+?) \| (.+?) \|$", self.p[a:self.p.index("## 3a.")], flags=re.M)
        self.assertEqual([int(r[0]) for r in rows], list(range(1, len(rows) + 1)))
        self.assertGreaterEqual(len(rows), 13)
        self.assertTrue(all(r[2].strip() for r in rows))

    def test_it_says_what_changed_since_it_was_written(self):
        self.assertIn("## 3a. Since this pack was first written", self.p)
        for words in ("on a phone with a finger", "every year the file holds", "A keyboard and a screen reader reach each region"):
            self.assertIn(words, self.p)

    def test_no_line_still_waits_for_files_that_have_landed(self):
        self.assertNotIn("The data machine is rebuilding the region files", self.p)

    def test_no_em_dash(self):
        for p in (("docs", "reviews", "grid-map-regions-signature-pack-2026-11-19.md"), ("docs", "reviews", "grid-map-read-2026-11-19.md"), ("site", "scripts", "check-grid-map.mjs"), ("tests", "test_session8616.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()

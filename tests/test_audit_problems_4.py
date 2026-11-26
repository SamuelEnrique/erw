"""Session 10229 (the problems audit, findings 4 and 5). The resource map's legend prints one decimal when its range is 5
or more (site/lib/resources.ts tickLabel), and a problem set's answer is computed from the list's unrounded values: the
sun's ratio from the legend's ends is 4.31, the key 4.36; the wind's gap 0.60, the key 0.62. A set's page now says the
answers are computed from the unrounded figures, and a set of the whole country says its figures come from committed page
files, which move when a file is rebuilt, not when the page is built. Facts from site/data/resources/manifest.json; words
from the set's module, the set's page and the method note.
"""
import json
import os
import unittest
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
SET = os.path.join(ROOT, "site", "lib", "problemsets", "under-the-ground-and-in-the-wind.ts")
PAGE = os.path.join(ROOT, "site", "app", "learn", "problems", "[slug]", "page.tsx")
NOTE = os.path.join(ROOT, "docs", "methods", "problem_sets.md")
r2 = lambda v: float(Decimal(v).quantize(Decimal("0.01"), ROUND_HALF_UP))
r1 = lambda v: float(Decimal(v).quantize(Decimal("0.1"), ROUND_HALF_UP))


def ends(layer):
    lows = [layer["legend"]["min"]] + [x["legend"]["min"] for x in layer.get("other_extents") or [] if x.get("legend")]
    highs = [layer["legend"]["max"]] + [x["legend"]["max"] for x in layer.get("other_extents") or [] if x.get("legend")]
    return min(lows), max(highs)


class TheLegendIsNotTheKey(unittest.TestCase):
    def setUp(self):
        self.L = {l["id"]: l for l in json.load(open(MANIFEST, encoding="utf-8"))["layers"]}

    def test_the_sun(self):
        lo, hi = ends(self.L["solar_ghi"])
        self.assertGreaterEqual(hi - lo, 5)                       # so the legend prints one decimal
        self.assertEqual(r2(hi / lo), 4.36)                       # the key
        self.assertEqual(r2(r1(hi) / r1(lo)), 4.31)               # from the legend
        self.assertEqual(r2(r2(hi) / r2(lo)), 4.37)               # from the answer's own printed figures

    def test_the_wind(self):
        lo, hi = ends(self.L["wind_speed_100m"])
        top = self.L["wind_speed_100m"]["source_stats"]["max"]
        self.assertGreaterEqual(hi - lo, 5)
        self.assertEqual(r2(top - hi), 0.62)
        self.assertEqual(r2(top - r1(hi)), 0.60)


class TheWords(unittest.TestCase):
    def test_the_set_says_it(self):
        src = open(SET, encoding="utf-8").read()
        self.assertIn("The answer divides the list's own values, which hold more decimals than the legend prints", src)
        self.assertIn("The legend prints it to one decimal; the answer subtracts the list's own value", src)

    def test_the_page_says_it(self):
        src = open(PAGE, encoding="utf-8").read()
        self.assertIn("Each answer is computed from the unrounded figures and printed as a whole number or to two decimals", src)
        self.assertIn("Every answer is computed from committed page files built from the warehouse&apos;s tables, so the numbers move when the data machine rebuilds a file.", src)
        self.assertIn("GUIDE[slug]?.files?.length", src)

    def test_the_note_says_it(self):
        note = open(NOTE, encoding="utf-8").read()
        self.assertIn("**Rounding (session 10229", note)
        self.assertIn("the sets of the whole country are in the dated editions too", note)
        for f in (SET, PAGE, NOTE):
            self.assertNotIn(chr(0x2014), open(f, encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()

"""Audit of the project map, finding 2 (session 10216, docs/reviews/map-model-audit-2026-11-26.md): where a point is.
The decisions and the hover of "Near a point" placed a datacenter at "the city's point": in the page's copy of 19
November 2026, 80 of the 278 are at the operator's own coordinates, 120 at a city's or town's point, 28 at a county's
point and 50 at none (they hold 25,158 of the 28,254 MW stated). The key put every queue position "at its county's
point": 184 are at a city's or town's. A unit's point was called "exact coordinates": it is EIA's point for the plant
(31,073 units at 16,022 points). No figure moves.

1. Through the page's file: datacenters stand at several kinds of point, queue positions at counties and places, and
   many units share their plant's point. Passes on main.
2. The fix on this branch, words only. Fails on main."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class WhereAPointIs(unittest.TestCase):
    def test_the_kinds_of_point_in_the_file(self):
        f = json.loads(src("site", "data", "map.json"))
        kinds = lambda k: {f["pr"][i] for i in range(len(f["k"])) if f["k"][i] == k}
        self.assertTrue({1, 2, 3} <= kinds(3), "datacenters at a county's point, a city's or town's point and the operator's coordinates")
        self.assertTrue({1, 2} <= kinds(2), "queue positions at a county's point and a city's or town's point")
        self.assertEqual(kinds(0) | kinds(1), {0}, "every unit at EIA's point")
        units = [i for i in range(len(f["k"])) if f["k"][i] in (0, 1) and f["la"][i] is not None]
        self.assertLess(len({(f["la"][i], f["lo"][i]) for i in units}), len(units) * 0.75, "many units share their plant's point")

    def test_the_words(self):
        dec = src("site", "app", "map", "Decisions.tsx")
        self.assertNotIn("the city's point for a datacenter", dec)
        self.assertIn("and for a datacenter the operator's own coordinates, its city's or town's point or its county's point", dec)
        page = src("site", "app", "map", "ProjectMap.tsx")
        self.assertNotIn("the city&apos;s point for a datacenter", page)
        self.assertIn("and for a datacenter the operator&apos;s own coordinates, its city&apos;s or town&apos;s point or its county&apos;s point", page)
        self.assertIn("queue position, at its county&apos;s, city&apos;s or town&apos;s point</li>", page)
        self.assertIn("measured from their county&apos;s, city&apos;s or town&apos;s point, not their site", page)
        lib = src("site", "lib", "projectmap.ts")
        self.assertNotIn('"exact coordinates"', lib)
        self.assertIn('export const PLACED_AT = ["EIA\'s plant coordinates", "county point", "city or town point", "operator\'s coordinates", "not placed"];', lib)
        self.assertIn("\"EIA's coordinates of the plant\" + at", lib)
        note = src("docs", "methods", "map.md")
        self.assertNotIn("the city's point for a datacenter", note)
        self.assertIn("the map audit, finding 2", note)
        for text in (dec, page, lib, note):
            self.assertNotIn(chr(0x2014), text)


if __name__ == "__main__":
    unittest.main()

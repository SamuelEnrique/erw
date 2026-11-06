"""Sessions 1586 to 1588 (chain 187): three faults AccessLint found on a build of main (6 November 2026, the internal
view), fixed in place. /data: 67 scrolling <pre> blocks (each table row's Python, Stata and R calls, and the install
lines) not reachable by keyboard. /consumption: the states table's scrolling div, the same. /prices/compare: the
table head's sort links drawn in the surface colour, white on a white page (a contrast of 1:1; the five headings
could not be seen). Source reading only: no network, no build. Nothing here sets the environment at import.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, "site", *parts), encoding="utf-8") as f:
        return f.read()


class TheData(unittest.TestCase):
    def test_every_scrolling_pre_is_a_region(self):
        s = src("app", "data", "page.tsx")
        self.assertIn('import { scrollRegion } from "@/lib/cells";', s)
        pres = re.findall(r"<pre [^>]*overflow-x-auto[^>]*>", s)
        self.assertEqual(len(pres), 3)
        for p in pres:
            self.assertIn("{...scrollRegion(", p)

    def test_the_row_region_names_its_table(self):
        self.assertIn("scrollRegion(`The calls for ${r.table_name} in Python, Stata and R`)", src("app", "data", "page.tsx"))


class TheConsumption(unittest.TestCase):
    def test_the_states_table_is_a_region(self):
        s = src("app", "consumption", "view.tsx")
        self.assertIn('<div className="overflow-x-auto" {...scrollRegion("Sector shares and growth, by state")}>', s)
        self.assertEqual(re.findall(r'<div className="overflow-x-auto">', s), [])
        self.assertEqual(s.count('<div className="overflow-x-auto" {...scrollRegion('), 3)   # session 1587: all three frames


class TheCompare(unittest.TestCase):
    def test_the_sort_links_are_not_white(self):
        s = src("app", "prices", "compare", "page.tsx")
        self.assertNotIn('style={{ color: "var(--color-surface)" }} data-sort', s)
        self.assertIn('className="underline" data-sort={m.slug}>', s)


if __name__ == "__main__":
    unittest.main()

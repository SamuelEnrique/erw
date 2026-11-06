"""Session 1526 (chain 163): the scenario block's two scrolling tables reachable by keyboard. AccessLint (session 1504)
found a scrolling region not reachable by keyboard on /cost-of-power (`figure > details > div`, the sensitivity chart
as a table); the scenarios table above it scrolls too. Both now carry lib/cells.ts's scrollRegion (tabIndex 0, a
region with a name), as session 412 gave the tool pages' tables. The block is shared by the battery, the generator and
the datacenter. Source reading only: no network, no build. Nothing here sets the environment at import.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK = os.path.join(ROOT, "site", "components", "decisions", "ScenarioBlock.tsx")


def src():
    with open(BLOCK, encoding="utf-8") as f:
        return f.read()


class TheScrollingTables(unittest.TestCase):
    def test_the_helper_is_imported(self):
        self.assertIn('import { scrollRegion } from "@/lib/cells";', src())

    def test_both_regions_are_named(self):
        s = src()
        self.assertIn('<div className="overflow-x-auto" {...scrollRegion("The sensitivity chart, as a table")}>', s)
        self.assertIn('<div className="overflow-x-auto" {...scrollRegion("Scenarios A and B")}>', s)

    def test_no_scrolling_div_without_it(self):
        bare = re.findall(r'<div className="overflow-x-auto">', src())
        self.assertEqual(bare, [])


if __name__ == "__main__":
    unittest.main()

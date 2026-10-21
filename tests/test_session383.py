"""Session 383: the internal shape-premium draft compares only the hubs whose grids are not held.

From 21 October 2026 the license holds (site/lib/license.ts) keep ISO-NE's, MISO's and NYISO's rows out of the reads, and
the draft looked for a month that all six hubs hold: there was none, and the page answered 500 (check-values stopped on it
on the landing build of wip/381-382-land). The page now takes the hubs that are not held, and names the held ones in one
line as "license needed".
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "shape-premium", "page.tsx")


def src():
    with open(PAGE, encoding="utf-8") as f:
        return f.read()


class TheDraftFollowsTheHolds(unittest.TestCase):
    def test_the_hubs_are_split_by_the_hold(self):
        s = src()
        self.assertIn('import { LICENSE_NEEDED, licenseHeldRow } from "@/lib/license";', s)
        self.assertIn("const OPEN = HUBS.filter((h) => !licenseHeldRow(M, h.e)), HELD = HUBS.filter((h) => licenseHeldRow(M, h.e));", s)

    def test_no_computation_asks_every_hub_of_the_six(self):
        s = src()
        # HUBS is named three times: its definition and twice in the split; every month, table and chart reads OPEN
        self.assertEqual(s.count("HUBS"), 3, "the definition, and HUBS.filter twice in the split line")
        for line in ("OPEN.every((h) => all.some(", "const six = OPEN.map(", "OPEN.every((h) => monthsOf(", "const year = lastAll ? OPEN.map(", "const shapes = OPEN.map("):
            self.assertIn(line, s)

    def test_the_held_hubs_are_named(self):
        s = src()
        self.assertIn("data-held-hubs", s)
        self.assertIn("{LICENSE_NEEDED} (held from 21 October 2026, lib/license.ts)", s)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), src())
        with open(__file__, encoding="utf-8") as f:
            self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()

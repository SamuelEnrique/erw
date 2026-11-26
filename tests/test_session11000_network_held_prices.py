"""Session 11000 (chain 750, the browser read of 26 November 2026): the Network view printed a held price.

NYISO's and ISO-NE's prices are held for a license since 21 October 2026 (warehouse/metadata/license_verdicts.csv:
"needs written permission" for both), and every page draws them as "license needed". The Grid tool's Network view
did so only in its live week, which reads the live set. Its replay of a past day reads site/public/network/
daily_<year>.json, whose hub_prices still carry both grids, and with the Prices switch on the page drew a ring on
each and printed "Hub price this day: <the price> USD/MWh" and the period's range in the panel of New York and of New
England (seen on production at 18:02 UTC on 26 November for a day of 2025 and for 20 November 2026). MISO, paused,
was already blank there (PAUSED_PRICE, session 124); the two held grids had never been given the same treatment.

The view now treats a held price as no price in every view: no ring, no figure, no part in the heaviest ring or the
period's range, and the panel prints the site's words for a held figure with the reason on hover. That the files
still carry the prices is data request 576 (the data machine's).

Energy Research Warehouse (ERW). No network, no build: the sources are read.

    python -m unittest tests.test_session11000_network_held_prices -v
"""

import csv
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheHeldGridsAreNamed(unittest.TestCase):
    def setUp(self):
        self.lib = read("site", "lib", "networkV3.ts")

    def test_the_two_grids_held_for_a_license_are_listed_with_their_reason(self):
        block = re.search(r"export const HELD_PRICE: Record<string, string> = \{(.*?)\n\};", self.lib, re.S)
        self.assertIsNotNone(block, "lib/networkV3.ts names no held price")
        keys = re.findall(r"^\s*([A-Z]+): \"", block.group(1), re.M)
        self.assertEqual(sorted(keys), ["ISNE", "NYIS"])
        for line in re.findall(r"^\s*[A-Z]+: \"(.*)\",?$", block.group(1), re.M):
            self.assertIn("written permission", line)
            self.assertIn("21 October 2026", line)
        self.assertIn('export const HELD_WORDS = "license needed";', self.lib)

    def test_the_hold_is_the_one_the_warehouse_records(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.reader(f)]
        by_name = {r[0]: r for r in rows if r}
        for name in ("NYISO", "ISO-NE"):
            self.assertIn(name, by_name, name + " is no longer in the license verdicts: read this test and HELD_PRICE again")
            self.assertIn("needs written permission", by_name[name], name + "'s verdict is no longer 'needs written permission': if the hold is lifted, HELD_PRICE follows")


class TheViewDrawsNoHeldPrice(unittest.TestCase):
    def setUp(self):
        self.view = read("site", "app", "network", "Network.tsx")

    def test_a_held_price_is_no_price_in_any_view(self):
        # the hold stands where a view answers for its price, so no reader can pass it: the live week, a story, a day
        self.assertIn("const unheld = (id: string, v: number | null | undefined): number | null => (HELD_PRICE[id] ? null : v ?? null);", self.view)
        defs = re.findall(r"\bprice: \(id, h\) => (.+?), priceKind:", self.view)
        self.assertEqual(len(defs), 3, "the view defines a price in three places (the live week, a story, a day): read this test again")
        for d in defs:
            self.assertTrue(d.startswith("unheld(id, "), "a view answers a price without asking whether it is held: " + d)
        # and the files' or the live set's prices are read nowhere else in the component
        self.assertEqual(len(re.findall(r"hub_prices\[id\]", self.view)), 2)
        self.assertEqual(len(re.findall(r"live\.prices\[id\]", self.view)), 1)
        # nothing reads a view's price but priceOf (session 124's own line, as it was)
        self.assertEqual(len(re.findall(r"view\.price\(", self.view)), 1)

    def test_the_panel_prints_the_sites_words_and_the_reason(self):
        self.assertIn(": HELD_PRICE[pick.id] ? <span data-price-held={pick.id} title={HELD_PRICE[pick.id]}", self.view)
        self.assertIn("{HELD_WORDS}</span> : pick.id === \"PJM\" ?", self.view)
        # a paused grid keeps its own words, before a held one (MISO is paused, not held)
        self.assertLess(self.view.index("data-price-paused={pick.id}"), self.view.index("data-price-held={pick.id}"))

    def test_the_rings_and_the_range_come_through_the_same_reader(self):
        # the rings, the heaviest ring and the period's range each read priceOf: a held grid has none of them
        for needle in ("priceWeight(priceOf(view, !!v3, n.id, hour), priceMax)", "priceOf(view, !!v3, n.id, hour) !== null).length", "const v = priceOf(view, !!v3, pick.id, h); if (v !== null) vals.push(v);"):
            self.assertIn(needle, self.view)


class TheCheckAndTheNoteFollow(unittest.TestCase):
    def test_the_browser_check_counts_no_ring_on_a_held_grid(self):
        s = read("site", "scripts", "check-network-v3.mjs")
        self.assertIn('import { easternHours, trace, PAUSED_PRICE, HELD_PRICE } from "../lib/networkV3.ts";', s)
        self.assertEqual(len(re.findall(r"!HELD_PRICE\[b\]", s)), 2, "both counts of priced grids leave the held ones out")
        self.assertIn("data-price-held", s)

    def test_the_method_note_says_it(self):
        note = read("docs", "methods", "grid_network.md")
        self.assertIn("**NYISO and ISO-NE have no ring: their prices are held for a license**", note)
        self.assertIn("data request 576", note)


if __name__ == "__main__":
    unittest.main()

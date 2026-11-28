"""Session 11407 (chain 770, part C): the states audit's finding 6 readied for Samuel's ruling, round once.

Carried over from session 10223's tests/test_audit_states_6.py (branch wip/audit-states-6), which showed that the files
carry rounded figures (the twelve months' price and the shares to 0.01) and the page rounded them again: Texas's homes
15.98 cents a kWh where revenue over sales is 159.8509 USD a MWh (15.99); SPP's share of Texas's people 4.2% where
1,314,559 of 31,709,821 is 4.1456 (4.1). On this branch the page computes the twelve months' price as revenue over
sales, a source's share as its MWh over the total, an authority's share as its people over the state's (site/lib/states.ts
price12, share12, peopleShare), from the same file, and rounds once. No site file changes.
docs/reviews/states-model-audit-2026-11-26.md, finding 6.
"""
import json
import os
import re
import unittest
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def js_fixed(v, nd):
    """JavaScript's toFixed on a double: the exact binary value, a tie away from zero."""
    return str(Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def once(v, nd):
    return str(Decimal(repr(v)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


class ThePageRoundsOnce(unittest.TestCase):
    def setUp(self):
        self.page = src("site", "app", "states", "page.tsx")
        self.lib = src("site", "lib", "states.ts")

    def test_the_lib_computes_from_the_parts(self):
        self.assertIn("b.revenue_usd / b.sales_mwh : b.price_usd_per_mwh", self.lib)
        self.assertIn("(100 * v) / l.total_mwh : l.share_pct[src] ?? null", self.lib)
        self.assertIn("(100 * a.population) / s.population : a.share_pct", self.lib)

    def test_every_twelve_month_price_and_share_goes_through_them(self):
        self.assertEqual(len(re.findall(r"price12\(", self.page)), 4)      # the sector table, the side table (two), the headline
        self.assertEqual(len(re.findall(r"share12\(", self.page)), 4)      # the twelve months' table, the side table (two), the headline
        self.assertEqual(len(re.findall(r"peopleShare\(", self.page)), 1)  # who operates
        self.assertNotIn("v={b.price_usd_per_mwh}", self.page)
        self.assertNotIn("v={g.last12.share_pct[s]}", self.page)
        self.assertNotIn("v={a.share_pct}", self.page)

    def test_the_note_says_so(self):
        note = src("docs", "methods", "states_page.md")
        self.assertIn("Rounded once (session 11407", note)
        for t in (self.page, self.lib, note):
            self.assertNotIn(chr(0x2014), t)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "tx.json")), "the states' page files are not on this machine")
class TexasTwoCells(unittest.TestCase):
    def test_texas(self):
        with open(os.path.join(DIR, "tx.json"), encoding="utf-8") as f:
            tx = json.load(f)
        b = tx["retail"]["last12"]["by_sector"]["residential"]
        sv = {a["code"]: a for a in tx["serving"]["by_authority"]}
        if b["price_usd_per_mwh"] != 159.85 or sv["SWPP"]["population"] != 1314559:
            self.skipTest("Texas's file has moved on from the figures of 20 to 28 November 2026")
        # before (the file's rounded figure, rounded again) and after (rounded once, as the lib now computes it)
        self.assertEqual(js_fixed(b["price_usd_per_mwh"] / 10, 2), "15.98")
        self.assertEqual(js_fixed(b["revenue_usd"] / b["sales_mwh"] / 10, 2), "15.99")
        self.assertEqual(once(b["revenue_usd"] / b["sales_mwh"] / 10, 2), "15.99")
        self.assertEqual(js_fixed(sv["SWPP"]["share_pct"], 1), "4.2")
        self.assertEqual(js_fixed(100 * sv["SWPP"]["population"] / tx["serving"]["population"], 1), "4.1")


if __name__ == "__main__":
    unittest.main()

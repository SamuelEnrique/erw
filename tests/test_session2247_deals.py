"""Session 2247 (chain 156): the method notes in the v2 shape name every figure the chain's views add.

site/scripts/check-methods.mjs holds a page's figures to its notes: a figure of the page's own arithmetic is named when
the note holds its family as a key starts it (`deals|`) and its measure as a whole word. The deals page links
docs/methods/energy_deals.md and the datacenter page docs/methods/datacenter_facilities.md.
"""

import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def note(name):
    with open(os.path.join(ROOT, "docs", "methods", name + ".md"), encoding="utf-8") as f:
        return f.read()


def named(text, family, measure):
    t = text.lower()
    return f"{family}|" in t and re.search(r"(?<![a-z0-9_])" + re.escape(measure).replace("_", "[_ ]") + r"(?![a-z0-9_])", t)


class TheNotes(unittest.TestCase):
    def test_every_deals_figure_is_named(self):
        t = note("energy_deals")
        for m in ("price_count", "price_median", "price_low", "price_high", "ai_deals", "ai_mw", "ai_with_mw", "ai_usd",
                  "ai_with_usd", "chart_mw", "chart_price", "chart_ai", "chart_party"):
            self.assertTrue(named(t, "deals", m), m)

    def test_every_datacenter_figure_is_named(self):
        t = note("datacenter_facilities")
        for fam, ms in (("datacenters", ("rollup_facilities", "rollup_mw", "rollup_with_mw", "rollup_without")),
                        ("dctime", ("count", "median")), ("dcchart", ("planned", "operator", "power")),
                        ("dcgrid", ("facilities", "with_mw", "planned", "under_construction", "operating", "peak_mw", "capacity_mw",
                                    "share_of_peak", "reserve_margin"))):
            for m in ms:
                self.assertTrue(named(t, fam, m), f"{fam} {m}")

    def test_the_v2_parts(self):
        t = note("energy_deals")
        for part in ("### Each field", "### One record a deal", "### The views and their keys", "### The tracers",
                     "### What the extraction cannot see"):
            self.assertIn(part, t)
        for name in ("energy_deals", "datacenter_facilities", "datacenter_projects", "deal_counterparties", "datacenter_tracker_rollups"):
            s = note(name)
            self.assertNotIn("—", s)
            self.assertNotIn("–", s)


if __name__ == "__main__":
    unittest.main()

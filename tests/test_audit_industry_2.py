"""Session 10224 (chain 710, the industry page audit, finding 2): electricity on /industry is electricity bought.

The survey's "Net electricity" (Table 3.2) leaves out what a plant makes from its own fuel, and the State Energy Data
System's and Form EIA-861M's electricity is sales to industrial customers. docs/reviews/industry-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class NetElectricity(unittest.TestCase):
    """What the page file holds (passes on main)."""

    def setUp(self):
        self.ind = json.loads(src("site", "data", "industry.json"))["industries"]["industries"]

    def net(self, n):
        e = self.ind[n]["electricity_mwh"]["us"]
        return (e["elec_purchases"] + e["elec_transfers_in"] + (e.get("gen_renewable") or 0) - e["elec_sales_transfers_offsite"]) * 3412 / 1e9

    def test_it_is_bought_electricity_net_of_sales(self):
        for n in ("325", "324", "322", "311", "total"):   # each with every part held (Primary Metals' transfers in are withheld)
            self.assertAlmostEqual(self.net(n), self.ind[n]["by_region"]["us"]["net_electricity"], delta=1.0)

    def test_it_is_not_the_electricity_used(self):
        paper = self.ind["322"]
        used = paper["electricity_mwh"]["us"]["elec_net_demand"] * 3412 / 1e9
        self.assertLess(paper["by_region"]["us"]["net_electricity"] / used, 0.55)
        south = self.ind["total"]["electricity_mwh"]["south"]
        self.assertGreater(south["elec_onsite_generation"] / south["elec_net_demand"], 0.2)


class TheWords(unittest.TestCase):
    """What the page and its note say (fails on main, passes on the branch)."""

    def test_the_hovers_say_it(self):
        page = src("site", "app", "industry", "page.tsx")
        self.assertIn("Electricity a plant makes from its own fuel is not in it", page)
        self.assertIn("An industry's electricity use is its net demand", page)
        self.assertIn("Electricity is the electricity sold to industrial customers", page)
        self.assertIn("Sales only: electricity a plant makes for itself is not in it.", page)

    def test_the_note_says_it(self):
        self.assertIn("is not an industry's electricity use", src("docs", "methods", "industry_page.md"))

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "page.tsx"), ("docs", "methods", "industry_page.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()

"""Session 10224 (chain 710, the industry page audit, finding 3): the states' "Average price" on /industry.

The State Energy Data System's industrial "total average price" is all fuels together and is per a smaller quantity than
the total printed beside it: expenditures are not the total times the price, and it is not a tariff or the price of
electricity. docs/reviews/industry-model-audit-2026-11-26.md.
"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class ThePrice(unittest.TestCase):
    """What the page file holds (passes on main)."""

    def setUp(self):
        s = json.loads(src("site", "data", "industry.json"))["states_annual"]
        self.i = [int(y) for y in s["years"]].index(2024)
        self.st = s["states"]

    def quantity(self, st):
        """The TBtu the price is per: expenditures over price."""
        d = self.st[st]
        return d["expenditures_usd"]["total"][self.i] / d["price_usd_per_mmbtu"][self.i] / 1e6

    def test_it_is_per_less_than_the_total_and_in_most_states_less_than_end_use(self):
        n = under_end_use = 0
        for st, d in self.st.items():
            p, x = d["price_usd_per_mmbtu"][self.i], d["expenditures_usd"]["total"][self.i]
            if not p or x is None:
                continue
            n += 1
            q = self.quantity(st)
            self.assertLess(q, d["consumption_tbtu"]["total"][self.i], st)
            self.assertLess(q, 1.005 * d["consumption_tbtu"]["end_use_total"][self.i], st)
            under_end_use += q < 0.99 * d["consumption_tbtu"]["end_use_total"][self.i]
        self.assertEqual(n, 52)
        self.assertEqual(under_end_use, 48)   # DC, Maryland, Rhode Island and Vermont at 99 to 100 percent of end use

    def test_texas(self):
        d = self.st["TX"]
        self.assertAlmostEqual(self.quantity("TX"), 5650.4, delta=0.5)
        self.assertAlmostEqual(d["expenditures_usd"]["total"][self.i] / d["consumption_tbtu"]["total"][self.i] / 1e6, 6.34, delta=0.01)
        self.assertEqual(d["price_usd_per_mmbtu"][self.i], 9.11)
        # electricity alone, expenditures over sales at 3,412 Btu a kWh: about 57 dollars a MWh
        mwh = d["consumption_tbtu"]["electricity"][self.i] * 1e9 / 3412
        self.assertAlmostEqual(d["expenditures_usd"]["electricity"][self.i] / mwh, 57.14, delta=0.01)


class TheWords(unittest.TestCase):
    """What the page and its note say (fails on main, passes on the branch)."""

    def test_the_hover_says_it(self):
        page = src("site", "app", "industry", "page.tsx")
        self.assertIn("all fuels together", page)
        self.assertIn("not a tariff", page)
        self.assertIn("so the expenditures are not the total times this price", page)
        self.assertEqual(page.count("src={PRICE_WHY}"), 3)   # the states' table and the two states' row, A and B

    def test_the_note_says_it(self):
        self.assertIn("expenditures are not the total times the price", src("docs", "methods", "industry_page.md"))

    def test_no_em_dash(self):
        for p in (("site", "app", "industry", "page.tsx"), ("docs", "methods", "industry_page.md")):
            self.assertNotIn(chr(0x2014), src(*p))


if __name__ == "__main__":
    unittest.main()

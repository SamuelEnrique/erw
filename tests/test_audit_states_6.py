"""Session 10223 (the states audit, finding 6, a figure for the owner's ruling; not for landing).

The files carry rounded figures (shares and prices to 0.01, MW to 0.1) and the page rounds them again. Where the file's
last digit is a 5 the printed digit can be one off the figure rounded once: Texas's homes pay 15.98 cents a kWh on the
page (the file's 159.85 USD a MWh, rounded again) where revenue over sales is 159.8509 (15.99); SPP's share of Texas's
people prints 4.2% where 1,314,559 of 31,709,821 is 4.1456 (4.1). On the files of 20 November 2026: 13 of 236
twelve-month prices, 13 of 423 twelve-month shares and 8 of 109 shares of the people. This test passes on main.
"""
import json
import os
import unittest
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def js_fixed(v, nd):
    """JavaScript's toFixed on a double: the exact binary value, a tie to the larger."""
    return str(Decimal(v).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def once(v, nd):
    return str(Decimal(repr(v)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def files():
    with open(os.path.join(DIR, "index.json"), encoding="utf-8") as f:
        idx = json.load(f)
    for r in idx["states"]:
        with open(os.path.join(DIR, r["file"]), encoding="utf-8") as f:
            yield r["state"], json.load(f)


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class AFigureForTheRuling(unittest.TestCase):
    def test_texas_two_cells(self):
        tx = dict(files())["TX"]
        b = tx["retail"]["last12"]["by_sector"]["residential"]
        self.assertEqual(js_fixed(b["price_usd_per_mwh"] / 10, 2), "15.98")
        self.assertEqual(once(b["revenue_usd"] / b["sales_mwh"] / 10, 2), "15.99")
        sv = {a["code"]: a for a in tx["serving"]["by_authority"]}
        tot = sum(a["population"] for a in tx["serving"]["by_authority"])
        self.assertEqual(js_fixed(sv["SWPP"]["share_pct"], 1), "4.2")
        self.assertEqual(once(100 * sv["SWPP"]["population"] / tot, 1), "4.1")

    def test_counts(self):
        n = {"price": [0, 0], "share": [0, 0], "people": [0, 0]}
        for _, f in files():
            for b in f["retail"]["last12"]["by_sector"].values():
                if b["price_usd_per_mwh"] is not None:
                    n["price"][0] += 1
                    n["price"][1] += js_fixed(b["price_usd_per_mwh"] / 10, 2) != once(b["revenue_usd"] / b["sales_mwh"] / 10, 2)
            g = f["generation"]["last12"]
            for s, v in g["share_pct"].items():
                if v is not None:
                    n["share"][0] += 1
                    n["share"][1] += js_fixed(v, 1) != once(100 * g["mwh"][s] / g["total_mwh"], 1)
            s = f["serving"]
            if s.get("by_authority") and not s.get("shares_reason"):
                tot = sum(a["population"] for a in s["by_authority"])
                for a in s["by_authority"]:
                    n["people"][0] += 1
                    n["people"][1] += js_fixed(a["share_pct"], 1) != once(100 * a["population"] / tot, 1)
        self.assertEqual(n, {"price": [236, 13], "share": [423, 13], "people": [109, 8]})


if __name__ == "__main__":
    unittest.main()

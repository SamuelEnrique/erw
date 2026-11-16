"""Session 7016 (chain 301, done-line request 4): a party's place by contracts in ferc_eqr_party_mw is its x_rank in
ferc_eqr_party_totals (by contracts, then rows, then name over every row of the product), the place the contracts page
names. It was ranked by contracts then name over the in-force rows only: 708 of the 812 rows held another place on 16
November 2026. Every name here is made up. No request, no model call."""
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_session125 as t125  # noqa: E402

et = t125.et


class ThePlace(unittest.TestCase):
    def scope(self):
        d = t125.made([dict(n=1, contract=1, quantity="100", units="MW"),
                       dict(n=2, contract=5, company=2, seller="Sample Wind LLC", buyer="Sample City Light", quantity="30", units="MW")])
        t = t125.terms_of(d)
        return t.assign(seller=d["x_seller_company_name"].values, company_id=d["x_company_id"].values)

    def test_the_place_is_the_totals_rank(self):
        scope = self.scope()
        buyer = next(r for r in et.party_mw(scope) if r["role"] == "buyer" and r["name"] == "Sample City Light")
        seller_id = buyer and next(r for r in et.party_mw(scope) if r["role"] == "seller" and r["name"] == "Sample Wind LLC")["company_id"]
        totals = pd.DataFrame([dict(name="Sample City Light", x_role="buyer", x_product="energy", x_rank="7", x_company_id=""),
                               dict(name="Sample Wind LLC", x_role="seller", x_product="energy", x_rank="12", x_company_id=seller_id)])
        rows = et.party_mw(scope, totals)
        got = {(r["role"], r["name"]): r["rank_contracts"] for r in rows}
        self.assertEqual(got[("buyer", "Sample City Light")], 7)
        self.assertEqual(got[("seller", "Sample Wind LLC")], 12)
        self.assertEqual(got[("buyer", "Example Power Co")], "")       # not in the totals: no place, never a made-up one

    def test_without_the_totals_every_place_is_blank(self):
        self.assertEqual({r["rank_contracts"] for r in et.party_mw(self.scope())}, {""})


if __name__ == "__main__":
    unittest.main()

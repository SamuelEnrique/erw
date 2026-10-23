"""Session 825: the FERC EQR rows beside the deals (chain 080).

The name key and the match rule of warehouse/deals/eqr_join.py on fixtures; the join on fixtures of deals and contract
rows (two parties, one party, the quarter); the site's file carries counts and no filed term; the page's code.
No request is made.
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
import eqr_join as J  # noqa: E402


def contract(i, seller, buyer, date, product="ENERGY", rate="42.1", quarter=None):
    return {"id": f"eqr:{i}", "date": date, "seller": seller, "buyer": buyer, "product": product, "class": "F", "term": "LT", "commencement": "", "termination": "",
            "quantity": "100", "units": "MW", "rate": rate, "rate_units": "$/MWH", "rate_description": "", "pod_ba": "PJM", "pod": "HUB", "quarter": quarter or J.quarter_of(date), "mw": ""}


class KeyTest(unittest.TestCase):
    def test_key(self):
        self.assertEqual(J.key("Constellation Energy Generation, LLC"), "CONSTELLATION ENERGY GENERATION")
        self.assertEqual(J.key("Amazon"), "AMAZON")
        self.assertEqual(J.key("The Energy Company, Inc."), "ENERGY")   # the corporate words dropped; a one-word key still needs four letters and a whole word
        self.assertEqual(J.key("AEP Texas Inc."), "AEP TEXAS")

    def test_matches(self):
        self.assertTrue(J.matches("CONSTELLATION", "CONSTELLATION ENERGY GENERATION"))
        self.assertFalse(J.matches("CONSTELLATION GENERATION", "CONSTELLATION"))   # one direction: the story's name is the shorter
        self.assertFalse(J.matches("MONOMOY CAPITAL", "CAPITAL ENERGY"))
        self.assertTrue(J.matches("VISTRA", "VISTRA ENERGY"))
        self.assertFalse(J.matches("CON", "CONSTELLATION GENERATION"))   # under four characters: whole key only
        self.assertTrue(J.matches("US", "US"))
        self.assertFalse(J.matches("US", "US NAVY"))
        self.assertFalse(J.matches("AMAZON", "AMAZONIA POWER"))   # a whole word, not a prefix
        self.assertFalse(J.matches("", "X"))


class JoinTest(unittest.TestCase):
    def setUp(self):
        self.contracts = [
            contract(1, "Constellation Energy Generation, LLC", "Amazon Data Services, Inc.", "2026-08-15"),
            contract(2, "Constellation Energy Generation, LLC", "Amazon Data Services, Inc.", "2026-05-02"),
            contract(3, "Amazon Energy LLC", "Constellation NewEnergy, Inc.", "2026-09-01"),   # the other way round
            contract(4, "Constellation Energy Generation, LLC", "Exelon Generation", "2026-08-15"),   # one party only
            contract(5, "Vistra Energy", "Someone Else", "2026-08-15"),
        ]
        self.names = {"Amazon Data Services, Inc.": "AMAZON DATA SERVICES"}

    def test_two_parties_in_quarter(self):
        deal = {"event_id": "deal:a", "event_date": "2026-09-30T12:00:00Z", "buyer": "Amazon", "seller": "Constellation", "other_parties": ""}
        j = J.join([deal], self.contracts, self.names)["deal:a"]
        self.assertEqual(j["quarter"], "2026_Q3")
        self.assertEqual(j["how"], "two parties")
        self.assertEqual(sorted(h["id"] for h in j["in_quarter"]), ["eqr:1", "eqr:3"])
        self.assertEqual(sorted(h["id"] for h in j["any_quarter"]), ["eqr:1", "eqr:2", "eqr:3"])

    def test_one_party(self):
        deal = {"event_id": "deal:b", "event_date": "2026-08-01T00:00:00Z", "buyer": "", "seller": "Vistra", "other_parties": ""}
        j = J.join([deal], self.contracts, self.names)["deal:b"]
        self.assertEqual(j["how"], "one party")
        self.assertEqual([h["id"] for h in j["in_quarter"]], ["eqr:5"])

    def test_no_match_on_one_of_two(self):
        deal = {"event_id": "deal:c", "event_date": "2026-08-01T00:00:00Z", "buyer": "Exelon", "seller": "Vistra", "other_parties": ""}
        j = J.join([deal], self.contracts, self.names)["deal:c"]
        self.assertEqual(j["any_quarter"], [])


class CommittedFileTest(unittest.TestCase):
    def test_counts_only(self):
        with open(os.path.join(SITE, "data", "deals_eqr.json"), encoding="utf-8") as f:
            file = json.load(f)
        with open(os.path.join(SITE, "data", "deals_public.json"), encoding="utf-8") as f:
            shown = {r["event_id"] for r in json.load(f)["shown"]}
        self.assertEqual(set(file["deals"]), shown)
        for v in file["deals"].values():
            self.assertEqual(set(v), {"quarter", "how", "in_quarter", "any_quarter", "products", "quarters"})
            self.assertIsInstance(v["in_quarter"], int)
            self.assertLessEqual(v["in_quarter"], v["any_quarter"])
        text = json.dumps(file).lower()
        for word in ("rate", "$/mwh", "point_of_delivery", "seller", "buyer"):
            self.assertNotIn(f'"{word}"', text)   # no filed term and no filed name is in the file


class PageCodeTest(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_panel(self):
        t = self.read("site", "app", "deals", "DealsTable.tsx")
        for s in ("Filed terms (FERC EQR)", 'eqrKey(d.id, "in_quarter")', 'eqrKey(d.id, "any_quarter")', 'data-license-held="ferc_eqr_contracts"'):
            self.assertIn(s, t, s)
        self.assertIn("deals_eqr.json", self.read("site", "app", "deals", "page.tsx"))
        self.assertIn('p[1] === "eqr"', self.read("site", "scripts", "check-values.mjs"))
        self.assertIn("dealpub|eqr|<deal>|in_quarter", self.read("docs", "methods", "energy_deals.md"))

    def test_no_em_dash(self):
        for p in (("warehouse", "deals", "eqr_join.py"), ("site", "lib", "dealspublic.ts"), ("site", "app", "deals", "DealsTable.tsx"), ("tests", "test_session825.py")):
            self.assertNotIn(chr(0x2014), self.read(*p), p)


if __name__ == "__main__":
    unittest.main()

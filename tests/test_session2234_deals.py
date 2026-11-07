"""Session 2234 (chain 156): the deal tracker's counterparties (warehouse/deals/counterparties.py).

Names joined only where the words are the same, a company word is added, or an alias of aliases.yaml (each with its
story) says so; a parent only where the name's own words or an alias show it; an EIA-861 number only for an exact
name. No model, no network; the utilities are a small dict here, as load_utilities reads them from
utility_service_territories.
"""

import os
import sys
import unittest

import pandas as pd
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (os.path.join(ROOT, "warehouse", "deals"), os.path.join(ROOT, "warehouse", "deals", "eval")):
    if p not in sys.path:
        sys.path.insert(0, p)

import counterparties as cp  # noqa: E402
import fixture  # noqa: E402

UTIL = {cp.key("Northern Indiana Public Service Co"): {"13756"}, cp.key("Duke Energy Indiana, LLC"): {"15470"},
        cp.key("Duke Energy Ohio Inc"): {"3542"}}
SPELLINGS = ["Constellation", "Constellation Energy", "Constellation Energy", "Constellation", "AEP",
             "American Electric Power", "AES", "AES Corp", "Related Digital", "Related Companies", "DOE", "US",
             "Department of Energy", "Blackstone's QTS", "Blackstone", "Amazon data center unit", "Amazon",
             "Northern Indiana Public Service Co", "Duke Energy", "Golar LNG", "AWS"]


class Names(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = cp.Names(SPELLINGS, aliases=cp.load_aliases(), utilities=UTIL)

    def test_spellings_of_one_company_are_one_name(self):
        self.assertEqual(self.n.name("Constellation"), self.n.name("Constellation Energy"))
        self.assertEqual(self.n.name("Constellation"), "Constellation Energy")   # a tie keeps the fuller
        self.assertEqual(self.n.name("AES"), self.n.name("AES Corp"))

    def test_an_alias_needs_its_story(self):
        self.assertEqual(self.n.name("AEP"), "American Electric Power")
        with open(cp.ALIASES, encoding="utf-8") as f:
            for e in yaml.safe_load(f)["aliases"]:
                self.assertRegex(e["evidence"], r"^news:[0-9a-f]{16}")

    def test_two_companies_that_share_a_first_word_stay_two(self):
        self.assertNotEqual(self.n.name("Related Digital"), self.n.name("Related Companies"))
        self.assertEqual(self.n.parent("Related Digital"), "")
        self.assertEqual(self.n.parent("Golar LNG"), "")

    def test_the_us_government_is_one_name(self):
        self.assertEqual({self.n.name(x) for x in ("DOE", "US", "Department of Energy")}, {"US government"})

    def test_a_parent_only_where_the_words_show_it(self):
        self.assertEqual(self.n.parent("Blackstone's QTS"), "Blackstone")
        self.assertEqual(self.n.parent("Amazon data center unit"), "Amazon")
        self.assertEqual(self.n.parent("AWS"), "Amazon")             # aliases.yaml
        self.assertEqual(self.n.name("AWS"), "Amazon Web Services")  # the name is kept, the parent is a second field
        self.assertEqual(self.n.parent("Constellation"), "")

    def test_an_eia861_number_only_for_an_exact_name(self):
        self.assertEqual(self.n.eia861("Northern Indiana Public Service Co"), "13756")
        self.assertEqual(self.n.eia861("Duke Energy"), "")   # a holding company: several utilities begin with it

    def test_a_field_of_several_parties_is_split(self):
        self.assertEqual(cp.split("Nvidia, Dell"), ["Nvidia", "Dell"])
        self.assertEqual(cp.split("Apollo and Blackstone"), ["Apollo", "Blackstone"])
        self.assertEqual(cp.split("BP, Woodside and Chevron"), ["BP", "Woodside", "Chevron"])
        self.assertEqual(cp.split("Mozambique LNG Partners"), ["Mozambique LNG Partners"])


class Directory(unittest.TestCase):
    def test_the_directory_counts_each_deal_once(self):
        d = pd.DataFrame([
            {"event_id": "deal:1", "event_date": "2026-09-30", "buyer": "Amazon", "seller": "Constellation", "mw": "190",
             "ai_power": "true", "source_url": "https://example.org/1"},
            {"event_id": "deal:2", "event_date": "2026-10-06", "buyer": "Google", "seller": "Constellation Energy",
             "mw": "", "ai_power": "true", "source_url": "https://example.org/2"},
            {"event_id": "deal:3", "event_date": "2026-10-06", "buyer": "Amazon", "seller": "Constellation Energy",
             "mw": "", "ai_power": "true", "source_url": "https://example.org/3"},
            {"event_id": "deal:4", "event_date": "2026-10-07", "buyer": "investors", "seller": "Nvidia, Dell",
             "mw": "", "ai_power": "true", "source_url": "https://example.org/4"},
        ])
        out = cp.directory(d, folded=["deal:3"], names=cp.Names(list(d.buyer) + list(d.seller), aliases={}, utilities={}))
        c = out.set_index("name")
        self.assertEqual(c.loc["Constellation Energy", "deals"], "2")      # deal:3 is folded into deal:1
        self.assertEqual(c.loc["Constellation Energy", "mw_stated"], "190")
        self.assertEqual(c.loc["Constellation Energy", "deals_with_mw"], "1")
        self.assertEqual(c.loc["Constellation Energy", "first_deal"], "2026-09-30")
        self.assertEqual(c.loc["Constellation Energy", "source_url"], "https://example.org/1")
        self.assertEqual(c.loc["Amazon", "kind"], "ai_buyer")
        self.assertIn("Dell", c.index)
        self.assertNotIn("investors", c.index)


class OnTheDeals(unittest.TestCase):
    def test_every_extracted_row_carries_the_role_names(self):
        rows, _ = fixture.replay("2232")
        for c in cp.ROLE_COLS:
            self.assertIn(c, rows.columns)
        aep = rows[rows["seller"].isin(["AEP", "American Electric Power"])]
        self.assertTrue(len(aep) >= 1)
        self.assertTrue((aep["seller_name"] == "American Electric Power").all())


if __name__ == "__main__":
    unittest.main()

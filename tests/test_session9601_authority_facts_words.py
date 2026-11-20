"""Session 9601 (chain 620, 20 November 2026): an authority that sends out more than it takes in is said to send out.

Energy Research Warehouse (ERW). The browser read of the Grid tool's map opened the panel "Its own facts" of Seminole
Electric Cooperative and read "Net imports met -592 percent of its demand." The figure is the file's
(`site/data/regions/authority/sec.json`: trades, net_import_share_of_demand_pct); the sentence was written for an
importer. Below zero the panel now says what the authority sent out, with the same figure and no sign.

Held here, on the source and the committed files: the two sentences and which one a figure takes; the figure itself is
not changed (the same value, its size); the files hold authorities on both sides of zero, so both sentences are drawn.
Nothing here sets the environment, reads a table or makes a request.
"""
import glob
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class ThePanel(unittest.TestCase):
    def setUp(self):
        self.s = src("site", "components", "grid", "AuthorityFacts.tsx")

    def test_below_zero_the_sentence_speaks_of_what_was_sent_out(self):
        self.assertIn("f.trades.net_import_share_of_demand_pct < 0", self.s)
        self.assertIn('<span data-facts-share="exports">It sent out, net, power equal to {pct(-f.trades.net_import_share_of_demand_pct)} percent of its demand.</span>', self.s)

    def test_at_or_above_zero_the_sentence_is_as_it_was(self):
        self.assertIn('<span data-facts-share="imports">Net imports met {pct(f.trades.net_import_share_of_demand_pct)} percent of its demand.</span>', self.s)

    def test_no_share_still_says_why(self):
        self.assertIn('No share of demand: {f.trades.why ?? "its demand is not held for the year"}', self.s)

    def test_no_em_dash(self):
        self.assertNotIn(EM, self.s)
        self.assertNotIn(EM, src("tests", "test_session9601_authority_facts_words.py"))


class TheFiles(unittest.TestCase):
    def test_authorities_stand_on_both_sides_of_zero(self):
        below, above = [], []
        for f in glob.glob(os.path.join(ROOT, "site", "data", "regions", "authority", "*.json")):
            with open(f, encoding="utf-8") as h:
                v = (json.load(h).get("trades") or {}).get("net_import_share_of_demand_pct")
            if isinstance(v, (int, float)):
                (below if v < 0 else above).append(os.path.basename(f))
        self.assertGreater(len(below), 0, "no authority sends out more than it takes in: the second sentence is never drawn")
        self.assertGreater(len(above), 0)
        self.assertIn("sec.json", below)


if __name__ == "__main__":
    unittest.main()

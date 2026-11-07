"""Session 2250 (chain 156): the counterparties read for missed aliases (warehouse/deals/counterparties.py, aliases.yaml).

A party field that describes a facility by its backer is not a name; a party followed by a country or a region is a
subsidiary whose parent is that party; an alias is added only with a stored story that shows both names.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
import counterparties as cp  # noqa: E402
import pandas as pd  # noqa: E402


class Aliases(unittest.TestCase):
    def test_a_description_by_its_backer_is_not_a_row(self):
        d = pd.DataFrame([{"event_id": f"deal:{i}", "event_date": "2026-10-01", "buyer": b, "seller": "Seller Co", "mw": "",
                           "ai_power": "true", "source_url": "https://example.org"}
                          for i, b in enumerate(["Meta-backed data centre", "Google-Linked Data Centers", "CoreWeave-tied data center",
                                                 "Anthropic data centre backed by Google", "Amazon"])])
        names = set(cp.directory(d, names=cp.Names(list(d.buyer) + list(d.seller), aliases={}, utilities={}))["name"])
        self.assertEqual(names, {"Amazon", "Seller Co"})

    def test_a_subsidiary_named_by_its_place(self):
        n = cp.Names(["Chevron", "Chevron Australia", "ExxonMobil", "ExxonMobil Asia Pacific", "Golar LNG"], aliases={}, utilities={})
        self.assertEqual(n.parent("Chevron Australia"), "Chevron")
        self.assertEqual(n.parent("ExxonMobil Asia Pacific"), "ExxonMobil")
        self.assertEqual(n.parent("Golar LNG"), "")

    def test_delfin_by_its_story(self):
        n = cp.Names(["Delfin", "Delfin Midstream"], aliases=cp.load_aliases(), utilities={})
        self.assertEqual(n.name("Delfin"), "Delfin Midstream")
        self.assertIn("news:45e9aea1ffe912fa", cp.load_aliases()[cp.key("Delfin")]["evidence"])


if __name__ == "__main__":
    unittest.main()

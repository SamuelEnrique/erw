"""Session 2288 (chain 179): talks that name one party only are not a deal.

The third read (session 2284) found T040, "Qatar in Talks to Buy More US LNG, Diversify Supply Outside Persian Gulf",
kept with one party and no counterparty. The prompt makes talks a transaction between two named companies;
warehouse/deals/fields.py (one_party_talks) refuses such a record. A first form keyed on the stage "rumored" also
dropped D085 ("LS Power looks to raise $2.1 billion stake sale"), which the 2232 answer counts as a deal, so the rule
reads the word "talks" only. On the four deal fixtures, only T040 is gone.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import deal_fields as fields  # noqa: E402  session 3233: by its own name (deal_fields.py)
import fixture  # noqa: E402


class TheRule(unittest.TestCase):
    def test_one_party_talks(self):
        self.assertTrue(fields.one_party_talks({"buyer": "Qatar", "evidence": "Qatar in Talks to Buy More US LNG"}))

    def test_left(self):
        self.assertEqual(fields.one_party_talks({"buyer": "NextEra", "seller": "Dominion",
                                                 "evidence": "NextEra, Dominion in talks to create $400 billion US utility"}), "")
        self.assertEqual(fields.one_party_talks({"seller": "LS Power",
                                                 "evidence": "LS Power looks to raise $2.1 billion stake sale in NRG Energy"}), "")


class TheSample(unittest.TestCase):
    def test_t040_gone(self):
        rows, log = fixture.replay("2284")
        self.assertEqual(len(rows), 8)
        self.assertFalse(any(r["buyer"] == "Qatar" for r in rows.to_dict("records")))
        rows2232, _ = fixture.replay("2232")
        self.assertTrue(any(r["seller"] == "LS Power" for r in rows2232.to_dict("records")))


if __name__ == "__main__":
    unittest.main()
